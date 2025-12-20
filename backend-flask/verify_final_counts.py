
import os
import psycopg2
import sys

# Alvo fornecido pelo usuário
TARGETS = {
    1: 874,   # Tributário
    2: 297,   # Trabalhista
    3: 397,   # Cível
    14: 145,  # Administrativo
    15: 1,    # Constitucional
    10: 3,    # Penal
    4: 1      # Previdenciário (Assumindo ID 4)
}

MAP_NAMES = {
    1: 'Tributária',
    2: 'Trabalhista',
    3: 'Cível',
    14: 'Administrativo',
    15: 'Constitucional',
    10: 'Penal',
    4: 'Previdenciária',
    5: 'LEGADO (Erro)',
    13: 'LEGADO (Erro)'
}

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def check():
    conn = psycopg2.connect(DEFAULT_DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT natureza_id, COUNT(*) FROM processos GROUP BY natureza_id")
    rows = cur.fetchall()
    
    print(f"{'Natureza':<20} | {'ID':<5} | {'Atual':<10} | {'Meta':<10} | {'Status'}")
    print("-" * 65)
    
    total_atual = 0
    total_meta = 0
    
    processed_ids = []
    
    for r in rows:
        nid = r[0]
        count = r[1]
        processed_ids.append(nid)
        name = MAP_NAMES.get(nid, f"Unknown({nid})")
        target = TARGETS.get(nid, 0)
        
        status = "✅ OK" if count == target else "⏳ Processando/Divergente"
        if nid == 5 or nid == 13: status = "❌ LEGADO (Falta Migrar)"
        
        print(f"{name:<20} | {nid:<5} | {count:<10} | {target:<10} | {status}")
        total_atual += count
        
    print("-" * 65)
    
    # Missing
    for tid, tcount in TARGETS.items():
        if tid not in processed_ids:
            name = MAP_NAMES.get(tid)
            print(f"{name:<20} | {tid:<5} | {0:<10} | {tcount:<10} | ⏳ Aguardando...")
            
    print(f"TOTAL: {total_atual}")
    conn.close()

if __name__ == "__main__":
    check()
