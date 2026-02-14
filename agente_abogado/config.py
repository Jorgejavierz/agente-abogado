# config.py

# Lista de orígenes permitidos para CORS
ALLOWED_ORIGINS = [
    "http://localhost:8000",   # Backend local
    "http://127.0.0.1:8000",   # Alternativa local
    "http://localhost:3000",   # Frontend local en React
    "https://agente-abogado.onrender.com",  # URL pública en Render
    "https://agente-laboral-frontend.vercel.app"  # Frontend en Vercel
]

# Configuración general de la aplicación
APP_TITLE = "Agente Abogado Laboral"
APP_VERSION = "1.7.0"
APP_DESCRIPTION = "API para análisis de contratos y conflictos laborales en Argentina"

# Ruta de la base de datos SQLite
DB_PATH = "memoria_agente.db"