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
    query: str = """Você é um analista especialista. Gere um relatório estruturado de SRAG. 
    Use a ferramenta de métricas, a ferramenta `generate_srag_charts` (não invente URLs!) e busque notícias."""

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