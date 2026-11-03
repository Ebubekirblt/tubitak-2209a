# Model yapılandırmaları

Bu klasörde AASIST, AASIST-L, RawNet2 ve RawGAT-ST deney yapılandırmaları
bulunur.

Türkçe eğitimde ASVspoof uyumlu `main.py` yerine kökteki
[`scripts/train_turkish.py`](../../scripts/train_turkish.py) kullanılmalıdır.
Türkçe RawNet2 ve RawGAT-ST yapılandırmaları:

- `Turkish_RawNet2.conf`
- `Turkish_RawGATST.conf`

`model_path` değerleri yalnızca önceden eğitilmiş ağırlıkla değerlendirme
yapılırken gereklidir. Türkçe eğitim çıktıları `experiments/turkish/` altında
oluşturulur.
