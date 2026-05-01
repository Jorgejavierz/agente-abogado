# backend/main.py

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuración centralizada
from backend.config import db, llm_client, FAISS_SERVER

# Agente jurídico
from backend.legal_agent import LaborLawyerAgent

# Routers (imports explícitos, más seguros)
from backend.routes.health import router as health_router
from backend.routes.analizar import router as analizar_router
from backend.routes.feedback import router as feedback_router
from backend.routes.memoria import router as memoria_router
from backend.routes.chat import router as chat_router
from backend.routes.intereses import router as intereses_router
from backend.routes.casos import router as casos_router

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")


# ============================================================
# Inicializar FastAPI
# ============================================================
app = FastAPI(
    title="Agente Laboral IA",
    version="1.0.0",
    description="Asistente jurídico especializado en derecho laboral argentino."
)


# ============================================================
# CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Podés restringirlo en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Inicializar el agente
# ============================================================
try:
    app.state.agent = LaborLawyerAgent(db=db, llm_client=llm_client)
    logger.info("LaborLawyerAgent inicializado correctamente.")
except Exception as e:
    logger.exception("Error al inicializar LaborLawyerAgent.")


# ============================================================
# Registrar routers
# ============================================================
app.include_router(health_router)
app.include_router(analizar_router)
app.include_router(feedback_router)
app.include_router(memoria_router)
app.include_router(chat_router)
app.include_router(intereses_router)
app.include_router(casos_router)


# ============================================================
# Ejecución local
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, log_level="info")
