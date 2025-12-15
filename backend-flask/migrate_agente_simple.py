"""
Migration: Adicionar novos campos ao AgenteJuridico - SEM EMOJIS
"""
import psycopg2
import os

def run_migration():
    """Executa a migration para adicionar novos campos"""
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERRO: DATABASE_URL nao encontrada")
        print("Por favor, configure a variavel de ambiente DATABASE_URL")
        return
    
    # Conectar ao banco
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Iniciando migration...")
    
    try:
        # 1. Adicionar coluna 'tipo'
        print("Adicionando coluna 'tipo'...")
        cur.execute("""
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'juridico';
        """)
        
        # 2. Adicionar coluna 'customizado'
        print("Adicionando coluna 'customizado'...")
        cur.execute("""
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS customizado BOOLEAN DEFAULT FALSE;
        """)
        
        # 3. Adicionar coluna 'prompt_template'
        print("Adicionando coluna 'prompt_template'...")
        cur.execute("""
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS prompt_template TEXT;
        """)
        
        # 4. Migrar dados
        print("Migrando dados de template_prompt para prompt_template...")
        cur.execute("""
            UPDATE agente_juridico 
            SET prompt_template = template_prompt 
            WHERE prompt_template IS NULL AND template_prompt IS NOT NULL;
        """)
        
        # 5. Adicionar coluna 'configuracoes_llm'
        print("Adicionando coluna 'configuracoes_llm'...")
        cur.execute("""
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS configuracoes_llm JSONB DEFAULT '{}'::jsonb;
        """)
        
        # 6. Popular configuracoes_llm
        print("Populando configuracoes_llm...")
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
        
        # 7. Adicionar coluna 'total_conversas'
        print("Adicionando coluna 'total_conversas'...")
        cur.execute("""
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS total_conversas INTEGER DEFAULT 0;
        """)
        
        # 8. Adicionar coluna 'created_by'
        print("Adicionando coluna 'created_by'...")
        cur.execute('''
            ALTER TABLE agente_juridico 
            ADD COLUMN IF NOT EXISTS created_by INTEGER;
        ''')
        
        # Adicionar foreign key depois
        print("Adicionando foreign key...")
        try:
            cur.execute('''
                ALTER TABLE agente_juridico 
                ADD CONSTRAINT fk_agente_created_by 
                FOREIGN KEY (created_by) REFERENCES "user"(id);
            ''')
        except Exception as fk_error:
            print(f"Warning: Foreign key may already exist: {fk_error}")
        
        # 9. Criar indices
        print("Criando indices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_agente_tipo 
            ON agente_juridico(tipo);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_agente_customizado 
            ON agente_juridico(customizado);
        """)
        
        conn.commit()
        print("\nMigration concluida com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERRO na migration: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
