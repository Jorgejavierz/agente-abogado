# backend/routes/pdf.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import io
import fitz  # ✅ PyMuPDF
from PIL import Image

# Configuración de Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta explícita de Poppler en Windows
POPPLER_PATH = r"C:\Program Files\poppler-25.12.0\Library\bin"

router = APIRouter(tags=["PDF"])

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------
# Utilidad interna: OCR + extracción
# ---------------------------
def extraer_texto_pdf(file_bytes: bytes) -> str:
    """
    Extrae texto de un PDF usando PyPDF2 y OCR como fallback.
    Si pdf2image falla, usa PyMuPDF para rasterizar páginas.
    """
    try:
        # Intento con PyPDF2
        reader = PdfReader(io.BytesIO(file_bytes))
        texto = ""
        for page in reader.pages:
            contenido = page.extract_text() or ""
            texto += contenido + "\n"

        texto = texto.strip()
        if texto:
            return texto

        # Si no hay texto → OCR con pdf2image
        try:
            imagenes = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
            texto_ocr = ""
            for img in imagenes:
                texto_ocr += pytesseract.image_to_string(img, lang="spa") + "\n"
            return texto_ocr.strip()
        except Exception:
            # Fallback final: usar PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            texto_ocr = ""
            for page in doc:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                texto_ocr += pytesseract.image_to_string(img, lang="spa") + "\n"
            return texto_ocr.strip()

    except Exception as e:
        print(f"Error al procesar PDF: {e}")
        return ""


# ---------------------------
# Indexación en FAISS
# ---------------------------
def indexar_texto_en_faiss(texto: str, fuente: str):
    """
    Convierte el texto en embeddings y lo agrega al índice FAISS.
    Guarda también la fuente del documento.
    """
    try:
        # Cargar índice y corpus existentes
        index = faiss.read_index("backend/faiss_index/index.faiss")
        with open("backend/faiss_index/corpus.pkl", "rb") as f:
            corpus = pickle.load(f)

        # Dividir texto en párrafos
        nuevos_parrafos = [p.strip() for p in texto.split("\n") if p.strip()]
        embeddings = model.encode(nuevos_parrafos)

        # Actualizar índice y corpus con metadatos
        index.add(embeddings)
        corpus.extend([{"texto": p, "fuente": fuente} for p in nuevos_parrafos])

        faiss.write_index(index, "backend/faiss_index/index.faiss")
        with open("backend/faiss_index/corpus.pkl", "wb") as f:
            pickle.dump(corpus, f)

        print(f"Indexación completada: {len(nuevos_parrafos)} párrafos agregados de {fuente}.")

    except Exception as e:
        print(f"Error al indexar texto en FAISS: {e}")


# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/pdf")
async def procesar_pdf(file: UploadFile = File(...)):
    """
    Extrae texto de un PDF. Si no tiene texto embebido, aplica OCR.
    Devuelve el texto extraído y lo indexa en FAISS con su fuente.
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

        # Indexar el texto extraído con fuente
        indexar_texto_en_faiss(contenido, file.filename)

        return {
            "status": "ok",
            "texto": contenido,
            "indexado": True,
            "fuente": file.filename,
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error en /pdf: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
