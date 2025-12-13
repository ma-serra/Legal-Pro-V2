"""
Sistema otimizado para criar templates específicos para especialidades dos agentes
Versão otimizada para processamento rápido de todos os 292 agentes
"""

import psycopg2
import os
import json
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

def conectar_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def gerar_template_compacto(nome_agente, capacidade, area_id):
    """Gera template compacto baseado na capacidade"""
    tipo = "Contrato" if any(x in capacidade.lower() for x in ['contrato', 'acordo']) else "Documento"
    
    template = {
        'nome': f"{tipo} - {capacidade[:45]}...",
        'descricao': f"Template para {capacidade.lower()} desenvolvido pelo {nome_agente}",
        'area_id': area_id,
        'conteudo': f'<div class="template"><h2>{tipo}</h2><p>{capacidade}</p><div class="campos"><label>Partes:</label><input type="text"><label>Objeto:</label><textarea>{capacidade}</textarea></div></div>',
        'palavras_chave': capacidade.replace(' ', ', ')[:100],
        'complexidade': 'media',
        'tempo': 60,
        'criado_por': nome_agente
    }
    
    return template

def mapear_area_por_nome(nome_agente):
    """Mapeia agente para área jurídica baseado no nome"""
    nome_lower = nome_agente.lower()
    
    mapeamentos = {
        'civil': 1, 'trabalhist': 2, 'empresarial': 3, 'penal': 4, 'criminal': 4,
        'agrari': 5, 'securit': 6, 'seguro': 6, 'tributari': 7, 'fiscal': 7,
        'digital': 8, 'lgpd': 8, 'administrativ': 9, 'constitucional': 10,
        'ambiental': 11, 'familia': 12, 'consumidor': 13, 'previdenciari': 14,
        'imobiliari': 15, 'bancari': 16, 'internacional': 17
    }
    
    for palavra_chave, area_id in mapeamentos.items():
        if palavra_chave in nome_lower:
            return area_id
    
    return 1  # Default Civil

def processar_todos_agentes():
    """Processa todos os agentes de uma vez"""
    conn = conectar_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Buscar agentes com capacidades
    cursor.execute("""
        SELECT nome, capacidades 
        FROM agente_juridico 
        WHERE ativo = true AND capacidades IS NOT NULL
        ORDER BY nome
    """)
    
    agentes = cursor.fetchall()
    templates_criados = 0
    batch_size = 50
    
    print(f"Processando {len(agentes)} agentes...")
    
    for i in range(0, len(agentes), batch_size):
        batch = agentes[i:i+batch_size]
        
        for nome_agente, capacidades_json in batch:
            try:
                capacidades = json.loads(capacidades_json) if isinstance(capacidades_json, str) else capacidades_json
                area_id = mapear_area_por_nome(nome_agente)
                
                # Criar 1 template principal por agente (otimizado)
                if capacidades:
                    capacidade_principal = capacidades[0]
                    template = gerar_template_compacto(nome_agente, capacidade_principal, area_id)
                    
                    # Verificar se já existe
                    cursor.execute("""
                        SELECT id FROM legal_templates_juridicos 
                        WHERE nome = %s AND area_juridica_id = %s
                    """, (template['nome'], template['area_id']))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO legal_templates_juridicos 
                            (nome, descricao, area_juridica_id, conteudo_html, palavras_chave, 
                             complexidade, tempo_estimado, ativo, criado_em, criado_por)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            template['nome'], template['descricao'], template['area_id'],
                            template['conteudo'], template['palavras_chave'],
                            template['complexidade'], template['tempo'], True,
                            datetime.now(), template['criado_por']
                        ))
                        templates_criados += 1
                        
            except Exception as e:
                print(f"Erro processando {nome_agente}: {e}")
                continue
        
        # Commit por batch
        conn.commit()
        print(f"Processados {min(i+batch_size, len(agentes))} agentes - {templates_criados} templates criados")
    
    # Relatório final
    cursor.execute("SELECT COUNT(*) FROM legal_templates_juridicos WHERE ativo = true")
    total_templates = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM agente_juridico WHERE ativo = true")
    total_agentes = cursor.fetchone()[0]
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Templates criados nesta execução: {templates_criados}")
    print(f"Total de templates no sistema: {total_templates}")
    print(f"Total de agentes especializados: {total_agentes}")
    print(f"Cobertura: {templates_criados}/{len(agentes)} agentes com templates específicos")
    
    # Templates por área
    cursor.execute("""
        SELECT laj.nome, COUNT(ltj.id) as total
        FROM legal_areas_juridicas laj
        LEFT JOIN legal_templates_juridicos ltj ON laj.id = ltj.area_juridica_id AND ltj.ativo = true
        WHERE laj.ativo = true
        GROUP BY laj.nome
        ORDER BY total DESC
    """)
    
    print(f"\nTemplates por área:")
    for area, count in cursor.fetchall():
        print(f"  {area}: {count}")
    
    conn.close()
    print(f"\nSistema Legal Design Pro V2 - Templates especializados implementados!")

if __name__ == "__main__":
    processar_todos_agentes()