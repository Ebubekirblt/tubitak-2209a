# Türkçe Ses Sahteciliği Tespit Projesi

Türkçe konuşma verilerinde gerçek ve yapay/sentetik sesleri ayırt etmek için
AASIST, RawNet2 ve RawGAT-ST tabanlı deneyleri içeren araştırma deposu.
Deneylerde yalnızca Türkçe veri kaynakları kullanılacaktır.

> **Durum:** Araştırma ve geliştirme aşamasındadır. Sonuçlar üretim kullanımı
> için doğrulanmamıştır.

## Depo yapısı

```text
.
├── aasist-source/       # Eğitim, değerlendirme ve model kodu
│   ├── config/          # Deney yapılandırmaları
│   └── models/          # AASIST, RawNet2 ve RawGAT-ST mimarileri
├── dataset/             # Yerel veri setleri (Git'e eklenmez)
├── docs/                # Proje ve teknik belgeler
├── experiments/         # Yerel deney çıktıları (Git'e eklenmez)
├── scripts/             # Kurulum, veri, eğitim ve doğrulama yardımcıları
├── setup-macos.sh       # macOS tek giriş noktası
└── setup-windows.ps1    # Windows tek giriş noktası
```

Büyük veri setleri, önceden eğitilmiş ağırlıklar ve sanal ortam dosyaları
`.gitignore` ile dışarıda tutulur. Veri setlerinin lisans ve kullanım
koşullarına uymak proje kullanıcısının sorumluluğundadır.

ASVspoof veri setleri bu projede kullanılmaz. AASIST'in orijinal
ASVspoof-uyumlu veri yükleyicisi yerine Türkçe veri setleri için bir manifest
ve veri yükleyici katmanı kullanılmalıdır.

RawNet2 ve RawGAT-ST, ham ses sinyali üzerinde çalışan ve belirli bir dile
bağlı olmayan mimarilerdir; Türkçe veriyle eğitilebilirler. Ancak bu depoda
onlara ait Türkçe ön-eğitimli ağırlık bulunmamaktadır. Modelleri kullanmak
için Türkçe manifest/veri yükleyici uyarlaması ve Türkçe veriyle yeniden
eğitim gerekir.

## Tek yerde kurulum ve kullanım

Bu bölüm Türkçe deneyler için önerilen akıştır. Komutları depo kökünde
çalıştırın. Linux/macOS için `python3`, Windows için `python` veya sanal
ortamın Python yürütücüsü kullanılabilir.

### Doğrudan tek komut

Depo kökünden platformunuza uygun giriş betiğini çalıştırın. Betikler eksik
araçları, Python 3.14 sanal ortamını, Python bağımlılıklarını, AASIST
kaynak kodunu, model ağırlıklarını ve CPU/GPU doğrulamasını kontrol edip
tamamlar. Var olan dosyalar silinmez.

macOS:

```bash
bash setup-macos.sh
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1
```

Windows giriş betiği varsayılan olarak veri seti indirmelerini de başlatır.
İlk kurulumda yalnızca ortam ve model kontrolü için
`.\setup-windows.ps1 -Mode Setup` kullanılabilir. MLAAD'ın tamamı büyük
olduğundan varsayılan
örneklem korunur; tamamı için `-Mode MLAAD -MlaadFull` eklenir.

Repo yapısı, manifest biçimi ve Python sözdizimi için:

```bash
make check
```

Komutların tamamı ve kullanım amaçları
[scripts/README.md](scripts/README.md) içindeki katalogda tutulur.

### 1. Ortam kurulumu

macOS Apple Silicon:

```bash
bash scripts/2209A_AASIST_kurulum_Python314.sh
source .venv-aasist-py314/bin/activate
```

