# routes/consultar_documento.py

from fastapi import APIRouter, Query
from backend.legal_agent import LaborLawyerAgent
from backend.config import db, llm_client

router = APIRouter()

# Inicializamos el agente
agent = LaborLawyerAgent(db=db, llm_client=llm_client)


@router.get("/consultar_documento")
def consultar_documento(
    pregunta: str = Query(..., description="Consulta laboral a analizar"),
    k: int = Query(3, description="Cantidad de antecedentes a recuperar")
):
    """
    Endpoint premium para consultas laborales.
    Devuelve un informe narrativo enriquecido con estilo conversacional,
    jurisprudencia relevante y recomendaciones prácticas.
    """

    try:
        historial = []

        # El método correcto es responder()
        resultado = agent.responder(pregunta)

        return {
            "informe": resultado.get("informe"),
            "consulta": resultado.get("consulta"),
            "explicacion_doctrinal": resultado.get("explicacion_doctrinal"),
            "jurisprudencia_relevante": resultado.get("fallos_relacionados"),
            "fallos_relacionados": resultado.get("fallos_relacionados"),
            "clasificacion": resultado.get("clasificacion"),
            "conclusion": resultado.get("conclusion"),
            "fuente": resultado.get("fuente", None),
            "origen": "Agente Laboral IA"
        }

    except Exception as e:
        return {
            "mensaje": "Error procesando la consulta",
            "detalle": str(e),
            "origen": "Agente Laboral IA"
        }
