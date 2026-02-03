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
        informe = {
            "resultado": f"{self.prompt}\n\n---\nContrato recibido:\n{contract_text}",
            "normativa": NORMATIVA_BASE,
            "fallos_relacionados": []
        }

        # Guardar en memoria (solo strings y listas serializadas)
        try:
            self.memoria.guardar_caso(
                tipo="contrato",
                texto=contract_text,
                resultado=informe["resultado"],   # string limpio
                fallos_relacionados=informe["fallos_relacionados"]  # lista vacía
            )
        except Exception as e:
            print(f"Error guardando contrato en memoria: {e}")

        return informe

    def analizar_conflicto(self, caso: str) -> dict:
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
            "resultado": f"Conflicto analizado: {caso}",
            "fallos_relacionados": fallos[:5],
            "similares": similares,
            "normativa": NORMATIVA_BASE
        }

        # Guardar en memoria (solo strings y listas serializadas)
        try:
            self.memoria.guardar_caso(
                tipo="conflicto",
                texto=caso,
                resultado=resultado["resultado"],   # string limpio
                fallos_relacionados=fallos[:5]      # lista serializada en memoria.py
            )
        except Exception as e:
            print(f"Error guardando conflicto en memoria: {e}")

        return resultado