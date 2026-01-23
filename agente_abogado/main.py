# agente_abogado/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import LaborLawyerAgent
from jurisprudencia import Jurisprudencia
from config import ALLOWED_ORIGINS
from validator import validar_contrato, validar_conflicto

# Inicializar FastAPI
app = FastAPI(
    title="Agente Abogado Laboral",
    version="1.0.0",
    description="API para análisis de contratos y conflictos laborales en Argentina"
)

# Configurar CORS usando ALLOWED_ORIGINS desde config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar dependencias en startup
@app.on_event("startup")
async def startup_event():
    try:
        app.state.agent = LaborLawyerAgent()
        app.state.buscador = Jurisprudencia()
    except Exception as e:
        print(f"Error inicializando dependencias: {e}")

# Endpoint raíz
@app.get("/", tags=["Health"])
async def root():
    return {"mensaje": "Agente Abogado Laboral inicializado correctamente ✅"}

# Endpoint health check
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

# Endpoint para analizar contrato
@app.post("/analizar-contrato", tags=["Contratos"])
async def analizar_contrato(data: dict):
    contrato = validar_contrato(data)
    if not contrato:
        return {"error": "Contrato inválido"}
    informe = app.state.agent.review_contract(contrato.texto)
    fallos = app.state.buscador.buscar_fallos("contrato")
    return {"resultado": informe, "fallos_relacionados": fallos}

# Endpoint para analizar conflicto
@app.post("/analizar-conflicto", tags=["Conflictos"])
async def analizar_conflicto(data: dict):
    conflicto = validar_conflicto(data)
    if not conflicto:
        return {"error": "Conflicto inválido"}
    informe = app.state.agent.analizar_conflicto(conflicto.descripcion)
    fallos = app.state.buscador.buscar_fallos("conflicto")
    return {"resultado": informe, "fallos_relacionados": fallos}