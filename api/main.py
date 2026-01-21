# api/main.py
"""
Este archivo ya no inicializa FastAPI.
Se mantiene como módulo auxiliar para lógica de negocio.
"""

from agent import LaborLawyerAgent

# Instanciar agente laboral
agent = LaborLawyerAgent()

def analizar_contrato(texto: str):
    """Analiza un contrato laboral y devuelve informe."""
    return agent.review_contract(texto)

def analizar_conflicto(descripcion: str):
    """Analiza un conflicto laboral y devuelve resultado con normativa y jurisprudencia."""
    return agent.analizar_conflicto(descripcion)