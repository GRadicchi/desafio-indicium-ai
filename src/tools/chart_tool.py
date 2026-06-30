import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text
from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Importando a conexão com o banco
from database.client import get_db_engine

@tool
def generate_srag_charts(reference_date: str) -> Dict[str, str]:
    """
    Gera gráficos de casos diários (últimos 30 dias) e mensais (últimos 12 meses) de SRAG.
    
    Args:
        reference_date (str): A data de referência para o cálculo do período (formato YYYY-MM-DD).
                              Normalmente é a data atual ou a data mais recente da base de dados.
        
    Returns:
        Dict: Um dicionário contendo os caminhos dos arquivos de imagem gerados.
    """
    engine = get_db_engine()
    
    # 1. Definir os intervalos de tempo baseados na data de referência
    ref_dt = datetime.strptime(reference_date, "%Y-%m-%d")
    
    start_30_days = (ref_dt - relativedelta(days=30)).strftime("%Y-%m-%d")
    start_12_months = (ref_dt - relativedelta(months=12)).strftime("%Y-%m-%d")
    
    # Garantir que o diretório de imagens existe
    output_dir = "reports/images"
    os.makedirs(output_dir, exist_ok=True)
    
    paths = {}

    try:
        with engine.connect() as conn:
            # ---------------------------------------------------------
            # Gráfico 1: Casos Diários (Últimos 30 dias)
            # ---------------------------------------------------------
            query_daily = text("""
                SELECT "DT_NOTIFIC" as data, COUNT(*) as casos
                FROM srag_dados
                WHERE "DT_NOTIFIC" BETWEEN :start_date AND :end_date
                GROUP BY "DT_NOTIFIC"
                ORDER BY "DT_NOTIFIC"
            """)
            
            df_daily = pd.read_sql(query_daily, conn, params={"start_date": start_30_days, "end_date": reference_date})
            
            if not df_daily.empty:
                df_daily['data'] = pd.to_datetime(df_daily['data'])
                
                plt.figure(figsize=(10, 5))
                plt.plot(df_daily['data'], df_daily['casos'], marker='o', linestyle='-', color='#1f77b4')
                plt.title('Casos Diários de SRAG (Últimos 30 Dias)')
                plt.xlabel('Data')
                plt.ylabel('Número de Casos')
                plt.xticks(rotation=45)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                daily_path = os.path.join(output_dir, "casos_diarios_30d.png")
                plt.savefig(daily_path)
                plt.close()
                paths["grafico_diario"] = daily_path
            else:
                paths["grafico_diario"] = "Sem dados para gerar gráfico diário."

            # ---------------------------------------------------------
            # Gráfico 2: Casos Mensais (Últimos 12 meses)
            # ---------------------------------------------------------
            # No PostgreSQL, usamos TO_CHAR e DATE_TRUNC para agrupar por mês
            query_monthly = text("""
                SELECT TO_CHAR(DATE_TRUNC('month', "DT_NOTIFIC"), 'YYYY-MM') as mes, COUNT(*) as casos
                FROM srag_dados
                WHERE "DT_NOTIFIC" BETWEEN :start_date AND :end_date
                GROUP BY DATE_TRUNC('month', "DT_NOTIFIC")
                ORDER BY mes
            """)
            
            df_monthly = pd.read_sql(query_monthly, conn, params={"start_date": start_12_months, "end_date": reference_date})
            
            if not df_monthly.empty:
                plt.figure(figsize=(10, 5))
                plt.bar(df_monthly['mes'], df_monthly['casos'], color='#ff7f0e')
                plt.title('Casos Mensais de SRAG (Últimos 12 Meses)')
                plt.xlabel('Mês')
                plt.ylabel('Número de Casos')
                plt.xticks(rotation=45)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                monthly_path = os.path.join(output_dir, "casos_mensais_12m.png")
                plt.savefig(monthly_path)
                plt.close()
                paths["grafico_mensal"] = monthly_path
            else:
                paths["grafico_mensal"] = "Sem dados para gerar gráfico mensal."

        return paths

    except Exception as e:
        return {"error": f"Erro ao gerar gráficos: {str(e)}"}