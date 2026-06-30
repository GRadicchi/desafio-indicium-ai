import pandas as pd
from sqlalchemy import text
from langchain_core.tools import tool
from typing import Dict, Any
from datetime import datetime, timedelta

# Importando a conexão com o banco
from database.client import get_db_engine

@tool
def get_srag_metrics(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Consulta a base de dados para calcular as métricas de Síndrome Respiratória Aguda Grave (SRAG)
    no período especificado.
    
    Args:
        start_date (str): Data de início da análise (formato YYYY-MM-DD).
        end_date (str): Data final da análise (formato YYYY-MM-DD).
        
    Returns:
        Dict: Dicionário contendo o total de casos, taxa de aumento, taxa de mortalidade, 
              taxa de ocupação de UTI e taxa de vacinação.
    """
    engine = get_db_engine()
    
    # 1. Calcular o período anterior para a taxa de aumento
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end_dt - start_dt
    
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - delta
    
    prev_start_date = prev_start_dt.strftime("%Y-%m-%d")
    prev_end_date = prev_end_dt.strftime("%Y-%m-%d")

    # 2. Query com as colunas reais do Dicionário SIVEP-Gripe
    current_period_query = text("""
        SELECT 
            COUNT(*) as total_casos,
            SUM(CASE WHEN "EVOLUCAO" = '2' THEN 1 ELSE 0 END) as total_obitos,
            SUM(CASE WHEN "UTI" = '1' THEN 1 ELSE 0 END) as total_uti,
            SUM(CASE WHEN "VACINA_COV" = '1' THEN 1 ELSE 0 END) as total_vacinados
        FROM srag_dados
        WHERE "DT_NOTIFIC" BETWEEN :start_date AND :end_date
    """)

    # 3. Query para o período anterior
    previous_period_query = text("""
        SELECT COUNT(*) as total_casos_anterior
        FROM srag_dados
        WHERE "DT_NOTIFIC" BETWEEN :prev_start AND :prev_end
    """)

    try:
        with engine.connect() as conn:
            current_result = conn.execute(current_period_query, {
                "start_date": start_date, 
                "end_date": end_date
            }).fetchone()
            
            prev_result = conn.execute(previous_period_query, {
                "prev_start": prev_start_date, 
                "prev_end": prev_end_date
            }).fetchone()

        total_casos = current_result.total_casos or 0
        total_obitos = current_result.total_obitos or 0
        total_uti = current_result.total_uti or 0
        total_vacinados = current_result.total_vacinados or 0
        total_casos_anterior = prev_result.total_casos_anterior or 0

        # 4. Cálculo das Métricas
        taxa_mortalidade = (total_obitos / total_casos * 100) if total_casos > 0 else 0.0
        taxa_ocupacao_uti = (total_uti / total_casos * 100) if total_casos > 0 else 0.0
        taxa_vacinacao = (total_vacinados / total_casos * 100) if total_casos > 0 else 0.0
        
        if total_casos_anterior > 0:
            taxa_aumento = ((total_casos - total_casos_anterior) / total_casos_anterior) * 100
        else:
            taxa_aumento = 100.0 if total_casos > 0 else 0.0

        return {
            "periodo_analisado": f"{start_date} a {end_date}",
            "total_casos": total_casos,
            "taxa_aumento_casos": f"{taxa_aumento:.2f}%",
            "taxa_mortalidade": f"{taxa_mortalidade:.2f}%",
            "taxa_ocupacao_uti": f"{taxa_ocupacao_uti:.2f}%",
            "taxa_vacinacao_covid": f"{taxa_vacinacao:.2f}%"
        }

    except Exception as e:
        return {"error": f"Falha ao executar consulta na base de dados: {str(e)}"}