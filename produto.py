from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

FUSO_BR = timezone(timedelta(hours=-3))


def agora_br():
    return datetime.now(FUSO_BR).replace(tzinfo=None)


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), nullable=True)
    nome = Column(String(150), nullable=False)
    categoria = Column(String(100), nullable=True, default="Geral")
    quantidade = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=5)
    preco_custo = Column(Float, nullable=False, default=0.0)
    preco = Column(Float, nullable=False, default=0.0)
    total_entradas = Column(Integer, nullable=False, default=0)
    total_saidas = Column(Integer, nullable=False, default=0)
    ultima_entrada_em = Column(DateTime, nullable=True)
    ultima_saida_em = Column(DateTime, nullable=True)