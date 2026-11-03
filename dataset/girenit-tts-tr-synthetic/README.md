---
license: apache-2.0
language:
  - tr
task_categories:
  - text-to-speech
pretty_name: girenit TTS TR Synthetic
tags:
  - tts
  - turkish
  - synthetic
  - speech
  - girenit
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files:
      - split: train
        path: "train/**"
      - split: test
        path: "test/**"
---

# girenit TTS TR Synthetic 🎙️🇹🇷

[girenit-TSS](https://huggingface.co/girenit/girenit-TSS) modelinin eğitiminde
kullanılan, tamamı sentetik Türkçe metinden-sese veri seti. İzinsiz gerçek kişi
kaydı veya ses klonlama verisi **içermez**; tüm sesler
[FreyaTTS-small](https://huggingface.co/freyavoice/Freya-TTS) öğretmen
modelinden sabit `20260814` tohumu ile üretilmiştir. Metinler girenit için özgün
olarak yazılmıştır.

## İçerik

| Split | Örnek | Süre | Açıklama |
|---|---:|---:|---|
| `train` | 1.272 | ~1,32 saat | 960 tam cümle (`subset=stage1`) + 312 kısa ifade (`subset=short`) |
| `test` | 20 | ~76 sn | Eğitimle sıfır çakışmalı ayrılmış değerlendirme seti |

- **Ses:** 48 kHz, 16-bit PCM, mono WAV
- **Sütunlar:** `audio`, `text`, `id`, `subset`, `teacher_model`, `teacher_seed`, `synthetic`
- **`provenance/`:** Orijinal eğitim manifestleri ve üretim raporları

## Kullanım

```python
from datasets import load_dataset

ds = load_dataset("girenit/girenit-tts-tr-synthetic", split="train")
print(ds[0]["text"])
```

## Etik ve köken

Bu veri setindeki tüm sesler sentetiktir ve kaynağı belgelenmiştir
(`teacher_model` + `teacher_seed` sütunları). Gerçek bir kişiye ait kayıt,
klonlanmış ses veya kişisel veri içermez. girenit-TSS modelinin
[değerlendirme sonuçları](https://huggingface.co/girenit/girenit-TSS/blob/main/evaluation.json)
bu setin `test` bölümü üzerinde ölçülmüştür.

## Lisans ve atıf

Apache License 2.0. Kullanırken `girenit/girenit-tts-tr-synthetic` ve öğretmen
model `freyavoice/Freya-TTS`'e atıf verilmesi rica olunur.

---

<details>
<summary><b>🌍 In English</b></summary>
<br/>

Fully synthetic Turkish text-to-speech dataset used to train
[girenit-TSS](https://huggingface.co/girenit/girenit-TSS). All audio was generated
from the Apache-2.0 [FreyaTTS-small](https://huggingface.co/freyavoice/Freya-TTS)
teacher model with a fixed seed (`20260814`); texts were written originally for
girenit. Contains no real-person recordings, no cloned voices, no personal data.
1,272 training utterances (~1.32 h) + 20 held-out eval sentences, 48 kHz mono
WAV. Licensed Apache-2.0.

</details>

<div align="center">
</div>
