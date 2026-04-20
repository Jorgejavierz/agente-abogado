# legal_agent.py

import json
import unicodedata
import requests
from openai import OpenAI

# Configuración y módulos internos
from backend.config import OPENAI_API_KEY, MODEL_NAME, FAISS_SERVER
from backend.juris_search import Jurisprudencia
from backend.prompt import LABOR_LAWYER_PROMPT
from backend.core.formatter import ResponseFormatter
from backend.core.context_builder import ContextBuilder


class LaborLawyerAgent:
    """
    Agente jurídico especializado en derecho argentino.
    Integra:
    - FAISS
    - Jurisprudencia
    - Doctrina
    - Casos guardados
    - Memoria del agente
    - Prompt jurídico
    - ContextBuilder
    - ResponseFormatter
    """

    def __init__(self, db, llm_client=None):
        self.db = db
        self.llm_client = llm_client or OpenAI(api_key=OPENAI_API_KEY)
        self.buscador = Jurisprudencia()
        self.context_builder = ContextBuilder()

    # ============================================================
    # Utilidades
    # ============================================================
    def normalizar(self, texto: str) -> str:
        texto = texto.lower()
        return "".join(
            c for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

    # ============================================================
    # FAISS
    # ============================================================
    def guardar_en_faiss(self, texto: str, respuesta: str):
        try:
            requests.post(
                f"{FAISS_SERVER}/guardar",
                json={"texto": texto, "respuesta": respuesta},
                timeout=10
            )
        except Exception as e:
            print(f"Error al guardar en FAISS: {e}")

    def buscar_en_faiss(self, texto: str, k: int = 5):
        try:
            resp = requests.get(
                f"{FAISS_SERVER}/buscar",
                params={"texto": texto, "k": k},
                timeout=10
            )
            return resp.json().get("resultados", [])
        except Exception as e:
            print(f"Error al buscar en FAISS: {e}")
            return []

    # ============================================================
    # Explicación doctrinal
    # ============================================================
    def explicar_concepto(self, texto: str) -> dict:
        antecedentes = self.buscar_en_faiss(texto)
        if antecedentes:
            return {
                "explicacion": f"Se encontraron {len(antecedentes)} antecedentes similares en FAISS.",
                "fuente": "Base FAISS local",
                "antecedentes": antecedentes,
            }

        fallos = self.buscador.buscar_fallos(consulta=texto, top_k=3)
        if fallos:
            f0 = fallos[0]
            fuente = f"{f0.get('tribunal', 'Tribunal no especificado')} - {f0.get('fecha', 'Fecha no disponible')}"
            return {
                "explicacion": f"Se hallaron {len(fallos)} antecedentes jurisprudenciales.",
                "fuente": fuente,
                "antecedentes": fallos,
            }

        return {
            "explicacion": "No se encontraron antecedentes documentales claros.",
            "fuente": "Sin fuente disponible",
            "antecedentes": [],
        }

    # ============================================================
    # Clasificación simple
    # ============================================================
    def _clasificar(self, texto: str) -> str:
        t = texto.lower()
        if "contrato" in t:
            return "Revisión de contrato"
        if "conflicto" in t or "despido" in t:
            return "Conflicto laboral"
        return "Consulta general"

    # ============================================================
    # Lógica principal
    # ============================================================
    def responder(self, texto: str) -> dict:
        """
        Flujo completo:
        1. Clasificación
        2. FAISS
        3. Jurisprudencia
        4. Doctrina
        5. Historial + Casos (DB)
        6. Construcción de contexto
        7. Prompt jurídico
        8. LLM
        9. Formateo
        10. Guardado en memoria y casos
        """

        clasificacion = self._clasificar(texto)
        antecedentes_faiss = self.buscar_en_faiss(texto)
        fallos_relacionados = self.buscador.buscar_fallos(consulta=texto, top_k=5)
        doctrina = self.explicar_concepto(texto)

        historial = self.db.listar_memoria(limit=5)
        casos = self.db.listar_casos(limit=5)

        contexto = self.context_builder.construir_contexto(
            historial=historial,
            casos=casos
        )

        prompt_final = LABOR_LAWYER_PROMPT.format(
            historial=contexto["historial"],
            casos=contexto["casos"]
        ) + f"\n\n=== CONSULTA DEL USUARIO ===\n{texto}\n"

        # LLM
        informe = None
        try:
            resp = self.llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt_final},
                    {"role": "user", "content": texto},
                ],
                temperature=0.2,
                max_tokens=1500
            )
            informe = resp.choices[0].message.content
        except Exception as e:
            print(f"Error al generar informe narrativo: {e}")

        informe = ResponseFormatter.formatear_respuesta(informe or "")

        # Guardar memoria
        self.db.guardar_memoria(
            tipo=clasificacion,
            texto=texto,
            resultado=informe,
            fallos_relacionados=fallos_relacionados
        )

        # Guardar caso si corresponde
        if clasificacion in ["Revisión de contrato", "Conflicto laboral"]:
            self.db.guardar_caso(
                tipo=clasificacion,
                texto=texto,
                normativa="Normativa aplicable pendiente de extracción.",
                jurisprudencia=json.dumps(fallos_relacionados, ensure_ascii=False),
                resultado=informe
            )

        return {
            "consulta": texto,
            "clasificacion": clasificacion,
            "explicacion_doctrinal": doctrina["explicacion"],
            "fuente_doctrina": doctrina["fuente"],
            "fallos_relacionados": fallos_relacionados,
            "antecedentes_faiss": antecedentes_faiss,
            "informe": informe,
            "conclusion": (
                "Este informe es una aproximación automatizada basada únicamente en el contexto disponible. "
                "No reemplaza la revisión jurídica especializada."
            )
        }
