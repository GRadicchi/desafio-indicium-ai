from langchain_core.tools import tool
from typing import Dict, Any

@tool
def get_srag_metrics(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Consulta o banco de dados para calcular as métricas de Síndrome Respiratória Aguda Grave (SRAG).
    
    Args:
        start_date (str): Data de início da análise (formato YYYY-MM-DD).
        end_date (str): Data final da análise (formato YYYY-MM-DD).
        
    Returns:
        Dict: Dicionário contendo a taxa de aumento de casos, taxa de mortalidade, 
              taxa de ocupação de UTI e taxa de vacinação.
    """
    
    # TODO: Implementar a conexão com o Supabase/PostgreSQL e executar as queries SQL.
    # Por enquanto, retornamos dados mockados para validar a integração com o LangGraph.
    
    mocked_metrics = {
        "periodo": f"{start_date} a {end_date}",
        "taxa_aumento_casos": "15%",
        "taxa_mortalidade": "2.5%",
        "taxa_ocupacao_uti": "85%",
        "taxa_vacinacao": "60%"
    }
    
    return mocked_metrics