
import psycopg2
import os
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'processos'")
    print(f"Total Columns: {cur.fetchone()[0]}")
    
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'processos'")
    print("Columns:")
    for r in cur.fetchall():
        print(f"- {r[0]} ({r[1]})")
    conn.close()
except Exception as e:
    print(e)
