import sqlite3

def ver_ultimos_casos(db_path="memoria_agente.db", limite=5):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Traer los últimos 'limite' casos ordenados por ID descendente
    cursor.execute("""
    SELECT id, tipo, texto, normativa, jurisprudencia, resultado
    FROM casos
    ORDER BY id DESC
    LIMIT ?
    """, (limite,))
    rows = cursor.fetchall()
    conn.close()

    # Mostrar resultados en formato legible
    print(f"\nÚltimos {len(rows)} casos guardados:\n")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Tipo: {row[1]}")
        print(f"Texto/Descripción: {row[2]}")
        print(f"Normativa: {row[3]}")
        print(f"Jurisprudencia: {row[4]}")
        print(f"Resultado: {row[5]}")
        print("-" * 50)

if __name__ == "__main__":
    ver_ultimos_casos()