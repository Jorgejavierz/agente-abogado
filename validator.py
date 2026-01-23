# validator.py
from pydantic import BaseModel, ValidationError

class ContratoInput(BaseModel):
    texto: str

class ConflictoInput(BaseModel):
    descripcion: str

def validar_contrato(data: dict) -> ContratoInput | None:
    """
    Valida que el contrato tenga el campo 'texto' y no esté vacío.
    Retorna un objeto ContratoInput válido o None si falla.
    """
    try:
        contrato = ContratoInput(**data)
        if not contrato.texto.strip():
            raise ValueError("El texto del contrato está vacío")
        return contrato
    except (ValidationError, ValueError) as e:
        print(f"Error validando contrato: {e}")
        return None

def validar_conflicto(data: dict) -> ConflictoInput | None:
    """
    Valida que el conflicto tenga el campo 'descripcion' y no esté vacío.
    Retorna un objeto ConflictoInput válido o None si falla.
    """
    try:
        conflicto = ConflictoInput(**data)
        if not conflicto.descripcion.strip():
            raise ValueError("La descripción del conflicto está vacía")
        return conflicto
    except (ValidationError, ValueError) as e:
        print(f"Error validando conflicto: {e}")
        return None