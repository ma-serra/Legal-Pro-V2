"""
API para Seleção Inteligente de Agentes com Alta Confiança
Implementa endpoint para seleção otimizada com >90% de confiança
"""

import logging
import time
from flask import request, jsonify
from sistema_confianca_alta import SistemaConfiancaAlta
# Imports movidos para dentro das funções para evitar circular import

logger = logging.getLogger(__name__)

def registrar_api_selecao_inteligente(app):
    """Registra a API de Seleção Inteligente de Agentes"""
    
    @app.route('/api/selecao-inteligente-agentes', methods=['POST'])
    def selecao_inteligente_agentes():
        """
        API para seleção inteligente de agentes com alta confiança
        Garante >90% de confiança na seleção
        """
        try:
            logger.info("🎯 Iniciando seleção inteligente de agentes com alta confiança")
            
            # Extrair dados da requisição
            data = request.get_json()
            if not data:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Dados JSON obrigatórios'
                }), 400
            
            texto_documento = data.get('texto', '').strip()
            numero_agentes = data.get('numero_agentes', 3)
            
            if len(texto_documento) < 10:
                return jsonify({
                    'status': 'erro', 
                    'mensagem': 'Texto muito curto para análise (mínimo 10 caracteres)'
                }), 400
            
            if numero_agentes < 1 or numero_agentes > 10:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Número de agentes deve estar entre 1 e 10'
                }), 400
            
            logger.info(f"📄 Processando documento: {len(texto_documento)} caracteres")
            logger.info(f"🎯 Selecionando {numero_agentes} agentes")
            
            tempo_inicio = time.time()
            
            # Imports locais para evitar circular import
            from models import AgenteJuridico
            from main import db
            
            # Buscar agentes disponíveis no banco de dados
            agentes_disponiveis = db.session.query(AgenteJuridico).filter(
                AgenteJuridico.ativo == True
            ).all()
            
            if not agentes_disponiveis:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Nenhum agente disponível no sistema'
                }), 500
            
            # Converter agentes para formato compatível
            agentes_dados = []
            for agente in agentes_disponiveis:
                agente_dict = {
                    'id': agente.id,
                    'nome': agente.nome,
                    'especialidade': agente.especialidade or agente.categoria or 'Geral',
                    'capacidades': agente.capacidades if isinstance(agente.capacidades, list) else [],
                    'nivel_experiencia': agente.nivel_experiencia or 'pleno',
                    'categoria': agente.categoria or 'Geral',
                    'area_juridica_id': agente.area_juridica_id,
                    'prompt_personalizado': agente.prompt_personalizado
                }
                agentes_dados.append(agente_dict)
            
            logger.info(f"📋 {len(agentes_dados)} agentes disponíveis para seleção")
            
            # Inicializar sistema de alta confiança
            sistema = SistemaConfiancaAlta()
            
            # Processar com alta confiança
            resultado = sistema.processar_com_alta_confianca(
                texto_documento, agentes_dados
            )
            
            tempo_total = time.time() - tempo_inicio
            
            # Preparar resposta detalhada
            agentes_selecionados = []
            for agente_score in resultado.agentes_selecionados:
                agente_info = {
                    'id': agente_score.id,
                    'nome': agente_score.nome,
                    'especialidade': agente_score.especialidade,
                    'score_final': round(agente_score.score_final, 2),
                    'confianca_percentual': round(agente_score.confianca_percentual, 1),
                    'razao_selecao': agente_score.razao_selecao,
                    'scores_detalhados': {
                        'especialidade': round(agente_score.score_principal, 2),
                        'contexto': round(agente_score.score_contexto, 2),
                        'experiencia': round(agente_score.score_experiencia, 2),
                        'capacidades': round(agente_score.score_capacidades, 2)
                    }
                }
                agentes_selecionados.append(agente_info)
            
            resposta = {
                'status': 'sucesso',
                'confianca_sistema': {
                    'confianca_final': round(resultado.confianca_final * 100, 1),
                    'nivel_certeza': resultado.nivel_certeza,
                    'meta_90_porcento': resultado.confianca_final >= 0.90
                },
                'agentes_selecionados': agentes_selecionados,
                'analise_documento': {
                    'justificativa_selecao': resultado.justificativa_selecao,
                    'metricas_qualidade': resultado.metrica_qualidade,
                    'recomendacoes_melhoria': resultado.recomendacoes_melhoria
                },
                'estatisticas': {
                    'total_agentes_avaliados': len(agentes_dados),
                    'agentes_selecionados': len(resultado.agentes_selecionados),
                    'tempo_processamento_segundos': round(tempo_total, 2),
                    'tamanho_documento_caracteres': len(texto_documento)
                },
                'meta': {
                    'timestamp': int(time.time()),
                    'versao_algoritmo': '2.0',
                    'sistema': 'confianca_alta'
                }
            }
            
            logger.info(f"🎉 Seleção concluída: {resultado.confianca_final:.1%} confiança, {len(resultado.agentes_selecionados)} agentes, {tempo_total:.2f}s")
            
            return jsonify(resposta)
            
        except Exception as e:
            logger.error(f"❌ Erro na seleção inteligente: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'erro',
                'mensagem': f'Erro interno: {str(e)}'
            }), 500
    
    @app.route('/api/validar-confianca-agentes', methods=['POST'])
    def validar_confianca_agentes():
        """
        API para validar se a seleção atual atende aos critérios de alta confiança
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'erro', 'mensagem': 'Dados obrigatórios'}), 400
            
            agentes_ids = data.get('agentes_ids', [])
            texto_documento = data.get('texto', '')
            
            if not agentes_ids or not texto_documento:
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'agentes_ids e texto são obrigatórios'
                }), 400
            
            # Imports locais para evitar circular import
            from models import AgenteJuridico
            from main import db
            
            # Buscar agentes selecionados
            agentes = db.session.query(AgenteJuridico).filter(
                AgenteJuridico.id.in_(agentes_ids)
            ).all()
            
            if len(agentes) != len(agentes_ids):
                return jsonify({
                    'status': 'erro',
                    'mensagem': 'Um ou mais agentes não foram encontrados'
                }), 404
            
            # Usar sistema para validar
            sistema = SistemaConfiancaAlta()
            analise_doc = sistema._analise_documento_aprofundada(texto_documento)
            
            # Simular AgentScore para validação
            from algoritmo_selecao_inteligente_v2 import AgentScore
            scores_agentes = []
            for agente in agentes:
                agente_dict = {
                    'id': agente.id,
                    'nome': agente.nome,
                    'especialidade': agente.especialidade or 'Geral',
                    'capacidades': agente.capacidades or [],
                    'nivel_experiencia': agente.nivel_experiencia or 'pleno'
                }
                score = sistema.algoritmo._calcular_score_agente(agente_dict, analise_doc.get('area_detectada', 'geral'), analise_doc)
                scores_agentes.append(score)
            
            # Validar seleção
            resultado_validacao = sistema._validar_e_calcular_confianca(scores_agentes, analise_doc, texto_documento)
            
            resposta = {
                'status': 'sucesso',
                'validacao': {
                    'confianca_atual': round(resultado_validacao.confianca_final * 100, 1),
                    'atende_meta_90': resultado_validacao.confianca_final >= 0.90,
                    'nivel_certeza': resultado_validacao.nivel_certeza,
                    'justificativa': resultado_validacao.justificativa_selecao
                },
                'metricas': resultado_validacao.metrica_qualidade,
                'recomendacoes': resultado_validacao.recomendacoes_melhoria,
                'agentes_validados': [
                    {
                        'id': score.id,
                        'nome': score.nome,
                        'score_final': round(score.score_final, 2),
                        'confianca': round(score.confianca_percentual, 1)
                    }
                    for score in scores_agentes
                ]
            }
            
            return jsonify(resposta)
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return jsonify({
                'status': 'erro',
                'mensagem': f'Erro interno: {str(e)}'
            }), 500
    
    logger.info("✅ API de Seleção Inteligente registrada com sucesso")
    return True