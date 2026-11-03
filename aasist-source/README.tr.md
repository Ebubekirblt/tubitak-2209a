# AASIST kaynak kodu

Bu klasör AASIST, AASIST-L, RawNet2 ve RawGAT-ST model mimarilerini içerir.
Orijinal `main.py` ve `data_utils.py` ASVspoof veri biçimi için yazılmıştır.

Bu projenin Türkçe deneylerinde kök dizindeki şu araçlar kullanılmalıdır:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --extract-archives
python scripts/run_turkish_pipeline.py \
  --models AASIST \
  --manifest dataset/turkish_manifest.jsonl \
  --epochs 1 \
  --batch-size 4
```

Tek model eğitimi:

```bash
python scripts/train_turkish.py \
  --manifest dataset/turkish_manifest.jsonl \
  --config aasist-source/config/Turkish_RawNet2.conf
```

Kurulum, lisans ve upstream atıfları için kök `README.md`, mevcut İngilizce
`README.md`,
`LICENSE` ve `NOTICE` dosyalarına bakın.
