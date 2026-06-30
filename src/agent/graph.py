import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Importando nossos componentes
from agent.state import AgentState
from tools import get_srag_metrics, generate_srag_charts, get_srag_news
from utils.config import load_config # Ajuste conforme necessário

# 1. Configurar o LLM e as Ferramentas
llm = ChatOpenAI(model="gpt-4o", temperature=0) # gpt-4o é recomendado para tarefas de agentes
tools = [get_srag_metrics, generate_srag_charts, get_srag_news]
llm_with_tools = llm.bind_tools(tools)

# 2. Definir os nós (Nodes) do Grafo
def call_model(state: AgentState):
    """Nó do LLM: decide se deve chamar uma ferramenta ou responder."""
    system_prompt = SystemMessage(content="""
        Você é um Engenheiro de IA especializado em saúde pública. 
        Sua tarefa é gerar relatórios de SRAG baseados em dados reais.
        - Sempre use as ferramentas disponíveis para buscar métricas, notícias e gerar gráficos.
        - Seja técnico, preciso e baseie-se nos dados fornecidos pelo banco.
        - Ao final, compile tudo em um relatório claro e estruturado.
    """)
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# O ToolNode executa as funções que o LLM decide chamar
tool_node = ToolNode(tools)

# 3. Definir o Grafo
workflow = StateGraph(AgentState)

# Adicionar nós
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Adicionar arestas (Edges)
# O fluxo começa no agente
workflow.set_entry_point("agent")

# Se o LLM decidir usar uma ferramenta, o LangGraph direciona para 'tools'
from langgraph.prebuilt import tools_condition
workflow.add_conditional_edges("agent", tools_condition)

# Depois que a ferramenta retorna, volta para o agente para ele avaliar
workflow.add_edge("tools", "agent")

# Compilar o grafo
app = workflow.compile()