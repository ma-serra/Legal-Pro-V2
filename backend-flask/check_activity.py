
import psycopg2
import os

DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT pid, state, query, wait_event_type, wait_event FROM pg_stat_activity WHERE state != 'idle' AND pid != pg_backend_pid()")
    rows = cur.fetchall()
    print("Active Queries:")
    for r in rows:
        print(f"PID: {r[0]} | State: {r[1]} | Wait: {r[3]}/{r[4]}")
        print(f"Query: {r[2]}")
        print("-" * 20)
    conn.close()
except Exception as e:
    print(e)
