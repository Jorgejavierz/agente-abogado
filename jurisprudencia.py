# jurisprudencia.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class Jurisprudencia:
    """
    Clase para buscar fallos judiciales en bases públicas mediante scraping
    y también realizar búsquedas semánticas sobre una base local de fallos.
    """

    BASE_URL = "http://juriscivil.jusneuquen.gov.ar/"

    def __init__(self, base_url: str = None):
        # Scraping
        self.base_url = base_url or self.BASE_URL
        self.headers = {"User-Agent": "Mozilla/5.0"}

        # Embeddings y FAISS
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.fallos = []
        self.index = None

    # -------------------------------
    # Scraping de portal público
    # -------------------------------
    def buscar_fallos_scraping(self, query: str) -> list[dict]:
        """Busca fallos judiciales en el portal de Neuquén por palabra clave."""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"No se pudo conectar con la página {self.base_url}: {e}")
            return [{"titulo": "Error de conexión", "link": None}]

        soup = BeautifulSoup(response.text, "html.parser")

        resultados = []
        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            href = urljoin(self.base_url, link["href"])

            if query.lower() in titulo.lower():
                resultados.append({"titulo": titulo, "link": href})

        # Elimina duplicados
        resultados_unicos = []
        vistos = set()
        for r in resultados:
            if r["titulo"] and r["titulo"] not in vistos:
                resultados_unicos.append(r)
                vistos.add(r["titulo"])

        if not resultados_unicos:
            logger.info(f"No se encontraron fallos relacionados con: {query}")
            return [{"titulo": "Sin resultados", "link": None}]

        return resultados_unicos

    # -------------------------------
    # Base local con embeddings
    # -------------------------------
    def agregar_fallo(self, titulo, texto, tema, tribunal, fecha):
        """Agrega un fallo con metadatos y lo indexa semánticamente."""
        embedding = self.model.encode([texto])[0]
        self.fallos.append({
            "titulo": titulo,
            "texto": texto,
            "tema": tema,
            "tribunal": tribunal,
            "fecha": fecha,
            "embedding": embedding
        })
        self._actualizar_index()

    def _actualizar_index(self):
        """Reconstruye el índice FAISS cada vez que se agregan fallos."""
        if self.fallos:
            embeddings = np.array([f["embedding"] for f in self.fallos])
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)

    def buscar_fallos_semanticos(self, consulta, top_k=5, tema=None):
        """Busca fallos relevantes por similitud semántica y opcionalmente por tema."""
        if not self.index:
            return []

        consulta_emb = self.model.encode([consulta])[0].reshape(1, -1)
        distancias, indices = self.index.search(consulta_emb, top_k)

        resultados = []
        for idx in indices[0]:
            fallo = self.fallos[idx]
            if tema and fallo["tema"] != tema:
                continue
            resultados.append({
                "titulo": fallo["titulo"],
                "tribunal": fallo["tribunal"],
                "fecha": fallo["fecha"],
                "tema": fallo["tema"],
                "texto": fallo["texto"][:300] + "..."
            })
        return resultados