from datetime import datetime, timezone, timedelta
import hashlib
import os
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from database import SessionLocal, engine, init_db
from models import LogAcessoModel, MovimentacaoEstoqueModel, UsuarioModel
from produto import ProdutoModel
from schemas import (
    LogAcessoResponse,
    LoginRequest,
    LoginResponse,
    MovimentacaoCreate,
    MovimentacaoResponse,
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
    UsuarioCreate,
    UsuarioResponse,
)

FUSO_BR = timezone(timedelta(hours=-3))


def agora_br() -> datetime:
    return datetime.now(FUSO_BR).replace(tzinfo=None)


def obter_origens_cors() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if not raw or raw == "*":
        return ["*"]
    return [origem.strip() for origem in raw.split(",") if origem.strip()]


app = FastAPI(title="LogiTrack API", version="1.2.0")

origens_cors = obter_origens_cors()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_cors,
    allow_credentials=origens_cors != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UsuarioUpdatePayload(BaseModel):
    nome_completo: Optional[str] = None
    funcao: Optional[str] = None
    nome_social: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    matricula: Optional[str] = None
    sexo: Optional[str] = None
    perfil: Optional[str] = None
    senha: Optional[str] = None


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${derived}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        salt, original_hash = stored_hash.split("$", 1)
    except ValueError:
        return False

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return derived == original_hash


def garantir_colunas_produtos():
    comandos = [
        "ALTER TABLE produtos ADD COLUMN total_entradas INT NOT NULL DEFAULT 0",
        "ALTER TABLE produtos ADD COLUMN total_saidas INT NOT NULL DEFAULT 0",
        "ALTER TABLE produtos ADD COLUMN ultima_entrada_em DATETIME NULL",
        "ALTER TABLE produtos ADD COLUMN ultima_saida_em DATETIME NULL",
        "ALTER TABLE usuarios ADD COLUMN funcao VARCHAR(120) NULL",
    ]
    with engine.connect() as conn:
        for sql in comandos:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                conn.rollback()


def garantir_admin_inicial(db: Session):
    admin_existente = db.query(UsuarioModel).filter(UsuarioModel.perfil == "admin").first()
    if not admin_existente:
        admin_email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@logitrack.local").strip()
        admin_matricula = os.getenv("INITIAL_ADMIN_MATRICULA", "ADM001").strip()
        admin_senha = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin@123")

        admin_padrao = UsuarioModel(
            nome_completo="Administrador LogiTrack",
            nome_social=None,
            cpf="000.000.000-00",
            email=admin_email,
            matricula=admin_matricula,
            sexo="Não informado",
            perfil="admin",
            senha_hash=hash_password(admin_senha),
            ativo=True,
            criado_em=agora_br(),
        )
        if hasattr(admin_padrao, "funcao"):
            admin_padrao.funcao = "Administrador"
        db.add(admin_padrao)
        db.commit()


def sincronizar_produtos_com_historico(db: Session):
    produtos = db.query(ProdutoModel).all()
    for p in produtos:
        movs = (
            db.query(MovimentacaoEstoqueModel)
            .filter(MovimentacaoEstoqueModel.produto_id == p.id)
            .order_by(MovimentacaoEstoqueModel.data_hora_movimentacao.asc())
            .all()
        )
        if movs:
            entradas_mov = sum(
                m.quantidade_movimentada or 0
                for m in movs
                if (m.tipo or "").lower() == "entrada"
            )
            saidas_mov = sum(
                m.quantidade_movimentada or 0
                for m in movs
                if (m.tipo or "").lower() == "saida"
            )
            ult_entrada = next(
                (
                    m.data_hora_entrada_ref or m.data_hora_movimentacao
                    for m in reversed(movs)
                    if (m.tipo or "").lower() == "entrada"
                ),
                None,
            )
            ult_saida = next(
                (
                    m.data_hora_saida_ref or m.data_hora_movimentacao
                    for m in reversed(movs)
                    if (m.tipo or "").lower() == "saida"
                ),
                None,
            )
            if (p.total_entradas or 0) == 0 and entradas_mov > 0:
                p.total_entradas = entradas_mov
            if (p.total_saidas or 0) == 0 and saidas_mov > 0:
                p.total_saidas = saidas_mov
            if not p.ultima_entrada_em and ult_entrada:
                p.ultima_entrada_em = ult_entrada
            if not p.ultima_saida_em and ult_saida:
                p.ultima_saida_em = ult_saida
        elif (p.total_entradas or 0) == 0 and (p.quantidade or 0) > 0:
            p.total_entradas = p.quantidade
            if not p.ultima_entrada_em:
                p.ultima_entrada_em = agora_br()
    db.commit()


