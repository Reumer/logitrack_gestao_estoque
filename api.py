from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from produto import ProdutoModel
from schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from typing import List

# Inicializa o banco de dados
init_db()

app = FastAPI(
    title="LogiTrack API",
    description="Modern inventory management API built with FastAPI and SQLAlchemy",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Products",
            "description": "Operations for managing and controlling product inventory.",
        }
    ]
)


# Dependência para obter a sessão do banco por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/products/", response_model=ProdutoResponse, status_code=201, summary="Create a new product",
          tags=["Products"])
def create_product(produto: ProdutoCreate, db: Session = Depends(get_db)):
    new_product = ProdutoModel(
        nome=produto.nome,
        quantidade=produto.quantidade,
        preco=produto.preco
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products/", response_model=List[ProdutoResponse], summary="List all products", tags=["Products"])
def list_products(db: Session = Depends(get_db)):
    products = db.query(ProdutoModel).all()
    return products


@app.put("/products/{product_id}", response_model=ProdutoResponse, summary="Update an existing product",
         tags=["Products"])
def update_product(product_id: int, produto_data: ProdutoUpdate, db: Session = Depends(get_db)):
    product = db.query(ProdutoModel).filter(ProdutoModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in inventory")

    if produto_data.quantidade is not None:
        product.quantidade = produto_data.quantidade
    if produto_data.preco is not None:
        product.preco = produto_data.preco

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204, summary="Delete a product", tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProdutoModel).filter(ProdutoModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in inventory")

    db.delete(product)
    db.commit()
    return None