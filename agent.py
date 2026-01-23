# agent.py
from prompt import LABOR_LAWYER_PROMPT
from jurisprudencia import Jurisprudencia
from memoria import MemoriaAgente
from config import NORMATIVA_BASE  # importamos normativa desde config.py

class LaborLawyerAgent:
    def __init__(self):
        self.prompt = LABOR_LAWYER_PROMPT
        self.jurisprudencia = Jurisprudencia()
        self.memoria = MemoriaAgente()

    def review_contract(self, contract_text: str) -> dict:
        informe = f"{self.prompt}\n\n---\nContrato recibido:\n{contract_text}"

        # Guardar en memoria
        try:
            self.memoria.guardar_caso(
                tipo="contrato",
                texto=contract_text,
                normativa=", ".join(NORMATIVA_BASE),
                jurisprudencia="N/A",
                resultado="Pendiente"
            )
        except Exception as e:
            print(f"Error guardando contrato en memoria: {e}")

        return {
            "informe": informe,
            "normativa": NORMATIVA_BASE
        }

    def analizar_conflicto(self, caso: str) -> dict:
        try:
            fallos = self.jurisprudencia.buscar_fallos(caso)
        except Exception as e:
            print(f"Error buscando fallos: {e}")
            fallos = []

        try:
            similares = self.memoria.buscar_similares(caso)
        except Exception as e:
            print(f"Error buscando casos similares: {e}")
            similares = []

        resultado = {
            "caso": caso,
            "fallos_relacionados": fallos[:5],
            "casos_previos": similares,
            "normativa": NORMATIVA_BASE
        }

        try:
            self.memoria.guardar_caso(
                tipo="conflicto",
                texto=caso,
                normativa=", ".join(NORMATIVA_BASE),
                jurisprudencia=str(fallos[:5]),
                resultado="Pendiente"
            )
        except Exception as e:
            print(f"Error guardando conflicto en memoria: {e}")

        return resultado