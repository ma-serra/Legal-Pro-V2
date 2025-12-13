"""
Script para corrigir cores e ícones das áreas jurídicas conforme especificações exatas
Aplica cores diretamente no banco de dados e atualiza template
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL não encontrada")
        
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session(), engine
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None, None

def obter_configuracoes_areas_corretas():
    """Retorna configurações corretas para todas as 18 áreas jurídicas"""
    return {
        'criminal': {
            'color': '#ef4444',
            'icon': 'fas fa-gavel',
            'name': 'Direito Criminal'
        },
        'penal': {
            'color': '#ef4444', 
            'icon': 'fas fa-gavel',
            'name': 'Direito Penal'
        },
        'agrario': {
            'color': '#896302',
            'icon': 'fas fa-tractor',
            'name': 'Direito Agrário'
        },
        'trabalhista': {
            'color': '#f97316',
            'icon': 'fas fa-hard-hat',
            'name': 'Direito Trabalhista'
        },
        'consumidor': {
            'color': '#10b981',
            'icon': 'fas fa-user-shield',
            'name': 'Direito do Consumidor'
        },
        'familia': {
            'color': '#d4a148',
            'icon': 'fas fa-users',
            'name': 'Direito de Família'
        },
        'civil': {
            'color': '#007dfa',
            'icon': 'fas fa-balance-scale',
            'name': 'Direito Civil'
        },
        'empresarial': {
            'color': '#3b82f6',
            'icon': 'fas fa-building',
            'name': 'Direito Empresarial'
        },
        'administrativo': {
            'color': '#6b7280',
            'icon': 'fas fa-university',
            'name': 'Direito Administrativo'
        },
        'constitucional': {
            'color': '#1c7dde',
            'icon': 'fas fa-landmark',
            'name': 'Direito Constitucional'
        },
        'digital': {
            'color': '#475569',
            'icon': 'fas fa-laptop-code',
            'name': 'Direito Digital'
        },
        'ambiental': {
            'color': '#1f744d',
            'icon': 'fas fa-leaf',
            'name': 'Direito Ambiental'
        },
        'bancario': {
            'color': '#c29e74',
            'icon': 'fas fa-piggy-bank',
            'name': 'Direito Bancário'
        },
        'previdenciario': {
            'color': '#ec4899',
            'icon': 'fas fa-coins',
            'name': 'Direito Previdenciário'
        },
        'seguros': {
            'color': '#06b6d4',
            'icon': 'fas fa-shield-alt',
            'name': 'Direito Securitário'
        },
        'imobiliario': {
            'color': '#059669',
            'icon': 'fas fa-home',
            'name': 'Direito Imobiliário'
        },
        'conflitos': {
            'color': '#64748b',
            'icon': 'fas fa-handshake',
            'name': 'Negociação e Conflitos'
        },
        'riscos': {
            'color': '#df3542',  # COR CORRETA CONFORME ESPECIFICAÇÃO
            'icon': 'fas fa-chart-line',  # ÍCONE CORRETO (analytics/gráfico)
            'name': 'Análise de Riscos Jurídicos'
        },
        'tributario': {
            'color': '#8b5cf6',
            'icon': 'fas fa-calculator',
            'name': 'Direito Tributário'
        }
    }

def atualizar_cores_banco_dados():
    """Atualiza cores no banco de dados se necessário"""
    session, engine = conectar_database()
    if not session:
        return False
    
    try:
        # Verificar se existe tabela de configurações de cores
        result = session.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'configuracao_areas_juridicas'
        """)).fetchone()
        
        if result[0] == 0:
            # Criar tabela de configurações se não existir
            session.execute(text("""
                CREATE TABLE configuracao_areas_juridicas (
                    id SERIAL PRIMARY KEY,
                    area_key VARCHAR(50) UNIQUE NOT NULL,
                    color VARCHAR(20) NOT NULL,
                    icon VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ Tabela de configurações criada")
        
        # Inserir/atualizar configurações
        configuracoes = obter_configuracoes_areas_corretas()
        for area_key, config in configuracoes.items():
            session.execute(text("""
                INSERT INTO configuracao_areas_juridicas (area_key, color, icon, name)
                VALUES (:area_key, :color, :icon, :name)
                ON CONFLICT (area_key) 
                DO UPDATE SET 
                    color = EXCLUDED.color,
                    icon = EXCLUDED.icon,
                    name = EXCLUDED.name
            """), {
                'area_key': area_key,
                'color': config['color'],
                'icon': config['icon'],
                'name': config['name']
            })
        
        session.commit()
        logger.info("✅ Configurações de cores atualizadas no banco")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar banco: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def gerar_javascript_cores_corretas():
    """Gera JavaScript com configurações corretas"""
    configuracoes = obter_configuracoes_areas_corretas()
    
    js_config = "const legalAreasConfig = {\n"
    for area_key, config in configuracoes.items():
        js_config += f"""  '{area_key}': {{
    color: '{config['color']}',
    icon: '{config['icon']}',
    name: '{config['name']}',
    btnColor: '{config['color']}'
  }},\n"""
    
    js_config += "};\n"
    return js_config

def aplicar_correcoes_template():
    """Aplica correções no template HTML"""
    try:
        # Ler template atual
        with open('templates/validacao_multi_agente_expandida.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Gerar novo JavaScript
        novo_js = gerar_javascript_cores_corretas()
        
        # Encontrar e substituir configuração
        import re
        pattern = r'const legalAreasConfig = \{[\s\S]*?\};'
        
        if re.search(pattern, content):
            content = re.sub(pattern, novo_js.strip(), content)
            logger.info("✅ Configuração JavaScript substituída")
        else:
            logger.warning("⚠️ Padrão de configuração não encontrado")
            return False
        
        # Salvar arquivo
        with open('templates/validacao_multi_agente_expandida.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Template atualizado com cores corretas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar template: {e}")
        return False

def validar_configuracoes():
    """Valida se as configurações foram aplicadas corretamente"""
    try:
        with open('templates/validacao_multi_agente_expandida.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se a cor #df3542 está presente (Análise de Riscos)
        if '#df3542' in content:
            logger.info("✅ Cor #df3542 encontrada no template")
        else:
            logger.error("❌ Cor #df3542 NÃO encontrada no template")
            return False
        
        # Verificar se o ícone chart-line está presente
        if 'fas fa-chart-line' in content:
            logger.info("✅ Ícone fas fa-chart-line encontrado no template")
        else:
            logger.error("❌ Ícone fas fa-chart-line NÃO encontrado no template")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando correção de cores e ícones das áreas jurídicas")
    
    # Aplicar correções no template
    if aplicar_correcoes_template():
        logger.info("✅ Template corrigido com sucesso")
    else:
        logger.error("❌ Falha ao corrigir template")
        return
    
    # Atualizar banco de dados
    if atualizar_cores_banco_dados():
        logger.info("✅ Banco de dados atualizado com sucesso")
    else:
        logger.warning("⚠️ Não foi possível atualizar banco de dados")
    
    # Validar configurações
    if validar_configuracoes():
        logger.info("✅ Validação concluída com sucesso")
        logger.info("🎯 Análise de Riscos Jurídicos agora usa cor #df3542 e ícone chart-line")
    else:
        logger.error("❌ Falha na validação")
    
    logger.info("🏁 Correção concluída")

if __name__ == "__main__":
    main()