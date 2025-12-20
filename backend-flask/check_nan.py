
import psycopg2
DB_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Verificar processos cíveis com titulo contendo 'nan'
cur.execute("""
    SELECT id_processo, titulo, natureza_id, autor, reu 
    FROM processos 
    WHERE natureza_id = 3 
    AND (titulo ILIKE '%nan%' OR titulo IS NULL OR titulo = 'nan')
    LIMIT 10
""")

print("Processos Cíveis com 'nan' no título:")
for row in cur.fetchall():
    print(f"ID: {row[0]} | Titulo: {row[1]} | Autor: {row[3]} | Reu: {row[4]}")

# Contar total
cur.execute("""
    SELECT COUNT(*) FROM processos 
    WHERE natureza_id = 3 
    AND (titulo ILIKE '%nan%' OR titulo IS NULL OR titulo = 'nan')
""")
print(f"\nTotal com problema: {cur.fetchone()[0]}")

conn.close()
