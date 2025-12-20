
"""Corrigir titulo dos processos que estão como 'nan' usando cliente_principal_nome"""
import psycopg2

DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# 1. Corrigir processos com titulo 'nan' que têm cliente_principal_nome
cur.execute("""
    UPDATE processos 
    SET titulo = cliente_principal_nome
    WHERE (titulo = 'nan' OR titulo IS NULL OR titulo = '')
    AND cliente_principal_nome IS NOT NULL
    AND cliente_principal_nome != ''
    AND cliente_principal_nome != 'nan'
""")
print(f"Títulos corrigidos a partir de cliente_principal_nome: {cur.rowcount}")

# 2. Para os que ainda não têm titulo, usar autor X reu se disponíveis
cur.execute("""
    UPDATE processos 
    SET titulo = CASE 
        WHEN autor IS NOT NULL AND reu IS NOT NULL THEN autor || ' X ' || reu
        WHEN autor IS NOT NULL THEN autor
        WHEN reu IS NOT NULL THEN reu
        ELSE 'Processo ' || numero_cnj
    END
    WHERE (titulo = 'nan' OR titulo IS NULL OR titulo = '')
""")
print(f"Títulos corrigidos a partir de autor/reu/cnj: {cur.rowcount}")

conn.commit()

# Verificar os 2 processos específicos
cnjs = ['0265258-13.2023.3.00.0000', '5000096-27.2020.8.24.0052']
print("\n=== Verificação Final ===")
for cnj in cnjs:
    cur.execute("SELECT titulo, cliente_principal_nome, pasta FROM processos WHERE numero_cnj = %s", (cnj,))
    row = cur.fetchone()
    if row:
        print(f"\nCNJ: {cnj}")
        print(f"  Título: {row[0]}")
        print(f"  Cliente: {row[1]}")
        print(f"  Pasta: {row[2]}")

conn.close()
print("\n✅ Correção concluída!")
