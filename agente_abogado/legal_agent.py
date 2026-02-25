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
        Explica conceptos jurídicos laborales con estilo profesional.
        Si no encuentra coincidencia interna, usa fallback con jurisprudencia o FAISS.
        """
        t = self.normalizar(texto)

        doctrinas = {
            "despido sin causa": {
                "explicacion": (
                    "El despido sin causa es la decisión unilateral del empleador de extinguir "
                    "la relación laboral sin invocar una razón justificada. Conforme al artículo 245 "
                    "de la Ley de Contrato de Trabajo, este tipo de despido obliga al empleador a "
                    "pagar una indemnización equivalente a un mes de sueldo por cada año de servicio "
                    "o fracción mayor a tres meses."
                ),
                "fuente": "Ley 20.744, art. 245"
            },
            "principio de irrenunciabilidad": {
                "explicacion": (
                    "El principio de irrenunciabilidad de derechos laborales establece que el trabajador "
                    "no puede renunciar válidamente a los derechos reconocidos por la ley, convenios colectivos "
                    "o contratos. Este principio, consagrado en el artículo 12 de la Ley de Contrato de Trabajo, "
                    "garantiza la tutela mínima indisponible y protege al trabajador frente a acuerdos que "
                    "pretendan disminuir sus derechos."
                ),
                "fuente": "Ley 20.744, art. 12"
            },
            "fraude laboral": {
                "explicacion": (
                    "El fraude laboral se configura cuando el empleador utiliza mecanismos aparentes o simulados "
                    "para encubrir una verdadera relación laboral, con el fin de evitar el cumplimiento de las "
                    "obligaciones legales. La jurisprudencia ha sido clara en sancionar estas prácticas, "
                    "reconociendo la primacía de la realidad sobre las formas."
                ),
                "fuente": "CNAT, Sala VII, 'Pérez c/ Empresa Y', 2020"
            }
        }

        # Buscar coincidencia interna
        for clave, valor in doctrinas.items():
            if clave in t:
                return valor

        # Fallback: búsqueda externa en jurisprudencia
        fallos = self.buscador.buscar_fallos(texto)
        if fallos:
            primer_fallo = fallos[0]
            fuente = f"{primer_fallo.get('tribunal', 'Tribunal desconocido')} - {primer_fallo.get('anio', 'Año no disponible')}"
            return {
                "explicacion": f"No se encontró definición interna, pero se hallaron {len(fallos)} antecedentes jurisprudenciales.",
                "fuente": f"Fuente: {fuente}"
            }

        # Fallback: búsqueda en FAISS
        antecedentes = self.buscar_en_faiss(texto)
        if antecedentes:
            return {
                "explicacion": f"No se encontró definición interna, pero FAISS devolvió {len(antecedentes)} antecedentes similares.",
                "fuente": "Base FAISS local"
            }

        return {
            "explicacion": "No se encontró una explicación doctrinal específica para este concepto.",
            "fuente": "Sin fuente disponible"
        }

    def responder_pregunta(self, texto: str) -> dict:
        """
        Responde cualquier consulta laboral con un informe narrativo estructurado.
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

        # Construcción del informe estructurado
        resultado = {
            "consulta": texto,
            "explicacion_doctrinal": doctrina["explicacion"],
            "normativa_aplicable": [
                "Ley de Contrato de Trabajo (Ley 20.744)",
                "Convenios colectivos aplicables",
                "Normas de seguridad laboral"
            ],
            "jurisprudencia_relevante": (
                f"Se encontraron {len(fallos_relacionados)} antecedentes relevantes."
                if fallos_relacionados else
                "No se encontraron antecedentes relevantes."
            ),
            "fallos_relacionados": fallos_relacionados,
            "clasificacion": clasificacion,
            "riesgos_legales": "El caso puede implicar riesgos legales según la normativa vigente.",
            "recomendaciones": "Consultar con un abogado laboral para validar hallazgos y definir un curso de acción confiable.",
            "conclusion": (
                "Este informe es una aproximación automatizada. No reemplaza la revisión jurídica especializada."
            ),
            "fuente": doctrina["fuente"]
        }

        # Guardar en FAISS para aprendizaje continuo
        self.guardar_en_faiss(texto, resultado["explicacion_doctrinal"])

        return resultado