#!/usr/bin/env python3
"""Train an anti-spoofing model on the Turkish JSONL manifest."""

import argparse
import importlib
import json
import random
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "aasist-source"
sys.path.insert(0, str(SOURCE))


def pad_random(audio: np.ndarray, length: int) -> np.ndarray:
    if len(audio) == 0:
        raise ValueError("Encountered an empty audio file")
    if len(audio) >= length:
        start = random.randint(0, len(audio) - length)
        return audio[start:start + length]
    repeats = (length + len(audio) - 1) // len(audio)
    return np.tile(audio, repeats)[:length]


class TurkishAudioDataset(Dataset):
    def __init__(self, records: list[dict], samples: int, training: bool):
        self.records = records
        self.samples = samples
        self.training = training

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        record = self.records[index]
        audio, sample_rate = sf.read(record["path"], dtype="float32", always_2d=False)
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        if len(audio) == 0:
            raise ValueError(f"Empty audio file: {record['path']}")
        if sample_rate != 16000:
            import scipy.signal
            audio = scipy.signal.resample_poly(audio, 16000, sample_rate).astype("float32")
        if self.training:
            audio = pad_random(audio, self.samples)
        else:
            audio = audio[:self.samples]
            if len(audio) < self.samples:
                audio = np.pad(audio, (0, self.samples - len(audio)), mode="wrap")
        return torch.from_numpy(audio.copy()), torch.tensor(record["label"], dtype=torch.long)


def load_manifest(path: Path) -> dict[str, list[dict]]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    result = {split: [record for record in records if record["split"] == split]
              for split in ("train", "dev", "test")}
    if not result["train"] or not result["dev"] or not result["test"]:
        raise ValueError("Manifest must contain non-empty train, dev, and test splits")
    return result


def build_model(config: dict, device: torch.device) -> nn.Module:
    module = importlib.import_module(f"models.{config['model_config']['architecture']}")
    model = module.Model(config["model_config"]).to(device)
    return model


def run_epoch(model, loader, criterion, device, optimizer=None) -> tuple[float, float]:
    training = optimizer is not None
    model.train(training)
    total_loss = correct = total = 0
    for audio, labels in loader:
        audio, labels = audio.to(device), labels.to(device)
        with torch.set_grad_enabled(training):
            _, logits = model(audio)
            loss = criterion(logits, labels)
            if training:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)
    return total_loss / total, correct / total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="auto")
    args = parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.output is None:
        architecture = config["model_config"]["architecture"]
        args.output = ROOT / "experiments" / "turkish" / architecture
    elif not args.output.is_absolute():
        args.output = ROOT / args.output
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"output={args.output.resolve()}")
    records = load_manifest(args.manifest)
    if args.device == "auto":
        device_name = "cuda" if torch.cuda.is_available() else (
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
    else:
        device_name = args.device
    if device_name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA istendi ancak kullanılabilir bir CUDA cihazı yok")
    if device_name == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS istendi ancak kullanılabilir bir Apple GPU yok")
    device = torch.device(device_name)
    print(f"device={device}")
    model = build_model(config, device)
    if args.weights:
        model.load_state_dict(torch.load(args.weights, map_location=device, weights_only=True))

    batch_size = args.batch_size or config["batch_size"]
    epochs = args.epochs or config["num_epochs"]
    samples = config["model_config"]["nb_samp"]
    loaders = {
        split: DataLoader(
            TurkishAudioDataset(items, samples, split == "train"),
            batch_size=batch_size,
            shuffle=split == "train",
            drop_last=False,
            num_workers=0,
        )
        for split, items in records.items()
    }
    counts = torch.bincount(torch.tensor([r["label"] for r in records["train"]]), minlength=2)
    weights = (counts.sum() / (2 * counts.clamp_min(1))).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["optim_config"]["base_lr"],
                                  weight_decay=config["optim_config"]["weight_decay"])
    best_accuracy = -1.0
    history = []
    for epoch in range(1, epochs + 1):
        train_loss, train_accuracy = run_epoch(model, loaders["train"], criterion, device, optimizer)
        dev_loss, dev_accuracy = run_epoch(model, loaders["dev"], criterion, device)
        print(f"epoch={epoch:03d} train_loss={train_loss:.4f} train_acc={train_accuracy:.4f} "
              f"dev_loss={dev_loss:.4f} dev_acc={dev_accuracy:.4f}")
        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "dev_loss": dev_loss,
            "dev_accuracy": dev_accuracy,
        })
        if dev_accuracy >= best_accuracy:
            best_accuracy = dev_accuracy
            torch.save(model.state_dict(), args.output / "best.pth")
    test_loss, test_accuracy = run_epoch(model, loaders["test"], criterion, device)
    print(f"test_loss={test_loss:.4f} test_acc={test_accuracy:.4f}")
    (args.output / "metrics.json").write_text(json.dumps({
        "config": str(args.config.resolve()),
        "manifest": str(args.manifest.resolve()),
        "device": str(device),
        "epochs": epochs,
        "batch_size": batch_size,
        "best_dev_accuracy": best_accuracy,
        "test_loss": test_loss,
        "test_accuracy": test_accuracy,
        "history": history,
    }, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
