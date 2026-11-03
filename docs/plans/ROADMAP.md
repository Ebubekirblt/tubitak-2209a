# Türkçe Telefon Kanalı Deepfake Tespit Roadmap'i

Bu belge projenin mevcut durumunu, tamamlanan işleri ve bundan sonraki teknik
adımları takip etmek için kullanılır. Veri dosyaları ve model ağırlıkları yerel
tutulur; bu roadmap yalnızca kaynak kodu, deney ve dokümantasyon durumunu takip
eder.

## Durum özeti

| Alan | Durum |
|---|---|
| GitHub repo yapısı | ✅ Tamamlandı |
| Türkçe veri hazırlama | ✅ İlk tam sürüm hazır |
| Common Voice TR | ✅ 64.808 WAV; `client_id` metadata’sı korundu |
| MLAAD Türkçe | ✅ 7.000 WAV indirildi |
| FLEURS TR ve girenit | ✅ Yerel veri mevcut |
| Türkçe manifest | ✅ 56.689 kayıtla üretildi |
| AASIST / AASIST-L | ✅ Eğitim akışı hazır |
| RawNet2 / RawGAT-ST | ✅ Eğitim akışı hazır |
| XLS-R | 🟡 Kod ve CLI hazır, kapsamlı eğitim bekliyor |
| Telefon kanalı simülasyonu | ✅ 8 kHz + G.711 μ-law |
| Gerçek Opus codec | ✅ Araç ve smoke test hazır |
| GSM / AMR-NB | 🔴 Encoder ve deney bekliyor |
| macOS MPS | ✅ Forward testi başarılı |
| Windows CUDA | 🟡 Gerçek cihaz testi bekliyor |
| Akademik metrikler | ✅ EER/AUC/F1 ve sınıflandırma metrikleri yazılıyor |
| Inference CLI/API | 🔴 Başlanmadı |

## Tamamlananlar

### Repo ve dokümantasyon

- [x] Repo kökünde tek Git yapısı oluşturuldu.
- [x] GitHub remote ve `main` branch yapılandırıldı.
- [x] Kaynak kodu, lisans, katkı ve bildirim dosyaları eklendi.
- [x] Büyük veri, model, ses ve deney çıktıları Git dışında bırakıldı.
- [x] `docs/daily/`, `docs/plans/` ve `docs/reference/` klasörleri oluşturuldu.
- [x] Türkçe README dosyaları önemli klasörlere eklendi.
- [x] Günlük geliştirme ve veri tamamlama belgeleri oluşturuldu.
- [x] GitHub Actions Python derleme kontrolü eklendi.

### Veri

- [x] FLEURS TR gerçek sesleri hazırlandı.
- [x] girenit Türkçe sentetik sesleri hazırlandı.
- [x] MLAAD Türkçe klasörlerinin tamamı indirildi.
- [x] Common Voice TR kayıtları WAV olarak dışa aktarıldı.
- [x] Train/dev/test manifest üretimi otomatikleştirildi.
- [x] Gerçek/sentetik etiketleme eklendi.
- [x] MLAAD TTS üreticisi bilgisi manifestte korunuyor.
- [x] Her split'te iki sınıfın bulunması doğrulanıyor.
- [x] Güvenli arşiv açma ve duplicate yol kontrolleri eklendi.
- [x] Common Voice resmi arşiv aktarımında `client_id` bilgisini `speaker_id`
      olarak koruyan exporter eklendi.
- [x] Speaker metadata’sı zorunlu olduğunda metadata içermeyen kaynakların
      sessizce kullanılmasını engelleyen doğrulama eklendi.

### Model ve eğitim

- [x] AASIST ve AASIST-L başlangıç ağırlık akışı hazırlandı.
- [x] RawNet2 ve RawGAT-ST Türkçe configleri eklendi.
- [x] Türkçe eğitim scripti oluşturuldu.
- [x] CPU, CUDA, MPS ve otomatik cihaz seçimi eklendi.
- [x] Model bazlı `best.pth` ve `metrics.json` çıktıları eklendi.
- [x] wav2vec2-XLS-R için ayrı fine-tuning scripti eklendi.
- [x] Dört yerel modelin macOS MPS forward testi tamamlandı.

