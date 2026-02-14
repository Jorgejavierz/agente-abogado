# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agente_abogado.config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION

# Importar routers desde la carpeta routes
from agente_abogado.routes import (
    health,
    analizar,
    feedback,
    memoria,
    jurisprudenciab,
    chat
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

# Registrar routers
app.include_router(health.router)
app.include_router(analizar.router)
app.include_router(feedback.router)
app.include_router(memoria.router)
app.include_router(jurisprudenciab.router)
app.include_router(chat.router)