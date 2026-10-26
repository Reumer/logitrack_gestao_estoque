from estoque import (
    adicionar_produto,
    listar_produtos,
    calcular_indicadores,
    atualizar_produto,
    deletar_produto
)


def menu():
    while True:
        print("\n=== LogiTrack (Versão SQL) ===")
        print("1. Adicionar Produto")
        print("2. Listar Produtos")
        print("3. Ver Indicadores")
        print("4. Atualizar Produto")
        print("5. Remover Produto")
        print("6. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome do produto: ")
            try:
                qtd = int(input("Quantidade: "))
                preco = float(input("Preço unitário (R$): "))
                adicionar_produto(nome, qtd, preco)
            except ValueError:
                print("\n[Erro] A quantidade deve ser um número inteiro e o preço deve ser numérico.")

        elif opcao == "2":
            listar_produtos()

        elif opcao == "3":
            calcular_indicadores()

        elif opcao == "4":
            listar_produtos()
            try:
                produto_id = int(input("\nID do produto que deseja atualizar: "))
                qtd_input = input("Nova quantidade (pressione Enter para não alterar): ")
                preco_input = input("Novo preço (pressione Enter para não alterar): ")

                nova_qtd = int(qtd_input) if qtd_input.strip() else None
                novo_preco = float(preco_input) if preco_input.strip() else None

                atualizar_produto(produto_id, nova_quantidade=nova_qtd, novo_preco=novo_preco)
            except ValueError:
                print("\n[Erro] Valores inválidos. Certifique-se de inserir números corretos.")

        elif opcao == "5":
            listar_produtos()
            try:
                produto_id = int(input("\nID do produto que deseja remover: "))
                deletar_produto(produto_id)
            except ValueError:
                print("\n[Erro] O ID deve ser um número inteiro.")

        elif opcao == "6":
            print("\nEncerrando o LogiTrack. Até logo!")
            break
        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()