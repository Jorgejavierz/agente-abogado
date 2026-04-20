# routes/intereses.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.calculadora_intereses import calcular_intereses  # Import corregido

router = APIRouter(tags=["Intereses"])


# ---------------------------
# Modelo de entrada
# ---------------------------
class InteresesInput(BaseModel):
    capital: float
    fecha_inicio: str
    fecha_fin: str
    tasa: float | None = None  # opcional: si no viene, usar tasa por defecto


# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/intereses")
async def calcular_intereses_endpoint(data: InteresesInput):
    """
    Calcula intereses entre dos fechas.
    Usa la función oficial del backend: calcular_intereses().
    """

    try:
        resultado = calcular_intereses(
            capital=data.capital,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            tasa=data.tasa,
        )

        return {
            "status": "ok",
            "capital": data.capital,
            "fecha_inicio": data.fecha_inicio,
            "fecha_fin": data.fecha_fin,
            "tasa": data.tasa,
            "intereses": resultado.get("intereses", 0),
            "total": resultado.get("total", 0),
            "detalle": resultado,
        }

    except Exception as e:
        print(f"Error en /intereses: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
