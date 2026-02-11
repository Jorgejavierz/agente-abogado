# startup.py

from legal_agent import LaborLawyerAgent
from juris_search import Jurisprudencia
from db import MemoriaDB

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