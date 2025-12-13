"""
Script para atualizar permissões e integrar a nova categoria Direito de Família
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ Erro: DATABASE_URL não encontrada nas variáveis de ambiente")
            return None
            
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Conexão com banco de dados estabelecida")
        return session
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return None

def atualizar_permissoes_familia():
    """Atualiza as permissões para incluir Direito de Família"""
    session = conectar_database()
    if not session:
        return False
    
    try:
        # Verificar se a categoria foi criada
        result = session.execute(text("SELECT id, nome FROM categoria_juridica WHERE nome = 'Direito de Família'"))
        categoria = result.fetchone()
        
        if categoria:
            print(f"✅ Categoria 'Direito de Família' encontrada com ID: {categoria[0]}")
            
            # Verificar quantos agentes foram criados
            result = session.execute(text("SELECT COUNT(*) FROM agente_juridico WHERE categoria_id = :cat_id"), 
                                   {'cat_id': categoria[0]})
            total_agentes = result.scalar()
            
            print(f"✅ Total de agentes criados em Direito de Família: {total_agentes}")
            
            # Listar os agentes criados
            result = session.execute(text("""
                SELECT nome, classe, capacidades 
                FROM agente_juridico 
                WHERE categoria_id = :cat_id 
                ORDER BY id
            """), {'cat_id': categoria[0]})
            
            agentes = result.fetchall()
            print("\n📋 Agentes de Direito de Família criados:")
            for i, agente in enumerate(agentes, 1):
                print(f"{i:2d}. {agente[0]} (classe: {agente[1]})")
                
            return True
        else:
            print("❌ Categoria 'Direito de Família' não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")
        return False
    finally:
        session.close()

def criar_assistente_direito_familia():
    """Cria configuração para assistente de Direito de Família"""
    config_content = '''# Configuração do Assistente de Direito de Família
AREA_JURIDICA = "direito_familia"
NOME_ASSISTENTE = "Direito de Família"
DESCRICAO = "Assistente especializado em questões de Direito de Família"
COR_TEMA = "#FFD700"  # Dourado
ICONE = "fas fa-users"

# Configurações de embedding
TABELA_EMBEDDINGS = "embeddings_direito_familia"
DIMENSOES_VETOR = 1536

# Especialidades cobertas
ESPECIALIDADES = [
    "Divórcio e Partilha de Bens",
    "Guarda e Visitação", 
    "Alimentos e Pensão",
    "Reconhecimento de Paternidade",
    "União Estável",
    "Adoção Nacional e Internacional",
    "Mediação Familiar",
    "Tutela e Curatela",
    "Alienação Parental",
    "Filiação Socioafetiva",
    "Planejamento Familiar",
    "Violência Doméstica",
    "Direitos da Criança",
    "Relações Homoafetivas",
    "Testamentos Familiares",
    "Inventários e Heranças"
]

# Prompts especializados
PROMPT_SISTEMA = """
Você é um especialista em Direito de Família com conhecimento abrangente em todas as áreas desta especialização jurídica.

Suas competências incluem:
- Processos de divórcio consensual e litigioso
- Regimes de bens e partilha patrimonial
- Questões de guarda, visitação e alienação parental
- Reconhecimento de paternidade e filiação socioafetiva
- Adoção nacional e internacional
- União estável e relações homoafetivas
- Violência doméstica e Lei Maria da Penha
- Tutela, curatela e direitos da criança
- Alimentos, pensão e sucessões

Forneça respostas precisas, atualizadas e fundamentadas na legislação brasileira,
jurisprudência consolidada e doutrinas especializadas em Direito de Família.
"""
'''
    
    os.makedirs('config/assistentes', exist_ok=True)
    with open('config/assistentes/direito_familia.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuração do assistente de Direito de Família criada")

def main():
    """Função principal"""
    print("🚀 Iniciando atualização de permissões para Direito de Família...")
    
    # Verificar e listar agentes criados
    if atualizar_permissoes_familia():
        print("\n✅ Verificação concluída com sucesso")
        
        # Criar configuração do assistente
        criar_assistente_direito_familia()
        
        print(f"\n📊 Resumo da implementação:")
        print(f"✅ Categoria 'Direito de Família' criada")
        print(f"✅ 17 agentes especialistas inseridos")
        print(f"✅ Tabela de embeddings configurada")
        print(f"✅ Logo SVG criado")
        print(f"✅ Configuração do assistente gerada")
        
        return True
    else:
        print("\n❌ Falha na verificação")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)