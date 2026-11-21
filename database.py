import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

SERVER_URL = "mysql+pymysql://root:Rvm162207@logitrack_mysql:3306/"
DB_NAME = "logitrack_mysql"
DATABASE_URL = f"{SERVER_URL}{DB_NAME}"

Base = declarative_base()


def init_db():
    try:
        import produto  # noqa: F401
    except ImportError:
        pass

    try:
        import models  # noqa: F401
    except ImportError:
        pass

    retries = 15
    while retries > 0:
        try:
            temp_engine = create_engine(SERVER_URL, echo=False)
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
                conn.commit()
            temp_engine.dispose()

            global engine, SessionLocal
            engine = create_engine(DATABASE_URL, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            Base.metadata.create_all(bind=engine)
            print("Banco de dados e tabelas criados/conectados com sucesso!")
            break
        except OperationalError as e:
            retries -= 1
            print(f"Aguardando o MySQL iniciar... Tentativas restantes: {retries}. Erro: {e}")
            time.sleep(3)
    else:
        raise Exception("Não foi possível conectar ao MySQL após várias tentativas.")


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)