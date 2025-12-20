
import pandas as pd
import psycopg2

# Ler Excel
EXCEL_PATH = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

print("Carregando Excel...")
df = pd.read_excel(EXCEL_PATH)

# Identificar coluna pasta
pasta_col = None
for c in df.columns:
    if 'pasta' in c.lower():
        pasta_col = c
        break

if not pasta_col:
    print("ERRO: Coluna 'pasta' não encontrada!")
    exit(1)

print(f"Coluna identificada: '{pasta_col}'")

# Conectar ao banco
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Buscar todos os processos ordenados por id_processo
cur.execute("SELECT id_processo, numero_cnj FROM processos ORDER BY id_processo")
processos_db = cur.fetchall()

print(f"\nAtualizando {len(processos_db)} registros...")

updated = 0
for i, (id_proc, cnj) in enumerate(processos_db):
    if i < len(df):
        pasta_excel = df.iloc[i][pasta_col]
        
        # Pular se for NaN
        if pd.isna(pasta_excel):
            pasta_excel = f"SEM-PASTA-{id_proc}"
        else:
            pasta_excel = str(pasta_excel).strip()
        
        cur.execute("UPDATE processos SET pasta = %s WHERE id_processo = %s", (pasta_excel, id_proc))
        updated += 1
        
        if updated % 200 == 0:
            conn.commit()
            print(f"  {updated} registros atualizados...")

conn.commit()
conn.close()

print(f"\n✅ Correção concluída! {updated} pastas atualizadas.")
