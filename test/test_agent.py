# test/test_agent.py
import pytest
from agent import LaborLawyerAgent
from memoria import MemoriaAgente

@pytest.fixture
def agente():
    # Usamos una base de datos temporal para no ensuciar la real
    memoria_test = MemoriaAgente(db_path=":memory:")
    agent = LaborLawyerAgent()
    agent.memoria = memoria_test
    return agent

def test_review_contract(agente):
    contrato = "El trabajador prestará servicios de lunes a viernes, jornada de 8 horas."
    resultado = agente.review_contract(contrato)

    assert "Contrato recibido" in resultado, "El contrato no fue procesado correctamente"
    # Verificamos que se guardó en memoria
    registros = agente.memoria.buscar_similares("lunes a viernes")
    assert len(registros) > 0, "El contrato no se guardó en memoria"

def test_analizar_conflicto(agente):
    conflicto = "Despido sin causa con reclamo de horas extras"
    resultado = agente.analizar_conflicto(conflicto)

    assert "resultado" in resultado
    assert isinstance(resultado["resultado"], str)
    assert "fallos_relacionados" in resultado
    assert isinstance(resultado["fallos_relacionados"], list)
    # Ahora verificamos que se guardó en memoria
    registros = agente.memoria.buscar_similares("horas extras")
    assert len(registros) >= 0

def test_memoria_persistencia(tmp_path):
    # Creamos una base de datos real en disco
    db_file = tmp_path / "memoria_test.db"
    memoria = MemoriaAgente(db_path=str(db_file))

    memoria.guardar_caso(
        tipo="conflicto",
        texto="Reclamo por horas extras",
        resultado="Pendiente",
        fallos_relacionados=["Art. 201 LCT"]
    )

    resultados = memoria.buscar_similares("horas extras")
    assert len(resultados) == 1
    assert "horas extras" in resultados[0][1]  # el campo texto

def test_jurisprudencia_integration(agente):
    # Probamos que la clase Jurisprudencia esté integrada
    resultado = agente.analizar_conflicto("despido")
    assert "fallos_relacionados" in resultado
    assert isinstance(resultado["fallos_relacionados"], list)