import psycopg2
db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM agente_juridico;")
print(f"Total: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM agente_juridico WHERE customizado = FALSE;")
print(f"Pre-configurados: {cur.fetchone()[0]}")
cur.execute("SELECT tipo, COUNT(*) FROM agente_juridico GROUP BY tipo;")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")
cur.close()
conn.close()
