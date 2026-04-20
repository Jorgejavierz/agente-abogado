import os
from openai import OpenAI
from backend.db import MemoriaDB

# ============================================================
# CONFIGURACIÓN DEL LLM
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
llm_client = OpenAI(api_key=OPENAI_API_KEY)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

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
