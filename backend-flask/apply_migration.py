"""
Script para aplicar migration 003_ml_tributario_tables.sql
"""
import psycopg2
import sys

# Conexão Railway
DATABASE_URL = "postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway"

def apply_migration():
    """Aplica migration SQL"""
    try:
        # Conectar
        print("Conectando ao banco Railway...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Ler migration
        print("Lendo migration 003_ml_tributario_tables.sql...")
        with open('migrations/003_ml_tributario_tables.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Executar
        print("Executando migration...")
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Migration aplicada com sucesso!")
        
        # Verificar tabelas criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('ml_modelo_tributario', 'ml_predicao_tributario')
        """)
        tabelas = cursor.fetchall()
        print(f"Tabelas criadas: {[t[0] for t in tabelas]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    apply_migration()
