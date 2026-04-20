# routes/casos.py

from fastapi import APIRouter, HTTPException
from backend.config import db  # Import corregido

router = APIRouter(tags=["Casos"])


# ---------------------------
# Listar casos guardados
# ---------------------------
@router.get("/casos")
async def listar_casos(limit: int = 10):
    """
    Devuelve los últimos casos guardados por el agente.
    """
    try:
        casos = db.listar_casos(limit=limit)
        return {"status": "ok", "casos": casos}

    except Exception as e:
        print(f"Error en /casos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


# ---------------------------
# Obtener un caso por ID
# ---------------------------
@router.get("/casos/{caso_id}")
async def obtener_caso(caso_id: int):
    """
    Devuelve un caso específico por ID.
    """
    try:
        caso = db.obtener_caso(caso_id)

        if not caso:
            raise HTTPException(status_code=404, detail="Caso no encontrado.")

        return {"status": "ok", "caso": caso}

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error en /casos/{caso_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


# ---------------------------
# Eliminar un caso por ID
# ---------------------------
@router.delete("/casos/{caso_id}")
async def eliminar_caso(caso_id: int):
    """
    Elimina un caso guardado por ID.
    """
    try:
        eliminado = db.eliminar_caso(caso_id)

        if not eliminado:
            raise HTTPException(status_code=404, detail="Caso no encontrado.")

        return {"status": "ok", "mensaje": "Caso eliminado correctamente."}

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error eliminando caso {caso_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
