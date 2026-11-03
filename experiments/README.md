# Deney çıktıları

Türkçe eğitim scriptinin checkpoint ve yerel deney çıktıları bu klasörde
tutulur. Dosyalar geçicidir; Git’e eklenmez.

Türkçe eğitim çıktıları varsayılan olarak şu alt klasörlerde oluşur:

```text
experiments/turkish/AASIST/
experiments/turkish/AASIST-L/
experiments/turkish/RawNet2Spoof/
experiments/turkish/RawNetGatSpoofST/
```

Deney sonuçlarını paylaşırken kullanılan manifest, config, epoch sayısı,
batch size ve donanım bilgisini ayrıca kaydedin. Mevcut eğitim scripti her
model klasörüne `best.pth` yazar; eğitim metriklerini terminalde gösterir.
Ayrıca aynı klasöre `metrics.json` yazar.

Not: `aasist-source/main.py` eski ASVspoof uyumlu akıştır ve varsayılan
çıktısını `aasist-source/exp_result/` altında oluşturur. Türkçe deneylerde bu
dosya kullanılmaz; `scripts/train_turkish.py` kullanılmalıdır.

`scripts/run_turkish_pipeline.py` ile oluşturulan `run_summary.json`, hangi
manifest ve modellerle çalışıldığını kaydeder.

XLS-R çıktıları `experiments/turkish/XLSR/` altında tutulur; model ve
`metrics.json` dosyası birlikte saklanır.

Telefon kanalı deneyi için `dataset/turkish_phone_manifest.jsonl` kullanılır.
Bu deneyin amacı temiz ses ile telefon kanalı sesindeki performans farkını
ölçmektir; sonuçları temiz test kümesiyle karıştırmayın.
