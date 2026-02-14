# routes/analizar.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from agente_abogado.formatter import ResponseFormatter

router = APIRouter(tags=["Analizar"])

class AnalizarInput(BaseModel):
    texto: str | None = None
    text: str | None = None
    tipo: str  # "contrato", "conflicto" o "consulta"

    @property
    def contenido(self) -> str:
        return self.texto or self.text or ""

@router.post("/analizar")
async def analizar_documento(request: Request, entrada: AnalizarInput):
    """
    Endpoint para analizar contratos, conflictos o consultas laborales.
    """
    agent = request.app.state.agent
    contenido = entrada.contenido.strip()

    if not contenido:
        return {"error": "No se recibió texto para analizar."}

    tipo = entrada.tipo.lower()
    if tipo == "contrato":
        resultado = agent.review_contract(contenido)
    elif tipo == "conflicto":
        resultado = agent.analizar_conflicto(contenido)
    elif tipo == "consulta":
        resultado = agent.responder_pregunta(contenido)
    else:
        return {"error": f"Tipo de análisis no reconocido: {entrada.tipo}"}

    # Formatear respuesta narrativa premium
    texto_formateado = ResponseFormatter.formatear(resultado)

    return {
        "resultado": resultado,
        "formateado": texto_formateado
    }