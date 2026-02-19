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
    Devuelve un informe narrativo premium con explicación doctrinal, normativa, jurisprudencia y fuentes.
    """
    agent = request.app.state.agent
    contenido = entrada.contenido.strip()

    if not contenido:
        return {"error": "No se recibió texto para analizar."}

    tipo = entrada.tipo.lower()

    # Usamos responder_pregunta como fallback seguro
    if tipo == "contrato" and hasattr(agent, "review_contract"):
        resultado = agent.review_contract(contenido)
    elif tipo == "conflicto" and hasattr(agent, "analizar_conflicto"):
        resultado = agent.analizar_conflicto(contenido)
    else:
        resultado = agent.responder_pregunta(contenido)

    # Asegurar que siempre exista el campo 'explicacion' y 'fuente'
    explicacion = resultado.get("explicacion", "No se encontró explicación doctrinal para este concepto.")
    fuente = resultado.get("fuente", "Sin fuente disponible")

    # Generar informe narrativo premium
    informe = f"""
    ⚖️ Informe Jurídico Automatizado

    1. Resumen ejecutivo:
    {resultado.get('resumen', 'Sin resumen disponible.')}

    2. Explicación doctrinal:
    {explicacion}
    Fuente: {fuente}

    3. Normativa aplicable:
    - {resultado['normativa'][0]}
    - {resultado['normativa'][1]}
    - {resultado['normativa'][2]}

    4. Jurisprudencia relevante:
    {resultado.get('jurisprudencia', 'No se encontraron antecedentes.')}

    5. Fallos relacionados:
    {len(resultado.get('fallos_relacionados', []))} antecedentes encontrados.

    6. Clasificación del caso:
    {resultado.get('clasificacion', 'Sin clasificación.')}

    7. Riesgos legales:
    {resultado.get('riesgos', 'No se identificaron riesgos.')}

    8. Recomendaciones:
    {resultado.get('recomendaciones', 'No se generaron recomendaciones.')}

    9. Conclusión:
    {resultado.get('conclusion', 'Sin conclusión disponible.')}
    """

    return {"informe": informe.strip()}