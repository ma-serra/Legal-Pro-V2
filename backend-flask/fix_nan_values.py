
import psycopg2
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Corrigir todos os campos que contêm 'nan' como string
fixes = [
    # Titulo
    ("UPDATE processos SET titulo = NULL WHERE titulo = 'nan'", "titulo"),
    # Autor
    ("UPDATE processos SET autor = NULL WHERE autor = 'nan'", "autor"),
    # Reu
    ("UPDATE processos SET reu = NULL WHERE reu = 'nan'", "reu"),
    # Cliente principal nome
    ("UPDATE processos SET cliente_principal_nome = NULL WHERE cliente_principal_nome = 'nan'", "cliente_principal_nome"),
    # Observacao
    ("UPDATE processos SET observacao_pasta = NULL WHERE observacao_pasta = 'nan'", "observacao_pasta"),
]

print("Corrigindo valores 'nan'...")
for sql, col in fixes:
    cur.execute(sql)
    print(f"  {col}: {cur.rowcount} registros corrigidos")

conn.commit()

# Gerar titulo automático para os que ficaram NULL
cur.execute("""
    UPDATE processos 
    SET titulo = COALESCE(autor, 'Processo') || ' X ' || COALESCE(reu, 'Parte')
    WHERE titulo IS NULL OR titulo = ''
""")
print(f"\nTítulos gerados automaticamente: {cur.rowcount}")

conn.commit()
conn.close()
print("\nCorreção concluída!")
