"""
Mapeamento completo entre agentes jurídicos e suas bases vetoriais correspondentes
"""

import psycopg2
import os
from datetime import datetime

def get_database_connection():
    """Conecta ao banco PostgreSQL"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT', 5432)
    )

def mapear_agentes_para_bases():
    """Mapeia agentes para suas respectivas bases vetoriais"""
    
    # Mapeamento baseado nas categorias e especialidades
    mapeamento_categoria_base = {
        1: "embeddings_direito_bancario",      # Direito Bancário
        2: "embeddings_direito_securitario",   # Direito Securitário  
        3: "embeddings_direito_trabalhista",   # Direito Trabalhista
        4: "embeddings_direito_previdenciario", # Direito Previdenciário
        5: "embeddings_direito_tributario",    # Direito Tributário
        6: "embeddings_direito_imobiliario",   # Direito Imobiliário
        7: "embeddings_direito_digital",       # Direito Digital
        8: "embeddings_direito_empresarial",   # Direito Empresarial
        9: "embeddings_analise_riscos",        # Análise de Riscos
        10: "embeddings_direito_penal",        # Direito Penal
        11: "embeddings_direito_ambiental",    # Direito Ambiental
        12: "embeddings_direito_consumidor",   # Direito do Consumidor
        13: "embeddings_direito_civil",        # Direito Civil
        14: "embeddings_negociacao_conflitos", # Negociação e Conflitos
        15: "embeddings_direito_familia",      # Direito de Família
        16: "embeddings_direito_administrativo", # Direito Administrativo
        17: "embeddings_direito_constitucional", # Direito Constitucional
        18: "embeddings_direito_agrario"       # Direito Agrário
    }
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Obter dados dos agentes e categorias
    cursor.execute("""
        SELECT 
            a.id,
            a.nome,
            a.classe,
            a.descricao,
            a.categoria_id,
            c.nome as categoria_nome,
            a.ativo
        FROM agente_juridico a
        JOIN categoria_juridica c ON a.categoria_id = c.id
        WHERE a.ativo = true
        ORDER BY c.nome, a.nome
    """)
    
    agentes = cursor.fetchall()
    
    # Verificar status das bases vetoriais
    bases_info = {}
    for categoria_id, base_name in mapeamento_categoria_base.items():
        try:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as processed_records
                FROM {base_name}
            """)
            result = cursor.fetchone()
            total, processed = result if result else (0, 0)
            
            # Buscar arquivos únicos
            cursor.execute(f"""
                SELECT COUNT(DISTINCT referencia) 
                FROM {base_name} 
                WHERE referencia IS NOT NULL
            """)
            arquivos = cursor.fetchone()[0] or 0
            
            bases_info[base_name] = {
                'total_records': total,
                'processed_records': processed,
                'arquivos': arquivos,
                'percentual': (processed / total * 100) if total > 0 else 0,
                'status': 'COMPLETA' if total > 0 and processed == total else 'EM PROGRESSO' if processed > 0 else 'VAZIA'
            }
            
        except Exception as e:
            bases_info[base_name] = {
                'total_records': 0,
                'processed_records': 0,
                'arquivos': 0,
                'percentual': 0,
                'status': 'ERRO',
                'erro': str(e)
            }
    
    cursor.close()
    conn.close()
    
    return agentes, bases_info, mapeamento_categoria_base

