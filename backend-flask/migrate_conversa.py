"""
Migration: Criar tabela conversa para histórico de conversas
Data: 2025-12-15
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway')

def run_migration():
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("=== Criando tabela conversa ===\n")
    
    try:
        # Criar tabela conversa
        print("1/4 Criando tabela conversa...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversa (
                id SERIAL PRIMARY KEY,
                assistente_id INTEGER NOT NULL,
                usuario_id INTEGER,
                titulo VARCHAR(200) NOT NULL,
                mensagens JSONB DEFAULT '[]'::jsonb,
                provider_usado VARCHAR(50),
                modelo_usado VARCHAR(100),
                arquivos_anexados JSON DEFAULT '[]'::json,
                data_criacao TIMESTAMP DEFAULT NOW(),
                data_atualizacao TIMESTAMP DEFAULT NOW(),
                ativa BOOLEAN DEFAULT TRUE
            );
        """)
        print("OK")
        
        # Adicionar foreign keys
        print("2/4 Adicionando foreign keys...")
        try:
            cur.execute("""
                ALTER TABLE conversa 
                ADD CONSTRAINT fk_conversa_assistente 
                FOREIGN KEY (assistente_id) REFERENCES agente_juridico(id) ON DELETE CASCADE;
            """)
        except Exception as e:
            print(f"Warning FK assistente: {e}")
        
        try:
            cur.execute("""
                ALTER TABLE conversa 
                ADD CONSTRAINT fk_conversa_usuario 
                FOREIGN KEY (usuario_id) REFERENCES \"user\"(id) ON DELETE SET NULL;
            """)
        except Exception as e:
            print(f"Warning FK usuario: {e}")
        print("OK")
        
        # Criar índices
        print("3/4 Criando índices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversa_assistente 
            ON conversa(assistente_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversa_usuario 
            ON conversa(usuario_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversa_ativa 
            ON conversa(ativa);
        """)
        print("OK")
        
        # Verificar
        print("4/4 Verificando...")
        cur.execute("SELECT COUNT(*) FROM conversa;")
        count = cur.fetchone()[0]
        print(f"OK - Tabela criada com {count} registros")
        
        print("\n=== Migration concluída com sucesso! ===")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
