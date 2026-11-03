#!/usr/bin/env python3
"""Download only Turkish MLAAD folders without enumerating the entire repository.

Usage:
  python mlaad_tr_dilimli_indir.py --list
  python mlaad_tr_dilimli_indir.py --model bark --limit 20
  python mlaad_tr_dilimli_indir.py --model bark --all
  python mlaad_tr_dilimli_indir.py --all
"""

import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "30")

from huggingface_hub import HfApi, RepoFile, RepoFolder, hf_hub_download

REPO = "mueller91/MLAAD"
TR_ROOT = "fake/tr"
DEFAULT_DEST = Path.home() / "Desktop/Tubitak/dataset/MLAAD"


def print_flush(message):
    print(message, flush=True)


def main():
    parser = argparse.ArgumentParser(description="MLAAD Turkce dizinleri parca parca indir.")
    parser.add_argument("--list", action="store_true", help="Sadece Turkce TTS klasorlerini listele.")
    parser.add_argument("--model", help="Klasor adinda aranacak kelime (ornegin bark veya xtts).")
    parser.add_argument("--limit", type=int, default=20, help="Her klasorden indirilecek azami dosya (varsayilan 20).")
    parser.add_argument("--all", action="store_true", help="Secilen klasor(ler)in tum dosyalarini indir.")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="Indirme klasoru")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit en az 1 olmali")

    api = HfApi()
    print_flush(f"Turkce model klasorleri listeleniyor: {REPO}/{TR_ROOT}")
    try:
        folders = sorted(
            (entry for entry in api.list_repo_tree(
                repo_id=REPO,
                repo_type="dataset",
                path_in_repo=TR_ROOT,
                recursive=False,
                expand=False,
                token=os.getenv("HF_TOKEN") or None,
            ) if isinstance(entry, RepoFolder)),
            key=lambda entry: entry.path,
        )
    except Exception as exc:
        print_flush(f"Klasor listeleme hatasi: {type(exc).__name__}: {exc}")
        return 1

    print_flush(f"Bulunan model klasoru sayisi: {len(folders)}")
    for folder in folders:
        print_flush("  " + folder.path.removeprefix(TR_ROOT + "/"))

    if args.list:
        return 0

    if args.model:
        folders = [folder for folder in folders if args.model.casefold() in folder.path.casefold()]
        if not folders:
            print_flush(f"'{args.model}' ile eslesen klasor yok. --list ile isimleri kontrol et.")
            return 1
    elif not args.all:
        print_flush("Güvenlik: tum klasorler icin --all veya tek model icin --model KELIME belirt.")
        return 1

    args.dest.mkdir(parents=True, exist_ok=True)
    errors = []
    downloaded = 0
    for folder in folders:
        print_flush(f"\n[{folder.path}] dosyalari listeleniyor...")
        try:
            files = [entry for entry in api.list_repo_tree(
                repo_id=REPO,
                repo_type="dataset",
                path_in_repo=folder.path,
                recursive=True,
                expand=False,
                token=os.getenv("HF_TOKEN") or None,
            ) if isinstance(entry, RepoFile)]
        except Exception as exc:
            errors.append((folder.path, str(exc)))
            print_flush(f"Listeleme basarisiz: {type(exc).__name__}: {exc}")
            continue

        files.sort(key=lambda entry: (not entry.path.endswith("meta.csv"), entry.path))
        total_bytes = sum(getattr(entry, "size", 0) or 0 for entry in files)
        to_download = files if args.all else files[:args.limit]
        print_flush(f"Toplam {len(files)} dosya / yaklasik {total_bytes / 1024**3:.2f} GiB. "
                    f"Bu turda {len(to_download)} dosya hedefleniyor.")
        for index, entry in enumerate(to_download, 1):
            for attempt in range(1, 4):
                try:
                    hf_hub_download(
                        repo_id=REPO,
                        repo_type="dataset",
                        filename=entry.path,
                        local_dir=str(args.dest),
                        token=os.getenv("HF_TOKEN") or None,
                    )
                    downloaded += 1
                    if index == 1 or index % 10 == 0 or index == len(to_download):
                        print_flush(f"  {index}/{len(to_download)} kontrol edildi / indirildi")
                    break
                except KeyboardInterrupt:
                    print_flush("\nDurduruldu. Ayni komutla sonra devam edebilirsin.")
                    return 130
                except Exception as exc:
                    if attempt == 3:
                        print_flush(f"  HATA: {entry.path} -> {type(exc).__name__}: {exc}")
                        errors.append((entry.path, str(exc)))
                    else:
                        print_flush(f"  Yeniden denenecek ({attempt}/3): {entry.path}")
                        time.sleep(2 * attempt)

    print_flush(f"\nIslem tamamlandi. Basarili dosya islemi: {downloaded}; hata: {len(errors)}")
    print_flush(f"Kayit klasoru: {args.dest}")
    if errors:
        print_flush("Ilk hatalar:")
        for filename, error in errors[:5]:
            print_flush(f"  {filename} -> {error}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
