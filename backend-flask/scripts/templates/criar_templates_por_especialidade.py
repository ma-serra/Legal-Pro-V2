"""
Sistema para criar templates específicos para cada especialidade dos 292 agentes
Mapeia capacidades de cada agente para templates únicos e especializados
"""

import psycopg2
import os
import json
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def obter_todos_agentes(conn):
    """Obtém todos os agentes ativos com suas capacidades"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, capacidades, classe 
        FROM agente_juridico 
        WHERE ativo = true AND capacidades IS NOT NULL
        ORDER BY nome
    """)
    return cursor.fetchall()

def mapear_area_juridica(classe_agente):
    """Mapeia classe do agente para área jurídica"""
    mapeamento = {
        'direito_digital': 8,
        'direito_criminal': 4,
        'direito_civil': 1,
        'direito_trabalhista': 2,
        'direito_empresarial': 3,
        'direito_penal': 4,
        'direito_agrario': 5,
        'direito_securitario': 6,
        'direito_tributario': 7,
        'direito_administrativo': 9,
        'direito_constitucional': 10,
        'direito_ambiental': 11,
        'direito_familia': 12,
        'direito_consumidor': 13,
        'direito_previdenciario': 14,
        'direito_imobiliario': 15,
        'direito_bancario': 16,
        'direito_internacional': 17
    }
    
    # Inferir área baseada no nome/classe se não encontrar mapeamento direto
    if classe_agente:
        classe_lower = classe_agente.lower()
        for chave, valor in mapeamento.items():
            if chave in classe_lower:
                return valor
    
    return 1  # Default para Direito Civil

def gerar_templates_por_capacidade(nome_agente, capacidades_json):
    """Gera templates específicos baseados nas capacidades do agente"""
    try:
        capacidades = json.loads(capacidades_json) if isinstance(capacidades_json, str) else capacidades_json
    except:
        return []
    
    templates = []
    
    for i, capacidade in enumerate(capacidades[:3]):  # Máximo 3 templates por agente
        # Determinar tipo de template baseado na capacidade
        tipo_template = determinar_tipo_template(capacidade)
        
        template = {
            'nome': f"{tipo_template} - {capacidade[:50]}",
            'descricao': f"Template especializado para {capacidade.lower()}. Desenvolvido especificamente para o {nome_agente}.",
            'conteudo_html': gerar_conteudo_html(nome_agente, capacidade, tipo_template),
            'palavras_chave': extrair_palavras_chave(capacidade),
            'complexidade': determinar_complexidade(capacidade),
            'tempo_estimado': calcular_tempo_estimado(capacidade)
        }
        
        templates.append(template)
    
    return templates

def determinar_tipo_template(capacidade):
    """Determina o tipo de template baseado na capacidade"""
    capacidade_lower = capacidade.lower()
    
    if any(word in capacidade_lower for word in ['contrato', 'acordo', 'convenção']):
        return 'Contrato'
    elif any(word in capacidade_lower for word in ['ação', 'petição', 'recurso', 'defesa']):
        return 'Petição'
    elif any(word in capacidade_lower for word in ['procedimento', 'processo', 'rito']):
        return 'Procedimento'
    elif any(word in capacidade_lower for word in ['análise', 'avaliação', 'verificação']):
        return 'Análise'
    elif any(word in capacidade_lower for word in ['declaração', 'termo', 'atestado']):
        return 'Declaração'
    elif any(word in capacidade_lower for word in ['parecer', 'relatório', 'laudo']):
        return 'Parecer'
    else:
        return 'Documento'

def gerar_conteudo_html(nome_agente, capacidade, tipo_template):
    """Gera conteúdo HTML estruturado para o template"""
    return f"""
<div class="template-especializado">
    <header class="template-header">
        <h1>{tipo_template} Especializado</h1>
        <h2>{capacidade}</h2>
        <p class="agente-responsavel">Desenvolvido por: {nome_agente}</p>
    </header>
    
    <section class="template-body">
        <div class="secao-principal">
            <h3>Dados Principais</h3>
            <div class="campo-form">
                <label>Partes Envolvidas:</label>
                <input type="text" name="partes" placeholder="Identificação das partes">
            </div>
            <div class="campo-form">
                <label>Objeto:</label>
                <textarea name="objeto" placeholder="Descrição detalhada do objeto">{capacidade}</textarea>
            </div>
        </div>
        
        <div class="secao-especifica">
            <h3>Cláusulas Específicas</h3>
            <div class="clausulas-container">
                <!-- Cláusulas específicas da capacidade {capacidade} -->
                <div class="clausula">
                    <strong>Fundamentação Legal:</strong>
                    <p>Conforme legislação aplicável a {capacidade.lower()}</p>
                </div>
            </div>
        </div>
        
        <div class="secao-assinatura">
            <h3>Assinaturas e Testemunhas</h3>
            <div class="assinaturas">
                <div class="assinatura-bloco">
                    <p>_______________________________</p>
                    <p>Parte 1</p>
                </div>
                <div class="assinatura-bloco">
                    <p>_______________________________</p>
                    <p>Parte 2</p>
                </div>
            </div>
        </div>
    </section>
    
    <footer class="template-footer">
        <p>Template gerado pelo sistema Legal Design Pro V2</p>
        <p>Especialista: {nome_agente}</p>
    </footer>
</div>
"""

