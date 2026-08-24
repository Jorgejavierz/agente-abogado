# backend/core/razonamiento/acciones.py
# Acciones del agente jurídico
# Autor: Jorge (Proyecto IA Jurídico)
# Descripción: Implementa funciones específicas para cada tipo de consulta.

from routes.consultar_documento import buscar_documento
from routes.juris_search import buscar_jurisprudencia
from faiss_index.search import buscar_en_faiss

def accion_documental(consulta: str):
    """
    Acción documental: búsqueda en corpus legal.
    Integra FAISS para recuperar documentos relevantes.
    """
    try:
        resultados = buscar_en_faiss(consulta)
        return {
            "tipo": "documental",
            "respuesta": resultados,
            "detalle": "Resultados obtenidos del corpus legal mediante FAISS."
        }
    except Exception:
        # Fallback: si FAISS falla, usar búsqueda tradicional
        resultados = buscar_documento(consulta)
        return {
            "tipo": "documental",
            "respuesta": resultados,
            "detalle": "Resultados obtenidos del módulo consultar_documento."
        }

def accion_soporte(consulta: str):
    """
    Acción de soporte: explicación doctrinal o conceptual.
    Inicialmente devuelve texto simple, luego puede integrarse con un LLM.
    """
    explicacion = f"Explicación doctrinal sobre: {consulta}"
    return {
        "tipo": "soporte",
        "respuesta": explicacion,
        "detalle": "Explicación doctrinal generada."
    }

def accion_workflow(consulta: str):
    """
    Acción de workflow: cálculo de plazos, generación de escritos o checklist de tareas.
    """
    checklist = [
        "Revisar normativa aplicable",
        "Calcular plazo de presentación",
        "Redactar escrito",
        "Presentar en tribunal"
    ]
    return {
        "tipo": "workflow",
        "respuesta": checklist,
        "detalle": "Workflow jurídico generado."
    }

def accion_indefinida(consulta: str):
    """
    Acción indefinida: fallback cuando no se puede clasificar la consulta.
    """
    return {
        "tipo": "indefinido",
        "respuesta": "No pude clasificar la consulta. Revisá el texto o contexto.",
        "detalle": "Tipo de consulta no reconocido."
    }
