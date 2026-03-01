from fastapi import APIRouter, UploadFile, File
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
import os

router = APIRouter()

@router.post("/procesar-pdf/")
async def procesar_pdf(file: UploadFile = File(...)):
    # Guardar temporalmente el PDF subido
    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    resultado = {"texto_pypdf2": [], "texto_ocr": []}

    try:
        # 1. Intentar extraer texto digital con PyPDF2
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                resultado["texto_pypdf2"].append({"pagina": i, "texto": text})

        # 2. Si no hay texto, usar OCR con Poppler + Tesseract
        if not resultado["texto_pypdf2"]:
            pages = convert_from_path(pdf_path)
            for i, page in enumerate(pages, start=1):
                text = pytesseract.image_to_string(page, lang="spa")
                resultado["texto_ocr"].append({"pagina": i, "texto": text})

    finally:
        # Borrar archivo temporal
        os.remove(pdf_path)

    return resultado