def extrair_palavras_chave(capacidade):
    """Extrai palavras-chave da capacidade"""
    # Remove artigos e preposições comuns
    stop_words = {'de', 'da', 'do', 'das', 'dos', 'e', 'em', 'com', 'para', 'por', 'a', 'o', 'as', 'os'}
    palavras = capacidade.lower().split()
    palavras_chave = [p for p in palavras if p not in stop_words and len(p) > 2]
    return ', '.join(palavras_chave[:5])  # Máximo 5 palavras-chave

def determinar_complexidade(capacidade):
    """Determina complexidade baseada na capacidade"""
    capacidade_lower = capacidade.lower()
    
    if any(word in capacidade_lower for word in ['análise', 'planejamento', 'estratégia', 'auditoria']):
        return 'alta'
    elif any(word in capacidade_lower for word in ['contrato', 'acordo', 'procedimento']):
        return 'media'
    else:
        return 'baixa'

def calcular_tempo_estimado(capacidade):
    """Calcula tempo estimado em minutos"""
    complexidade = determinar_complexidade(capacidade)
    tempos = {'baixa': 30, 'media': 60, 'alta': 120}
    return tempos.get(complexidade, 60)

def inserir_templates_especializados(conn):
    """Insere templates especializados para todos os agentes"""
    cursor = conn.cursor()
    agentes = obter_todos_agentes(conn)
    
    total_templates = 0
    templates_por_agente = {}
    
    print(f"🎯 Processando {len(agentes)} agentes especializados...")
    
    for nome_agente, capacidades_json, classe in agentes:
        if not capacidades_json:
            continue
            
        # Mapear área jurídica
        area_id = mapear_area_juridica(classe)
        
        # Gerar templates para este agente
        templates = gerar_templates_por_capacidade(nome_agente, capacidades_json)
        templates_por_agente[nome_agente] = len(templates)
        
        print(f"\n👤 {nome_agente} ({len(templates)} templates)")
        
        for template in templates:
            # Verificar se template já existe
            cursor.execute("""
                SELECT id FROM legal_templates_juridicos 
                WHERE nome = %s AND area_juridica_id = %s
            """, (template['nome'], area_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO legal_templates_juridicos 
                    (nome, descricao, area_juridica_id, conteudo_html, palavras_chave, 
                     complexidade, tempo_estimado, ativo, criado_em, criado_por)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    template['nome'],
                    template['descricao'],
                    area_id,
                    template['conteudo_html'],
                    template['palavras_chave'],
                    template['complexidade'],
                    template['tempo_estimado'],
                    True,
                    datetime.now(),
                    nome_agente
                ))
                
                total_templates += 1
                print(f"  ✅ {template['nome'][:60]}...")
            else:
                print(f"  📋 {template['nome'][:60]}... (já existe)")
    
    conn.commit()
    return total_templates, templates_por_agente

def gerar_relatorio_especialidades(conn, total_templates, templates_por_agente):
    """Gera relatório final das especialidades"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE TEMPLATES POR ESPECIALIDADE")
    print("="*80)
    
    # Templates totais
    cursor.execute("SELECT COUNT(*) FROM legal_templates_juridicos WHERE ativo = true")
    total_templates_sistema = cursor.fetchone()[0]
    
    print(f"📈 Templates Novos Criados: {total_templates}")
    print(f"📊 Total de Templates no Sistema: {total_templates_sistema}")
    print(f"🤖 Agentes com Templates Especializados: {len(templates_por_agente)}")
    
    # Top 10 agentes com mais templates
    print(f"\n🏆 Top 10 Agentes com Mais Templates Especializados:")
    sorted_agentes = sorted(templates_por_agente.items(), key=lambda x: x[1], reverse=True)
    
    for i, (agente, count) in enumerate(sorted_agentes[:10], 1):
        print(f"  {i:2d}. {agente}: {count} templates")
    
    # Templates por área
    cursor.execute("""
        SELECT laj.nome, COUNT(ltj.id) as total
        FROM legal_areas_juridicas laj
        LEFT JOIN legal_templates_juridicos ltj ON laj.id = ltj.area_juridica_id AND ltj.ativo = true
        WHERE laj.ativo = true
        GROUP BY laj.id, laj.nome
        ORDER BY total DESC
    """)
    
    areas_templates = cursor.fetchall()
    print(f"\n📂 Templates por Área Jurídica:")
    for area, count in areas_templates:
        print(f"  • {area}: {count} templates")
    
    # Estatísticas de complexidade
    cursor.execute("""
        SELECT complexidade, COUNT(*) as total
        FROM legal_templates_juridicos 
        WHERE ativo = true AND complexidade IS NOT NULL
        GROUP BY complexidade
        ORDER BY total DESC
    """)
    
    complexidades = cursor.fetchall()
    print(f"\n⚖️ Distribuição por Complexidade:")
    for complexidade, count in complexidades:
        print(f"  • {complexidade.title()}: {count} templates")
    
    print(f"\n🎉 Sistema Legal Design Pro V2 - Templates Especializados Implementados!")
    print(f"✅ Cada agente agora possui templates alinhados com suas capacidades específicas")

def main():
    """Função principal"""
    print("🚀 Iniciando criação de templates por especialidade dos agentes...")
    
    conn = conectar_database()
    if not conn:
        return
    
    try:
        # Inserir templates especializados
        print("\n1️⃣ Criando templates específicos para cada agente...")
        total_templates, templates_por_agente = inserir_templates_especializados(conn)
        
        # Gerar relatório
        print("\n2️⃣ Gerando relatório de especialidades...")
        gerar_relatorio_especialidades(conn, total_templates, templates_por_agente)
        
    except Exception as e:
        print(f"❌ Erro durante criação de templates: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()