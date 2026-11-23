from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base

FUSO_BR = timezone(timedelta(hours=-3))


def agora_br():
    return datetime.now(FUSO_BR).replace(tzinfo=None)


class EmpresaModel(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=True, index=True)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, nullable=False, default=agora_br)


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1, index=True)
    nome_completo = Column(String(150), nullable=False)
    nome_social = Column(String(150), nullable=True)
    funcao = Column(String(120), nullable=True)
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
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    identificador_login = Column(String(150), nullable=False)
    data_hora_acesso = Column(DateTime, nullable=False, default=agora_br)
    sucesso = Column(Boolean, nullable=False, default=True)


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1, index=True)
    sku = Column(String(60), nullable=True, index=True)
    nome = Column(String(150), nullable=False)
    categoria = Column(String(80), nullable=True, default="Geral")
    quantidade = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=5)
    preco_custo = Column(Float, nullable=False, default=0.0)
    preco = Column(Float, nullable=False, default=0.0)
    total_entradas = Column(Integer, nullable=False, default=0)
    total_saidas = Column(Integer, nullable=False, default=0)
    ultima_entrada_em = Column(DateTime, nullable=True)
    ultima_saida_em = Column(DateTime, nullable=True)


class MovimentacaoEstoqueModel(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, default=1, index=True)
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