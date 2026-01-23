# memoria.py
import sqlite3
from config import DB_PATH  # importamos la ruta de la base desde config.py

class MemoriaAgente:
    """
    Clase para manejar la memoria persistente del agente laboral.
    Usa SQLite para almacenar contratos y conflictos analizados.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._crear_tabla()

    def _crear_tabla(self) -> None:
        """Crea la tabla de casos si no existe."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS casos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                texto TEXT,
                normativa TEXT,
                jurisprudencia TEXT,
                resultado TEXT
            )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creando tabla de casos: {e}")
        finally:
            conn.close()

    def guardar_caso(self, tipo: str, texto: str, normativa: str, jurisprudencia: str, resultado: str) -> None:
        """Guarda un caso en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO casos (tipo, texto, normativa, jurisprudencia, resultado)
            VALUES (?, ?, ?, ?, ?)
            """, (tipo, texto, normativa, jurisprudencia, resultado))
            conn.commit()
        except Exception as e:
            print(f"Error guardando caso en memoria: {e}")
        finally:
            conn.close()

    def buscar_similares(self, query: str):
        """
        Busca casos previos que contengan la query en el texto.
        Retorna una lista de tuplas con (texto, normativa, jurisprudencia, resultado).
        """
        resultados = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT texto, normativa, jurisprudencia, resultado
            FROM casos
            WHERE texto LIKE ?
            """, (f"%{query}%",))
            resultados = cursor.fetchall()
        except Exception as e:
            print(f"Error buscando casos similares: {e}")
        finally:
            conn.close()
        return resultados