"""
Script automático para aplicar cores padronizadas por área jurídica
Garante que todos os cards de agentes tenham o atributo data-area correto
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Mapeamento das cores por área jurídica (conforme documento padrão)
CORES_AREAS = {
    'criminal': {'cor': '#dc3545', 'texto': '#ffffff'},
    'empresarial': {'cor': '#007bff', 'texto': '#ffffff'},
    'trabalhista': {'cor': '#fd7e14', 'texto': '#ffffff'},
    'bancario': {'cor': '#c29e74', 'texto': '#ffffff'},
    'recuperacao': {'cor': '#ffc107', 'texto': '#212529'},
    'agrario': {'cor': '#896302', 'texto': '#ffffff'},
    'familia': {'cor': '#d4a148', 'texto': '#ffffff'},
    'administrativo': {'cor': '#093d88', 'texto': '#ffffff'},
    'constitucional': {'cor': '#1c7dde', 'texto': '#ffffff'},
    'digital': {'cor': '#c0c0c0', 'texto': '#212529'},
    'consumidor': {'cor': '#34c79d', 'texto': '#ffffff'},
    'ambiental': {'cor': '#1f744d', 'texto': '#ffffff'},
    'previdenciario': {'cor': '#18689c', 'texto': '#ffffff'},
    'seguros': {'cor': '#6c757d', 'texto': '#ffffff'},
    'conflitos_mediacao': {'cor': '#6f42c1', 'texto': '#ffffff'},
    'analise_riscos': {'cor': '#e83e8c', 'texto': '#ffffff'},
}

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def obter_agentes_por_area():
    """Obtém agentes organizados por área jurídica"""
    conn = conectar_database()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome, area_juridica, classe
            FROM agente_juridico 
            ORDER BY area_juridica, nome
        """)
        
        agentes = cursor.fetchall()
        agentes_por_area = {}
        
        for nome, area, classe in agentes:
            if area:  # Verificar se área não é None
                # Normalizar nome da área para formato snake_case
                area_normalizada = area.lower().replace(' ', '_').replace('-', '_')
                
                if area_normalizada not in agentes_por_area:
                    agentes_por_area[area_normalizada] = []
                
                agentes_por_area[area_normalizada].append({
                    'nome': nome,
                    'area_original': area,
                    'classe': classe
                })
        
        cursor.close()
        conn.close()
        return agentes_por_area
        
    except Exception as e:
        print(f"❌ Erro ao obter agentes: {e}")
        if conn:
            conn.close()
        return {}

def gerar_css_cores_areas():
    """Gera CSS para cores das áreas baseado no padrão oficial"""
    css_content = """
/* Cores específicas por área jurídica - PADRÃO OFICIAL */
/* Gerado automaticamente pelo script aplicar_cores_padronizadas_automatico.py */
/* Data: 16/06/2025 - Baseado no documento PADRAO_CORES_AREAS_JURIDICAS.md */

"""
    
    for area, config in CORES_AREAS.items():
        css_content += f"""
.agent-card[data-area="{area}"] {{
    border-left: 4px solid {config['cor']};
}}

.agent-card[data-area="{area}"] .agent-logo,
.agent-card[data-area="{area}"] .capability-item i {{
    background-color: {config['cor']} !important;
    color: {config['texto']} !important;
}}

.agent-card[data-area="{area}"] .area-tag,
.agent-card[data-area="{area}"] .badge {{
    background: {config['cor']} !important;
    color: {config['texto']} !important;
}}

.agent-card[data-area="{area}"] .btn-details {{
    background: {config['cor']} !important;
    color: {config['texto']} !important;
    border-color: {config['cor']} !important;
}}

.agent-card[data-area="{area}"] .btn-edit,
.agent-card[data-area="{area}"] .btn-use {{
    border-color: {config['cor']} !important;
    color: {config['cor']} !important;
}}

.agent-card[data-area="{area}"] .btn-edit:hover,
.agent-card[data-area="{area}"] .btn-use:hover {{
    background-color: {config['cor']} !important;
    color: {config['texto']} !important;
}}
"""
    
    return css_content

