from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class EmpresaCreate(BaseModel):
    nome: str
    cnpj: Optional[str] = None


class EmpresaResponse(BaseModel):
    id: int
    nome: str
    cnpj: Optional[str] = None
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class ProdutoCreate(BaseModel):
    empresa_id: Optional[int] = 1
    sku: Optional[str] = None
    nome: str
    categoria: Optional[str] = "Geral"
    quantidade: int = 0
    estoque_minimo: int = 5
    preco_custo: float = 0.0
    preco: float
    usuario_nome: Optional[str] = None


class ProdutoUpdate(BaseModel):
    sku: Optional[str] = None
    nome: Optional[str] = None
    categoria: Optional[str] = None
    quantidade: Optional[int] = None
    estoque_minimo: Optional[int] = None
    preco_custo: Optional[float] = None
    preco: Optional[float] = None


class ProdutoResponse(BaseModel):
    id: int
    empresa_id: int = 1
    sku: Optional[str] = None
    nome: str
    categoria: Optional[str] = "Geral"
    quantidade: int
    estoque_minimo: int
    preco_custo: float
    preco: float
    total_entradas: int = 0
    total_saidas: int = 0
    ultima_entrada_em: Optional[datetime] = None
    ultima_saida_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class MovimentacaoCreate(BaseModel):
    empresa_id: Optional[int] = None
    produto_id: int
    tipo: str
    quantidade: int
    usuario_nome: Optional[str] = "Sistema"
    observacao: Optional[str] = None


class MovimentacaoResponse(BaseModel):
    id: int
    empresa_id: int = 1
    produto_id: int
    produto_nome: str
    tipo: str
    quantidade_movimentada: int
    total_entradas_acumulado: int
    estoque_anterior: int
    estoque_restante: int
    data_hora_entrada_ref: Optional[datetime] = None
    data_hora_saida_ref: Optional[datetime] = None
    data_hora_movimentacao: datetime
    usuario_nome: Optional[str] = None
    observacao: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    empresa_id: Optional[int] = 1
    nome_completo: str
    nome_social: Optional[str] = None
    funcao: Optional[str] = None
    cpf: str
    email: EmailStr
    matricula: str
    sexo: str
    senha: str
    perfil: str = "usuario"


class UsuarioResponse(BaseModel):
    id: int
    empresa_id: int = 1
    nome_completo: str
    nome_social: Optional[str] = None
    funcao: Optional[str] = None
    cpf: str
    email: str
    matricula: str
    sexo: str
    perfil: str
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    identificador: str
    senha: str


class LoginResponse(BaseModel):
    mensagem: str
    log_id: int
    data_hora_acesso: datetime
    usuario: UsuarioResponse


class LogAcessoResponse(BaseModel):
    id: int
    empresa_id: int = 1
    usuario_id: Optional[int] = None
    identificador_login: str
    data_hora_acesso: datetime
    sucesso: bool

    class Config:
        from_attributes = True