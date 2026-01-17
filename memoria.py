import os
import sqlite3

# Detecta si hay una variable de entorno DB_PATH, si no usa la base local
DB_PATH = os.getenv("DB_PATH", "memoria_agente.db")

class MemoriaAgente:
    """
    Clase para manejar la memoria persistente del agente laboral.
    Usa SQLite para almacenar contratos y conflictos analizados.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._crear_tabla()

    def _crear_tabla(self):
        """Crea la tabla de casos si no existe."""
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
        conn.close()

    def guardar_caso(self, tipo, texto, normativa, jurisprudencia, resultado):
        """Guarda un caso en la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO casos (tipo, texto, normativa, jurisprudencia, resultado)
        VALUES (?, ?, ?, ?, ?)
        """, (tipo, texto, normativa, jurisprudencia, resultado))
        conn.commit()
        conn.close()

    def buscar_similares(self, query):
        """
        Busca casos previos que contengan la query en el texto.
        Retorna una lista de tuplas con (texto, normativa, jurisprudencia, resultado).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT texto, normativa, jurisprudencia, resultado
        FROM casos
        WHERE texto LIKE ?
        """, (f"%{query}%",))
        resultados = cursor.fetchall()
        conn.close()
        return resultados