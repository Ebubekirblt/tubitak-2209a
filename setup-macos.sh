#!/usr/bin/env bash
# TÜBİTAK Türkçe ses sahteciliği projesi - macOS tek giriş betiği.
#
# Kullanım:
#   bash setup-macos.sh
#   TUBITAK_ROOT=/path/to/Tubitak bash setup-macos.sh
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
INSTALLER="$SCRIPT_DIR/scripts/2209A_AASIST_kurulum_Python314.sh"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "HATA: Bu betik yalnızca macOS üzerinde çalışır." >&2
  exit 1
fi

if [[ ! -f "$INSTALLER" ]]; then
  echo "HATA: Kurulum betiği bulunamadı: $INSTALLER" >&2
  exit 1
fi

export TUBITAK_ROOT="${TUBITAK_ROOT:-$SCRIPT_DIR}"
printf 'TÜBİTAK kurulumu başlatılıyor: %s\n' "$TUBITAK_ROOT"
exec bash "$INSTALLER"
