from langchain_tavily import TavilySearch
from langchain_core.tools import tool
import logging

tavily_search = TavilySearch(max_results=3)

@tool
def get_srag_news(query: str) -> str:
    """
    Pesquisa notícias recentes e contexto em tempo real sobre a Síndrome Respiratória Aguda Grave (SRAG) 
    ou vírus respiratórios (COVID, Influenza, VSR).
    
    Args:
        query (str): O termo de pesquisa (ex: "cenário atual aumento SRAG Brasil").
        
    Returns:
        str: Um resumo das notícias encontradas com as respetivas fontes.
    """
    try:
        results = tavily_search.invoke(query)
        if not results:
            return "Nenhuma notícia encontrada."
        
        formatted_news = "Notícias encontradas:\n"
        for res in results:
            conteudo = res.get('content', 'Sem conteúdo') if isinstance(res, dict) else str(res)
            formatted_news += f"- {conteudo}\n"
        return formatted_news
    except Exception as e:
        logging.error(f"Erro Tavily: {e}")
        return "Erro ao buscar notícias."