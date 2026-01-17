# jurisprudencia.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger

class Jurisprudencia:
    """
    Clase para buscar fallos judiciales en bases públicas mediante scraping.
    Actualmente apunta al portal de jurisprudencia de Neuquén.
    """

    BASE_URL = "http://juriscivil.jusneuquen.gov.ar/"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.BASE_URL
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def buscar_fallos(self, query: str) -> list:
        """
        Busca fallos judiciales relacionados con la query.
        Retorna una lista de diccionarios con 'titulo' y 'link'.
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"No se pudo conectar con la página {self.base_url}: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        resultados = []
        # ⚠️ Ajustar selector según la estructura real del sitio
        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            href = urljoin(self.base_url, link["href"])

            if query.lower() in titulo.lower():
                resultados.append({
                    "titulo": titulo,
                    "link": href
                })

        # Elimina duplicados y entradas vacías
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