# Script kataloğu

Tüm komutlar depo kökünden çalıştırılır. Python scriptleri için kurulumdan
sonra sanal ortamı etkinleştirin. Scriptler veri setlerini, model ağırlıklarını
ve deney çıktısını Git’e eklemez.

## Kurulum

| Script | Platform | Görev |
|---|---|---|
| [`../setup-macos.sh`](../setup-macos.sh) | macOS Apple Silicon | Tek komutla macOS ortam kurulumu |
| [`../setup-windows.ps1`](../setup-windows.ps1) | Windows 10/11 x64 | Tek komutla Windows ortam/veri kurulumu |
| [`2209A_AASIST_kurulum_Python314.sh`](2209A_AASIST_kurulum_Python314.sh) | macOS | Ayrıntılı Python, bağımlılık ve ağırlık kurulumu |
| [`TUBITAK_2209A_Windows_Tek_Script-2.ps1`](TUBITAK_2209A_Windows_Tek_Script-2.ps1) | Windows | Ayrıntılı kurulum ve veri seçenekleri |
| [`check_repository.py`](check_repository.py) | Tüm platformlar | Repo ve manifest kalite kontrolü |

```bash
python3 scripts/check_repository.py
```

## Veri hazırlama

| Script | Görev |
|---|---|
| [`create_turkish_manifest.py`](create_turkish_manifest.py) | Veri klasörlerinden Türkçe JSONL manifest üretir |
| [`download_commonvoice_tr.py`](download_commonvoice_tr.py) | Common Voice TR kayıtlarını WAV olarak dışa aktarır |
| [`mlaad_tr_dilimli_indir.py`](mlaad_tr_dilimli_indir.py) | MLAAD Türkçe klasörlerini sınırlı veya tam indirir |
| [`create_phone_channel_manifest.py`](create_phone_channel_manifest.py) | 8 kHz/G.711 telefon kanalı simülasyonu üretir |
| [`create_real_codec_manifest.py`](create_real_codec_manifest.py) | FFmpeg ile GSM/AMR-NB/Opus varyantı üretir |

Önerilen sıra:

```bash
python scripts/create_turkish_manifest.py --root dataset --extract-archives
python scripts/create_phone_channel_manifest.py
```

`create_turkish_manifest.py` seçenekleri:

```text
--root PATH
--output PATH
--extract-archives
--holdout-generator NAME
```

Common Voice ve MLAAD örnekleri:

```bash
python scripts/download_commonvoice_tr.py --limit 1000
python scripts/download_commonvoice_tr.py --all
python scripts/mlaad_tr_dilimli_indir.py --list
python scripts/mlaad_tr_dilimli_indir.py --limit 20
python scripts/mlaad_tr_dilimli_indir.py --all
```

Tam MLAAD indirmesi büyük olabilir. Hugging Face kimlik doğrulaması
gerekiyorsa token’ı script içine yazmadan `hf auth login` kullanın.
`gdown`, yalnızca `-IncludeASR` ile istenen opsiyonel TurkicASR arşivi için
kurulur; ana Türkçe sahtecilik akışı için gerekli değildir.

## Eğitim ve doğrulama

| Script | Görev |
|---|---|
| [`run_turkish_pipeline.py`](run_turkish_pipeline.py) | Manifest, doğrulama ve eğitim akışını birleştirir |
| [`train_turkish.py`](train_turkish.py) | Tek bir Türkçe modelini eğitir |
| [`metrics.py`](metrics.py) | EER, ROC-AUC, F1 ve sınıflandırma metriklerini hesaplar |
| [`train_xlsr_turkish.py`](train_xlsr_turkish.py) | XLS-R ince ayarı yapar |
| [`verify_models.py`](verify_models.py) | Yerel model ileri geçişini doğrular |

Pipeline:

```bash
python scripts/run_turkish_pipeline.py \
  --models AASIST \
  --extract-archives \
  --epochs 1 \
  --batch-size 4 \
  --device auto
```

Pipeline modelleri: `AASIST`, `AASIST-L`, `RawNet2`, `RawGAT-ST`, `XLSR`
ve `all`. Yararlı seçenekler:

```text
--manifest PATH
--phone-channel
--holdout-generator NAME
--prepare-only
--skip-verify
--device auto|cpu|cuda|mps
--epochs N
--batch-size N
```

Tek model:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawNet2.conf \
  --device auto
```

`--weights` başlangıç ağırlığı, `--output` deney klasörü, `--seed` deney
tekrarlanabilirliği için kullanılır. Test değerlendirmesi en iyi dev checkpoint
üzerinde yapılır. `metrics.json` içinde EER, ROC-AUC, F1, precision, recall,
balanced accuracy ve confusion matrix kaydedilir. Varsayılan çıktılar
`experiments/turkish/` altındadır.

Model doğrulama:

```bash
python scripts/verify_models.py --model all --device cpu
python scripts/verify_models.py --model AASIST --device mps
```

## Platform notları

- macOS Apple Silicon: `auto` MPS’yi seçebilir; sorun olursa `cpu` kullanın.
- Windows NVIDIA: uyumlu NVIDIA sürücüsü ve CUDA uyumlu PyTorch kurulumu
  gerekir.
- Windows CPU: çalışır ancak eğitim yavaştır.
- Linux: platform kurulum betiği yoktur; manuel sanal ortam kurun.

Türkçe deneylerde eski ASVspoof akışı olan `aasist-source/main.py` yerine
`run_turkish_pipeline.py` veya `train_turkish.py` kullanın.
