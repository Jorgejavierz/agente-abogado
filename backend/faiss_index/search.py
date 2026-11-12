# backend/faiss_index/search.py
# API para consultar el índice FAISS con metadatos

import faiss
import pickle

from fastapi import APIRouter, FastAPI, Query
from pydantic import BaseModel

# Crear router
router = APIRouter()

# ============================================================
# Lazy Loading
# ============================================================

_model = None
_index = None
_corpus = None


def get_model():
    global _model

    if _model is None:

        print("Cargando modelo FAISS...")

        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Modelo FAISS cargado.")

    return _model


def get_index():
    global _index

    if _index is None:

        _index = faiss.read_index(
            "backend/faiss_index/index.faiss"
        )

    return _index


def get_corpus():
    global _corpus

    if _corpus is None:

        with open(
            "backend/faiss_index/corpus.pkl",
            "rb"
        ) as f:

            _corpus = pickle.load(f)

    return _corpus


# ============================================================
# Búsqueda
# ============================================================

def buscar_en_faiss(
    consulta: str,
    k: int = 3
):
    """
    Busca en el índice FAISS los documentos más relevantes.
    """

    model = get_model()
    index = get_index()
    corpus = get_corpus()

    consulta_embedding = model.encode(
        [consulta]
    )

    distances, indices = index.search(
        consulta_embedding,
        k
    )

    resultados = []

    for i, idx in enumerate(indices[0]):

        if idx < 0 or idx >= len(corpus):
            continue

        if isinstance(corpus[idx], dict):

            resultados.append({
                "texto": corpus[idx].get(
                    "texto",
                    ""
                )[:600] + "...",

                "documento": corpus[idx].get(
                    "fuente",
                    f"Documento_{idx + 1}"
                ),

                "distancia": float(
                    distances[0][i]
                )
            })

        else:

            resultados.append({
                "texto": str(
                    corpus[idx]
                )[:600] + "...",

                "documento": f"Documento_{idx + 1}",

                "distancia": float(
                    distances[0][i]
                )
            })

    return resultados


# ============================================================
# Modelo de entrada
# ============================================================

class Consulta(BaseModel):
    query: str
    k: int = 3


# ============================================================
# Router FastAPI
# ============================================================

@router.post("/buscar")
def buscar_post(payload: Consulta):

    resultados = buscar_en_faiss(
        payload.query,
        payload.k
    )

    return {
        "consulta": payload.query,
        "resultados": resultados
    }


# ============================================================
# Compatibilidad servidor standalone
# ============================================================

app = FastAPI(
    title="FAISS Search API"
)


@app.get("/buscar")
def buscar_get(
    texto: str = Query(...),
    k: int = Query(3)
):

    resultados = buscar_en_faiss(
        texto,
        k
    )

    return {
        "consulta": texto,
        "resultados": resultados
    }