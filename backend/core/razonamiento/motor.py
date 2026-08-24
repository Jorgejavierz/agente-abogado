# backend/core/razonamiento/motor.py
# Módulo central de razonamiento jurídico
# Autor: Jorge (Proyecto IA Jurídico)
# Descripción: Decide la acción a ejecutar según el tipo de consulta.

from backend.core.razonamiento.clasificador import clasificar_consulta
from backend.routes.consultar_documento import buscar_documento
from backend.juris_search import buscar_jurisprudencia

def razonamiento_juridico(consulta: str):
    """
    Procesa una consulta jurídica y decide la acción correspondiente.
    Retorna un diccionario con tipo y respuesta.
    """

    tipo = clasificar_consulta(consulta)

    if tipo == "documental":
        # Búsqueda en corpus legal (FAISS o base documental)
        resultados = buscar_documento(consulta)
        return {
            "tipo": "documental",
            "respuesta": resultados,
            "detalle": "Consulta documental procesada correctamente."
        }

    elif tipo == "soporte":
        # Explicación doctrinal o conceptual
        explicacion = f"Explicación jurídica sobre: {consulta}"
        return {
            "tipo": "soporte",
            "respuesta": explicacion,
            "detalle": "Consulta de soporte jurídico procesada correctamente."
        }

    elif tipo == "workflow":
        # Automatización de tareas o cálculo de plazos
        checklist = f"Checklist de plazos y tareas para: {consulta}"
        return {
            "tipo": "workflow",
            "respuesta": checklist,
            "detalle": "Consulta de workflow jurídico procesada correctamente."
        }

    elif tipo == "jurisprudencia":
        # Búsqueda de jurisprudencia
        resultados = buscar_jurisprudencia(consulta)
        return {
            "tipo": "jurisprudencia",
            "respuesta": resultados,
            "detalle": "Consulta de jurisprudencia procesada correctamente."
        }

    else:
        # Caso no clasificado
        return {
            "tipo": "indefinido",
            "respuesta": "No pude clasificar la consulta. Revisá el texto o contexto.",
            "detalle": "Tipo de consulta no reconocido."
        }
