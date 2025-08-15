import streamlit as st
from db import listar_vendas_com_itens
from datetime import datetime, date

def aba_fechamento():
    st.header("📆 Fechamento de Vendas do Dia")

    data_selecionada = st.date_input("Selecionar data", value=date.today())
    vendas = listar_vendas_com_itens()

    vendas_do_dia = {}
    for v in vendas:
        venda_id = v[0]
        data_venda = datetime.strptime(v[1], "%Y-%m-%d %H:%M:%S")
        if data_venda.date() == data_selecionada:
            if venda_id not in vendas_do_dia:
                vendas_do_dia[venda_id] = {
                    "data": v[1],
                    "total": v[2],
                    "itens": []
                }
            vendas_do_dia[venda_id]["itens"].append({
                "produto": v[3],
                "quantidade": v[4],
                "valor_unitario": v[5]
            })

    if vendas_do_dia:
        total_dia = sum([v["total"] for v in vendas_do_dia.values()])
        st.success(f"Total vendido em {data_selecionada.strftime('%d/%m/%Y')}: R$ {total_dia:.2f}")

        for venda_id, dados in sorted(vendas_do_dia.items(), reverse=True):
            st.markdown(f"**Venda #{venda_id}** - 🕒 {dados['data']} - 💰 Total: R$ {dados['total']:.2f}")
            for item in dados["itens"]:
                subtotal = item["quantidade"] * item["valor_unitario"]
                st.write(f"{item['quantidade']}x {item['produto']} - R$ {subtotal:.2f}")
            st.markdown("---")
    else:
        st.info("Nenhuma venda registrada nesta data.")
