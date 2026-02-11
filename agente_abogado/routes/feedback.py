# routes/feedback.py

from fastapi import APIRouter
from pydantic import BaseModel
from db import MemoriaDB

router = APIRouter(tags=["Feedback"])
db = MemoriaDB()

class FeedbackInput(BaseModel):
    texto: str
    util: bool
    timestamp: str

@router.post("/feedback")
async def guardar_feedback(feedback: FeedbackInput):
    """
    Guarda un feedback en la base de datos.
    """
    db.guardar_feedback(feedback.texto, feedback.util, feedback.timestamp)
    return {"mensaje": "Feedback guardado correctamente ✅"}

@router.get("/feedback")
async def listar_feedback():
    """
    Lista todos los feedbacks almacenados.
    """
    return {"feedback": db.listar_feedback()}