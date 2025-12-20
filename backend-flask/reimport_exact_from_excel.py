
"""
Re-importação COMPLETA dos dados do Excel para o banco.
Importa EXATAMENTE os valores da tabela, sem substituições automáticas.
"""
import pandas as pd
import psycopg2
import numpy as np

EXCEL_PATH = r"D:\Legal Pro Hub\Tabela_Processos_ETL.xlsx"
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def clean_value(val):
    """Limpa valor - converte NaN para None, e strip strings"""
    if pd.isna(val) or val == 'nan' or val == 'NaN':
        return None
    if isinstance(val, str):
        val = val.strip()
        if val == '' or val.lower() == 'nan':
            return None
    return val

def main():
    print("Carregando Excel...")
    df = pd.read_excel(EXCEL_PATH)
    print(f"Total de linhas: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    
    # Mapear colunas do Excel para colunas do banco
    # (ajustar conforme os nomes reais das colunas no Excel)
    column_map = {
        'pasta': ['pasta', 'PASTA', 'Pasta'],
        'numero_cnj': ['numero_cnj', 'cnj', 'CNJ', 'NUMERO_CNJ', 'Número CNJ'],
        'autor': ['autor', 'AUTOR', 'Autor', 'parte_autor', 'PARTE_AUTOR'],
        'reu': ['reu', 'REU', 'Reu', 'Réu', 'parte_reu', 'PARTE_REU'],
        'titulo': ['titulo', 'TITULO', 'Titulo', 'nome', 'NOME'],
    }
    
    # Encontrar colunas correspondentes
    found_cols = {}
    for db_col, excel_options in column_map.items():
        for opt in excel_options:
            if opt in df.columns:
                found_cols[db_col] = opt
                break
    
    print(f"\nColunas mapeadas: {found_cols}")
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Buscar processos ordenados
    cur.execute("SELECT id_processo FROM processos ORDER BY id_processo")
    ids = [r[0] for r in cur.fetchall()]
    
    print(f"\nAtualizando {len(ids)} registros com dados do Excel...")
    
    updated = 0
    for i, id_proc in enumerate(ids):
        if i >= len(df):
            break
            
        row = df.iloc[i]
        
        updates = []
        params = []
        
        # Para cada campo mapeado, pegar valor EXATO do Excel
        for db_col, excel_col in found_cols.items():
            val = clean_value(row[excel_col])
            updates.append(f"{db_col} = %s")
            params.append(val)
        
        if updates:
            params.append(id_proc)
            sql = f"UPDATE processos SET {', '.join(updates)} WHERE id_processo = %s"
            cur.execute(sql, params)
            updated += 1
        
        if updated % 200 == 0 and updated > 0:
            conn.commit()
            print(f"  {updated} registros atualizados...")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Reimportação completa! {updated} registros atualizados com dados EXATOS do Excel.")

if __name__ == "__main__":
    main()