### Telefon kanalı ve otomasyon

- [x] 8 kHz mono telefon kanalı dönüşümü eklendi.
- [x] G.711 μ-law simülasyonu eklendi.
- [x] FFmpeg ile Opus round-trip aracı eklendi.
- [x] Görülmemiş TTS üreticisi holdout seçeneği eklendi.
- [x] Manifest, doğrulama ve eğitim pipeline'ı tek komutta birleştirildi.

## Devam eden ve bekleyen işler

### P0 — Deney güvenilirliği

- [x] Speaker metadata taşıma ve speaker-disjoint split doğrulama akışını ekle.
- [x] FLEURS/MLAAD/Girenit metadata’sından speaker gruplarını manifest’e taşı.
- [x] Metadata’sı olmayan Common Voice’i speaker-disjoint alt kümesinden
      açıkça dışlama seçeneği ekle.
- [x] Common Voice dışı 11.899 kayıtla leakage-free speaker-disjoint manifest
      üretimini ve doğrulamasını çalıştır.
- [x] `client_id` içeren resmi Common Voice arşivinden yeniden dışa aktarım
      aracını ekle. Mozilla Data Collective arşivi indirildiğinde `--source-dir`
      ve `--require-speaker-id` ile çalışır.
- [x] Resmi Common Voice 27.0 arşivini Mozilla Data Collective’den dışa aktar,
      eski metadata’sız kopyayı dışarıda bırak ve tam speaker-disjoint split’i
      üret.
- [x] `--holdout-generator` ile TTS üreticisi-disjoint deney akışını doğrula.
- [x] Yedi TTS üreticisi için holdout manifestlerini üret ve doğrula.
- [x] Holdout dev splitlerinde yüksek sınıf oranını tespit edip holdout dışı
      train kayıtlarıyla deterministik sınıf dengelemesi uygula.
- [ ] Holdout eğitimlerini tüm üreticilerle çalıştır.
- [x] Temiz ses ve telefon kanalı manifestlerini ayrı tut.
- [x] Veri kaynakları ve kayıt sayılarını manifest doğrulamasında raporla.
- [x] Sentetik sınıf dengesini manifest doğrulamasında kontrol et; yüksek oranı
      sessizce kabul etmek yerine doğrulama hatası olarak raporla.

#### Common Voice speaker metadata raporu

Speaker-disjoint değerlendirme için her ses kaydının güvenilir bir konuşmacı
kimliğiyle eşleştirilmesi gerekiyor. Mevcut
`ysdede/commonvoice_17_tr_fixed` kopyası yalnızca ses ve içerik alanlarını
sağlıyor; `client_id` veya eşdeğer bir konuşmacı alanı içermiyor. Bu nedenle
mevcut WAV dosyalarından konuşmacı kimliğini sonradan güvenilir biçimde
üretmek mümkün değil. Yapay veya dosya adına dayalı speaker ID üretmek,
ölçümün leakage-free olduğu iddiasını geçersiz kılabileceği için özellikle
kullanılmıyor.

Bu kısıtı çözmek için `scripts/download_commonvoice_tr.py` içine resmi Common
Voice arşivini doğrudan okuyabilen bir aktarım yolu eklendi. Beklenen arşiv
yapısı şöyledir:

```text
cv-corpus-tr/
├── clips/
├── train.tsv
├── dev.tsv
└── test.tsv
```

Exporter’ın davranışı:

- `train.tsv`, `dev.tsv` ve `test.tsv` içindeki `client_id` alanını
  `speaker_id` olarak manifest’e taşır.
- Ses dosyalarını `clips/` altından bulur ve WAV çıktısı üretir.
- MP3 ve desteklenen diğer girişleri FFmpeg üzerinden dönüştürür.
- Orijinal split bilgisini korur.
- `--require-speaker-id` kullanıldığında metadata eksikliğini açık hata olarak
  bildirir; kayıtları sessizce dışlamaz veya sahte kimlik oluşturmaz.
