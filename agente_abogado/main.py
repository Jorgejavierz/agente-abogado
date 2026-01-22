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

# Configurar CORS (para permitir llamadas desde tu frontend en Vercel y pruebas locales)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agente-laboral-frontend.vercel.app",  # dominio de tu frontend en producción
        "http://localhost:5173",                       # para pruebas locales
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

# Endpoint raíz para verificar que el backend está vivo
@app.get("/")
def root():
    return {"mensaje": "Agente Abogado Laboral inicializado correctamente ✅"}

# Endpoint para analizar contrato
@app.post("/analizar-contrato")
def analizar_contrato(data: ContratoInput):
    informe = agent.analizar_contrato(data.texto)
    fallos = buscador.buscar_fallos("contrato")
    return {
        "resultado": informe,
        "fallos_relacionados": fallos
    }

# Endpoint para analizar conflicto
@app.post("/analizar-conflicto")
def analizar_conflicto(data: ConflictoInput):
    informe = agent.analizar_conflicto(data.descripcion)
    fallos = buscador.buscar_fallos("conflicto")
    return {
        "resultado": informe,
        "fallos_relacionados": fallos
    }