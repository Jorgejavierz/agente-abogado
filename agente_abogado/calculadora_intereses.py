from datetime import datetime

class CalculadoraIntereses:
    def __init__(self):
        self.ultima_tasa_guardada = None

    def obtener_tasa_oficial(self):
        """
        Simulación: en producción deberías hacer un request a la web oficial
        del Poder Judicial de Neuquén o BPN para traer la tasa vigente.
        """
        try:
            # Ejemplo: supongamos que la tasa oficial es 60% TNA
            tasa = {"valor": 60, "fecha": datetime.now().strftime("%Y-%m-%d")}
            self.ultima_tasa_guardada = tasa
            return tasa
        except Exception:
            return None

    def calcular(self, capital: float, fecha_inicio: str, fecha_fin: str):
        tasa = self.obtener_tasa_oficial()
        if not tasa and self.ultima_tasa_guardada:
            tasa = self.ultima_tasa_guardada

        if not tasa:
            raise ValueError("No se pudo obtener ninguna tasa vigente")

        inicio = datetime.fromisoformat(fecha_inicio)
        fin = datetime.fromisoformat(fecha_fin)
        dias = (fin - inicio).days

        tasa_diaria = tasa["valor"] / 365
        intereses = capital * (tasa_diaria / 100) * dias
        monto_final = capital + intereses

        return {
            "capital": capital,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tasa_usada": tasa,
            "monto_final": monto_final
        }