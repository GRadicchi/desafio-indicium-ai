import os
import pandas as pd
import matplotlib.pyplot as plt
import logging
from sqlalchemy import text
from langchain_core.tools import tool
from typing import Dict
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.database.client import get_db_engine

@tool
def generate_srag_charts(reference_date: str) -> Dict[str, str]:
    """
    Gera gráficos de casos semanais (últimos 30 dias) e mensais (últimos 12 meses) de SRAG.
    
    Args:
        reference_date (str): Data de referência no formato YYYY-MM-DD.
        
    Returns:
        Dict: Dicionário contendo os caminhos dos arquivos de imagem gerados ou erro.
    """
    engine = get_db_engine()
    ref_dt = datetime.strptime(reference_date, "%Y-%m-%d")
    
    start_30_days = (ref_dt - relativedelta(days=30)).strftime("%Y-%m-%d")
    start_12_months = (ref_dt - relativedelta(months=12)).strftime("%Y-%m-%d")
    
    output_dir = "reports/images"
    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    try:
        with engine.connect() as conn:
            logging.info("Gerando gráfico semanal...")
            query_weekly = text("""
                SELECT 
                    date_trunc('week', to_date("DT_NOTIFIC", 'DD/MM/YYYY')) as data, 
                    COUNT(*) as casos
                FROM srag_dados
                WHERE to_date("DT_NOTIFIC", 'DD/MM/YYYY') >= :start_date::date 
                  AND to_date("DT_NOTIFIC", 'DD/MM/YYYY') <= :end_date::date
                GROUP BY 1
                ORDER BY 1
            """)
            
            df_weekly = pd.read_sql(
                query_weekly, 
                conn, 
                params={"start_date": start_30_days, "end_date": reference_date}
            )
            
            if not df_weekly.empty:
                plt.figure(figsize=(10, 5))
                plt.plot(df_weekly['data'], df_weekly['casos'], marker='o', linestyle='-', color='#1f77b4')
                plt.title('Casos Semanais de SRAG (Últimos 30 Dias)')
                plt.xlabel('Semana')
                plt.ylabel('Número de Casos')
                plt.xticks(rotation=45)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                daily_path = os.path.join(output_dir, "casos_semanais_30d.png")
                plt.savefig(daily_path)
                plt.close()
                paths["grafico_semanal"] = daily_path

            logging.info("Gerando gráfico mensal...")
            query_monthly = text("""
                SELECT 
                    date_trunc('month', to_date("DT_NOTIFIC", 'DD/MM/YYYY')) as mes, 
                    COUNT(*) as casos
                FROM srag_dados
                WHERE to_date("DT_NOTIFIC", 'DD/MM/YYYY') >= :start_date::date 
                  AND to_date("DT_NOTIFIC", 'DD/MM/YYYY') <= :end_date::date
                GROUP BY 1
                ORDER BY 1
            """)
            
            df_monthly = pd.read_sql(
                query_monthly, 
                conn, 
                params={"start_date": start_12_months, "end_date": reference_date}
            )
            
            if not df_monthly.empty:
                plt.figure(figsize=(10, 5))
                plt.bar(df_monthly['mes'].astype(str), df_monthly['casos'], color='#ff7f0e')
                plt.title('Casos Mensais de SRAG (Últimos 12 Meses)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                monthly_path = os.path.join(output_dir, "casos_mensais_12m.png")
                plt.savefig(monthly_path)
                plt.close()
                paths["grafico_mensal"] = monthly_path

            logging.info("Gráficos gerados com sucesso.")
            return paths

    except Exception as e:
        logging.error(f"Erro na tool de gráficos: {e}")
        return {"error": "Falha na geração de gráficos."}