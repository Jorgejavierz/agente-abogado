# backend/faiss_index/search.py
# Funciones para buscar en FAISS

import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Cargar modelo y datos
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("backend/faiss_index/index.faiss")

with open("backend/faiss_index/corpus.pkl", "rb") as f:
    corpus = pickle.load(f)

def buscar_en_faiss(consulta: str, k: int = 3):
    """
    Busca en el índice FAISS los k documentos más relevantes.
    """
    consulta_embedding = model.encode([consulta])
    distances, indices = index.search(consulta_embedding, k)

    resultados = []
    for idx in indices[0]:
        resultados.append(corpus[idx])

    return resultados
