# test/test_agent.py
import os
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

    assert "Contrato recibido" in resultado
    # Verificamos que se guardó en memoria
    casos = agente.memoria.buscar_similares("lunes a viernes")
    assert len(casos) > 0

def test_analizar_conflicto(agente):
    conflicto = "Despido sin causa con reclamo de horas extras"
    resultado = agente.analizar_conflicto(conflicto)

    assert "caso" in resultado
    assert resultado["caso"] == conflicto
    assert "fallos_relacionados" in resultado
    assert isinstance(resultado["fallos_relacionados"], list)
    assert "casos_previos" in resultado

def test_memoria_persistencia(tmp_path):
    # Creamos una base de datos real en disco
    db_file = tmp_path / "memoria_test.db"
    memoria = MemoriaAgente(db_path=str(db_file))

    memoria.guardar_caso(
        tipo="conflicto",
        texto="Reclamo por horas extras",
        normativa="Art. 201 LCT",
        jurisprudencia="N/A",
        resultado="Pendiente"
    )

    resultados = memoria.buscar_similares("horas extras")
    assert len(resultados) == 1
    assert "horas extras" in resultados[0][0]

def test_jurisprudencia_integration(agente):
    # Probamos que la clase Jurisprudencia esté integrada
    resultado = agente.analizar_conflicto("despido")
    assert "fallos_relacionados" in resultado
    # No garantizamos resultados reales, pero debe devolver una lista
    assert isinstance(resultado["fallos_relacionados"], list)