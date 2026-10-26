from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nome do arquivo do banco de dados local
DATABASE_URL = "sqlite:///estoque.db"

# Inicializa o motor do banco de dados
engine = create_engine(DATABASE_URL, echo=False)

# Cria a fábrica de sessões para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criar os modelos de tabelas
Base = declarative_base()

def init_db():
    # Cria a tabela no banco caso ela ainda não exista
    Base.metadata.create_all(bind=engine)