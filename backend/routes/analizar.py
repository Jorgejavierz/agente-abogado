# backend/routes/analizar.py

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
import logging
from backend.routes.pdf import extraer_texto_pdf  # Usamos la función centralizada

logger = logging.getLogger("backend.routes.analizar")

# Definir el router
router = APIRouter(tags=["Analizar"])


# ---------------------------
# Modelo de entrada
# ---------------------------
class AnalizarInput(BaseModel):
    texto: str | None = None
    text: str | None = None
    tipo: str | None = "consulta"

    @property
    def contenido(self) -> str:
        return (self.texto or self.text or "").strip()


# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/procesar-documento")
@router.post("/analizar")
async def analizar_documento(
    request: Request,
    entrada: AnalizarInput | None = None,
    file: UploadFile | None = File(None)
):
    """
    Analiza texto o PDF y devuelve un informe jurídico estructurado.
    """

    agente = request.app.state.agent
    contenido = ""

    try:
        # Caso 1: archivo PDF
        if file:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")

            file_bytes = await file.read()
            contenido = extraer_texto_pdf(file_bytes)

            if not contenido:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo extraer texto del PDF, ni siquiera con OCR."
                )

        # Caso 2: texto enviado en JSON
        elif entrada:
            contenido = entrada.contenido

        # Validación
        if not contenido:
            raise HTTPException(status_code=400, detail="No se recibió texto válido para analizar.")

        # Delegar al agente jurídico
        resultado = agente.responder(contenido)

        # Construcción del informe narrativo
        informe = f"""
⚖️ Informe Jurídico Automatizado

1. Consulta recibida:
{resultado.get('consulta', 'Sin consulta disponible.')}

2. Explicación doctrinal:
{resultado.get('explicacion_doctrinal', 'No se encontró explicación doctrinal.')}
Fuente: {resultado.get('fuente', 'Sin fuente disponible')}

3. Jurisprudencia relevante:
{resultado.get('jurisprudencia_relevante', 'No se encontraron antecedentes.')}

4. Fallos relacionados:
{len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

5. Clasificación del caso:
{resultado.get('clasificacion', 'Sin clasificación.')}

6. Recomendaciones:
{resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

7. Conclusión:
{resultado.get('conclusion', 'Sin conclusión disponible.')}
"""

        return {
            "status": "ok",
            "informe": informe.strip(),
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en /analizar: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


# ---------------------------
# Endpoint GET para consultas rápidas
# ---------------------------
@router.get("/consultar_documento")
async def consultar_documento(request: Request, pregunta: str = Query(..., min_length=1)):
    """
    Endpoint para consultas rápidas por texto: /consultar_documento?pregunta=...
    """
    agente = request.app.state.agent
    try:
        contenido = pregunta.strip()
        if not contenido:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

        resultado = agente.responder(contenido)

        informe = f"""
⚖️ Informe Jurídico Automatizado

1. Consulta recibida:
{resultado.get('consulta', 'Sin consulta disponible.')}

2. Explicación doctrinal:
{resultado.get('explicacion_doctrinal', 'No se encontró explicación doctrinal.')}
Fuente: {resultado.get('fuente', 'Sin fuente disponible')}

3. Jurisprudencia relevante:
{resultado.get('jurisprudencia_relevante', 'No se encontraron antecedentes.')}

4. Fallos relacionados:
{len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

5. Clasificación del caso:
{resultado.get('clasificacion', 'Sin clasificación.')}

6. Recomendaciones:
{resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

7. Conclusión:
{resultado.get('conclusion', 'Sin conclusión disponible.')}
"""
        return {
            "status": "ok",
            "informe": informe.strip(),
            "origen": "Agente Laboral IA"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en /consultar_documento: %s", e)
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
