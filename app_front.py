import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="LogiTrack - Controle de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_PRODUCTS_URL = f"{API_BASE_URL}/products/"

# --- 2. CSS CUSTOMIZADO LIMPO ---
st.markdown("""
<style>
    .stApp { background-color: #F4F6FB; }
    section[data-testid="stSidebar"] {
        background-color: #161B33 !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    section[data-testid="stSidebar"] .stRadio label {
        padding: 10px 14px; border-radius: 10px; transition: background 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(99, 102, 241, 0.25);
    }
    .kpi-card {
        border-radius: 14px; padding: 18px 20px;
        display: flex; align-items: center; gap: 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04); margin-bottom: 10px;
    }
    .kpi-blue { background: linear-gradient(135deg, #EEF4FF 0%, #E0EAFF 100%); border: 1px solid #D0E0FF; }
    .kpi-green { background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #A7F3D0; }
    .kpi-orange { background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%); border: 1px solid #FED7AA; }
    .kpi-purple { background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%); border: 1px solid #DDD6FE; }
    .kpi-icon {
        width: 48px; height: 48px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; color: white; font-weight: bold;
    }
    .icon-blue { background-color: #3B82F6; }
    .icon-green { background-color: #10B981; }
    .icon-orange { background-color: #F97316; }
    .icon-purple { background-color: #7C3AED; }
    .kpi-value { font-size: 24px; font-weight: 800; color: #0F172A; line-height: 1.1; }
    .kpi-label { font-size: 13px; color: #475569; font-weight: 500; margin-top: 2px; }
    .white-box {
        background-color: #FFFFFF; border-radius: 14px; padding: 20px;
        border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03); margin-bottom: 16px;
    }
    .badge-normal { background-color: #DCFCE7; color: #15803D; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .badge-low { background-color: #FFEDD5; color: #C2410C; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .status-box {
        background-color: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; padding: 14px; margin-top: 30px; font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. FUNÇÃO DE FORMATAÇÃO DIRETA (EXATO COMO O USUÁRIO DIGITOU) ---
def format_currency_direct(valor):
    try:
        val = float(valor)
    except (ValueError, TypeError):
        val = 0.0
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_float_direct(texto):
    """Converte o texto digitado diretamente mantendo o valor exato (ex: 1500 vira 1500.00)"""
    if not texto:
        return 0.0
    # Remove símbolos de moeda e espaços
    limpo = str(texto).replace("R$", "").strip()
    # Se houver ponto e vírgula (ex: 1.500,00), remove ponto de milhar e troca vírgula por ponto
    if "." in limpo and "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def get_products():
    try:
        res = requests.get(API_PRODUCTS_URL, timeout=4)
        if res.status_code == 200:
            data = res.json()
            return data if isinstance(data, list) else [], True
    except Exception:
        pass
    return [], False


products, api_online = get_products()

normalized_products = []
for p in products:
    normalized_products.append({
        "id": p.get("id"),
        "codigo": f"PROD{int(p.get('id', 0)):03d}",
        "nome": p.get("name", p.get("nome", "Sem Nome")),
        "categoria": p.get("category", p.get("categoria", "Geral")),
        "preco": float(p.get("price", p.get("preco", 0.0))),
        "estoque": int(p.get("quantity", p.get("quantidade", 0))),
        "minimo": int(p.get("min_stock", p.get("estoque_minimo", 5)))
    })

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("## 📦 LogiTrack")
    st.caption("Gestão Inteligente de Estoque")
    st.markdown("---")

    pagina = st.radio(
        "Menu Principal",
        ["🏠 Dashboard", "📦 Produtos", "⬇️ Entradas", "⬆️ Saídas"],
        label_visibility="collapsed"
    )

    status_cor = "#22C55E" if api_online else "#EF4444"
    status_texto = "Sistema Online" if api_online else "API Desconectada"
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    st.markdown(f"""
        <div class="status-box">
            <div style="display:flex; align-items:center; gap:8px; font-weight:700; margin-bottom:4px;">
                <span style="width:10px; height:10px; border-radius:50%; background:{status_cor}; display:inline-block;"></span>
                {status_texto}
            </div>
            <div style="color:#94A3B8 !important; font-size:11px;">
                Última atualização:<br>{agora}
            </div>
        </div>
    """, unsafe_allow_html=True)

if "acao_rapida" not in st.session_state:
    st.session_state.acao_rapida = None

SENHA_MESTRE = "1234"  # Senha para exclusão de produtos

# --- 5. INDICADORES ---
total_skus = len(normalized_products)
total_unidades = sum(item["estoque"] for item in normalized_products)
valor_total_estoque = sum(item["estoque"] * item["preco"] for item in normalized_products)
itens_baixo_estoque = sum(1 for item in normalized_products if item["estoque"] <= item["minimo"])

# --- 6. CABEÇALHO ---
col_head_left, col_head_right = st.columns([3, 1])
with col_head_left:
    st.markdown("## 📦 Controle de Estoque")
    st.caption("Gerencie seus produtos, acompanhe o estoque e tome decisões com dados precisos.")
with col_head_right:
    busca_global = st.text_input("🔍 Pesquisar produtos...", placeholder="Digite a inicial (ex: C)...",
                                 label_visibility="collapsed")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f'<div class="kpi-card kpi-blue"><div class="kpi-icon icon-blue">📦</div><div><div class="kpi-value">{total_skus}</div><div class="kpi-label">Total de Produtos</div></div></div>',
        unsafe_allow_html=True)
with k2:
    st.markdown(
        f'<div class="kpi-card kpi-green"><div class="kpi-icon icon-green">📊</div><div><div class="kpi-value">{total_unidades:,}</div><div class="kpi-label">Unidades em Estoque</div></div></div>'.replace(
            ",", "."), unsafe_allow_html=True)
with k3:
    st.markdown(
        f'<div class="kpi-card kpi-orange"><div class="kpi-icon icon-orange">💰</div><div><div class="kpi-value" style="font-size:20px;">{format_currency_direct(valor_total_estoque)}</div><div class="kpi-label">Valor Patrimonial</div></div></div>',
        unsafe_allow_html=True)
with k4:
    st.markdown(
        f'<div class="kpi-card kpi-purple"><div class="kpi-icon icon-purple">⚠️</div><div><div class="kpi-value">{itens_baixo_estoque}</div><div class="kpi-label">Itens em Estoque Baixo</div></div></div>',
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# DASHBOARD
# ==============================================================================
if pagina == "🏠 Dashboard":
    col_tabela, col_lateral = st.columns([2.6, 1])

    with col_tabela:
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        t_col1, t_col2, t_col3 = st.columns([1.5, 2, 1.3])
        with t_col1:
            st.markdown("### 📦 Produtos")
        with t_col2:
            filtro_tabela = st.text_input("Buscar na tabela", value=busca_global,
                                          placeholder="🔍 Buscar produto (ex: C)...", label_visibility="collapsed")
        with t_col3:
            if st.button("➕ Cadastrar Produtos", type="primary", use_container_width=True):
                st.session_state.acao_rapida = "novo"

        lista_filtrada = normalized_products
        if filtro_tabela.strip():
            termo = filtro_tabela.strip().lower()
            comeca = [p for p in normalized_products if p["nome"].lower().startswith(termo)]
            contem = [p for p in normalized_products if
                      termo in p["nome"].lower() and not p["nome"].lower().startswith(termo)]
            lista_filtrada = comeca + contem

        if lista_filtrada:
            linhas_html = ""
            for item in lista_filtrada:
                status_badge = '<span class="badge-low">Baixo Estoque</span>' if item["estoque"] <= item[
                    "minimo"] else '<span class="badge-normal">Normal</span>'
                linhas_html += f"""
                <tr style="border-bottom: 1px solid #F1F5F9;">
                    <td style="padding: 12px 10px; font-weight:600; color:#475569;">{item['codigo']}</td>
                    <td style="padding: 12px 10px; font-weight:600; color:#0F172A;">{item['nome']}</td>
                    <td style="padding: 12px 10px; color:#64748B;">{format_currency_direct(item['preco'])}</td>
                    <td style="padding: 12px 10px; font-weight:700; color:#0F172A;">{item['estoque']}</td>
                    <td style="padding: 12px 10px;">{status_badge}</td>
                </tr>
                """
            st.markdown(
                f'<div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse; text-align:left; font-size:14px;"><thead><tr style="background-color:#F8FAFC; color:#475569; border-bottom:2px solid #E2E8F0;"><th style="padding:12px 10px;">Código</th><th style="padding:12px 10px;">Produto</th><th style="padding:12px 10px;">Preço Unit.</th><th style="padding:12px 10px;">Estoque</th><th style="padding:12px 10px;">Status</th></tr></thead><tbody>{linhas_html}</tbody></table></div>',
                unsafe_allow_html=True)
        else:
            st.info("Nenhum produto encontrado.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_lateral:
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.markdown("### ⚡ Ações Rápidas")

        if st.button("⬇️ Registrar Entrada", use_container_width=True):
            st.session_state.acao_rapida = "entrada"
        if st.button("⬆️ Registrar Saída", use_container_width=True):
            st.session_state.acao_rapida = "saida"
        if st.button("➕ Cadastrar Produtos", use_container_width=True):
            st.session_state.acao_rapida = "novo"

        if st.session_state.acao_rapida in ["entrada", "saida"]:
            st.markdown("---")
            tipo = st.session_state.acao_rapida
            st.markdown(f"**{'⬇️ Entrada' if tipo == 'entrada' else '⬆️ Saída'} de Estoque**")
            if normalized_products:
                filtro_prod = st.text_input("Filtrar por letra:", placeholder="Ex: C",
                                            key="filtro_acao").strip().lower()
                opcoes = [p for p in normalized_products if
                          not filtro_prod or p["nome"].lower().startswith(filtro_prod) or filtro_prod in p[
                              "nome"].lower()]
                if opcoes:
                    mapa_opcoes = {f"{p['nome']} (Atual: {p['estoque']})": p for p in opcoes}
                    escolha = st.selectbox("Selecione o produto:", list(mapa_opcoes.keys()))
                    prod_sel = mapa_opcoes[escolha]

                    if "qtd_mov_val" not in st.session_state:
                        st.session_state.qtd_mov_val = 1

                    b_sub10, b_sub1, b_add1, b_add10 = st.columns(4)
                    if b_sub10.button("-10"): st.session_state.qtd_mov_val = max(1, st.session_state.qtd_mov_val - 10)
                    if b_sub1.button("-1"):  st.session_state.qtd_mov_val = max(1, st.session_state.qtd_mov_val - 1)
                    if b_add1.button("+1"):  st.session_state.qtd_mov_val += 1
                    if b_add10.button("+10"): st.session_state.qtd_mov_val += 10

                    txt_qtd = st.text_input("Quantidade exata:", value=str(st.session_state.qtd_mov_val),
                                            key="txt_qtd_mov")
                    try:
                        st.session_state.qtd_mov_val = int("".join(filter(str.isdigit, txt_qtd)) or 1)
                    except:
                        st.session_state.qtd_mov_val = 1

                    if st.button("Confirmar Movimentação", type="primary", use_container_width=True):
                        nova_qtd = prod_sel["estoque"] + st.session_state.qtd_mov_val if tipo == "entrada" else max(0,
                                                                                                                    prod_sel[
                                                                                                                        "estoque"] - st.session_state.qtd_mov_val)
                        payload = {"name": prod_sel["nome"], "price": prod_sel["preco"], "quantity": nova_qtd,
                                   "min_stock": prod_sel["minimo"]}
                        r = requests.put(f"{API_PRODUCTS_URL}{prod_sel['id']}", json=payload)
                        if r.status_code == 200:
                            st.success("Atualizado!")
                            st.session_state.acao_rapida = None
                            st.rerun()

        elif st.session_state.acao_rapida == "novo":
            st.markdown("---")
            st.markdown("**➕ Cadastrar Produtos**")
            novo_nome = st.text_input("Nome do Produto", key="novo_nome_dash")

            # Preço direto sem conversão maluca
            raw_input = st.text_input("Preço (R$)", value="1500", placeholder="Ex: 1500", key="input_preco_ui")
            preco_final = parse_float_direct(raw_input)
            st.caption(irá := f"Valor interpretado: **{format_currency_direct(preco_final)}**")

            txt_q_ini = st.text_input("Quantidade Inicial", value="0", key="txt_q_ini_dash")
            qtd_inicial = int("".join(filter(str.isdigit, txt_q_ini)) or 0)

            txt_min = st.text_input("Estoque Mínimo", value="5", key="txt_min_dash")
            estoque_min = int("".join(filter(str.isdigit, txt_min)) or 5)

            if st.button("Cadastrar Produtos", type="primary", use_container_width=True):
                if novo_nome.strip():
                    payload = {"name": novo_nome.strip(), "price": preco_final, "quantity": qtd_inicial,
                               "min_stock": estoque_min}
                    r = requests.post(API_PRODUCTS_URL, json=payload)
                    if r.status_code in [200, 201]:
                        st.success("Cadastrado com sucesso!")
                        st.session_state.acao_rapida = None
                        st.rerun()
                else:
                    st.warning("Informe o nome.")

        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# PRODUTOS (ABA DEDICADA)
# ==============================================================================
elif pagina == "📦 Produtos":
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader("➕ Cadastrar Produtos")

    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    with c1:
        p_nome = st.text_input("Nome do Item", key="prod_nome_full")
    with c2:
        p_preco_raw = st.text_input("Preço (R$)", value="1500", key="prod_preco_full")
        p_preco = parse_float_direct(p_preco_raw)
        st.caption(f"Valor: **{format_currency_direct(p_preco)}**")
    with c3:
        p_qtd_txt = st.text_input("Qtd. Inicial", value="0", key="prod_qtd_txt")
        p_qtd = int("".join(filter(str.isdigit, p_qtd_txt)) or 0)
    with c4:
        p_min_txt = st.text_input("Estoque Mín.", value="5", key="prod_min_txt")
        p_min = int("".join(filter(str.isdigit, p_min_txt)) or 5)

    if st.button("Cadastrar Produtos", type="primary"):
        if p_nome.strip():
            payload = {"name": p_nome.strip(), "price": p_preco, "quantity": p_qtd, "min_stock": p_min}
            res = requests.post(API_PRODUCTS_URL, json=payload)
            if res.status_code in [200, 201]:
                st.success(f"'{p_nome}' salvo com sucesso!")
                st.rerun()
        else:
            st.warning("Digite o nome.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Gerenciar / Remover com Balão Compacto e Moderno (Popover)
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader("🗑️ Gerenciar / Remover Produtos")

    if normalized_products:
        for item in normalized_products:
            col_a, col_b, col_c, col_d = st.columns([2.5, 1.5, 1.5, 1])
            col_a.write(f"**{item['codigo']}** — {item['nome']}")
            col_b.write(format_currency_direct(item['preco']))
            col_c.write(f"{item['estoque']} un.")

            with col_d:
                with st.popover("Excluir 🗑️"):
                    st.markdown(f"Deseja excluir **{item['nome']}**?")
                    senha_digitada = st.text_input("Senha:", type="password", key=f"pwd_pop_{item['id']}")

                    if st.button("Confirmar Exclusão", key=f"conf_pop_{item['id']}", type="primary"):
                        if senha_digitada == SENHA_MESTRE:
                            requests.delete(f"{API_PRODUCTS_URL}{item['id']}")
                            st.success("Excluído!")
                            st.rerun()
                        else:
                            st.error("Senha incorreta!")
    else:
        st.info("Nenhum produto cadastrado.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ENTRADAS E SAÍDAS
# ==============================================================================
elif pagina in ["⬇️ Entradas", "⬆️ Saídas"]:
    eh_entrada = pagina == "⬇️ Entradas"
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.subheader("⬇️ Registrar Entrada" if eh_entrada else "⬆️ Registrar Saída")

    if normalized_products:
        busca_letra = st.text_input("🔍 Filtrar por letra inicial (ex: digite 'C'):", "").strip().lower()
        filtrados = [p for p in normalized_products if
                     not busca_letra or p["nome"].lower().startswith(busca_letra) or busca_letra in p["nome"].lower()]

        if filtrados:
            mapa = {f"{p['codigo']} - {p['nome']} (Estoque atual: {p['estoque']})": p for p in filtrados}
            selecionado = st.selectbox("Produto:", list(mapa.keys()))
            prod = mapa[selecionado]

            if "qtd_mov_main" not in st.session_state:
                st.session_state.qtd_mov_main = 1

            bs10, bs1, ba1, ba10 = st.columns(4)
            if bs10.button("-10", key="bm_10"): st.session_state.qtd_mov_main = max(1,
                                                                                    st.session_state.qtd_mov_main - 10)
            if bs1.button("-1", key="bm_1"):   st.session_state.qtd_mov_main = max(1, st.session_state.qtd_mov_main - 1)
            if ba1.button("+1", key="bp_1"):   st.session_state.qtd_mov_main += 1
            if ba10.button("+10", key="bp_10"): st.session_state.qtd_mov_main += 10

            txt_m = st.text_input("Quantidade:", value=str(st.session_state.qtd_mov_main), key="txt_m_val")
            try:
                st.session_state.qtd_mov_main = int("".join(filter(str.isdigit, txt_m)) or 1)
            except:
                st.session_state.qtd_mov_main = int(st.session_state.get('qtd_mov_main', 1))

            if st.button("Confirmar Lançamento", type="primary"):
                nova_qtd = prod["estoque"] + st.session_state.qtd_mov_main if eh_entrada else max(0, prod[
                    "estoque"] - st.session_state.qtd_mov_main)
                payload = {"name": prod["nome"], "price": prod["preco"], "quantity": nova_qtd,
                           "min_stock": prod["minimo"]}
                res = requests.put(f"{API_PRODUCTS_URL}{prod['id']}", json=payload)
                if res.status_code == 200:
                    st.success("Atualizado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum produto encontrado com essa letra.")
    st.markdown('</div>', unsafe_allow_html=True)