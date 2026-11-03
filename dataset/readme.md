# Veri Setleri ve Kullanım Amaçları

Bu projede kullanılan veri setleri, gerçek insan konuşmalarını öğrenmek, sentetik sesleri ayırt etmek ve modelin farklı koşullardaki başarısını değerlendirmek amacıyla bir araya getirilmiştir.

| Veri seti | Türü | Projedeki kullanım amacı |
|---|---|---|
| **Common Voice 17 TR** | Gerçek ses | Modelin gerçek insan konuşmalarının özelliklerini öğrenmesini sağlamak |
| **MLAAD Türkçe** | Sahte ses | Farklı TTS modelleri tarafından üretilen yapay sesleri tanımak |
| **girenit-tts-tr-synthetic** | Sahte ses | Eğitimde kullanılmamış bir üreticiyle modelin genelleme başarısını test etmek |
| **Synthetic Turkish TTS Data** | Sahte ses | Farklı Türkçe sentetik sesleri ve konuşma içeriklerini ek olarak değerlendirmek |

## Yardımcı Model

| Model | Dosya | Kullanım amacı |
|---|---|---|
| **TurkicASR** | `turkic_languages_model.zip` | Türkçe konuşmayı metne dönüştürme sürecinde yardımcı olmak |