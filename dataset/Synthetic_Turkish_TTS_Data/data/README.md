# Synthetic Turkish TTS veri dosyaları

Parquet veri parçaları sentetik Türkçe ses ve metadata içerir. Büyük parquet
dosyaları Git'e eklenmez.

Eğitim akışına dahil etmeden önce bu verileri WAV/manifest biçimine dönüştüren
bir dönüştürme adımı gerekir. Mevcut `create_turkish_manifest.py` doğrudan
parquet okumaz.
