import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Carrega as variáveis de ambiente a partir do ficheiro .env
load_dotenv()

def get_db_engine() -> Engine:
    """
    Cria e devolve a engine de ligação à base de dados PostgreSQL (Supabase).
    
    Returns:
        Engine: Instância do SQLAlchemy Engine ligada à base de dados.
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        raise ValueError("A variável de ambiente DATABASE_URL não está definida no ficheiro .env.")
        
    # O parâmetro pool_pre_ping=True verifica se a ligação ainda está ativa antes de a utilizar,
    # prevenindo erros de "connection dropped" em bases de dados remotas.
    engine = create_engine(db_url, pool_pre_ping=True)
    
    return engine