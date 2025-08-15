# C:\Users\Maria Eduarda\sistema\relatorios.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import listar_vendas_com_itens

def aba_relatorios():
    st.header("📊 Relatórios de Vendas")

    # 📅 Filtro de período
    hoje = date.today()
    inicio_default = hoje - timedelta(days=7)
    periodo = st.date_input(
        "Período",
        value=(inicio_default, hoje),
        help="Selecione a data inicial e final para filtrar as vendas."
    )

# Aceita tuple/list com 2 datas, 1 data, ou vazio
    data_ini, data_fim = inicio_default, hoje  # padrão
    if isinstance(periodo, (list, tuple)):
        if len(periodo) == 2 and periodo[0] and periodo[1]:
            data_ini, data_fim = periodo[0], periodo[1]
        elif len(periodo) == 1 and periodo[0]:
            data_ini = data_fim = periodo[0]
    elif periodo:  # caso Streamlit retorne um único date (não lista/tupla)
        data_ini = data_fim = periodo

# Se o usuário inverter (fim < ini), corrige
    if data_fim < data_ini:
        data_ini, data_fim = data_fim, data_ini


    # Busca dados
    vendas = listar_vendas_com_itens()  # [(id, data_venda, total, nome, qtd, valor)]
    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    # DataFrame
    df = pd.DataFrame(vendas, columns=[
        "venda_id", "data_venda", "valor_total_venda",
        "produto", "quantidade", "valor_unitario"
    ])
    # Converte datas e calcula subtotal do item
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    df["subtotal_item"] = df["quantidade"] * df["valor_unitario"]

    # Aplica filtro por período (00:00 até 23:59 do dia fim)
    mask = (df["data_venda"].dt.date >= data_ini) & (df["data_venda"].dt.date <= data_fim)
    dfp = df.loc[mask].copy()

    if dfp.empty:
        st.warning("Sem vendas no período selecionado.")
        return

    # Métricas
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("🧾 Nº de vendas", dfp["venda_id"].nunique())
    with col_b:
        st.metric("🛍️ Itens vendidos", int(dfp["quantidade"].sum()))
    with col_c:
        st.metric("💰 Faturamento (período)", f"R$ {dfp['subtotal_item'].sum():.2f}")

    st.markdown("### Detalhes por item")
    df_itens = dfp[["data_venda", "venda_id", "produto", "quantidade", "valor_unitario", "subtotal_item"]]
    df_itens = df_itens.sort_values(["data_venda", "venda_id"])
    st.dataframe(
        df_itens.rename(columns={
            "data_venda": "Data",
            "venda_id": "Venda",
            "produto": "Produto",
            "quantidade": "Qtd.",
            "valor_unitario": "Vlr Unit.",
            "subtotal_item": "Subtotal"
        }),
        use_container_width=True
    )

    st.markdown("### Resumo por produto")
    resumo = (
        dfp.groupby("produto", as_index=False)
           .agg(qtd_total=("quantidade", "sum"),
                faturamento=("subtotal_item", "sum"))
           .sort_values("faturamento", ascending=False)
    )
    st.dataframe(resumo.rename(columns={
        "produto": "Produto",
        "qtd_total": "Qtd. total",
        "faturamento": "Faturamento"
    }), use_container_width=True)

    # Exportar CSV
    csv = df_itens.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Baixar CSV (itens do período)",
        data=csv,
        file_name=f"relatorio_vendas_{data_ini}_a_{data_fim}.csv",
        mime="text/csv"
    )
