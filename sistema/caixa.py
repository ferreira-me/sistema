import streamlit as st
from db import listar_produtos, registrar_venda

def aba_caixa():
    st.header("💰 Caixa (PDV)")

    produtos = listar_produtos()
    nomes_produtos = [p[1] for p in produtos]
    estoque_dict = {p[1]: {"estoque": p[2], "valor": p[3]} for p in produtos}

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    st.subheader("Adicionar item à venda")
    with st.form("form_caixa"):
        nome = st.selectbox("Produto", nomes_produtos)
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        adicionar = st.form_submit_button("Adicionar ao carrinho")

        if adicionar:
            if estoque_dict[nome]["estoque"] < quantidade:
                st.warning(f"Estoque insuficiente: disponível {estoque_dict[nome]['estoque']}")
            else:
                st.session_state.carrinho.append({
                    "nome": nome,
                    "quantidade": quantidade,
                    "valor_unitario": estoque_dict[nome]["valor"],
                    "subtotal": round(quantidade * estoque_dict[nome]["valor"], 2)
                })

    # Mostrar carrinho
    if st.session_state.carrinho:
        st.subheader("Itens no carrinho")
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"{item['quantidade']}x {item['nome']} - R$ {item['subtotal']:.2f}")
            total += item["subtotal"]

        st.success(f"Total: R$ {total:.2f}")
        if st.button("Finalizar venda"):
            try:
                for item in st.session_state.carrinho:
                    registrar_venda(item["nome"], item["quantidade"])
                st.success("Venda finalizada com sucesso!")
                st.session_state.carrinho = []
            except Exception as e:
                st.error(str(e))
    else:
        st.info("Nenhum item no carrinho.")
