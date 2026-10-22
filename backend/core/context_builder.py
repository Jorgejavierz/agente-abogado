from backend.core.formatter import ResponseFormatter


class ContextBuilder:
    """
    Construye el contexto completo del agente jurídico.

    Combina:
    - historial
    - casos
    - antecedentes FAISS
    - jurisprudencia
    - normativa
    """

    def __init__(self, max_historial=5, max_casos=5, max_fallos=5):
        self.max_historial = max_historial
        self.max_casos = max_casos
        self.max_fallos = max_fallos

    # ============================================================
    # HISTORIAL
    # ============================================================

    def construir_historial(self, historial):

        if not historial:
            return "No hay historial previo."

        partes = []

        for h in historial[-self.max_historial:]:

            consulta = h.get("consulta", "N/A")

            respuesta = (
                h.get("respuesta", "")[:500]
                if h.get("respuesta")
                else "N/A"
            )

            partes.append(
                f"Consulta: {consulta}\n"
                f"Respuesta: {respuesta}"
            )

        return "\n\n".join(partes)

    # ============================================================
    # CASOS
    # ============================================================

    def construir_casos(self, casos):

        if not casos:
            return "No hay casos guardados."

        partes = []

        for c in casos[-self.max_casos:]:

            resultado = (
                c.get("resultado", "")[:500]
                if c.get("resultado")
                else ""
            )

            partes.append(
                f"Caso #{c.get('id')}\n"
                f"Tipo: {c.get('tipo')}\n"
                f"Consulta: {c.get('texto')}\n"
                f"Resultado: {resultado}"
            )

        return "\n\n".join(partes)

    # ============================================================
    # FAISS
    # ============================================================

    def construir_faiss(self, antecedentes):

        if not antecedentes:
            return "No se encontraron antecedentes en FAISS."

        partes = []

        for a in antecedentes[:5]:

            partes.append(
                f"Documento: {a.get('documento', 'Sin fuente')}\n"
                f"Contenido: {a.get('texto', '')}"
            )

        return "\n\n".join(partes)

    # ============================================================
    # JURISPRUDENCIA
    # ============================================================

    def construir_jurisprudencia(self, fallos):

        if not fallos:
            return "No se encontraron antecedentes jurisprudenciales."

        partes = []

        for f in fallos[:self.max_fallos]:

            partes.append(
                f"Título: {f.get('titulo')}\n"
                f"Origen: {f.get('origen')}\n"
                f"Tribunal: {f.get('tribunal')}\n"
                f"Fecha: {f.get('fecha')}\n"
                f"Contenido: {f.get('contenido')}"
            )

        return "\n\n".join(partes)

    # ============================================================
    # NORMATIVA
    # ============================================================

    def construir_normativa(self, normas):

        if not normas:
            return "No se encontró normativa aplicable."

        partes = []

        for n in normas[:5]:

            partes.append(
                f"Título: {n.get('titulo')}\n"
                f"Origen: {n.get('origen')}\n"
                f"Contenido: {n.get('contenido')}"
            )

        return "\n\n".join(partes)
    
    # ============================================================
    # CONTEXTO FINAL
    # ============================================================

    def construir_contexto(
        self,
        historial,
        casos,
        antecedentes_faiss=None,
        fallos=None,
        normativa=None
    ):

        return {
            "historial": ResponseFormatter.limpiar_texto(
                self.construir_historial(historial)
            ),

            "casos": ResponseFormatter.limpiar_texto(
                self.construir_casos(casos)
            ),

            "faiss": ResponseFormatter.limpiar_texto(
                self.construir_faiss(antecedentes_faiss or [])
            ),

            "jurisprudencia": ResponseFormatter.limpiar_texto(
                self.construir_jurisprudencia(fallos or [])
            ),

            "normativa": ResponseFormatter.limpiar_texto(
                self.construir_normativa(normativa or [])
            ),
        }