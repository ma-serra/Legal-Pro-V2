"""
Verificar quantos assistentes foram realmente criados no banco
"""
import psycopg2
import os

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway')

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("=== Verificando Assistentes no Banco ===\n")

# Total de assistentes
cur.execute("SELECT COUNT(*) FROM agente_juridico;")
total = cur.fetchone()[0]
print(f"Total de assistentes: {total}")

# Por tipo
cur.execute("""
    SELECT tipo, COUNT(*) 
    FROM agente_juridico 
    GROUP BY tipo 
    ORDER BY COUNT(*) DESC;
""")
print("\nPor tipo:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Por customizado
cur.execute("""
    SELECT customizado, COUNT(*) 
    FROM agente_juridico 
    GROUP BY customizado;
""")
print("\nPor customizado:")
for row in cur.fetchall():
    customizado = "Sim" if row[0] else "Não"
    print(f"  {customizado}: {row[1]}")

# Primeiros 15 nomes
cur.execute("""
    SELECT id, nome, tipo 
    FROM agente_juridico 
    ORDER BY id 
    LIMIT 15;
""")
print("\nPrimeiros 15 assistentes:")
for row in cur.fetchall():
    print(f"  #{row[0]}: {row[1]} ({row[2]})")

cur.close()
conn.close()
