
import psycopg2
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT natureza_id, COUNT(*) FROM processos GROUP BY natureza_id ORDER BY natureza_id")
print("=== CONTAGEM POR NATUREZA ===")
for row in cur.fetchall():
    print(f"ID {row[0]}: {row[1]} processos")
cur.execute("SELECT COUNT(*) FROM processos")
print(f"\nTOTAL: {cur.fetchone()[0]}")
conn.close()
