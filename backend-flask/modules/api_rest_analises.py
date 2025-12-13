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
        
        # Integrar com MULTI-AGENT ORCHESTRATOR REAL
        try:
            from modules.multi_agent_orchestrator import MultiAgentOrchestrator
            
            orchestrator = MultiAgentOrchestrator()
            
            # Processar com agentes selecionados
            resultado = orchestrator.process_document_with_selected_agents(
                texto=texto,
                area_juridica='empresarial',  # Pode ser passado como parâmetro
                agentes_ids=[str(id) for id in agentes_ids],
                usar_validacao=True  # Usar validação multi-API
            )
            
            if resultado.get('status') == 'success':
                # Formatar resposta consolidada
                analise_consolidada = f"""
# Análise Multi-Agente - {len(agentes_ids)} Especialistas

## Agentes Participantes
{', '.join(resultado.get('agentes_utilizados', {}).get('especialistas', []))}

## Processamento Sequencial
"""
                # Adicionar resultados de processamento
                for agente_nome, result in resultado.get('processamento_agentes', {}).items():
                    analise_consolidada += f"\n### {agente_nome.title()}\n{result.get('resultado', 'N/A')}\n"
                
                analise_consolidada += "\n## Análises dos Especialistas\n"
                
                # Adicionar análises de especialistas
                for esp in resultado.get('especialistas_analises', []):
                    analise_consolidada += f"\n### {esp['agente']} ({esp['area']})\n{esp['analise']}\n"
                
                # Adicionar validações de APIs
                if resultado.get('validacao_apis'):
                    analise_consolidada += "\n## Validação Multi-API\n"
                    for val in resultado['validacao_apis']:
                        analise_consolidada += f"\n### {val['api']}\n**Especialidade:** {val['especialidade']}\n\n{val['validacao']}\n"
                
                analise_consolidada += f"\n## Consolidação Final\n\n{resultado.get('consolidacao_final', '')}\n"
                analise_consolidada += f"\n---\n*Análise gerada em: {resultado['timestamp']}*\n"
                analise_consolidada += f"*Tempo total: {resultado['total_processing_time']}s*"
                
                return jsonify({
                    'analise_consolidada': analise_consolidada,
                    'resultados_individuais': resultado.get('especialistas_analises', []),
                    'total_agentes': resultado['total_agentes'],
                    'metricas': resultado.get('metricas', {}),
                    'timestamp': resultado['timestamp'],
                    'tokens_totais': 0,  # Seria calculado se implementado
                    'tipo': 'multi_agente_real',
                    'status': 'success'
                }), 200
            else:
                # Erro no processamento
                return jsonify({
                    'error': resultado.get('message', 'Erro no processamento'),
                    'status': 'error'
                }), 500
                
        except Exception as e:
            logger.error(f"Erro ao processar multi-agente: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback para resposta mock
            analise_consolidada_fallback = f"""
# Análise Multi-Agente - Modo Fallback

Desculpe, ocorreu um erro ao processar com os agentes especializados.

**Erro:** {str(e)}

Esta funcionalidade requer:
- Agentes configurados no banco de dados
- APIs de IA ativas (OpenAI, Anthropic, etc.)
- Conexão com banco de dados

Por favor, verifique as configurações e tente novamente.
"""
            
            return jsonify({
                'analise_consolidada': analise_consolidada_fallback,
                'error': str(e),
                'tipo': 'fallback',
                'status': 'partial_error'
            }), 200
        
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
