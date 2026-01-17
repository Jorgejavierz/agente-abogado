# api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import LaborLawyerAgent

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Agente Laboral API",
    version="1.0.0",
    description="API para análisis de contratos y conflictos laborales en Argentina"
)

# Instanciar agente laboral
agent = LaborLawyerAgent()

# Modelos de entrada
class ContratoRequest(BaseModel):
    texto: str

class ConflictoRequest(BaseModel):
    descripcion: str

# Rutas
@app.get("/status")
def status():
    """Verifica que la API esté funcionando."""
    return {"status": "ok", "agent": "laboral", "version": "1.0.0"}

@app.post("/analizar-contrato")
def analizar_contrato(req: ContratoRequest):
    """Analiza un contrato laboral y devuelve informe."""
    informe = agent.review_contract(req.texto)
    return {"informe": informe}

@app.post("/analizar-conflicto")
def analizar_conflicto(req: ConflictoRequest):
    """Analiza un conflicto laboral y devuelve resultado con normativa y jurisprudencia."""
    resultado = agent.analizar_conflicto(req.descripcion)
    return {"resultado": resultado}