# routes/analizar.py

from fastapi import APIRouter, Request, UploadFile, File
from pydantic import BaseModel
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

# Configuración de Tesseract en Windows
# Ajustá la ruta si instalaste Tesseract en otro directorio
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

router = APIRouter(tags=["Analizar"])

class AnalizarInput(BaseModel):
    texto: str | None = None
    text: str | None = None
    tipo: str | None = "consulta"  # valor por defecto

    @property
    def contenido(self) -> str:
        return self.texto or self.text or ""


@router.post("/analizar")
async def analizar_documento(
    request: Request,
    entrada: AnalizarInput = None,
    file: UploadFile = File(None)
):
    """
    Endpoint premium para analizar contratos, conflictos o consultas laborales.
    Puede recibir texto en JSON o un archivo PDF.
    Si el PDF no tiene texto embebido, aplica OCR para extraerlo.
    Devuelve un informe narrativo con explicación doctrinal, normativa, jurisprudencia y fuentes.
    """
    agent = request.app.state.agent
    contenido = ""

    # Caso 1: si se sube un archivo PDF
    if file:
        # Intentar extraer texto con PyPDF2
        reader = PdfReader(file.file)
        contenido = "".join([page.extract_text() or "" for page in reader.pages]).strip()

        # Si no se pudo extraer texto, aplicar OCR
        if not contenido:
            file.file.seek(0)  # volver al inicio del archivo
            pdf_bytes = file.file.read()
            paginas = convert_from_bytes(pdf_bytes)
            contenido = ""
            for pagina in paginas:
                contenido += pytesseract.image_to_string(pagina, lang="spa") + "\n"
            contenido = contenido.strip()

        if not contenido:
            return {"error": "No se pudo extraer texto del archivo, ni siquiera con OCR."}

    # Caso 2: si se envía texto en JSON
    elif entrada:
        contenido = entrada.contenido.strip()

    if not contenido:
        return {"error": "No se recibió texto ni archivo para analizar."}

    tipo = entrada.tipo.lower() if entrada and entrada.tipo else "consulta"

    # Usamos responder_pregunta como fallback seguro
    if tipo == "contrato" and hasattr(agent, "review_contract"):
        resultado = agent.review_contract(contenido)
    elif tipo == "conflicto" and hasattr(agent, "analizar_conflicto"):
        resultado = agent.analizar_conflicto(contenido)
    else:
        resultado = agent.responder_pregunta(contenido)

    # Generar informe narrativo premium
    informe = f"""
    ⚖️ Informe Jurídico Automatizado

    1. Consulta recibida:
    {resultado.get('consulta', 'Sin consulta disponible.')}

    2. Explicación doctrinal:
    {resultado.get('explicacion_doctrinal', 'No se encontró explicación doctrinal.')}
    Fuente: {resultado.get('fuente', 'Sin fuente disponible')}

    3. Normativa aplicable:
    - {resultado.get('normativa_aplicable', ['Sin normativa'])[0]}
    - {resultado.get('normativa_aplicable', ['Sin normativa'])[1] if len(resultado.get('normativa_aplicable', [])) > 1 else ''}
    - {resultado.get('normativa_aplicable', ['Sin normativa'])[2] if len(resultado.get('normativa_aplicable', [])) > 2 else ''}

    4. Jurisprudencia relevante:
    {resultado.get('jurisprudencia_relevante', 'No se encontraron antecedentes.')}

    5. Fallos relacionados:
    {len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

    6. Clasificación del caso:
    {resultado.get('clasificacion', 'Sin clasificación.')}

    7. Riesgos legales:
    {resultado.get('riesgos_legales', 'No se identificaron riesgos.')}

    8. Recomendaciones:
    {resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

    9. Conclusión:
    {resultado.get('conclusion', 'Sin conclusión disponible.')}
    """

    return {"informe": informe.strip()}