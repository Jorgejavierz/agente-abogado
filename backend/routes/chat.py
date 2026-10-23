# routes/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.container import container

router = APIRouter()


# ---------------------------
# Modelos de entrada
# ---------------------------
class ChatRequest(BaseModel):
    mensaje: str

# ---------------------------
# Endpoint principal del chat
# ---------------------------
@router.post("/chat")
async def chat_endpoint(data: ChatRequest):
    """
    Endpoint principal del agente conversacional jurídico.
    Recibe un mensaje del usuario y devuelve un análisis legal estructurado.
    """

    texto = data.mensaje.strip()

    if not texto:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    try:
        respuesta = container.agent.responder(texto)
        return {
            "status": "ok",
            "respuesta": respuesta
        }

    except Exception as e:
        print(f"Error en /chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

