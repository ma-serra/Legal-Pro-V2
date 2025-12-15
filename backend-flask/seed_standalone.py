"""
Seed Standalone: Assistentes Especializados (sem dependencias do Flask)
"""
import json
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

def seed_assistentes():
    """Carrega assistentes do JSON para o banco"""
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERRO: DATABASE_URL nao encontrada")
        return
    
    print("Iniciando seed de assistentes...")
    
    # Carregar JSON
    json_path = r'D:\Legal Pro Hub\estrutura_vercel_railway\templates_multiagentes\agentes_preconfigurados.json'
    
    if not os.path.exists(json_path):
        print(f"ERRO: Arquivo nao encontrado: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assistentes_data = data.get('templates', [])
    print(f"Carregados {len(assistentes_data)} assistentes do JSON")
    
    # Conectar
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Garantir categoria Geral
    cur.execute("SELECT id FROM categoria_juridica WHERE nome = 'Geral';")
    cat_geral = cur.fetchone()
    
    if not cat_geral:
        print("Criando categoria 'Geral'...")
        cur.execute("""
            INSERT INTO categoria_juridica (nome, descricao, icone, cor, ativa, created_at, updated_at)
            VALUES ('Geral', 'Categoria geral para assistentes', 'fas fa-robot', '#3B82F6', TRUE, NOW(), NOW())
            RETURNING id;
        """)
        cat_id = cur.fetchone()[0]
        print(f"Categoria criada com ID {cat_id}")
    else:
        cat_id = cat_geral[0]
        print(f"Categoria 'Geral' ja existe com ID {cat_id}")
    
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
        'analisador': 'juridico'
    }
    
    count_criados = 0
    count_existentes = 0
    count_erros = 0
    
    for assistente_json in assistentes_data:
        try:
            nome = assistente_json['nome']
            
            # Verificar se ja existe
            cur.execute("SELECT id FROM agente_juridico WHERE nome = %s;", (nome,))
            if cur.fetchone():
                print(f"Pulando '{nome}' - ja existe")
                count_existentes += 1
                continue
            
            # Mapear tipo
            tipo_original = assistente_json.get('tipo', 'juridico').lower()
            tipo = tipo_map.get(tipo_original, 'juridico')
            
            # Configuracoes
            config = assistente_json.get('configuracoes', {})
            configuracoes_llm = json.dumps({
                'llm_provider': config.get('llm_provider', 'openai'),
                'llm_model': config.get('llm_model', 'gpt-4o'),
                'temperatura': config.get('temperatura', 0.3),
                'parametros': config.get('parametros', {}),
                'modo_debug': config.get('modo_debug', False),
                'sempre_executar': config.get('sempre_executar', True),
                'timeout': config.get('timeout', 120),
                'max_tokens': config.get('max_tokens', 8000)
            })
            
            # Inserir
            cur.execute("""
                INSERT INTO agente_juridico (
                    nome, classe, tipo, descricao, prompt_template,
                    categoria_id, configuracoes_llm, customizado, ativo,
                    icone, cor_destaque, modelo_ai, temperatura, max_tokens,
                    data_criacao, data_atualizacao
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s::jsonb, %s, %s,
                    %s, %s, %s, %s, %s,
                    NOW(), NOW()
                );
            """, (
                nome,
                f"Assistente{tipo.capitalize()}",
                tipo,
                assistente_json.get('descricao', ''),
                assistente_json.get('prompt_template', ''),
                cat_id,
                configuracoes_llm,
                False,  # customizado
                True,  # ativo
                'fas fa-robot',
                '#3B82F6',
                config.get('llm_model', 'gpt-4o'),
                config.get('temperatura', 0.3),
                config.get('max_tokens', 8000)
            ))
            
            count_criados += 1
            print(f"Criado: {nome} ({tipo})")
            
        except Exception as e:
            count_erros += 1
            print(f"ERRO ao criar '{assistente_json.get('nome', '?')}': {e}")
            continue
    
    # Resultado
    print(f"\n=== Seed concluido! ===")
    print(f"  Criados: {count_criados}")
    print(f"  Ja existiam: {count_existentes}")
    print(f"  Erros: {count_erros}")
    
    # Total final
    cur.execute("SELECT COUNT(*) FROM agente_juridico;")
    total = cur.fetchone()[0]
    print(f"\nTotal de assistentes no banco: {total}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    seed_assistentes()
