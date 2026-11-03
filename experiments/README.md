# Deney çıktıları

Bu klasör yerel eğitim checkpoint’lerini, metrikleri, pipeline özetlerini ve
TensorBoard çıktısını tutar. Büyük deney çıktıları Git’e eklenmez.

## Varsayılan çıktı yapısı

```text
experiments/
└── turkish/
    ├── AASIST/
    ├── AASIST-L/
    ├── RawNet2Spoof/
    ├── RawNetGatSpoofST/
    ├── XLSR/
    └── run_summary.json
```

`train_turkish.py` model klasörüne checkpoint ve `metrics.json` yazar.
`metrics.json` test loss/accuracy yanında EER, ROC-AUC, F1, precision, recall,
balanced accuracy ve confusion matrix içerir. Test değerlendirmesi en iyi dev
checkpoint ile yapılır.
`run_turkish_pipeline.py` çalıştırılan manifest, model ve seçenekleri
`run_summary.json` içinde kaydeder.

Deney paylaşırken manifest yolu/sürümü, config, model ağırlığı, epoch, batch
size, seed, cihaz ve metrikleri birlikte belirtin. Test kümesini eğitimde
kullanmayın; telefon kanalı ve görülmemiş üretici sonuçlarını temiz test
sonuçlarından ayrı raporlayın.

Eski `aasist-source/main.py` ASVspoof uyumlu akışa aittir ve çıktısını
`aasist-source/exp_result/` altında oluşturabilir. Türkçe deneylerde bunun
yerine `scripts/run_turkish_pipeline.py` kullanın.
