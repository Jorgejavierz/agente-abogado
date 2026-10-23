from backend.config import db, llm_client
from backend.legal_agent import LaborLawyerAgent


class Container:
    """
    Contenedor central de dependencias de la aplicación.
    """

    def __init__(self):
        self.db = db
        self.llm_client = llm_client

        self.agent = LaborLawyerAgent(
            db=self.db,
            llm_client=self.llm_client
        )


container = Container()