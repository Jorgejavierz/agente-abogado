from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384

# Archivos persistentes
INDEX_FILE = "faiss_index.bin"
DOCS_FILE = "documentos.json"

# Cargar índice FAISS si existe
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
else:
    index = faiss.IndexFlatL2(dimension)

# Cargar documentos si existen
if os.path.exists(DOCS_FILE):
    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        documentos = json.load(f)
else:
    documentos = []

class Documento(BaseModel):
    texto: str
    respuesta: str

@app.get("/health")
def health_check():
    return {"status": "ok", "documentos": len(documentos)}

@app.post("/guardar")
def guardar(doc: Documento):
    if not doc.texto.strip():
        return {"error": "El texto está vacío"}

    try:
        embedding = model.encode([doc.texto])
        embedding = np.array(embedding, dtype=np.float32)
    except Exception as e:
        return {"error": f"Error generando embedding: {e}"}

    try:
        index.add(embedding)
    except Exception as e:
        return {"error": f"Error agregando al índice FAISS: {e}"}

    documentos.append({"texto": doc.texto, "respuesta": doc.respuesta})

    # Guardar persistencia
    faiss.write_index(index, INDEX_FILE)
    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)

    return {"mensaje": "Documento guardado", "total": len(documentos)}

@app.get("/buscar")
def buscar(texto: str, k: int = 3):
    if not texto.strip():
        return {"error": "El texto de consulta está vacío"}

    if len(documentos) == 0:
        return {"resultados": [], "mensaje": "No hay documentos en el índice"}

    try:
        embedding = model.encode([texto])
        embedding = np.array(embedding, dtype=np.float32)
    except Exception as e:
        return {"error": f"Error generando embedding: {e}"}

    try:
        D, I = index.search(embedding, k)
    except Exception as e:
        return {"error": f"Error buscando en FAISS: {e}"}

    resultados = []
    for dist, idx in zip(D[0], I[0]):
        if idx < len(documentos):
            doc = documentos[idx]
            resultados.append({
                "texto": doc["texto"],
                "respuesta": doc["respuesta"],
                "distancia": float(dist)
            })

    return {"consulta": texto, "resultados": resultados}
