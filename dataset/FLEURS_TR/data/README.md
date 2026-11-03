# FLEURS TR veri dosyaları

Bu klasörde FLEURS Türkçe metadata ve ses arşivleri bulunur. `train.tsv`,
`dev.tsv` ve `test.tsv` bölümleri korunmalıdır.

Ses arşivlerini çıkarmak ve ortak manifesti yenilemek için depo kökünden:

```bash
python scripts/create_turkish_manifest.py --root dataset --extract-archives
```

Ses arşivleri ve çıkarılmış WAV dosyaları Git'e eklenmez.
