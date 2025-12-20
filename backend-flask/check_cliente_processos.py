
"""Verificar e corrigir os 2 processos sem pasta com cliente principal"""
import pandas as pd
import psycopg2

EXCEL_PATH = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

# Processos a verificar
cnjs_alvo = ['0265258-13.2023.3.00.0000', '5000096-27.2020.8.24.0052']

print("=== Verificando processos no banco ===")
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

for cnj in cnjs_alvo:
    cur.execute("""
        SELECT id_processo, numero_cnj, pasta, titulo, autor, reu, cliente_principal_nome 
        FROM processos 
        WHERE numero_cnj = %s
    """, (cnj,))
    row = cur.fetchone()
    if row:
        print(f"\nCNJ: {row[1]}")
        print(f"  ID: {row[0]}")
        print(f"  Pasta: {row[2]}")
        print(f"  Título: {row[3]}")
        print(f"  Autor: {row[4]}")
        print(f"  Réu: {row[5]}")
        print(f"  Cliente Principal Nome: {row[6]}")
    else:
        print(f"\nCNJ {cnj}: NÃO ENCONTRADO")

print("\n=== Verificando no Excel ===")
df = pd.read_excel(EXCEL_PATH)

# Procurar pelas colunas relevantes
print(f"Colunas do Excel: {list(df.columns)[:15]}...")

# Buscar colunas de cliente
cliente_cols = [c for c in df.columns if 'cliente' in c.lower() or 'autor' in c.lower() or 'parte' in c.lower()]
print(f"Colunas de cliente: {cliente_cols}")

for cnj in cnjs_alvo:
    mask = df['numero_cnj'].astype(str) == cnj
    if mask.any():
        row = df[mask].iloc[0]
        print(f"\nCNJ: {cnj}")
        for col in cliente_cols:
            print(f"  {col}: {row[col]}")
        print(f"  titulo: {row.get('titulo', 'N/A')}")
    else:
        print(f"\nCNJ {cnj}: não encontrado no Excel")

conn.close()
