# agent.py
from prompt import LABOR_LAWYER_PROMPT
from jurisprudencia import Jurisprudencia
from memoria import MemoriaAgente

class LaborLawyerAgent:
    def __init__(self):
        self.prompt = LABOR_LAWYER_PROMPT
        self.jurisprudencia = Jurisprudencia()
        self.memoria = MemoriaAgente()

    def review_contract(self, contract_text: str) -> str:
        informe = f"{self.prompt}\n\n---\nContrato recibido:\n{contract_text}"

        # Guardar en memoria
        self.memoria.guardar_caso(
            tipo="contrato",
            texto=contract_text,
            normativa="Ley 20.744, DNU 70/2023, Ley 24.901",
            jurisprudencia="N/A",
            resultado="Pendiente"
        )
        return informe

    def analizar_conflicto(self, caso: str) -> dict:
        fallos = self.jurisprudencia.buscar_fallos(caso)
        similares = self.memoria.buscar_similares(caso)

        resultado = {
            "caso": caso,
            "fallos_relacionados": fallos[:5],
            "casos_previos": similares,
            "normativa": ["Ley 20.744", "DNU 70/2023", "Ley 24.901"]
        }

        self.memoria.guardar_caso(
            tipo="conflicto",
            texto=caso,
            normativa="Ley 20.744, DNU 70/2023, Ley 24.901",
            jurisprudencia=str(fallos[:5]),
            resultado="Pendiente"
        )
        return resultado