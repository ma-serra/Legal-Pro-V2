
import pandas as pd
import psycopg2
import os
import datetime
import numpy as np

# DB Configuration
DB_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway")

def clean_currency(value):
    if pd.isna(value) or value == '': return None
    try:
        if isinstance(value, (int, float)): return float(value)
        val = str(value).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        return float(val)
    except: return 0

def get_natureza_id(natureza_str):
    if pd.isna(natureza_str): return 1
    nat = str(natureza_str).lower()
    if 'tribut' in nat or 'fiscal' in nat: return 1
    if 'trabalh' in nat or 'reclama' in nat: return 2
    if 'civel' in nat or 'cível' in nat or 'civil' in nat: return 3
    if 'penal' in nat or 'crime' in nat: return 10
    if 'adm' in nat: return 14
    return 1

def run():
    print("Starting SQL-Only ETL...")
    try:
        df = pd.read_excel(r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx")
    except Exception as e:
        print(f"Excel read error: {e}")
        return

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # 1. Tenancy
        print("Ensuring Tenancy...")
        cur.execute("INSERT INTO tenancy (name, slug, domain, status) VALUES ('Legal Pro Hub', 'legal-pro-hub', 'app.legalprohub.com', 'active') ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name RETURNING id")
        tid = cur.fetchone()[0]
        conn.commit()
        
        # 2. Process Rows
        client_map = {}
        # Pre-load clients
        cur.execute("SELECT name, id FROM client WHERE tenancy_id = %s", (tid,))
        for r in cur.fetchall():
            client_map[r[0]] = r[1]
            
        count_new = 0
        count_exist = 0
        
        print(f"Processing {len(df)} rows...")
        
        for idx, row in df.iterrows():
            try:
                # Client
                c_name = str(row.get('cliente', 'Cliente Desconhecido')).strip()
                if c_name not in client_map:
                    cur.execute("INSERT INTO client (name, tenancy_id, status) VALUES (%s, %s, 'active') RETURNING id", (c_name, tid))
                    cid = cur.fetchone()[0]
                    client_map[c_name] = cid
                    conn.commit()
                else:
                    cid = client_map[c_name]
                
                # Natureza
                nat_id = get_natureza_id(row.get('natureza'))
                
                # Check Exists (CNJ)
                cnj = row.get('numero_cnj')
                cnj_clean = str(cnj).strip() if pd.notna(cnj) else None
                
                pid = None
                if cnj_clean:
                    cur.execute("SELECT id_processo FROM processos WHERE numero_cnj = %s", (cnj_clean,))
                    res = cur.fetchone()
                    if res: pid = res[0]
                
                if not pid:
                    # Insert Processo
                    pasta = f"PROC-{idx+1}-{datetime.datetime.now().microsecond}"
                    val = clean_currency(row.get('valor_causa'))
                    
                    cur.execute("""
                        INSERT INTO processos (numero_cnj, pasta, cliente_id, natureza_id, status_id, valor_causa, data_criacao, titulo, autor, reu, observacao_pasta)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s) RETURNING id_processo
                    """, (
                        cnj_clean,
                        pasta,
                        cid,
                        nat_id,
                        1, # Active
                        val,
                        str(row.get('titulo', f"Processo {c_name}"))[:255],
                        str(row.get('autor', ''))[:255],
                        str(row.get('reu', ''))[:255],
                        str(row.get('observacoes', ''))
                    ))
                    pid = cur.fetchone()[0]
                    count_new += 1
                    
                    # Insert Subtable
                    if nat_id == 1:
                        cur.execute("INSERT INTO processo_tributario (processo_id, valor_principal) VALUES (%s, %s) ON CONFLICT DO NOTHING", (pid, val))
                    elif nat_id == 2:
                        cur.execute("INSERT INTO processo_trabalhista (processo_id) VALUES (%s) ON CONFLICT DO NOTHING", (pid,))
                    elif nat_id == 3:
                        cur.execute("INSERT INTO processo_civel (processo_id) VALUES (%s) ON CONFLICT DO NOTHING", (pid,))
                    
                    conn.commit()
                else:
                    count_exist += 1
                    # Update natureza to fix misclassification
                    cur.execute("UPDATE processos SET natureza_id = %s WHERE id_processo = %s", (nat_id, pid))
                    conn.commit()
                    
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                conn.rollback()

        print(f"Done. New: {count_new}, Existing: {count_exist}")
        conn.close()

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    run()
