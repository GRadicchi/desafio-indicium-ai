from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

# Instanciamos a ferramenta da Tavily para retornar os 3 melhores resultados
# O LangChain já se encarrega de ler a TAVILY_API_KEY do seu .env
tavily_search = TavilySearchResults(max_results=3)

@tool
def get_srag_news(query: str) -> str:
    """
    Pesquisa notícias recentes e contexto em tempo real sobre a Síndrome Respiratória Aguda Grave (SRAG) 
    ou vírus respiratórios (COVID, Influenza, VSR).
    
    Args:
        query (str): O termo de pesquisa (ex: "cenário atual aumento SRAG Brasil", "notícias surto VSR").
        
    Returns:
        str: Um resumo das notícias encontradas com as respetivas fontes e URLs.
    """
    try:
        # Executa a pesquisa
        results = tavily_search.invoke({"query": query})
        
        if not results:
            return "Não foram encontradas notícias recentes para esta pesquisa."
            
        # Formata os resultados num texto limpo para o LLM processar
        formatted_news = "Notícias recentes encontradas:\n\n"
        for i, res in enumerate(results, 1):
            conteudo = res.get('content', 'Sem conteúdo')
            url = res.get('url', 'URL Desconhecido')
            formatted_news += f"{i}. {conteudo}\n(Fonte: {url})\n\n"
            
        return formatted_news
        
    except Exception as e:
        return f"Erro ao aceder ao motor de pesquisa de notícias: {str(e)}"