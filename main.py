# main.py
from agent import LaborLawyerAgent
from jurisprudencia import Jurisprudencia

def main():
    print("Agente Abogado Laboral inicializado correctamente ✅")

    # Inicializar agente
    agent = LaborLawyerAgent()

    # Ejemplo: analizar un conflicto laboral
    caso = "Despido sin causa con reclamo de horas extras"
    informe = agent.analizar_conflicto(caso)

    # Buscar jurisprudencia relacionada
    buscador = Jurisprudencia()
    fallos = buscador.buscar_fallos("despido")

    print("\n--- Informe del agente ---\n")
    print(informe)

    print("\n--- Jurisprudencia relacionada ---\n")
    if not fallos:
        print("No se encontraron fallos relacionados.")
    else:
        for fallo in fallos:
            print(f"- {fallo['titulo']} → {fallo['link']}")

if __name__ == "__main__":
    main()