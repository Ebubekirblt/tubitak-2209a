#!/usr/bin/env python3
"""Fine-tune a wav2vec2-XLS-R classifier from the Turkish JSONL manifest."""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly
from torch.utils.data import DataLoader, Dataset
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification


ROOT = Path(__file__).resolve().parents[1]


class ManifestAudio(Dataset):
    def __init__(self, records: list[dict], training: bool):
        self.records = records
        self.training = training

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict:
        record = self.records[index]
        audio, rate = sf.read(record["path"], dtype="float32", always_2d=False)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        if rate != 16000:
            audio = resample_poly(audio, 16000, rate).astype("float32")
        if len(audio) > 64000:
            start = random.randint(0, len(audio) - 64000) if self.training else 0
            audio = audio[start:start + 64000]
        elif len(audio) < 64000:
            audio = np.pad(audio, (0, 64000 - len(audio)), mode="wrap")
        return {"audio": audio, "label": record["label"]}


def collate(batch: list[dict], extractor):
    return {
        **extractor([item["audio"] for item in batch], sampling_rate=16000,
                    padding=True, return_tensors="pt"),
        "labels": torch.tensor([item["label"] for item in batch], dtype=torch.long),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model", default="facebook/wav2vec2-xls-r-300m")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/turkish/XLSR")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="auto")
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line]
    splits = {name: [row for row in rows if row["split"] == name] for name in ("train", "dev", "test")}
    if any(not items for items in splits.values()):
        raise SystemExit("Manifest must contain train, dev, and test records")
    if args.device == "auto":
        name = "cuda" if torch.cuda.is_available() else (
            "mps" if torch.backends.mps.is_available() else "cpu")
    else:
        name = args.device
    if name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    if name == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS is unavailable")
    device = torch.device(name)
    extractor = AutoFeatureExtractor.from_pretrained(args.model)
    model = AutoModelForAudioClassification.from_pretrained(
        args.model, num_labels=2, label2id={"genuine": 1, "synthetic": 0},
        id2label={0: "synthetic", 1: "genuine"}, ignore_mismatched_sizes=True,
    ).to(device)
    loaders = {
        split: DataLoader(ManifestAudio(items, split == "train"), args.batch_size,
                          shuffle=split == "train", collate_fn=lambda b: collate(b, extractor))
        for split, items in splits.items()
    }
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    args.output.mkdir(parents=True, exist_ok=True)
    history = []
    best = -1.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        for batch in loaders["train"]:
            batch = {key: value.to(device) for key, value in batch.items()}
            loss = model(**batch).loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.inference_mode():
            correct = total = 0
            for batch in loaders["dev"]:
                batch = {key: value.to(device) for key, value in batch.items()}
                logits = model(**batch).logits
                correct += (logits.argmax(1) == batch["labels"]).sum().item()
                total += len(batch["labels"])
        accuracy = correct / total
        history.append({"epoch": epoch, "dev_accuracy": accuracy})
        print(f"epoch={epoch:03d} dev_acc={accuracy:.4f}")
        if accuracy >= best:
            best = accuracy
            model.save_pretrained(args.output)
            extractor.save_pretrained(args.output)
    (args.output / "metrics.json").write_text(json.dumps({
        "model": args.model, "device": str(device), "best_dev_accuracy": best,
        "history": history,
    }, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