@app.on_event("startup")
def on_startup():
    init_db()
    garantir_colunas_produtos()
    db = SessionLocal()
    try:
        garantir_admin_inicial(db)
        sincronizar_produtos_com_historico(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Autenticação e Usuários ---
@app.post("/auth/login", response_model=LoginResponse)
def login(credenciais: LoginRequest, db: Session = Depends(get_db)):
    identificador = credenciais.identificador.strip()
    agora = agora_br()

    usuario = (
        db.query(UsuarioModel)
        .filter(
            or_(
                UsuarioModel.email == identificador,
                UsuarioModel.matricula == identificador,
            )
        )
        .first()
    )

    if not usuario or not verify_password(credenciais.senha, usuario.senha_hash):
        log_falha = LogAcessoModel(
            usuario_id=usuario.id if usuario else None,
            identificador_login=identificador,
            data_hora_acesso=agora,
            sucesso=False,
        )
        db.add(log_falha)
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not usuario.ativo:
        log_inativo = LogAcessoModel(
            usuario_id=usuario.id,
            identificador_login=identificador,
            data_hora_acesso=agora,
            sucesso=False,
        )
        db.add(log_inativo)
        db.commit()
        raise HTTPException(status_code=403, detail="Usuário inativo")

    log_sucesso = LogAcessoModel(
        usuario_id=usuario.id,
        identificador_login=identificador,
        data_hora_acesso=agora,
        sucesso=True,
    )
    db.add(log_sucesso)
    db.commit()
    db.refresh(log_sucesso)

    return LoginResponse(
        mensagem="Acesso realizado com sucesso",
        log_id=log_sucesso.id,
        data_hora_acesso=log_sucesso.data_hora_acesso,
        usuario=usuario,
    )


@app.post("/users/", response_model=UsuarioResponse, status_code=201)
def cadastrar_usuario(
    dados: UsuarioCreate,
    admin_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    if admin_id is not None:
        admin = db.query(UsuarioModel).filter(UsuarioModel.id == admin_id).first()
        if not admin or admin.perfil != "admin" or not admin.ativo:
            raise HTTPException(
                status_code=403,
                detail="Apenas administradores ativos podem cadastrar novos usuários",
            )

    cpf_limpo = dados.cpf.strip()
    email_limpo = dados.email.strip().lower()
    matricula_limpa = dados.matricula.strip()

    duplicado = (
        db.query(UsuarioModel)
        .filter(
            or_(
                UsuarioModel.cpf == cpf_limpo,
                UsuarioModel.email == email_limpo,
                UsuarioModel.matricula == matricula_limpa,
            )
        )
        .first()
    )
    if duplicado:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este CPF, e-mail ou matrícula",
        )

    perfil_normalizado = dados.perfil.strip().lower()
    if perfil_normalizado not in ("admin", "usuario"):
        perfil_normalizado = "usuario"

    funcao_texto = (
        getattr(dados, "funcao", None)
        or dados.nome_social
        or None
    )
    funcao_limpa = funcao_texto.strip() if funcao_texto else None

    novo_usuario = UsuarioModel(
        nome_completo=dados.nome_completo.strip(),
        nome_social=funcao_limpa,
        cpf=cpf_limpo,
        email=email_limpo,
        matricula=matricula_limpa,
        sexo=dados.sexo.strip(),
        perfil=perfil_normalizado,
        senha_hash=hash_password(dados.senha),
        ativo=True,
        criado_em=agora_br(),
    )
    if hasattr(novo_usuario, "funcao"):
        novo_usuario.funcao = funcao_limpa

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@app.get("/users/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(UsuarioModel).order_by(UsuarioModel.id.desc()).all()


@app.put("/users/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdatePayload,
    db: Session = Depends(get_db),
):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if dados.cpf is not None:
        cpf_limpo = dados.cpf.strip()
        conflito = (
            db.query(UsuarioModel)
            .filter(UsuarioModel.cpf == cpf_limpo, UsuarioModel.id != usuario_id)
            .first()
        )
        if conflito:
            raise HTTPException(status_code=400, detail="CPF já utilizado por outro usuário")
        usuario.cpf = cpf_limpo

    if dados.email is not None:
        email_limpo = dados.email.strip().lower()
        conflito = (
            db.query(UsuarioModel)
            .filter(UsuarioModel.email == email_limpo, UsuarioModel.id != usuario_id)
            .first()
        )
        if conflito:
            raise HTTPException(status_code=400, detail="E-mail já utilizado por outro usuário")
        usuario.email = email_limpo

    if dados.matricula is not None:
        matricula_limpa = dados.matricula.strip()
        conflito = (
            db.query(UsuarioModel)
            .filter(UsuarioModel.matricula == matricula_limpa, UsuarioModel.id != usuario_id)
            .first()
        )
        if conflito:
            raise HTTPException(status_code=400, detail="Matrícula já utilizada por outro usuário")
        usuario.matricula = matricula_limpa

    if dados.nome_completo is not None:
        usuario.nome_completo = dados.nome_completo.strip()

    funcao_nova = dados.funcao if dados.funcao is not None else dados.nome_social
    if funcao_nova is not None:
        funcao_limpa = funcao_nova.strip() or None
        usuario.nome_social = funcao_limpa
        if hasattr(usuario, "funcao"):
            usuario.funcao = funcao_limpa

    if dados.sexo is not None:
        usuario.sexo = dados.sexo.strip()

    if dados.perfil is not None:
        perfil_norm = dados.perfil.strip().lower()
        if perfil_norm in ("admin", "usuario"):
            usuario.perfil = perfil_norm

    if dados.senha:
        usuario.senha_hash = hash_password(dados.senha)

    db.commit()
    db.refresh(usuario)
    return usuario


@app.delete("/users/{usuario_id}")
def excluir_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario)
    db.commit()
    return {"mensagem": "Usuário excluído com sucesso"}


@app.get("/auth/logs", response_model=List[LogAcessoResponse])
def listar_logs_acesso(db: Session = Depends(get_db)):
    return db.query(LogAcessoModel).order_by(LogAcessoModel.data_hora_acesso.desc()).all()


# --- Produtos & Movimentações ---
@app.get("/products/", response_model=List[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProdutoModel).all()


@app.post("/products/", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    agora = agora_br()
    qtd_inicial = max(0, produto.quantidade)

    novo_produto = ProdutoModel(
        sku=produto.sku,
        nome=produto.nome,
        categoria=produto.categoria,
        quantidade=qtd_inicial,
        estoque_minimo=produto.estoque_minimo,
        preco_custo=produto.preco_custo,
        preco=produto.preco,
        total_entradas=qtd_inicial,
        total_saidas=0,
        ultima_entrada_em=agora if qtd_inicial > 0 else None,
        ultima_saida_em=None,
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    if qtd_inicial > 0:
        mov = MovimentacaoEstoqueModel(
            produto_id=novo_produto.id,
            produto_nome=novo_produto.nome,
            tipo="entrada",
            quantidade_movimentada=qtd_inicial,
            total_entradas_acumulado=qtd_inicial,
            estoque_anterior=0,
            estoque_restante=qtd_inicial,
            data_hora_entrada_ref=agora,
            data_hora_saida_ref=None,
            data_hora_movimentacao=agora,
            usuario_nome=produto.usuario_nome or "Sistema",
            observacao="Cadastro inicial do produto",
        )
        db.add(mov)
        db.commit()

    return novo_produto


@app.post("/products/movimentar", response_model=MovimentacaoResponse)
def movimentar_estoque(dados: MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == dados.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if dados.quantidade <= 0:
        raise HTTPException(status_code=400, detail="A quantidade deve ser maior que zero")

    tipo = dados.tipo.strip().lower()
    if tipo not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'")

    agora = agora_br()
    estoque_anterior = produto.quantidade or 0

    if tipo == "entrada":
        novo_estoque = estoque_anterior + dados.quantidade
        produto.quantidade = novo_estoque
        produto.total_entradas = (produto.total_entradas or 0) + dados.quantidade
        produto.ultima_entrada_em = agora
    else:
        if dados.quantidade > estoque_anterior:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {estoque_anterior} unidade(s).",
            )
        novo_estoque = estoque_anterior - dados.quantidade
        produto.quantidade = novo_estoque
        produto.total_saidas = (produto.total_saidas or 0) + dados.quantidade
        produto.ultima_saida_em = agora

    movimentacao = MovimentacaoEstoqueModel(
        produto_id=produto.id,
        produto_nome=produto.nome,
        tipo=tipo,
        quantidade_movimentada=dados.quantidade,
        total_entradas_acumulado=produto.total_entradas or 0,
        estoque_anterior=estoque_anterior,
        estoque_restante=novo_estoque,
        data_hora_entrada_ref=produto.ultima_entrada_em,
        data_hora_saida_ref=produto.ultima_saida_em,
        data_hora_movimentacao=agora,
        usuario_nome=dados.usuario_nome or "Sistema",
        observacao=dados.observacao.strip() if dados.observacao else None,
    )

    db.add(movimentacao)
    db.commit()
    db.refresh(movimentacao)
    return movimentacao


@app.get("/movements/", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(db: Session = Depends(get_db)):
    return (
        db.query(MovimentacaoEstoqueModel)
        .order_by(MovimentacaoEstoqueModel.data_hora_movimentacao.desc())
        .all()
    )


@app.put("/products/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if dados.sku is not None:
        produto.sku = dados.sku
    if dados.nome is not None:
        produto.nome = dados.nome
    if dados.categoria is not None:
        produto.categoria = dados.categoria
    if dados.quantidade is not None:
        produto.quantidade = dados.quantidade
    if dados.estoque_minimo is not None:
        produto.estoque_minimo = dados.estoque_minimo
    if dados.preco_custo is not None:
        produto.preco_custo = dados.preco_custo
    if dados.preco is not None:
        produto.preco = dados.preco

    db.commit()
    db.refresh(produto)
    return produto


@app.delete("/products/{produto_id}")
def deletar_produto(
    produto_id: int,
    usuario_nome: Optional[str] = Query(default="Sistema"),
    db: Session = Depends(get_db),
):
    produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    agora = agora_br()
    mov_exclusao = MovimentacaoEstoqueModel(
        produto_id=produto.id,
        produto_nome=produto.nome,
        tipo="exclusao",
        quantidade_movimentada=produto.quantidade or 0,
        total_entradas_acumulado=produto.total_entradas or 0,
        estoque_anterior=produto.quantidade or 0,
        estoque_restante=0,
        data_hora_entrada_ref=produto.ultima_entrada_em,
        data_hora_saida_ref=produto.ultima_saida_em,
        data_hora_movimentacao=agora,
        usuario_nome=usuario_nome or "Sistema",
        observacao="Produto excluído do catálogo",
    )
    db.add(mov_exclusao)
    db.delete(produto)
    db.commit()
    return {"mensagem": "Produto excluído com sucesso"}