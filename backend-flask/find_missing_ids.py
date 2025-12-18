
import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

DEFAULT_DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"
DB_URL = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)

def find_missing():
    try:
        # 1. Load Excel
        excel_path = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
        if not os.path.exists(excel_path):
            print("Excel not found.")
            return

        print("Lendo Excel...")
        df = pd.read_excel(excel_path)
        
        # Map CNJ -> List of IDs (to detect duplicates in excel)
        excel_map = {}
        for idx, row in df.iterrows():
            cnj = row.get('numero_cnj')
            if pd.isna(cnj) or not str(cnj).strip(): continue
            cnj = str(cnj).strip()
            row_id = row.get('id', idx+1)
            
            if cnj not in excel_map:
                excel_map[cnj] = []
            excel_map[cnj].append(row_id)
            
        print(f"Total CNJs únicos no Excel: {len(excel_map)}")
        print(f"Total linhas com CNJ no Excel: {sum(len(v) for v in excel_map.values())}")

        # 2. Load DB
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        print("Lendo Banco...")
        cur.execute("SELECT numero_cnj FROM processos")
        db_cnjs = set(row[0] for row in cur.fetchall())
        
        # 3. Compare
        missing = []
        duplicates = []
        
        for cnj, ids in excel_map.items():
            if cnj not in db_cnjs:
                missing.append({'cnj': cnj, 'ids': ids})
            
            if len(ids) > 1:
                duplicates.append({'cnj': cnj, 'ids': ids})
                
        # 4. Report
        with open('missing_ids_report.txt', 'w', encoding='utf-8') as f:
            f.write("=== RELATÓRIO DE DIVERGÊNCIAS ===\n")
            
            if duplicates:
                f.write(f"\n[DUPLICATAS NO EXCEL] (Foram unificadas no banco: {len(duplicates)} casos)\n")
                for item in duplicates:
                    f.write(f"CNJ: {item['cnj']} -> IDs Excel: {item['ids']}\n")
                    
            if missing:
                f.write(f"\n[NÃO IMPORTADOS] (Realmente faltam no banco: {len(missing)} casos)\n")
                for item in missing:
                    f.write(f"CNJ: {item['cnj']} -> IDs Excel: {item['ids']}\n")
            
            if not missing:
                f.write("\nTodos os CNJs do Excel estão presentes no Banco. As diferenças são apenas duplicatas.\n")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    find_missing()
