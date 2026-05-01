# core/context_builder.py

from backend.core.formatter import ResponseFormatter


class ContextBuilder:
    """
    Construye el contexto que se envía al agente jurídico.
    Combina:
    - historial reciente
    - casos guardados
    - texto del usuario
    - resultados de búsqueda (si aplica)
    """

    def __init__(self, max_historial=5, max_casos=5):
        self.max_historial = max_historial
        self.max_casos = max_casos

    def construir_historial(self, historial):
        """
        Recibe una lista de dicts:
        [{"consulta": "...", "respuesta": "..."}]
        """
        if not historial:
            return "No hay historial previo."

        partes = []
        for h in historial[-self.max_historial:]:
            partes.append(
                f"- Consulta: {h['consulta']}\n  Respuesta: {h['respuesta']}"
            )

        return "\n".join(partes)

    def construir_casos(self, casos):
        """
        Recibe una lista de dicts provenientes de la DB.
        """
        if not casos:
            return "No hay casos guardados."

        partes = []
        for c in casos[-self.max_casos:]:
            partes.append(
                f"- Caso #{c['id']} ({c['tipo']}): {c['texto']}\n"
                f"  Resultado: {c['resultado']}"
            )

        return "\n".join(partes)

    def construir_contexto(self, historial, casos):
        """
        Devuelve un dict listo para inyectar en el prompt.
        """
        return {
            "historial": ResponseFormatter.limpiar_texto(
                self.construir_historial(historial)
            ),
            "casos": ResponseFormatter.limpiar_texto(
                self.construir_casos(casos)
            )
        }
