import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Importando o grafo compilado da nossa arquitetura
from src.agent.graph import app

def main():
    # Carrega as chaves de API (OpenAI, Tavily) e Database URL
    load_dotenv()
    
    print("==================================================")
    print("Iniciando o Orquestrador de Relatórios SRAG...")
    print("==================================================\n")
    
    # O prompt do usuário que aciona o agente. 
    # Passamos datas fixas como exemplo para garantir que bata com os dados do Supabase.
    query = """
    Você é o analista responsável. Gere um relatório estruturado em Markdown sobre o cenário atual 
    da Síndrome Respiratória Aguda Grave (SRAG) no Brasil. 
    
    Siga estes passos obrigatórios:
    1. Busque as métricas exatas do banco de dados para o período entre '2024-04-01' e '2024-04-30'.
    2. Gere os gráficos de casos (diários e mensais) usando '2024-04-30' como data de referência e 
       inclua os caminhos das imagens no relatório.
    3. Busque notícias recentes sobre 'aumento de casos de SRAG e vírus respiratórios' para 
       contextualizar as métricas numéricas.
    
    Ao final, entregue o relatório completo, cruzando os dados quantitativos com as notícias.
    """
    
    # O estado inicial contém apenas a mensagem humana
    inputs = {"messages": [HumanMessage(content=query)]}
    
    print("Iniciando ciclo de execução (Raciocínio -> Ferramentas -> Resposta)...\n")
    
    # Utilizamos o método .stream() para auditar passo a passo as decisões do agente.
    # Isso cobre o requisito de "Governança e Transparência / Mecanismos de auditoria".
    ultima_mensagem = None
    
    for output in app.stream(inputs, stream_mode="updates"):
        for node_name, state_update in output.items():
            print(f">>> [Auditoria] Nó executado: '{node_name}'")
            
            ultima_mensagem = state_update["messages"][-1]
            
            # Se o nó for o agente e ele decidiu usar uma ferramenta
            if node_name == "agent" and hasattr(ultima_mensagem, 'tool_calls') and ultima_mensagem.tool_calls:
                ferramentas_chamadas = [t['name'] for t in ultima_mensagem.tool_calls]
                print(f"    Decisão: O agente optou por acionar as ferramentas: {ferramentas_chamadas}\n")
            
            # Se o nó for a execução das ferramentas
            elif node_name == "tools":
                print(f"    Resultado: Retorno da ferramenta '{ultima_mensagem.name}' capturado com sucesso.\n")
    
    print("==================================================")
    print("RELATÓRIO FINAL GERADO:")
    print("==================================================\n")
    
    # Imprime a resposta final gerada pelo LLM
    if ultima_mensagem:
        print(ultima_mensagem.content)

if __name__ == "__main__":
    main()