
import pandas as pd
import psycopg2

EXCEL_PATH = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

# Ler Excel
df = pd.read_excel(EXCEL_PATH)

# Procurar pelos 2 CNJs problemáticos
cnjs = ['5000096-27.2020.8.24.0052', '0265258-13.2023.3.00.0000']

print("=== Dados no Excel ===")
for cnj in cnjs:
    # Encontrar nas colunas possíveis
    cnj_cols = [c for c in df.columns if 'cnj' in c.lower() or 'numero' in c.lower()]
    if cnj_cols:
        match = df[df[cnj_cols[0]].astype(str).str.contains(cnj.replace('-', '').replace('.', ''), na=False)]
        if len(match) == 0:
            # Tentar busca mais flexível
            for col in df.columns:
                match = df[df[col].astype(str).str.contains(cnj[:10], na=False)]
                if len(match) > 0:
                    break
        
        if len(match) > 0:
            print(f"\nCNJ: {cnj}")
            row = match.iloc[0]
            for col in ['autor', 'reu', 'Autor', 'Reu', 'AUTOR', 'REU', 'parte_autor', 'parte_reu', 'cliente', 'titulo', 'pasta']:
                if col in df.columns:
                    print(f"  {col}: {row.get(col, 'N/A')}")
        else:
            print(f"\nCNJ {cnj}: NÃO ENCONTRADO no Excel")

# Verificar no banco
print("\n=== Dados no Banco ===")
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
for cnj in cnjs:
    cur.execute("SELECT id_processo, numero_cnj, pasta, titulo, autor, reu, cliente_principal_nome FROM processos WHERE numero_cnj ILIKE %s", (f'%{cnj[:10]}%',))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"\nID: {r[0]} | CNJ: {r[1]}")
            print(f"  Pasta: {r[2]}")
            print(f"  Titulo: {r[3]}")
            print(f"  Autor: {r[4]}")
            print(f"  Reu: {r[5]}")
            print(f"  Cliente Nome: {r[6]}")
conn.close()