def aplicar_cores_validacao_multi_agente():
    """Aplica cores na página de validação multi-agente"""
    arquivo_template = 'templates/validacao_multi_agente_expandida.html'
    
    try:
        with open(arquivo_template, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Localizar onde inserir o CSS das cores
        css_cores = gerar_css_cores_areas()
        
        # Procurar por um comentário específico ou criar um
        marcador_inicio = "/* Cores específicas por área jurídica - igual à página de especialistas */"
        marcador_fim = "  .agent-header {"
        
        if marcador_inicio in conteudo:
            # Substituir CSS existente
            inicio = conteudo.find(marcador_inicio)
            fim = conteudo.find(marcador_fim, inicio)
            
            if fim != -1:
                novo_conteudo = (
                    conteudo[:inicio] + 
                    css_cores.rstrip() + "\n\n  " +
                    conteudo[fim:]
                )
                
                with open(arquivo_template, 'w', encoding='utf-8') as f:
                    f.write(novo_conteudo)
                
                print("✅ Cores aplicadas na página de validação multi-agente")
                return True
        
        print("⚠️ Marcador CSS não encontrado na página de validação")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao aplicar cores: {e}")
        return False

def criar_funcao_javascript_cores():
    """Cria função JavaScript para aplicar cores dinamicamente"""
    js_content = f"""
// Função para aplicar cores por área jurídica
function aplicarCoresPorArea() {{
    const coresAreas = {str(CORES_AREAS).replace("'", '"')};
    
    document.querySelectorAll('.agent-card').forEach(card => {{
        const areaElement = card.querySelector('.area-tag');
        if (areaElement) {{
            const areaTexto = areaElement.textContent.toLowerCase().trim();
            let areaNormalizada = areaTexto.replace(/\s+/g, '_').replace(/-/g, '_');
            
            // Mapeamento específico para áreas conhecidas
            const mapeamentoAreas = {{
                'direito_criminal': 'criminal',
                'direito_empresarial': 'empresarial',
                'direito_trabalhista': 'trabalhista',
                'direito_bancario': 'bancario',
                'recuperacao_judicial': 'recuperacao',
                'direito_agrario': 'agrario',
                'direito_familia': 'familia',
                'direito_administrativo': 'administrativo',
                'direito_constitucional': 'constitucional',
                'direito_digital': 'digital',
                'direito_consumidor': 'consumidor',
                'direito_ambiental': 'ambiental',
                'direito_previdenciario': 'previdenciario',
                'seguros': 'seguros',
                'conflitos_mediacao': 'conflitos_mediacao',
                'analise_riscos': 'analise_riscos'
            }};
            
            if (mapeamentoAreas[areaNormalizada]) {{
                areaNormalizada = mapeamentoAreas[areaNormalizada];
            }}
            
            // Aplicar data-area
            card.setAttribute('data-area', areaNormalizada);
            
            console.log(`✅ Área ${{areaNormalizada}} aplicada ao agente`);
        }}
    }});
    
    console.log('✅ Cores por área aplicadas dinamicamente');
}}

// Executar quando a página carregar
document.addEventListener('DOMContentLoaded', aplicarCoresPorArea);

// Executar após carregar agentes via AJAX
if (typeof window.aplicarCoresCallback === 'undefined') {{
    window.aplicarCoresCallback = aplicarCoresPorArea;
}}
"""
    
    return js_content

def relatorio_aplicacao():
    """Gera relatório da aplicação das cores"""
    agentes_por_area = obter_agentes_por_area()
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE APLICAÇÃO DE CORES POR ÁREA")
    print("="*60)
    
    total_agentes = 0
    areas_com_cores = 0
    areas_sem_cores = 0
    
    for area, agentes in agentes_por_area.items():
        qtd_agentes = len(agentes)
        total_agentes += qtd_agentes
        
        if area in CORES_AREAS:
            cor_info = CORES_AREAS[area]
            status = "✅ COM COR"
            areas_com_cores += 1
            print(f"{area:20} | {qtd_agentes:3} agentes | {status} | {cor_info['cor']}")
        else:
            status = "❌ SEM COR"
            areas_sem_cores += 1
            print(f"{area:20} | {qtd_agentes:3} agentes | {status} | DEFINIR COR")
    
    print("="*60)
    print(f"📈 RESUMO:")
    print(f"   Total de agentes: {total_agentes}")
    print(f"   Áreas com cores:  {areas_com_cores}")
    print(f"   Áreas sem cores:  {areas_sem_cores}")
    print(f"   Cobertura:        {(areas_com_cores/(areas_com_cores+areas_sem_cores)*100):.1f}%")
    
    if areas_sem_cores > 0:
        print(f"\n⚠️  ATENÇÃO: {areas_sem_cores} áreas precisam de cores definidas")
    
    return {
        'total_agentes': total_agentes,
        'areas_com_cores': areas_com_cores,
        'areas_sem_cores': areas_sem_cores,
        'agentes_por_area': agentes_por_area
    }

def main():
    """Função principal"""
    print("🎨 Aplicando cores padronizadas por área jurídica...")
    
    # 1. Gerar relatório
    relatorio = relatorio_aplicacao()
    
    # 2. Aplicar cores na página de validação
    if aplicar_cores_validacao_multi_agente():
        print("✅ CSS de cores aplicado na página de validação")
    
    # 3. Criar função JavaScript
    js_cores = criar_funcao_javascript_cores()
    with open('static/js/cores_areas_automatico.js', 'w', encoding='utf-8') as f:
        f.write(js_cores)
    print("✅ Função JavaScript criada em static/js/cores_areas_automatico.js")
    
    print("\n🎯 Aplicação de cores concluída!")
    print("📝 Documento padrão: PADRAO_CORES_AREAS_JURIDICAS.md")
    print("🔧 CSS atualizado na página de validação multi-agente")
    print("⚡ JavaScript criado para aplicação dinâmica")

if __name__ == "__main__":
    main()