from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import PyPDF2
import docx
import numpy as np
import faiss

from agent import LaborLawyerAgent
from jurisprudencia import Jurisprudencia
from config import ALLOWED_ORIGINS
from pydantic import BaseModel

# -------------------------------
# Función para formatear respuestas narrativas
# -------------------------------
def formatear_respuesta(data: dict) -> str:
    normativa = "\n".join([f"- {n}" for n in data.get("normativa", [])]) or "No se identificó normativa directamente aplicable al documento analizado."
    fallos = "\n".join([f"- {f['titulo']}" for f in data.get("fallos_relacionados", [])]) or "No se hallaron fallos relacionados en la base consultada."

    return f"""
1. Resumen ejecutivo:
{data.get("resultado", "El análisis automático no detectó hallazgos específicos. Este tipo de documentos requiere revisión humana especializada.")}

2. Normativa aplicable:
{normativa}

3. Jurisprudencia relevante:
{data.get("jurisprudencia", "No se encontraron antecedentes jurisprudenciales relevantes para este caso.")}

4. Fallos relacionados:
{fallos}

5. Clasificación del caso:
{data.get("clasificacion", "Sin clasificación automática disponible. Se recomienda evaluación jurídica.")}

6. Riesgos legales:
{data.get("riesgos", "No se detectaron riesgos específicos en esta etapa preliminar. Una revisión experta podría identificar aspectos adicionales.")}

7. Recomendaciones:
{data.get("recomendaciones", "Se recomienda revisión jurídica especializada para determinar implicancias y definir estrategias.")}

8. OCT (Análisis complementario):
- Clasificación OCT: {data.get("oct", {}).get("clasificacion_oct", "No disponible")}
- Riesgos OCT: {data.get("oct", {}).get("riesgos_oct", "No disponible")}
- Recomendaciones OCT: {data.get("oct", {}).get("recomendaciones_oct", "No disponible")}

9. Conclusión:
El presente informe constituye una aproximación automatizada. No reemplaza la revisión jurídica especializada. Se recomienda la intervención de un abogado para evaluar riesgos, validar hallazgos y definir un curso de acción confiable.
"""

# -------------------------------
# Inicializar FastAPI
# -------------------------------
app = FastAPI(
    title="Agente Abogado Laboral",
    version="1.7.0",
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

# -------------------------------
# Inicializar dependencias en startup (optimizado)
# -------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        # Inicializamos solo el agente liviano
        app.state.agent = LaborLawyerAgent()

        # ⚠️ Jurisprudencia se cargará bajo demanda en los endpoints
        # if not hasattr(app.state, "buscador"):
        #     app.state.buscador = Jurisprudencia()

        # Inicializamos la base de datos y tablas
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
# Endpoint de análisis
# -------------------------------
@app.post("/analizar", tags=["Análisis"])
async def analizar_texto(
    file: UploadFile = File(None),
    texto: str = Form(None)
):
    try:
        contenido = ""

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

        # 🔎 Detección de tipo de documento
        palabras_judiciales = ["juzgado", "expediente", "autos", "pronto despacho", "sentencia"]
        if any(p in contenido.lower() for p in palabras_judiciales):
            informe = {"resultado": "El documento corresponde a un escrito judicial. Se recomienda revisión humana especializada."}
            tipo = "judicial"
        else:
            palabras_conflicto = ["denuncia", "conflicto", "discriminación", "acoso", "reclamo"]
            if any(palabra in contenido.lower() for palabra in palabras_conflicto):
                informe = agent.analizar_conflicto(contenido)
                tipo = "conflicto"
            else:
                informe = agent.review_contract(contenido)
                tipo = "contrato"

        if not informe.get("resultado"):
            informe["resultado"] = "No se detectaron hallazgos específicos en este texto."

        # 🔹 Algoritmo OCT integrado
        def ejecutar_oct(texto: str) -> dict:
            return {
                "clasificacion_oct": "Clasificación OCT simulada",
                "riesgos_oct": "Riesgos detectados por OCT",
                "recomendaciones_oct": "Recomendaciones OCT"
            }

        oct_resultado = ejecutar_oct(contenido)

        # 🔹 Buscar fallos (scraping + semántica)
        fallos = app.state.buscador.buscar_fallos(contenido, top_k=5, tema=tipo)

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

# -------------------------------
# Endpoints de Jurisprudencia (administración)
# -------------------------------

class FalloInput(BaseModel):
    titulo: str
    texto: str
    tema: str
    tribunal: str
    fecha: str
    link: str | None = None

@app.post("/agregar_fallo", tags=["Jurisprudencia"])
async def agregar_fallo(fallo: FalloInput):
    """
    Agrega un fallo manualmente a la base local e indexa en FAISS.
    """
    app.state.buscador.agregar_fallo(
        titulo=fallo.titulo,
        texto=fallo.texto,
        tema=fallo.tema,
        tribunal=fallo.tribunal,
        fecha=fallo.fecha,
        link=fallo.link
    )
    return {"mensaje": "Fallo agregado e indexado correctamente ✅", "titulo": fallo.titulo}

@app.get("/listar_fallos", tags=["Jurisprudencia"])
async def listar_fallos():
    """
    Lista todos los fallos cargados en la base local con sus metadatos.
    """
    if not app.state.buscador.fallos:
        return {"mensaje": "No hay fallos cargados en la base local."}

    resultados = [
        {
            "titulo": fallo["titulo"],
            "tema": fallo["tema"],
            "tribunal": fallo["tribunal"],
            "fecha": fallo["fecha"],
            "fuente": fallo.get("link", "Fuente local")
        }
        for fallo in app.state.buscador.fallos
    ]

    return {"fallos": resultados}

@app.delete("/eliminar_fallo/{titulo}", tags=["Jurisprudencia"])
async def eliminar_fallo(titulo: str):
    """
    Elimina un fallo de la base local por su título y reconstruye el índice FAISS.
    """
    fallo_encontrado = None
    for fallo in app.state.buscador.fallos:
        if fallo["titulo"].lower() == titulo.lower():
            fallo_encontrado = fallo
            break

    if not fallo_encontrado:
        raise HTTPException(status_code=404, detail=f"No se encontró ningún fallo con el título: {titulo}")

    app.state.buscador.fallos.remove(fallo_encontrado)

    if app.state.buscador.fallos:
        embeddings = np.array([f["embedding"] for f in app.state.buscador.fallos])
        app.state.buscador.index = faiss.IndexFlatL2(embeddings.shape[1])
        app.state.buscador.index.add(embeddings)
    else:
        app.state.buscador.index = None

    return {"mensaje": f"Fallo '{titulo}' eliminado correctamente ✅"}