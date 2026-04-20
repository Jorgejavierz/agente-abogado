# backend/routes/analizar.py

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
import io
import logging
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

# Configuración de Tesseract en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = logging.getLogger("backend.routes.analizar")

# Definir el router antes de usarlo en decoradores
router = APIRouter(tags=["Analizar"])


# ---------------------------
# Modelo de entrada
# ---------------------------
class AnalizarInput(BaseModel):
    texto: str | None = None
    text: str | None = None
    tipo: str | None = "consulta"

    @property
    def contenido(self) -> str:
        return (self.texto or self.text or "").strip()


# ---------------------------
# Utilidades internas
# ---------------------------
def extraer_texto_pdf(file_bytes: bytes) -> str:
    """Extrae texto de un PDF usando PyPDF2 y OCR como fallback."""
    try:
        # PdfReader espera un stream o path; usamos BytesIO
        reader = PdfReader(io.BytesIO(file_bytes))
        texto = ""

        for page in reader.pages:
            contenido = page.extract_text() or ""
            texto += contenido + "\n"

        texto = texto.strip()
        if texto:
            return texto

        # Si no hay texto → usar OCR (pdf2image)
        try:
            imagenes = convert_from_bytes(file_bytes)
        except Exception as e_conv:
            logger.exception("pdf2image falló al convertir bytes a imágenes: %s", e_conv)
            # Si necesitás usar poppler en Windows, descomentá y ajustá la línea siguiente:
            # imagenes = convert_from_bytes(file_bytes, poppler_path=r"C:\ruta\a\poppler\bin")
            raise

        texto_ocr = ""
        for img in imagenes:
            texto_ocr += pytesseract.image_to_string(img, lang="spa") + "\n"

        return texto_ocr.strip()

    except Exception as e:
        logger.exception("Error al procesar PDF en extraer_texto_pdf: %s", e)
        return ""


# ---------------------------
# Endpoint principal (alias + original)
# ---------------------------
@router.post("/procesar-documento")
@router.post("/analizar")
async def analizar_documento(
    request: Request,
    entrada: AnalizarInput | None = None,
    file: UploadFile | None = File(None)
):
    """
    Analiza texto o PDF y devuelve un informe jurídico estructurado.
    """

    agente = request.app.state.agent
    contenido = ""

    try:
        # Caso 1: archivo PDF
        if file:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")

            file_bytes = await file.read()
            contenido = extraer_texto_pdf(file_bytes)

            if not contenido:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo extraer texto del PDF, ni siquiera con OCR."
                )

        # Caso 2: texto enviado en JSON
        elif entrada:
            contenido = entrada.contenido

        # Validación
        if not contenido:
            raise HTTPException(status_code=400, detail="No se recibió texto válido para analizar.")

        # Delegar al agente jurídico (método correcto)
        resultado = agente.responder(contenido)

        # Construcción del informe narrativo
        informe = f"""
⚖️ Informe Jurídico Automatizado

1. Consulta recibida:
{resultado.get('consulta', 'Sin consulta disponible.')}

2. Explicación doctrinal:
{resultado.get('explicacion_doctrinal', 'No se encontró explicación doctrinal.')}
Fuente: {resultado.get('fuente', 'Sin fuente disponible')}

3. Jurisprudencia relevante:
{resultado.get('jurisprudencia_relevante', 'No se encontraron antecedentes.')}

4. Fallos relacionados:
{len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

5. Clasificación del caso:
{resultado.get('clasificacion', 'Sin clasificación.')}

6. Recomendaciones:
{resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

7. Conclusión:
{resultado.get('conclusion', 'Sin conclusión disponible.')}
"""

        return {
            "status": "ok",
            "informe": informe.strip(),
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error en /analizar: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


# ---------------------------
# Endpoint GET para consultas rápidas
# ---------------------------
@router.get("/consultar_documento")
async def consultar_documento(request: Request, pregunta: str = Query(..., min_length=1)):
    """
    Endpoint para consultas rápidas por texto: /consultar_documento?pregunta=...
    """
    agente = request.app.state.agent
    try:
        contenido = pregunta.strip()
        if not contenido:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

        resultado = agente.responder(contenido)

        informe = f"""
⚖️ Informe Jurídico Automatizado

1. Consulta recibida:
{resultado.get('consulta', 'Sin consulta disponible.')}

2. Explicación doctrinal:
{resultado.get('explicacion_doctrinal', 'No se encontró explicación doctrinal.')}
Fuente: {resultado.get('fuente', 'Sin fuente disponible')}

3. Jurisprudencia relevante:
{resultado.get('jurisprudencia_relevante', 'No se encontraron antecedentes.')}

4. Fallos relacionados:
{len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

5. Clasificación del caso:
{resultado.get('clasificacion', 'Sin clasificación.')}

6. Recomendaciones:
{resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

7. Conclusión:
{resultado.get('conclusion', 'Sin conclusión disponible.')}
"""
        return {
            "status": "ok",
            "informe": informe.strip(),
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en /consultar_documento: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
