# config.py
import os

# 📌 Configuración de base de datos
# Por defecto usa memoria, pero podés definir DB_PATH en Render o localmente
DB_PATH = os.getenv("DB_PATH", ":memory:")

# 📌 Configuración de CORS
# Lista de orígenes permitidos para tu frontend y pruebas locales
ALLOWED_ORIGINS = [
    "https://agente-laboral-frontend.vercel.app",  # dominio de tu frontend en producción
    "http://localhost:5173",                       # pruebas locales
    "*"                                            # abierto para pruebas generales
]

# 📌 Normativa laboral común
# Centralizamos las leyes que se usan en varios métodos
NORMATIVA_BASE = [
    "Ley 20.744",
    "DNU 70/2023",
    "Ley 24.901"
]