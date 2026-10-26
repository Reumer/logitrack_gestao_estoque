from database import SessionLocal, init_db
from produto import ProdutoModel

# Garante que o banco e as tabelas sejam criados assim que o módulo for carregado
init_db()


def adicionar_produto(nome, quantidade, preco):
    db = SessionLocal()
    try:
        novo_produto = ProdutoModel(nome=nome, quantidade=quantidade, preco=preco)
        db.add(novo_produto)
        db.commit()
        print(f"\n[Sucesso] Produto '{nome}' cadastrado no banco de dados!")
    except Exception as e:
        db.rollback()
        print(f"\n[Erro] Não foi possível cadastrar o produto: {e}")
    finally:
        db.close()


def listar_produtos():
    db = SessionLocal()
    try:
        produtos = db.query(ProdutoModel).all()
        if not produtos:
            print("\nEstoque vazio.")
            return

        print("\n" + "=" * 40)
        print("         LISTA DE ESTOQUE (SQL)        ")
        print("=" * 40)
        for p in produtos:
            print(f"ID: {p.id} | Nome: {p.nome} | Qtd: {p.quantidade} | Preço: R$ {p.preco:.2f}")
        print("=" * 40)
    finally:
        db.close()


def calcular_indicadores():
    db = SessionLocal()
    try:
        produtos = db.query(ProdutoModel).all()
        if not produtos:
            print("\nSem dados para calcular indicadores.")
            return

        total_itens = sum(p.quantidade for p in produtos)
        valor_total = sum(p.quantidade * p.preco for p in produtos)

        print("\n" + "=" * 40)
        print("       INDICADORES DE DESEMPENHO        ")
        print("=" * 40)
        print(f"Total de tipos de produtos: {len(produtos)}")
        print(f"Quantidade total em estoque: {total_itens} unidades")
        print(f"Valor total investido: R$ {valor_total:.2f}")
        print("=" * 40)
    finally:
        db.close()


def atualizar_produto(produto_id, nova_quantidade=None, novo_preco=None):
    db = SessionLocal()
    try:
        produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
        if not produto:
            print(f"\n[Erro] Produto com ID {produto_id} não foi encontrado.")
            return

        if nova_quantidade is not None:
            produto.quantidade = nova_quantidade
        if novo_preco is not None:
            produto.preco = novo_preco

        db.commit()
        print(f"\n[Sucesso] Produto ID {produto_id} atualizado com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"\n[Erro] Não foi possível atualizar o produto: {e}")
    finally:
        db.close()


def deletar_produto(produto_id):
    db = SessionLocal()
    try:
        produto = db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()
        if not produto:
            print(f"\n[Erro] Produto com ID {produto_id} não foi encontrado.")
            return

        db.delete(produto)
        db.commit()
        print(f"\n[Sucesso] Produto ID {produto_id} removido do estoque!")
    except Exception as e:
        db.rollback()
        print(f"\n[Erro] Não foi possível remover o produto: {e}")
    finally:
        db.close()