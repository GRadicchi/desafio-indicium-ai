from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Define o estado do nosso orquestrador LangGraph.
    
    A chave 'messages' utiliza o reducer 'add_messages'. Isto é crucial porque 
    garante que, a cada iteração do agente (por exemplo, quando ele pensa, 
    chama uma tool e recebe a resposta da tool), a nova mensagem é adicionada 
    ao histórico existente, em vez de o substituir.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Se, no futuro, precisarmos de forçar o agente a guardar variáveis 
    # específicas fora do histórico de mensagens (ex: metadata do relatório), 
    # adicionaríamos aqui. Para a nossa arquitetura ReAct/Tool Calling, 
    # o histórico de mensagens é suficiente.