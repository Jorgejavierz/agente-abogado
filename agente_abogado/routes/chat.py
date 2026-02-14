# routes/chat.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from agente_abogado.db import MemoriaDB
from agente_abogado.formatter import ResponseFormatter

router = APIRouter(tags=["Chat"])
db = MemoriaDB()

class ChatInput(BaseModel):
    texto: str
    usuario: str | None = "anonimo"

@router.post("/chat")
async def chat(request: Request, entrada: ChatInput):
    agent = request.app.state.agent

    # Procesar la consulta con el agente
    resultado = agent.responder_pregunta(entrada.texto)

    # Guardar en memoria
    db.guardar_memoria(
        tipo="chat",
        texto=entrada.texto,
        resultado=resultado.get("resumen", resultado.get("resultado", "")),
        fallos_relacionados=resultado.get("fallos_relacionados", [])
    )

    # Formatear respuesta narrativa premium
    texto_formateado = ResponseFormatter.formatear(resultado)

    return {
        "usuario": entrada.usuario,
        "pregunta": entrada.texto,
        "resultado": resultado,
        "formateado": texto_formateado,
        "historial": db.listar_memoria(limit=5)  # últimas 5 interacciones
    }