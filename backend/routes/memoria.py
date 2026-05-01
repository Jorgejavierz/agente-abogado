# routes/memoria.py

from fastapi import APIRouter, HTTPException
from backend.config import db  # Import corregido

router = APIRouter(tags=["Memoria"])


# ---------------------------
# Listar memoria
# ---------------------------
@router.get("/memoria")
async def listar_memoria(limit: int = 20):
    """
    Devuelve los últimos registros de memoria del agente.
    """
    try:
        memoria = db.listar_memoria(limit=limit)
        return {"status": "ok", "memoria": memoria}

    except Exception as e:
        print(f"Error en /memoria: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


# ---------------------------
# Eliminar memoria
# ---------------------------
@router.delete("/memoria/{memoria_id}")
async def eliminar_memoria(memoria_id: int):
    """
    Elimina un registro de memoria por ID.
    """

    try:
        # ⚠️ ESTE MÉTODO NO EXISTE EN MemoriaDB
        eliminado = db.eliminar_memoria(memoria_id)

        if not eliminado:
            raise HTTPException(status_code=404, detail="Registro no encontrado.")

        return {"status": "ok", "mensaje": "Registro eliminado correctamente."}

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error eliminando memoria {memoria_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
