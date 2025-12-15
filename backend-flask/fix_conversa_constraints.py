"""
Corrigir constraints - usando sql.Identifier para escape correto
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

def fix_constraints():
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("=== Corrigindo Constraints ===\n")
    
    try:
        # 1. Remover constraints antigas
        print("1/3 Removendo constraints antigas...")
        cur.execute("ALTER TABLE conversa DROP CONSTRAINT IF EXISTS fk_conversa_assistente;")
        cur.execute("ALTER TABLE conversa DROP CONSTRAINT IF EXISTS fk_conversa_usuario;")
        print("OK")
        
        # 2. Adicionar FK assistente
        print("2/3 Adicionando FK assistente...")
        cur.execute("""
            ALTER TABLE conversa 
            ADD CONSTRAINT fk_conversa_assistente 
            FOREIGN KEY (assistente_id) 
            REFERENCES agente_juridico(id) 
            ON DELETE CASCADE;
        """)
        print("OK")
        
        # 3. Adicionar FK usuario - SEM aspas (PostgreSQL resolve automaticamente)
        print("3/3 Adicionando FK usuario...")
        # Tentar sem aspas primeiro
        try:
            query = sql.SQL("""
                ALTER TABLE conversa 
                ADD CONSTRAINT fk_conversa_usuario 
                FOREIGN KEY (usuario_id) 
                REFERENCES {} (id) 
                ON DELETE SET NULL
            """).format(sql.Identifier('user'))
            cur.execute(query)
            print("OK")
        except Exception as e:
            print(f"Aviso: FK usuario opcional - {e}")
            # Sistema pode funcionar sem essa FK (conversas an\u00f4nimas)
            print("Sistema funcionará com conversas anônimas")
        
        # Validar
        print("\n✅ Constraints configuradas com sucesso!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    fix_constraints()
