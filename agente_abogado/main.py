# agente_abogado/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import json

from agent import LaborLawyerAgent
from jurisprudencia import Jurisprudencia
from config import ALLOWED_ORIGINS

# -------------------------------
# Función para formatear respuestas narrativas
# -------------------------------
def formatear_respuesta(data: dict) -> str:
    normativa = "\n".join([f"- {n}" for n in data.get("normativa", [])]) or "No se encontró normativa aplicable."
    fallos = "\n".join([f"- {f['titulo']}" for f in data.get("fallos_relacionados", [])]) or "Sin resultados"

    return f"""
1. Resumen ejecutivo:
{data.get("resultado", "Sin conclusión")}

2. Normativa aplicable:
{normativa}

3. Jurisprudencia relevante:
{data.get("jurisprudencia", "No se encontraron fallos relevantes.")}

4. Clasificación del caso:
{data.get("clasificacion", "No se especificó clasificación.")}

5. Riesgos legales:
{data.get("riesgos", "No se detectaron riesgos específicos.")}

6. Recomendaciones:
{data.get("recomendaciones", "Se recomienda revisión por abogado humano.")}

7. Conclusión:
Este análisis debe ser revisado por un abogado humano antes de tomar decisiones.
"""

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

# -------------------------------
# Endpoint único de análisis
# -------------------------------
class TextoEntrada(BaseModel):
    texto: str

@app.post("/analizar", tags=["Análisis"])
async def analizar_texto(payload: TextoEntrada):
    texto = payload.texto
    agent = app.state.agent

    # Lógica simple de detección
    palabras_conflicto = ["denuncia", "conflicto", "discriminación", "acoso", "reclamo"]
    if any(palabra in texto.lower() for palabra in palabras_conflicto):
        informe = agent.analizar_conflicto(texto)
        tipo = "conflicto"
    else:
        informe = agent.review_contract(texto)
        tipo = "contrato"

    fallos = app.state.buscador.buscar_fallos(tipo)

    # Guardar en memoria con hora local
    conn = sqlite3.connect("memoria_agente.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
        VALUES (?, ?, ?, ?, datetime('now','localtime'))
    """, (
        tipo,
        texto,
        informe["resultado"],
        json.dumps(fallos)
    ))
    conn.commit()
    conn.close()

    resultado = {
        "resultado": informe["resultado"],
        "fallos_relacionados": fallos,
        "normativa": informe.get("normativa", []),
        "jurisprudencia": informe.get("jurisprudencia", ""),
        "clasificacion": informe.get("clasificacion", ""),
        "riesgos": informe.get("riesgos", ""),
        "recomendaciones": informe.get("recomendaciones", "")
    }

    return {
        "json": resultado,
        "texto_formateado": formatear_respuesta(resultado)
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
    feedback = [
        {"id": row[0], "texto": row[1], "util": bool(row[2]), "timestamp": row[3]}
        for row in rows
    ]
    return {"feedback": feedback}

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

    memoria = [
        {
            "id": row[0],
            "tipo": row[1],
            "texto": row[2],
            "resultado": row[3],
            "fallos_relacionados": json.loads(row[4]) if row[4] else [],
            "timestamp": row[5],
        }
        for row in rows
    ]

    return {"memoria": memoria}