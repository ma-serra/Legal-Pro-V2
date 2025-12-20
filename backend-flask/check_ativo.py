
import psycopg2
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'processos' AND column_name = 'ativo'")
result = cur.fetchall()
print(f"Coluna 'ativo' existe: {len(result) > 0}")
print(result)
conn.close()
