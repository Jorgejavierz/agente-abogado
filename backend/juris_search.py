import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger

from backend.config import FAISS_SERVER, SAIJ_API_KEY

class SaijAPI:
    BASE_URL = "https://juridica.ar/api/v1/search"
    API_KEY = SAIJ_API_KEY

    def buscar(
        self,
        consulta: str,
        tipo: str = "legislacion",
        limit: int = 5
    ):
        headers = {
            "Authorization": f"Bearer {self.API_KEY}"
        }

        params = {
            "q": consulta,
            "tipo": tipo,
            "limit": limit
        }

        try:
            resp = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=10
            )

            resp.raise_for_status()

            return resp.json().get("results", [])

        except Exception as e:

            logger.error(
                f"Error al consultar SAIJ API: {e}"
            )

            return [{
                "titulo": "SAIJ no disponible",
                "contenido": "No se pudo conectar con la API de SAIJ.",
                "link": None,
                "tribunal": None,
                "fecha": None,
                "origen": "SAIJ API"
            }]

    def buscar_legislacion(
        self,
        consulta: str,
        limit: int = 5
    ):
        return self.buscar(
            consulta=consulta,
            tipo="legislacion",
            limit=limit
        )

class Jurisprudencia:
    """
    Módulo premium para búsqueda de fallos:
    - Scraping del portal oficial
    - Búsqueda semántica en FAISS externo
    - Consulta a la API de SAIJ
    Devuelve SIEMPRE una estructura uniforme.
    """

    BASE_URL = "http://juriscivil.jusneuquen.gov.ar/"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.BASE_URL
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.saij_api = SaijAPI()

    # ============================================================
    # SCRAPING OFICIAL
    # ============================================================
    def buscar_fallos_scraping(self, query: str, max_resultados=5) -> list[dict]:
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"No se pudo conectar con {self.base_url}: {e}")
            return [{
                "titulo": "Portal oficial no disponible",
                "contenido": "No se pudo acceder al portal de jurisprudencia.",
                "link": self.base_url,
                "tribunal": None,
                "fecha": None,
                "origen": "Portal oficial"
            }]

        soup = BeautifulSoup(response.text, "html.parser")
        resultados, vistos = [], set()

        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            href = urljoin(self.base_url, link["href"])

            if query.lower() not in titulo.lower() or titulo in vistos:
                continue

            contenido = ""
            try:
                fallo_resp = requests.get(href, headers=self.headers, timeout=10)
                fallo_resp.raise_for_status()
                fallo_soup = BeautifulSoup(fallo_resp.text, "html.parser")
                contenido = fallo_soup.get_text(" ", strip=True)
                if contenido and len(contenido) >= 200:
                    contenido = contenido[:600] + "..."
                else:
                    continue
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

        return resultados or [{
            "titulo": "Sin resultados en portal oficial",
            "contenido": "No se encontraron fallos para la consulta.",
            "link": self.base_url,
            "tribunal": None,
            "fecha": None,
            "origen": "Portal oficial"
        }]

    # ============================================================
    # FAISS EXTERNO
    # ============================================================
    def buscar_fallos_semanticos(self, consulta: str, top_k=5) -> list[dict]:
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
            return [{
                "titulo": "FAISS no disponible",
                "contenido": "No se pudo conectar con el servidor FAISS.",
                "link": None,
                "tribunal": None,
                "fecha": None,
                "origen": "FAISS externo"
            }]

        fallos = []
        for r in resultados:
            texto = r.get("texto", "Fallo sin título")
            respuesta = r.get("respuesta", "")
            if not respuesta:
                continue
            fallos.append({
                "titulo": texto,
                "contenido": respuesta[:600] + "...",
                "link": None,
                "tribunal": r.get("tribunal"),
                "fecha": r.get("fecha"),
                "origen": "FAISS externo"
            })

        return fallos or [{
            "titulo": "Sin resultados en FAISS",
            "contenido": "No se encontraron fallos relevantes en FAISS.",
            "link": None,
            "tribunal": None,
            "fecha": None,
            "origen": "FAISS externo"
        }]
    # ============================================================
    # SAIJ API
    # ============================================================
    def buscar_fallos_saij(
        self,
        consulta: str,
        limit=5
    ) -> list[dict]:

        resultados = self.saij_api.buscar(
            consulta,
            tipo="legislacion",
            limit=limit
        )

        fallos = []

        for r in resultados:

            fallos.append({
                "titulo": r.get("titulo", "Sin título"),
                "contenido": (
                    r.get("texto", "")[:600] + "..."
                    if r.get("texto")
                    else ""
                ),
                "link": r.get("link"),
                "tribunal": r.get("tribunal"),
                "fecha": r.get("fecha"),
                "origen": "SAIJ API"
            })

        return fallos or [{
            "titulo": "Sin resultados en SAIJ",
            "contenido": "No se encontraron normas relevantes en SAIJ.",
            "link": None,
            "tribunal": None,
            "fecha": None,
            "origen": "SAIJ API"
        }]

    # ============================================================
    # LEGISLACIÓN (SAIJ)
    # ============================================================
    def buscar_legislacion(
        self,
        consulta: str,
        limit=5
    ) -> list[dict]:

        resultados = self.saij_api.buscar_legislacion(
            consulta,
            limit=limit
        )

        normas = []

        for r in resultados:

            normas.append({
                "titulo": (
                    ", ".join(r.get("descriptores", []))
                    if r.get("descriptores")
                    else f"Norma {r.get('uuid', '')}"
                ),

                "contenido": (
                    f"Jurisdicción: {r.get('jurisdiccion', 'No informada')} | "
                    f"Fecha: {r.get('fecha', 'No informada')}"
                ),

                "link": r.get("url"),

                "origen": "SAIJ API"
            })

        return normas or [{
            "titulo": "Sin normativa",
            "contenido": "No se encontraron normas relevantes.",
            "link": None,
            "origen": "SAIJ API"
        }]
    
    # ============================================================
    # MÉTODO MAESTRO
    # ============================================================
    def buscar_fallos(
        self,
        consulta: str,
        top_k=5,
        incluir_scraping=True,
        incluir_saij=True
    ) -> list[dict]:

        resultados = []

        # 1. FAISS externo
        resultados.extend(
            self.buscar_fallos_semanticos(
                consulta,
                top_k
            )
        )

        # 2. Scraping oficial
        if incluir_scraping:

            resultados.extend(
                self.buscar_fallos_scraping(
                    consulta,
                    top_k
                )
            )

        # SAIJ ya NO forma parte de la jurisprudencia.
        # La normativa se consulta mediante:
        # self.buscar_legislacion()

        resultados.sort(
            key=lambda x: x.get("fecha") or "",
            reverse=True
        )

        return resultados or [{
            "titulo": "Sin resultados",
            "contenido": "No se encontraron fallos para la consulta.",
            "link": None,
            "tribunal": None,
            "fecha": None,
            "origen": "Agente Laboral IA"
        }]
    # ============================================================
