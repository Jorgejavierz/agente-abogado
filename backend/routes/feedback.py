# routes/feedback.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import db  # Import corregido

router = APIRouter(tags=["Feedback"])


# ---------------------------
# Modelo de entrada
# ---------------------------
class FeedbackInput(BaseModel):
    consulta: str
    calificacion: int
    comentario: str | None = None


# ---------------------------
# Guardar feedback
# ---------------------------
@router.post("/feedback")
async def guardar_feedback(data: FeedbackInput):
    """
    Guarda feedback del usuario sobre la respuesta del agente.
    """

    if not (1 <= data.calificacion <= 5):
        raise HTTPException(
            status_code=400,
            detail="La calificación debe estar entre 1 y 5."
        )

    try:
        db.guardar_feedback(
            consulta=data.consulta,
            calificacion=data.calificacion,
            comentario=data.comentario or ""
        )

        return {
            "status": "ok",
            "mensaje": "Feedback guardado correctamente."
        }

    except Exception as e:
        print(f"Error guardando feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor."
        )


# ---------------------------
# Listar feedback
# ---------------------------
@router.get("/feedback")
async def listar_feedback(limit: int = 20):
    """
    Devuelve los últimos registros de feedback.
    """

    try:
        registros = db.listar_feedback(limit=limit)

        return {
            "status": "ok",
            "cantidad": len(registros),
            "feedback": registros
        }

    except Exception as e:
        print(f"Error en /feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor."
        )
