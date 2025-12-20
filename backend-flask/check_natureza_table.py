
import psycopg2
import os

DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("Checking tables related to 'natureza'...")
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%natureza%'")
    tables = cur.fetchall()
    print(tables)
    
    if tables:
        tname = tables[0][0]
        print(f"\nContents of {tname}:")
        cur.execute(f"SELECT * FROM {tname} ORDER BY id")
        rows = cur.fetchall()
        for r in rows:
            print(r)
            
    conn.close()
except Exception as e:
    print(e)
