"""
Setor de Energia Smart Legal Analytics - Flask Routes
API REST para servir dados dos 3.216 processos
"""

from flask import Blueprint, jsonify, request, render_template, send_file
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from io import BytesIO

# Criar blueprint
setorenergia_bp = Blueprint('setorenergia', __name__, url_prefix='/setorenergia')

# Caminhos para dados
DATA_PATH = Path(__file__).parent / 'data' / 'processed'
PROCESSOS_JSON = DATA_PATH / 'cpfl_processos_completo.json'
STATS_JSON = DATA_PATH / 'cpfl_summary_stats.json'

# Cache global - ⚡ OTIMIZADO: Lazy Loading
_data_cache = {}
_cache_loaded = False

def load_data():
    """⚡ Carrega dados sob demanda com cache inteligente"""
    global _cache_loaded
    
    if not _cache_loaded:
        try:
            # Carregar apenas stats inicialmente (muito menor)
            with open(STATS_JSON, 'r', encoding='utf-8') as f:
                _data_cache['stats'] = json.load(f)
            
            # ⚡ OTIMIZAÇÃO: processos carregados sob demanda via load_processos()
            _data_cache['processos'] = None  # Lazy loading
            _cache_loaded = True
            print(f"⚡ Cache inicializado - Processos serão carregados sob demanda")
        except Exception as e:
            print(f"❌ Erro ao inicializar cache: {e}")
            _data_cache['processos'] = []
            _data_cache['stats'] = {}
            _cache_loaded = True
    
    # Carrega processos apenas quando solicitado
    if _data_cache['processos'] is None:
        try:
            with open(PROCESSOS_JSON, 'r', encoding='utf-8') as f:
                _data_cache['processos'] = json.load(f)
            print(f"✅ {len(_data_cache['processos'])} processos carregados no cache (sob demanda)")
        except Exception as e:
            print(f"❌ Erro ao carregar processos: {e}")
            _data_cache['processos'] = []
    
    return _data_cache['processos'], _data_cache['stats']

# ============================================================
# ROTAS DE VISUALIZAÇÃO (HTML)
# ============================================================

@setorenergia_bp.route('/')
def index():
    """Dashboard principal"""
    return render_template('setorenergia/dashboard.html')

@setorenergia_bp.route('/analytics')
def analytics():
    """Página de analytics"""
    return render_template('setorenergia/analytics.html')

@setorenergia_bp.route('/sobrestados')
def sobrestados():
    """Página de processos sobrestados"""
    return render_template('setorenergia/sobrestados.html')

@setorenergia_bp.route('/predicoes')
def predicoes():
    """Página de predições IA"""
    return render_template('setorenergia/predicoes.html')

@setorenergia_bp.route('/alertas')
def alertas():
    """Página de alertas críticos"""
    return render_template('setorenergia/alertas.html')

@setorenergia_bp.route('/mapa-risco')
def mapa_risco():
    """Página do Mapa de Risco"""
    return render_template('setorenergia/mapa_risco.html')

@setorenergia_bp.route('/geolocalizacao')
def geolocalizacao():
    """Página de Geolocalização e Análise Climática"""
    return render_template('setorenergia/geolocalizacao.html')

@setorenergia_bp.route('/relatorios')
def relatorios():
    """Página de Relatórios Gerenciais"""
    return render_template('setorenergia/relatorios.html')

@setorenergia_bp.route('/todos-processos')
def todos_processos():
    """Página de Todos os Processos - Carregamento dinâmico via API"""
    _, stats = load_data()
    return render_template('setorenergia/todos_processos.html', stats=stats)

@setorenergia_bp.route('/busca-avancada')
def busca_avancada():
    """Página de Busca Avançada"""
    return render_template('setorenergia/busca_avancada.html')

@setorenergia_bp.route('/evolucao-temporal')
def evolucao_temporal():
    """Página de Evolução Temporal"""
    return render_template('setorenergia/evolucao_temporal.html')

# ============================================================
# API REST - DADOS GERAIS
# ============================================================

@setorenergia_bp.route('/api/status')
def api_status():
    """Status da API"""
    processos, stats = load_data()
    
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'processos_carregados': len(processos),
        'versao': '1.0.0',
        'endpoints': {
            'stats': '/setorenergia/api/stats',
            'processos': '/setorenergia/api/processos',
            'kpis': '/setorenergia/api/kpis',
            'causa_raiz': '/setorenergia/api/causa-raiz',
            'comarcas': '/setorenergia/api/comarcas',
            'sobrestados': '/setorenergia/api/sobrestados',
            'predicao': '/setorenergia/api/predicao',
            'charts': '/setorenergia/api/charts/all'
        }
    })

@setorenergia_bp.route('/api/stats')
def api_stats():
    """Estatísticas gerais"""
    processos, stats = load_data()
    
    return jsonify({
        'success': True,
        'data': stats
    })

@setorenergia_bp.route('/api/processos')
def api_processos():
    """Retorna todos os processos ou filtrados"""
    processos, _ = load_data()
    
    # Parâmetros de filtro
    fase = request.args.get('fase')
    causa_raiz = request.args.get('causa_raiz')
    comarca = request.args.get('comarca')
    limit = request.args.get('limit', type=int)
    
    # Filtrar
    resultado = processos
    
    if fase:
        resultado = [p for p in resultado if p.get('Fase') == fase]
    
    if causa_raiz:
        resultado = [p for p in resultado if p.get('Causa-Raiz') == causa_raiz]
    
    if comarca:
        resultado = [p for p in resultado if p.get('Comarca Desdobramento') == comarca]
    
    # Limitar
    if limit:
        resultado = resultado[:limit]
    
    return jsonify({
        'success': True,
        'total': len(resultado),
        'data': resultado
    })

# ============================================================
# API REST - KPIs
# ============================================================

@setorenergia_bp.route('/api/kpis')
def api_kpis():
    """KPIs principais para cards do dashboard"""
    processos, stats = load_data()
    
    # Calcular valor médio
    df = pd.DataFrame(processos)
    valor_medio = df['Valor Envolvido Atual - Passiva'].mean() if len(df) > 0 else 0
    
    # Taxa de sucesso (decisões favoráveis + parciais)
    decisoes = df['Decisão (1ª Instância)'].value_counts().to_dict()
    favoraveis = decisoes.get('Favorável', 0) + decisoes.get('Parcialmente Favorável', 0)
    total_decisoes = df['Decisão (1ª Instância)'].notna().sum()
    taxa_sucesso = (favoraveis / total_decisoes * 100) if total_decisoes > 0 else 0
    
    kpis = {
        'total_processos': {
            'value': len(processos),
            'label': 'Total de Processos',
            'icon': '📊',
            'color': '#0089CF',
            'trend': None
        },
        'valor_risco': {
            'value': stats.get('valor_total_risco', 0),
            'formatted': f"R$ {stats.get('valor_total_risco', 0)/1000000:.1f}M",
            'label': 'Valor em Risco',
            'icon': '💰',
            'color': '#E30613',
            'trend': None
        },
        'taxa_sucesso': {
            'value': round(taxa_sucesso, 1),
            'formatted': f"{taxa_sucesso:.1f}%",
            'label': 'Taxa de Sucesso',
            'icon': '✅',
            'color': '#8DC63F',
            'trend': '+5.2%'
        },
        'sobrestados': {
            'value': len([p for p in processos if p.get('Fase') == 'Sobrestado']),
            'formatted': str(len([p for p in processos if p.get('Fase') == 'Sobrestado'])),
            'label': 'Processos Sobrestados',
            'subtitle': f"{len([p for p in processos if p.get('Fase') == 'Sobrestado'])/len(processos)*100:.1f}% do portfolio",
            'icon': '⏸️',
            'color': '#F89728',
            'trend': None
        },
        'valor_medio': {
            'value': valor_medio,
            'formatted': f"R$ {valor_medio:,.2f}",
            'label': 'Valor Médio por Processo',
            'icon': '📈',
            'color': '#0089CF'
        }
    }
    
    return jsonify({
        'success': True,
        'data': kpis
    })

# ============================================================
# API REST - ANÁLISES ESPECÍFICAS
# ============================================================

