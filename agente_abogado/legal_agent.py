# legal_agent.py

from agente_abogado.juris_search import Jurisprudencia

class LaborLawyerAgent:
    def __init__(self):
        self.buscador = Jurisprudencia()

    def responder_pregunta(self, texto: str) -> dict:
        """
        Responde cualquier consulta laboral con un informe narrativo completo.
        """
        # Clasificación básica del tipo de consulta
        if "contrato" in texto.lower():
            clasificacion = "Revisión de contrato"
        elif "conflicto" in texto.lower():
            clasificacion = "Conflicto laboral"
        else:
            clasificacion = "Consulta general"

        # Buscar jurisprudencia relacionada
        fallos_relacionados = self.buscador.buscar_fallos(texto)

        # Construir respuesta narrativa
        resultado = {
            "resumen": f"Consulta recibida: {texto}",
            "normativa": [
                "Ley de Contrato de Trabajo (Ley 20.744)",
                "Convenios colectivos aplicables",
                "Normas de seguridad laboral"
            ],
            "jurisprudencia": (
                "Se encontraron antecedentes relevantes en la base de jurisprudencia."
                if fallos_relacionados else
                "No se encontraron antecedentes relevantes."
            ),
            "fallos_relacionados": fallos_relacionados,
            "clasificacion": clasificacion,
            "riesgos": "El caso puede implicar riesgos legales según la normativa vigente.",
            "recomendaciones": (
                "Consultar con un abogado laboral para validar hallazgos y definir un curso de acción confiable."
            ),
            "conclusion": (
                "Este informe es una aproximación automatizada. No reemplaza la revisión jurídica especializada."
            )
        }

        return resultado