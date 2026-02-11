# formatter.py

class ResponseFormatter:
    """
    Clase encargada de dar formato narrativo a las respuestas
    generadas por el agente laboral.
    """

    @staticmethod
    def formatear(data: dict) -> str:
        normativa = "\n".join([f"- {n}" for n in data.get("normativa", [])]) \
                    or "No se identificó normativa directamente aplicable al documento analizado."
        fallos = "\n".join([f"- {f.get('titulo', 'Sin título')}" for f in data.get("fallos_relacionados", [])]) \
                 or "No se hallaron fallos relacionados en la base consultada."

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
El presente informe constituye una aproximación automatizada. No reemplaza la revisión jurídica especializada. 
Se recomienda la intervención de un abogado para evaluar riesgos, validar hallazgos y definir un curso de acción confiable.
"""