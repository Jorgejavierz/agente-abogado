from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader

pdf_path = "Codigo Penal.pdf"

# Intento con PyPDF2
reader = PdfReader(pdf_path)
print("=== Texto con PyPDF2 ===")
for i, page in enumerate(reader.pages, start=1):
    print(page.extract_text())

# Intento con OCR
print("\n=== Texto con OCR ===")
pages = convert_from_path(pdf_path)
for i, page in enumerate(pages, start=1):
    text = pytesseract.image_to_string(page, lang="spa")
    print(f"Página {i}:\n{text}")