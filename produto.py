from sqlalchemy import Column, Integer, String, Float
from database import Base

class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)