#!/usr/bin/env python3
"""Create a train/dev/test JSONL manifest from local Turkish WAV datasets."""

import argparse
import csv
import json
import tarfile
from collections import defaultdict
from pathlib import Path


SYNTHETIC_NAMES = {"mlaad", "girenit-tts-tr-synthetic", "synthetic_turkish_tts_data"}
REAL_NAMES = {"fleurs_tr", "commonvoice_17_tr_fixed", "commonvoice"}


def split_for(path: Path) -> str | None:
    parts = {part.casefold() for part in path.parts}
    if "train" in parts:
        return "train"
    if "dev" in parts or "validation" in parts:
        return "dev"
    if "test" in parts or "eval" in parts:
        return "test"
    return None


def source_and_label(path: Path) -> tuple[str, int]:
    dataset = next(
        (part for part in path.parts if part.casefold() in SYNTHETIC_NAMES),
        None,
    )
    if dataset:
        return dataset, 0
    dataset = next(
        (part for part in path.parts if part.casefold() in REAL_NAMES),
        None,
    )
    return dataset or "genuine", 1


def generator_for(path: Path, root: Path) -> str:
    parts = path.relative_to(root).parts
    dataset = parts[0] if parts else "unknown"
    if dataset.casefold() == "mlaad":
        try:
            language_index = next(
                index for index, part in enumerate(parts)
                if part.casefold() == "tr"
            )
            if language_index + 1 < len(parts) - 1:
                return f"MLAAD/{parts[language_index + 1]}"
        except StopIteration:
            pass
    return dataset


def speaker_metadata(root: Path) -> dict[str, str]:
    metadata = {}
    for tsv in root.glob("FLEURS_TR/data/tr_tr/*.tsv"):
        with tsv.open(encoding="utf-8") as handle:
            for row in csv.reader(handle, delimiter="\t"):
                if len(row) >= 2 and row[0] != "id":
                    metadata[str((tsv.parent / "audio" / tsv.stem / row[1]).resolve())] = (
                        f"FLEURS_TR/{row[0]}"
                    )
    for csv_path in root.glob("girenit-tts-tr-synthetic/*/metadata.csv"):
        with csv_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                speaker = row.get("reference_speaker") or row.get("teacher_model")
                if row.get("file_name") and speaker:
                    metadata[str((csv_path.parent / row["file_name"]).resolve())] = (
                        f"girenit/{speaker}"
                    )
    for meta in root.glob("MLAAD/fake/tr/*/meta.csv"):
        with meta.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="|"):
                relative = row.get("path", "")
                speaker = row.get("model_name")
                if relative and speaker:
                    metadata[str((root / "MLAAD" / relative).resolve())] = (
                        f"MLAAD/{speaker}"
                    )
    return metadata


