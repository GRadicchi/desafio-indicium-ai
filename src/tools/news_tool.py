from langchain_tavily import TavilySearch
from langchain_core.tools import tool

# Atualizado para a nova implementação recomendada
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
        # A nova versão do TavilySearch funciona de forma similar
        results = tavily_search.invoke(query)
        
        if not results:
            return "Não foram encontradas notícias recentes para esta pesquisa."
            
        formatted_news = "Notícias recentes encontradas:\n\n"
        for i, res in enumerate(results, 1):
            # Nota: O formato de saída pode variar ligeiramente entre versões, 
            # adaptamos para garantir robustez
            conteudo = res.get('content', 'Sem conteúdo') if isinstance(res, dict) else str(res)
            formatted_news += f"{i}. {conteudo}\n\n"
            
        return formatted_news
        
    except Exception as e:
        return f"Erro ao aceder ao motor de pesquisa de notícias: {str(e)}"