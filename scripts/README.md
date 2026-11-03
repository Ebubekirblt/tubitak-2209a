# Kurulum ve veri scriptleri

Bu klasörde platforma ve kullanım amacına göre yardımcı scriptler bulunur.
Scriptler veri setlerini ve model ağırlıklarını yerel diske indirir; indirilen
dosyalar kök `.gitignore` kuralları nedeniyle Git'e eklenmez.

## Kurulum kapsamı

| Bileşen | macOS scripti | Windows `-Mode All` |
|---|---:|---:|
| Python 3.14 ve bağımlılıklar | Evet | Evet |
| AASIST ve AASIST-L ağırlıkları | Evet | Evet |
| Türkçe veri setleri | Hayır | Evet, MLAAD sınırlı örneklem |
| ASVspoof2019 LA | Kullanılmıyor | Kullanılmıyor |
| RawNet2 / RawGAT-ST Türkçe hazır ağırlıkları | Hayır | Hayır |

Bu proje Türkçe veri kaynaklarıyla çalışır; ASVspoof2019 ve ASVspoof2021
kullanılmaz. Mevcut `aasist-source/main.py` eğitim/değerlendirme akışı
ASVspoof2019 LA klasör yapısını beklediği için Türkçe veri setleriyle doğrudan
çalıştırılmamalıdır. Türkçe eğitim için sağlanan manifest ve `Dataset` akışı
olan `scripts/train_turkish.py` kullanılmalıdır.

## Platform uyumluluğu

| Platform | Kurulum | Eğitim | Not |
|---|---|---|---|
| macOS Apple Silicon | macOS scripti | CPU veya MPS | `auto` MPS'yi seçer; sorun olursa CPU kullanılabilir |
| Windows 10/11 x64 + NVIDIA | Windows scripti | CUDA | Uyumlu NVIDIA sürücüsü gerekir |
| Windows 10/11 x64 CPU | Windows scripti | CPU | Çalışır ancak yavaştır |
| Linux | Manuel kurulum | CPU/CUDA | Platform scriptleri Linux için değildir |

Model mimarileri iki platformda da aynıdır. İyi Türkçe sonuç için gerçek ve
sentetik Türkçe verilerle eğitim yapılması gerekir; başlangıç AASIST ağırlığı
Türkçe ön-eğitimli değildir.

| Script | Platform | Kullanım |
|---|---|---|
| [`2209A_AASIST_kurulum_Python314.sh`](2209A_AASIST_kurulum_Python314.sh) | macOS Apple Silicon | Python 3.14 ortamı, bağımlılıklar ve AASIST/AASIST-L ağırlıkları |
| [`TUBITAK_2209A_Windows_Tek_Script-2.ps1`](TUBITAK_2209A_Windows_Tek_Script-2.ps1) | Windows 10/11 x64 | Gerekirse `Desktop/Tubitak` klasörünü oluşturur; kurulum, veri seti ve iki AASIST ağırlığı |
| [`mlaad_tr_dilimli_indir.py`](mlaad_tr_dilimli_indir.py) | Python | MLAAD Türkçe klasörlerinden sınırlı veya tam indirme |
| [`verify_models.py`](verify_models.py) | Python | AASIST, RawNet2 ve RawGAT-ST mimarilerinin yerel ileri geçiş kontrolü |
| [`train_xlsr_turkish.py`](train_xlsr_turkish.py) | Python | wav2vec2-XLS-R Türkçe ince ayarı |
| [`download_commonvoice_tr.py`](download_commonvoice_tr.py) | Python | Common Voice TR alt kümesini WAV olarak dışa aktarma |
| [`create_real_codec_manifest.py`](create_real_codec_manifest.py) | Python + FFmpeg | GSM/Opus gerçek codec round-trip manifesti |

## macOS

```bash
bash scripts/2209A_AASIST_kurulum_Python314.sh
```

Farklı bir depo yolu için `TUBITAK_ROOT` ortam değişkeni kullanılabilir. Script
mevcut `aasist-source` klasörünü de kullanır; resmi depoyu yalnızca kaynak
klasörü yoksa klonlar. Ağırlık `aasist-source/models/weights/AASIST.pth`
konumuna indirilir.

## Windows

