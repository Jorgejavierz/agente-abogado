# config.py

# Lista de orígenes permitidos para CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",   # Frontend local
    "http://127.0.0.1:3000",   # Alternativa local
    "https://tu-dominio.com",  # Producción (ajusta según tu despliegue)
]

# Configuración general de la aplicación
APP_TITLE = "Agente Abogado Laboral"
APP_VERSION = "1.7.0"
APP_DESCRIPTION = "API para análisis de contratos y conflictos laborales en Argentina"

# Ruta de la base de datos SQLite
DB_PATH = "memoria_agente.db"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, APP_DESCRIPTION

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)