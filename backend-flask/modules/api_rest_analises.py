"""
API REST para Análises - Análise de documentos jurídicos com IA
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from main import db
from models import AnaliseDocumento, Documento, AgenteJuridico, VersaoDocumento, User
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

analises_api = Blueprint('analises_api', __name__, url_prefix='/api/analises')

# Tipos de análise disponíveis
TIPOS_ANALISE = ['estrategica', 'tecnica', 'estatistica', 'preditiva']

@analises_api.route('', methods=['POST'])
def criar_analise():
    """
    Cria uma nova análise de documento
    Body: { "texto": "...", "tipo": "estrategica|tecnica|estatistica|preditiva", "agente_id": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('texto'):
            return jsonify({'error': 'Texto é obrigatório'}), 400
        
        texto = data['texto']
        tipo = data.get('tipo', 'tecnica')
        agente_id = data.get('agente_id')
        
        if tipo not in TIPOS_ANALISE:
            return jsonify({'error': f'Tipo deve ser um de: {", ".join(TIPOS_ANALISE)}'}), 400
        
        # Por enquanto retornar análise mockada
        # TODO: Integrar com módulos de análise reais
        resultado_mock = f"""
# Análise {tipo.capitalize()} - Documento Jurídico

## Resumo Executivo
Este documento foi analisado utilizando técnicas avançadas de processamento de linguagem natural e inteligência artificial jurídica.

## Pontos Principais Identificados

### 1. Análise do Contexto Jurídico
O texto apresentado contém elementos característicos de {tipo} jurídica, com foco em:
- Identificação de elementos relevantes
- Avaliação de riscos e oportunidades
- Sugestões de estratégias

### 2. Recomendações
Com base na análise realizada, as seguintes recomendações são sugeridas:
- Revisar cláusulas específicas
- Consultar precedentes similares
- Avaliar recursos disponíveis

### 3. Próximos Passos
- Documentar achados principais
- Preparar relatório executivo
- Agendar reunião com equipe jurídica

---
*Análise gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}*  
*Tipo: {tipo}*  
*Modelo: GPT-4o (OpenAI)*
"""
        
        # Se um agente foi especificado, buscar informações
        agente_nome = "Sistema"
        if agente_id:
            agente = AgenteJuridico.query.filter_by(id=agente_id, ativo=True).first()
            if agente:
                agente_nome = agente.nome
        
        response_data = {
            'id': None,  # Seria o ID no banco
            'tipo': tipo,
            'resultado': resultado_mock,
            'score': 0.85,
            'timestamp': datetime.now().isoformat(),
            'agente': agente_nome,
            'tokens_usados': len(texto.split()) * 2  # Aproximação
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar análise: {e}")
        return jsonify({'error': 'Erro ao criar análise'}), 500

@analises_api.route('', methods=['GET'])
def listar_analises():
    """
    Lista análises realizadas
    Query params: limit, tipo
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        tipo = request.args.get('tipo', '')
        
        # Query base
        query = AnaliseDocumento.query
        
        # Filtrar por tipo se fornecido
        # TODO: Adicionar campo tipo em AnaliseDocumento model
        
        # Ordenar por data mais recente
        query = query.order_by(desc(AnaliseDocumento.data_analise))
        
        # Limitar resultados
        analises = query.limit(limit).all()
        
        # Serializar
        result = []
        for analise in analises:
            result.append({
                'id': analise.id,
                'documento_id': analise.documento_id,
                'agente_id': analise.agente_id,
                'agente_nome': analise.agente.nome if analise.agente else 'Desconhecido',
                'data_analise': analise.data_analise.isoformat() if analise.data_analise else None,
                'preview': analise.conteudo_analise[:200] + '...' if len(analise.conteudo_analise) > 200 else analise.conteudo_analise
            })
        
        return jsonify({'analises': result}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar análises: {e}")
        return jsonify({'error': 'Erro ao listar análises'}), 500

@analises_api.route('/<int:analise_id>', methods=['GET'])
def obter_analise(analise_id):
    """
    Retorna detalhes completos de uma análise
    """
    try:
        analise = AnaliseDocumento.query.get_or_404(analise_id)
        
        return jsonify({
            'id': analise.id,
            'documento_id': analise.documento_id,
            'versao_id': analise.versao_id,
            'agente_id': analise.agente_id,
            'agente_nome': analise.agente.nome if analise.agente else 'Desconhecido',
            'conteudo_analise': analise.conteudo_analise,
            'conteudo_analise_html': analise.conteudo_analise_html,
            'data_analise': analise.data_analise.isoformat() if analise.data_analise else None,
            'metadados': analise.metadados
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter análise {analise_id}: {e}")
        return jsonify({'error': 'Análise não encontrada'}), 404

@analises_api.route('/multi-agente', methods=['POST'])
def analise_multi_agente():
    """
    Realiza análise com múltiplos agentes
    Body: { "texto": "...", "agentes_ids": [1, 2, 3] }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('texto'):
            return jsonify({'error': 'Texto é obrigatório'}), 400
        
        texto = data['texto']
        agentes_ids = data.get('agentes_ids', [])
        
        if not agentes_ids or len(agentes_ids) == 0:
            return jsonify({'error': 'Ao menos um agente deve ser especificado'}), 400
        
        # Buscar agentes
        agentes = AgenteJuridico.query.filter(
            AgenteJuridico.id.in_(agentes_ids),
            AgenteJuridico.ativo == True
        ).all()
        
        if len(agentes) == 0:
            return jsonify({'error': 'Nenhum agente válido encontrado'}), 404
        
        # Mock: simular análise de cada agente
        resultados_agentes = []
        for agente in agentes:
            resultados_agentes.append({
                'agente_id': agente.id,
                'agente_nome': agente.nome,
                'categoria': agente.categoria.nome if agente.categoria else 'Geral',
                'analise': f"Análise realizada por {agente.nome}: O documento apresenta características específicas da área de {agente.categoria.nome if agente.categoria else 'Direito'}. Recomenda-se atenção especial aos pontos destacados.",
                'score_confianca': 0.88,
                'tokens_usados': 200
            })
        
        # Gerar análise consolidada
        analise_consolidada = f"""
# Análise Multi-Agente - {len(agentes)} Especialistas

## Agentes Participantes
{', '.join([a.nome for a in agentes])}

## Análise Consolidada
Este documento foi analisado por {len(agentes)} agentes especializados, cada um trazendo sua perspectiva única.

## Consensos Identificados
- Todos os agentes concordam quanto à relevância jurídica do documento
- Elementos principais foram identificados de forma consistente
- Recomendações convergem para uma estratégia unificada

## Divergências
- Pequenas variações na interpretação de cláusulas específicas
- Diferentes níveis de risco atribuídos a determinados aspectos

## Recomendação Final
Com base na análise combinada, recomenda-se proceder com cautela, considerando todos os pontos levantados pelos especialistas.

---
*Análise multi-agente gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}*
"""
        
        response_data = {
            'analise_consolidada': analise_consolidada,
            'resultados_individuais': resultados_agentes,
            'total_agentes': len(agentes),
            'timestamp': datetime.now().isoformat(),
            'tokens_totais': sum(r['tokens_usados'] for r in resultados_agentes)
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Erro ao realizar análise multi-agente: {e}")
        return jsonify({'error': 'Erro ao realizar análise multi-agente'}), 500

@analises_api.route('/tipos', methods=['GET'])
def listar_tipos():
    """
    Lista tipos de análise disponíveis
    """
    tipos_detalhados = [
        {
            'id': 'estrategica',
            'nome': 'Análise Estratégica',
            'descricao': 'Avalia aspectos estratégicos do caso, identificando pontos fortes e fracos.'
        },
        {
            'id': 'tecnica',
            'nome': 'Análise Técnica',
            'descricao': 'Examina aspectos técnicos e jurídicos do documento ou processo.'
        },
        {
            'id': 'estatistica',
            'nome': 'Análise Estatística',
            'descricao': 'Compara com casos similares e apresenta estatísticas de sucesso.'
        },
        {
            'id': 'preditiva',
            'nome': 'Análise Preditiva',
            'descricao': 'Utiliza IA para prever resultados e tendências do caso.'
        }
    ]
    
    return jsonify({'tipos': tipos_detalhados}), 200

def register_analises_api(app):
    """Registra o blueprint de análises no app"""
    app.register_blueprint(analises_api)
    print("✅ API REST de Análises registrada")
    logger.info("✅ API REST de Análises registrada com sucesso")
