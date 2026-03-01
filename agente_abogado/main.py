from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from agente_abogado.config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION
from agente_abogado.legal_agent import LaborLawyerAgent  # importar el agente

# Importar routers desde la carpeta routes
from agente_abogado.routes import (
    health,
    analizar,
    feedback,
    memoria,
    chat,
    intereses   # 👈 nuevo router para la calculadora de intereses
)

import requests
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
import os
import uvicorn

# Dirección del servidor FAISS (ajustar si lo desplegás en otro host/puerto)
FAISS_SERVER = "http://127.0.0.1:8081"

# Inicializar aplicación FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # dominios permitidos (ej. Vercel, localhost)
    allow_credentials=True,
    allow_methods=["*"],             # permitir todos los métodos
    allow_headers=["*"],             # permitir todos los headers
)

# Inicializar el agente y guardarlo en el estado de la app
app.state.agent = LaborLawyerAgent()

# Registrar routers
app.include_router(health.router)
app.include_router(analizar.router)
app.include_router(feedback.router)
app.include_router(memoria.router)
app.include_router(chat.router)
app.include_router(intereses.router)  # 👈 integración del nuevo endpoint

# Endpoint para subir documentos y cargarlos en FAISS
@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    # Guardar temporalmente el PDF subido
    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    texto_total = ""

    try:
        # 1. Intentar extraer texto digital con PyPDF2
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texto_total += text + "\n"

        # 2. Si no hay texto, usar OCR con Poppler + Tesseract
        if not texto_total.strip():
            pages = convert_from_path(pdf_path)
            for page in pages:
                text = pytesseract.image_to_string(page, lang="spa")
                texto_total += text + "\n"

        # Dividir en fragmentos
        palabras = texto_total.split()
        fragmentos = [
            " ".join(palabras[i:i+400])
            for i in range(0, len(palabras), 400)
        ]

        # Guardar en FAISS
        for idx, frag in enumerate(fragmentos):
            payload = {"texto": frag, "respuesta": f"Fragmento {idx+1}"}
            requests.post(f"{FAISS_SERVER}/guardar", json=payload)

        return {"mensaje": "Documento cargado correctamente", "fragmentos": len(fragmentos)}

    finally:
        # Borrar archivo temporal
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# Endpoint para consultar documentos cargados en FAISS y responder con el agente
@app.get("/consultar_documento")
async def consultar_documento(pregunta: str, k: int = 3):
    # Consultar FAISS para obtener fragmentos relevantes
    resp = requests.get(f"{FAISS_SERVER}/buscar", params={"texto": pregunta, "k": k})
    
    if resp.status_code == 200:
        resultados = resp.json().get("resultados", [])
        # Pasar la pregunta al agente laboral para generar un informe narrativo
        informe = app.state.agent.responder_pregunta(pregunta)
        return {
            "pregunta": pregunta,
            "informe": informe,
            "fragmentos": resultados
        }
    else:
        return {"error": "No se pudo consultar FAISS", "detalle": resp.text}

# Bloque para ejecución local y en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render asigna el puerto
    uvicorn.run("agente_abogado.main:app", host="0.0.0.0", port=port)