import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Importa o nosso orquestrador LangGraph
from src.agent.graph import app as agent_app

# Carrega as variáveis de ambiente (Chaves de API, Database URL)
load_dotenv()

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="SRAG Agent API",
    description="API do Agente de IA para análise epidemiológica de Síndrome Respiratória Aguda Grave.",
    version="1.0.0"
)

# Define o formato do corpo da requisição (Payload)
class QueryRequest(BaseModel):
    query: str = """Você é um analista de dados especialista em saúde pública. 
Gere um relatório executivo estruturado em Markdown sobre o cenário da SRAG no Brasil.

OBRIGAÇÕES DO RELATÓRIO:
1. MÉTRICAS: Acione a ferramenta de métricas no banco de dados e extraia explicitamente: Taxa de aumento de casos, Taxa de mortalidade, Taxa de ocupação de UTI e Taxa de vacinação.
2. GRÁFICOS: Você DEVE acionar a ferramenta `generate_srag_charts`. É ESTRITAMENTE PROIBIDO inventar URLs ou usar imagens da internet. Use apenas o caminho local do arquivo que a ferramenta te retornar (ex: ![Gráfico](caminho_local.png)).
3. NOTÍCIAS: Busque notícias recentes.

Cruze as informações e apresente os resultados de forma clara e direta."""

# Cria a rota POST que vai acionar o agente
@app.post("/api/v1/report")
async def generate_report(request: QueryRequest):
    try:
        # Prepara o estado inicial (a mensagem do usuário)
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        # O método invoke roda o grafo inteiro até o fim e retorna o estado final
        # Ao contrário do stream(), ele não imprime passo a passo, apenas aguarda o resultado.
        final_state = agent_app.invoke(inputs)
        
        # Extrai o conteúdo da última mensagem (a resposta do LLM)
        relatorio = final_state["messages"][-1].content
        
        return {
            "status": "success",
            "relatorio": relatorio
        }
        
    except Exception as e:
        # Se ocorrer o erro 429 de Quota ou de Timeout, a API devolve um erro claro
        raise HTTPException(status_code=500, detail=str(e))