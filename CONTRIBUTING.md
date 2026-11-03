# Katkı rehberi

## Başlamadan önce

1. Küçük ve tek bir amaca odaklanan değişiklikler yapın.
2. Veri setlerini, model ağırlıklarını, sanal ortamları veya deney çıktılarını
   commit etmeyin.
3. Veri setlerinin lisans ve atıf koşullarını koruyun.
4. Güncel kullanım ve komut değişikliklerini kök `README.md` ile ilgili
   alt README dosyalarında birlikte güncelleyin.

## Kontroller

```bash
make check
make compile
```

`make check` bağımlılık gerektirmeyen repo yapısı, manifest JSONL biçimi ve
Python sözdizimi kontrolünü birlikte çalıştırır. `make compile` yalnızca
Python derleme kontrolünü tekrarlar; Make kurulu değilse aynı komutları
doğrudan `python3` ile çalıştırabilirsiniz.

Model eğitimi ve değerlendirmesi veri seti ile GPU gerektirebilir; çalıştırılan
komutları ve kullanılan yapılandırmayı pull request açıklamasında belirtin.
Dokümantasyon değişikliklerinde hangi akışın ve hangi platformun doğrulandığını
ayrıca belirtin.

## Pull request

Pull request açıklamasında amaç, değişen dosyalar, doğrulama komutları ve
varsa metrik sonuçları yer almalıdır. Büyük ikili dosyaları doğrudan GitHub'a
yüklemek yerine sürüm kontrollü bir model/data deposuna veya harici bir
artifact deposuna bağlantı verin.
