#!/usr/bin/env python3
"""Verify or export a bounded Common Voice Turkish subset as WAV files."""

import argparse
import io
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from datasets import Audio, load_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dataset/commonvoice_17_tr_fixed"))
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--all", action="store_true", help="Export every record in each selected split")
    parser.add_argument("--splits", nargs="+", default=["train", "validation", "test"])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for split in args.splits:
        dataset = load_dataset("ysdede/commonvoice_17_tr_fixed", split=split, streaming=True)
        dataset = dataset.cast_column("audio", Audio(decode=False))
        for index, item in enumerate(dataset):
            if not args.all and index >= args.limit:
                break
            target = args.output / split / f"{index:08d}.wav"
            target.parent.mkdir(parents=True, exist_ok=True)
            audio = item["audio"]
            if audio.get("bytes") is not None:
                samples, rate = sf.read(io.BytesIO(audio["bytes"]), dtype="float32")
            else:
                samples, rate = sf.read(audio["path"], dtype="float32")
            if samples.ndim == 2:
                samples = np.mean(samples, axis=1)
            sf.write(target, samples, rate, subtype="PCM_16")
            speaker_id = item.get("client_id")
            row = {"path": str(target.resolve()), "split": split, "label": 1,
                   "source": "commonvoice_17_tr_fixed",
                   "generator": "commonvoice_17_tr_fixed"}
            if speaker_id:
                row["speaker_id"] = str(speaker_id)
            rows.append(row)
    manifest = args.output.parent / "commonvoice_tr_manifest.jsonl"
    manifest.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    print(f"Exported {len(rows)} Common Voice records to {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
