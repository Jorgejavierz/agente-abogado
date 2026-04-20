import os
import requests
from PyPDF2 import PdfReader

FAISS_SERVER = "http://127.0.0.1:8081"  # dirección de tu servidor FAISS

def cargar_pdf_en_faiss(pdf_path, chunk_size=400):
    # Validar archivo
    if not os.path.exists(pdf_path):
        print(f"❌ El archivo no existe: {pdf_path}")
        return

    # Leer PDF
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"❌ Error al abrir el PDF: {e}")
        return

    texto_total = ""
    for i, page in enumerate(reader.pages):
        try:
            texto = page.extract_text()
            if texto:
                texto_total += texto + "\n"
            else:
                print(f"⚠ Página {i+1} sin texto detectable.")
        except Exception as e:
            print(f"⚠ Error leyendo página {i+1}: {e}")

    if not texto_total.strip():
        print("❌ No se pudo extraer texto del PDF.")
        return

    # Limpiar texto
    texto_total = " ".join(texto_total.split())

    # Dividir en fragmentos
    palabras = texto_total.split()
    fragmentos = [
        " ".join(palabras[i:i+chunk_size])
        for i in range(0, len(palabras), chunk_size)
    ]

    print(f"📚 Total de fragmentos a enviar: {len(fragmentos)}")

    # Guardar cada fragmento en FAISS
    for idx, frag in enumerate(fragmentos, start=1):
        if not frag.strip():
            print(f"⚠ Fragmento {idx} vacío, se omite.")
            continue

        payload = {"texto": frag, "respuesta": f"Fragmento {idx} del libro"}

        try:
            r = requests.post(
                f"{FAISS_SERVER}/guardar",
                json=payload,
                timeout=10
            )
            if r.status_code == 200:
                print(f"✅ Fragmento {idx} guardado.")
            else:
                print(f"❌ Error en fragmento {idx}: {r.text}")
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout al enviar fragmento {idx}.")
        except Exception as e:
            print(f"❌ Error de conexión en fragmento {idx}: {e}")

    print("✔ Carga completa en FAISS.")

if __name__ == "__main__":
    cargar_pdf_en_faiss("libro_despido_laboral.pdf")
