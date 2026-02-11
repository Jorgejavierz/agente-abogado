# routes/jurisprudenciab.py

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["Jurisprudencia"])

class FalloInput(BaseModel):
    titulo: str
    texto: str
    tema: str
    tribunal: str
    fecha: str
    link: str | None = None

@router.post("/agregar_fallo")
async def agregar_fallo(request: Request, fallo: FalloInput):
    """
    Agrega un fallo a la base de jurisprudencia.
    """
    buscador = request.app.state.buscador
    buscador.agregar_fallo(
        titulo=fallo.titulo,
        texto=fallo.texto,
        tema=fallo.tema,
        tribunal=fallo.tribunal,
        fecha=fallo.fecha,
        link=fallo.link
    )
    return {"mensaje": f"Fallo '{fallo.titulo}' agregado correctamente ✅"}

@router.get("/listar_fallos")
async def listar_fallos(request: Request):
    """
    Lista todos los fallos almacenados.
    """
    buscador = request.app.state.buscador
    return {"fallos": buscador.listar_fallos()}

@router.delete("/eliminar_fallo/{titulo}")
async def eliminar_fallo(request: Request, titulo: str):
    """
    Elimina un fallo por título.
    """
    buscador = request.app.state.buscador
    try:
        buscador.eliminar_fallo(titulo)
        return {"mensaje": f"Fallo '{titulo}' eliminado correctamente ✅"}
    except ValueError as e:
        return {"error": str(e)}