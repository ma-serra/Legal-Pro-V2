"""
Script para adicionar colunas de configuração de fragmentação à tabela agente_juridico
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def add_fragmentacao_columns():
    """Adiciona as colunas de configuração de fragmentação."""
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return False
            
        engine = create_engine(database_url)
        
        # Lista de colunas para adicionar
        columns_to_add = [
            "modo_fragmentacao VARCHAR(20) DEFAULT 'geral'",
            "identificador_segmento VARCHAR(10) DEFAULT '\\n\\n'", 
            "comprimento_max_fragmento INTEGER DEFAULT 1024",
            "sobreposicao_blocos INTEGER DEFAULT 50",
            "comprimento_fragmento_filho INTEGER DEFAULT 512",
            "preprocessamento_texto BOOLEAN DEFAULT TRUE"
        ]
        
        with engine.connect() as conn:
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                
                # Verificar se a coluna já existe
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='agente_juridico' AND column_name=:column_name
                """), {"column_name": column_name})
                
                if result.fetchone():
                    print(f"✅ Coluna {column_name} já existe")
                    continue
                
                # Adicionar a coluna (usando interpolação segura)
                conn.execute(text("ALTER TABLE agente_juridico ADD COLUMN " + column_def))
                print(f"✅ Coluna {column_name} adicionada")
            
            conn.commit()
            print("✅ Todas as colunas de fragmentação foram processadas")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Erro ao adicionar colunas: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adicionando colunas de configuração de fragmentação...")
    success = add_fragmentacao_columns()
    
    if success:
        print("✅ Migração de fragmentação concluída!")
    else:
        print("❌ Migração falhou!")