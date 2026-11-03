#!/usr/bin/env python3
"""Verify that the bundled anti-spoofing model architectures run locally."""

import argparse
import json
import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "aasist-source"
sys.path.insert(0, str(SOURCE))

from models.AASIST import Model as AASIST  # noqa: E402
from models.RawNet2Spoof import Model as RawNet2  # noqa: E402
from models.RawNetGatSpoofST import Model as RawGATST  # noqa: E402


MODELS = {
    "AASIST": (AASIST, "AASIST.conf"),
    "AASIST-L": (AASIST, "AASIST-L.conf"),
    "RawNet2": (RawNet2, "RawNet2_baseline.conf"),
    "RawGAT-ST": (RawGATST, "RawGATST_baseline.conf"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=(*MODELS, "all"), default="all")
    parser.add_argument("--device", choices=("cpu", "cuda", "mps"), default="cpu")
    args = parser.parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable")
    if args.device == "mps" and not torch.backends.mps.is_available():
        raise SystemExit("MPS is unavailable")
    device = torch.device(args.device)

    names = MODELS if args.model == "all" else {args.model: MODELS[args.model]}
    for name, (model_type, config_name) in names.items():
        config = json.loads((SOURCE / "config" / config_name).read_text())
        model = model_type(config["model_config"]).to(device).eval()
        with torch.inference_mode():
            _, logits = model(torch.zeros(1, config["model_config"]["nb_samp"], device=device))
        if tuple(logits.shape) != (1, 2):
            raise RuntimeError(f"{name}: unexpected output shape {tuple(logits.shape)}")
        print(f"{name}: OK {tuple(logits.shape)} device={device}")
        del model
        if device.type == "mps":
            torch.mps.empty_cache()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
