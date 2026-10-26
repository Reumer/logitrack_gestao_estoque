from pydantic import BaseModel
from typing import Optional

class ProdutoCreate(BaseModel):
    nome: str
    quantidade: int
    preco: float

class ProdutoUpdate(BaseModel):
    quantidade: Optional[int] = None
    preco: Optional[float] = None

class ProdutoResponse(ProdutoCreate):
    id: int

    class Config:
        from_attributes = True