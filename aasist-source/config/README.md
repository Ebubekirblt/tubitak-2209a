# Model yapılandırmaları

Bu klasörde AASIST, AASIST-L, RawNet2 ve RawGAT-ST deney yapılandırmaları
bulunur.

Türkçe eğitimde ASVspoof uyumlu `main.py` yerine kökteki
[`scripts/train_turkish.py`](../../scripts/train_turkish.py) kullanılmalıdır.
Türkçe RawNet2 ve RawGAT-ST yapılandırmaları:

- `Turkish_RawNet2.conf`
- `Turkish_RawGATST.conf`

Türkçe pipeline’da başlangıç ağırlığıyla kullanılan config dosyaları:

- `AASIST.conf`
- `AASIST-L.conf`

`RawNet2_baseline.conf` ve `RawGATST_baseline.conf` upstream ASVspoof akışı
için korunur. Türkçe RawNet2 ve RawGAT-ST eğitiminde `Turkish_*.conf`
dosyalarını; AASIST eğitiminde `AASIST*.conf` dosyalarını ve kökteki
`scripts/train_turkish.py` veya pipeline’ı kullanın.

`model_path` değerleri yalnızca önceden eğitilmiş ağırlıkla değerlendirme
yapılırken gereklidir. Türkçe eğitim çıktıları `experiments/turkish/` altında
oluşturulur.
