# Türkçe Ses Sahteciliği Tespit Projesi

Türkçe konuşmalarda gerçek insan sesini yapay/sentetik sesten ayırmak için
AASIST, RawNet2, RawGAT-ST ve XLS-R tabanlı deneyler içeren araştırma
deposudur.

> **Durum:** Araştırma ve geliştirme aşamasındadır. Sonuçlar üretim kullanımı
> için doğrulanmamıştır.

## Hızlı başlangıç

Komutları her zaman depo kökünde çalıştırın.

### 1. Ortamı kurun

macOS Apple Silicon:

```bash
bash setup-macos.sh
source .venv-aasist-py314/bin/activate
```

Windows 10/11 x64 PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1 -Mode Setup
```

Windows’ta veri setleri de indirilecekse:

```powershell
.\setup-windows.ps1 -Mode All -MlaadLimit 20
```

Kurulum betikleri mevcut dosyaları silmez. macOS betiği Apple Silicon için
hazırlanmıştır; Windows betiği x64 içindir. Linux için ortamı elle kurun:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r aasist-source/requirements.txt
python -m pip install huggingface_hub
```

### 2. Veri setlerini hazırlayın

Windows `-Mode All` veri setlerini indirmeyi dener. Diğer platformlarda veri
sağlayıcılarının lisans ve erişim koşullarına uyarak veri setlerini
`dataset/` altına yerleştirin. Sonra manifest üretin:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --extract-archives
```

Bu komut `dataset/turkish_manifest.jsonl` üretir. Gerçek kayıtlar `label=1`,
sentetik kayıtlar `label=0` olarak işaretlenir. Her split’te iki sınıfın da
bulunması gerekir.

### 3. Modelleri doğrulayın

Bağımlılıkların kurulu olduğu ortamı etkinleştirdikten sonra:

```bash
python scripts/verify_models.py --device cpu
```

Apple Silicon için `--device mps`, NVIDIA için `--device cuda` kullanılabilir.
Bu kontrol RawNet2 ve RawGAT-ST dahil yerel model mimarilerinin ileri geçişini
doğrular; veri indirmez.

### 4. Türkçe eğitim pipeline’ını çalıştırın

Manifest hazırlama, model doğrulama ve eğitimi tek akışta çalıştırmak için:

```bash
python scripts/run_turkish_pipeline.py \
  --models AASIST \
  --extract-archives \
  --epochs 1 \
  --batch-size 4
```

`--models all` ile `AASIST`, `AASIST-L`, `RawNet2`, `RawGAT-ST` ve `XLSR`
kollarını seçebilirsiniz. İlk denemelerde düşük epoch/batch değerleri
kullanın. Sadece manifest ve hazırlık için `--prepare-only`, model kontrolünü
atlamak için `--skip-verify` eklenebilir.

Pipeline seçenekleri:

```text
--device auto|cpu|cuda|mps
--phone-channel
--holdout-generator OmniVoice
--prepare-only
--skip-verify
```

## Veri ve deney akışları

Telefon kanalı simülasyonu:

```bash
python scripts/create_phone_channel_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_phone_manifest.jsonl
```

Gerçek codec deneyi için FFmpeg gerekir:

```bash
python scripts/create_real_codec_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_gsm_manifest.jsonl \
  --output-dir dataset/real_codec_gsm \
  --codec gsm
```

Common Voice TR dışa aktarma:

```bash
python scripts/download_commonvoice_tr.py --limit 1000
python scripts/download_commonvoice_tr.py --all
```

MLAAD Türkçe örneklemi:

```bash
python scripts/mlaad_tr_dilimli_indir.py --list
python scripts/mlaad_tr_dilimli_indir.py --limit 20
python scripts/mlaad_tr_dilimli_indir.py --all
```

XLS-R ince ayarı:

```bash
python scripts/train_xlsr_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --epochs 3
```

Tüm scriptlerin seçenekleri ve görevleri için
[scripts/README.md](scripts/README.md) dosyasına bakın.

## Dizin yapısı

```text
.
├── aasist-source/       # Model kodu ve config dosyaları
├── dataset/             # Yerel veri setleri ve manifestler
├── docs/                # Plan, günlük ve referans belgeleri
├── experiments/         # Yerel checkpoint ve deney çıktıları
├── scripts/             # Veri, eğitim, indirme ve doğrulama araçları
│   └── README.md        # Ayrıntılı komut kataloğu
├── setup-macos.sh       # macOS giriş betiği
├── setup-windows.ps1    # Windows giriş betiği
└── Makefile             # Repo kalite komutları
```

Veri setleri, model ağırlıkları, sanal ortamlar ve deney çıktıları Git’e
eklenmez. Lisans ve kullanım koşullarını her veri sağlayıcısı için ayrıca
kontrol edin.

## Model ve veri sınırları

- Bu proje ASVspoof veri setlerini kullanmaz.
- `aasist-source/main.py` eski ASVspoof uyumlu akıştır; Türkçe deneylerde
  `scripts/train_turkish.py` veya pipeline kullanılmalıdır.
- RawNet2 ve RawGAT-ST için bu repoda Türkçe hazır ağırlık yoktur; Türkçe
  manifest ile yeniden eğitim gerekir.
- `AASIST.pth` ve `AASIST-L.pth` yalnızca kurulum betikleriyle sağlanan
  başlangıç ağırlıklarıdır; Türkçe performans garantisi vermez.

## Repo kontrolleri

```bash
make check
make compile
```

`make check` repo yapısını, manifest JSONL biçimini ve Python sözdizimini
kontrol eder. CI da aynı kontrolleri çalıştırır.

## Belgeler

- [Script kataloğu](scripts/README.md)
- [Veri setleri](dataset/readme.md)
- [Deney çıktıları](experiments/README.md)
- [Proje belgeleri](docs/README.md)
- [Katkı rehberi](CONTRIBUTING.md)
