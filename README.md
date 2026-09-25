# AI_Compassion — Offline EN ↔ JA Document Translator

A robust, **100% offline** Python CLI application for document translation (`.txt`, `.docx`, `.pdf`) between **English** and **Japanese**. Powered by [Argos Translate](https://github.com/argosopentech/argos-translate) (CTranslate2 / OpenNMT), this tool guarantees complete data privacy, eliminates external API rate limits, and runs entirely on local hardware.

---

## ✨ Key Features

### 1. 100% Offline Translation Engine
- **Engine migration**: refactored from web-based translation APIs (Google Translate, MyMemory) to a fully local engine powered by `argostranslate`.
- **Zero external dependencies at runtime**: no more network errors, `429 Too Many Requests`, IP throttling, or service quotas.
- **Data privacy**: all translation logic and text parsing happen exclusively on your local machine.

### 2. Install-on-Demand Models & Repository Optimization
- **Automatic model management**: detects missing language pair models (`en ↔ ja`) and downloads them automatically on first run.
- **Global storage architecture**: model packages (`.argosmodel`) are cached in the system user directory (`~/.local/share/argos-translate/packages`), keeping the repo lightweight and under GitHub's 100 MB file limit.
- **System-wide reusability**: installed models are shared across any local Python script or app — no duplicate downloads.

### 3. Automatic Hardware Acceleration
- **GPU / CPU adaptability**: CTranslate2 automatically detects CUDA-compatible NVIDIA GPUs to accelerate translation.
- **Graceful fallback**: reverts to multi-threaded CPU execution when no GPU/CUDA drivers are present, avoiding crashes.

### 4. Multi-Format File Handling & CJK Font Support
- **Full document support**: reads, extracts, and generates `.txt`, `.docx`, and `.pdf` files.
- **Japanese font rendering**: integrates ReportLab's `HeiseiMin-W3` Unicode CID font to prevent garbled text or square-box glyph errors when exporting Japanese text to PDF.

### 5. Paragraph-Level Chunking for Large Documents
- **Large file support**: processes documents over 10,000 characters without context loss or truncation.
- **Contextual preservation**: splits text along natural paragraph boundaries (not arbitrary character limits), preserving NMT translation quality and sentence structure.

### 6. Dependency Optimization & Clean Project Structure
- **Standardized dependencies**: version-pinned `requirements.txt`, deprecated web-translation packages removed.
- **Version control hygiene**: `.gitignore` excludes generated translation artifacts (`*_to_*.txt`, `*_to_*.docx`, `*_to_*.pdf`) and cache directories.

---

## 🛠 Tech Stack

| Component | Library / Framework | Purpose |
|---|---|---|
| Language | Python 3.10+ | Primary development environment |
| Translation Engine | `argostranslate` | Offline NMT (CTranslate2 / OpenNMT) |
| Language Detection | `langdetect` | Automatic source language identification (EN vs JA) |
| Word Processing | `python-docx` | Reading and writing `.docx` documents |
| PDF Extraction | `pdfplumber` | Accurate text extraction from `.pdf` files |
| PDF Generation | `reportlab` | PDF creation with native CJK font support |

---

## 📁 Repository Structure

```
AI_Compassion/
├── TranslatorApp.py       # Main CLI application entry point and translation logic
├── requirements.txt       # Cleaned, version-pinned project dependencies
├── .gitignore              # Git rules to exclude outputs and cache
└── README.md               # Technical project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd AI_Compassion
   ```

2. **Activate your Python environment**
   ```bash
   conda activate AI_Compassion
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage Guide

Run `TranslatorApp.py` by specifying the path to your input document and the target output format (`txt`, `docx`, or `pdf`).

### Syntax
```bash
python TranslatorApp.py <input_file> <output_format>
```

### Execution Examples

**Translate a Text File to Word Document (EN → JA):**
```bash
python TranslatorApp.py test_en.txt docx
```
Generated output: `test_en_en_to_ja.docx`

**Translate a Japanese Document to Plain Text (JA → EN):**
```bash
python TranslatorApp.py test_ja.txt txt
```
Generated output: `test_ja_ja_to_en.txt`

**Translate a Word File to PDF (EN → JA):**
```bash
python TranslatorApp.py document.docx pdf
```
Generated output: `document_en_to_ja.pdf`

> The source and target languages are auto-detected from the input text — you only need to specify the desired **output format**.

---

## 📦 Model Storage Locations

To keep Git commits light, translation models are saved globally on your machine:

| OS | Path |
|---|---|
| Windows | `C:\Users\<user>\.local\share\argos-translate\packages` |
| Linux / macOS | `~/.local/share/argos-translate/packages` |

---

## 📝 Operating Notes

- **First-run network access**: an internet connection is required only once per language direction (`en → ja` or `ja → en`) to download the required models. All subsequent translations run 100% offline.
- **File lock prevention (`PermissionError`)**: close generated output files in external applications (e.g., Microsoft Word or Adobe Acrobat) before re-running translations, to avoid file lock errors.

---

## 📋 Requirements

```
argostranslate>=1.11.0
python-docx>=0.8.11
pdfplumber>=0.10.0
reportlab>=4.0.0
langdetect>=1.0.9
```

---

## 📄 License

Add your license of choice here (e.g., MIT, Apache 2.0).