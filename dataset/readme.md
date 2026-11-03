# Veri setleri

Bu klasör gerçek Türkçe konuşmaları, sentetik Türkçe konuşmaları ve bunlardan
üretilen manifestleri içerir. Büyük dosyalar Git’e eklenmez; yalnızca README
ve küçük metadata dosyaları sürümlenir.

## Veri kaynakları

| Klasör | Tür | Kullanım |
|---|---|---|
| `commonvoice_17_tr_fixed/` | Gerçek | İnsan konuşması |
| `FLEURS_TR/` | Gerçek | İnsan konuşması ve değerlendirme |
| `MLAAD/` | Sentetik | TTS üreticileri arası çeşitlilik |
| `girenit-tts-tr-synthetic/` | Sentetik | Türkçe TTS örnekleri |
| `Synthetic_Turkish_TTS_Data/` | Sentetik | Parquet tabanlı TTS verisi |
| `turkic_languages_model/` | Yardımcı ASR | İsteğe bağlı, sahtecilik sınıfı değildir |

Windows’ta indirme akışı için:

```powershell
.\setup-windows.ps1 -Mode All -MlaadLimit 20
```

Manuel/ macOS akışında veri sağlayıcılarından dosyaları ilgili klasörlere
yerleştirin. Lisans, atıf, erişim ve yeniden dağıtım koşullarını ayrıca
inceleyin.

## Manifest üretimi

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --output dataset/turkish_manifest.jsonl \
  --extract-archives
```

Manifest alanları veri kaynağına göre `path`, `label`, `split` ve varsa
`generator`/metadata alanlarını içerir. Bu projede:

- `label=1`: gerçek insan sesi
- `label=0`: sentetik/yapay ses

Eğitimden önce manifestte `train`, `dev` ve `test` split’lerinin ve iki sınıfın
da bulunduğunu kontrol edin. Görülmemiş üretici deneyi için:

```bash
python scripts/create_turkish_manifest.py \
  --holdout-generator OmniVoice
```

## Kanal ve codec varyantları

Telefon kanalı simülasyonu:

```bash
python scripts/create_phone_channel_manifest.py
```

Gerçek codec varyantları için FFmpeg gerekir:

```bash
python scripts/create_real_codec_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_opus_manifest.jsonl \
  --output-dir dataset/real_codec_opus \
  --codec opus
```

Codec scripti encoder bulunamadığında sessizce başka codec’e dönmez; hatayı
gösterir.