- Üretilen veri, `create_turkish_manifest.py` içindeki
  `--speaker-disjoint` akışına verilebilir.

Resmi arşiv indirildikten sonra önerilen tam akış:

```bash
python scripts/download_commonvoice_tr.py \
  --source-dir /path/to/cv-corpus-tr \
  --output dataset/commonvoice_17_tr_fixed \
  --all \
  --require-speaker-id

python scripts/create_turkish_manifest.py \
  --speaker-disjoint \
  --output dataset/turkish_speaker_disjoint_manifest.jsonl

python scripts/validate_manifest.py \
  dataset/turkish_speaker_disjoint_manifest.jsonl \
  --require-speaker-id \
  --speaker-disjoint
```

Aktarım aracı yerel bir Common Voice arşiv simülasyonu ile doğrulandı.
Metadata’sız mevcut HF kaynağıyla `--require-speaker-id` çalıştırıldığında
işlem beklenen şekilde açık hata veriyor. FLEURS, MLAAD ve Girenit kaynakları
üzerinden üretilen 11.899 kayıtlık alt kümede ise splitler arasında speaker
çakışması bulunmadığı doğrulandı. Tam Common Voice katkısı, Mozilla Data
Collective erişimi olan resmi arşivin indirilmesinden sonra tamamlanacak;
bu dış veri erişimi gereksinimi kod veya mevcut WAV’lar üzerinden çözülebilecek
bir eksiklik değildir.

Arşiv aktarımı daha sonra tamamlandı. `cv-corpus-27.0-2026-09-11-tr.tar.gz`
arşivindeki train/dev/test TSV dosyalarında toplam 64.808 kullanılabilir kayıt
bulundu ve kayıtların tamamında `client_id` mevcuttu. MP3 kayıtları
`dataset/commonvoice_27_tr_fixed/` altında WAV olarak üretildi. Eski
`commonvoice_17_tr_fixed` kopyası speaker metadata’sı olmadığı için final
manifestten çıkarıldı.

Üretilen final manifest:

```text
dataset/turkish_speaker_disjoint_manifest_commonvoice27.jsonl
```

Final doğrulama özeti:

| Split | Kayıt | Gerçek | Sentetik | Speaker |
|---|---:|---:|---:|---:|
| train | 19.846 | 17.554 | 2.292 | 449 |
| dev | 25.160 | 22.160 | 3.000 | 1.252 |
| test | 31.701 | 28.701 | 3.000 | 1.873 |

- Train/dev speaker kesişimi: `0`
- Train/test speaker kesişimi: `0`
- Dev/test speaker kesişimi: `0`
- Eksik ses dosyası: `0`
- `validate_manifest.py --require-speaker-id --speaker-disjoint`: başarılı

#### TTS üreticisi holdout dengeleme raporu

Yedi üretici için holdout manifestleri üretildi: `OmniVoice`, `VoxCPM2`,
`FreyaTTS`, `bark`, `xtts_v1.1`, `xtts_v2` ve `glow-tts`. Her akışta eşleşen
üreticinin tüm kayıtları test splitine taşınıyor; böylece testte görülmemiş
üretici koşulu korunuyor.

İlk doğrulamada `xtts_v2` ve `glow-tts` holdout’larında dev splitindeki
sentetik kayıt sayısı azaldığı için sırasıyla 29.92:1 ve 22.44:1 sınıf oranları
görüldü. `create_turkish_manifest.py` artık bu durumu deterministik biçimde
ele alıyor: yalnızca holdout dışında kalan train sentetik kayıtlarını dev’e
taşıyor ve doğrulama sınırı olan 20:1 oranını karşılayacak minimum örnek sayısını
sağlıyor. Held-out üreticinin kayıtları asla train veya dev’e geri alınmıyor.

Son doğrulama sonucunda yedi manifestin tamamı `validate_manifest.py` ile
başarılı oldu. `xtts_v2` ve `glow-tts` için gerekli dengeleme uygulanırken
train/dev kayıt sayıları değişti; diğer holdout manifestlerinin split yapısı
değişmedi. Bu hazırlık adımı tamamlandı, üretici bazlı eğitimlerin çalıştırılması
P0’da kalan iştir.

