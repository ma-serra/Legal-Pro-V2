"""
Sistema de Análise Multi-Agente para Documentos Jurídicos
Utiliza agentes reais do banco de dados e múltiplos provedores de IA
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from flask import Blueprint, request, jsonify, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import logging

from models import db, AgenteJuridico, ResultadoAnaliseMultiAgente
from document_processor import DocumentProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para análise multi-agente
multi_agent_bp = Blueprint('multi_agent', __name__)

class MultiAgentAnalysisSystem:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        
    def process_document_analysis(self, document_path: str, selected_agent_ids: List[int], user_id: int):
        """
        Processa análise multi-agente de documento
        """
        try:
            # Extrair texto do documento
            document_text = await self.document_processor.extract_text(document_path)
            
            # Buscar agentes selecionados do banco
            agents = AgenteJuridico.query.filter(
                AgenteJuridico.id.in_(selected_agent_ids),
                AgenteJuridico.ativo == True
            ).all()
            
            if not agents:
                raise ValueError("Nenhum agente válido encontrado")
            
            # Processar análises em paralelo
            analysis_results = []
            total_agents = len(agents)
            
            for i, agent in enumerate(agents):
                progress = int(((i + 1) / total_agents) * 100)
                
                # Enviar progresso
                yield {
                    'type': 'agent_processing',
                    'agent': agent.id,
                    'progress': progress,
                    'message': f'Processando análise com {agent.nome}...'
                }
                
                try:
                    # Executar análise com o agente específico
                    result = await self._execute_agent_analysis(agent, document_text)
                    analysis_results.append({
                        'agent_id': agent.id,
                        'agent_name': agent.nome,
                        'model': agent.modelo_ai,
                        'result': result,
                        'status': 'completed'
                    })
                    
                    yield {
                        'type': 'agent_completed',
                        'agent': agent.id,
                        'progress': progress,
                        'message': f'Análise concluída: {agent.nome}'
                    }
                    
                except Exception as e:
                    logger.error(f"Erro na análise do agente {agent.nome}: {str(e)}")
                    analysis_results.append({
                        'agent_id': agent.id,
                        'agent_name': agent.nome,
                        'model': agent.modelo_ai,
                        'result': None,
                        'status': 'error',
                        'error': str(e)
                    })
                    
                    yield {
                        'type': 'agent_error',
                        'agent': agent.id,
                        'message': f'Erro na análise: {agent.nome} - {str(e)}'
                    }
            
            # Salvar resultados no banco
            resultado_id = await self._save_analysis_results(
                document_path, selected_agent_ids, analysis_results, user_id
            )
            
            # Gerar relatório consolidado
            consolidated_report = await self._generate_consolidated_report(analysis_results)
            
            yield {
                'type': 'analysis_complete',
                'progress': 100,
                'message': 'Análise multi-agente concluída com sucesso',
                'results': consolidated_report,
                'resultado_id': resultado_id
            }
            
        except Exception as e:
            logger.error(f"Erro na análise multi-agente: {str(e)}")
            yield {
                'type': 'error',
                'message': f'Erro na análise: {str(e)}'
            }
    
    async def _execute_agent_analysis(self, agent: AgenteJuridico, document_text: str) -> Dict[str, Any]:
        """
        Executa análise com um agente específico
        """
        # Construir prompt especializado baseado no agente
        system_prompt = f"""
        Você é um {agent.nome} especializado em análise jurídica.
        
        Descrição: {agent.descricao}
        
        Capacidades: {agent.detalhes_tecnicos}
        
        Analise o documento fornecido seguindo esta estrutura:
        
        1. **RESUMO EXECUTIVO**
        - Síntese dos pontos principais do documento
        
        2. **ANÁLISE TÉCNICA ESPECIALIZADA**
        - Análise detalhada conforme sua especialização
        - Identificação de questões relevantes à sua área
        
        3. **RISCOS IDENTIFICADOS**
        - Riscos jurídicos específicos da sua área
        - Classificação por grau de severidade
        
        4. **RECOMENDAÇÕES**
        - Ações específicas recomendadas
        - Priorização por urgência
        
        5. **FUNDAMENTAÇÃO LEGAL**
        - Base legal aplicável
        - Jurisprudência relevante
        
        Seja preciso, técnico e fundamentado em sua resposta.
        """
        
        user_prompt = f"Documento para análise:\n\n{document_text}"
        
        # Determinar provedor de IA baseado no modelo do agente
        provider = self._get_provider_for_model(agent.modelo_ai)
        
        # Executar análise
        response = await self.api_handler.process_request(
            provider=provider,
            model=agent.modelo_ai or 'gpt-4o',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=agent.temperatura or 0.7,
            max_tokens=agent.max_tokens or 2000
        )
        
        return {
            'analysis': response.get('content', ''),
            'provider': provider,
            'model': agent.modelo_ai,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_provider_for_model(self, model: str) -> str:
        """
        Determina o provedor baseado no modelo
        """
        if not model:
            return 'openai'
            
        model_lower = model.lower()
        if 'gpt' in model_lower or 'openai' in model_lower:
            return 'openai'
        elif 'claude' in model_lower or 'anthropic' in model_lower:
            return 'anthropic'
        elif 'gemini' in model_lower or 'google' in model_lower:
            return 'google'
        elif 'deepseek' in model_lower:
            return 'deepseek'
        else:
            return 'openai'  # Fallback padrão
    
    async def _save_analysis_results(self, document_path: str, agent_ids: List[int], 
                                   results: List[Dict], user_id: int) -> int:
        """
        Salva resultados da análise no banco de dados
        """
        try:
            resultado = ResultadoAnaliseMultiAgente(
                user_id=user_id,
                documento_nome=os.path.basename(document_path),
                agentes_utilizados=json.dumps(agent_ids),
                resultados_analise=json.dumps(results),
                status='concluido',
                data_criacao=datetime.now()
            )
            
            db.session.add(resultado)
            db.session.commit()
            
            return resultado.id
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
            db.session.rollback()
            raise
    
    async def _generate_consolidated_report(self, analysis_results: List[Dict]) -> str:
        """
        Gera relatório consolidado das análises
        """
        successful_analyses = [r for r in analysis_results if r['status'] == 'completed']
        
        if not successful_analyses:
            return "<div class='alert alert-danger'>Nenhuma análise foi concluída com sucesso.</div>"
        
        report_html = f"""
        <div class="analysis-report">
            <div class="report-header mb-4">
                <h3>Relatório de Análise Multi-Agente</h3>
                <div class="report-meta">
                    <span class="badge bg-success me-2">{len(successful_analyses)} Análises Concluídas</span>
                    <span class="badge bg-secondary">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
                </div>
            </div>
        """
        
        # Análises individuais
        for i, result in enumerate(successful_analyses, 1):
            report_html += f"""
            <div class="agent-analysis mb-4">
                <div class="analysis-header">
                    <h4>
                        <i class="fas fa-user-tie me-2"></i>
                        {result['agent_name']}
                    </h4>
                    <small class="text-muted">Modelo: {result['model']} | Provedor: {result['result'].get('provider', 'N/A')}</small>
                </div>
                <div class="analysis-content mt-3">
                    <div class="formatted-analysis">
                        {self._format_analysis_content(result['result']['analysis'])}
                    </div>
                </div>
            </div>
            """
            
            if i < len(successful_analyses):
                report_html += "<hr class='my-4'>"
        
        report_html += "</div>"
        
        return report_html
    
    def _format_analysis_content(self, content: str) -> str:
        """
        Formata o conteúdo da análise para HTML
        """
        # Substituir quebras de linha por <br>
        formatted = content.replace('\n', '<br>')
        
        # Destacar seções em negrito
        sections = ['RESUMO EXECUTIVO', 'ANÁLISE TÉCNICA', 'RISCOS IDENTIFICADOS', 
                   'RECOMENDAÇÕES', 'FUNDAMENTAÇÃO LEGAL']
        
        for section in sections:
            formatted = formatted.replace(
                f'**{section}**', 
                f'<h6 class="text-primary mt-3 mb-2"><strong>{section}</strong></h6>'
            )
        
        return formatted

# Instância global do sistema
analysis_system = MultiAgentAnalysisSystem()

@multi_agent_bp.route('/juridico/especialistas/analise-multi-agente', methods=['POST'])
@login_required
def analise_multi_agente():
    """
    Endpoint para processar análise multi-agente
    """
    try:
        # Validar arquivo
        if 'document' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Validar agentes selecionados
        agents_json = request.form.get('agents')
        if not agents_json:
            return jsonify({'error': 'Nenhum agente selecionado'}), 400
        
        try:
            selected_agent_ids = json.loads(agents_json)
            selected_agent_ids = [int(id) for id in selected_agent_ids]
        except (json.JSONDecodeError, ValueError):
            return jsonify({'error': 'IDs de agentes inválidos'}), 400
        
        if len(selected_agent_ids) == 0 or len(selected_agent_ids) > 4:
            return jsonify({'error': 'Selecione de 1 a 4 agentes'}), 400
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        upload_path = os.path.join('temp', f"{current_user.id}_{filename}")
        os.makedirs('temp', exist_ok=True)
        file.save(upload_path)
        
        def generate():
            """Gerador para streaming de progresso"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async_gen = analysis_system.process_document_analysis(
                    upload_path, selected_agent_ids, current_user.id
                )
                
                async def run_analysis():
                    async for update in async_gen:
                        yield f"data: {json.dumps(update)}\n\n"
                
                for chunk in loop.run_until_complete(run_analysis()):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"Erro no streaming: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            finally:
                # Limpar arquivo temporário
                try:
                    if os.path.exists(upload_path):
                        os.remove(upload_path)
                except:
                    pass
                loop.close()
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Erro na análise multi-agente: {str(e)}")
        return jsonify({'error': str(e)}), 500

