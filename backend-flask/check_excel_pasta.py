
import pandas as pd
import psycopg2

# Ler Excel
EXCEL_PATH = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
df = pd.read_excel(EXCEL_PATH)

print(f"Colunas do Excel: {list(df.columns)}")
print(f"\nTotal de linhas: {len(df)}")

# Mostrar primeiras linhas da coluna pasta
if 'PASTA' in df.columns:
    col = 'PASTA'
elif 'Pasta' in df.columns:
    col = 'Pasta'
elif 'pasta' in df.columns:
    col = 'pasta'
else:
    print("\nColuna 'pasta' não encontrada diretamente.")
    # Listar colunas que contêm 'pasta'
    pasta_cols = [c for c in df.columns if 'pasta' in c.lower()]
    print(f"Colunas relacionadas: {pasta_cols}")
    col = None

if col:
    print(f"\nPrimeiros 10 valores da coluna '{col}':")
    print(df[col].head(10).tolist())
    
    # Contar NaN
    nan_count = df[col].isna().sum()
    print(f"\nValores NaN na coluna: {nan_count}")
