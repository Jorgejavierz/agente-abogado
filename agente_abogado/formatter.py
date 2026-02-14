# formatter.py

class ResponseFormatter:
    @staticmethod
    def formatear(resultado: dict) -> str:
        """
        Convierte la respuesta del agente en un informe narrativo profesional.
        """
        partes = []

        # 1. Resumen ejecutivo
        partes.append("1. Resumen ejecutivo:")
        partes.append(resultado.get("resumen", resultado.get("resultado", "No disponible")))
        partes.append("")

        # 2. Normativa aplicable
        partes.append("2. Normativa aplicable:")
        normativa = resultado.get("normativa", [])
        if normativa:
            for norma in normativa:
                partes.append(f"- {norma}")
        else:
            partes.append("No se identificaron normas relevantes.")
        partes.append("")

        # 3. Jurisprudencia relevante
        partes.append("3. Jurisprudencia relevante:")
        partes.append(resultado.get("jurisprudencia", "No disponible"))
        partes.append("")

        # 4. Fallos relacionados
        partes.append("4. Fallos relacionados:")
        fallos = resultado.get("fallos_relacionados", [])
        if fallos:
            for fallo in fallos:
                partes.append(f"- {fallo}")
        else:
            partes.append("No se encontraron fallos relacionados.")
        partes.append("")

        # 5. Clasificación del caso
        partes.append("5. Clasificación del caso:")
        partes.append(resultado.get("clasificacion", "No disponible"))
        partes.append("")

        # 6. Riesgos legales
        partes.append("6. Riesgos legales:")
        partes.append(resultado.get("riesgos", "No disponible"))
        partes.append("")

        # 7. Recomendaciones
        partes.append("7. Recomendaciones:")
        partes.append(resultado.get("recomendaciones", "No disponible"))
        partes.append("")

        # 8. Conclusión
        partes.append("8. Conclusión:")
        partes.append(resultado.get("conclusion", "Este informe es una aproximación automatizada. No reemplaza la revisión jurídica especializada."))
        partes.append("")

        return "\n".join(partes)