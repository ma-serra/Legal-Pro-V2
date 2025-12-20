
import os
import psycopg2
DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
try:
    conn = psycopg2.connect(DEFAULT_DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT natureza_id, COUNT(*) FROM processos GROUP BY natureza_id")
    print("Contagem Atual por Natureza:")
    for row in cur.fetchall():
        print(f"ID {row[0]}: {row[1]}")
    conn.close()
except Exception as e:
    print(e)
