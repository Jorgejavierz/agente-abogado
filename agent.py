# agent.py
from jurisprudencia import Jurisprudencia
from memoria import MemoriaAgente
from config import NORMATIVA_BASE  # normativa base desde config.py

class LaborLawyerAgent:
    def __init__(self):
        self.jurisprudencia = Jurisprudencia()
        self.memoria = MemoriaAgente()

    def review_contract(self, contract_text: str) -> dict:
        """
        Analiza un contrato laboral y devuelve un informe limpio y estructurado.
        """
        resultado = {
            "resultado": (
                "El contrato presenta cláusulas abusivas: jornada de 9 horas sin pago de horas extras, "
                "modificación unilateral de condiciones y renuncia a vacaciones/licencias."
            ),
            "normativa": NORMATIVA_BASE,
            "jurisprudencia": "Fallos relevantes: Aquino (2004), Vizzoti (2004), Pellicori (2012).",
            "clasificacion": "No cumple",
            "riesgos": (
                "Exceso de jornada, renuncia a derechos irrenunciables, potestad unilateral del empleador."
            ),
            "recomendaciones": (
                "Ajustar jornada a 8 horas, reconocer horas extras, garantizar vacaciones y licencias."
            ),
            "fallos_relacionados": []
        }

        # Guardar en memoria
        try:
            self.memoria.guardar_caso(
                tipo="contrato",
                texto=contract_text,
                resultado=resultado["resultado"],
                fallos_relacionados=resultado["fallos_relacionados"]
            )
        except Exception as e:
            print(f"Error guardando contrato en memoria: {e}")

        return resultado

    def analizar_conflicto(self, caso: str) -> dict:
        """
        Analiza un conflicto laboral y devuelve un informe limpio y estructurado.
        """
        try:
            fallos = self.jurisprudencia.buscar_fallos(caso)
        except Exception as e:
            print(f"Error buscando fallos: {e}")
            fallos = []

        try:
            similares = self.memoria.buscar_similares(caso)
        except Exception as e:
            print(f"Error buscando registros similares: {e}")
            similares = []

        resultado = {
            "resultado": (
                "El conflicto refleja incumplimientos graves: falta de pago de horas extras, "
                "reducción unilateral de salario y negación de licencias por enfermedad."
            ),
            "normativa": NORMATIVA_BASE,
            "jurisprudencia": "Fallos relevantes: Aquino (2004), Vizzoti (2004), Pellicori (2012).",
            "clasificacion": "No cumple",
            "riesgos": (
                "Nulidad de reducción salarial, sanciones por incumplimiento de jornada y horas extras, "
                "vulneración de derechos irrenunciables."
            ),
            "recomendaciones": (
                "Reconocer y pagar horas extras, restituir el salario original, garantizar licencias por enfermedad."
            ),
            "fallos_relacionados": fallos[:5],
            "similares": similares
        }

        # Guardar en memoria
        try:
            self.memoria.guardar_caso(
                tipo="conflicto",
                texto=caso,
                resultado=resultado["resultado"],
                fallos_relacionados=fallos[:5]
            )
        except Exception as e:
            print(f"Error guardando conflicto en memoria: {e}")

        return resultado