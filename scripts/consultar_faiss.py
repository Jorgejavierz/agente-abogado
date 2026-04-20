import requests

FAISS_SERVER = "http://127.0.0.1:8081"

def preguntar(texto, k=3):
    if not texto or not texto.strip():
        print("❌ El texto de consulta está vacío.")
        return

    try:
        resp = requests.get(
            f"{FAISS_SERVER}/buscar",
            params={"texto": texto, "k": k},
            timeout=10
        )
    except requests.exceptions.Timeout:
        print("⏳ Timeout: el servidor FAISS no respondió a tiempo.")
        return
    except Exception as e:
        print(f"❌ Error de conexión con FAISS: {e}")
        return

    if resp.status_code != 200:
        print(f"❌ Error en la consulta ({resp.status_code}): {resp.text}")
        return

    try:
        data = resp.json()
    except Exception:
        print("❌ La respuesta del servidor no es JSON válido.")
        return

    resultados = data.get("resultados")
    if not resultados:
        print("⚠ No se encontraron resultados.")
        return

    print(f"\n🔎 Consulta: {texto}")
    print(f"📌 Resultados encontrados: {len(resultados)}")

    for i, r in enumerate(resultados, 1):
        texto_res = r.get("texto", "")[:200]
        respuesta = r.get("respuesta", "Sin respuesta")

        print(f"\n--- Resultado {i} ---")
        print(f"📝 Texto: {texto_res}...")
        print(f"💬 Respuesta: {respuesta}")

if __name__ == "__main__":
    preguntar("Explicame el despido sin causa")
    preguntar("Qué dice sobre fraude laboral")
