
import pandas as pd
import psycopg2
import os

DB_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway")

def run_fix():
    print("Fixing Niche Areas (Constitucional, Previdenciário)...")
    try:
        df = pd.read_excel(r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        updates = 0
        
        for idx, row in df.iterrows():
            nat = str(row.get('natureza', '')).lower()
            target_id = None
            
            if 'constitu' in nat: target_id = 15
            elif 'previdenc' in nat: target_id = 4
            
            if target_id:
                cnj = row.get('numero_cnj')
                cnj_clean = str(cnj).strip() if pd.notna(cnj) else None
                
                if cnj_clean:
                    cur.execute("UPDATE processos SET natureza_id = %s WHERE numero_cnj = %s AND natureza_id != %s", (target_id, cnj_clean, target_id))
                    if cur.rowcount > 0:
                        updates += cur.rowcount
                        print(f"Fixed: {cnj_clean} -> ID {target_id}")
                        
        conn.commit()
        conn.close()
        print(f"Fixed {updates} records.")
        
    except Exception as e:
        print(f"Fix Error: {e}")

if __name__ == "__main__":
    run_fix()
