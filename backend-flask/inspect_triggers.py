
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

def inspect_triggers(table):
    print(f"--- TRIGGERS: {table} ---")
    try:
        cur.execute(f"SELECT trigger_name, event_manipulation, action_statement FROM information_schema.triggers WHERE event_object_table = '{table}'")
        rows = cur.fetchall()
        for r in rows:
            print(f"{r}")
    except Exception as e:
        print(e)

inspect_triggers("processo_tributario")
conn.close()
