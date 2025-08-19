import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Carregamento do arquivo de configuração (usuários e senhas)
# Se o arquivo não existir, ele será criado com um usuário inicial
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    # Criação de um arquivo de configuração inicial
    config = {
        'cookie': {
            'expiry_days': 30,
            'key': 'some_random_key_after_password_hashing',
            'name': 'some_cookie_name'
        },
        'credentials': {
            'usernames': {
                'admin': {
                    'email': 'admin@example.com',
                    'name': 'Admin',
                    'password': 'admin_password'  # A senha será hashada na primeira execução
                }
            }
        },
        'preauthorized': {
            'emails': ['']
        }
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    st.warning("Arquivo 'config.yaml' criado. Execute o app novamente para hashing da senha.")
    st.stop()


# --- O restante do seu código de imports deve vir aqui ---
from relatorios import aba_relatorios
from db import (
    criar_tabela_produtos,
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


# --- Criação da instância do autenticador ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Página de login ---
name, authentication_status, username = authenticator.login('Login', 'main')

# --- Verificação de status ---
if authentication_status:
    # Se autenticado, exibe o nome do usuário e o botão de logout
    st.sidebar.title(f"Bem-vindo, {name}")
    authenticator.logout('Sair', 'sidebar')

    # ----------------------------------------------------
    # SEU CÓDIGO ATUAL COMEÇA AQUI
    # ----------------------------------------------------
    
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

elif authentication_status == False:
    st.error('Usuário/senha incorretos')

elif authentication_status == None:
    st.warning('Por favor, digite seu usuário e senha')

    # --- Adicionar formulário de registro de novos usuários ---
    st.markdown("---")
    st.subheader("Não tem uma conta? Cadastre-se.")
    try:
        if authenticator.register_user('Registrar usuário', 'main'):
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('Usuário registrado com sucesso! Por favor, faça o login.')
    except Exception as e:
        st.error(e)
