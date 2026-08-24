# backend/faiss_index/build_index.py
# Script para construir el índice FAISS con corpus jurídico

import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

# Modelo de embeddings (podés cambiarlo por otro más específico)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Corpus jurídico de ejemplo (luego lo reemplazás por tus textos reales)
corpus = [
    "Artículo 245 LCT: indemnización por despido.",
    "Artículo 14 bis Constitución Nacional: derechos laborales.",
    "Ley 20.744: contrato de trabajo.",
    "Jurisprudencia: fallo 'Pérez c/ Empresa X' sobre despido injustificado."
]

# Convertir corpus en embeddings
embeddings = model.encode(corpus)

# Crear índice FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Guardar índice
faiss.write_index(index, "backend/faiss_index/index.faiss")

# Guardar corpus para referencia
with open("backend/faiss_index/corpus.pkl", "wb") as f:
    pickle.dump(corpus, f)

print("Índice FAISS creado y corpus guardado correctamente.")
