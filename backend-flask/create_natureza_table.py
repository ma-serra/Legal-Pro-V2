
import psycopg2

DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

NATUREZAS = [
    (1, 'Tributária', 'Direito Tributário'),
    (2, 'Trabalhista', 'Direito Trabalhista'),
    (3, 'Cível', 'Direito Cível'),
    (4, 'Previdenciária', 'Direito Previdenciário'),
    (10, 'Penal', 'Direito Penal'),
    (14, 'Administrativo', 'Direito Administrativo'),
    (15, 'Constitucional', 'Direito Constitucional'),
]

def create_natureza_table():
    print("Criando tabela natureza_processo...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Criar tabela
    cur.execute("""
        CREATE TABLE IF NOT EXISTS natureza_processo (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descricao VARCHAR(255)
        )
    """)
    
    # Inserir valores
    for nat in NATUREZAS:
        cur.execute("""
            INSERT INTO natureza_processo (id, nome, descricao)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome, descricao = EXCLUDED.descricao
        """, nat)
        print(f"  ID {nat[0]}: {nat[1]}")
    
    conn.commit()
    conn.close()
    print("Tabela natureza_processo criada com sucesso!")

if __name__ == "__main__":
    create_natureza_table()
