# backend/core/razonamiento/clasificador.py
# Clasificador de consultas jurídicas
# Autor: Jorge (Proyecto IA Jurídico)
# Descripción: Determina si una consulta es documental, soporte o workflow.

def clasificar_consulta(texto: str) -> str:
    """
    Clasifica la consulta jurídica en categorías:
    - documental: búsqueda de leyes, artículos, jurisprudencia
    - soporte: explicación doctrinal o conceptual
    - workflow: plazos, tareas, escritos procesales
    - indefinido: no se pudo clasificar
    """

    if not texto:
        return "indefinido"

    texto = texto.lower()

    # Reglas simples iniciales (se pueden mejorar con NLP/LLM)
    if any(palabra in texto for palabra in ["ley", "artículo", "jurisprudencia", "norma", "código"]):
        return "documental"

    elif any(palabra in texto for palabra in ["qué significa", "cómo", "explicación", "doctrina", "concepto"]):
        return "soporte"

    elif any(palabra in texto for palabra in ["plazo", "presentar", "escrito", "demanda", "workflow", "tarea"]):
        return "workflow"

    else:
        return "indefinido"
