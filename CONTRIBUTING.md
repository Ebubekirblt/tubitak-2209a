# Katkı rehberi

## Başlamadan önce

1. Küçük ve tek bir amaca odaklanan değişiklikler yapın.
2. Veri setlerini, model ağırlıklarını, sanal ortamları veya deney çıktılarını
   commit etmeyin.
3. Veri setlerinin lisans ve atıf koşullarını koruyun.

## Kontroller

```bash
python -m compileall -q aasist-source
```

Model eğitimi ve değerlendirmesi veri seti ile GPU gerektirebilir; çalıştırılan
komutları ve kullanılan yapılandırmayı pull request açıklamasında belirtin.

## Pull request

Pull request açıklamasında amaç, değişen dosyalar, doğrulama komutları ve
varsa metrik sonuçları yer almalıdır. Büyük ikili dosyaları doğrudan GitHub'a
yüklemek yerine sürüm kontrollü bir model/data deposuna veya harici bir
artifact deposuna bağlantı verin.
