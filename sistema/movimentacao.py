import streamlit as st
from db import listar_produtos, registrar_venda, listar_vendas

def aba_movimentacao():
    st.header("🛒 Movimentação de Vendas")

    produtos = listar_produtos()
    nomes_produtos = [p[1] for p in produtos]

    if nomes_produtos:
        st.subheader("Registrar uma venda")
        with st.form("form_venda"):
            nome = st.selectbox("Produto", nomes_produtos)
            quantidade = st.number_input("Quantidade vendida", min_value=1, step=1)
            submitted = st.form_submit_button("Registrar venda")
            if submitted:
                try:
                    registrar_venda(nome, quantidade)
                    st.success(f"Venda registrada com sucesso: {quantidade}x {nome}")
                except ValueError as e:
                    st.error(str(e))
    else:
        st.info("Nenhum produto disponível no estoque para vender.")

    st.subheader("Histórico de Vendas")
    vendas = listar_vendas()
    if vendas:
        st.table([
            {
                "Produto": v[1],
                "Quantidade": v[2],
                "Valor Unitário": v[3],
                "Data": v[4]
            }
            for v in vendas
        ])
    else:
        st.info("Nenhuma venda registrada ainda.")
