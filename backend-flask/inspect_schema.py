
import os
import psycopg2
import logging

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def inspect(table):
    print(f"--- TABLE: {table} ---")
    try:
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
        rows = cur.fetchall()
        for r in rows:
            print(f"{r[0]} ({r[1]})")
    except Exception as e:
        print(e)
        conn.rollback()

inspect("processos")
inspect("processo_tributario")
inspect("client")
inspect("tenancy")
conn.close()
