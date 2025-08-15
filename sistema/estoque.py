import streamlit as st
from db import listar_produtos, conectar, atualizar_produto_por_id, adicionar_ou_atualizar_produto
import os

# Pasta de dados do usuário + arquivo global
APP_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SISTEMA_CAIXA")
os.makedirs(APP_DIR, exist_ok=True)
ESTOQUE_GLOBAL_PATH = os.path.join(APP_DIR, "estoque_minimo_global.txt")


# 🟢 Funções para controle de estoque mínimo global
def obter_estoque_minimo_global():
    if os.path.exists(ESTOQUE_GLOBAL_PATH):
        with open(ESTOQUE_GLOBAL_PATH, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def definir_estoque_minimo_global(valor):
    with open(ESTOQUE_GLOBAL_PATH, "w") as f:
        f.write(str(valor))

# 🟢 Função principal da aba de estoque
def aba_estoque():
    st.header("📦 Estoque de Produtos")

    # ➕ Formulário de cadastro
    st.subheader("Cadastrar novo produto")
    with st.form("form_produto"):
        codigo_barras = st.text_input("Código de Barras (use o leitor)")
        nome = st.text_input("Nome do produto")
        quantidade = st.number_input("Quantidade", min_value=0, step=1)
        valor = st.number_input("Valor unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
        estoque_minimo_personalizado = st.number_input("Estoque mínimo (opcional)", min_value=0, step=1)
        submitted = st.form_submit_button("Salvar")
        if submitted and nome:
            adicionar_ou_atualizar_produto(codigo_barras, nome, quantidade, valor, estoque_minimo_personalizado)
            st.success(f"Produto '{nome}' salvo com sucesso!")
            st.rerun()



    # 📋 Tabela com produtos
    st.subheader("Produtos cadastrados")
    produtos = listar_produtos()

    estoque_global_atual = obter_estoque_minimo_global()
    if not produtos:
        st.info("Nenhum produto cadastrado ainda.")
        return

    # Cabeçalhos da tabela
    colunas = st.columns([2, 3, 2, 2, 2, 1])
    with colunas[0]: st.markdown("**Código de Barras**")
    with colunas[1]: st.markdown("**Produto**")
    with colunas[2]: st.markdown("**Quantidade**")
    with colunas[3]: st.markdown("**Valor Unitário (R$)**")
    with colunas[4]: st.markdown("**Estoque Mínimo**")
    with colunas[5]: st.markdown("**Ações**")



    for produto in produtos:
        id_produto, cod_barras, nome, quantidade, valor_unit, estoque_min = produto

        if st.session_state.get("editar_id") == id_produto:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 2, 2, 1])
            with col1:
                st.text_input("Código de Barras", cod_barras, disabled=True, label_visibility="collapsed")
            with col2:
                novo_nome = st.text_input("Nome", value=nome, key=f"nome_{id_produto}", label_visibility="collapsed")
            with col3:
                nova_quantidade = st.number_input("Quantidade", value=quantidade, key=f"qtd_{id_produto}", step=1, min_value=0, label_visibility="collapsed")
            with col4:
                novo_valor = st.number_input("Valor", value=valor_unit, key=f"val_{id_produto}", step=0.01, format="%.2f", min_value=0.0, label_visibility="collapsed")
            with col5:
                novo_estoque_min = st.number_input("Est. Mín.", value=estoque_min, key=f"est_{id_produto}", step=1, min_value=0, label_visibility="collapsed")
            with col6:
                if st.button("💾", key=f"salvar_{id_produto}"):
                    atualizar_produto_por_id(id_produto, novo_nome, nova_quantidade, novo_valor, novo_estoque_min)
                    del st.session_state["editar_id"]
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()

                if st.button("❌", key=f"cancelar_{id_produto}"):
                    del st.session_state["editar_id"]
                    st.rerun()

        else:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 2, 2, 1])
            with col1: st.write(cod_barras)
            with col2: st.write(nome)
            with col3: st.write(quantidade)
            with col4: st.write(f"R$ {valor_unit:.2f}")
            with col5:
                if estoque_min > 0:
                    st.write(estoque_min)
                else:
                    st.write(f"Global: {estoque_global_atual}")
            with col6:
                if st.button("✏️", key=f"editar_{id_produto}"):
                    st.session_state["editar_id"] = id_produto


def aba_configuracao_estoque_minimo():
    st.subheader("⚙️ Configurar Estoque Mínimo")
    estoque_minimo = st.number_input("Definir valor global mínimo para todos os produtos", min_value=0, step=1, value=obter_estoque_minimo_global())
    if st.button("Salvar configuração global"):
        definir_estoque_minimo_global(estoque_minimo)
        st.success("Estoque mínimo global atualizado com sucesso!")

def aba_alerta_estoque_minimo():
    st.subheader("🚨 Produtos com Estoque Mínimo Atingido")

    produtos = listar_produtos()
    estoque_min_global = obter_estoque_minimo_global()
    alerta = []

    for produto in produtos:
        _, cod_barras, nome, quantidade, _, estoque_min = produto
        estoque_minimo_efetivo = estoque_min if estoque_min > 0 else estoque_min_global
        if quantidade <= estoque_minimo_efetivo:
            alerta.append((cod_barras, nome, quantidade, estoque_minimo_efetivo))

    if not alerta:
        st.success("Nenhum produto abaixo do estoque mínimo.")
        return

    for cod_barras, nome, qtd, min_estoque in alerta:
        st.error(f"⚠️ {nome} ({cod_barras}) - Quantidade atual: {qtd}, Mínimo: {min_estoque}")
