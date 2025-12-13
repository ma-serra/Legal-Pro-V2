"""
Script simplificado para ativar funcionalidades do Legal Design Pro
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração do banco
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def ativar_funcionalidades():
    """Ativa funcionalidades do Legal Design Pro"""
    session = Session()
    
    try:
        # Criar tabela de configurações
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS legal_design_config (
                id SERIAL PRIMARY KEY,
                feature_name VARCHAR(255) UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                config_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Limpar configurações existentes
        session.execute(text("DELETE FROM legal_design_config"))
        
        # Inserir funcionalidades
        funcionalidades = [
            ("elementos_graficos", True, "Repositório de elementos gráficos ativo"),
            ("templates_inteligentes", True, "Templates com IA ativados"),
            ("preview_visual", True, "Preview em tempo real ativo"),
            ("colaboracao", True, "Sistema de colaboração ativo"),
            ("ia_assistente", True, "Assistente de IA ativo"),
            ("exportacao_avancada", True, "Exportação multi-formato ativa"),
            ("legal_design_tools", True, "Ferramentas de design jurídico ativas"),
            ("timeline_processual", True, "Timeline de processos ativa"),
            ("graficos_tabelas", True, "Gráficos e tabelas ativas"),
            ("citacoes_automaticas", True, "Citações automáticas ativas")
        ]
        
        for nome, ativo, desc in funcionalidades:
            session.execute(text("""
                INSERT INTO legal_design_config (feature_name, enabled, config_data)
                VALUES (:nome, :ativo, :desc)
            """), {"nome": nome, "ativo": ativo, "desc": desc})
        
        session.commit()
        print("✅ Funcionalidades ativadas com sucesso")
        
        # Verificar ativação
        result = session.execute(text("SELECT feature_name, enabled FROM legal_design_config ORDER BY feature_name"))
        print("\n📋 Funcionalidades ativas:")
        for row in result:
            status = "✅" if row[1] else "❌"
            print(f"   {status} {row[0]}")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Ativando funcionalidades do Legal Design Pro...")
    ativar_funcionalidades()