### P1 — Sentetik veri ve telefon koşulları

- [ ] Synthetic Turkish TTS parquet dosyalarını WAV veya doğrudan dataset
      okuyucusu ile manifest akışına dahil et.
- [ ] G.711 μ-law yanında A-law, farklı Opus bitrate ve paket kaybı senaryoları
      ekle.
- [ ] GSM-FR encoder bulunan bir ortamda GSM testi çalıştır.
- [ ] AMR-NB encoder bulunan bir ortamda AMR-NB testi çalıştır.
- [ ] Gerçek telefon kayıtları veya kontrollü VoIP kayıtlarıyla dış test yap.

### P1 — Model karşılaştırması

- [ ] AASIST ile temiz kanal baseline eğitimi tamamla.
- [ ] AASIST ile telefon kanalı eğitimi tamamla.
- [ ] AASIST-L, RawNet2 ve RawGAT-ST aynı splitlerde çalıştır.
- [ ] XLS-R için küçük smoke test ve ardından tam eğitim çalıştır.
- [ ] Tüm modelleri aynı test protokolüyle karşılaştır.
- [ ] Başlangıç ağırlığı ile sıfırdan eğitim sonuçlarını ayır.

### P1 — Değerlendirme ve raporlama

- [x] EER hesaplama modülünü ve eğitim çıktısını ekle.
- [x] ROC-AUC, F1, precision, recall ve balanced accuracy hesaplama ekle.
- [x] Confusion matrix üretimini `metrics.json` içine ekle.
- [ ] Model, üretici ve codec bazlı sonuç tabloları oluştur.
- [x] Temel sonuçları `metrics.json` içine yaz.
- [ ] Model, üretici ve codec bazlı özet CSV/JSON dosyaları oluştur.
- [ ] Deneylerde Git commit hash ve veri manifest hash bilgisini sakla.

### P2 — Kullanım ve dağıtım

- [ ] `predict.py` ile tek ses dosyası inference CLI oluştur.
- [ ] WAV, MP3 ve 8 kHz ses girişlerini destekle.
- [ ] Tahmin etiketi, olasılık ve kullanılan model bilgisini döndür.
- [ ] FastAPI veya benzeri bir servis katmanı ekle.
- [ ] Kurulum ve inference için Docker seçeneği değerlendir.
- [ ] Örnek test sesleri ve örnek çıktı formatı hazırla.

## Önerilen sıradaki çalışma

İlk uygulanacak sıra:

1. Konuşmacı-disjoint split üret.
2. AASIST temiz kanal baseline eğit.
3. AASIST G.711/Opus telefon kanalı deneyini yap.
4. TTS üreticisi-disjoint testleri çalıştır.
5. RawNet2, RawGAT-ST ve XLS-R sonuçlarını aynı tabloya koy.
6. Synthetic Turkish TTS parquet entegrasyonunu tamamla.
7. GSM/AMR-NB deneylerini uygun encoder ortamında yap.
8. En iyi model için inference CLI oluştur.

## Deney başarı ölçütleri

Bir deney tamamlandı sayılması için:

- Kullanılan manifest ve split açıkça belirtilmeli.
- Train/dev/test konuşmacı sızıntısı olmamalı.
- Testteki görülmemiş TTS üreticileri belirtilmeli.
- Kanal/codec koşulu kaydedilmeli.
- Model, epoch, batch size ve cihaz bilgisi kaydedilmeli.
- Accuracy dışında en az EER ve ROC-AUC raporlanmalı.
- Checkpoint ve `metrics.json` repo içindeki doğru deney klasöründe bulunmalı.

## Güncelleme kuralı

Her önemli tamamlanan işten sonra:

1. Bu roadmap güncellenir.
2. Gerekirse `docs/plans/` altında tarihli ayrıntılı plan güncellenir.
3. Test veya doğrulama sonucu ilgili günlük dosyasına eklenir.
4. Değişiklik kendi konusu ile ilişkili ayrı commit olarak kaydedilir.

Son güncelleme: **2026-11-04**
