# routes/analizar.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from formatter import ResponseFormatter

router = APIRouter(tags=["Analizar"])

class AnalizarInput(BaseModel):
    texto: str
    tipo: str  # "contrato", "conflicto" o "consulta"

@router.post("/analizar")
async def analizar_documento(request: Request, entrada: AnalizarInput):
    """
    Endpoint para analizar contratos, conflictos o consultas laborales.
    """
    agent = request.app.state.agent

    if entrada.tipo.lower() == "contrato":
        resultado = agent.review_contract(entrada.texto)
    elif entrada.tipo.lower() == "conflicto":
        resultado = agent.analizar_conflicto(entrada.texto)
    elif entrada.tipo.lower() == "consulta":
        resultado = agent.responder_pregunta(entrada.texto)
    else:
        return {"error": f"Tipo de análisis no reconocido: {entrada.tipo}"}

    # Formatear respuesta narrativa
    texto_formateado = ResponseFormatter.formatear(resultado)

    return {
        "resultado": resultado,
        "formateado": texto_formateado
    }