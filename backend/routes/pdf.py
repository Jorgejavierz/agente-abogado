# routes/pdf.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

# Configuración de Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

router = APIRouter(tags=["PDF"])


# ---------------------------
# Utilidad interna
# ---------------------------
def extraer_texto_pdf(file_bytes: bytes) -> str:
    """Extrae texto de un PDF usando PyPDF2 y OCR como fallback."""
    try:
        reader = PdfReader(file_bytes)
        texto = ""

        for page in reader.pages:
            contenido = page.extract_text() or ""
            texto += contenido + "\n"

        texto = texto.strip()

        if texto:
            return texto

        # Si no hay texto → usar OCR
        imagenes = convert_from_bytes(file_bytes)
        texto_ocr = ""

        for img in imagenes:
            texto_ocr += pytesseract.image_to_string(img, lang="spa") + "\n"

        return texto_ocr.strip()

    except Exception as e:
        print(f"Error al procesar PDF: {e}")
        return ""


# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/pdf")
async def procesar_pdf(file: UploadFile = File(...)):
    """
    Extrae texto de un PDF. Si no tiene texto embebido, aplica OCR.
    Devuelve únicamente el texto extraído.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")

    try:
        file_bytes = await file.read()
        contenido = extraer_texto_pdf(file_bytes)

        if not contenido:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer texto del PDF, ni siquiera con OCR."
            )

        return {
            "status": "ok",
            "texto": contenido,
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error en /pdf: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
