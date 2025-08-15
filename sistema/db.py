# db.py
import os, sqlite3

# Pasta de dados do usuário (Windows): C:\Users\<user>\AppData\Roaming\SISTEMA_CAIXA
APP_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SISTEMA_CAIXA")
os.makedirs(APP_DIR, exist_ok=True)
DB_PATH = os.path.join(APP_DIR, "caixa.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabela_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT,
            nome TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            estoque_minimo_personalizado INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# db.py  ── função central de cadastro/atualização
# ─── db.py ───
def adicionar_ou_atualizar_produto(codigo_barras, nome,
                                   quantidade, valor_unitario,
                                   estoque_minimo_personalizado=0):

    # ▸ 1. Normaliza entrada ─ transforma "" em None (NULL no banco)
    codigo_barras = (codigo_barras or '').strip()
    if codigo_barras == '':
        codigo_barras = None          # ← NULL não conflita com UNIQUE

    conn = conectar()
    cur  = conn.cursor()

    # ▸ 2. Procura primeiro pelo código-de-barras (se existir)
    if codigo_barras is not None:
        cur.execute("SELECT id FROM produtos WHERE codigo_barras = ?", (codigo_barras,))
    else:                             # senão, procura pelo NOME
        cur.execute("SELECT id FROM produtos WHERE nome = ?", (nome,))

    row = cur.fetchone()

    if row:                                        # → já existe: somar quantidade
        cur.execute("""
            UPDATE produtos
               SET quantidade                  = quantidade + ?,
                   valor_unitario              = ?,
                   nome                        = ?,
                   estoque_minimo_personalizado = ?
             WHERE id = ?
        """, (quantidade, valor_unitario, nome,
              estoque_minimo_personalizado, row[0]))
    else:                                          # → não existe: inserir
        cur.execute("""
            INSERT INTO produtos
                  (codigo_barras, nome, quantidade,
                   valor_unitario, estoque_minimo_personalizado)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo_barras, nome, quantidade,
              valor_unitario, estoque_minimo_personalizado))

    conn.commit()
    conn.close()



def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo_barras, nome, quantidade, valor_unitario, estoque_minimo_personalizado FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos





# Cria tabela de vendas
def criar_tabela_vendas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_produto TEXT NOT NULL,
            quantidade INTEGER,
            valor_unitario REAL,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

# Registrar uma venda
def registrar_venda(nome, quantidade):
    conn = conectar()
    cursor = conn.cursor()
    
    # Buscar valor e quantidade atuais do produto
    cursor.execute("SELECT quantidade, valor_unitario FROM produtos WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()
    if resultado:
        estoque_atual, valor_unitario = resultado
        if estoque_atual >= quantidade:
            # Registrar venda
            cursor.execute("""
                INSERT INTO vendas (nome_produto, quantidade, valor_unitario)
                VALUES (?, ?, ?)
            """, (nome, quantidade, valor_unitario))
            # Atualizar estoque
            cursor.execute("""
                UPDATE produtos SET quantidade = quantidade - ? WHERE nome = ?
            """, (quantidade, nome))
            conn.commit()
        else:
            conn.close()
            raise ValueError(f"Estoque insuficiente! Disponível: {estoque_atual}")
    else:
        conn.close()
        raise ValueError("Produto não encontrado.")
    conn.close()

# Listar vendas
def listar_vendas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendas ORDER BY data_venda DESC")
    vendas = cursor.fetchall()
    conn.close()
    return vendas
# Criação da tabela de contas
def criar_tabela_contas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL,
            vencimento DATE
        );
    """)
    conn.commit()
    conn.close()

# Adicionar uma conta
def adicionar_conta(descricao, valor, vencimento):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contas (descricao, valor, vencimento)
        VALUES (?, ?, ?)
    """, (descricao, valor, vencimento))
    conn.commit()
    conn.close()

# Listar todas as contas
def listar_contas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas ORDER BY vencimento ASC")
    contas = cursor.fetchall()
    conn.close()
    return contas
# NOVAS TABELAS
def criar_tabela_vendas_nova():
    conn = conectar()
    cur = conn.cursor()

    # vendas com status_pagamento e nome_cliente
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valor_total REAL,
            status_pagamento TEXT DEFAULT 'feito',
            nome_cliente TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            nome_produto TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            FOREIGN KEY(venda_id) REFERENCES vendas(id)
        );
    """)
    conn.commit()
    conn.close()


def garantir_colunas_pagamento():
    """Garante que colunas status_pagamento e nome_cliente existam na tabela vendas (migração)."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vendas)")
    cols = {row[1] for row in cur.fetchall()}

    if "status_pagamento" not in cols:
        cur.execute("ALTER TABLE vendas ADD COLUMN status_pagamento TEXT DEFAULT 'feito'")
    if "nome_cliente" not in cols:
        cur.execute("ALTER TABLE vendas ADD COLUMN nome_cliente TEXT")

    conn.commit()
    conn.close()




def registrar_venda_completa(carrinho, status_pagamento="feito", nome_cliente=None):
    conn = conectar()
    cur = conn.cursor()

    total = sum(item['quantidade'] * item['valor_unitario'] for item in carrinho)

    # Criar venda com status e cliente (cliente só se pendente)
    cur.execute(
        "INSERT INTO vendas (valor_total, status_pagamento, nome_cliente) VALUES (?, ?, ?)",
        (total, status_pagamento, nome_cliente if status_pagamento == "pendente" else None)
    )
    venda_id = cur.lastrowid

    for item in carrinho:
        cur.execute("""
            INSERT INTO itens_venda (venda_id, nome_produto, quantidade, valor_unitario)
            VALUES (?, ?, ?, ?)
        """, (venda_id, item['nome'], item['quantidade'], item['valor_unitario']))

        cur.execute("""
            UPDATE produtos SET quantidade = quantidade - ?
            WHERE nome = ?
        """, (item['quantidade'], item['nome']))

    conn.commit()
    conn.close()
def marcar_venda_como_paga(venda_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE vendas SET status_pagamento='feito' WHERE id=?", (venda_id,))
    conn.commit()
    conn.close()

def listar_vendas_pendentes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, data_venda, valor_total, nome_cliente FROM vendas WHERE status_pagamento='pendente' ORDER BY data_venda DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# Buscar histórico de vendas
def listar_vendas_com_itens():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT v.id, v.data_venda, v.valor_total, i.nome_produto, i.quantidade, i.valor_unitario
        FROM vendas v
        JOIN itens_venda i ON v.id = i.venda_id
        ORDER BY v.data_venda DESC
    """)
    vendas = cursor.fetchall()
    conn.close()
    return vendas

def atualizar_produto_por_id(id_produto, nome, quantidade, valor_unitario, estoque_minimo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos 
        SET nome = ?, quantidade = ?, valor_unitario = ?, estoque_minimo_personalizado = ?
        WHERE id = ?
    """, (nome, quantidade, valor_unitario, estoque_minimo, id_produto))
    conn.commit()
    conn.close()

def alterar_tabela_produtos():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN estoque_minimo_personalizado INTEGER DEFAULT 0")
    except:
        pass  # Já existe
    conn.commit()
    conn.close()

def criar_tabela_configuracoes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor INTEGER
        )
    """)

    # Inserir estoque mínimo padrão se ainda não existir
    cursor.execute("""
        INSERT OR IGNORE INTO configuracoes (chave, valor)
        VALUES ('estoque_minimo_padrao', 5)
    """)

    conn.commit()
    conn.close()
