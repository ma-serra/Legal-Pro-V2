"""Ver estrutura da tabela processos"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Ver se tabela processos existe e suas colunas
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_name = 'processos'
    ORDER BY ordinal_position
""")

print("Colunas da tabela processos:")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[1]})")

cur.close()
conn.close()
