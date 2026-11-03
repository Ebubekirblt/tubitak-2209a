# 2026-11-03 Geliştirme Günlüğü

Bu belge, 3 Kasım 2026 tarihinde Türkçe telefon kanalı deepfake ses tespiti
projesinde yapılan geliştirmeleri, alınan kararları ve doğrulamaları özetler.

## Projenin hedefi

Proje, Türkçe konuşmalarda gerçek insan sesleri ile TTS/üretici tabanlı sahte
sesleri ayırt eden bir sistem geliştirmeyi hedefler. Ana araştırma senaryosu
telefon kanalıdır:

- Türkçe gerçek konuşmaların kullanılması
- Türkçe sentetik/TTS seslerin kullanılması
- 8 kHz dar bant ve telefon codec koşullarının ölçülmesi
- Eğitimde görülmeyen TTS üreticilerine genellemenin test edilmesi
- AASIST ve alternatif ses modellerinin karşılaştırılması

ASVspoof veri setleri bu proje kapsamında kullanılmaz.

## Repo ve Git yapısı

- Repo kökünde Git deposu oluşturuldu.
- İç içe bulunan eski Git deposu yapısı kaldırılarak tek repo düzenine geçildi.
- Kök `README.md`, `CONTRIBUTING.md`, `LICENSE` ve `NOTICE` eklendi.
- GitHub Actions ile temel Python derleme kontrolü eklendi.
- Büyük dosyaların GitHub'a gönderilmesini önleyen `.gitignore` düzenlendi.
- WAV, Parquet, arşiv, sanal ortam, checkpoint ve model ağırlıkları Git dışında
  bırakıldı.
- Veri klasörlerinde README dosyalarının izlenebilir kalması sağlandı.
- Önemli klasörlere Türkçe açıklamalar eklendi:
  - `aasist-source/`
  - `aasist-source/config/`
  - `aasist-source/models/`
  - `dataset/`
  - veri seti alt klasörleri
  - `docs/`
  - `experiments/`
  - `scripts/`

## Kaynak kodu ve modeller

Repo içinde aşağıdaki mimariler kullanılabilir hale getirildi:

- AASIST
- AASIST-L
- RawNet2
- RawGAT-ST
- wav2vec2-XLS-R için ayrı Türkçe ince ayar akışı

AASIST ve AASIST-L başlangıç ağırlıkları şu konumda tutulur:

```text
aasist-source/models/weights/
```

Bu ağırlıklar büyük ikili dosyalar olduğu için Git'e eklenmez. RawNet2 ve
RawGAT-ST için güvenilir Türkçe hazır ağırlık bulunmadığından Türkçe veriyle
yeniden eğitim gerekir.

## Veri kaynakları

Projede veri rolleri şu şekilde belirlendi:

| Veri kaynağı | Rol | Etiket |
|---|---|---:|
| FLEURS TR | Gerçek insan sesi | `1` |
| Common Voice 17 TR | Gerçek insan sesi | `1` |
| MLAAD Türkçe | Sentetik/TTS ses | `0` |
| girenit Türkçe TTS | Sentetik/TTS ses | `0` |
| Synthetic Turkish TTS Data | Ek sentetik kaynak | `0` |

Common Voice TR için dışa aktarma scripti eklendi:

```bash
python scripts/download_commonvoice_tr.py --limit 1000
```

Bu script, sesleri WAV olarak dışa aktarır ve kaynak manifesti oluşturur.
Gün içinde Common Voice TR’den 300 kayıt dışa aktarıldı ve ana manifest
yeniden üretildi.

Son doğrulanan ana manifest:

- Toplam: 12.199 kayıt
- Train: 9.498
- Dev: 1.138
- Test: 1.563

Ana manifest yerel dosyadır ve Git'e eklenmez:

```text
dataset/turkish_manifest.jsonl
```

## Manifest üretimi

[`scripts/create_turkish_manifest.py`](../scripts/create_turkish_manifest.py)
şunları yapar:

- Dataset klasörlerindeki WAV dosyalarını tarar.
- Gerçek/sentetik etiketleri üretir.
- Train/dev/test split bilgilerini korur veya deterministik split üretir.
- MLAAD TTS üreticisini `generator` alanında saklar.
- Manifestte duplicate ses yollarını reddeder.
- Her split'te hem gerçek hem sentetik sınıf bulunmasını zorunlu kılar.
- `.tar.gz` açarken path traversal girişimlerini engeller.
- Belirli bir üreticiyi yalnızca testte bırakabilir.

Görülmemiş üretici testi:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --holdout-generator OmniVoice
```

Bu yöntem, modelin eğitimde görmediği bir TTS üreticisine genellemesini ölçmek
için kullanılır.

## Telefon kanalı çalışmaları

### G.711 dar bant simülasyonu

[`scripts/create_phone_channel_manifest.py`](../scripts/create_phone_channel_manifest.py)
eklendi. Script:

- Sesi mono yapar.
- 8 kHz'e indirir.
- G.711 mu-law kuantalaması uygular.
- Ayrı WAV dosyaları ve manifest üretir.

```bash
python scripts/create_phone_channel_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_phone_manifest.jsonl
```

Üretilen sesler:

```text
dataset/phone_channel_8k/
```

### Gerçek codec dönüşümü

[`scripts/create_real_codec_manifest.py`](../scripts/create_real_codec_manifest.py)
eklendi. FFmpeg encoder'ı mevcutsa GSM, AMR-NB veya Opus round-trip deneyi
üretebilir.

Örnek:

```bash
python scripts/create_real_codec_manifest.py \
  --input-manifest dataset/turkish_manifest.jsonl \
  --output-manifest dataset/turkish_opus_manifest.jsonl \
  --output-dir dataset/real_codec_opus \
  --codec opus
