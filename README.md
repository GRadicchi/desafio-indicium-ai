# desafio-indicium-ai

Desafio técnico da Indicium AI para desenvolvimento de uma solução de IA Generativa para análise de dados epidemiológicos.

## 🚀 Arquitetura da Solução

O sistema foi desenhado com foco em modularidade, governança e transparência, utilizando os seguintes componentes:

* **Orquestrador (Agente Principal):** Construído com `LangGraph`, gerencia o fluxo de raciocínio (ReAct) e a tomada de decisão sobre quais ferramentas acionar.
* **Ferramentas (Tools):**
    * `get_srag_metrics`: Consulta dados epidemiológicos (casos, óbitos, UTI, vacinação) no PostgreSQL.
    * `generate_srag_charts`: Gera visualizações gráficas (casos semanais e mensais) utilizando `Matplotlib`.
    * `get_srag_news`: Integração com Tavily para pesquisa de contexto em tempo real sobre a SRAG.
* **Pipeline de Dados (ETL):** Script robusto que processa dados brutos do DATASUS, aplicando anonimização (removendo dados sensíveis/PII) e filtros clínicos de SRAG antes da ingestão no banco de dados.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **IA/LLM:** LangChain, LangGraph, Google Gemini.
* **Banco de Dados:** PostgreSQL (Supabase).
* **APIs:** Tavily (Busca de notícias), FastAPI (Interface da API).
* **Engenharia de Dados:** Pandas, SQLAlchemy.

## ⚙️ Como Executar

1. **Configuração do Ambiente:**
   Crie um arquivo `.env` na raiz seguindo o modelo do `.env.example`:
   ```bash
   DATABASE_URL="postgresql://usuario:senha@host:5432/nome_do_banco"
   GOOGLE_API_KEY="AIza..."
   TAVILY_API_KEY="tvly-..."


## Instalação de dependências:

pip install -r requirements.txt

    ### Rodar o ETL (Importação dos dados):

        python src/utils/etl.py

    ### Rodar a API:

        uvicorn api:app --reload

## 📋 Governança e Transparência
O agente utiliza o padrão de state do LangGraph, garantindo que todo o histórico de interações seja mantido e auditável (logado via main.py). O sistema foi configurado para tratar dados sensíveis (PII) durante a etapa de ETL, garantindo conformidade com práticas de privacidade.