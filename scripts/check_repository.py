"""Run dependency-free consistency checks for the repository."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "setup-macos.sh",
    "setup-windows.ps1",
    "scripts/2209A_AASIST_kurulum_Python314.sh",
    "scripts/TUBITAK_2209A_Windows_Tek_Script-2.ps1",
    "scripts/run_turkish_pipeline.py",
    "scripts/train_turkish.py",
    "scripts/verify_models.py",
)
REQUIRED_DIRECTORIES = (
    "aasist-source/config",
    "aasist-source/models",
    "dataset",
    "docs",
    "experiments",
    "scripts",
)
MANIFESTS = (
    "dataset/commonvoice_tr_manifest.jsonl",
    "dataset/turkish_manifest.jsonl",
)


def fail(message: str) -> None:
    raise SystemExit(f"[HATA] {message}")


def check_paths() -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"Gerekli dosya eksik: {relative}")
    for relative in REQUIRED_DIRECTORIES:
        if not (ROOT / relative).is_dir():
            fail(f"Gerekli klasör eksik: {relative}")


def check_manifests() -> None:
    for relative in MANIFESTS:
        path = ROOT / relative
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    fail(f"{relative}:{line_number} geçersiz JSON: {error.msg}")
                if not isinstance(value, dict):
                    fail(f"{relative}:{line_number} JSON nesnesi olmalı")


def check_python_compile() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "aasist-source", "scripts"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        fail("Python sözdizimi kontrolü başarısız")


def main() -> int:
    check_paths()
    check_manifests()
    check_python_compile()
    print("Repo kontrolü başarılı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
