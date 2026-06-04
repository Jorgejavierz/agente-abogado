from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI
from backend.db import MemoriaDB

# ============================================================
# CONFIGURACIÓN DEL LLM (DeepSeek)
# ============================================================

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró OPENAI_API_KEY en el entorno. Verificá el archivo .env")

llm_client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1"
)

MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

# ============================================================
# CONFIGURACIÓN DE FAISS
# ============================================================

FAISS_SERVER = os.getenv("FAISS_URL", "http://127.0.0.1:8081")

# ============================================================
# BASE DE DATOS LOCAL
# ============================================================

DB_PATH = os.getenv("DB_PATH", "memoria_agente.db")
db = MemoriaDB(DB_PATH)

# ============================================================
# CONFIGURACIÓN DE OCR
# ============================================================

TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
