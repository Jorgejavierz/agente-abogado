import unicodedata
import requests
from agente_abogado.juris_search import Jurisprudencia

FAISS_SERVER = "http://127.0.0.1:8081"  # Servidor FAISS local

class LaborLawyerAgent:
    def __init__(self):
        self.buscador = Jurisprudencia()

    def normalizar(self, texto: str) -> str:
        """Normaliza texto: minúsculas y sin acentos."""
        texto = texto.lower()
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        return texto

    def guardar_en_faiss(self, texto: str, respuesta: str):
        """Guarda consulta y respuesta en FAISS."""
        payload = {"texto": texto, "respuesta": respuesta}
        try:
            requests.post(f"{FAISS_SERVER}/guardar", json=payload)
        except Exception as e:
            print(f"Error al guardar en FAISS: {e}")

    def buscar_en_faiss(self, texto: str, k: int = 3):
        """Busca antecedentes similares en FAISS."""
        try:
            resp = requests.get(f"{FAISS_SERVER}/buscar", params={"texto": texto, "k": k})
            return resp.json().get("resultados", [])
        except Exception as e:
            print(f"Error al buscar en FAISS: {e}")
            return []

    def explicar_concepto(self, texto: str) -> dict:
        """
        Explica conceptos jurídicos laborales con respaldo documental.
        Nunca inventa jurisprudencia ni artículos: si no hay fuente, lo indica.
        """
        # Buscar en FAISS primero
        antecedentes = self.buscar_en_faiss(texto)
        if antecedentes:
            return {
                "explicacion": f"FAISS devolvió {len(antecedentes)} antecedentes relevantes.",
                "fuente": "Base FAISS local"
            }

        # Buscar en jurisprudencia externa
        fallos = self.buscador.buscar_fallos(texto)
        if fallos:
            primer_fallo = fallos[0]
            fuente = f"{primer_fallo.get('tribunal', 'Tribunal desconocido')} - {primer_fallo.get('anio', 'Año no disponible')}"
            return {
                "explicacion": f"Se hallaron {len(fallos)} antecedentes jurisprudenciales.",
                "fuente": fuente
            }

        # Si no hay nada, no inventar
        return {
            "explicacion": "No se encontró explicación ni antecedentes documentales para este concepto.",
            "fuente": "Sin fuente disponible"
        }

    def responder_pregunta(self, texto: str) -> dict:
        """
        Responde cualquier consulta laboral con respaldo documental.
        Nunca inventa: si no hay datos, lo indica claramente.
        """
        # Clasificación básica
        if "contrato" in texto.lower():
            clasificacion = "Revisión de contrato"
        elif "conflicto" in texto.lower():
            clasificacion = "Conflicto laboral"
        else:
            clasificacion = "Consulta general"

        # Buscar jurisprudencia
        fallos_relacionados = self.buscador.buscar_fallos(texto)

        # Explicación doctrinal con fuente
        doctrina = self.explicar_concepto(texto)

        resultado = {
            "consulta": texto,
            "explicacion_doctrinal": doctrina["explicacion"],
            "jurisprudencia_relevante": (
                f"Se encontraron {len(fallos_relacionados)} antecedentes relevantes."
                if fallos_relacionados else
                "No se encontraron antecedentes relevantes."
            ),
            "fallos_relacionados": fallos_relacionados,
            "clasificacion": clasificacion,
            "conclusion": "Este informe es una aproximación automatizada. No reemplaza la revisión jurídica especializada.",
            "fuente": doctrina["fuente"]
        }

        # Guardar en FAISS para aprendizaje continuo
        self.guardar_en_faiss(texto, resultado["explicacion_doctrinal"])

        return resultado