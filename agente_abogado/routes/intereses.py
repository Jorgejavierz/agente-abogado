from fastapi import APIRouter
from agente_abogado.calculadora_intereses import CalculadoraIntereses

router = APIRouter()
calculadora = CalculadoraIntereses()

@router.post("/calcular-intereses")
def calcular_intereses(capital: float, fecha_inicio: str, fecha_fin: str):
    try:
        resultado = calculadora.calcular(capital, fecha_inicio, fecha_fin)
        return resultado
    except Exception as e:
        return {"error": str(e)}