Windows 10/11 x64 (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1 -Mode Setup
.\scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1 -Mode Datasets
```

Windows scripti masaüstündeki `Tubitak` klasörünü oluşturur ve mevcut
`aasist-source` klasörünü korur. `-Mode All` iki adımı tek seferde çalıştırır:

```powershell
.\scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1 -Mode All -MlaadLimit 20
```

Manuel kurulum:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r aasist-source/requirements.txt
python -m pip install huggingface_hub
```

Manuel kurulum için Python 3.10 veya üzeri gerekir. Hazır macOS ve Windows
kurulum scriptleri Python 3.14 hedefler.

### 2. Veri setlerini hazırlama

Windows `-Mode All` Türkçe veri setlerini indirir. macOS veya manuel kurulumda
veri setlerini sağlayıcılarından indirip `dataset/` altına yerleştirin.
Hugging Face erişimi istenirse token'ı terminalde veya CLI ile tanımlayın;
koda yazmayın:

```bash
hf auth login
python scripts/mlaad_tr_dilimli_indir.py --list
python scripts/mlaad_tr_dilimli_indir.py --model bark --limit 20
```

MLAAD'ın tüm Türkçe dosyaları büyük olabilir:

```bash
python scripts/mlaad_tr_dilimli_indir.py --all
```

FLEURS arşivlerini ve diğer `.tar.gz` dosyalarını çıkarıp manifest oluşturun:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --extract-archives
```

Bu işlem `dataset/turkish_manifest.jsonl` üretir. Gerçek sesler `1`, sentetik
sesler `0` etiketlenir; mevcut train/dev/test klasörleri korunur, klasörsüz
dosyalar deterministik olarak bölünür.

MLAAD içinden görülmemiş bir TTS üreticisini testte tutmak için üretici adı
manifestte korunur. Örneğin:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --holdout-generator OmniVoice
```

Bu seçenek eşleşen üreticinin kayıtlarını yalnızca testte bırakır. Bu deney,
aynı TTS üreticisinin train ve testte bulunmasına göre daha anlamlı bir
genelleme ölçümüdür.

Manifest üreticisi her train/dev/test bölümünde hem gerçek (`1`) hem sentetik
(`0`) sınıf bulunmasını zorunlu kılar; dengesiz veya eksik bir deney sessizce
başlamaz.

Telefon kanalı deney setini üretmek için:

```bash
python scripts/create_phone_channel_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_phone_manifest.jsonl
```

Bu işlem sesleri 8 kHz dar bant ve G.711 mu-law kuantalama ile
`dataset/phone_channel_8k/` altına kopyalar. Eğitimde bu manifesti kullanın:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_phone_manifest.jsonl \
  --config aasist-source/config/AASIST.conf \
  --weights aasist-source/models/weights/AASIST.pth
```

Bu, telefon kanalının yeniden üretilebilir bir G.711/narrowband simülasyonudur;
gerçek GSM/VoIP ağ koşullarının tamamını temsil etmez. Yayın deneyinde ayrıca
gerçek kodek kayıtları veya FFmpeg tabanlı GSM/Opus varyantları test edilmelidir.

### 3. Modelleri doğrulama

```bash
python scripts/verify_models.py
```

Beklenen çıktı:

```text
AASIST: OK (1, 2)
AASIST-L: OK (1, 2)
RawNet2: OK (1, 2)
RawGAT-ST: OK (1, 2)
```

### 4. Türkçe eğitim

#### Otomatik pipeline

Manifest oluşturma, model doğrulama ve eğitimi tek komutta çalıştırmak için:

```bash
python scripts/run_turkish_pipeline.py \
  --models AASIST \
  --extract-archives \
  --phone-channel \
  --holdout-generator OmniVoice \
  --epochs 1 \
  --batch-size 4
```

Tüm mimarileri sırayla eğitmek için `--models all` kullanın. Sadece veri
hazırlamak için `--prepare-only`, model doğrulamasını atlamak için
`--skip-verify` eklenebilir. `--phone-channel` 8 kHz/G.711 simülasyonunu
otomatik üretir; `--holdout-generator` görülmemiş TTS testini etkinleştirir.
Pipeline sonunda
`experiments/turkish/run_summary.json` oluşturulur.
`--models XLSR` seçeneği wav2vec2-XLS-R kolunu pipeline'a dahil eder; model
ilk kullanımda Hugging Face'ten indirilir.

### XLS-R ve gerçek codec deneyleri

XLS-R ince ayarı için:

```bash
python scripts/train_xlsr_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --model facebook/wav2vec2-xls-r-300m \
  --epochs 3
```

İlk çalıştırmada model Hugging Face'ten indirilir; ağırlıklar Git'e eklenmez.
Common Voice TR'den sınırlı bir WAV alt kümesi almak için:

```bash
python scripts/download_commonvoice_tr.py --limit 1000
```

FFmpeg kurulu ve ilgili encoder'ı içeriyorsa gerçek GSM, AMR-NB veya Opus
round-trip testi üretilebilir:

```bash
python scripts/create_real_codec_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_gsm_manifest.jsonl \
  --output-dir dataset/real_codec_gsm \
  --codec gsm
```

AMR-NB için `--codec amr_nb`, Opus için `--codec opus` kullanın. Encoder
kurulu değilse script açık hata verir; G.711 simülasyonuna sessizce dönmez.

Apple Silicon MPS doğrulaması:

```bash
python scripts/verify_models.py --device mps
```

AASIST:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/AASIST.conf \
  --weights aasist-source/models/weights/AASIST.pth
```

AASIST-L:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/AASIST-L.conf \
  --weights aasist-source/models/weights/AASIST-L.pth
```

RawNet2:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawNet2.conf
```

RawGAT-ST:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawGATST.conf
```

İlk kontrol için `--epochs 1 --batch-size 4` ekleyin. Gerçek deneylerde
GPU önerilir:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawNet2.conf \
  --epochs 30 \
  --batch-size 16
```

Türkçe eğitim scripti varsayılan olarak çalışma dizininden bağımsız biçimde
repo içindeki `experiments/turkish/<model>/` klasörüne yazar. Her modelin
checkpoint'i `best.pth` adını alır ve Git'e eklenmez. `--output` verirseniz
özel çıktı yolunu siz belirlersiniz.
Değerlendirme/test metrikleri terminalde gösterilir ve `metrics.json` içine de
kaydedilir; en iyi ağırlık `best.pth` olarak kaydedilir.

### 5. Sorun giderme

- `No WAV files found`: veri setleri `dataset/` altında değil veya arşivler
  çıkarılmamış; `--extract-archives` kullanın.
- `huggingface_hub` hatası: sanal ortamı etkinleştirip `pip install
  huggingface_hub` çalıştırın.
- CUDA yoksa eğitim CPU'da çalışır ancak çok yavaş olabilir.
- Apple Silicon'da `--device auto` MPS'yi seçer; sorun yaşanırsa
  `--device cpu` kullanın.
- Windows'ta CUDA için NVIDIA sürücüsü gerekir; CUDA Toolkit'i ayrıca kurmak
  çoğu PyTorch wheel'i için gerekmez.
- `AASIST.pth`/`AASIST-L.pth` eksikse macOS/Windows kurulum scriptini tekrar
  çalıştırın.
- Orijinal `aasist-source/main.py` ASVspoof formatı içindir; Türkçe deneylerde
  bu dosya yerine `scripts/train_turkish.py` kullanılmalıdır.

### Platform gerçekliği

Kurulum scriptleri bağımlılıkları ve AASIST/AASIST-L başlangıç ağırlıklarını
iki platformda da kurar. RawNet2 ve RawGAT-ST için Türkçe hazır ağırlık yoktur;
Türkçe manifest ile yeniden eğitim gerekir. Windows scripti public Hugging Face
verilerini login olmadan dener, erişim hatasında `hf auth login` yeterlidir.
macOS scripti Apple Silicon içindir; Intel Mac'te manuel kurulum kullanılmalıdır.

## Geliştirme

Değişiklikleri küçük ve odaklı tutun; yeni deneylerde kullanılan veri,
konfigürasyon ve metrikleri açıklayın. Kaynak kodu değişikliklerini göndermeden
önce aşağıdaki hızlı kontrolü çalıştırın:

```bash
python -m compileall -q aasist-source
```

Katkı ayrıntıları için [`CONTRIBUTING.md`](CONTRIBUTING.md) dosyasına bakın.

Script ayrıntıları için [`scripts/README.md`](scripts/README.md), veri
kaynakları için [`dataset/readme.md`](dataset/readme.md) dosyasına bakın.

## Lisans ve atıflar

Kaynak kodu lisansları için [`LICENSE`](LICENSE) ve üçüncü taraf bildirimleri
için [`NOTICE`](NOTICE) dosyalarını inceleyin. AASIST çalışması ve kullanılan
veri setleri için kaynaklar [`aasist-source/README.md`](aasist-source/README.md)
dosyasında listelenmiştir.
