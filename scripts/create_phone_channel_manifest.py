#!/usr/bin/env python3
"""Create a telephone-channel (8 kHz, G.711 mu-law) copy of a JSONL manifest."""

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


def mulaw_roundtrip(audio: np.ndarray) -> np.ndarray:
    """Apply the standard 8-bit G.711 mu-law quantization and decode it."""
    clipped = np.clip(audio, -1.0, 1.0)
    encoded = np.sign(clipped) * np.log1p(255 * np.abs(clipped)) / np.log1p(255)
    quantized = np.floor((encoded + 1.0) * 127.5 + 0.5) / 127.5 - 1.0
    return np.sign(quantized) * (np.expm1(np.abs(quantized) * np.log1p(255)) / 255)


def convert(path: Path) -> np.ndarray:
    audio, sample_rate = sf.read(path, dtype="float32", always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if audio.size == 0:
        raise ValueError(f"Empty audio file: {path}")
    narrowband = resample_poly(audio, 8000, sample_rate)
    return mulaw_roundtrip(narrowband).astype("float32")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=Path("dataset/turkish_manifest.jsonl"))
    parser.add_argument("--output-manifest", type=Path,
                        default=Path("dataset/turkish_phone_manifest.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("dataset/phone_channel_8k"))
    parser.add_argument("--limit", type=int, help="Process only the first N records")
    args = parser.parse_args()

    records = [
        json.loads(line)
        for line in args.input_manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if args.limit is not None:
        records = records[:args.limit]
    if not records:
        raise SystemExit("Manifest is empty")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    converted = []
    for index, record in enumerate(records):
        source = Path(record["path"])
        target = args.output_dir / f"{index:08d}_{source.stem}.wav"
        sf.write(target, convert(source), 8000, subtype="PCM_16")
        converted.append({
            **record,
            "path": str(target.resolve()),
            "channel": "telephone_8khz_g711_mulaw",
        })

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8") as handle:
        for record in converted:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote {len(converted)} telephone-channel records to {args.output_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
