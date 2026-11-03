#!/usr/bin/env bash
# TÜBİTAK 2209-A / macOS Apple Silicon / Python 3.14
# Çalıştır: bash ~/Downloads/2209A_AASIST_kurulum_Python314.sh
# Çalışma klasörü: ~/Desktop/Tubitak (TUBITAK_ROOT ile değiştirilebilir)
set -euo pipefail

ROOT="${TUBITAK_ROOT:-$HOME/Desktop/Tubitak}"
ENV_DIR="$ROOT/.venv-aasist-py314"
SOURCE_DIR="$ROOT/aasist-source"
MODEL_DIR="$SOURCE_DIR/models/weights"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo 'HATA: Bu betik macOS için hazırlanmıştır.' >&2
  exit 1
fi
if ! command -v brew >/dev/null 2>&1; then
  echo 'HATA: Homebrew bulunamadı (https://brew.sh).' >&2
  exit 1
fi

printf '\n==> Python 3.14, FFmpeg, libsndfile ve Git kuruluyor/kontrol ediliyor\n'
brew install python@3.14 ffmpeg libsndfile git
PY314="$(brew --prefix python@3.14)/bin/python3.14"
if [[ ! -x "$PY314" ]]; then
  echo "HATA: Python 3.14 yürütücüsü bulunamadı: $PY314" >&2
  exit 1
fi
"$PY314" --version

mkdir -p "$ROOT" "$ROOT/models" "$ROOT/experiments"
if [[ ! -e "$ENV_DIR/pyvenv.cfg" ]]; then
  if [[ -e "$ENV_DIR" ]]; then
    echo "HATA: $ENV_DIR klasörü var fakat sanal ortam değil; otomatik silinmeyecek." >&2
    exit 1
  fi
  printf '\n==> Yeni Python 3.14 sanal ortamı oluşturuluyor\n'
  "$PY314" -m venv "$ENV_DIR"
else
  printf '\n==> Var olan Python 3.14 sanal ortamı kullanılacak\n'
fi
# shellcheck disable=SC1091
source "$ENV_DIR/bin/activate"
python - <<'PY'
import sys
assert sys.version_info[:2] == (3, 14), f"Sanal ortam Python 3.14 değil: {sys.version}"
print('Etkin Python:', sys.version.split()[0])
PY
python -m pip install --upgrade pip setuptools wheel
python -m pip install huggingface_hub
HF="$ENV_DIR/bin/hf"

printf '\n==> PyTorch ve TorchAudio yükleniyor (Python 3.14 destekli sürümler)\n'
python -m pip install 'torch>=2.11' 'torchaudio>=2.11'

printf '\n==> Ses işleme, veri analizi ve araştırma kütüphaneleri yükleniyor\n'
python -m pip install \
  numpy scipy soundfile librosa soxr \
  scikit-learn pandas pyarrow datasets huggingface_hub \
  matplotlib tqdm pyyaml tensorboard \
  transformers accelerate evaluate

# Resmî AASIST eğitim kodu SWA için bu eski paketi kullanır.
# Python 3.14'te desteği garanti olmadığından isteğe bağlıdır;
# başarısız olsa bile modelin çıkarım/test kurulumu tamamlanır.
printf '\n==> İsteğe bağlı AASIST eğitim yardımcısı: torchcontrib\n'
if ! python -m pip install torchcontrib; then
  echo 'UYARI: torchcontrib kurulamadı; Mac üzerinde model testi yapılabilir, eğitim için ortam uyarlaması gerekecek.' >&2
fi

printf '\n==> AASIST resmî kaynak kodu\n'
if [[ -f "$SOURCE_DIR/main.py" ]]; then
  echo "Mevcut AASIST kaynak kodu korunuyor: $SOURCE_DIR"
elif [[ -d "$SOURCE_DIR/.git" ]]; then
  echo "Mevcut AASIST Git deposu korunuyor: $SOURCE_DIR"
elif [[ -e "$SOURCE_DIR" ]]; then
  echo "HATA: $SOURCE_DIR mevcut ancak Git deposu değil. Klasörü silmeden kontrol edin." >&2
  exit 1
else
  git clone --depth 1 https://github.com/clovaai/aasist.git "$SOURCE_DIR"
fi

mkdir -p "$MODEL_DIR"
printf '\n==> Önceden eğitilmiş AASIST model ağırlığı indiriliyor\n'
if [[ ! -s "$MODEL_DIR/AASIST.pth" ]]; then
  "$HF" download SpeechAntiSpoofingBenchmarks/AASIST AASIST.pth --local-dir "$MODEL_DIR"
fi
if [[ ! -s "$MODEL_DIR/AASIST-L.pth" ]]; then
  curl -fL --retry 3 \
    -o "$MODEL_DIR/AASIST-L.pth" \
    https://raw.githubusercontent.com/clovaai/aasist/main/models/weights/AASIST-L.pth
fi

printf '\n==> Kütüphaneler, checkpoint ve CPU çıkarım testi\n'
AASIST_ROOT="$ROOT" python - <<'PY'
import importlib, json, os, sys
from pathlib import Path
root = Path(os.environ['AASIST_ROOT'])
for name in ('torch', 'torchaudio', 'numpy', 'scipy', 'soundfile', 'librosa',
             'sklearn', 'pandas', 'pyarrow', 'datasets', 'huggingface_hub',
             'matplotlib', 'transformers', 'accelerate', 'tensorboard'):
    importlib.import_module(name)
import torch
print('Python:', sys.version.split()[0])
print('PyTorch:', torch.__version__)
print('TorchAudio:', importlib.import_module('torchaudio').__version__)
print('MPS algılandı:', torch.backends.mps.is_available())
sys.path.insert(0, str(root / 'aasist-source'))
from models.AASIST import Model
config_file = root / 'aasist-source' / 'config' / 'AASIST.conf'
config = json.loads(config_file.read_text(encoding='utf-8'))
model = Model(config['model_config'])
for model_name in ('AASIST', 'AASIST-L'):
    model_config = json.loads(
        (root / 'aasist-source' / 'config' / f'{model_name}.conf').read_text()
    )
    model = Model(model_config['model_config'])
    weights = root / 'aasist-source' / 'models' / 'weights' / f'{model_name}.pth'
    state = torch.load(weights, map_location='cpu', weights_only=True)
    model.load_state_dict(state, strict=True)
    model.eval()
    with torch.inference_mode():
        _, logits = model(torch.zeros(1, 64600, dtype=torch.float32))
    assert logits.shape == (1, 2), f'{model_name}: beklenmeyen boyut {tuple(logits.shape)}'
    print(f'{model_name} modeli ve ağırlığı: OK; çıktı boyutu: {tuple(logits.shape)}')
print('BAŞARILI: AASIST çıkarım testi tamamlandı (CPU).')
PY

printf '\n==> FFmpeg sürümü\n'
ffmpeg -version | sed -n '1p'
printf '\nKurulum tamamlandı.\n'
printf 'Sanal ortamı etkinleştir: source "%s/bin/activate"\n' "$ENV_DIR"
printf 'AASIST kaynak kodu: %s\n' "$SOURCE_DIR"
printf 'Model ağırlıkları: %s/AASIST.pth ve %s/AASIST-L.pth\n' "$MODEL_DIR" "$MODEL_DIR"
printf 'NOT: Bu doğrulama CPU içindir; Türkçe eğitimde --device auto|cpu|mps|cuda kullanabilirsiniz.\n'
