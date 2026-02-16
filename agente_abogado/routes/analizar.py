# routes/analizar.py

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["Analizar"])

class AnalizarInput(BaseModel):
    texto: str | None = None
    text: str | None = None
    tipo: str | None = "consulta"  # valor por defecto

    @property
    def contenido(self) -> str:
        return self.texto or self.text or ""


@router.post("/analizar")
async def analizar_documento(request: Request, entrada: AnalizarInput):
    """
    Endpoint para analizar contratos, conflictos o consultas laborales.
    Devuelve un informe narrativo premium con explicación doctrinal.
    """
    agent = request.app.state.agent
    contenido = entrada.contenido.strip()

    if not contenido:
        return {"error": "No se recibió texto para analizar."}

    tipo = entrada.tipo.lower()
    if tipo == "contrato":
        resultado = agent.review_contract(contenido)
    elif tipo == "conflicto":
        resultado = agent.analizar_conflicto(contenido)
    elif tipo == "consulta":
        resultado = agent.responder_pregunta(contenido)
    else:
        return {"error": f"Tipo de análisis no reconocido: {entrada.tipo}"}

    # Generar informe narrativo premium
    informe = f"""
    ⚖️ Informe Jurídico Automatizado

    1. Resumen ejecutivo:
    {resultado['resumen']}

    2. Explicación doctrinal:
    {resultado['explicacion']}

    3. Normativa aplicable:
    - {resultado['normativa'][0]}
    - {resultado['normativa'][1]}
    - {resultado['normativa'][2]}

    4. Jurisprudencia relevante:
    {resultado['jurisprudencia']}

    5. Fallos relacionados:
    {len(resultado['fallos_relacionados'])} antecedentes encontrados.

    6. Clasificación del caso:
    {resultado['clasificacion']}

    7. Riesgos legales:
    {resultado['riesgos']}

    8. Recomendaciones:
    {resultado['recomendaciones']}

    9. Conclusión:
    {resultado['conclusion']}
    """

    return {"informe": informe.strip()}