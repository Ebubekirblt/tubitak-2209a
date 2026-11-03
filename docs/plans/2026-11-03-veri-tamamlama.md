# 2026-11-03 Veri Tamamlama ve Sonraki Aşamalar

Bu belge, veri setlerinin neden ilk aşamada tamamen GitHub'a eklenmediğini ve
yerel makinede tam veri hazırlama sürecini açıklar.

## Neden veri setlerinin tamamı GitHub'a konulmadı?

Ses, Parquet, model ve arşiv dosyaları çok büyüktür; GitHub kaynak kodu
deposuna eklenmeleri:

- depo boyutunu gereksiz büyütür,
- GitHub dosya limitlerine takılabilir,
- lisans ve yeniden dağıtım koşullarını ihlal edebilir,
- veri güncelleme ve sürümlemeyi zorlaştırabilir.

Bu nedenle repo kaynak kodunu, config dosyalarını, scriptleri ve README'leri
tutar; veri dosyaları yerel olarak indirilir ve `.gitignore` ile dışarıda kalır.

## 2026-11-03 yerel veri durumu

Kontrol edilen yaklaşık boyutlar:

| Kaynak | Yerel durum |
|---|---:|
| FLEURS TR | yaklaşık 2.6 GB |
| MLAAD Türkçe | 7.000 WAV + 7 `meta.csv`, yaklaşık 2.4 GB |
| girenit Türkçe TTS | yaklaşık 452 MB |
| Synthetic Turkish TTS parquet | yaklaşık 3.1 GB |
| TurkicASR yardımcı modeli | yaklaşık 609 MB |
| Common Voice TR | 44.790 WAV olarak dışa aktarıldı |

Common Voice ana manifesti tam yerel kayıtlarla yeniden üretildi:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --output dataset/turkish_manifest.jsonl
```

## Tam indirme komutları

### Common Voice TR

Tüm seçili split'leri WAV olarak dışa aktarmak için:

```bash
python scripts/download_commonvoice_tr.py --all
```

Sınırlı deneme için:

```bash
python scripts/download_commonvoice_tr.py --limit 300
```

### MLAAD Türkçe

Türkçe TTS klasörlerinin tamamını indirmek için:

```bash
python scripts/mlaad_tr_dilimli_indir.py --all
```

Hugging Face erişim şartı veya token gerekirse:

```bash
hf auth login
```

### Manifest yenileme

Tüm WAV kaynakları hazırlandıktan sonra:

```bash
python scripts/create_turkish_manifest.py \
  --root dataset \
  --output dataset/turkish_manifest.jsonl \
  --extract-archives
```

## Bundan sonra yapılacaklar

1. Synthetic Turkish TTS parquet dosyalarını WAV veya doğrudan dataset
    okuyucusuyla manifest akışına dahil etmek.
2. Konuşmacı-disjoint train/dev/test bölünmesi oluşturmak.
3. TTS üreticisi-disjoint testleri tekrarlamak.
4. G.711, Opus, GSM-FR ve AMR-NB telefon koşullarını karşılaştırmak.
5. AASIST, RawNet2, RawGAT-ST ve XLS-R modellerini aynı test setlerinde
    eğitip karşılaştırmak.
6. EER, ROC-AUC, F1, balanced accuracy ve confusion matrix raporlamak.
7. En iyi modeli ses dosyası alan bir inference CLI/API ile paketlemek.
8. Lisans, veri kaynağı ve deney konfigürasyonlarını yayınlanabilir rapora
    dönüştürmek.

## Kapsam notu

“Tam veri seti” GitHub'a yükleme anlamına gelmez. Tamamlanması gereken iş,
verilerin lisanslarına uygun biçimde yerel makineye indirilmesi, manifestte
doğru etiketlenmesi ve deneylerde izlenebilir şekilde kullanılmasıdır.
