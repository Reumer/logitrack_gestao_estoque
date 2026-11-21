from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from database import Base

FUSO_BR = timezone(timedelta(hours=-3))


def agora_br():
    return datetime.now(FUSO_BR).replace(tzinfo=None)


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(150), nullable=False)
    nome_social = Column(String(150), nullable=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    matricula = Column(String(50), unique=True, nullable=False, index=True)
    sexo = Column(String(30), nullable=False)
    perfil = Column(String(20), nullable=False, default="usuario")
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, nullable=False, default=agora_br)


class LogAcessoModel(Base):
    __tablename__ = "logs_acesso"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    identificador_login = Column(String(150), nullable=False)
    data_hora_acesso = Column(DateTime, nullable=False, default=agora_br)
    sucesso = Column(Boolean, nullable=False, default=True)


class MovimentacaoEstoqueModel(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, nullable=False, index=True)
    produto_nome = Column(String(150), nullable=False)
    tipo = Column(String(20), nullable=False)  # "entrada", "saida", "cadastro", "exclusao"
    quantidade_movimentada = Column(Integer, nullable=False, default=0)
    total_entradas_acumulado = Column(Integer, nullable=False, default=0)
    estoque_anterior = Column(Integer, nullable=False, default=0)
    estoque_restante = Column(Integer, nullable=False, default=0)
    data_hora_entrada_ref = Column(DateTime, nullable=True)
    data_hora_saida_ref = Column(DateTime, nullable=True)
    data_hora_movimentacao = Column(DateTime, nullable=False, default=agora_br)
    usuario_nome = Column(String(150), nullable=True)
    observacao = Column(String(255), nullable=True)