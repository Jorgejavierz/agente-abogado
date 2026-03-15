import os
import json
import logging
import traceback
import tempfile
import shutil

from fastapi import FastAPI, UploadFile, File, Response, status
from fastapi.middleware.cors import CORSMiddleware

import requests
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
import uvicorn

# Importar configuración y routers
from agente_abogado.config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION
from agente_abogado.legal_agent import LaborLawyerAgent

from agente_abogado.routes import (
    health,
    analizar,
    feedback,
    memoria,
    chat,
    intereses
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agente_abogado")

# FAISS_SERVER configurable por variable de entorno
FAISS_SERVER = os.getenv("FAISS_SERVER", "http://127.0.0.1:8081")

# Inicializar FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configuración CORS (usar ALLOWED_ORIGINS desde config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el agente con manejo de errores para que no rompa el startup
try:
    app.state.agent = LaborLawyerAgent()
    logger.info("LaborLawyerAgent inicializado correctamente.")
except Exception:
    logger.exception("Error al inicializar LaborLawyerAgent. La app seguirá levantando pero el agente puede fallar.")

# Registrar routers
app.include_router(health.router)
app.include_router(analizar.router)
app.include_router(feedback.router)
app.include_router(memoria.router)
app.include_router(chat.router)
app.include_router(intereses.router)

# Endpoint para subir documentos y cargarlos en FAISS
@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    # Usar archivo temporal para evitar colisiones y problemas con OneDrive
    tmp_dir = tempfile.mkdtemp(prefix="agente_doc_")
    pdf_path = os.path.join(tmp_dir, file.filename)
    try:
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        texto_total = ""

        # 1. Intentar extraer texto digital con PyPDF2
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texto_total += text + "\n"
        except Exception:
            logger.info("PyPDF2 no pudo extraer texto, se intentará OCR.")
            logger.debug(traceback.format_exc())

        # 2. Si no hay texto, usar OCR con Poppler + Tesseract
        if not texto_total.strip():
            try:
                pages = convert_from_path(pdf_path)
                for page in pages:
                    text = pytesseract.image_to_string(page, lang="spa")
                    texto_total += text + "\n"
            except Exception:
                logger.exception("Error durante OCR con pdf2image/pytesseract.")

        # Dividir en fragmentos de ~400 palabras
        palabras = texto_total.split()
        fragmentos = [
            " ".join(palabras[i:i+400])
            for i in range(0, len(palabras), 400)
        ] if palabras else []

        # Guardar en FAISS (con timeout y manejo de errores)
        guardados = 0
        for idx, frag in enumerate(fragmentos):
            payload = {"texto": frag, "respuesta": f"Fragmento {idx+1}"}
            try:
                r = requests.post(f"{FAISS_SERVER}/guardar", json=payload, timeout=8)
                r.raise_for_status()
                guardados += 1
            except Exception:
                logger.exception("Error al guardar fragmento en FAISS (continuando con el siguiente).")

        return {"mensaje": "Documento procesado", "fragmentos": len(fragmentos), "guardados": guardados}

    finally:
        # Limpiar archivos temporales
        try:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
        except Exception:
            logger.exception("Error al eliminar archivos temporales.")

# Endpoint para consultar documentos cargados en FAISS y responder con el agente
@app.get("/consultar_documento")
async def consultar_documento(pregunta: str, k: int = 3):
    try:
        # Llamada a FAISS con timeout y manejo de errores
        try:
            resp = requests.get(
                f"{FAISS_SERVER}/buscar",
                params={"texto": pregunta, "k": k},
                timeout=8
            )
            resp.raise_for_status()
            resultados = resp.json().get("resultados", [])
        except Exception as e_faiss:
            logger.exception("Error consultando FAISS.")
            # No abortamos: devolvemos un arreglo vacío de fragmentos y seguimos
            resultados = []
            # opcional: incluir detalle en logs, pero no exponer todo al cliente
            faiss_error = str(e_faiss)
        # Usar el agente para generar informe (manejar si el agente falla)
        try:
            informe = app.state.agent.responder_pregunta(pregunta)
        except Exception:
            logger.exception("Error en app.state.agent.responder_pregunta")
            informe = "No se pudo generar informe (error interno del agente)."

        response_payload = {
            "pregunta": pregunta,
            "informe": informe,
            "fragmentos": resultados
        }
        # Si hubo error con FAISS, añadir detalle mínimo
        if 'faiss_error' in locals():
            response_payload["faiss_error"] = "No se pudo conectar con FAISS en producción."

        return response_payload

    except Exception as e:
        # Capturar cualquier excepción inesperada, loguearla y devolver 500 controlado
        logger.exception("Error interno en /consultar_documento")
        traceback.print_exc()
        return Response(
            content=json.dumps({"error": "Error interno", "detalle": str(e)}),
            media_type="application/json",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Bloque para ejecución local y en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("agente_abogado.main:app", host="0.0.0.0", port=port, log_level="info")