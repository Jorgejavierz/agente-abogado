from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import LaborLawyerAgent
from jurisprudencia import Jurisprudencia

# Inicializar FastAPI
app = FastAPI(
    title="Agente Abogado Laboral",
    version="1.0.0",
    description="API para análisis de contratos y conflictos laborales en Argentina"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agente-laboral-frontend.vercel.app",  # dominio de tu frontend en producción
        "http://localhost:5173",                       # pruebas locales
        "*"                                            # abierto para pruebas generales
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agente y buscador
agent = LaborLawyerAgent()
buscador = Jurisprudencia()

# Modelos de entrada
class ContratoInput(BaseModel):
    texto: str

class ConflictoInput(BaseModel):
    descripcion: str

# Endpoint raíz
@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint de salud para verificar que el backend está vivo.
    """
    return {"mensaje": "Agente Abogado Laboral inicializado correctamente ✅"}

# Endpoint para analizar contrato
@app.post("/analizar-contrato", tags=["Contratos"])
async def analizar_contrato(data: ContratoInput):
    """
    Analiza un contrato laboral y devuelve un informe junto con fallos relacionados.
    """
    informe = agent.analizar_contrato(data.texto)
    fallos = buscador.buscar_fallos("contrato")
    return {
        "resultado": informe,
        "fallos_relacionados": fallos
    }

# Endpoint para analizar conflicto
@app.post("/analizar-conflicto", tags=["Conflictos"])
async def analizar_conflicto(data: ConflictoInput):
    """
    Analiza un conflicto laboral y devuelve un informe junto con fallos relacionados.
    """
    informe = agent.analizar_conflicto(data.descripcion)
    fallos = buscador.buscar_fallos("conflicto")
    return {
        "resultado": informe,
        "fallos_relacionados": fallos
    }