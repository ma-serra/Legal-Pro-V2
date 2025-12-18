
import os
import psycopg2
import logging
import uuid
from datetime import datetime

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    print("Checking processo_tributario structure...")
    cur.execute("SELECT * FROM processo_tributario LIMIT 0")
    print([desc.name for desc in cur.description])

    # Need a valid processo_id first
    cur.execute("SELECT id_processo FROM processos LIMIT 1")
    res = cur.fetchone()
    if not res:
        print("No process found to link to.")
        # Create dummy process?
        puuid = str(uuid.uuid4())
        cur.execute("INSERT INTO processos (uuid, numero_cnj, pasta, data_criacao, ativo) VALUES (%s, 'TEST-CNJ', 'TEST-PASTA', NOW(), true) RETURNING id_processo", (puuid,))
        proc_id = cur.fetchone()[0]
        print(f"Created temporary process {proc_id}")
    else:
        proc_id = res[0]
        print(f"Using process {proc_id}")

    print("Attempting INSERT...")
    cur.execute("""
        INSERT INTO processo_tributario (
            processo_id, valor_principal, numero_cda, numero_aiim,
            data_criacao, data_atualizacao
        ) VALUES (%s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (proc_id, 100.00, 'TEST-CDA', 'TEST-AIIM'))
    
    new_id = cur.fetchone()[0]
    print(f"INSERT SUCCESS. New ID: {new_id}")
    
    conn.rollback() # Don't keep junk
    print("Rolled back.")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    if 'conn' in locals(): conn.close()
