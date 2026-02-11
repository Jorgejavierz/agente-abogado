# routes/memoria.py

from fastapi import APIRouter
from db import MemoriaDB

router = APIRouter(tags=["Memoria"])
db = MemoriaDB()

@router.get("/memoria")
async def listar_memoria(limit: int = 10):
    """
    Lista los últimos registros de memoria del agente.
    """
    return {"memoria": db.listar_memoria(limit)}