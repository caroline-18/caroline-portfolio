# Harmful Language & Criminal Intent Detector

An NLP-powered web application that classifies text into harmful intent categories using a fine-tuned DistilBERT model. Built as part of an NLP research project focused on detecting toxic language and criminal intent in dialogues.

## Project Overview
This project uses a fine-tuned DistilBERT transformer model to classify input text into 5 intent categories ranging from neutral content to explicit threats. It includes a clean Gradio web interface for real-time predictions with confidence scores.

## Intent Categories
| Label | Category | Description |
|-------|----------|-------------|
| 0 | Neutral | Normal, non-harmful content |
| 1 | Confession | Admission of crimes |
| 2 | Discussing Illegal Activity | Past crime discussion |
| 3 | Planning Crime | Active plotting of crimes |
| 4 | Threatening Action | Explicit threats or coercion |

## Tech Stack
- **Model**: DistilBERT (distilbert-base-uncased), fine-tuned
- **Framework**: HuggingFace Transformers + PyTorch
- **Interface**: Gradio web UI
- **Training Data**: Jigsaw Toxic Comments + Custom synthetic crime dialogues (6K samples)
- **Language**: Python 3.8+

## Installation

```bash
git clone https://github.com/Das-Debjit/Harmful-Language-Detection.git
cd Harmful-Language-Detection
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

Then open: http://127.0.0.1:7860

## Features
- Real-time text classification into 5 intent categories
- Confidence scores for all categories
- 7 built-in example prompts for quick testing
- GPU auto-detection with CPU fallback
- Clean web UI with blue/sky color scheme

## Project Structure
├── app.py                               # Main Gradio application (228 lines)
├── intent_label_mapping_combined.json   # Label mappings (0-4)
├── model/                               # Fine-tuned DistilBERT
│   ├── model.safetensors                # Model weights stored via Git LFS
│   ├── config.json                      # Model architecture config
│   ├── tokenizer.json                   # Tokenizer vocabulary
│   ├── tokenizer_config.json            # Tokenizer settings
│   ├── special_tokens_map.json          # Special tokens
│   └── vocab.txt                        # DistilBERT vocabulary
├── notebooks/                           # Training and preprocessing notebooks
├── requirements.txt                     # Python dependencies
└── README.md

## Large Files (Datasets & Full Model)
The full training datasets and large model checkpoint are stored in Google Drive:

🔗 [Download from Google Drive](https://drive.google.com/drive/folders/1l1RR57PszifCWqTrMNnR8FeiRuozuLOV?usp=sharing)

| File | Size | Description |
|------|------|-------------|
| `cleaned_toxic_comments.csv` | 122MB | Full Jigsaw toxic comments dataset |
| `high_end_intent_model_combined_v1/` | 2.3GB | Full DistilBERT checkpoint |
| `intent_train_split_combined.csv` | 1.6MB | Training split |
| `intent_test_split_combined.csv` | 384KB | Test split |
| `synthetic_intent_dataset_6k_randomized.csv` | 597KB | Synthetic crime dialogues |

## System Requirements
- Python 3.8+
- GPU optional (auto-detects, falls back to CPU)
- ~500MB disk space (without large files)

## Team
| Name | GitHub |
|------|--------|
| Debjit Das | [Das-Debjit](https://github.com/Das-Debjit) |
| Sajani Dengle | [sajanidengle](https://github.com/sajanidengle) |
| Caroline Manjari | [caroline-18](https://github.com/caroline-18) |