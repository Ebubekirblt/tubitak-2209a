# FLEURS Türkçe

FLEURS Türkçe, gerçek insan konuşmalarından oluşan veri kaynağıdır ve
manifestte `label=1` olarak işaretlenir.

`data/tr_tr/` altında train, dev ve test metadata dosyaları bulunur. Ses
arşivleri çıkarıldıktan sonra ortak manifest oluşturun:

```bash
python scripts/create_turkish_manifest.py --root dataset --extract-archives
```

Veri setinin lisans ve atıf koşullarını sağlayıcısının resmi sayfasından
kontrol edin. Ses dosyaları Git’e eklenmez.
