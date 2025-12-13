"""
Script para adicionar a coluna config_json na tabela de prompts do assistente.
"""
import os
import logging
from sqlalchemy import create_engine, text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Adiciona a coluna config_json na tabela de prompts.
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
            # Verificar se a coluna já existe
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'assistente_prompt_templates' 
                AND column_name = 'config_json'
            """)
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            logger.info(f"Colunas existentes: {existing_columns}")
            
            # Adicionar coluna config_json se não existir
            if 'config_json' not in existing_columns:
                logger.info("Adicionando coluna config_json...")
                conn.execute(text("""
                    ALTER TABLE assistente_prompt_templates 
                    ADD COLUMN config_json TEXT DEFAULT '{}'
                """))
                
                conn.commit()
                logger.info("Migração concluída com sucesso!")
                return True
            else:
                logger.info("Coluna config_json já existe. Nada a fazer.")
                return True
            
    except Exception as e:
        logger.error(f"Erro ao executar migração: {e}")
        return False

if __name__ == "__main__":
    main()