# 📦 LogiTrack — Sistema de Gestão de Estoque & KPIs Logísticos

Sistema web de controle de estoque, movimentação de mercadorias, indicadores (KPIs), gestão de usuários, logs de acesso e base multi-empresa (`empresa_id`).

## 📌 Funcionalidades

- **Controle de Produtos e Saldo:** Cadastro, edição e exclusão de itens com preço, estoque mínimo, entradas/saídas acumuladas e datas/horas de referência.
- **Entradas e Saídas com Trava de Saldo:** Registro de movimentações com validação para impedir saídas maiores que o saldo disponível e geração automática de histórico.
- **Dashboard Executivo:**
  - KPIs de Total de Produtos, Unidades Restantes, Valor Patrimonial, Itens em Estoque Baixo e Produtos Esgotados.
  - Gráficos interativos de fluxo (entradas, saídas e saldo restante) e distribuição de status do catálogo.
- **Usuários e Logs de Acesso:** Cadastro, edição e exclusão de usuários com perfis (`admin` e `usuario`), registro de acessos e política configurável de retenção de logs (`LOG_RETENTION_DAYS`, padrão de 30 dias).
- **Base Multi-Empresa (SaaS):** Estrutura com `empresa_id` e empresa padrão inicial para isolamento de dados entre empresas.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, FastAPI, SQLAlchemy, Pydantic
- **Banco de Dados:** MySQL
- **Frontend:** HTML5, Tailwind CSS, Chart.js, JavaScript
- **Infraestrutura e Ferramentas:** Docker / Docker Compose, Git/GitHub, PyCharm

## 🚀 Como Executar com Docker

1. Clone o repositório:
   ```bash
   git clone [https://github.com/Reumer/logitrack_gestao_estoque.git](https://github.com/Reumer/logitrack_gestao_estoque.git)
   cd logitrack_gestao_estoque