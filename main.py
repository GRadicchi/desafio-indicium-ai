import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.agent.graph import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    load_dotenv()
    
    query = """
    Analise o cenário atual da SRAG no Brasil. 
    1. Obtenha métricas de abril de 2024.
    2. Gere gráficos de referência.
    3. Busque notícias recentes para contextualização.
    """
    
    inputs = {"messages": [HumanMessage(content=query)]}
    logging.info("Iniciando execução do Agente...")
    
    for output in app.stream(inputs, stream_mode="updates"):
        for node_name, state_update in output.items():
            logging.info(f"Nó executado: {node_name}")
            
    final_state = app.invoke(inputs)
    logging.info("Relatório final gerado.")
    print(final_state["messages"][-1].content)

if __name__ == "__main__":
    main()