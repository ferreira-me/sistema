import streamlit as st
from relatorios import aba_relatorios

from db import (
    criar_tabela_produtos,
    criar_tabela_vendas,
    criar_tabela_vendas_nova,
    criar_tabela_contas,
    alterar_tabela_produtos,
    criar_tabela_configuracoes,
    garantir_colunas_pagamento
)

from estoque import (
    aba_estoque,
    aba_configuracao_estoque_minimo,
    aba_alerta_estoque_minimo
)

from movimentacao_caixa import aba_movimentacao_caixa
from fechamento import aba_fechamento
from contas import aba_contas

# Criar tabelas no início
criar_tabela_produtos()
criar_tabela_contas()
criar_tabela_vendas_nova()
alterar_tabela_produtos()
criar_tabela_configuracoes()
garantir_colunas_pagamento()  
# Menu lateral principal
st.sidebar.title("📋 Menu do Sistema de Caixa")
aba = st.sidebar.selectbox("Escolha uma aba:", ["Estoque", "Movimentação / Caixa", "Fechamento", "Contas a Pagar", "Relatórios"])

# Direcionamento
if aba == "Estoque":
    subaba = st.sidebar.radio("Função do Estoque:", ["📦 Controle de Produtos", "⚙️ Configurar Estoque Mínimo", "🚨 Alerta Estoque Mínimo"])

    if subaba == "📦 Controle de Produtos":
        aba_estoque()
    elif subaba == "⚙️ Configurar Estoque Mínimo":
        aba_configuracao_estoque_minimo()
    elif subaba == "🚨 Alerta Estoque Mínimo":
        aba_alerta_estoque_minimo()

elif aba == "Movimentação / Caixa":
    aba_movimentacao_caixa()

elif aba == "Fechamento":
    aba_fechamento()

elif aba == "Contas a Pagar":
    aba_contas()

elif aba == "Relatórios":
    aba_relatorios()
