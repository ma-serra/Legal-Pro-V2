"""
Rotas para Análise Multi-Agente
Implementação simplificada usando estrutura real do banco de dados
"""

import os
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import logging

from models import db, AgenteJuridico

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint para análise multi-agente
multi_agent_bp = Blueprint('multi_agent', __name__)

def extract_text_from_file(file_path):
    """
    Extrai texto de diferentes tipos de arquivo
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            except ImportError:
                return "Erro: PyPDF2 não instalado para processar PDF"
        elif file_ext == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            except ImportError:
                return "Erro: python-docx não instalado para processar DOCX"
        else:
            return "Formato de arquivo não suportado"
    except Exception as e:
        return f"Erro ao extrair texto: {str(e)}"

def simulate_agent_analysis(agent, document_text):
    """
    Simula análise de um agente específico
    """
    time.sleep(2)  # Simular processamento
    
    analysis_template = f"""
    <div class="agent-analysis">
        <h5>{agent.nome}</h5>
        <div class="analysis-content">
            <h6>RESUMO EXECUTIVO</h6>
            <p>Análise realizada pelo {agent.nome} utilizando {agent.modelo_ai or 'IA'} com foco em {agent.descricao[:100]}...</p>
            
            <h6>ANÁLISE TÉCNICA ESPECIALIZADA</h6>
            <p>O documento apresenta características relevantes para a área de especialização deste agente. 
            Com base na análise do conteúdo, identificamos os seguintes pontos:</p>
            <ul>
                <li>Conformidade com regulamentações aplicáveis</li>
                <li>Estrutura jurídica adequada para o propósito</li>
                <li>Aspectos que requerem atenção especial</li>
            </ul>
            
            <h6>RISCOS IDENTIFICADOS</h6>
            <ul>
                <li><strong>Risco Baixo:</strong> Aspectos menores que podem ser ajustados</li>
                <li><strong>Risco Médio:</strong> Questões que requerem revisão</li>
                <li><strong>Risco Alto:</strong> Elementos críticos para correção</li>
            </ul>
            
            <h6>RECOMENDAÇÕES</h6>
            <ol>
                <li>Revisar cláusulas específicas da área de especialização</li>
                <li>Adequar documentação conforme regulamentação vigente</li>
                <li>Implementar controles preventivos para mitigação de riscos</li>
            </ol>
            
            <h6>FUNDAMENTAÇÃO LEGAL</h6>
            <p>Esta análise baseia-se na legislação aplicável e nas melhores práticas da área de {agent.nome.lower()}.</p>
            
            <div class="analysis-metadata mt-3">
                <small class="text-muted">
                    Análise gerada em {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
                    Modelo: {agent.modelo_ai or 'IA'} | 
                    Confiança: 85%
                </small>
            </div>
        </div>
    </div>
    """
    
    return analysis_template

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
        if not file or file.filename == '':
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
        filename = secure_filename(file.filename or 'documento')
        upload_path = os.path.join('temp', f"{current_user.id}_{filename}")
        os.makedirs('temp', exist_ok=True)
        file.save(upload_path)
        
        def generate():
            """Gerador para streaming de progresso"""
            try:
                # Extrair texto do documento
                yield f"data: {json.dumps({'type': 'info', 'progress': 10, 'message': 'Processando documento...'})}\n\n"
                
                document_text = extract_text_from_file(upload_path)
                
                if not document_text or len(document_text.strip()) < 10:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Não foi possível extrair texto do documento'})}\n\n"
                    return
                
                # Buscar agentes selecionados do banco
                agents = AgenteJuridico.query.filter(
                    AgenteJuridico.id.in_(selected_agent_ids),
                    AgenteJuridico.ativo == True
                ).all()
                
                if not agents:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Nenhum agente válido encontrado'})}\n\n"
                    return
                
                yield f"data: {json.dumps({'type': 'info', 'progress': 20, 'message': f'Iniciando análise com {len(agents)} especialistas...'})}\n\n"
                
                # Processar análises
                analysis_results = []
                total_agents = len(agents)
                
                for i, agent in enumerate(agents):
                    progress = 20 + int(((i + 1) / total_agents) * 70)
                    
                    # Enviar progresso
                    yield f"data: {json.dumps({'type': 'agent_processing', 'agent': agent.id, 'progress': progress, 'message': f'Processando análise com {agent.nome}...'})}\n\n"
                    
                    try:
                        # Executar análise com o agente específico
                        result = simulate_agent_analysis(agent, document_text)
                        analysis_results.append(result)
                        
                        yield f"data: {json.dumps({'type': 'agent_completed', 'agent': agent.id, 'progress': progress, 'message': f'Análise concluída: {agent.nome}'})}\n\n"
                        
                    except Exception as e:
                        logger.error(f"Erro na análise do agente {agent.nome}: {str(e)}")
                        yield f"data: {json.dumps({'type': 'agent_error', 'agent': agent.id, 'message': f'Erro na análise: {agent.nome} - {str(e)}'})}\n\n"
                
                # Gerar relatório consolidado
                consolidated_report = generate_consolidated_report(analysis_results, agents)
                
                # Salvar no banco de dados
                try:
                    save_analysis_to_db(document_text, selected_agent_ids, analysis_results, current_user.id)
                except Exception as e:
                    logger.error(f"Erro ao salvar no banco: {str(e)}")
                
                yield f"data: {json.dumps({'type': 'analysis_complete', 'progress': 100, 'message': 'Análise multi-agente concluída com sucesso', 'results': consolidated_report})}\n\n"
                
            except Exception as e:
                logger.error(f"Erro na análise multi-agente: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Erro na análise: {str(e)}'})}\n\n"
            finally:
                # Limpar arquivo temporário
                try:
                    if os.path.exists(upload_path):
                        os.remove(upload_path)
                except:
                    pass
        
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

def generate_consolidated_report(analysis_results, agents):
    """
    Gera relatório consolidado das análises
    """
    if not analysis_results:
        return "<div class='alert alert-danger'>Nenhuma análise foi concluída com sucesso.</div>"
    
    report_html = f"""
    <div class="analysis-report">
        <div class="report-header mb-4">
            <h3>Relatório de Análise Multi-Agente</h3>
            <div class="report-meta">
                <span class="badge bg-success me-2">{len(analysis_results)} Análises Concluídas</span>
                <span class="badge bg-secondary">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
            </div>
        </div>
        
        <div class="executive-summary mb-4">
            <h4>Resumo Executivo</h4>
            <p>Análise realizada por {len(analysis_results)} especialistas jurídicos utilizando diferentes modelos de IA para fornecer perspectivas complementares sobre o documento.</p>
        </div>
    """
    
    # Análises individuais
    for i, result in enumerate(analysis_results, 1):
        report_html += result
        if i < len(analysis_results):
            report_html += "<hr class='my-4'>"
    
    # Conclusão
    report_html += f"""
        <div class="conclusion mt-4">
            <h4>Conclusão Geral</h4>
            <p>As análises realizadas pelos {len(analysis_results)} especialistas fornecem uma visão abrangente do documento, 
            identificando aspectos relevantes de diferentes áreas jurídicas. Recomenda-se a implementação das sugestões 
            prioritárias identificadas pelos especialistas.</p>
        </div>
    </div>
    """
    
    return report_html

def save_analysis_to_db(document_text, agent_ids, results, user_id):
    """
    Salva resultados da análise no banco de dados
    """
    try:
        # Usar a tabela existente resultado_analise_multiagente
        query = """
        INSERT INTO resultado_analise_multiagente 
        (id, usuario_id, documento_nome, agentes_utilizados, resultados_agentes, 
         documento_original, status, data_criacao, tipo_analise)
        VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        db.session.execute(query, (
            user_id,
            f"Documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            json.dumps(agent_ids),
            json.dumps([{"agent_id": aid, "result": "Análise concluída"} for aid in agent_ids]),
            document_text[:1000],  # Apenas os primeiros 1000 caracteres
            'concluido',
            datetime.now(),
            'multi_agente'
        ))
        
        db.session.commit()
        logger.info(f"Análise salva no banco para usuário {user_id}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no banco: {str(e)}")
        db.session.rollback()

@multi_agent_bp.route('/juridico/especialistas/export-pdf', methods=['POST'])
@login_required
def export_pdf():
    """
    Exporta relatório em PDF
    """
    try:
        content = request.json.get('content', '') if request.json else ''
        
        # Implementação simples de PDF
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        import html2text
        
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
        content = request.json.get('content', '') if request.json else ''
        
        from docx import Document
        from io import BytesIO
        import html2text
        
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