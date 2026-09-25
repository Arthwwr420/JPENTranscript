import os
import sys
import docx
import time
import pdfplumber
import argostranslate.package
import argostranslate.translate
from langdetect import detect, DetectorFactory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

## ------- Seed already pinned for consistent results -------
DetectorFactory.seed = 0
# Register a font for Japanese characters
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

# ------------------------- Module 1 read archives -------------------------

def read_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read() 

def read_docx(filepath: str):
    doc = docx.Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def read_pdf(filepath: str) -> str:
    text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text.append(extracted)
    return "\n".join(text)

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return read_txt(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.pdf':
        return read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

#------------------------- Module 2 detect language and translation -------------------------
def ensure_model_installed(src_lang: str, target_lang: str):
    """
    Ensures and installs automatically the language model if doesnt exists
    """
    installed_languages = argostranslate.translate.get_installed_languages()

    src = next((l for l in installed_languages if l.code == src_lang), None)
    target = next((l for l in installed_languages if l.code == target_lang), None)

    if src and target and src.get_translation(target):
        return  # Model already installed

    print(f"[INFO] Local model ({src_lang} -> {target_lang}) not found. Downloading and installing...")
    print(f"[INFO] Please wait, this may take a few minutes depending on your internet connection...")

    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    package_to_install = next(
        filter(
            lambda x: x.from_code == src_lang and x.to_code == target_lang,
            available_packages
        ), None
    )

    if package_to_install:
        download_path = package_to_install.download()        
        argostranslate.package.install_from_path(download_path)
        print(f"[INFO] Model ({src_lang} -> {target_lang}) installed successfully.")
    else:
        raise ValueError(f"No available translation package found for {src_lang} -> {target_lang}")



def detect_and_translate(text: str) -> tuple[str, str, str]:
    """
    Detects the language of the given text and returns 
    the language code, name, and confidence level.
    """
    sample = detect(text[:1000])  # Evaluates the first 1000 characters to increase accuracy and of course to detect which language is being used

    if sample.startswith('ja'):
        src_lang = 'ja'
        target_lang = 'en'
    else: 
        src_lang = 'en'
        target_lang = 'ja'

    print(f"[INFO] detected language: {src_lang.upper()} -> language required: {target_lang.upper()} ")

    ensure_model_installed(src_lang, target_lang)
    
    installed_languages = argostranslate.translate.get_installed_languages()
    src = next(l for l in installed_languages if l.code == src_lang)
    target = next(l for l in installed_languages if l.code == target_lang)
    translation = src.get_translation(target)

    paragraphs = text.split('\n')
    translated_paragraphs = []

    for paragraph in paragraphs:
        clean_paragraph = paragraph.strip()
        if clean_paragraph:
            translated_text = translation.translate(clean_paragraph)
            translated_paragraphs.append(translated_text)    
        else:
            translated_paragraphs.append("")

    return "\n".join(translated_paragraphs), src_lang, target_lang

#------------------------- Module 3 write and archives exportations -------------------------

def write_txt(text: str, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

def write_docx(text: str, output_path: str):
    doc = docx.Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    doc.save(output_path)

def write_pdf(text: str, output_path: str, target_lang: str):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y_position = height - 40  
    line_height = 14

    font_name = "HeiseiMin-W3" if target_lang == 'ja' else "Helvetica"
    c.setFont(font_name, 10)

    for line in text.split('\n'):
        if y_position < 40:  
            c.showPage()
            c.setFont(font_name, 10)
            y_position = height - 40

        max_lenght = 40 if target_lang == 'ja' else 80
        c.drawString(40, y_position, line[:max_lenght])
        y_position -= line_height

    c.save()

def export_file(text: str, output_path: str, target_lang: str):
    ext = os.path.splitext(output_path)[1].lower()
    if ext == '.txt':
        write_txt(text, output_path)
    elif ext == '.docx':
        write_docx(text, output_path)
    elif ext == '.pdf':
        write_pdf(text, output_path, target_lang)
    else:
        raise ValueError(f"Unsupported file: {ext}")

# --------------------------- Main function -------------------------

def process_document(input_file: str, output_format: str):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Infput archive not exists: {input_file}")

    print(f"[1/3] Reading input file: {input_file}...")
    raw_text = extract_text(input_file)

    if not raw_text.strip():
        raise ValueError("The input file is empty or contains no readable text.")

    print(f"[2/3] Detecting language and translating...")
    translated_content, src_lang, target_lang = detect_and_translate(raw_text)

    output_format = output_format.strip('.').lower()
    base_name = os.path.splitext(input_file)[0]
    output_filename = f"{base_name}_{src_lang}_to_{target_lang}.{output_format}"  


    print(f"[3/3] Exporting translateted content to {output_format}...")
    export_file(translated_content, output_filename, target_lang)

    print(f"[INFO] Translation completed successfully! Output file: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python translator_app.py  ")
    else:
        process_document(sys.argv[1], sys.argv[2])  