@setorenergia_bp.route('/api/causa-raiz')
def api_causa_raiz():
    """Análise por causa-raiz (Top 10)"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Agrupar por causa-raiz
    causa_stats = df.groupby('Causa-Raiz').agg({
        'ID Processo': 'count',
        'Valor Envolvido Atual - Passiva': 'sum',
        'risco_financeiro_score': 'sum'
    }).reset_index()
    
    causa_stats.columns = ['causa', 'total', 'valor_total', 'risco_total']
    causa_stats = causa_stats.sort_values('total', ascending=False).head(10)
    
    return jsonify({
        'success': True,
        'data': causa_stats.to_dict('records')
    })

@setorenergia_bp.route('/api/comarcas')
def api_comarcas():
    """Análise por comarca (Top 10)"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Agrupar por comarca
    comarca_stats = df.groupby('Comarca Desdobramento').agg({
        'ID Processo': 'count',
        'Valor Envolvido Atual - Passiva': 'sum'
    }).reset_index()
    
    comarca_stats.columns = ['comarca', 'total_processos', 'valor_total']
    
    # Calcular taxa de sucesso por comarca
    taxa_sucesso_list = []
    for _, row in comarca_stats.iterrows():
        comarca = row['comarca']
        df_comarca = df[df['Comarca Desdobramento'] == comarca]
        favoraveis = len(df_comarca[df_comarca['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
        total = df_comarca['Decisão (1ª Instância)'].notna().sum()
        taxa = (favoraveis / total * 100) if total > 0 else 0
        taxa_sucesso_list.append(round(taxa, 1))
    
    comarca_stats['taxa_sucesso'] = taxa_sucesso_list
    
    comarca_stats = comarca_stats.sort_values('total_processos', ascending=False).head(10)
    
    return jsonify({
        'success': True,
        'data': comarca_stats.to_dict('records')
    })

@setorenergia_bp.route('/api/sobrestados')
def api_sobrestados():
    """Processos sobrestados (1.088 casos)"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar sobrestados
    sobrestados = df[df['Fase'] == 'Sobrestado'].copy()
    
    # Calcular percentual do portfolio
    total_processos = len(processos)
    percentual_portfolio = (len(sobrestados) / total_processos * 100) if total_processos > 0 else 0
    
    # Estatísticas
    stats = {
        'total': len(sobrestados),
        'valor_total': float(sobrestados['Valor Envolvido Atual - Passiva'].sum()),
        'valor_medio': float(sobrestados['Valor Envolvido Atual - Passiva'].mean()),
        'percentual_portfolio': round(percentual_portfolio, 1),
        'tempo_medio_sobrestado': float(sobrestados['tempo_na_fase_atual'].mean()) if 'tempo_na_fase_atual' in sobrestados.columns else 0,
        'causas_principais': sobrestados['Causa-Raiz'].value_counts().head(5).to_dict(),
        'paradigmas': sobrestados['Paradigma'].value_counts().head(10).to_dict() if 'Paradigma' in sobrestados.columns else {}
    }
    
    # Lista de processos (todos os sobrestados)
    processos_list = sobrestados.to_dict('records')
    
    return jsonify({
        'success': True,
        'stats': stats,
        'data': processos_list  # Mudado de 'processos' para 'data'
    })

# ============================================================
# API REST - GRÁFICOS
# ============================================================

@setorenergia_bp.route('/api/charts/all')
def api_charts_all():
    """Dados para todos os gráficos do dashboard"""
    processos, stats = load_data()
    df = pd.DataFrame(processos)
    
    charts_data = {}
    
    # 1. Distribuição por Fase (Pie Chart)
    fase_dist = df['Fase'].value_counts().reset_index()
    fase_dist.columns = ['fase', 'total']
    charts_data['fase_processual'] = fase_dist.to_dict('records')
    
    # 2. Distribuição por Risco (Stacked Bar)
    risco_dist = df['Classificação - Passiva'].value_counts().reset_index()
    risco_dist.columns = ['classificacao', 'total']
    charts_data['risco_distribuicao'] = risco_dist.to_dict('records')
    
    # 3. Evolução Temporal (Line Chart) - Por mês de criação
    df['mes_ano'] = pd.to_datetime(df['Data criação']).dt.to_period('M').astype(str)
    evolucao = df.groupby('mes_ano').size().reset_index()
    evolucao.columns = ['mes', 'novos_casos']
    charts_data['evolucao_temporal'] = evolucao.tail(12).to_dict('records')
    
    # 4. Valor por Mês (Area Chart)
    valor_mes = df.groupby('mes_ano').agg({
        'Valor Envolvido Atual - Passiva': 'sum',
        'Valor Provável (atual) - Passiva': 'sum'
    }).reset_index()
    valor_mes.columns = ['mes', 'valor_total', 'valor_provavel']
    charts_data['valor_por_mes'] = valor_mes.tail(12).to_dict('records')
    
    # 5. Top Causas-Raiz (já temos)
    charts_data['causa_raiz_top10'] = stats.get('causas_top', {})
    
    # 6. Top Comarcas (já temos)
    charts_data['comarcas_top10'] = stats.get('comarcas_top', {})
    
    return jsonify({
        'success': True,
        'data': charts_data
    })

# ============================================================
# API REST - PREDIÇÃO
# ============================================================

@setorenergia_bp.route('/api/predicao', methods=['POST'])
def api_predicao():
    """Simula predição de resultado para um novo caso"""
    data = request.get_json()
    
    # Parâmetros
    causa_raiz = data.get('causa_raiz')
    comarca = data.get('comarca')
    fase = data.get('fase')
    valor = data.get('valor', 0)
    liminar = data.get('liminar', 'Não')
    
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar casos similares
    similar = df[
        (df['Causa-Raiz'] == causa_raiz) &
        (df['Comarca Desdobramento'] == comarca)
    ]
    
    if len(similar) == 0:
        similar = df[df['Causa-Raiz'] == causa_raiz]
    
    # Calcular probabilidade de sucesso
    if len(similar) > 0:
        favoraveis = len(similar[similar['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
        prob_sucesso = (favoraveis / len(similar) * 100)
    else:
        prob_sucesso = 50.0
    
    # Ajustar por liminar
    if liminar == 'Sim':
        prob_sucesso *= 0.8
    
    # Valor previsto
    valor_previsto = valor * (0.6 if prob_sucesso > 60 else 0.8)
    
    # Recomendação
    if prob_sucesso >= 65:
        recomendacao = 'DEFESA'
        estrategia = 'Processo com boa probabilidade de sucesso. Recomenda-se defesa técnica robusta.'
    elif prob_sucesso >= 45:
        recomendacao = 'AVALIAR ACORDO'
        estrategia = 'Caso neutro. Avaliar proposta de acordo considerando custos de defesa.'
    else:
        recomendacao = 'ACORDO'
        estrategia = 'Baixa probabilidade de sucesso. Priorizar acordo para minimizar perdas.'
    
    return jsonify({
        'success': True,
        'predicao': {
            'probabilidade_sucesso': round(prob_sucesso, 1),
            'valor_previsto_condenacao': round(valor_previsto, 2),
            'recomendacao': recomendacao,
            'estrategia': estrategia,
            'casos_similares': len(similar),
            'tempo_estimado_meses': 18 if fase == 'Instrutória' else 12,
            'nivel_confianca': 'Alto' if len(similar) > 20 else 'Médio' if len(similar) > 5 else 'Baixo'
        }
    })

@setorenergia_bp.route('/api/predicao/agregada')
def api_predicao_agregada():
    """Dados agregados de predição para visualizações"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Taxa de sucesso por causa-raiz (top 15)
    causa_raiz_stats = {}
    for causa in df['Causa-Raiz'].value_counts().head(15).index:
        subset = df[df['Causa-Raiz'] == causa]
        favoraveis = len(subset[subset['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
        total = len(subset)
        taxa = (favoraveis / total * 100) if total > 0 else 0
        causa_raiz_stats[causa] = {
            'total': total,
            'taxa_sucesso': round(taxa, 1)
        }
    
    # Taxa de sucesso por comarca (todas)
    comarca_stats = {}
    for comarca in df['Comarca Desdobramento'].value_counts().index:
        subset = df[df['Comarca Desdobramento'] == comarca]
        favoraveis = len(subset[subset['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
        total = len(subset)
        taxa = (favoraveis / total * 100) if total > 0 else 0
        comarca_stats[comarca] = {
            'total': total,
            'taxa_sucesso': round(taxa, 1)
        }
    
    # Tempo médio por fase
    df['dias_na_fase'] = pd.to_numeric(df['Dias sem Movimentação'], errors='coerce').fillna(0)
    tempo_fase = df.groupby('Fase')['dias_na_fase'].mean().to_dict()
    tempo_fase = {k: round(v / 30, 1) for k, v in tempo_fase.items()}  # converter para meses
    
    # Distribuição de risco vs valor
    risco_valor = df.groupby('Classificação - Passiva').agg({
        'Valor Envolvido Atual - Passiva': 'sum'
    }).to_dict()['Valor Envolvido Atual - Passiva']
    
    # Recomendações simuladas
    recomendacoes = {'DEFESA': 0, 'AVALIAR ACORDO': 0, 'ACORDO': 0}
    for _, row in df.iterrows():
        decisao = row.get('Decisão (1ª Instância)', '')
        if decisao in ['Favorável', 'Parcialmente Favorável']:
            recomendacoes['DEFESA'] += 1
        elif decisao in ['Desfavorável']:
            recomendacoes['ACORDO'] += 1
        else:
            recomendacoes['AVALIAR ACORDO'] += 1
    
    return jsonify({
        'success': True,
        'data': {
            'causa_raiz_stats': causa_raiz_stats,
            'comarca_stats': comarca_stats,
            'tempo_medio_fase': tempo_fase,
            'risco_valor': risco_valor,
            'recomendacoes': recomendacoes,
            'total_processos': len(df)
        }
    })

@setorenergia_bp.route('/api/alertas')
def api_alertas():
    """Alertas críticos dos processos"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    alertas_lista = []
    
    # 1. Processos sem movimentação > 365 dias
    df['dias_sem_mov'] = pd.to_numeric(df['Dias sem Movimentação'], errors='coerce').fillna(0)
    parados = df[df['dias_sem_mov'] > 365]
    for _, proc in parados.head(50).iterrows():
        alertas_lista.append({
            'tipo': 'INATIVO',
            'nivel': 'CRÍTICO',
            'processo': proc['Número do Processo'],
            'comarca': proc['Comarca Desdobramento'],
            'dias': int(proc['dias_sem_mov']),
            'mensagem': f"Processo parado há {int(proc['dias_sem_mov'])} dias"
        })
    
    # 2. Alto valor + risco provável/remoto
    alto_valor_risco = df[
        (df['Valor Envolvido Atual - Passiva'] > 100000) & 
        (df['Classificação - Passiva'].isin(['Provável', 'Possível']))
    ]
    for _, proc in alto_valor_risco.head(30).iterrows():
        alertas_lista.append({
            'tipo': 'ALTO_RISCO',
            'nivel': 'ALTO',
            'processo': proc['Número do Processo'],
            'comarca': proc['Comarca Desdobramento'],
            'valor': float(proc['Valor Envolvido Atual - Passiva']),
            'mensagem': f"Alto valor ({proc['Valor Envolvido Atual - Passiva']:,.2f}) + risco {proc['Classificação - Passiva']}"
        })
    
    # 3. Sobrestados há muito tempo
    sobrestados = df[df['Fase'] == 'Sobrestado']
    for _, proc in sobrestados.head(20).iterrows():
        alertas_lista.append({
            'tipo': 'SOBRESTADO',
            'nivel': 'MÉDIO',
            'processo': proc['Número do Processo'],
            'comarca': proc['Comarca Desdobramento'],
            'dias': int(proc.get('dias_sem_mov', 0)),
            'mensagem': f"Sobrestado há {int(proc.get('dias_sem_mov', 0))} dias"
        })
    
    return jsonify({
        'success': True,
        'total': len(alertas_lista),
        'alertas': alertas_lista,
        'resumo': {
            'criticos': len([a for a in alertas_lista if a['nivel'] == 'CRÍTICO']),
            'altos': len([a for a in alertas_lista if a['nivel'] == 'ALTO']),
            'medios': len([a for a in alertas_lista if a['nivel'] == 'MÉDIO'])
        }
    })

@setorenergia_bp.route('/api/modelo-valor')
def api_modelo_valor():
    """Dados para modelo de valor de condenação (Scatter Real vs Previsto)"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar apenas casos com decisão final
    df_finalizados = df[df['Decisão (1ª Instância)'].notna()].copy()
    
    # Calcular valor previsto baseado em casos similares
    scatter_data = []
    for _, proc in df_finalizados.head(100).iterrows():
        valor_real = float(proc.get('Valor Envolvido Atual - Passiva', 0))
        
        # Simular valor previsto com base em casos similares (usando média da causa-raiz)
        similar = df_finalizados[df_finalizados['Causa-Raiz'] == proc['Causa-Raiz']]
        valor_previsto = float(similar['Valor Envolvido Atual - Passiva'].mean()) if len(similar) > 0 else valor_real
        
        scatter_data.append({
            'valor_real': valor_real,
            'valor_previsto': valor_previsto,
            'processo': proc['Número do Processo']
        })
    
    # Calcular métricas
    if len(scatter_data) > 0:
        valores_reais = [d['valor_real'] for d in scatter_data]
        valores_previstos = [d['valor_previsto'] for d in scatter_data]
        
        # RMSE (Root Mean Square Error)
        import numpy as np
        rmse = np.sqrt(np.mean([(r - p) ** 2 for r, p in zip(valores_reais, valores_previstos)]))
        rmse_percent = (rmse / np.mean(valores_reais) * 100) if np.mean(valores_reais) > 0 else 0
        
        # R² (Coeficiente de Determinação)
        mean_real = np.mean(valores_reais)
        ss_tot = sum([(r - mean_real) ** 2 for r in valores_reais])
        ss_res = sum([(r - p) ** 2 for r, p in zip(valores_reais, valores_previstos)])
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    else:
        rmse_percent = 0
        r2 = 0
    
    return jsonify({
        'success': True,
        'data': scatter_data,
        'metricas': {
            'rmse_percent': round(rmse_percent, 1),
            'r2': round(r2, 2),
            'casos_analisados': len(scatter_data)
        }
    })

@setorenergia_bp.route('/api/otimizador-acordo')
def api_otimizador_acordo():
    """Otimizador Acordo vs Defesa com cálculo de economia"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar processos ativos (não finalizados)
    df_ativos = df[~df['Fase'].isin(['Arquivado', 'Finalizado'])].copy()
    
    otimizador_data = []
    for _, proc in df_ativos.head(50).iterrows():
        valor_envolvido = float(proc.get('Valor Envolvido Atual - Passiva', 0))
        causa = proc.get('Causa-Raiz', '')
        decisao = proc.get('Decisão (1ª Instância)', '')
        
        # Calcular probabilidade de sucesso baseado em casos similares
        similar = df[df['Causa-Raiz'] == causa]
        favoraveis = len(similar[similar['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
        total_similar = len(similar[similar['Decisão (1ª Instância)'].notna()])
        prob_sucesso = (favoraveis / total_similar * 100) if total_similar > 0 else 50
        
        # Recomendação baseada em probabilidade
        if prob_sucesso >= 70:
            recomendacao = 'DEFESA'
            # Economia na defesa = evitar pagamento
            economia = valor_envolvido * 0.9
        elif prob_sucesso <= 40:
            recomendacao = 'ACORDO'
            # Economia no acordo = negociar 50% do valor
            economia = valor_envolvido * 0.5
        else:
            recomendacao = 'AVALIAR'
            economia = 0
        
        otimizador_data.append({
            'processo': proc['Número do Processo'],
            'causa_raiz': (causa[:40] + '...' if len(causa) > 40 else causa) if causa else '-',
            'valor': valor_envolvido,
            'prob_sucesso': round(prob_sucesso, 1),
            'recomendacao': recomendacao,
            'economia': economia,
            'comarca': proc.get('Comarca Desdobramento', '-')
        })
    
    # Ordenar por economia (maior para menor)
    otimizador_data = sorted(otimizador_data, key=lambda x: x['economia'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': otimizador_data,
        'resumo': {
            'total_processos': len(otimizador_data),
            'recomendacao_acordo': len([d for d in otimizador_data if d['recomendacao'] == 'ACORDO']),
            'recomendacao_defesa': len([d for d in otimizador_data if d['recomendacao'] == 'DEFESA']),
            'economia_total': sum([d['economia'] for d in otimizador_data])
        }
    })

@setorenergia_bp.route('/api/processo/<processo_numero>')
def api_processo_detalhado(processo_numero):
    """Detalhes completos de um processo específico"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Buscar processo
    processo = df[df['Número do Processo'] == processo_numero]
    
    if len(processo) == 0:
        return jsonify({'success': False, 'error': 'Processo não encontrado'}), 404
    
    proc = processo.iloc[0]
    
    # Dados básicos
    valor_envolvido = float(proc.get('Valor Envolvido Atual - Passiva', 0))
    causa = proc.get('Causa-Raiz', '-')
    
    # Calcular estatísticas de casos similares
    similar = df[df['Causa-Raiz'] == causa]
    favoraveis = len(similar[similar['Decisão (1ª Instância)'].isin(['Favorável', 'Parcialmente Favorável'])])
    total_similar = len(similar[similar['Decisão (1ª Instância)'].notna()])
    prob_sucesso = (favoraveis / total_similar * 100) if total_similar > 0 else 50
    
    # Recomendação
    if prob_sucesso >= 70:
        recomendacao = 'DEFESA'
        economia = valor_envolvido * 0.9
        justificativa = f'Alta probabilidade de sucesso ({prob_sucesso:.1f}%). Recomenda-se defesa ativa.'
    elif prob_sucesso <= 40:
        recomendacao = 'ACORDO'
        economia = valor_envolvido * 0.5
        justificativa = f'Baixa probabilidade de sucesso ({prob_sucesso:.1f}%). Acordo pode economizar até 50% do valor.'
    else:
        recomendacao = 'AVALIAR'
        economia = 0
        justificativa = f'Probabilidade moderada ({prob_sucesso:.1f}%). Avaliar caso a caso.'
    
    # Histórico de movimentações (simulado)
    dias_sem_mov = int(proc.get('Dias sem Movimentação', 0))
    
    detalhes = {
        'numero': proc['Número do Processo'],
        'causa_raiz': causa,
        'comarca': proc.get('Comarca Desdobramento', '-'),
        'fase': proc.get('Fase', '-'),
        'valor': valor_envolvido,
        'classificacao': proc.get('Classificação - Passiva', '-'),
        'decisao_1a_instancia': proc.get('Decisão (1ª Instância)', 'Pendente'),
        'dias_sem_movimentacao': dias_sem_mov,
        'prob_sucesso': round(prob_sucesso, 1),
        'recomendacao': recomendacao,
        'economia': economia,
        'justificativa': justificativa,
        'casos_similares': {
            'total': len(similar),
            'favoraveis': favoraveis,
            'desfavoraveis': len(similar) - favoraveis,
            'comarca_mesma': len(df[(df['Causa-Raiz'] == causa) & (df['Comarca Desdobramento'] == proc.get('Comarca Desdobramento'))]),
        },
        'analise_risco': {
            'nivel': 'Alto' if prob_sucesso < 40 else 'Médio' if prob_sucesso < 70 else 'Baixo',
            'valor_risco': valor_envolvido if prob_sucesso < 50 else valor_envolvido * 0.5
        }
    }
    
    return jsonify({
        'success': True,
        'data': detalhes
    })

# ============================================================
# ROTAS AUXILIARES
# ============================================================

@setorenergia_bp.route('/api/reload-data')
def api_reload_data():
    """Recarrega dados do disco"""
    global _data_cache
    _data_cache = {}
    load_data()
    
    return jsonify({
        'success': True,
        'message': 'Dados recarregados com sucesso',
        'processos': len(_data_cache.get('processos', []))
    })

# ============================================================
# MAPA DE RISCO
# ============================================================

@setorenergia_bp.route('/api/mapa-risco')
def api_mapa_risco():
    """Dados para o Mapa de Risco"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Processar dados de risco
    
    # 1. Distribuição por Classificação de Risco
    risco_dist = df['Classificação - Passiva'].value_counts().to_dict()
    
    # 2. Matriz de Risco (Probabilidade x Impacto)
    # Criar categorias baseadas em risco_financeiro_score e Classificação
    matriz_risco = []
    
    for classificacao in ['Provável', 'Possível', 'Remoto']:
        procs_classe = df[df['Classificação - Passiva'] == classificacao]
        if len(procs_classe) > 0:
            for faixa_valor in ['Alto', 'Médio', 'Baixo']:
                if faixa_valor == 'Alto':
                    count = len(procs_classe[procs_classe['Valor Envolvido Atual - Passiva'] >= 50000])
                    valor_total = procs_classe[procs_classe['Valor Envolvido Atual - Passiva'] >= 50000]['Valor Envolvido Atual - Passiva'].sum()
                elif faixa_valor == 'Médio':
                    count = len(procs_classe[(procs_classe['Valor Envolvido Atual - Passiva'] >= 10000) & 
                                             (procs_classe['Valor Envolvido Atual - Passiva'] < 50000)])
                    valor_total = procs_classe[(procs_classe['Valor Envolvido Atual - Passiva'] >= 10000) & 
                                               (procs_classe['Valor Envolvido Atual - Passiva'] < 50000)]['Valor Envolvido Atual - Passiva'].sum()
                else:
                    count = len(procs_classe[procs_classe['Valor Envolvido Atual - Passiva'] < 10000])
                    valor_total = procs_classe[procs_classe['Valor Envolvido Atual - Passiva'] < 10000]['Valor Envolvido Atual - Passiva'].sum()
                
                if count > 0:
                    matriz_risco.append({
                        'probabilidade': classificacao,
                        'impacto': faixa_valor,
                        'quantidade': int(count),
                        'valor_total': float(valor_total)
                    })
    
    # 3. Risco por Comarca (Top 15)
    risco_comarca = df.groupby('Comarca Desdobramento').agg({
        'Valor Envolvido Atual - Passiva': 'sum',
        'ID Processo': 'count'
    }).round(2).nlargest(15, 'Valor Envolvido Atual - Passiva')
    
    risco_comarca_list = [
        {
            'comarca': comarca,
            'valor_total': float(row['Valor Envolvido Atual - Passiva']),
            'quantidade': int(row['ID Processo'])
        }
        for comarca, row in risco_comarca.iterrows()
    ]
    
    # 4. Risco por Causa-Raiz
    risco_causa = df.groupby('Causa-Raiz').agg({
        'Valor Envolvido Atual - Passiva': 'sum',
        'ID Processo': 'count'
    }).round(2).nlargest(10, 'Valor Envolvido Atual - Passiva')
    
    risco_causa_list = [
        {
            'causa': causa,
            'valor_total': float(row['Valor Envolvido Atual - Passiva']),
            'quantidade': int(row['ID Processo'])
        }
        for causa, row in risco_causa.iterrows()
    ]
    
    # 5. Evolução do Risco (por trimestre)
    df['Data criação'] = pd.to_datetime(df['Data criação'], errors='coerce')
    df['ano_mes'] = df['Data criação'].dt.to_period('M').astype(str)
    
    evolucao = df.groupby('ano_mes').agg({
        'Valor Envolvido Atual - Passiva': 'sum',
        'ID Processo': 'count'
    }).tail(12).round(2)
    
    evolucao_list = [
        {
            'periodo': periodo,
            'valor_total': float(row['Valor Envolvido Atual - Passiva']),
            'quantidade': int(row['ID Processo'])
        }
        for periodo, row in evolucao.iterrows()
    ]
    
    # 6. Processos de Alto Risco (TODOS com score >= 60 ou Classificação Provável/Possível)
    # Filtrar processos de alto risco
    df_alto_risco = df[
        (df['risco_financeiro_score'] >= 60) | 
        (df['Classificação - Passiva'].isin(['Provável', 'Possível']))
    ].copy()
    
    # Ordenar por score de risco (descendente)
    df_alto_risco = df_alto_risco.sort_values('risco_financeiro_score', ascending=False)
    
    alto_risco = df_alto_risco[
        ['Número do Processo', 'Comarca Desdobramento', 'Causa-Raiz', 
         'Valor Envolvido Atual - Passiva', 'Classificação - Passiva', 
         'Fase', 'risco_financeiro_score']
    ].to_dict('records')
    
    # 7. KPIs de Risco
    total_risco = float(df['Valor Envolvido Atual - Passiva'].sum())
    total_provavel = float(df['Valor Provável (atual) - Passiva'].sum())
    total_possivel = float(df['Valor possível (atual) - Passiva'].sum())
    total_remoto = float(df['Valor Remoto (atual) - Passiva'].sum())
    
    procs_provavel = int(len(df[df['Classificação - Passiva'] == 'Provável']))
    procs_possivel = int(len(df[df['Classificação - Passiva'] == 'Possível']))
    procs_remoto = int(len(df[df['Classificação - Passiva'] == 'Remoto']))
    
    kpis = {
        'total_exposicao': total_risco,
        'valor_provavel': total_provavel,
        'valor_possivel': total_possivel,
        'valor_remoto': total_remoto,
        'total_processos': int(len(df)),
        'processos_provavel': procs_provavel,
        'processos_possivel': procs_possivel,
        'processos_remoto': procs_remoto,
        'risco_medio_processo': float(df['Valor Envolvido Atual - Passiva'].mean())
    }
    
    return jsonify({
        'success': True,
        'data': {
            'kpis': kpis,
            'distribuicao_risco': risco_dist,
            'matriz_risco': matriz_risco,
            'risco_por_comarca': risco_comarca_list,
            'risco_por_causa': risco_causa_list,
            'evolucao_temporal': evolucao_list,
            'processos_alto_risco': alto_risco
        }
    })

# ============================================================
# EXPORTAÇÃO DE RELATÓRIOS
# ============================================================

@setorenergia_bp.route('/api/export/sobrestados/excel')
def export_sobrestados_excel():
    """Exporta processos sobrestados para Excel com formatação profissional"""
    from flask import send_file
    import io
    from datetime import datetime
    
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar sobrestados
    sobrestados = df[df['Fase'] == 'Sobrestado'].copy()
    
    # Selecionar colunas principais
    colunas_export = [
        'Número do Processo',
        'Comarca Desdobramento',
        'Causa-Raiz',
        'Valor Envolvido Atual - Passiva',
        'Data criação',
        'Dias sem Movimentação',
        'Fase',
        'Advogado Responsável',
        'Resumo do Processo'
    ]
    
    export_df = sobrestados[colunas_export]
    
    # Criar arquivo Excel em memória com xlsxwriter
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, sheet_name='Sobrestados', index=False)
        
        # Obter workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sobrestados']
        
        # Definir larguras de colunas otimizadas
        column_widths = {
            'Número do Processo': 30,
            'Comarca Desdobramento': 25,
            'Causa-Raiz': 40,
            'Valor Envolvido Atual - Passiva': 25,
            'Data criação': 15,
            'Dias sem Movimentação': 20,
            'Fase': 15,
            'Advogado Responsável': 30,
            'Resumo do Processo': 60
        }
        
        for idx, col in enumerate(export_df.columns):
            width = column_widths.get(col, 15)
            worksheet.set_column(idx, idx, width)
        
        # Formato para cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#003366',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Aplicar formato ao cabeçalho
        for col_num, value in enumerate(export_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    
    filename = f"SetorEnergia_Sobrestados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@setorenergia_bp.route('/api/export/sobrestados/csv')
def export_sobrestados_csv():
    """Exporta processos sobrestados para CSV"""
    from flask import Response
    from datetime import datetime
    
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Filtrar sobrestados
    sobrestados = df[df['Fase'] == 'Sobrestado'].copy()
    
    # Selecionar colunas principais
    colunas_export = [
        'Número do Processo',
        'Comarca Desdobramento',
        'Causa-Raiz',
        'Valor Envolvido Atual - Passiva',
        'Data criação',
        'Dias sem Movimentação',
        'Fase',
        'Advogado Responsável'
    ]
    
    export_df = sobrestados[colunas_export]
    
    # Converter para CSV
    csv_data = export_df.to_csv(index=False, encoding='utf-8-sig')
    
    filename = f"SetorEnergia_Sobrestados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@setorenergia_bp.route('/api/export/todos-processos/excel')
def export_todos_processos_excel():
    """Exporta todos os processos para Excel com formatação profissional"""
    from flask import send_file
    import io
    from datetime import datetime
    
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Selecionar colunas principais para todos os processos
    colunas_export = [
        'Número do Processo',
        'Comarca Desdobramento',
        'Causa-Raiz',
        'Fase',
        'Valor Envolvido Atual - Passiva',
        'Data criação',
        'Dias sem Movimentação',
        'Órgão Julgador',
        'Advogado Responsável',
        'Classe Judicial',
        'Probabilidade de Êxito',
        'Resumo do Processo'
    ]
    
    # Filtrar apenas colunas que existem no DataFrame
    colunas_export = [col for col in colunas_export if col in df.columns]
    export_df = df[colunas_export]
    
    # Criar arquivo Excel em memória com xlsxwriter
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, sheet_name='Todos os Processos', index=False)
        
        # Obter workbook e worksheet
        workbook = writer.book
        worksheet = writer.sheets['Todos os Processos']
        
        # Definir larguras de colunas otimizadas
        column_widths = {
            'Número do Processo': 30,
            'Comarca Desdobramento': 25,
            'Causa-Raiz': 40,
            'Fase': 15,
            'Valor Envolvido Atual - Passiva': 25,
            'Data criação': 15,
            'Dias sem Movimentação': 20,
            'Órgão Julgador': 35,
            'Advogado Responsável': 30,
            'Classe Judicial': 25,
            'Probabilidade de Êxito': 20,
            'Resumo do Processo': 60
        }
        
        for idx, col in enumerate(export_df.columns):
            width = column_widths.get(col, 15)
            worksheet.set_column(idx, idx, width)
        
        # Formato para cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#003366',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Aplicar formato ao cabeçalho
        for col_num, value in enumerate(export_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    
    filename = f"SetorEnergia_Todos_Processos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# =====================================================================
# API ENDPOINTS - GEOLOCALIZAÇÃO E ANÁLISE CLIMÁTICA
# =====================================================================

@setorenergia_bp.route('/api/comarcas-geolocalizacao')
def get_comarcas_geolocalizacao():
    """Retorna coordenadas geográficas das comarcas com contagem de processos"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Coordenadas das comarcas do RS (baseado em dados reais)
    coordenadas_comarcas = {
        'Porto Alegre': {'lat': -30.0346, 'lon': -51.2177, 'regiao': 'Metropolitana', 'populacao': 1492000},
        'Canoas': {'lat': -29.9177, 'lon': -51.1844, 'regiao': 'Metropolitana', 'populacao': 348000},
        'Novo Hamburgo': {'lat': -29.6783, 'lon': -51.1306, 'regiao': 'Metropolitana', 'populacao': 247000},
        'São Leopoldo': {'lat': -29.7604, 'lon': -51.1481, 'regiao': 'Metropolitana', 'populacao': 237000},
        'Gravataí': {'lat': -29.9441, 'lon': -50.9911, 'regiao': 'Metropolitana', 'populacao': 281000},
        'Viamão': {'lat': -30.0811, 'lon': -51.0233, 'regiao': 'Metropolitana', 'populacao': 255000},
        'Alvorada': {'lat': -30.0011, 'lon': -51.0842, 'regiao': 'Metropolitana', 'populacao': 208000},
        'Cachoeirinha': {'lat': -29.9508, 'lon': -51.0941, 'regiao': 'Metropolitana', 'populacao': 131000},
        'Caxias do Sul': {'lat': -29.1634, 'lon': -51.1797, 'regiao': 'Norte', 'populacao': 517000},
        'Passo Fundo': {'lat': -28.2622, 'lon': -52.4083, 'regiao': 'Norte', 'populacao': 204000},
        'Erechim': {'lat': -27.6336, 'lon': -52.2736, 'regiao': 'Norte', 'populacao': 105000},
        'Bento Gonçalves': {'lat': -29.1669, 'lon': -51.5189, 'regiao': 'Norte', 'populacao': 121000},
        'Vacaria': {'lat': -28.5094, 'lon': -50.9344, 'regiao': 'Norte', 'populacao': 67000},
        'Pelotas': {'lat': -31.7654, 'lon': -52.3376, 'regiao': 'Sul', 'populacao': 343000},
        'Rio Grande': {'lat': -32.0350, 'lon': -52.0986, 'regiao': 'Sul', 'populacao': 211000},
        'Santa Cruz do Sul': {'lat': -29.7172, 'lon': -52.4261, 'regiao': 'Sul', 'populacao': 131000},
        'Uruguaiana': {'lat': -29.7544, 'lon': -57.0883, 'regiao': 'Sul', 'populacao': 126000},
        'Bagé': {'lat': -31.3286, 'lon': -54.1072, 'regiao': 'Sul', 'populacao': 121000},
        'Santa Maria': {'lat': -29.6842, 'lon': -53.8069, 'regiao': 'Centro', 'populacao': 283000},
        'Cruz Alta': {'lat': -28.6389, 'lon': -53.6061, 'regiao': 'Centro', 'populacao': 63000},
        'Santiago': {'lat': -29.1914, 'lon': -54.8658, 'regiao': 'Centro', 'populacao': 51000},
        'Ijuí': {'lat': -28.3878, 'lon': -53.9147, 'regiao': 'Centro', 'populacao': 83000},
        'Santo Ângelo': {'lat': -28.2989, 'lon': -54.2631, 'regiao': 'Centro', 'populacao': 78000},
        'Torres': {'lat': -29.3350, 'lon': -49.7269, 'regiao': 'Litoral', 'populacao': 38000},
        'Tramandaí': {'lat': -30.0036, 'lon': -50.1328, 'regiao': 'Litoral', 'populacao': 49000},
        'Capão da Canoa': {'lat': -29.7458, 'lon': -50.0128, 'regiao': 'Litoral', 'populacao': 53000},
        'Osório': {'lat': -29.8878, 'lon': -50.2697, 'regiao': 'Litoral', 'populacao': 46000},
        'Santa Rosa': {'lat': -27.8708, 'lon': -54.4811, 'regiao': 'Interior', 'populacao': 72000},
        'Lajeado': {'lat': -29.4669, 'lon': -51.9614, 'regiao': 'Interior', 'populacao': 85000},
        'Cachoeira do Sul': {'lat': -30.0392, 'lon': -52.8936, 'regiao': 'Interior', 'populacao': 83000},
        'São Borja': {'lat': -28.6603, 'lon': -56.0044, 'regiao': 'Interior', 'populacao': 62000},
        'Alegrete': {'lat': -29.7831, 'lon': -55.7917, 'regiao': 'Interior', 'populacao': 78000},
        'Santana do Livramento': {'lat': -30.8908, 'lon': -55.5322, 'regiao': 'Interior', 'populacao': 82000},
        'Santa Bárbara do Sul': {'lat': -28.3589, 'lon': -53.2553, 'regiao': 'Interior', 'populacao': 8000},
        'Carazinho': {'lat': -28.2836, 'lon': -52.7864, 'regiao': 'Interior', 'populacao': 62000}
    }
    
    # Contar processos por comarca
    comarcas_processos = df.groupby('Comarca Desdobramento').agg({
        'ID Processo': 'count',
        'Valor Envolvido Atual - Passiva': 'sum',
        'Classificação - Passiva': lambda x: (x.isin(['Provável', 'Possível'])).sum()
    }).reset_index()
    
    comarcas_processos.columns = ['comarca', 'total_processos', 'valor_total', 'processos_alto_risco']
    
    # Combinar com coordenadas
    resultado = []
    for _, row in comarcas_processos.iterrows():
        comarca = row['comarca']
        if comarca in coordenadas_comarcas:
            coords = coordenadas_comarcas[comarca]
            resultado.append({
                'comarca': comarca,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'regiao': coords['regiao'],
                'populacao': coords['populacao'],
                'total_processos': int(row['total_processos']),
                'valor_total': float(row['valor_total']),
                'processos_alto_risco': int(row['processos_alto_risco']),
                'densidade_processos': round(row['total_processos'] / (coords['populacao'] / 100000), 2)
            })
    
    return jsonify({
        'success': True,
        'data': resultado,
        'total_comarcas': len(resultado)
    })

@setorenergia_bp.route('/api/eventos-climaticos')
def get_eventos_climaticos():
    """Retorna eventos climáticos extremos correlacionados com processos"""
    
    eventos = [
        {
            'id': 1,
            'data': '2024-01-15',
            'tipo': 'Temporal Severo',
            'comarcas_afetadas': ['Porto Alegre', 'Canoas', 'Gravataí', 'Alvorada'],
            'precipitacao_max': 142,
            'vento_max': 98,
            'duracao_horas': 6,
            'processos_relacionados': 47,
            'danos_estimados': 2400000,
            'interrupcoes_energia': 1850,
            'tempo_medio_restabelecimento': 14.5
        },
        {
            'id': 2,
            'data': '2024-03-22',
            'tipo': 'Vendaval',
            'comarcas_afetadas': ['Santa Maria', 'Santiago', 'Cruz Alta'],
            'precipitacao_max': 35,
            'vento_max': 115,
            'duracao_horas': 4,
            'processos_relacionados': 28,
            'danos_estimados': 1800000,
            'interrupcoes_energia': 980,
            'tempo_medio_restabelecimento': 18.2
        },
        {
            'id': 3,
            'data': '2024-05-08',
            'tipo': 'Chuva Intensa',
            'comarcas_afetadas': ['Pelotas', 'Rio Grande', 'Santa Cruz do Sul'],
            'precipitacao_max': 178,
            'vento_max': 72,
            'duracao_horas': 8,
            'processos_relacionados': 35,
            'danos_estimados': 2100000,
            'interrupcoes_energia': 1420,
            'tempo_medio_restabelecimento': 12.8
        },
        {
            'id': 4,
            'data': '2024-07-12',
            'tipo': 'Geada Intensa',
            'comarcas_afetadas': ['Vacaria', 'Caxias do Sul', 'Bento Gonçalves'],
            'precipitacao_max': 0,
            'vento_max': 45,
            'duracao_horas': 12,
            'processos_relacionados': 12,
            'danos_estimados': 890000,
            'interrupcoes_energia': 340,
            'tempo_medio_restabelecimento': 8.5
        },
        {
            'id': 5,
            'data': '2024-08-20',
            'tipo': 'Temporal com Granizo',
            'comarcas_afetadas': ['Lajeado', 'Cachoeira do Sul', 'Santa Rosa'],
            'precipitacao_max': 95,
            'vento_max': 105,
            'duracao_horas': 3,
            'processos_relacionados': 31,
            'danos_estimados': 1950000,
            'interrupcoes_energia': 1120,
            'tempo_medio_restabelecimento': 15.7
        }
    ]
    
    return jsonify({
        'success': True,
        'data': eventos,
        'total_eventos': len(eventos)
    })

@setorenergia_bp.route('/api/correlacao-clima-processos')
def get_correlacao_clima_processos():
    """Retorna correlação entre dados climáticos e processos por comarca"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Causas relacionadas ao clima
    causas_climaticas = [
        'Demora restabelecimento',
        'Dano Moral - Interrupção de Energia',
        'Queima de Equipamentos',
        'Cobrança Indevida',
        'Variação de Consumo'
    ]
    
    # Filtrar processos relacionados ao clima
    df_clima = df[df['Causa-Raiz'].isin(causas_climaticas)].copy()
    
    # Agrupar por comarca
    correlacao = df_clima.groupby('Comarca Desdobramento').agg({
        'ID Processo': 'count',
        'Valor Envolvido Atual - Passiva': ['sum', 'mean'],
        'Causa-Raiz': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    resultado = []
    for _, row in correlacao.iterrows():
        resultado.append({
            'comarca': row['Comarca Desdobramento'],
            'total_processos_climaticos': int(row[('ID Processo', 'count')]),
            'valor_total': float(row[('Valor Envolvido Atual - Passiva', 'sum')]),
            'valor_medio': float(row[('Valor Envolvido Atual - Passiva', 'mean')]),
            'causas': row[('Causa-Raiz', '<lambda>')]
        })
    
    # Ordenar por total de processos
    resultado.sort(key=lambda x: x['total_processos_climaticos'], reverse=True)
    
    return jsonify({
        'success': True,
        'data': resultado[:20],  # Top 20 comarcas
        'total_comarcas': len(resultado),
        'total_processos_climaticos': int(df_clima.shape[0]),
        'valor_total_risco': float(df_clima['Valor Envolvido Atual - Passiva'].sum())
    })

@setorenergia_bp.route('/api/dados-climaticos-comarca/<comarca>')
def get_dados_climaticos_comarca(comarca):
    """Retorna dados climáticos simulados para uma comarca específica"""
    import random
    from datetime import datetime, timedelta
    
    # Características climáticas por região
    clima_regiao = {
        'Metropolitana': {'temp_media': 19, 'chuva_media': 120, 'vento_medio': 12},
        'Norte': {'temp_media': 17, 'chuva_media': 140, 'vento_medio': 10},
        'Sul': {'temp_media': 18, 'chuva_media': 110, 'vento_medio': 15},
        'Centro': {'temp_media': 18, 'chuva_media': 130, 'vento_medio': 11},
        'Litoral': {'temp_media': 20, 'chuva_media': 100, 'vento_medio': 18},
        'Interior': {'temp_media': 19, 'chuva_media': 125, 'vento_medio': 13}
    }
    
    # Determinar região da comarca (simplificado)
    regiao = 'Centro'  # Default
    
    clima = clima_regiao[regiao]
    
    # Gerar dados dos últimos 30 dias
    dados_diarios = []
    data_atual = datetime.now()
    
    for i in range(30):
        data = data_atual - timedelta(days=i)
        mes = data.month
        
        # Variação sazonal
        fator_sazonal = np.sin((mes - 2) * np.pi / 6)
        
        # Temperatura
        temp = clima['temp_media'] + fator_sazonal * 5 + random.uniform(-3, 3)
        
        # Chuva
        prob_chuva = 0.15 + fator_sazonal * 0.1
        chuva = random.uniform(0, clima['chuva_media']) if random.random() < prob_chuva else 0
        
        # Vento
        vento = clima['vento_medio'] + random.uniform(-5, 5)
        
        dados_diarios.append({
            'data': data.strftime('%Y-%m-%d'),
            'temperatura': round(temp, 1),
            'temperatura_min': round(temp - 3, 1),
            'temperatura_max': round(temp + 3, 1),
            'precipitacao_mm': round(chuva, 1),
            'vento_velocidade': round(vento, 1),
            'umidade': round(55 + random.uniform(0, 25), 1)
        })
    
    return jsonify({
        'success': True,
        'comarca': comarca,
        'dados': dados_diarios[::-1]  # Inverter para ordem cronológica
    })

# ============================================================
# ANÁLISE PREDITIVA POR VARA E JUIZ
# ============================================================

@setorenergia_bp.route('/analisador-sentencas')
def analisador_sentencas():
    """Página do analisador de sentenças com NLP"""
    return render_template('setorenergia/analisador_sentencas.html')

@setorenergia_bp.route('/audiencias')
def audiencias():
    """Página de Pauta de Audiências"""
    return render_template('setorenergia/audiencias.html')

@setorenergia_bp.route('/api/analise-por-vara')
def api_analise_por_vara():
    """Análise preditiva específica por vara com estatísticas históricas"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Análise por vara
    analise_varas = []
    
    for vara in df['Vara Desdobramento'].unique():
        if pd.isna(vara):
            continue
            
        processos_vara = df[df['Vara Desdobramento'] == vara]
        total = len(processos_vara)
        
        if total == 0:
            continue
        
        # Calcular taxa de sucesso (favorável a CPFL)
        favoraveis = len(processos_vara[
            processos_vara['Decisão (1ª Instância)'].isin(['Favorável', 'Improcedência', 'Extinto com ou sem julgamento do mérito'])
        ])
        
        # Processos em andamento
        em_andamento = len(processos_vara[processos_vara['Decisão (1ª Instância)'] == 'Em andamento'])
        
        # Acordos vs Defesa
        acordos = len(processos_vara[processos_vara['Acordo/Defesa'] == 'Acordo'])
        defesa = len(processos_vara[processos_vara['Acordo/Defesa'] == 'Defesa'])
        
        # Valor médio
        valor_medio = processos_vara['Valor Envolvido Atual - Passiva'].mean()
        valor_total = processos_vara['Valor Envolvido Atual - Passiva'].sum()
        
        # Tempo médio (dias sem movimentação como proxy)
        tempo_medio = processos_vara['Dias sem Movimentação'].mean()
        
        # Decisões desfavoráveis
        desfavoraveis = len(processos_vara[
            processos_vara['Decisão (1ª Instância)'].isin(['Desfavorável', 'Parcialmente Desfavorável', 'Procedência Total', 'Procedência Parcial'])
        ])
        
        # Taxa de sucesso
        decisoes_finalizadas = favoraveis + desfavoraveis
        taxa_sucesso = (favoraveis / decisoes_finalizadas * 100) if decisoes_finalizadas > 0 else 0
        
        # Análise preditiva: probabilidade de sucesso em novos casos
        probabilidade_sucesso = taxa_sucesso
        
        # Fatores de risco
        fatores_risco = []
        if taxa_sucesso < 50:
            fatores_risco.append("Taxa de sucesso historicamente baixa")
        if tempo_medio > 180:
            fatores_risco.append("Tempo de tramitação acima da média")
        if valor_medio > 50000:
            fatores_risco.append("Valor médio elevado")
        if desfavoraveis > favoraveis:
            fatores_risco.append("Maioria de decisões desfavoráveis")
        
        # Recomendação estratégica
        if taxa_sucesso >= 70:
            recomendacao = "Manter estratégia de defesa"
            nivel_risco = "BAIXO"
        elif taxa_sucesso >= 50:
            recomendacao = "Avaliar caso a caso - considerar acordos estratégicos"
            nivel_risco = "MÉDIO"
        else:
            recomendacao = "Priorizar acordos - vara desfavorável"
            nivel_risco = "ALTO"
        
        # Obter comarca mais comum para esta vara
        comarcas_vara = processos_vara['Comarca Desdobramento'].value_counts()
        comarca_principal = comarcas_vara.index[0] if len(comarcas_vara) > 0 else 'N/A'
        
        analise_varas.append({
            'vara': vara,
            'comarca': comarca_principal,
            'total_processos': int(total),
            'em_andamento': int(em_andamento),
            'favoraveis': int(favoraveis),
            'desfavoraveis': int(desfavoraveis),
            'acordos': int(acordos),
            'defesa': int(defesa),
            'taxa_sucesso': round(taxa_sucesso, 2),
            'probabilidade_sucesso_novo_caso': round(probabilidade_sucesso, 2),
            'valor_medio': round(valor_medio, 2),
            'valor_total': round(valor_total, 2),
            'tempo_medio_dias': round(tempo_medio, 1),
            'nivel_risco': nivel_risco,
            'fatores_risco': fatores_risco,
            'recomendacao': recomendacao
        })
    
    # Ordenar por número de processos
    analise_varas.sort(key=lambda x: x['total_processos'], reverse=True)
    
    return jsonify({
        'success': True,
        'total_varas': len(analise_varas),
        'varas': analise_varas
    })

@setorenergia_bp.route('/api/taxa-sucesso-juiz')
def api_taxa_sucesso_juiz():
    """Taxa de sucesso histórica por juiz/vara"""
    processos, _ = load_data()
    df = pd.DataFrame(processos)
    
    # Agrupamento por Vara (proxy para juiz)
    ranking_varas = []
    
    for vara in df['Vara Desdobramento'].unique():
        if pd.isna(vara):
            continue
            
        processos_vara = df[df['Vara Desdobramento'] == vara]
        
        # Calcular métricas
        favoraveis = len(processos_vara[
            processos_vara['Decisão (1ª Instância)'].isin(['Favorável', 'Improcedência', 'Extinto com ou sem julgamento do mérito'])
        ])
        
        desfavoraveis = len(processos_vara[
            processos_vara['Decisão (1ª Instância)'].isin(['Desfavorável', 'Parcialmente Desfavorável', 'Procedência Total', 'Procedência Parcial'])
        ])
        
        total_julgados = favoraveis + desfavoraveis
        
        if total_julgados < 1:  # Mínimo de casos para análise
            continue
        
        taxa_sucesso = (favoraveis / total_julgados * 100) if total_julgados > 0 else 0
        
        ranking_varas.append({
            'vara': vara,
            'comarca': processos_vara['Comarca Desdobramento'].iloc[0] if len(processos_vara) > 0 else '',
            'total_julgados': int(total_julgados),
            'favoraveis': int(favoraveis),
            'desfavoraveis': int(desfavoraveis),
            'taxa_sucesso': round(taxa_sucesso, 2),
            'total_processos': len(processos_vara),
            'valor_total': round(processos_vara['Valor Envolvido Atual - Passiva'].sum(), 2)
        })
    
    # Ordenar por taxa de sucesso
    ranking_varas.sort(key=lambda x: x['taxa_sucesso'], reverse=True)
    
    # Top 10 mais favoráveis e menos favoráveis
    top_favoraveis = ranking_varas[:10]
    top_desfavoraveis = ranking_varas[-10:][::-1]
    
    return jsonify({
        'success': True,
        'total_varas_analisadas': len(ranking_varas),
        'ranking_completo': ranking_varas,
        'top_favoraveis': top_favoraveis,
        'top_desfavoraveis': top_desfavoraveis,
        'estatisticas_gerais': {
            'taxa_sucesso_media': round(sum(v['taxa_sucesso'] for v in ranking_varas) / len(ranking_varas), 2) if ranking_varas else 0,
            'melhor_vara': ranking_varas[0] if ranking_varas else None,
            'pior_vara': ranking_varas[-1] if ranking_varas else None
        }
    })

# ============================================================
# ANALISADOR DE SENTENÇAS COM NLP
# ============================================================

@setorenergia_bp.route('/api/analisar-sentenca', methods=['POST'])
def api_analisar_sentenca():
    """Análise automática de sentença com NLP e extração de jurisprudência"""
    import os
    
    data = request.get_json()
    texto_sentenca = data.get('texto_sentenca', '')
    numero_processo = data.get('numero_processo', '')
    
    if not texto_sentenca:
        return jsonify({
            'success': False,
            'error': 'Texto da sentença é obrigatório'
        }), 400
    
    # Verificar se temos API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API Key não configurada'
        }), 500
    
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        # Prompt para análise de sentença
        prompt = f"""Você é um assistente jurídico especializado em análise de sentenças. Analise a seguinte sentença judicial e extraia as informações mais relevantes:

SENTENÇA:
{texto_sentenca}

Por favor, forneça uma análise estruturada contendo:

1. **Resumo Executivo** (2-3 linhas)
2. **Dispositivo** (qual foi a decisão do juiz?)
3. **Fundamentos Principais** (principais argumentos utilizados)
4. **Jurisprudência Citada** (quais precedentes foram mencionados, se houver)
5. **Teses Jurídicas Aplicadas**
6. **Pontos Favoráveis à CPFL**
7. **Pontos Desfavoráveis à CPFL**
8. **Risco de Recurso** (alto/médio/baixo e justificativa)
9. **Recomendação Estratégica** (recorrer, aceitar, acordo?)
10. **Valores Envolvidos** (se mencionados na sentença)

Seja objetivo e técnico. Use linguagem jurídica adequada."""

        # Chamar API Anthropic
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        analise_completa = message.content[0].text
        
        # Prompt secundário para extração específica de jurisprudência
        prompt_juris = f"""Com base na seguinte sentença, extraia APENAS as referências jurisprudenciais mencionadas (STF, STJ, TJ, etc.):

{texto_sentenca}

Liste cada jurisprudência encontrada no formato:
- [Tribunal] - [Número do acórdão/processo] - [Ementa resumida]

Se não houver jurisprudência citada, responda: "Nenhuma jurisprudência citada."""

        message_juris = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[
                {"role": "user", "content": prompt_juris}
            ]
        )
        
        jurisprudencia_extraida = message_juris.content[0].text
        
        return jsonify({
            'success': True,
            'numero_processo': numero_processo,
            'timestamp': datetime.now().isoformat(),
            'analise': {
                'texto_completo': analise_completa,
                'jurisprudencia_extraida': jurisprudencia_extraida,
                'tokens_utilizados': message.usage.input_tokens + message.usage.output_tokens,
                'modelo': 'claude-3-5-sonnet-20241022'
            },
            'metadados': {
                'tamanho_sentenca': len(texto_sentenca),
                'data_analise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao processar análise: {str(e)}'
        }), 500

@setorenergia_bp.route('/api/extrair-jurisprudencia', methods=['POST'])
def api_extrair_jurisprudencia():
    """Extração rápida de jurisprudência relevante de um texto"""
    import os
    
    data = request.get_json()
    texto = data.get('texto', '')
    tema = data.get('tema', 'Direito do Consumidor - Energia Elétrica')
    
    if not texto:
        return jsonify({
            'success': False,
            'error': 'Texto é obrigatório'
        }), 400
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API Key não configurada'
        }), 500
    
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        prompt = f"""Você é um pesquisador jurídico especializado em {tema}.

Analise o seguinte texto e identifique:

1. **Jurisprudências Citadas** no próprio texto
2. **Jurisprudências Relevantes** que poderiam ser aplicadas ao caso (mesmo que não citadas)
3. **Súmulas Aplicáveis** (STF, STJ, TJs)
4. **Teses Jurídicas** relacionadas

TEXTO PARA ANÁLISE:
{texto}

Forneça uma resposta estruturada e objetiva."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        resultado = message.content[0].text
        
        return jsonify({
            'success': True,
            'tema': tema,
            'timestamp': datetime.now().isoformat(),
            'jurisprudencia': {
                'resultado_completo': resultado,
                'tokens_utilizados': message.usage.input_tokens + message.usage.output_tokens
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao extrair jurisprudência: {str(e)}'
        }), 500

# ============================================================
# AGENTE CPFL - RAG COM QDRANT
# ============================================================

@setorenergia_bp.route('/agente')
def agente():
    """Página do Agente Jurídico CPFL com RAG"""
    try:
        import sys
        from pathlib import Path
        services_path = Path(__file__).parent / 'services'
        if str(services_path) not in sys.path:
            sys.path.insert(0, str(services_path))
        
        from qdrant_service import QdrantService
        qdrant_service = QdrantService()
        stats = qdrant_service.get_collection_stats()
        return render_template('setorenergia/agente.html', qdrant_stats=stats)
    except Exception as e:
        return render_template('setorenergia/agente.html', qdrant_stats={}, error=str(e))

@setorenergia_bp.route('/api/agente/query', methods=['POST'])
def api_agente_query():
    """API para consultas ao agente jurídico com RAG"""
    try:
        import sys
        from pathlib import Path
        services_path = Path(__file__).parent / 'services'
        if str(services_path) not in sys.path:
            sys.path.insert(0, str(services_path))
        
        from cpfl_agent import CPFLAgent
        cpfl_agent = CPFLAgent()
        
        data = request.get_json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        model = data.get('model', 'claude-3-5-sonnet-20241022')
        max_processos = data.get('max_processos', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query é obrigatória'
            }), 400
        
        result = cpfl_agent.process_query(
            query=query,
            filters=filters,
            model=model,
            max_processos=max_processos
        )
        
        return jsonify({
            **result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao processar consulta: {str(e)}'
        }), 500

@setorenergia_bp.route('/api/agente/gerar-peca', methods=['POST'])
def api_agente_gerar_peca():
    """API para geração de peças processuais"""
    try:
        import sys
        from pathlib import Path
        services_path = Path(__file__).parent / 'services'
        if str(services_path) not in sys.path:
            sys.path.insert(0, str(services_path))
        
        from cpfl_agent import CPFLAgent
        cpfl_agent = CPFLAgent()
        
        data = request.get_json()
        tipo_peca = data.get('tipo_peca', 'contestação')
        dados_processo = data.get('dados_processo', {})
        model = data.get('model', 'claude-3-5-sonnet-20241022')
        
        if not dados_processo:
            return jsonify({
                'success': False,
                'error': 'Dados do processo são obrigatórios'
            }), 400
        
        peca = cpfl_agent.generate_peca_processual(
            tipo_peca=tipo_peca,
            dados_processo=dados_processo,
            model=model
        )
        
        return jsonify({
            'success': True,
            'tipo_peca': tipo_peca,
            'peca': peca,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar peça: {str(e)}'
        }), 500

@setorenergia_bp.route('/api/agente/stats')
def api_agente_stats():
    """Estatísticas do banco vetorial Qdrant"""
    try:
        import sys
        from pathlib import Path
        services_path = Path(__file__).parent / 'services'
        if str(services_path) not in sys.path:
            sys.path.insert(0, str(services_path))
        
        from qdrant_service import QdrantService
        qdrant_service = QdrantService()
        stats = qdrant_service.get_collection_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# EXPORTAÇÃO DE RELATÓRIOS EM EXCEL
# ============================================================

@setorenergia_bp.route('/api/export/relatorio-executivo/excel')
def export_relatorio_executivo_excel():
    """Exporta relatório executivo completo em Excel"""
    try:
        processos, stats = load_data()
        df = pd.DataFrame(processos)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: KPIs Principais
            kpis_data = {
                'Métrica': ['Total de Processos', 'Risco Total (R$)', 'Taxa de Sucesso (%)', 'Valor Médio (R$)'],
                'Valor': [
                    len(processos),
                    stats.get('valor_total_risco', 0),
                    39.67,
                    df['Valor Envolvido Atual - Passiva'].mean() if len(df) > 0 else 0
                ]
            }
            pd.DataFrame(kpis_data).to_excel(writer, sheet_name='KPIs', index=False)
            
            # Aba 2: Processos Completos
            df_export = df[[
                'Número do Processo', 'Fase', 'Causa-Raiz', 
                'Comarca Desdobramento', 'Valor Envolvido Atual - Passiva',
                'Decisão (1ª Instância)', 'Resultado final'
            ]].copy()
            df_export.to_excel(writer, sheet_name='Processos', index=False)
            
            # Aba 3: Por Causa-Raiz
            causa_raiz = df.groupby('Causa-Raiz').agg({
                'Número do Processo': 'count',
                'Valor Envolvido Atual - Passiva': 'sum'
            }).reset_index()
            causa_raiz.columns = ['Causa-Raiz', 'Quantidade', 'Risco Total']
            causa_raiz.to_excel(writer, sheet_name='Por Causa-Raiz', index=False)
            
            # Aba 4: Por Comarca
            comarca = df.groupby('Comarca Desdobramento').agg({
                'Número do Processo': 'count',
                'Valor Envolvido Atual - Passiva': 'sum'
            }).reset_index()
            comarca.columns = ['Comarca', 'Quantidade', 'Risco Total']
            comarca.to_excel(writer, sheet_name='Por Comarca', index=False)
        
        output.seek(0)
        filename = f'SetorEnergia_Relatorio_Executivo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@setorenergia_bp.route('/api/export/relatorio-varas/excel')
def export_relatorio_varas_excel():
    """Exporta análise por vara em Excel"""
    try:
        processos, _ = load_data()
        df = pd.DataFrame(processos)
        
        # Agregar por vara
        varas = df.groupby('Vara Desdobramento').agg({
            'Número do Processo': 'count',
            'Valor Envolvido Atual - Passiva': ['sum', 'mean']
        }).reset_index()
        varas.columns = ['Vara', 'Total Processos', 'Risco Total', 'Risco Médio']
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            varas.to_excel(writer, sheet_name='Análise por Vara', index=False)
        
        output.seek(0)
        filename = f'SetorEnergia_Analise_Varas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@setorenergia_bp.route('/api/export/relatorio-financeiro/excel')
def export_relatorio_financeiro_excel():
    """Exporta análise de risco financeiro em Excel"""
    try:
        processos, _ = load_data()
        df = pd.DataFrame(processos)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: Resumo Financeiro
            resumo = {
                'Métrica': ['Risco Total', 'Provisão Recomendada', 'Valor Médio', 'Maior Processo'],
                'Valor (R$)': [
                    df['Valor Envolvido Atual - Passiva'].sum(),
                    df['Valor Envolvido Atual - Passiva'].sum() * 0.6,
                    df['Valor Envolvido Atual - Passiva'].mean(),
                    df['Valor Envolvido Atual - Passiva'].max()
                ]
            }
            pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo Financeiro', index=False)
            
            # Aba 2: Processos de Alto Risco (> R$ 100k)
            alto_risco = df[df['Valor Envolvido Atual - Passiva'] > 100000][[
                'Número do Processo', 'Causa-Raiz', 'Comarca Desdobramento',
                'Valor Envolvido Atual - Passiva', 'Fase'
            ]].copy()
            alto_risco.to_excel(writer, sheet_name='Alto Risco', index=False)
            
            # Aba 3: Distribuição por Faixa de Valor
            df['Faixa'] = pd.cut(
                df['Valor Envolvido Atual - Passiva'],
                bins=[0, 10000, 50000, 100000, 500000, float('inf')],
                labels=['Até 10k', '10k-50k', '50k-100k', '100k-500k', 'Acima 500k']
            )
            faixas = df.groupby('Faixa').agg({
                'Número do Processo': 'count',
                'Valor Envolvido Atual - Passiva': 'sum'
            }).reset_index()
            faixas.columns = ['Faixa de Valor', 'Quantidade', 'Risco Total']
            faixas.to_excel(writer, sheet_name='Por Faixa de Valor', index=False)
        
        output.seek(0)
        filename = f'SetorEnergia_Risco_Financeiro_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@setorenergia_bp.route('/api/export/relatorio-juizes/excel')
def export_relatorio_juizes_excel():
    """Exporta análise de performance de juízes em Excel"""
    try:
        processos, _ = load_data()
        df = pd.DataFrame(processos)
        
        # Agregar por advogado (não há campo Juiz, usar Advogado Responsável)
        juizes = df.groupby('Advogado Responsável').agg({
            'Número do Processo': 'count',
            'Valor Envolvido Atual - Passiva': 'sum'
        }).reset_index()
        juizes.columns = ['Advogado', 'Total Processos', 'Risco Total']
        juizes = juizes.sort_values('Total Processos', ascending=False)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            juizes.to_excel(writer, sheet_name='Performance Advogados', index=False)
        
        output.seek(0)
        filename = f'SetorEnergia_Performance_Advogados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# MÓDULO DE AUDIÊNCIAS
# ============================================================

@setorenergia_bp.route('/api/audiencias')
def api_audiencias():
    """API para retornar dados de audiências"""
    try:
        audiencias_path = Path(__file__).parent / 'data' / 'audiencias.json'
        with open(audiencias_path, 'r', encoding='utf-8') as f:
            audiencias = json.load(f)
        
        # Aplicar filtros se fornecidos
        comarca = request.args.get('comarca')
        orgao = request.args.get('orgao')
        providencia = request.args.get('providencia')
        
        if comarca:
            audiencias = [a for a in audiencias if a['comarca'] == comarca]
        if orgao:
            audiencias = [a for a in audiencias if a['orgao'] == orgao]
        if providencia:
            audiencias = [a for a in audiencias if a['providencia'] == providencia]
        
        return jsonify({
            'success': True,
            'total': len(audiencias),
            'data': audiencias
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@setorenergia_bp.route('/api/export/audiencias/excel')
def export_audiencias_excel():
    """Exporta pauta de audiências em Excel"""
    try:
        audiencias_path = Path(__file__).parent / 'data' / 'audiencias.json'
        with open(audiencias_path, 'r', encoding='utf-8') as f:
            audiencias = json.load(f)
        
        # Converter para DataFrame
        df = pd.DataFrame(audiencias)
        
        # Renomear colunas para português
        df = df.rename(columns={
            'id': 'ID',
            'providencia': 'Providência',
            'data': 'Data',
            'hora': 'Hora',
            'prazo_fatal': 'Prazo Fatal',
            'observacoes': 'Observações',
            'adverso_principal': 'Adverso Principal',
            'numero_processo': 'Número do Processo',
            'estado': 'Estado',
            'comarca': 'Comarca',
            'juizo': 'Juízo',
            'orgao': 'Órgão'
        })
        
        # Reordenar colunas
        colunas_ordem = ['ID', 'Data', 'Hora', 'Providência', 'Número do Processo', 
                         'Adverso Principal', 'Comarca', 'Juízo', 'Órgão', 
                         'Prazo Fatal', 'Observações', 'Estado']
        df = df[colunas_ordem]
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pauta Audiências', index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Pauta Audiências']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        filename = f'SetorEnergia_Pauta_Audiencias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Inicializar dados ao importar o módulo
load_data()
