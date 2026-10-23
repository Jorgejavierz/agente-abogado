# startup.py

from agente_abogado.legal_agent import LaborLawyerAgent
from agente_abogado.juris_search import Jurisprudencia
from agente_abogado.db import MemoriaDB

async def startup_event(app):
    """
    Inicializa dependencias al arrancar la aplicación.
    """
    # Inicializar agente laboral
    app.state.agent = LaborLawyerAgent()

    # Inicializar buscador de jurisprudencia
    app.state.buscador = Jurisprudencia()

    # Inicializar base de datos
    app.state.db = MemoriaDB()