# juris_search.py

class Jurisprudencia:
    """
    Clase encargada de manejar la base de jurisprudencia.
    Permite agregar, listar y eliminar fallos.
    """

    def __init__(self):
        self.fallos = []

    def agregar_fallo(self, titulo: str, texto: str, tema: str, tribunal: str, fecha: str, link: str = None):
        fallo = {
            "titulo": titulo,
            "texto": texto,
            "tema": tema,
            "tribunal": tribunal,
            "fecha": fecha,
            "link": link
        }
        self.fallos.append(fallo)

    def listar_fallos(self):
        return self.fallos

    def eliminar_fallo(self, titulo: str):
        for fallo in self.fallos:
            if fallo["titulo"] == titulo:
                self.fallos.remove(fallo)
                return
        raise ValueError(f"No se encontró un fallo con el título: {titulo}")