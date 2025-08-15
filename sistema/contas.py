import streamlit as st
from db import adicionar_conta, listar_contas
from datetime import datetime, date

def aba_contas():
    st.header("📑 Contas a Pagar")

    st.subheader("Cadastrar nova conta")
    with st.form("form_conta"):
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
        vencimento = st.date_input("Data de vencimento", value=date.today())
        submitted = st.form_submit_button("Salvar")
        if submitted and descricao:
            adicionar_conta(descricao, valor, vencimento)
            st.success("Conta cadastrada com sucesso.")

    st.subheader("Contas registradas")
    contas = listar_contas()
    hoje = date.today()
    notificacoes = []

    if contas:
        linhas = []
        for c in contas:
            status = "VENCIDA" if datetime.strptime(c[3], "%Y-%m-%d").date() < hoje else "Em aberto"
            if status == "VENCIDA":
                notificacoes.append(f"{c[1]} - R$ {c[2]:.2f} (venc. {c[3]})")

            linhas.append({
                "Descrição": c[1],
                "Valor (R$)": f"{c[2]:.2f}",
                "Vencimento": c[3],
                "Status": status
            })

        st.table(linhas)
    else:
        st.info("Nenhuma conta registrada.")

    # Notificações na parte inferior
    if notificacoes:
        st.markdown("---")
        st.error("⚠️ Contas vencidas:")
        for alerta in notificacoes:
            st.markdown(f"- {alerta}")
