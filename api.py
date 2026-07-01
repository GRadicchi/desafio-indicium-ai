import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from datetime import date
from src.agent.graph import app as agent_app
from src.tools.chart_tool import generate_srag_charts

load_dotenv()

app = FastAPI(title="SRAG Agent API")

class QueryRequest(BaseModel):
    query: str = """Você é um analista de dados especialista em saúde pública. 
                    Gere um relatório executivo estruturado em Markdown sobre o cenário da SRAG no Brasil.

                    OBRIGAÇÕES DO RELATÓRIO:
                    1. MÉTRICAS: Acione a ferramenta de métricas no banco de dados e extraia explicitamente: Taxa de aumento de casos, Taxa de mortalidade, Taxa de ocupação de UTI e Taxa de vacinação.
                    2. GRÁFICOS: Você DEVE acionar a ferramenta `generate_srag_charts`. É ESTRITAMENTE PROIBIDO inventar URLs ou usar imagens da internet. Use apenas o caminho local do arquivo que a ferramenta te retornar (ex: ![Gráfico](caminho_local.png)).
                    3. NOTÍCIAS: Busque notícias recentes.

                    Cruze as informações e apresente os resultados de forma clara e direta."""

@app.post("/api/v1/report")
async def generate_report(request: QueryRequest):
    try:
        inputs = {"messages": [HumanMessage(content=request.query)]}
        final_state = agent_app.invoke(inputs)
        return {"status": "success", "relatorio": final_state["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/charts/generate")
async def trigger_chart_generation():
    resultado = generate_srag_charts.invoke({"reference_date": date.today().isoformat()})
    if isinstance(resultado, dict) and "error" in resultado:
        raise HTTPException(status_code=500, detail=resultado["error"])
    return {"status": "success", "arquivos": resultado}

@app.get("/api/v1/charts/{chart_name}")
async def get_chart(chart_name: str):
    file_path = f"reports/images/{chart_name}.png"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Gráfico não encontrado")