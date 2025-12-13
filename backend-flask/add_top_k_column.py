"""
Script para adicionar a coluna top_k à tabela agente_juridico
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def add_top_k_column():
    """Adiciona a coluna top_k à tabela agente_juridico."""
    try:
        # Conectar ao banco de dados
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='agente_juridico' AND column_name='top_k'
            """))
            
            if result.fetchone():
                print("✅ Coluna top_k já existe")
                return True
            
            # Adicionar a coluna top_k
            conn.execute(text("""
                ALTER TABLE agente_juridico 
                ADD COLUMN top_k INTEGER DEFAULT 50
            """))
            
            # Confirmar a transação
            conn.commit()
            print("✅ Coluna top_k adicionada com sucesso")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao adicionar coluna top_k: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adicionando coluna top_k à tabela agente_juridico...")
    success = add_top_k_column()
    
    if success:
        print("✅ Migração concluída com sucesso!")
    else:
        print("❌ Migração falhou!")