def extract_archives(root: Path) -> None:
    for archive in root.rglob("*.tar.gz"):
        target = archive.parent
        marker = target / f".{archive.name}.extracted"
        if marker.exists():
            continue
        with tarfile.open(archive) as handle:
            target_resolved = target.resolve()
            for member in handle.getmembers():
                member_path = (target / member.name).resolve()
                if member_path != target_resolved and target_resolved not in member_path.parents:
                    raise ValueError(f"Unsafe archive member: {member.name}")
            handle.extractall(target)
        marker.touch()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("dataset"))
    parser.add_argument("--output", type=Path, default=Path("dataset/turkish_manifest.jsonl"))
    parser.add_argument("--extract-archives", action="store_true")
    parser.add_argument(
        "--speaker-disjoint",
        action="store_true",
        help="Create deterministic group-disjoint splits; requires speaker_id metadata",
    )
    parser.add_argument(
        "--exclude-source",
        action="append",
        default=[],
        help="Exclude a source name; repeat for multiple sources",
    )
    parser.add_argument(
        "--holdout-generator",
        help="Move matching generator records to test for unseen-generator evaluation",
    )
    args = parser.parse_args()

    if args.extract_archives:
        extract_archives(args.root)
    metadata_by_path = {}
    speaker_by_filename = speaker_metadata(args.root)
    source_manifests = (
        args.root / "commonvoice_tr_manifest.jsonl",
        args.root / "commonvoice_17_tr_fixed" / "commonvoice_tr_manifest.jsonl",
    )
    for metadata_path in source_manifests:
        if not metadata_path.is_file():
            continue
        for line in metadata_path.read_text(encoding="utf-8").splitlines():
            if line:
                item = json.loads(line)
                metadata_by_path[str(Path(item["path"]).resolve())] = item
    records = []
    seen_paths = set()
    for audio in sorted(args.root.rglob("*.wav")):
        if any(part.startswith(".") for part in audio.parts):
            continue
        source, label = source_and_label(audio)
        resolved_path = str(audio.resolve())
        if resolved_path in seen_paths:
            raise SystemExit(f"Duplicate audio path: {resolved_path}")
        seen_paths.add(resolved_path)
        record = {
            "path": resolved_path,
            "label": label,
            "split": split_for(audio),
            "source": source,
            "generator": generator_for(audio, args.root),
        }
        source_metadata = metadata_by_path.get(resolved_path, {})
        if source_metadata.get("speaker_id"):
            record["speaker_id"] = source_metadata["speaker_id"]
        elif resolved_path in speaker_by_filename:
            record["speaker_id"] = speaker_by_filename[resolved_path]
        if source in args.exclude_source:
            continue
        records.append(record)
    if not records:
        raise SystemExit("No WAV files found. Download/extract Turkish datasets first.")
    if args.speaker_disjoint:
        missing_speakers = [
            record["path"] for record in records if not record.get("speaker_id")
        ]
        if missing_speakers:
            raise SystemExit(
                "--speaker-disjoint requires speaker_id metadata; "
                f"{len(missing_speakers)} records are missing it"
            )
        groups = defaultdict(list)
        for record in records:
            groups[record["speaker_id"]].append(record)
        speaker_groups = sorted(groups.values(), key=lambda items: items[0]["speaker_id"])
        by_label = defaultdict(list)
        for items in speaker_groups:
            dominant_label = max(
                (0, 1),
                key=lambda label: sum(record["label"] == label for record in items),
            )
            by_label[dominant_label].append(items)
        for label_groups in by_label.values():
            if len(label_groups) < 3:
                raise SystemExit(
                    "Speaker-disjoint split requires at least three speaker groups "
                    "for each label"
                )
            ordered = sorted(label_groups, key=lambda items: items[0]["speaker_id"])
            assignments = {}
            for index, items in enumerate(ordered):
                if index == 0:
                    split = "train"
                elif index == 1:
                    split = "dev"
                elif index == 2:
                    split = "test"
                else:
                    split = "train"
                assignments[id(items)] = split
            for items in ordered[3:]:
                assignments[id(items)] = min(
                    ("train", "dev", "test"),
                    key=lambda split: (
                        sum(
                            len(group)
                            for group in ordered
                            if assignments.get(id(group)) == split
                        ),
                        split,
                    ),
                )
            for items in ordered:
                split = assignments[id(items)]
                for record in items:
                    record["split"] = split
    for label in (0, 1):
        if args.speaker_disjoint:
            continue
        pending = sorted(
            (record for record in records if record["label"] == label and record["split"] is None),
            key=lambda record: record["path"],
        )
        for index, record in enumerate(pending):
            ratio = index / max(len(pending), 1)
            record["split"] = "train" if ratio < 0.8 else "dev" if ratio < 0.9 else "test"
    records = [record for record in records if record["split"] is not None]
    if args.holdout_generator:
        needle = args.holdout_generator.casefold()
        held_out = [
            record for record in records
            if needle in record["generator"].casefold()
        ]
        if not held_out:
            raise SystemExit(
                f"No generator matched --holdout-generator={args.holdout_generator}"
            )
        for record in held_out:
            record["split"] = "test"
    for missing in ("dev", "test"):
        if not any(record["split"] == missing for record in records):
            if args.speaker_disjoint:
                raise SystemExit(
                    f"Speaker-disjoint split could not create {missing} without leakage"
                )
            candidates = [record for record in records if record["split"] == "train"]
            if not candidates:
                raise SystemExit(f"Cannot create {missing} split from the discovered audio")
            candidates[-1]["split"] = missing
    for split in ("dev", "test"):
        labels = {record["label"] for record in records if record["split"] == split}
        for label in {0, 1} - labels:
            if args.speaker_disjoint:
                raise SystemExit(
                    f"Speaker-disjoint {split} split is missing label {label}; "
                    "adjust source grouping or provide more speaker groups"
                )
            candidates = [
                record for record in records
                if record["split"] == "train"
                and record["label"] == label
                and not (args.holdout_generator
                         and args.holdout_generator.casefold() in record["generator"].casefold())
            ]
            if not candidates:
                raise SystemExit(
                    f"Cannot add label {label} to {split} without breaking holdout constraints"
                )
            candidates[-1]["split"] = split
    for split in ("train", "dev", "test"):
        labels = {record["label"] for record in records if record["split"] == split}
        if labels != {0, 1}:
            raise SystemExit(
                f"{split} split must contain both labels 0 and 1; found {sorted(labels)}"
            )
    counts = {
        split: sum(record["split"] == split for record in records)
        for split in ("train", "dev", "test")
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} records to {args.output}")
    print("Splits:", counts)
    print("Labels: genuine=1, synthetic=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
