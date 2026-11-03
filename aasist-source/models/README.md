# Model mimarileri

Bu klasörde ham ses tabanlı anti-spoofing model mimarileri bulunur:

- `AASIST.py`
- `RawNet2Spoof.py`
- `RawNetGatSpoofST.py`

Modeller 16 kHz ses ve yaklaşık dört saniyelik (`64600` örnek) giriş
bekler. Türkçe uyumluluk model mimarisinden değil, Türkçe gerçek/sentetik
veriyle yapılan eğitimden gelir.

`weights/` klasörü yerel model ağırlıkları içindir ve ağırlık dosyaları Git’e
eklenmez. Ağırlıkların kontrolü için
[`scripts/verify_models.py`](../../scripts/verify_models.py) kullanılabilir.
