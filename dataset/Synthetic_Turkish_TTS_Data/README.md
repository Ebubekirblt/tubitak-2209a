---
dataset_info:
  features:
  - name: audio
    dtype: audio
  - name: text
    dtype: string
  - name: source
    dtype: string
  - name: sample_rate
    dtype: int64
  - name: speaker
    dtype: string
  splits:
  - name: train
    num_bytes: 2942869578
    num_examples: 13000
  download_size: 3303296950
  dataset_size: 2942869578
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
license: cc
task_categories:
- text-to-speech
- automatic-speech-recognition
language:
- tr
size_categories:
- 10K<n<100K
---

# Synthetic Turkish TTS Data

This dataset was created by generating synthetic Turkish text across multiple speech scenarios. The text was produced in the following domains: `finance_master`, `cs_master`, `parcel_delivery`, `ecommerce`, `telecom`, `isp_support`, `technical_support`, `subscription`, `insurance`, `health_appointments`, `public_services`, `education_registration`, and `daily_speech`.

These synthetic texts were then synthesized with a high-quality Turkish TTS model. The dataset is intended to be used as synthetic training data for future Turkish TTS model training.

## Dataset Summary

- Total number of samples: **13,000**
- Total number of speakers: **4**
- Total duration: **28 hours 50 minutes 13 seconds**

### Speaker Distribution

- **ali**: 6 hours 50 minutes 57 seconds (3250 wav files)
- **zeynep**: 6 hours 50 minutes 35 seconds (3250 wav files)
- **leyla**: 7 hours 10 minutes 55 seconds (3250 wav files)
- **alev**: 7 hours 57 minutes 46 seconds (3250 wav files)

## Columns

- `audio`: audio file
- `text`: corresponding transcription
- `source`: scenario/domain from which the sample was generated
- `sample_rate`: audio sampling rate
- `speaker`: speaker name

## License
This dataset is released under the CC BY 4.0 license. You may use, share, and adapt the dataset provided that proper attribution is given.

## Audio Generation

The audio samples in this dataset were generated using the Freya AI API.

Reference: https://www.linkedin.com/company/107923818/