```

Bu makinede Opus encoder doğrulandı. Mevcut FFmpeg derlemesinde GSM ve AMR-NB
encoder'ı bulunmadığı için bu codec'ler için script açık hata verir; sessizce
G.711 simülasyonuna dönmez.

## Otomasyon

[`scripts/run_turkish_pipeline.py`](../scripts/run_turkish_pipeline.py) ile
manifest, doğrulama, telefon kanalı dönüşümü ve eğitim tek komutta
çalıştırılabilir:

```bash
python scripts/run_turkish_pipeline.py \
  --models AASIST \
  --extract-archives \
  --phone-channel \
  --holdout-generator OmniVoice \
  --epochs 30 \
  --batch-size 16 \
  --device auto
```

Desteklenen model seçenekleri:

- `AASIST`
- `AASIST-L`
- `RawNet2`
- `RawGAT-ST`
- `XLSR`
- `all`

Pipeline özeti:

```text
experiments/turkish/run_summary.json
```

## XLS-R akışı

[`scripts/train_xlsr_turkish.py`](../scripts/train_xlsr_turkish.py) ile
`facebook/wav2vec2-xls-r-300m` modeli Türkçe manifest üzerinden sınıflandırıcı
olarak ince ayarlanabilir:

```bash
python scripts/train_xlsr_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --model facebook/wav2vec2-xls-r-300m \
  --epochs 3
```

Çıktılar:

```text
experiments/turkish/XLSR/
```

İlk kullanımda model Hugging Face üzerinden indirilir. Model ağırlıkları Git'e
eklenmez.

## Eğitim çıktıları

Türkçe eğitim scriptleri varsayılan olarak repo içindeki model bazlı klasörlere
yazar:

```text
experiments/turkish/AASIST/
experiments/turkish/AASIST-L/
experiments/turkish/RawNet2/
experiments/turkish/RawGAT-ST/
experiments/turkish/XLSR/
```

Her eğitim klasöründe mümkün olduğunda:

- `best.pth`
- `metrics.json`

bulunur. Eğitim metrikleri ayrıca terminalde gösterilir.

Eski `aasist-source/main.py` ASVspoof uyumlu akıştır ve farklı olarak
`aasist-source/exp_result/` kullanır. Türkçe deneylerde bu dosya yerine
`scripts/train_turkish.py` veya `scripts/train_xlsr_turkish.py` kullanılmalıdır.

## Platform doğrulamaları

### macOS Apple Silicon

MPS üzerinde dört yerel modelin ileri geçiş testi başarıyla tamamlandı:

```text
AASIST: OK (1, 2) device=mps
AASIST-L: OK (1, 2) device=mps
RawNet2: OK (1, 2) device=mps
RawGAT-ST: OK (1, 2) device=mps
```

Komut:

```bash
python scripts/verify_models.py --device mps
```

### Windows

Windows fiziksel CUDA testi bu geliştirme gününün kapsamına alınmadı.
Windows scripti ve CUDA kurulum yolu dokümante edilmiştir; gerçek Windows
makinesinde ayrıca doğrulanmalıdır.

## Bağımlılıklar ve doğrulamalar

Gün içinde şu kontroller yapıldı:

- Bash syntax kontrolü
- Python compile/syntax kontrolü
- Model CLI yardım kontrolleri
- AASIST, AASIST-L, RawNet2 ve RawGAT-ST CPU/MPS forward testleri
- Manifest üretimi
- Common Voice TR dışa aktarma
- G.711 telefon kanalı dönüşümü
- Opus gerçek codec round-trip dönüşümü
- Görülmemiş TTS üreticisi holdout testi
- Git diff biçim kontrolü
- Büyük dosyaların Git'e eklenmediği kontrolü

## Bilinen sınırlamalar

- Gerçek GSM ve AMR-NB testi için uygun FFmpeg encoder'ı gerekir.
- G.711 simülasyonu gerçek mobil ağ, GSM veya VoIP koşullarının tamamını
  temsil etmez.
- XLS-R eğitimi büyük model indirmesi ve ciddi GPU belleği gerektirebilir.
- Common Voice ana manifeste dahil edilmiştir; ancak veri lisansı ve atıf
  koşulları korunmalıdır.
- Eğitim/test konuşmacı ayrımı, mevcut genel manifest akışında ayrıca
  güçlendirilebilir.
- Gerçek saha telefon kayıtları henüz kullanılmamıştır.
- Model sonuçları araştırma amaçlıdır; üretim kullanımına hazır kabul
  edilmemelidir.

## Git commit geçmişi

Gün içinde oluşturulan ilgili commit'ler:

```text
4948db2 chore: establish repository structure
5b109a9 feat: add Turkish anti-spoofing pipeline
09718e2 docs: add project reference materials
f1665f0 chore: exclude local dataset artifacts
```

