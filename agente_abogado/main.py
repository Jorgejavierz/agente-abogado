from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agente_abogado.config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION
from agente_abogado.legal_agent import LaborLawyerAgent  # importar el agente

# Importar routers desde la carpeta routes
from agente_abogado.routes import (
    health,
    analizar,
    feedback,
    memoria,
    chat,
    intereses   # 👈 nuevo router para la calculadora de intereses
)

# Inicializar aplicación FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # dominios permitidos (ej. Vercel, localhost)
    allow_credentials=True,
    allow_methods=["*"],             # permitir todos los métodos
    allow_headers=["*"],             # permitir todos los headers
)

# Inicializar el agente y guardarlo en el estado de la app
app.state.agent = LaborLawyerAgent()

# Registrar routers
app.include_router(health.router)
app.include_router(analizar.router)
app.include_router(feedback.router)
app.include_router(memoria.router)
app.include_router(chat.router)
app.include_router(intereses.router)  # 👈 integración del nuevo endpoint