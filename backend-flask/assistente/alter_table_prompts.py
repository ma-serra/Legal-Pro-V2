"""
Script para adicionar novas colunas na tabela de prompts do assistente.
"""
import os
import logging
from sqlalchemy import create_engine, text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Adiciona novas colunas para temperatura, top_p e top_k na tabela de prompts.
    """
    try:
        # Obter a URL do banco de dados das variáveis de ambiente
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL não encontrada nas variáveis de ambiente")
            return False
        
        # Criar engine
        engine = create_engine(database_url)
        
        # Conectar ao banco de dados
        with engine.connect() as conn:
            # Verificar se as colunas já existem
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'assistente_prompt_templates' 
                AND column_name IN ('temperatura', 'top_p', 'top_k')
            """)
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            logger.info(f"Colunas existentes: {existing_columns}")
            
            # Adicionar coluna temperatura se não existir
            if 'temperatura' not in existing_columns:
                logger.info("Adicionando coluna temperatura...")
                conn.execute(text("""
                    ALTER TABLE assistente_prompt_templates 
                    ADD COLUMN temperatura FLOAT DEFAULT 0.7
                """))
            
            # Adicionar coluna top_p se não existir
            if 'top_p' not in existing_columns:
                logger.info("Adicionando coluna top_p...")
                conn.execute(text("""
                    ALTER TABLE assistente_prompt_templates 
                    ADD COLUMN top_p FLOAT DEFAULT 0.9
                """))
            
            # Adicionar coluna top_k se não existir
            if 'top_k' not in existing_columns:
                logger.info("Adicionando coluna top_k...")
                conn.execute(text("""
                    ALTER TABLE assistente_prompt_templates 
                    ADD COLUMN top_k INTEGER DEFAULT 40
                """))
            
            conn.commit()
            
            logger.info("Migração concluída com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao executar migração: {e}")
        return False

if __name__ == "__main__":
    main()