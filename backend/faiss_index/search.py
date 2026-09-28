# backend/faiss_index/search.py
# API para consultar el índice FAISS con metadatos

import faiss
import pickle
from sentence_transformers import SentenceTransformer
from fastapi import APIRouter
from pydantic import BaseModel

# Crear router en lugar de app
router = APIRouter()

# Cargar modelo y datos
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("backend/faiss_index/index.faiss")

with open("backend/faiss_index/corpus.pkl", "rb") as f:
    corpus = pickle.load(f)

def buscar_en_faiss(consulta: str, k: int = 3):
    """
    Busca en el índice FAISS los k documentos más relevantes.
    Devuelve texto + fuente del documento + distancia de similitud.
    """
    consulta_embedding = model.encode([consulta])
    distances, indices = index.search(consulta_embedding, k)

    resultados = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(corpus):
            continue

        if isinstance(corpus[idx], dict):
            resultados.append({
                "texto": corpus[idx].get("texto", "")[:600] + "...",
                "documento": corpus[idx].get("fuente", f"Documento_{idx+1}"),
                "distancia": float(distances[0][i])
            })
        else:
            resultados.append({
                "texto": str(corpus[idx])[:600] + "...",
                "documento": f"Documento_{idx+1}",
                "distancia": float(distances[0][i])
            })

    return resultados

# Modelo para recibir JSON
class Consulta(BaseModel):
    query: str
    k: int = 3

@router.post("/buscar")
def buscar(payload: Consulta):
    """
    Endpoint HTTP para buscar en FAISS.
    Recibe JSON: {"query": "...", "k": 3}
    """
    resultados = buscar_en_faiss(payload.query, payload.k)
    return {"consulta": payload.query, "resultados": resultados}
from fastapi import FastAPI, Query

app = FastAPI(title="FAISS Search API")

@app.get("/buscar")
def buscar(texto: str = Query(...), k: int = Query(3)):
    """
    Endpoint HTTP para buscar en FAISS.
    """
    resultados = buscar_en_faiss(texto, k)
    return {"consulta": texto, "resultados": resultados}
