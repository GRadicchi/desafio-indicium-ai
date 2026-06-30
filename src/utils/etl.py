import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente para conectar ao Supabase
load_dotenv()

def run_etl_pipeline(csv_path: str):
    """
    Lê o CSV bruto do DATASUS, aplica regras de negócio oficiais de SRAG,
    remove dados sensíveis e envia para o banco de dados.
    """
    print("Iniciando carregamento do CSV...")
    # low_memory=False ajuda a ler arquivos grandes com tipos mistos
    df = pd.read_csv(csv_path, sep=';', low_memory=False)
    
    total_linhas_iniciais = len(df)
    print(f"Total de linhas carregadas: {total_linhas_iniciais}")

    # 1. Remoção de Dados Sensíveis (LGPD / HIPAA)
    # Lista baseada nas documentações de anonimização do DATASUS
    colunas_sensiveis = [
        'NM_PACIENT', 'NM_MAE_PAC', 'NM_BAIRRO', 'NOME_PROF', 'NM_LOGRADO', 
        'NU_NUMERO', 'NM_COMPLEM', 'NU_CPF', 'NU_CNS', 'NU_CEP', 'NU_TELEFON', 
        'NU_DDD_TEL', 'REG_PROF', 'CO_UN_INTE', 'VG_LAB', 'VG_CODLAB', 
        'VG_CODDEST', 'VG_PROF', 'VG_EST', 'CO_LAB_AN', 'CO_LAB_PCR', 'NU_DO', 
        'OBSERVA', 'REQUI_GAL', 'CO_UNI_NOT', 'ID_UN_INTE', 'ID_UNIDADE', 
        'LAB_AN', 'LAB_PCR'
    ]
    
    cols_to_drop = [col for col in colunas_sensiveis if col in df.columns]
    df.drop(columns=cols_to_drop, inplace=True)
    print(f"Removidas {len(cols_to_drop)} colunas contendo dados sensíveis (PII).")

    # 2. Aplicação dos Critérios Clínicos de SRAG (Traduzido do Script 1 Oficial em R)
    # Critério 1: Hospitalização ou Óbito
    crit_1 = (df['HOSPITAL'] == 1) | (df['EVOLUCAO'] == 2)
    
    # Critério 2: Tosse ou Dor de Garganta
    crit_2 = (df['TOSSE'] == 1) | (df['GARGANTA'] == 1)
    
    # Critério 3: Falta de ar, saturação baixa ou desconforto respiratório
    crit_3 = (df['DISPNEIA'] == 1) | (df['SATURACAO'] == 1) | (df['DESC_RESP'] == 1)
    
    # Filtrar o DataFrame
    df_srag = df[crit_1 & crit_2 & crit_3].copy()
    print(f"Linhas retidas após filtros clínicos de SRAG: {len(df_srag)}")

    # 3. Tratamento de Colunas Essenciais para as Métricas
    colunas_vitais = ['DT_NOTIFIC', 'EVOLUCAO', 'UTI', 'VACINA_COV']
    for col in colunas_vitais:
        if col in df_srag.columns:
            # Substituir valores nulos por 9 ('Ignorado' no dicionário DATASUS)
            df_srag[col] = df_srag[col].fillna(9)

    # 4. Envio para o Banco de Dados (Supabase/PostgreSQL)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Erro: DATABASE_URL não encontrada no .env")
        return

    print("Conectando ao banco de dados e enviando a tabela 'srag_dados'...")
    engine = create_engine(db_url)
    
    # Escreve o dataframe diretamente no PostgreSQL. 
    # if_exists='replace' recria a tabela. Para produção seria 'append'.
    df_srag.to_sql('srag_dados', engine, if_exists='replace', index=False)
    print("ETL concluído com sucesso!")

if __name__ == "__main__":
    # Apontando para o arquivo real na raiz do projeto
    run_etl_pipeline("INFLUD26-29-06-2026.csv")