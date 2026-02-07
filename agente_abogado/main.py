# agente_abogado/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import PyPDF2
import docx

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

4. Fallos relacionados:
{fallos}

5. Clasificación del caso:
{data.get("clasificacion", "No se especificó clasificación.")}

6. Riesgos legales:
{data.get("riesgos", "No se detectaron riesgos específicos.")}

7. Recomendaciones:
{data.get("recomendaciones", "Se recomienda revisión por abogado humano.")}

8. OCT (Análisis complementario):
Clasificación OCT: {data.get("oct", {}).get("clasificacion_oct", "No disponible")}
Riesgos OCT: {data.get("oct", {}).get("riesgos_oct", "No disponible")}
Recomendaciones OCT: {data.get("oct", {}).get("recomendaciones_oct", "No disponible")}

9. Conclusión:
Este análisis debe ser revisado por un abogado humano antes de tomar decisiones.
"""

# Inicializar FastAPI
app = FastAPI(
    title="Agente Abogado Laboral",
    version="1.4.0",
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
        print(f"[ERROR] Inicializando dependencias: {e}")

# -------------------------------
# Endpoints de salud
# -------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"mensaje": "Agente Abogado Laboral inicializado correctamente ✅"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

# -------------------------------
# Endpoint de análisis (con soporte de archivo y OCT integrado)
# -------------------------------
@app.post("/analizar", tags=["Análisis"])
async def analizar_texto(
    file: UploadFile = File(None),
    texto: str = Form(None)
):
    try:
        contenido = ""

        # Logging para depuración
        if file:
            print(f"[LOG] Recibí archivo: {file.filename}")
        if texto:
            print(f"[LOG] Recibí texto: {texto[:200]}...")

        # Procesar archivo si existe
        if file:
            if file.filename.endswith(".pdf"):
                reader = PyPDF2.PdfReader(file.file)
                contenido = "".join([page.extract_text() or "" for page in reader.pages])
            elif file.filename.endswith(".docx"):
                docx_file = docx.Document(file.file)
                contenido = "\n".join([para.text for para in docx_file.paragraphs])
            elif file.filename.endswith(".txt"):
                contenido = (await file.read()).decode("utf-8")
            else:
                raise HTTPException(status_code=400, detail="Formato no soportado")
        elif texto:
            contenido = texto
        else:
            raise HTTPException(status_code=400, detail="No se recibió archivo ni texto")

        agent = app.state.agent

        # Lógica de detección básica
        palabras_conflicto = ["denuncia", "conflicto", "discriminación", "acoso", "reclamo"]
        if any(palabra in contenido.lower() for palabra in palabras_conflicto):
            informe = agent.analizar_conflicto(contenido)
            tipo = "conflicto"
        else:
            informe = agent.review_contract(contenido)
            tipo = "contrato"

        # Evitar respuestas repetidas: si no hay hallazgos, devolver mensaje claro
        if not informe.get("resultado"):
            informe["resultado"] = "No se encontraron cláusulas abusivas específicas en este texto."

        # 🔹 Algoritmo OCT integrado
        def ejecutar_oct(texto: str) -> dict:
            return {
                "clasificacion_oct": "Clasificación OCT simulada",
                "riesgos_oct": "Riesgos detectados por OCT",
                "recomendaciones_oct": "Recomendaciones OCT"
            }

        oct_resultado = ejecutar_oct(contenido)

        fallos = app.state.buscador.buscar_fallos(tipo)

        # Guardar en memoria
        conn = sqlite3.connect("memoria_agente.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
            VALUES (?, ?, ?, ?, datetime('now','localtime'))
        """, (
            tipo,
            contenido,
            informe.get("resultado", ""),
            json.dumps(fallos)
        ))
        conn.commit()
        conn.close()

        # Combinar informe normal + OCT
        resultado = {
            "resultado": informe.get("resultado", ""),
            "fallos_relacionados": fallos,
            "normativa": informe.get("normativa", []),
            "jurisprudencia": informe.get("jurisprudencia", ""),
            "clasificacion": informe.get("clasificacion", ""),
            "riesgos": informe.get("riesgos", ""),
            "recomendaciones": informe.get("recomendaciones", ""),
            "oct": oct_resultado
        }

        return {
            "json": resultado,
            "texto": contenido[:1000],
            "texto_formateado": formatear_respuesta(resultado)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

# -------------------------------
# Endpoints de Feedback
# -------------------------------
@app.post("/feedback", tags=["Feedback"])
async def guardar_feedback(feedback: dict):
    try:
        conn = sqlite3.connect("memoria_agente.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (texto, util, timestamp)
            VALUES (?, ?, ?)
        """, (feedback["texto"], feedback["util"], feedback["timestamp"]))
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