def gerar_relatorio_conexoes():
    """Gera relatório completo das conexões agentes-bases"""
    
    agentes, bases_info, mapeamento = mapear_agentes_para_bases()
    
    print("MAPEAMENTO COMPLETO: AGENTES JURÍDICOS ↔ BASES VETORIAIS")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Total de Agentes Ativos: {len(agentes)}")
    print(f"Total de Bases Vetoriais: {len(bases_info)}")
    print("=" * 80)
    
    # Agrupar agentes por categoria
    agentes_por_categoria = {}
    for agente in agentes:
        categoria_id = agente[4]
        categoria_nome = agente[5]
        
        if categoria_id not in agentes_por_categoria:
            agentes_por_categoria[categoria_id] = {
                'nome': categoria_nome,
                'agentes': [],
                'base_vetorial': mapeamento.get(categoria_id, 'N/A')
            }
        
        agentes_por_categoria[categoria_id]['agentes'].append({
            'id': agente[0],
            'nome': agente[1],
            'classe': agente[2],
            'descricao': agente[3]
        })
    
    # Relatório por categoria
    for categoria_id, dados in agentes_por_categoria.items():
        base_name = dados['base_vetorial']
        base_info = bases_info.get(base_name, {})
        
        print(f"\n📂 CATEGORIA: {dados['nome']} (ID: {categoria_id})")
        print(f"   🔗 Base Vetorial: {base_name}")
        print(f"   📊 Status da Base: {base_info.get('status', 'DESCONHECIDO')}")
        print(f"   📁 Arquivos: {base_info.get('arquivos', 0)}")
        print(f"   📄 Registros: {base_info.get('total_records', 0)} (Processados: {base_info.get('processed_records', 0)})")
        print(f"   📈 Percentual: {base_info.get('percentual', 0):.1f}%")
        print(f"   👥 Agentes ({len(dados['agentes'])}):")
        
        for agente in dados['agentes'][:5]:  # Mostrar apenas os primeiros 5
            print(f"      • {agente['nome']} ({agente['classe']})")
        
        if len(dados['agentes']) > 5:
            print(f"      ... e mais {len(dados['agentes']) - 5} agentes")
    
    # Resumo das bases com dados
    print(f"\n🔍 RESUMO DAS BASES COM DADOS:")
    print("-" * 50)
    
    bases_com_dados = [(nome, info) for nome, info in bases_info.items() if info['arquivos'] > 0]
    bases_com_dados.sort(key=lambda x: x[1]['arquivos'], reverse=True)
    
    for base_name, info in bases_com_dados:
        categoria_relacionada = None
        for cat_id, base_mapeada in mapeamento.items():
            if base_mapeada == base_name:
                categoria_relacionada = agentes_por_categoria.get(cat_id, {}).get('nome', 'N/A')
                break
        
        print(f"✅ {base_name}")
        print(f"   📂 Categoria: {categoria_relacionada}")
        print(f"   📁 {info['arquivos']} arquivos | {info['total_records']} registros | {info['percentual']:.1f}% processado")
    
    # Estatísticas gerais
    total_bases_com_dados = len(bases_com_dados)
    total_bases_vazias = len(bases_info) - total_bases_com_dados
    total_agentes = len(agentes)
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   👥 Total de Agentes Ativos: {total_agentes}")
    print(f"   🗃️ Total de Bases Vetoriais: {len(bases_info)}")
    print(f"   ✅ Bases com Dados: {total_bases_com_dados}")
    print(f"   📭 Bases Vazias: {total_bases_vazias}")
    print(f"   📈 Cobertura: {(total_bases_com_dados/len(bases_info)*100):.1f}%")

def salvar_mapeamento_json():
    """Salva mapeamento em arquivo JSON"""
    import json
    
    agentes, bases_info, mapeamento = mapear_agentes_para_bases()
    
    # Organizar dados para JSON
    dados_exportacao = {
        'gerado_em': datetime.now().isoformat(),
        'total_agentes': len(agentes),
        'total_bases': len(bases_info),
        'mapeamento_categoria_base': mapeamento,
        'categorias': {},
        'bases_vetoriais': bases_info
    }
    
    # Agrupar por categoria
    for agente in agentes:
        categoria_id = agente[4]
        categoria_nome = agente[5]
        
        if str(categoria_id) not in dados_exportacao['categorias']:
            dados_exportacao['categorias'][str(categoria_id)] = {
                'nome': categoria_nome,
                'base_vetorial': mapeamento.get(categoria_id, 'N/A'),
                'agentes': []
            }
        
        dados_exportacao['categorias'][str(categoria_id)]['agentes'].append({
            'id': agente[0],
            'nome': agente[1],
            'classe': agente[2],
            'descricao': agente[3],
            'ativo': agente[6]
        })
    
    filename = f"mapeamento_agentes_bases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dados_exportacao, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Mapeamento salvo em: {filename}")
    return filename

if __name__ == "__main__":
    gerar_relatorio_conexoes()
    salvar_mapeamento_json()