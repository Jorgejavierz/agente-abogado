# agente_abogado/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json

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

# Configurar CORS
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
        # Inicializar base de datos
        conn = sqlite3.connect("memoria_agente.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT,
                util BOOLEAN,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                texto TEXT,
                resultado TEXT,
                fallos_relacionados TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
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

    # Guardar en memoria (solo strings y listas serializadas)
    conn = sqlite3.connect("memoria_agente.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        "contrato",
        contrato.texto,
        informe["resultado"],          # string
        json.dumps(fallos)             # lista serializada
    ))
    conn.commit()
    conn.close()

    return {
        "resultado": informe["resultado"],
        "fallos_relacionados": fallos,
        "normativa": informe["normativa"]
    }

# Endpoint para analizar conflicto
@app.post("/analizar-conflicto", tags=["Conflictos"])
async def analizar_conflicto(data: dict):
    conflicto = validar_conflicto(data)
    if not conflicto:
        return {"error": "Conflicto inválido"}

    informe = app.state.agent.analizar_conflicto(conflicto.descripcion)
    fallos = app.state.buscador.buscar_fallos("conflicto")

    # Guardar en memoria (solo strings y listas serializadas)
    conn = sqlite3.connect("memoria_agente.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        "conflicto",
        conflicto.descripcion,
        informe["resultado"],          # string
        json.dumps(fallos)             # lista serializada
    ))
    conn.commit()
    conn.close()

    return {
        "resultado": informe["resultado"],
        "fallos_relacionados": fallos,
        "normativa": informe["normativa"]
    }

# -------------------------------
# Endpoint de Feedback
# -------------------------------

class Feedback(BaseModel):
    texto: str
    util: bool
    timestamp: str

@app.post("/feedback", tags=["Feedback"])
async def guardar_feedback(feedback: Feedback):
    try:
        conn = sqlite3.connect("memoria_agente.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (texto, util, timestamp)
            VALUES (?, ?, ?)
        """, (feedback.texto, feedback.util, feedback.timestamp))
        conn.commit()
        conn.close()
        return {"mensaje": "Feedback guardado correctamente ✅"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/feedback", tags=["Feedback"])
async def listar_feedback():
    conn = sqlite3.connect("memoria_agente.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto, util, timestamp FROM feedback ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return {"feedback": rows}

# -------------------------------
# Endpoint de Memoria
# -------------------------------

@app.get("/memoria", tags=["Memoria"])
async def listar_memoria(limit: int = 10):
    conn = sqlite3.connect("memoria_agente.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo, texto, resultado, fallos_relacionados, timestamp
        FROM memoria
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"memoria": rows}