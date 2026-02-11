# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION
from startup import startup_event

# Importar routers
from routes import health, analizar, feedback, memoria, jurisprudenciab

# Inicializar aplicación FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de startup
@app.on_event("startup")
async def on_startup():
    await startup_event(app)

# Registrar routers
app.include_router(health.router)
app.include_router(analizar.router)
app.include_router(feedback.router)
app.include_router(memoria.router)
app.include_router(jurisprudenciab.router)