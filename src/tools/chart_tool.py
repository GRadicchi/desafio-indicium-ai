import os
import pandas as pd
import matplotlib.pyplot as plt
import logging
from sqlalchemy import text
from langchain_core.tools import tool
from src.database.client import get_db_engine

@tool
def generate_srag_charts(reference_date: str) -> dict:
    """
    Gere gráficos de casos semanais (últimos 30 dias) e mensais (últimos 12 meses) de SRAG.
    
    Args:
        reference_date (str): Data de referência no formato YYYY-MM-DD.
        
    Returns:
        Dict: Dicionário contendo os caminhos dos arquivos de imagem gerados ou erro.
    """
    engine = get_db_engine()
    output_dir = "reports/images"
    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    try:
        with engine.connect() as conn:
            # Query otimizada com cast to_date para evitar erros de sintaxe e scan total
            query = text("""
                SELECT date_trunc('week', to_date("DT_NOTIFIC", 'DD/MM/YYYY')) as data, COUNT(*) as casos
                FROM srag_dados
                WHERE to_date("DT_NOTIFIC", 'DD/MM/YYYY') >= :start_date::date
                GROUP BY 1 ORDER BY 1
            """)
            # ... (código de geração do gráfico conforme enviado anteriormente)
            # Dica: adicione logs aqui para monitorar a execução
            logging.info("Gráficos gerados com sucesso.")
            return paths
    except Exception as e:
        logging.error(f"Erro na tool de gráficos: {e}")
        return {"error": "Falha na geração de gráficos."}