@multi_agent_bp.route('/juridico/especialistas/export-pdf', methods=['POST'])
@login_required
def export_pdf():
    """
    Exporta relatório em PDF
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from io import BytesIO
        import html2text
        
        content = request.json.get('content', '')
        
        # Converter HTML para texto
        h = html2text.HTML2Text()
        h.ignore_links = True
        text_content = h.handle(content)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Relatório de Análise Multi-Agente", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Conteúdo
        for line in text_content.split('\n'):
            if line.strip():
                para = Paragraph(line, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 6))
        
        doc.build(story)
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': 'attachment; filename=analise_multi_agente.pdf'}
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@multi_agent_bp.route('/juridico/especialistas/export-word', methods=['POST'])
@login_required
def export_word():
    """
    Exporta relatório em Word
    """
    try:
        from docx import Document
        from io import BytesIO
        import html2text
        
        content = request.json.get('content', '')
        
        # Converter HTML para texto
        h = html2text.HTML2Text()
        h.ignore_links = True
        text_content = h.handle(content)
        
        # Criar documento Word
        doc = Document()
        doc.add_heading('Relatório de Análise Multi-Agente', 0)
        
        for line in text_content.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
        
        # Salvar em buffer
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={'Content-Disposition': 'attachment; filename=analise_multi_agente.docx'}
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar Word: {str(e)}")
        return jsonify({'error': str(e)}), 500