# INSTANCIA GLOBAL
# ============================================================

_juris = Jurisprudencia()


# ============================================================
# CONSULTA DE JURISPRUDENCIA
# ============================================================

def buscar_jurisprudencia(
    consulta: str,
    k: int = 5,
    incluir_scraping: bool = True,
    incluir_saij: bool = True
):
    try:

        resultados = _juris.buscar_fallos(
            consulta,
            top_k=k,
            incluir_scraping=incluir_scraping,
            incluir_saij=incluir_saij
        )

        if not resultados:
            resultados = [{
                "titulo": "Sin resultados",
                "contenido": "No se encontraron fallos para la consulta.",
                "link": None,
                "tribunal": None,
                "fecha": None,
                "origen": "Agente Laboral IA"
            }]

        return {
            "consulta": consulta,
            "jurisprudencia_relevante": resultados,
            "detalle": "Consulta de jurisprudencia procesada correctamente.",
            "origen": "Agente Laboral IA"
        }

    except Exception as e:

        return {
            "consulta": consulta,
            "jurisprudencia_relevante": [{
                "titulo": "Error interno",
                "contenido": f"No se pudo procesar la consulta: {e}",
                "link": None,
                "tribunal": None,
                "fecha": None,
                "origen": "Agente Laboral IA"
            }],
            "detalle": f"Error en búsqueda de jurisprudencia: {e}",
            "origen": "Agente Laboral IA"
        }


# ============================================================
# CONSULTA DE LEGISLACIÓN
# ============================================================

def buscar_legislacion(
    consulta: str,
    limit: int = 5
):
    try:

        resultados = _juris.buscar_legislacion(
            consulta,
            limit=limit
        )

        return {
            "consulta": consulta,
            "normativa_relevante": resultados,
            "detalle": "Consulta normativa procesada correctamente.",
            "origen": "Agente Laboral IA"
        }

    except Exception as e:

        return {
            "consulta": consulta,
            "normativa_relevante": [{
                "titulo": "Error interno",
                "contenido": f"No se pudo procesar la consulta: {e}",
                "link": None,
                "origen": "Agente Laboral IA"
            }],
            "detalle": f"Error en búsqueda normativa: {e}",
            "origen": "Agente Laboral IA"
        }