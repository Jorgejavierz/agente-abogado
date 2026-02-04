import sqlite3
import json
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
        """Crea la tabla de memoria si no existe."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                texto TEXT,
                resultado TEXT,
                fallos_relacionados TEXT,
                timestamp TEXT
            )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creando tabla de memoria: {e}")
        finally:
            conn.close()

    def guardar_caso(self, tipo: str, texto: str, resultado: str, fallos_relacionados: list) -> None:
        """Guarda un caso en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
            VALUES (?, ?, ?, ?, datetime('now'))
            """, (tipo, texto, resultado, json.dumps(fallos_relacionados)))
            conn.commit()
        except Exception as e:
            print(f"Error guardando caso en memoria: {e}")
        finally:
            conn.close()

    def buscar_similares(self, query: str):
        """
        Busca registros previos que contengan la query en el texto.
        Retorna una lista de tuplas con (id, tipo, texto, resultado, fallos_relacionados, timestamp).
        """
        resultados = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, tipo, texto, resultado, fallos_relacionados, timestamp
            FROM memoria
            WHERE texto LIKE ?
            """, (f"%{query}%",))
            resultados = cursor.fetchall()
        except Exception as e:
            print(f"Error buscando registros similares: {e}")
        finally:
            conn.close()
        return resultados