import streamlit as st
from db import (
    listar_produtos, registrar_venda_completa, listar_vendas_com_itens,
    listar_vendas_pendentes, marcar_venda_como_paga
)

def aba_movimentacao_caixa():
    st.header("🧾 Movimentação / Caixa (Venda Completa)")

    produtos = listar_produtos()
    if not produtos:
        st.info("Cadastre produtos no estoque primeiro.")
        return

    # p = (id, codigo_barras, nome, quantidade, valor_unitario, estoque_min)
    by_name = {p[2]: {"estoque": p[3], "valor": p[4], "codigo": p[1]} for p in produtos}
    by_code = {
        str(p[1]).strip(): {"nome": p[2], "estoque": p[3], "valor": p[4]}
        for p in produtos
        if p[1] is not None and str(p[1]).strip() != ""
    }
    nomes_produtos = list(by_name.keys())

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    st.subheader("Adicionar item à venda")
    with st.form("form_venda_completa"):
        codigo_input = st.text_input("Código de Barras (opcional) — use o leitor")
        nome_selecionado = st.selectbox("Produto", nomes_produtos)
        quantidade = st.number_input("Quantidade", min_value=1, step=1)

        # NOVO: status de pagamento
        status_pg = st.selectbox("Pagamento", ["Feito", "Pendente"], index=0)
        nome_cliente = None
        if status_pg == "Pendente":
            nome_cliente = st.text_input("Nome do cliente (obrigatório quando pendente)")

        adicionar = st.form_submit_button("Adicionar ao carrinho")

        if adicionar:
            # lookup por código se preenchido
            if codigo_input.strip():
                cod = codigo_input.strip()
                if cod in by_code:
                    nome = by_code[cod]["nome"]
                    estoque = by_code[cod]["estoque"]
                    valor = by_code[cod]["valor"]
                else:
                    st.error("Código de barras não encontrado.")
                    return
            else:
                nome = nome_selecionado
                estoque = by_name[nome]["estoque"]
                valor = by_name[nome]["valor"]

            if estoque < quantidade:
                st.warning(f"Estoque insuficiente: disponível {estoque}")
            else:
                st.session_state.carrinho.append({
                    "nome": nome,
                    "quantidade": int(quantidade),
                    "valor_unitario": float(valor)
                })
                # Guarda a escolha do pagamento para esta venda (fora dos itens)
                st.session_state.status_pagamento_atual = "pendente" if status_pg == "Pendente" else "feito"
                st.session_state.nome_cliente_atual = nome_cliente.strip() if nome_cliente else None
                st.success(f"{int(quantidade)}x {nome} adicionado ao carrinho.")

    # Carrinho
    if st.session_state.carrinho:
        st.subheader("Carrinho de Venda")
        total = 0.0
        for item in st.session_state.carrinho:
            subtotal = item["quantidade"] * item["valor_unitario"]
            total += subtotal
            st.write(f"{item['quantidade']}x {item['nome']} - R$ {subtotal:.2f}")
        info_pg = st.session_state.get("status_pagamento_atual", "feito")
        if info_pg == "pendente":
            cliente_show = st.session_state.get("nome_cliente_atual") or "(sem nome)"
            st.warning(f"Pagamento: PENDENTE — Cliente: {cliente_show}")
        else:
            st.info("Pagamento: FEITO")

        st.success(f"Total da venda: R$ {total:.2f}")

        if st.button("Finalizar venda"):
            try:
                status = st.session_state.get("status_pagamento_atual", "feito")
                cliente = st.session_state.get("nome_cliente_atual") if status == "pendente" else None

                if status == "pendente" and (not cliente or not cliente.strip()):
                    st.error("Informe o nome do cliente para vendas com pagamento pendente.")
                else:
                    registrar_venda_completa(st.session_state.carrinho, status, cliente)
                    st.success("Venda registrada com sucesso!")
                    st.session_state.carrinho = []
                    st.session_state.status_pagamento_atual = "feito"
                    st.session_state.nome_cliente_atual = None
            except Exception as e:
                st.error(str(e))
    else:
        st.info("Nenhum item no carrinho.")

    st.markdown("---")
    st.subheader("📚 Histórico de Vendas")
    vendas = listar_vendas_com_itens()
    if vendas:
        for venda_id in sorted({v[0] for v in vendas}, reverse=True):
            st.markdown(f"**Venda #{venda_id}**")
            for v in [v for v in vendas if v[0] == venda_id]:
                st.write(f"{v[4]}x {v[3]} - R$ {v[5]:.2f}")
            total = next(v[2] for v in vendas if v[0] == venda_id)
            data = next(v[1] for v in vendas if v[0] == venda_id)
            st.caption(f"🕒 {data} | 💰 Total: R$ {total:.2f}")
            st.markdown("---")
    else:
        st.info("Nenhuma venda registrada ainda.")

    st.subheader("🧾 Pagamentos Pendentes")
    pendentes = listar_vendas_pendentes()
    if pendentes:
        for vid, data, total, cliente in pendentes:
            cols = st.columns([6, 3, 3])
            with cols[0]:
                st.write(f"**#{vid}** — {data} — Cliente: {cliente or '(sem nome)'}")
            with cols[1]:
                st.write(f"Total: R$ {total:.2f}")
            with cols[2]:
                if st.button("Marcar como pago", key=f"paga_{vid}"):
                    marcar_venda_como_paga(vid)
                    st.success(f"Venda #{vid} marcada como paga.")
                    st.rerun()
    else:
        st.info("Nenhum pagamento pendente.")
