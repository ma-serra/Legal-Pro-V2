
import time
import psycopg2
import os
import subprocess
import sys

# Forçar output unbuffered
sys.stdout.reconfigure(line_buffering=True)

DB_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway")

def get_count():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM processos")
        cnt = cur.fetchone()[0]
        conn.close()
        return cnt
    except Exception as e:
        print(e)
        return 0

print("Monitor de Importação Iniciado...")
last_count = -1
stable_checks = 0

while True:
    cnt = get_count()
    print(f"Processos Importados: {cnt} / ~1718")
    
    if cnt >= 1710: # Perto do total
        if cnt == last_count:
            stable_checks += 1
        else:
            stable_checks = 0
            
        if stable_checks >= 4: # ~20s estável
            print(">>> Detecção de Finalização. Executando Scripts de Correção de Nicho...")
            subprocess.run(["python", "scripts/etl_fix_niche.py"], shell=True)
            print(">>> Verificação Final:")
            subprocess.run(["python", "verify_final_counts.py"], shell=True)
            break
    
    last_count = cnt
    time.sleep(5)
