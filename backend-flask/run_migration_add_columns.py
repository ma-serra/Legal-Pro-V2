
import psycopg2

DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def run_migration():
    print("Executando migração: Adicionando colunas faltantes...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    migrations = [
        "ALTER TABLE processos ADD COLUMN IF NOT EXISTS cliente_principal_nome VARCHAR(255)",
        "ALTER TABLE processos ADD COLUMN IF NOT EXISTS uf VARCHAR(2)",
        "ALTER TABLE processos ADD COLUMN IF NOT EXISTS cidade VARCHAR(100)",
        "ALTER TABLE processos ADD COLUMN IF NOT EXISTS uf_vara VARCHAR(2)",
    ]
    
    for sql in migrations:
        try:
            cur.execute(sql)
            print(f"✅ {sql.split('ADD COLUMN IF NOT EXISTS ')[1].split()[0]}")
        except Exception as e:
            print(f"⚠️ Erro: {e}")
    
    conn.commit()
    conn.close()
    print("\nMigração concluída!")

if __name__ == "__main__":
    run_migration()
