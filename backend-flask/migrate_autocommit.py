"""
Migration com AUTOCOMMIT para evitar problemas de transacao
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def run_migration():
    """Executa a migration com autocommit"""
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERRO: DATABASE_URL nao encontrada")
        return
    
    # Conectar com autocommit
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("Iniciando migration com autocommit...")
    
    try:
        # 1. Tipo
        print("1/8 Adicionando coluna 'tipo'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'juridico';")
        print("OK")
        
        # 2. Customizado
        print("2/8 Adicionando coluna 'customizado'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS customizado BOOLEAN DEFAULT FALSE;")
        print("OK")
        
        # 3. Prompt template
        print("3/8 Adicionando coluna 'prompt_template'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS prompt_template TEXT;")
        print("OK")
        
        # 4. Migrar dados
        print("4/8 Migrando dados de template_prompt...")
        cur.execute("UPDATE agente_juridico SET prompt_template = template_prompt WHERE prompt_template IS NULL AND template_prompt IS NOT NULL;")
        print("OK")
        
        # 5. Configuracoes LLM
        print("5/8 Adicionando coluna 'configuracoes_llm'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS configuracoes_llm JSONB DEFAULT '{}'::jsonb;")
        print("OK")
        
        # 6. Popular configuracoes
        print("6/8 Populando configuracoes_llm...")
        cur.execute("""
            UPDATE agente_juridico 
            SET configuracoes_llm = jsonb_build_object(
                'llm_provider', 'openai',
                'llm_model', COALESCE(modelo_ai, 'gpt-4o'),
                'temperatura', COALESCE(temperatura, 0.3),
                'parametros', '{}'::jsonb,
                'modo_debug', false,
                'sempre_executar', true,
                'timeout', 120,
                'max_tokens', COALESCE(max_tokens, 8000)
            )
            WHERE configuracoes_llm = '{}'::jsonb OR configuracoes_llm IS NULL;
        """)
        print("OK")
        
        # 7. Total conversas
        print("7/8 Adicionando coluna 'total_conversas'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS total_conversas INTEGER DEFAULT 0;")
        print("OK")
        
        # 8. Created by (sem FK por enquanto)
        print("8/8 Adicionando coluna 'created_by'...")
        cur.execute("ALTER TABLE agente_juridico ADD COLUMN IF NOT EXISTS created_by INTEGER;")
        print("OK")
        
        # Indices
        print("Criando indices...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agente_tipo ON agente_juridico(tipo);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_agente_customizado ON agente_juridico(customizado);")
        print("OK")
        
        print("\n=== Migration concluida com sucesso! ===")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
