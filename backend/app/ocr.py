# backend/app/ocr.py
import PyPDF2

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text