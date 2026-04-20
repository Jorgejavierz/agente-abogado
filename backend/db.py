import os
import sqlite3
import json

# Leer DB_PATH directamente del entorno para evitar import circular
DB_PATH = os.getenv("DB_PATH", "memoria_agente.db")


class MemoriaDB:
    """
    Módulo profesional de persistencia en SQLite.
    Maneja:
    - feedback
    - memoria del agente
    - casos jurídicos
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ============================================================
    # Inicialización de tablas
    # ============================================================
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabla de feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consulta TEXT,
                    calificacion INTEGER,
                    comentario TEXT,
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

            # Tabla de casos jurídicos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS casos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT,
                    texto TEXT,
                    normativa TEXT,
                    jurisprudencia TEXT,
                    resultado TEXT,
                    timestamp TEXT
                )
            """)

            conn.commit()

    # ============================================================
    # Feedback
    # ============================================================
    def guardar_feedback(self, consulta: str, calificacion: int, comentario: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (consulta, calificacion, comentario, timestamp)
                VALUES (?, ?, ?, datetime('now','localtime'))
            """, (consulta, calificacion, comentario))
            conn.commit()

    def listar_feedback(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, consulta, calificacion, comentario, timestamp
                FROM feedback
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # ============================================================
    # Memoria del agente
    # ============================================================
    def guardar_memoria(self, tipo: str, texto: str, resultado: str, fallos_relacionados: list):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memoria (tipo, texto, resultado, fallos_relacionados, timestamp)
                VALUES (?, ?, ?, ?, datetime('now','localtime'))
            """, (tipo, texto, resultado, json.dumps(fallos_relacionados)))
            conn.commit()

    def listar_memoria(self, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tipo, texto, resultado, fallos_relacionados, timestamp
                FROM memoria
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

        resultados = []
        for row in rows:
            try:
                fallos = json.loads(row["fallos_relacionados"]) if row["fallos_relacionados"] else []
            except Exception:
                fallos = []

            resultados.append({
                "id": row["id"],
                "tipo": row["tipo"],
                "texto": row["texto"],
                "resultado": row["resultado"],
                "fallos_relacionados": fallos,
                "timestamp": row["timestamp"],
            })

        return resultados

    # ============================================================
    # Casos jurídicos
    # ============================================================
    def guardar_caso(self, tipo: str, texto: str, normativa: str, jurisprudencia: str, resultado: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO casos (tipo, texto, normativa, jurisprudencia, resultado, timestamp)
                VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
            """, (tipo, texto, normativa, jurisprudencia, resultado))
            conn.commit()

    def listar_casos(self, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tipo, texto, normativa, jurisprudencia, resultado, timestamp
                FROM casos
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def obtener_caso(self, caso_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tipo, texto, normativa, jurisprudencia, resultado, timestamp
                FROM casos
                WHERE id = ?
            """, (caso_id,))
            row = cursor.fetchone()

        return dict(row) if row else None

    def eliminar_caso(self, caso_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM casos WHERE id = ?", (caso_id,))
            cambios = conn.total_changes
            conn.commit()

        return cambios > 0
