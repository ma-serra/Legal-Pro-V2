"""
Seed Database: Assistentes Especializados do agentes_preconfigurados.json
Data: 2025-12-15
Carrega os 40+ assistentes especializados do sistema original
"""
import json
import os
import sys
from main import app, db
from models import AgenteJuridico, CategoriaJuridica

def seed_assistentes_especializados():
    """Carrega assistentes do JSON original para o banco"""
    
    with app.app_context():
        print("🌱 Iniciando seed de assistentes especializados...")
        
        # Carregar JSON original
        json_path = r'D:\Legal Pro Hub\estrutura_vercel_railway\templates_multiagentes\agentes_preconfigurados.json'
        
        if not os.path.exists(json_path):
            print(f"❌ Arquivo não encontrado: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            assistentes_data = json.load(f)
        
        print(f"📂 Carregados {len(assistentes_data)} assistentes do JSON")
        
        # Garantir que categoria "Geral" existe
        cat_geral = CategoriaJuridica.query.filter_by(nome='Geral').first()
        if not cat_geral:
            print("📝 Criando categoria 'Geral'...")
            cat_geral = CategoriaJuridica(
                nome='Geral',
                descricao='Categoria geral para assistentes especializados',
                icone='fas fa-robot',
                cor='#3B82F6',
                ativa=True
            )
            db.session.add(cat_geral)
            db.session.commit()
            print("✅ Categoria 'Geral' criada")
        
        # Mapeamento de tipos
        tipo_map = {
            'juridico': 'juridico',
            'resumidor': 'resumidor',
            'sentimento': 'sentimento',
            'extrator': 'extrator',
            'tradutor': 'tradutor',
            'classificador': 'classificador',
            'gerador': 'gerador',
            'sintetizador': 'sintetizador',
            'formatador': 'formatador',
            'analisador': 'juridico'  # Fallback
        }
        
        count_criados = 0
        count_existentes = 0
        count_erros = 0
        
        for assistente_json in assistentes_data:
            try:
                # Verificar se já existe
                existe = AgenteJuridico.query.filter_by(nome=assistente_json['nome']).first()
                if existe:
                    print(f"⏩ '{assistente_json['nome']}' já existe - pulando")
                    count_existentes += 1
                    continue
                
                # Mapear tipo
                tipo_original = assistente_json.get('tipo', 'juridico').lower()
                tipo = tipo_map.get(tipo_original, 'juridico')
                
                # Extrair configurações
                config_original = assistente_json.get('configuracoes', {})
                
                # Criar configurações LLM estruturadas
                configuracoes_llm = {
                    'llm_provider': config_original.get('llm_provider', 'openai'),
                    'llm_model': config_original.get('llm_model', 'gpt-4o'),
                    'temperatura': config_original.get('temperatura', 0.3),
                    'parametros': config_original.get('parametros', {}),
                    'modo_debug': config_original.get('modo_debug', False),
                    'sempre_executar': config_original.get('sempre_executar', True),
                    'timeout': config_original.get('timeout', 120),
                    'max_tokens': config_original.get('max_tokens', 8000)
                }
                
                # Criar assistente
                assistente = AgenteJuridico(
                    nome=assistente_json['nome'],
                    classe=f"Assistente{tipo.capitalize()}",  # Nome da classe genérico
                    tipo=tipo,
                    descricao=assistente_json.get('descricao', ''),
                    prompt_template=assistente_json.get('prompt_template', ''),
                    categoria_id=cat_geral.id,
                    configuracoes_llm=configuracoes_llm,
                    customizado=False,  # Pré-configurado
                    ativo=True,
                    icone='fas fa-robot',
                    cor_destaque='#3B82F6',
                    # Manter compatibilidade com campos antigos
                    modelo_ai=config_original.get('llm_model', 'gpt-4o'),
                    temperatura=config_original.get('temperatura', 0.3),
                    max_tokens=config_original.get('max_tokens', 8000)
                )
                
                db.session.add(assistente)
                count_criados += 1
                print(f"✅ Criado: {assistente.nome} ({tipo})")
                
            except Exception as e:
                count_erros += 1
                print(f"❌ Erro ao criar '{assistente_json.get('nome', 'desconhecido')}': {e}")
                continue
        
        # Commit final
        try:
            db.session.commit()
            print(f"\n🎉 Seed concluído!")
            print(f"  ✅ {count_criados} assistentes criados")
            print(f"  ⏩ {count_existentes} já existiam")
            print(f"  ❌ {count_erros} erros")
            print(f"\n📊 Total no banco: {AgenteJuridico.query.count()} assistentes")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro no commit final: {e}")
            raise

if __name__ == '__main__':
    seed_assistentes_especializados()
