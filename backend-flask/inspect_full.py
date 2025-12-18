
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def inspect(table):
    print(f"--- TABLE: {table} ---")
    try:
        cur.execute(f"SELECT * FROM {table} LIMIT 0")
        for desc in cur.description:
            print(desc.name)
    except Exception as e:
        print(e)
        conn.rollback()

inspect("processo_tributario")
conn.close()
