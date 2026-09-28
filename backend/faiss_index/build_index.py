# backend/faiss_index/build_index.py

import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from backend.routes.pdf import extraer_texto_pdf  # OCR centralizado

# Modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Directorio de documentos
DOCS_DIR = "Documentos legales"
INDEX_PATH = "backend/faiss_index/index.faiss"
CORPUS_PATH = "backend/faiss_index/corpus.pkl"


def cargar_documentos():
    """
    Carga todos los PDFs del directorio, extrae texto (con OCR si es necesario),
    y devuelve una lista de dicts con texto + fuente.
    """
    corpus = []
    for archivo in os.listdir(DOCS_DIR):
        if not archivo.lower().endswith(".pdf"):
            continue

        ruta = os.path.join(DOCS_DIR, archivo)
        with open(ruta, "rb") as f:
            file_bytes = f.read()
            texto = extraer_texto_pdf(file_bytes)

        if not texto:
            print(f"⚠️ No se pudo extraer texto de {archivo}, se descarta.")
            continue

        # Dividir en párrafos y guardar con fuente
        parrafos = [p.strip() for p in texto.split("\n") if p.strip()]
        corpus.extend([{"texto": p, "fuente": archivo} for p in parrafos])

        print(f"✅ {archivo}: {len(parrafos)} párrafos indexados.")

    return corpus


def construir_indice(corpus):
    """
    Construye el índice FAISS a partir del corpus.
    """
    textos = [item["texto"] for item in corpus]
    embeddings = model.encode(textos)

    # Crear índice FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Guardar índice y corpus
    faiss.write_index(index, INDEX_PATH)
    with open(CORPUS_PATH, "wb") as f:
        pickle.dump(corpus, f)

    print(f"📚 Corpus total: {len(corpus)} párrafos.")
    print("✅ Índice FAISS construido y guardado.")


if __name__ == "__main__":
    corpus = cargar_documentos()
    if corpus:
        construir_indice(corpus)
    else:
        print("⚠️ No se encontraron documentos válidos para indexar.")
