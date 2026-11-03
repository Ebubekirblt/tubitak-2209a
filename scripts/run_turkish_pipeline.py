#!/usr/bin/env python3
"""Run the repeatable Turkish data, verification, and training pipeline."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "dataset" / "turkish_manifest.jsonl"
MODEL_CONFIGS = {
    "AASIST": ("aasist-source/config/AASIST.conf", "aasist-source/models/weights/AASIST.pth"),
    "AASIST-L": ("aasist-source/config/AASIST-L.conf", "aasist-source/models/weights/AASIST-L.pth"),
    "RawNet2": ("aasist-source/config/Turkish_RawNet2.conf", None),
    "RawGAT-ST": ("aasist-source/config/Turkish_RawGATST.conf", None),
}


def run(command: list[str]) -> None:
    print("\n==>", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def parse_models(value: str) -> list[str]:
    available = {*MODEL_CONFIGS, "XLSR"}
    names = list(MODEL_CONFIGS) + ["XLSR"] if value == "all" else [item.strip() for item in value.split(",")]
    unknown = sorted(set(names) - available)
    if unknown:
        raise SystemExit(f"Unknown model(s): {', '.join(unknown)}")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", default="AASIST",
                        help="Comma-separated models, XLSR, or 'all' (default: AASIST)")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--extract-archives", action="store_true")
    parser.add_argument("--holdout-generator",
                        help="Keep a matching TTS generator only in the test split")
    parser.add_argument("--phone-channel", action="store_true",
                        help="Train/evaluate on the generated 8 kHz G.711 manifest")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="auto")
    args = parser.parse_args()

    models = parse_models(args.models)
    manifest = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest_cmd = [
        sys.executable, str(ROOT / "scripts" / "create_turkish_manifest.py"),
        "--root", str(ROOT / "dataset"), "--output", str(manifest),
    ]
    if args.extract_archives:
        manifest_cmd.append("--extract-archives")
    if args.holdout_generator:
        manifest_cmd.extend(["--holdout-generator", args.holdout_generator])
    run(manifest_cmd)

    if args.phone_channel:
        phone_manifest = ROOT / "dataset" / "turkish_phone_manifest.jsonl"
        run([
            sys.executable, str(ROOT / "scripts" / "create_phone_channel_manifest.py"),
            "--input-manifest", str(manifest),
            "--output-manifest", str(phone_manifest),
            "--output-dir", str(ROOT / "dataset" / "phone_channel_8k"),
        ])
        manifest = phone_manifest

    if args.prepare_only:
        print(f"\nManifest hazır: {manifest}")
        return 0

    if not args.skip_verify:
        run([sys.executable, str(ROOT / "scripts" / "verify_models.py")])

    summary = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(manifest),
        "models": models,
        "device": args.device,
        "phone_channel": args.phone_channel,
        "holdout_generator": args.holdout_generator,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "runs": [],
    }
    for model_name in models:
        if model_name == "XLSR":
            xlsr_command = [
                sys.executable, str(ROOT / "scripts" / "train_xlsr_turkish.py"),
                "--manifest", str(manifest), "--device", args.device,
                "--output", str(ROOT / "experiments" / "turkish" / "XLSR"),
            ]
            if args.epochs is not None:
                xlsr_command.extend(["--epochs", str(args.epochs)])
            if args.batch_size is not None:
                xlsr_command.extend(["--batch-size", str(args.batch_size)])
            run(xlsr_command)
            summary["runs"].append({
                "model": model_name,
                "output": str(ROOT / "experiments" / "turkish" / "XLSR"),
            })
            continue
        config_name, weights_name = MODEL_CONFIGS[model_name]
        command = [
            sys.executable, str(ROOT / "scripts" / "train_turkish.py"),
            "--manifest", str(manifest),
            "--config", str(ROOT / config_name),
            "--output", str(ROOT / "experiments" / "turkish" / model_name),
            "--device", args.device,
        ]
        if weights_name:
            command.extend(["--weights", str(ROOT / weights_name)])
        if args.epochs is not None:
            command.extend(["--epochs", str(args.epochs)])
        if args.batch_size is not None:
            command.extend(["--batch-size", str(args.batch_size)])
        run(command)
        summary["runs"].append({
            "model": model_name,
            "output": str(ROOT / "experiments" / "turkish" / model_name),
        })

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    summary_path = ROOT / "experiments" / "turkish" / "run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nPipeline tamamlandı. Özet: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
