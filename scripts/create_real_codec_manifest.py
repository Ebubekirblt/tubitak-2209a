#!/usr/bin/env python3
"""Create a manifest using real FFmpeg GSM/AMR/Opus codec round-trips."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


CODECS = {
    "gsm": (["-ar", "8000", "-ac", "1", "-c:a", "gsm"], ".wav"),
    "opus": (["-ar", "8000", "-ac", "1", "-c:a", "libopus", "-b:a", "12k"], ".ogg"),
    "amr_nb": (["-ar", "8000", "-ac", "1", "-c:a", "libopencore_amrnb", "-b:a", "12.2k"], ".amr"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--codec", choices=tuple(CODECS), required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required for real codec conversion")
    rows = [json.loads(line) for line in args.input_manifest.read_text().splitlines() if line]
    if args.limit is not None:
        rows = rows[:args.limit]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    converted = []
    with tempfile.TemporaryDirectory() as temp:
        for index, row in enumerate(rows):
            encoded = Path(temp) / f"{index}{CODECS[args.codec][1]}"
            target = args.output_dir / f"{index:08d}.wav"
            command = [ffmpeg, "-y", "-i", row["path"], *CODECS[args.codec][0], str(encoded)]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            subprocess.run([ffmpeg, "-y", "-i", str(encoded), "-ar", "8000", "-ac", "1",
                            "-c:a", "pcm_s16le", str(target)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            converted.append({**row, "path": str(target.resolve()),
                              "channel": f"real_{args.codec}"})
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_manifest.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in converted) + "\n",
        encoding="utf-8")
    print(f"Wrote {len(converted)} {args.codec} codec records to {args.output_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
