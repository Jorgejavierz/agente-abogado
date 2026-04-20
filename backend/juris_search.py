import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger

from backend.config import FAISS_SERVER


class Jurisprudencia:
    """
    Módulo premium para búsqueda de fallos:
    - Scraping del portal oficial
    - Búsqueda semántica en FAISS externo
    Devuelve SIEMPRE una estructura uniforme.
    """

    BASE_URL = "http://juriscivil.jusneuquen.gov.ar/"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.BASE_URL
        self.headers = {"User-Agent": "Mozilla/5.0"}

    # ============================================================
    # SCRAPING OFICIAL
    # ============================================================
    def buscar_fallos_scraping(self, query: str, max_resultados=5) -> list[dict]:
        """Busca fallos judiciales en el portal público por palabra clave."""

        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"No se pudo conectar con {self.base_url}: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        resultados = []
        vistos = set()

        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            href = urljoin(self.base_url, link["href"])

            if query.lower() not in titulo.lower():
                continue

            if titulo in vistos:
                continue

            # Intentar extraer contenido del fallo
            contenido = ""
            try:
                fallo_resp = requests.get(href, headers=self.headers, timeout=10)
                fallo_resp.raise_for_status()
                fallo_soup = BeautifulSoup(fallo_resp.text, "html.parser")
                contenido = fallo_soup.get_text(" ", strip=True)
                contenido = contenido[:600] + "..." if contenido else ""
            except Exception:
                contenido = "No se pudo extraer el contenido del fallo."

            resultados.append({
                "titulo": titulo,
                "contenido": contenido,
                "link": href,
                "tribunal": None,
                "fecha": None,
                "origen": "Portal oficial"
            })

            vistos.add(titulo)

            if len(resultados) >= max_resultados:
                break

        return resultados

    # ============================================================
    # FAISS EXTERNO
    # ============================================================
    def buscar_fallos_semanticos(self, consulta: str, top_k=5) -> list[dict]:
        """Busca fallos relevantes en FAISS externo."""
        try:
            resp = requests.get(
                f"{FAISS_SERVER}/buscar",
                params={"texto": consulta, "k": top_k},
                timeout=10
            )
            resp.raise_for_status()
            resultados = resp.json().get("resultados", [])
        except Exception as e:
            logger.error(f"Error al buscar en FAISS: {e}")
            return []

        fallos = []
        for r in resultados:
            fallos.append({
                "titulo": r.get("texto", "Fallo sin título"),
                "contenido": r.get("respuesta", "")[:600] + "...",
                "link": None,
                "tribunal": r.get("tribunal"),
                "fecha": r.get("fecha"),
                "origen": "FAISS externo"
            })

        return fallos

    # ============================================================
    # MÉTODO MAESTRO
    # ============================================================
    def buscar_fallos(self, consulta: str, top_k=5, incluir_scraping=True) -> list[dict]:
        """
        Combina:
        - Búsqueda semántica en FAISS externo
        - Scraping del portal oficial
        Devuelve una lista uniforme de fallos.
        """

        resultados = []

        # 1. FAISS externo
        semanticos = self.buscar_fallos_semanticos(consulta, top_k)
        resultados.extend(semanticos)

        # 2. Scraping oficial
        if incluir_scraping:
            scraping = self.buscar_fallos_scraping(consulta, top_k)
            resultados.extend(scraping)

        # 3. Ordenar por fecha si existe
        resultados.sort(key=lambda x: x.get("fecha") or "", reverse=True)

        return resultados or []
