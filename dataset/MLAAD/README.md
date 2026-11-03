# MLAAD Türkçe

MLAAD’ın `fake/tr/` altındaki Türkçe üretici klasörleri sentetik seslerden
oluşur ve manifestte `label=0` olarak işaretlenir.

Türkçe klasörleri sınırlı indirmek için:

```bash
python scripts/mlaad_tr_dilimli_indir.py --list
python scripts/mlaad_tr_dilimli_indir.py --model bark --limit 20
```

Tüm Türkçe dosyalar büyük olabilir:

```bash
python scripts/mlaad_tr_dilimli_indir.py --all
```

Hugging Face erişimi gerekirse önce `hf auth login` çalıştırın. Veri ve cache
dosyaları Git’e eklenmez.
