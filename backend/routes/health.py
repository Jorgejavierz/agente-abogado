# routes/health.py

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """
    Endpoint raíz de la API.
    """
    return {"mensaje": "Agente Abogado Laboral API en funcionamiento ✅"}


@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud.
    """
    return {
        "status": "ok",
        "detalle": "La API está operativa y lista para recibir solicitudes."
    }