PowerShell'de:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1
```

Script varsayılan olarak masaüstündeki `Tubitak` klasörünü kullanır; klasör
yoksa ve gerekli üst klasörler mevcutsa otomatik olarak oluşturur. Mevcut
`aasist-source` klasörünü kullanır ve AASIST ve AASIST-L ağırlıklarını `aasist-source/models/weights/` konumuna
indirir. RawNet2 ve RawGAT-ST için Türkçe hazır ağırlık indirme adımı yoktur; mimariler
Türkçe veriyle yeniden eğitilmelidir. Ayrıntılı
seçenekler için:

```powershell
Get-Help .\scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1 -Full
```

## MLAAD Türkçe veri indirme

Önce `huggingface_hub` paketini kurun veya kurulum scriptlerinin oluşturduğu
sanal ortamı etkinleştirin:

```bash
python -m pip install huggingface_hub
```

```bash
python scripts/mlaad_tr_dilimli_indir.py --list
python scripts/mlaad_tr_dilimli_indir.py --model bark --limit 20
python scripts/mlaad_tr_dilimli_indir.py --all
```

Tam indirme çok büyük olabilir. Kimlik doğrulama gerekiyorsa Hugging Face
CLI ile giriş yapın; token'ı script içine yazmayın.

## Model ağırlığı durumu

Kurulum scriptleri resmi AASIST kaynaklarından `AASIST.pth` ve
`AASIST-L.pth` dosyalarını indirir ve ikisini de CPU ileri geçiş testiyle
doğrular. RawNet2 ve RawGAT-ST kaynak kodları depoda bulunur; bu proje için hazır
ağırlıkları yoktur. Türkçe eğitim scripti `model_path` yerine açıkça verilen
`--weights` dosyasını kullanır ve varsayılan olarak checkpoint'i repo içindeki
`experiments/turkish/<model>/best.pth` konumuna yazar. Bu iki modeli
değerlendirmeden önce eğitim yapıp ağırlık üretmek gerekir.

Windows `-Mode All` Türkçe veri kaynaklarını indirir: Common Voice TR,
FLEURS TR, girenit-tts-tr-synthetic, Synthetic Turkish TTS Data ve sınırlı
MLAAD örnekleri. MLAAD'ın tamamı için `-Mode MLAAD -MlaadFull` kullanılabilir.

## Türkçe manifest ve eğitim

### Tek komut pipeline

`run_turkish_pipeline.py` veri manifestini üretir, mimarileri doğrular ve
seçilen modelleri sırayla eğitir:

```bash
python scripts/run_turkish_pipeline.py --models AASIST --phone-channel --epochs 1 --batch-size 4
```

`--models all` dört yerel mimariyi ve XLS-R kolunu çalıştırır. `--prepare-only` yalnızca manifest
hazırlar. Varsayılan çıktıların tamamı repo içindeki
`experiments/turkish/` klasöründedir; işlem özeti
`experiments/turkish/run_summary.json` dosyasına yazılır.
`--holdout-generator OmniVoice` görülmemiş TTS üreticisini testte tutar.
Manifest üretimi ayrıca her üç split'te de gerçek ve sentetik sınıfların
bulunduğunu doğrular; eksik sınıf varsa eğitim başlamadan hata verir.

XLS-R ilk çalıştırmada `facebook/wav2vec2-xls-r-300m` modelini indirir.
Apple Silicon MPS kontrolü için `python scripts/verify_models.py --device mps`
çalıştırılabilir.

Common Voice TR'nin seçili train/validation/test split'lerindeki tüm kayıtları
indirmek için `--all` kullanılır. Veri sürümüne göre kayıt sayısı değişebilir
ve işlem uzun sürebilir:

```bash
python scripts/download_commonvoice_tr.py --all
```

Önce WAV arşivlerini çıkarıp ortak manifesti oluşturun:

```bash
python scripts/create_turkish_manifest.py --root dataset --extract-archives
```

Telefon kanalı koşulunu üretmek için `create_phone_channel_manifest.py`
kullanılır. Sesler 8 kHz dar banda indirilir ve G.711 mu-law kuantalamasından
geçirilir; çıktı ayrı manifest ve klasörde tutulur.

Manifestte gerçek sesler `label=1`, sentetik sesler `label=0` olarak tutulur.
`FLEURS_TR` ve Common Voice gerçek ses; `MLAAD`, `girenit` ve
`Synthetic_Turkish_TTS_Data` sentetik ses olarak işaretlenir.

MLAAD üretici adı ayrıca `generator` alanına yazılır. Görülmemiş üretici
genellemesini ölçmek için manifest oluştururken örneğin
`--holdout-generator OmniVoice` kullanın.

RawNet2 eğitimi:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawNet2.conf
```

Donanımı elle seçmek için `--device auto|cpu|cuda|mps` kullanılabilir.

RawGAT-ST eğitimi için config yolunu değiştirin:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawGATST.conf
```

Model çıktıları varsayılan olarak `experiments/turkish/<model>/` altına yazılır
ve Git'e eklenmez; böylece farklı modeller birbirinin `best.pth` dosyasını
ezmez.
İlk denemelerde `--epochs 1 --batch-size 4` kullanılabilir. Eğitim için
gerçek ve sentetik sınıfların her iki split'te de bulunması gerekir.

Kurulumdan sonra tüm mimarileri kontrol etmek için:

```bash
python scripts/verify_models.py
```

Bu kontrol ağırlık indirmez; model sınıflarının ve Türkçe ham ses giriş
şeklinin çalıştığını doğrular. RawNet2 ve RawGAT-ST için Türkçe ağırlık
üretmek üzere Türkçe gerçek/sentetik manifest ile eğitim yapılmalıdır.
