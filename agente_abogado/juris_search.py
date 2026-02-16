# juris_search.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger

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

        # Embeddings y FAISS (carga diferida)
        self._model = None
        self.fallos = []
        self.index = None

    # -------------------------------
    # Carga diferida del modelo
    # -------------------------------
    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            # Modelo más liviano para ahorrar memoria
            self._model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        return self._model

    # -------------------------------
    # Scraping mejorado
    # -------------------------------
    def buscar_fallos_scraping(self, query: str, max_resultados=10) -> list[dict]:
        """Busca fallos judiciales en el portal público por palabra clave."""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"No se pudo conectar con la página {self.base_url}: {e}")
            return [{"titulo": "Error de conexión", "link": None, "contenido": None}]

        soup = BeautifulSoup(response.text, "html.parser")

        resultados = []
        vistos = set()

        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            href = urljoin(self.base_url, link["href"])

            if query.lower() in titulo.lower() and titulo not in vistos:
                try:
                    fallo_resp = requests.get(href, headers=self.headers, timeout=10)
                    fallo_resp.raise_for_status()
                    fallo_soup = BeautifulSoup(fallo_resp.text, "html.parser")
                    contenido = fallo_soup.get_text(" ", strip=True)[:500] + "..."
                except Exception:
                    contenido = "No se pudo extraer el contenido completo."

                resultados.append({
                    "titulo": titulo,
                    "link": href,
                    "contenido": contenido,
                    "explicacion": (
                        f"Este fallo encontrado en el portal oficial se relaciona con la consulta '{query}'. "
                        f"Fuente: {href}"
                    )
                })
                vistos.add(titulo)

            if len(resultados) >= max_resultados:
                break

        if not resultados:
            logger.info(f"No se encontraron fallos relacionados con: {query}")
            return [{"titulo": "Sin resultados", "link": None, "contenido": None}]

        return resultados

    # -------------------------------
    # Base local con embeddings
    # -------------------------------
    def agregar_fallo(self, titulo, texto, tema, tribunal, fecha, link=None):
        """Agrega un fallo con metadatos y lo indexa semánticamente."""
        enriched_text = f"Tema: {tema} | Tribunal: {tribunal} | Fecha: {fecha} | Texto: {texto}"
        model = self._get_model()
        embedding = model.encode([enriched_text])[0]
        self.fallos.append({
            "titulo": titulo,
            "texto": texto,
            "tema": tema,
            "tribunal": tribunal,
            "fecha": fecha,
            "link": link,
            "embedding": embedding
        })
        self._actualizar_index()

    def _actualizar_index(self):
        """Reconstruye el índice FAISS cada vez que se agregan fallos."""
        if self.fallos:
            embeddings = np.array([f["embedding"] for f in self.fallos])
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)

    def listar_fallos(self):
        """Devuelve todos los fallos almacenados."""
        return self.fallos

    def eliminar_fallo(self, titulo: str):
        """Elimina un fallo por título."""
        for i, fallo in enumerate(self.fallos):
            if fallo["titulo"] == titulo:
                self.fallos.pop(i)
                self._actualizar_index()
                return
        raise ValueError(f"No se encontró un fallo con título: {titulo}")

    def buscar_fallos_semanticos(self, consulta, top_k=5, tema=None, ordenar_por_fecha=True):
        """Busca fallos relevantes por similitud semántica y opcionalmente por tema."""
        if not self.index:
            return [{"mensaje": "No hay fallos indexados en la base local."}]

        model = self._get_model()
        consulta_texto = f"Consulta: {consulta} | Tema: {tema if tema else 'general'}"
        consulta_emb = model.encode([consulta_texto])[0].reshape(1, -1)

        distancias, indices = self.index.search(consulta_emb, top_k)

        resultados = []
        for idx, distancia in zip(indices[0], distancias[0]):
            fallo = self.fallos[idx]
            if tema and fallo["tema"].lower() != tema.lower():
                continue
            resultados.append({
                "titulo": fallo["titulo"],
                "tribunal": fallo["tribunal"],
                "fecha": fallo["fecha"],
                "tema": fallo["tema"],
                "fragmento": fallo["texto"][:300] + "...",
                "relevancia": round(float(1 / (1 + distancia)), 3),
                "fuente": fallo.get("link", "Fuente local"),
                "explicacion": (
                    f"Este fallo del {fallo['tribunal']} ({fallo['fecha']}) "
                    f"se relaciona con el tema '{fallo['tema']}' y presenta "
                    f"similitudes semánticas con la consulta realizada."
                )
            })

        if ordenar_por_fecha:
            resultados.sort(key=lambda x: x.get("fecha", ""), reverse=True)

        if not resultados:
            return [{"mensaje": f"No se encontraron fallos relevantes para: {consulta}"}]

        return resultados

    # -------------------------------
    # Método maestro
    # -------------------------------
    def buscar_fallos(self, consulta, top_k=5, tema=None, incluir_scraping=True):
        """
        Método maestro que combina:
        - Scraping de portal oficial
        - Búsqueda semántica en base local
        Devuelve resultados narrativos, transparentes y ordenados.
        """
        resultados = []

        # 1. Búsqueda semántica local
        semanticos = self.buscar_fallos_semanticos(
            consulta=consulta,
            top_k=top_k,
            tema=tema,
            ordenar_por_fecha=True
        )
        for r in semanticos:
            r["origen"] = "Base local (FAISS)"
            resultados.append(r)

        # 2. Scraping oficial
        if incluir_scraping:
            scraping = self.buscar_fallos_scraping(query=consulta, max_resultados=top_k)
            for r in scraping:
                r["origen"] = "Portal oficial"
                resultados.append(r)

        # 3. Ordenar resultados por relevancia y fecha
        resultados.sort(
            key=lambda x: (
                x.get("relevancia", 0),
                x.get("fecha", "")
            ),
            reverse=True
        )

        if not resultados:
            return [{"mensaje": f"No se encontraron fallos relevantes para la consulta: {consulta}"}]

        return resultados