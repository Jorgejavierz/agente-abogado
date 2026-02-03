# ver_memoria.py
import sqlite3
from config import DB_PATH  # usamos la ruta de la base desde config.py

def ver_ultimos_memoria(db_path: str = DB_PATH, limite: int = 5) -> None:
    """
    Muestra los últimos registros guardados en la tabla memoria.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, tipo, texto, resultado, fallos_relacionados, timestamp
        FROM memoria
        ORDER BY id DESC
        LIMIT ?
        """, (limite,))
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error accediendo a la base de datos: {e}")
        rows = []
    finally:
        conn.close()

    # Mostrar resultados en formato legible
    if rows:
        print(f"\nÚltimos {len(rows)} registros guardados en memoria:\n")
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Tipo: {row[1]}")
            print(f"Texto/Descripción: {row[2]}")
            print(f"Resultado: {row[3]}")
            print(f"Fallos relacionados: {row[4]}")
            print(f"Timestamp: {row[5]}")
            print("-" * 50)
    else:
        print("\nNo hay registros guardados en la memoria.\n")

if __name__ == "__main__":
    ver_ultimos_memoria()