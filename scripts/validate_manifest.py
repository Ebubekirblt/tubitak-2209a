#!/usr/bin/env python3
"""Validate split integrity and class/source balance for a JSONL manifest."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-speaker-id", action="store_true")
    parser.add_argument("--speaker-disjoint", action="store_true")
    parser.add_argument("--max-class-ratio", type=float, default=20.0)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        raise SystemExit("Manifest is empty")
    splits = {name: [row for row in rows if row.get("split") == name] for name in ("train", "dev", "test")}
    if any(not items for items in splits.values()):
        raise SystemExit("Manifest must contain non-empty train, dev, and test splits")
    if args.require_speaker_id and any(not row.get("speaker_id") for row in rows):
        raise SystemExit("Speaker-disjoint validation requires speaker_id on every record")
    if args.speaker_disjoint:
        speaker_sets = {
            split: {row["speaker_id"] for row in items}
            for split, items in splits.items()
        }
        for left, right in (("train", "dev"), ("train", "test"), ("dev", "test")):
            overlap = speaker_sets[left] & speaker_sets[right]
            if overlap:
                raise SystemExit(f"Speaker leakage between {left}/{right}: {len(overlap)} speakers")
    for split, items in splits.items():
        counts = collections.Counter(row.get("label") for row in items)
        if set(counts) != {0, 1}:
            raise SystemExit(f"{split} must contain labels 0 and 1, found {dict(counts)}")
        ratio = max(counts.values()) / min(counts.values())
        if ratio > args.max_class_ratio:
            raise SystemExit(f"{split} class imbalance ratio {ratio:.2f} exceeds limit")
    print("splits:", {name: len(items) for name, items in splits.items()})
    print("sources:", dict(collections.Counter(row.get("source") for row in rows)))
    print("generators:", dict(collections.Counter(row.get("generator") for row in rows)))
    print("manifest validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
