from fastapi import APIRouter
from pydantic import BaseModel
from agente_abogado.calculadora_intereses import CalculadoraIntereses

router = APIRouter()
calculadora = CalculadoraIntereses()

# Modelo de datos para recibir el body JSON
class InteresRequest(BaseModel):
    capital: float
    fecha_inicio: str
    fecha_fin: str

@router.post("/calcular-intereses")
def calcular_intereses(req: InteresRequest):
    try:
        resultado = calculadora.calcular(
            req.capital,
            req.fecha_inicio,
            req.fecha_fin
        )
        return resultado
    except Exception as e:
        return {"error": str(e)}