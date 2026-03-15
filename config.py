import os

# 📌 Configuración de base de datos
DB_PATH = os.getenv("DB_PATH", ":memory:")

# 📌 Configuración de CORS
# Lista de orígenes permitidos para tu frontend en producción y pruebas locales
ALLOWED_ORIGINS = [
    "https://agente-laboral-frontend.vercel.app",  # dominio de tu frontend en Vercel
    "http://localhost:5173"                        # pruebas locales
]

# 📌 Normativa laboral común
NORMATIVA_BASE = [
    "Ley 20.744",
    "DNU 70/2023",
    "Ley 24.901"
]