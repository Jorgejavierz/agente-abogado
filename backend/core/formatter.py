# core/formatter.py

import re


class ResponseFormatter:
    """
    Formatea las respuestas del agente para asegurar:
    - Limpieza de texto
    - Markdown consistente
    - Eliminación de repeticiones
    - Estructura jurídica clara
    """

    @staticmethod
    def limpiar_texto(texto: str) -> str:
        """Normaliza espacios, saltos de línea y caracteres invisibles."""
        if not texto:
            return ""

        # Quitar espacios duplicados
        texto = re.sub(r"[ \t]+", " ", texto)

        # Normalizar saltos de línea
        texto = texto.replace("\r", "")
        texto = re.sub(r"\n{3,}", "\n\n", texto)

        # Quitar caracteres invisibles
        texto = texto.replace("\u200b", "")

        return texto.strip()

    @staticmethod
    def limpiar_bullets(texto: str) -> str:
        """Asegura que los bullets tengan formato Markdown correcto."""
        if not texto:
            return ""

        # Convertir bullets raros a "-"
        texto = re.sub(r"^[•●▪▶►]", "- ", texto, flags=re.MULTILINE)

        # Asegurar espacio después del guion
        texto = re.sub(r"^-([^ ])", "- \\1", texto, flags=re.MULTILINE)

        return texto

    @staticmethod
    def eliminar_repeticiones(texto: str) -> str:
        """Elimina repeticiones típicas del LLM."""
        if not texto:
            return ""

        texto = re.sub(
            r"(En resumen,|En conclusión,|Por lo tanto,)\s*\1",
            r"\1",
            texto,
            flags=re.IGNORECASE
        )

        return texto

    @staticmethod
    def formatear_respuesta(texto: str) -> str:
        """Pipeline completo de formateo."""
        texto = ResponseFormatter.limpiar_texto(texto)
        texto = ResponseFormatter.limpiar_bullets(texto)
        texto = ResponseFormatter.eliminar_repeticiones(texto)
        return texto
