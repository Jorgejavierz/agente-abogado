# db.py

import sqlite3
import json

class MemoriaDB:
    """
    Clase encargada de manejar la persistencia en SQLite
    para feedback y memoria del agente.
    """

    def __init__(self, db_path="memoria_agente.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Crea las tablas si no existen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT,
                util BOOLEAN,
                timestamp TEXT
            )
        """)

        # Tabla de memoria
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
        conn.close()

    # -------------------------------
    # Feedback
    # -------------------------------
    def guardar_feedback(self, texto: str, util: bool, timestamp: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (texto, util, timestamp)
            VALUES (?, ?, ?)
        """, (texto, util, timestamp))
        conn.commit()
        conn.close()

    def listar_feedback(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, texto, util, timestamp FROM feedback ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        return [
            {"id": row[0], "texto": row[1], "util": bool(row[2]), "timestamp": row[3]}
            for row in rows
        ]

    # -------------------------------
    # Memoria
    # -------------------------------
    def guardar_memoria(self, tipo: str, texto: str, resultado: str, fallos_relacionados: list):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
            VALUES (?, ?, ?, ?, datetime('now','localtime'))
        """, (tipo, texto, resultado, json.dumps(fallos_relacionados)))
        conn.commit()
        conn.close()

    def listar_memoria(self, limit: int = 10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, texto, resultado, fallos_relacionados, timestamp
            FROM memoria
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "tipo": row[1],
                "texto": row[2],
                "resultado": row[3],
                "fallos_relacionados": json.loads(row[4]) if row[4] else [],
                "timestamp": row[5],
            }
            for row in rows
        ]