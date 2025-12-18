
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

EXPECTED = {
    5: 874,   # Tributária
    13: 400,  # Cível
    3: 297,   # Trabalhista
    10: 4,    # Penal
    15: 1,    # Constitucional
    4: 1,     # Previdenciária
    14: 145   # Administrativo
}

NAME_MAP = {
    5: 'Tributária',
    13: 'Cível',
    3: 'Trabalhista',
    10: 'Penal',
    15: 'Constitucional',
    4: 'Previdenciária',
    14: 'Administrativo'
}

def verify():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        with open('report_counts.txt', 'w', encoding='utf-8') as f:
            f.write("--- CONTAGEM POR NATUREZA ---\n")
            cur.execute("SELECT natureza_id, COUNT(*) as qtd FROM processos GROUP BY natureza_id ORDER BY qtd DESC")
            rows = cur.fetchall()
            
            total_banco = 0
            total_esperado = sum(EXPECTED.values())
            
            f.write(f"{'Natureza':<20} | {'ID':<5} | {'Encontrado':<10} | {'Esperado':<10} | {'Status'}\n")
            f.write("-" * 70 + "\n")
            
            found_ids = set()
            
            for r in rows:
                nid = r[0]
                qtd = r[1]
                found_ids.add(nid)
                total_banco += qtd
                
                exp = EXPECTED.get(nid, 0)
                name = NAME_MAP.get(nid, f"Unknown({nid})")
                
                status = "✅ OK" if qtd == exp else f"❌ DIF ({qtd-exp})"
                f.write(f"{name:<20} | {nid:<5} | {qtd:<10} | {exp:<10} | {status}\n")
                
            # Check missing expected categories
            for nid, exp in EXPECTED.items():
                if nid not in found_ids:
                    name = NAME_MAP.get(nid)
                    f.write(f"{name:<20} | {nid:<5} | {0:<10} | {exp:<10} | ❌ AUSENTE\n")

            f.write("-" * 70 + "\n")
            f.write(f"TOTAL: {total_banco} (Esperado: {total_esperado})\n")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    verify()
