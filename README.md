# Bilingual Interlinear PDF Reader

A local, open-source web application that converts Spanish PDFs into a bilingual "interlinear" reading interface.

## Features

- 📄 Upload any Spanish PDF
- 🌐 Automatic Spanish → English translation (runs locally, no API costs)
- 📖 Interlinear display: Spanish sentences with English translations directly below
- 🎨 Clean styling: Spanish (bold, black) / English (italic, gray)

## Installation

### 1. Create and activate virtual environment

```bash
cd bilingual-reader
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download NLTK data (first-time only)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

## Usage

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Notes

- **First run**: The translation model (~300MB) will download automatically
- **Performance**: Large PDFs may take a few minutes on CPU
- **GPU**: If you have a CUDA GPU, install `torch` with CUDA support for faster translation

## Tech Stack

- **Streamlit** - Web UI
- **PyMuPDF** - PDF text extraction
- **NLTK** - Sentence tokenization
- **Transformers + MarianMT** - Local neural machine translation
