#!/usr/bin/env python3
"""Create a train/dev/test JSONL manifest from local Turkish WAV datasets."""

import argparse
import json
import tarfile
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
        "--holdout-generator",
        help="Move matching generator records to test for unseen-generator evaluation",
    )
    args = parser.parse_args()

    if args.extract_archives:
        extract_archives(args.root)
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
        records.append({
            "path": resolved_path,
            "label": label,
            "split": split_for(audio),
            "source": source,
            "generator": generator_for(audio, args.root),
        })
    if not records:
        raise SystemExit("No WAV files found. Download/extract Turkish datasets first.")
    for label in (0, 1):
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
            candidates = [record for record in records if record["split"] == "train"]
            if not candidates:
                raise SystemExit(f"Cannot create {missing} split from the discovered audio")
            candidates[-1]["split"] = missing
    for split in ("dev", "test"):
        labels = {record["label"] for record in records if record["split"] == split}
        for label in {0, 1} - labels:
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
