import requests
from bs4 import BeautifulSoup
from datetime import datetime

class CalculadoraIntereses:
    def __init__(self):
        self.ultima_tasa_guardada = None

    def obtener_tasa_oficial(self, tipo_tasa="TEA"):
        try:
            url = "https://cintereses.agjusneuquen.gob.ar/"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")

            # 🔹 Buscar la tasa según el tipo (ej. "TEA", "TNA", "Activa", "Pasiva")
            tasa_text = soup.find(string=lambda t: t and tipo_tasa in t).find_next("td").text
            tasa_valor = float(tasa_text.replace("%", "").strip())

            tasa = {
                "tipo": tipo_tasa,
                "valor": tasa_valor,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "fuente": "Poder Judicial de Neuquén"
            }
            self.ultima_tasa_guardada = tasa
            return tasa
        except Exception:
            return self.ultima_tasa_guardada

    def calcular(self, capital: float, fecha_inicio: str, fecha_fin: str, tipo_tasa="TEA"):
        tasa = self.obtener_tasa_oficial(tipo_tasa)
        if not tasa:
            raise ValueError("No se pudo obtener ninguna tasa vigente")

        inicio = datetime.fromisoformat(fecha_inicio)
        fin = datetime.fromisoformat(fecha_fin)
        dias = (fin - inicio).days

        # 🔹 Ajustar cálculo según tipo de tasa
        if tipo_tasa.upper() == "TEA":
            tasa_diaria = (1 + tasa["valor"]/100) ** (1/365) - 1
        else:
            tasa_diaria = tasa["valor"] / 365 / 100

        intereses = capital * tasa_diaria * dias
        monto_final = capital + intereses

        return {
            "capital": capital,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tasa_usada": tasa,
            "monto_final": monto_final
        }