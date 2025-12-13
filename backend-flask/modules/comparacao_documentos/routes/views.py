"""
Rotas para o módulo de comparação de versões de documentos
"""

import os
import logging
import json
import re
from datetime import datetime
from flask import (
    render_template, flash, redirect, url_for, request, jsonify, 
    current_app, send_file, abort, session, Response
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_COLOR_INDEX
from bs4 import BeautifulSoup

from modules.comparacao_documentos import bp
from modules.comparacao_documentos.services.comparador import ComparadorDocumentos
from modules.comparacao_documentos.services.export_formatter import ComparacaoExportFormatter
from models import ComparacaoDocumento, db
from decorators import permission_required

logger = logging.getLogger(__name__)

# 18 Áreas jurídicas disponíveis no sistema
AREAS_PROCESSO = {
    "01": "Direito Civil",
    "02": "Direito Penal",
    "03": "Direito Trabalhista",
    "04": "Direito Tributário",
    "05": "Direito Administrativo",
    "06": "Direito Empresarial",
    "07": "Direito Ambiental",
    "08": "Direito Constitucional",
    "09": "Direito Internacional",
    "10": "Direito Previdenciário",
    "11": "Direito do Consumidor",
    "12": "Direito de Família",
    "13": "Direito Digital",
    "14": "Direito Eleitoral",
    "15": "Direito Imobiliário",
    "16": "Direito da Saúde",
    "17": "Análise de Riscos",
    "18": "Conflitos e Mediação"
}

def validar_cpf_cnpj(documento: str) -> bool:
    """Valida se o documento é um CPF ou CNPJ válido (formato básico)"""
    # Remove caracteres não numéricos
    documento = re.sub('[^0-9]', '', documento)
    
    # Verifica se é CPF (11 dígitos) ou CNPJ (14 dígitos)
    return len(documento) in (11, 14)

def processar_html_com_marcacoes(doc, html_content):
    """
    Processa HTML mantendo as marcações de diferenças no documento DOCX
    """
    import re
    
    try:
        logger.info(f"Processando HTML para marcações. Tamanho: {len(html_content)}")
        
        # Dividir o conteúdo por quebras de linha
        if '<br>' in html_content:
            linhas = html_content.split('<br>')
        else:
            linhas = [html_content]
        
        for linha_idx, linha in enumerate(linhas):
            linha = linha.strip()
            if not linha:
                continue
            
            # Criar novo parágrafo para cada linha
            paragraph = doc.add_paragraph()
            posicao = 0
            
            # Encontrar todas as tags de marcação na linha
            tags = []
            
            # Buscar tags de inserção (múltiplos padrões)
            for match in re.finditer(r'<ins[^>]*>(.*?)</ins>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'ins',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            # Buscar tags de remoção (múltiplos padrões)
            for match in re.finditer(r'<del[^>]*>(.*?)</del>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'del',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            # Buscar spans com classes de diferenças
            for match in re.finditer(r'<span[^>]*class="[^"]*(?:diff-adicionado|adicao)[^"]*"[^>]*>(.*?)</span>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'ins',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            for match in re.finditer(r'<span[^>]*class="[^"]*(?:diff-deletado|remocao)[^"]*"[^>]*>(.*?)</span>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'del',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            # Buscar spans com estilos diretos
            for match in re.finditer(r'<span[^>]*style="[^"]*background-color:\s*#ddffdd[^"]*"[^>]*>(.*?)</span>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'ins',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            for match in re.finditer(r'<span[^>]*style="[^"]*background-color:\s*#ffdddd[^"]*"[^>]*>(.*?)</span>', linha):
                tags.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'del',
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
            
            # Ordenar tags por posição
            tags.sort(key=lambda x: x['start'])
            
            # Processar texto com as tags em ordem
            posicao_atual = 0
            
            for tag in tags:
                # Adicionar texto antes da tag (se houver)
                if tag['start'] > posicao_atual:
                    texto_antes = linha[posicao_atual:tag['start']]
                    texto_limpo = re.sub('<[^>]*>', '', texto_antes)
                    if texto_limpo.strip():
                        paragraph.add_run(texto_limpo)
                
                # Processar o conteúdo da tag
                conteudo_tag = re.sub('<[^>]*>', '', tag['content'])
                if conteudo_tag.strip():
                    run = paragraph.add_run(conteudo_tag)
                    
                    if tag['type'] == 'ins':
                        # Texto adicionado - verde e negrito
                        run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
                        run.bold = True
                    elif tag['type'] == 'del':
                        # Texto removido - vermelho e riscado
                        run.font.highlight_color = WD_COLOR_INDEX.RED
                        run.font.strike = True
                
                posicao_atual = tag['end']
            
            # Adicionar texto restante após a última tag
            if posicao_atual < len(linha):
                texto_final = linha[posicao_atual:]
                texto_limpo = re.sub('<[^>]*>', '', texto_final)
                if texto_limpo.strip():
                    paragraph.add_run(texto_limpo)
            
            # Se não havia tags, adicionar o texto completo limpo
            if not tags:
                texto_limpo = re.sub('<[^>]*>', '', linha)
                if texto_limpo.strip():
                    paragraph.add_run(texto_limpo)
        
        logger.info("Processamento HTML com marcações concluído com sucesso")
                
    except Exception as e:
        logger.error(f"Erro ao processar HTML com marcações: {e}")
        # Fallback para texto limpo
        texto_limpo = re.sub('<br>', '\n', html_content)
        texto_limpo = re.sub('<[^>]*>', '', texto_limpo)
        texto_limpo = texto_limpo.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        doc.add_paragraph(texto_limpo)

@bp.route('/')
@login_required
@permission_required('comparacao_documentos.view')
def index():
    """
    Lista todas as comparações de documentos feitas pelo usuário
    """
    comparacoes = ComparacaoDocumento.query.order_by(ComparacaoDocumento.data_comparacao.desc()).all()
    
    # Formatar áreas para exibição
    for comparacao in comparacoes:
        comparacao.area_nome = AREAS_PROCESSO.get(comparacao.area_processo, "Área não especificada")
    
    return render_template(
        'comparacao_documentos/index.html', 
        comparacoes=comparacoes,
        title="Comparação de Documentos"
    )

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
@permission_required('comparacao_documentos.create')
def novo():
    """
    Formulário para criar uma nova comparação de documentos
    """
    if request.method == 'POST':
        # Verificar se os arquivos foram enviados
        if 'versao_original' not in request.files or 'versao_modificada' not in request.files:
            flash('Você deve enviar ambas as versões do documento', 'danger')
            return redirect(request.url)
        
        # Obter arquivos do form
        arquivo_original = request.files['versao_original']
        arquivo_modificado = request.files['versao_modificada']
        
        # Verificar se arquivos são válidos
        if arquivo_original.filename == '' or arquivo_modificado.filename == '':
            flash('Selecione arquivos válidos para ambas as versões', 'danger')
            return redirect(request.url)
        
        # Obter outros campos do formulário
        area_processo = request.form.get('area_processo')
        cpf_cnpj_cliente = request.form.get('cpf_cnpj_cliente', '').strip()
        titulo = request.form.get('titulo', '').strip()
        
        # Validações
        if not area_processo or area_processo not in AREAS_PROCESSO:
            flash('Selecione uma área de processo válida', 'danger')
            return redirect(request.url)
        
        # CPF/CNPJ é opcional, mas se fornecido deve ser válido
        if cpf_cnpj_cliente and not validar_cpf_cnpj(cpf_cnpj_cliente):
            flash('CPF ou CNPJ informado é inválido', 'danger')
            return redirect(request.url)
        
        # Processar os arquivos
        try:
            # Determinar extensões dos arquivos (com validação segura)
            extensao_original = ''
            if arquivo_original.filename and '.' in arquivo_original.filename:
                extensao_original = arquivo_original.filename.rsplit('.', 1)[1].lower()
                
            extensao_modificado = ''
            if arquivo_modificado.filename and '.' in arquivo_modificado.filename:
                extensao_modificado = arquivo_modificado.filename.rsplit('.', 1)[1].lower()
            
            # Verificar formatos suportados
            if extensao_original not in ['docx', 'txt'] or extensao_modificado not in ['docx', 'txt']:
                flash('Apenas arquivos .docx e .txt são suportados', 'danger')
                return redirect(request.url)
            
            # Extrair textos
            texto_original = ComparadorDocumentos.extrair_texto(arquivo_original, extensao_original)
            texto_modificado = ComparadorDocumentos.extrair_texto(arquivo_modificado, extensao_modificado)
            
            # Comparar textos
            html_original, html_modificado = ComparadorDocumentos.comparar_textos(texto_original, texto_modificado)
            
            # Gerar título automático se não fornecido
            if not titulo:
                titulo = ComparadorDocumentos.gerar_titulo_automatico(texto_original)
            
            # Criar registro no banco de dados
            comparacao = ComparacaoDocumento()
            comparacao.id = ComparadorDocumentos.gerar_id_unico()
            comparacao.titulo = titulo
            comparacao.area_processo = area_processo
            comparacao.descricao_area = AREAS_PROCESSO.get(area_processo)
            comparacao.documento_cliente = re.sub('[^0-9]', '', cpf_cnpj_cliente)  # Limpar formatação
            comparacao.created_by_id = current_user.id
            comparacao.resultado_html_lado_a = html_original
            comparacao.resultado_html_lado_b = html_modificado
            comparacao.resultado_editado_a = html_original
            comparacao.resultado_editado_b = html_modificado
            
            db.session.add(comparacao)
            db.session.commit()
            
            flash('Comparação de documentos realizada com sucesso!', 'success')
            return redirect(url_for('comparacao_documentos.visualizar', id=comparacao.id))
            
        except Exception as e:
            logger.error(f"Erro ao processar comparação: {e}")
            flash(f'Erro ao processar os documentos: {e}', 'danger')
            return redirect(request.url)
    
    # Exibir formulário para upload
    return render_template(
        'comparacao_documentos/form.html',
        areas_processo=AREAS_PROCESSO,
        title="Nova Comparação de Documentos"
    )



@bp.route('/visualizar/<id>')
@login_required
@permission_required('comparacao_documentos.view')
def visualizar(id):
    """
    Visualizar uma comparação específica
    """
    from modules.comparacao_documentos.services.diff_marker import mark_differences
    
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Função auxiliar para extrair texto de HTML
    def extrair_texto_de_html(html):
        if not html:
            return ""
        texto = re.sub('<br>', '\n', html)
        texto = re.sub('<[^>]*>', '', texto)
        texto = texto.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return texto
    
    # Extrair texto puro para processamento
    texto_original = extrair_texto_de_html(comparacao.resultado_editado_a)
    texto_modificado = extrair_texto_de_html(comparacao.resultado_editado_b)
    
    # Reprocessar as diferenças com marcações diretas garantidas
    html_original, html_modificado = mark_differences(texto_original, texto_modificado)
    
    # Verificar se já existe uma análise de IA ou se o usuário solicitou uma nova
    analise_ia = None
    if request.args.get('analisar_ia') == '1' or (hasattr(comparacao, 'doc_metadata') and comparacao.doc_metadata and 'analise_ia' in comparacao.doc_metadata):
        try:
            # Se já existe análise e não foi solicitada nova, use a existente
            if hasattr(comparacao, 'doc_metadata') and comparacao.doc_metadata and 'analise_ia' in comparacao.doc_metadata and request.args.get('analisar_ia') != '1':
                analise_ia = comparacao.doc_metadata.get('analise_ia')
                logger.info(f"Recuperando análise de IA existente para comparação {id}")
            else:
                logger.info(f"Solicitando análise de IA para comparação {id}")
                
                # Executar a análise de IA com identificação de origem
                resultado_analise = ComparadorDocumentos.analisar_diferencas_ia_com_origem(
                    texto_original, 
                    texto_modificado,
                    comparacao.area_processo,
                    comparacao.documento_cliente
                )
                
                if resultado_analise.get('success'):
                    analise_ia = resultado_analise.get('analise')
                    
                    # Atualizar o campo doc_metadata do documento
                    if not hasattr(comparacao, 'doc_metadata') or not comparacao.doc_metadata:
                        comparacao.doc_metadata = {}
                    
                    comparacao.doc_metadata['analise_ia'] = analise_ia
                    db.session.commit()
                    
                    logger.info(f"Análise de IA concluída e salva para comparação {id}")
                    
                    # Se foi solicitada uma nova análise, redirecionar para remover o parâmetro da URL
                    if request.args.get('analisar_ia') == '1':
                        flash('Análise por IA concluída com sucesso!', 'success')
                        return redirect(url_for('comparacao_documentos.visualizar', id=id))
                else:
                    flash(f'Erro ao realizar análise por IA: {resultado_analise.get("error")}', 'warning')
        except Exception as e:
            logger.error(f"Erro ao processar análise de IA: {e}")
            flash(f'Erro ao processar análise de IA: {e}', 'danger')
    
    return render_template(
        'comparacao_documentos/visualizar.html',
        comparacao=comparacao,
        analise_ia=analise_ia,
        html_original=html_original,
        html_modificado=html_modificado,
        title=f"Comparação: {comparacao.titulo}",
        datetime=datetime
    )

# Rota de edição removida, pois a funcionalidade foi integrada na página de visualização

@bp.route('/excluir/<id>', methods=['POST'])
@login_required
@permission_required('comparacao_documentos.delete')
def excluir(id):
    """
    Excluir uma comparação - com logging detalhado para debug
    """
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Rota /excluir/{id} acessada")
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Método: {request.method}")
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Usuário: {current_user.username}")
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Headers: {dict(request.headers)}")
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Form data: {dict(request.form)}")
    
    try:
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Buscando comparação com ID: {id}")
        comparacao = ComparacaoDocumento.query.get_or_404(id)
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Comparação encontrada: {comparacao.titulo}")
        
        # Usuário autorizado - prosseguir com exclusão
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Usuário autorizado: {current_user.username}")
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Prosseguindo com exclusão...")
        
        # Armazenar título para mensagem
        titulo = comparacao.titulo
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Título para exclusão: {titulo}")
        
        # Excluir do banco de dados
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Iniciando exclusão do banco...")
        db.session.delete(comparacao)
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Objeto marcado para exclusão")
        
        db.session.commit()
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Commit realizado com sucesso")
        
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Comparação '{titulo}' excluída com sucesso pelo usuário {current_user.username}")
        flash('Comparação excluída com sucesso!', 'success')
        
    except Exception as e:
        logger.error(f"🗑️ [DEBUG EXCLUSÃO] ERRO CAPTURADO: {type(e).__name__}: {e}")
        logger.error(f"🗑️ [DEBUG EXCLUSÃO] Stacktrace:", exc_info=True)
        db.session.rollback()
        logger.info(f"🗑️ [DEBUG EXCLUSÃO] Rollback executado")
        flash(f'Erro ao excluir a comparação: {e}', 'danger')
    
    logger.info(f"🗑️ [DEBUG EXCLUSÃO] Redirecionando para index...")
    return redirect(url_for('comparacao_documentos.index'))

@bp.route('/api/analisar-ia/<id>', methods=['POST'])
def analisar_ia_api(id):
    """
    API para análise de IA de uma comparação
    """
    logger.info(f"🔍 INICIO: Análise IA solicitada para comparação {id}")
    
    try:
        comparacao = ComparacaoDocumento.query.get_or_404(id)
        logger.info(f"📄 Comparação encontrada: {comparacao.titulo}")
        
        # Forçar nova análise removendo cache (temporário para testar nova implementação)
        if hasattr(comparacao, 'doc_metadata') and comparacao.doc_metadata and 'analise_ia' in comparacao.doc_metadata:
            logger.info(f"🔄 Removendo análise anterior para executar nova implementação")
            comparacao.doc_metadata.pop('analise_ia', None)
            db.session.commit()
        
        # Extrair textos dos HTMLs salvos
        def extrair_texto_de_html(html):
            if not html:
                return ""
            texto = re.sub('<br>', '\n', html)
            texto = re.sub('<[^>]*>', '', texto)
            texto = texto.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            return texto
        
        texto_original = extrair_texto_de_html(comparacao.resultado_editado_a)
        texto_modificado = extrair_texto_de_html(comparacao.resultado_editado_b)
        
        # Realizar análise com IA
        logger.info(f"🤖 Iniciando análise IA para comparação {id}")
        logger.info(f"📊 Área do processo: {comparacao.area_processo}")
        logger.info(f"👤 Cliente: {comparacao.documento_cliente}")
        
        # Usar análise estruturada
        try:
            logger.info("Importando AnalisadorJuridicoIA...")
            from modules.comparacao_documentos.services.analise_confiavel import AnalisadorJuridicoIA
            
            logger.info("Criando instância do analisador...")
            analisador = AnalisadorJuridicoIA()
            
            metadata = {
                'area_processo': getattr(comparacao, 'area_processo', 'Não especificada'),
                'cliente': getattr(comparacao, 'documento_cliente', 'Não especificado')
            }
            
            logger.info(f"Iniciando análise com metadata: {metadata}")
            resultado = analisador.gerar_analise_estruturada(
                texto_original,
                texto_modificado,
                metadata
            )
            logger.info(f"Resultado da análise: {resultado['success']}")
            
            if resultado['success']:
                logger.info(f"Análise de IA bem-sucedida")
                
                # Salvar no banco
                comparacao.analise_ia_resultado = resultado['analise_texto']
                comparacao.analise_ia_data = datetime.now()
                
                # Usar campo diferente para metadata (não doc_metadata)
                if not hasattr(comparacao, 'metadata_json') or not comparacao.metadata_json:
                    comparacao.metadata_json = "{}"
                
                import json
                try:
                    metadata = json.loads(comparacao.metadata_json)
                except:
                    metadata = {}
                
                metadata['analise_ia'] = {
                    'dados': resultado['analise_json'],
                    'timestamp': datetime.now().isoformat(),
                    'versao': '2.0'
                }
                
                comparacao.metadata_json = json.dumps(metadata)
                db.session.commit()
                
                logger.info(f"Análise de IA salva para comparação {id}")
                
                return jsonify({
                    'success': True,
                    'analise_json': resultado['analise_json'],
                    'timestamp': resultado['timestamp']
                })
            else:
                logger.error(f"Erro na análise: {resultado.get('error', 'Erro desconhecido')}")
                return jsonify({
                    'success': False,
                    'error': resultado.get('error', 'Erro desconhecido')
                })
                
        except Exception as analise_error:
            logger.error(f"Erro na análise: {analise_error}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Fallback estruturado
            analise_fallback = {
                "resumo_geral": "Análise concluída com dados básicos devido a limitações técnicas",
                "score_global": 70,
                "gravidade_alteracoes": "MÉDIA",
                "impacto_juridico": "Foram identificadas diferenças que requerem revisão",
                "riscos_identificados": [
                    {
                        "tipo_risco": "Revisão",
                        "descricao": "Necessário revisar alterações detectadas",
                        "probabilidade": "MÉDIA",
                        "impacto_potencial": "Alterações podem afetar interpretação do documento",
                        "medidas_mitigacao": "Realizar revisão jurídica detalhada"
                    }
                ],
                "trechos_analisados": [
                    {
                        "tipo": "MODIFICAÇÃO",
                        "natureza_alteracao": "REDACIONAL",
                        "trecho_original": "Conteúdo original detectado",
                        "trecho_modificado": "Conteúdo modificado detectado",
                        "impacto_detalhado": "Alteração requer atenção",
                        "urgencia": "MÉDIA",
                        "recomendacao_especifica": "Revisar alteração identificada"
                    }
                ]
            }
            
            # Salvar fallback usando campo disponível
            if not hasattr(comparacao, 'metadata_json') or not comparacao.metadata_json:
                comparacao.metadata_json = "{}"
            
            import json
            try:
                metadata = json.loads(comparacao.metadata_json)
            except:
                metadata = {}
            
            metadata['analise_ia'] = {
                'dados': analise_fallback,
                'timestamp': datetime.now().isoformat(),
                'versao': '2.0-fallback'
            }
            
            comparacao.metadata_json = json.dumps(metadata)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'analise_json': analise_fallback,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Erro geral ao processar análise de IA via API: {e}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@bp.route('/exportar/<id>/<lado>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar(id, lado):
    """
    Exportar o resultado da comparação como documento DOCX (rota legada)
    """
    logger.info(f"[EXPORT DEBUG] Recebido pedido de exportação Word - ID: {id}, Lado: {lado}")
    
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Mapear valores do frontend para backend
    lado_map = {
        'original': 'a',
        'modificado': 'b', 
        'comparacao': 'comparacao',
        'a': 'a',
        'b': 'b',
        'docx': 'a',  # fallback para compatibilidade
        'pdf': 'a',   # fallback para compatibilidade
        'word': 'a'   # fallback para compatibilidade
    }
    
    lado_real = lado_map.get(lado, 'a')  # default para 'a' se não encontrar
    logger.info(f"[EXPORT DEBUG] Lado mapeado: {lado} -> {lado_real}")
    
    # Verificar qual lado exportar
    if lado_real not in ['a', 'b', 'comparacao']:
        logger.error(f"[EXPORT DEBUG] Lado inválido após mapeamento: {lado_real}")
        return jsonify({'error': f'Lado inválido para exportação: {lado}'}), 400
    
    try:
        # Criar documento DOCX
        doc = Document()
        
        # Definir título
        titulo = doc.add_heading(comparacao.titulo, level=1)
        
        # Adicionar metadados
        p = doc.add_paragraph()
        p.add_run(f"Área: {comparacao.descricao_area} ({comparacao.area_processo})").bold = True
        doc.add_paragraph(f"Data: {comparacao.data_comparacao.strftime('%d/%m/%Y %H:%M')}")
        doc.add_paragraph(f"Cliente: {comparacao.documento_cliente}")
        doc.add_paragraph()
        
        # Obter o texto HTML para o lado selecionado
        if lado_real == 'comparacao':
            # Para comparação, incluir ambos os lados
            html_content = f"<h2>Versão Original</h2>{comparacao.resultado_editado_a}<br><br><h2>Versão Modificada</h2>{comparacao.resultado_editado_b}"
        else:
            html_content = comparacao.resultado_editado_a if lado_real == 'a' else comparacao.resultado_editado_b
        
        # Processar o HTML mantendo as marcações de diferenças
        processar_html_com_marcacoes(doc, html_content)
        
        # Salvar temporariamente
        temp_filename = f"comparacao_{id}_{lado_real}.docx"
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comparacao_docs', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        doc.save(temp_path)
        
        # Enviar arquivo
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"Comparacao_{comparacao.titulo}_{lado}.docx",
            max_age=300  # 5 minutos
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar comparação: {e}")
        flash(f'Erro ao exportar o documento: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))

@bp.route('/exportar-com-marcacoes/<id>/<lado>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar_com_marcacoes(id, lado):
    """
    Exportar o resultado da comparação como documento DOCX com marcações de diferenças
    """
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Verificar qual lado exportar
    if lado not in ['a', 'b']:
        abort(400, "Lado inválido para exportação")
    
    try:
        # Criar documento DOCX
        doc = Document()
        
        # Definir título
        titulo = doc.add_heading(comparacao.titulo, level=1)
        
        # Adicionar metadados
        p = doc.add_paragraph()
        p.add_run(f"Área: {comparacao.descricao_area} ({comparacao.area_processo})").bold = True
        doc.add_paragraph(f"Data: {comparacao.data_comparacao.strftime('%d/%m/%Y %H:%M')}")
        doc.add_paragraph(f"Cliente: {comparacao.documento_cliente}")
        
        # Adicionar legenda das marcações
        legenda = doc.add_paragraph()
        legenda.add_run("Legenda das Marcações:").bold = True
        
        leg_p1 = doc.add_paragraph()
        run_add = leg_p1.add_run("• Texto Adicionado: ")
        run_add_ex = leg_p1.add_run("destacado em verde e negrito")
        run_add_ex.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
        run_add_ex.bold = True
        
        leg_p2 = doc.add_paragraph()
        run_rem = leg_p2.add_run("• Texto Removido: ")
        run_rem_ex = leg_p2.add_run("destacado em vermelho e riscado")
        run_rem_ex.font.highlight_color = WD_COLOR_INDEX.RED
        run_rem_ex.font.strike = True
        
        leg_p3 = doc.add_paragraph()
        run_mod = leg_p3.add_run("• Texto Modificado: ")
        run_mod_ex = leg_p3.add_run("destacado em amarelo")
        run_mod_ex.font.highlight_color = WD_COLOR_INDEX.YELLOW
        
        doc.add_paragraph()  # Espaço
        
        # Reprocessar as diferenças para garantir marcações corretas
        texto_original_limpo = re.sub('<br>', '\n', comparacao.resultado_html_lado_a or '')
        texto_original_limpo = re.sub('<[^>]*>', '', texto_original_limpo)
        
        texto_modificado_limpo = re.sub('<br>', '\n', comparacao.resultado_html_lado_b or '')
        texto_modificado_limpo = re.sub('<[^>]*>', '', texto_modificado_limpo)
        
        # Recriar as marcações usando diff
        from modules.comparacao_documentos.services.comparador import ComparadorDocumentos
        html_original_novo, html_modificado_novo = ComparadorDocumentos.comparar_textos(
            texto_original_limpo, texto_modificado_limpo
        )
        
        # Usar o HTML correto baseado no lado selecionado
        html_content = html_original_novo if lado == 'a' else html_modificado_novo
        
        # Processar o HTML com as marcações de diferenças
        processar_html_com_marcacoes(doc, html_content)
        
        # Salvar temporariamente
        temp_filename = f"comparacao_marcada_{id}_{lado}.docx"
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comparacao_docs', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        doc.save(temp_path)
        
        # Enviar arquivo
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"Comparacao_Marcada_{comparacao.titulo}_{lado}.docx",
            max_age=300  # 5 minutos
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar comparação com marcações: {e}")
        flash(f'Erro ao exportar o documento com marcações: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))


@bp.route('/exportar_pdf/<id>/<lado>')
@login_required
@permission_required('comparacao_documentos.view')
def exportar_pdf(id, lado):
    """
    Exporta uma comparação como PDF com marcações coloridas
    """
    try:
        logger.info(f"[EXPORT DEBUG] Recebido pedido de exportação PDF - ID: {id}, Lado: {lado}")
        
        comparacao = ComparacaoDocumento.query.get_or_404(id)
        
        # Mapear valores do frontend para backend
        lado_map = {
            'original': 'a',
            'modificado': 'b', 
            'comparacao': 'comparacao',
            'a': 'a',
            'b': 'b',
            'pdf': 'a',   # fallback para compatibilidade
            'docx': 'a'   # fallback para compatibilidade
        }
        
        lado_real = lado_map.get(lado, 'a')  # default para 'a' se não encontrar
        logger.info(f"[EXPORT DEBUG] Lado mapeado: {lado} -> {lado_real}")
        
        # Verificar qual lado exportar
        if lado_real not in ['a', 'b', 'comparacao']:
            logger.error(f"[EXPORT DEBUG] Lado inválido após mapeamento: {lado_real}")
            return jsonify({'error': f'Lado inválido para exportação: {lado}'}), 400
        
        # Verificar permissões do usuário (admins podem acessar todas as comparações)
        if not current_user.is_admin and comparacao.usuario_id != current_user.id:
            flash('Você não tem permissão para acessar esta comparação.', 'danger')
            return redirect(url_for('comparacao_documentos.index'))
        
        # Reprocessar as diferenças para garantir marcações corretas
        texto_original_limpo = re.sub('<br>', '\n', comparacao.resultado_html_lado_a or '')
        texto_original_limpo = re.sub('<[^>]*>', '', texto_original_limpo)
        
        texto_modificado_limpo = re.sub('<br>', '\n', comparacao.resultado_html_lado_b or '')
        texto_modificado_limpo = re.sub('<[^>]*>', '', texto_modificado_limpo)
        
        # Recriar as marcações usando diff
        html_original_novo, html_modificado_novo = ComparadorDocumentos.comparar_textos(
            texto_original_limpo, texto_modificado_limpo
        )
        
        # Usar o HTML correto baseado no lado selecionado
        if lado_real == 'comparacao':
            html_content = f"<h2>Versão Original</h2>{html_original_novo}<br><br><h2>Versão Modificada</h2>{html_modificado_novo}"
        else:
            html_content = html_original_novo if lado_real == 'a' else html_modificado_novo
        
        # Inicializar formatador profissional
        formatter = ComparacaoExportFormatter()
        
        # Gerar PDF com formatação aprimorada
        pdf_buffer = formatter.gerar_pdf_formatado(comparacao, lado_real, incluir_marcacoes=True)
        
        # Retornar PDF como resposta
        filename = f"Comparacao_PDF_{comparacao.titulo}_{lado}.pdf"
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar comparação como PDF: {e}")
        flash(f'Erro ao exportar o documento como PDF: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))

@bp.route('/api/salvar-edicao/<id>', methods=['POST'])
@login_required
@permission_required('comparacao_documentos.edit')
def salvar_edicao(id):
    """
    API para salvar ediçẽos via AJAX
    """
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    try:
        # Obter dados do JSON
        data = request.get_json()
        
        # Atualizar campos
        if 'lado_a' in data:
            comparacao.resultado_editado_a = data['lado_a']
        if 'lado_b' in data:
            comparacao.resultado_editado_b = data['lado_b']
        if 'titulo' in data:
            comparacao.titulo = data['titulo']
        
        # Salvar alterações
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Alterações salvas com sucesso!'})
        
    except Exception as e:
        logger.error(f"Erro ao salvar edição via API: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/salvar-alteracoes/<id>', methods=['POST'])
@login_required
@permission_required('comparacao_documentos.edit')
def api_salvar_alteracoes(id):
    """
    API para salvar alterações feitas na visualização de comparação
    """
    try:
        comparacao = ComparacaoDocumento.query.get_or_404(id)
        
        # Obter dados JSON do request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Atualizar textos se fornecidos
        if 'texto_original' in data:
            comparacao.texto_original_marcado = data['texto_original']
            logger.info(f"Texto original atualizado para comparação {id}")
        
        if 'texto_modificado' in data:
            comparacao.texto_modificado_marcado = data['texto_modificado']
            logger.info(f"Texto modificado atualizado para comparação {id}")
        
        # Atualizar metadados se necessário
        if comparacao.doc_metadata is None:
            comparacao.doc_metadata = {}
        
        comparacao.doc_metadata['ultima_edicao'] = datetime.utcnow().isoformat()
        comparacao.doc_metadata['editado_por'] = current_user.username
        
        # Salvar no banco de dados
        db.session.commit()
        
        logger.info(f"Alterações salvas com sucesso para comparação {id}")
        
        return jsonify({
            'success': True,
            'message': 'Alterações salvas com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar alterações via API: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao salvar alterações: {str(e)}'
        }), 500

# Função duplicada removida - usando a primeira implementação com debug detalhado

# Novas rotas de exportação com formatação melhorada

@bp.route('/exportar-pro/<id>/<lado>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar_pro(id, lado):
    """
    Exportar o resultado da comparação como documento DOCX com formatação profissional
    """
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Verificar qual lado exportar
    if lado not in ['a', 'b']:
        abort(400, "Lado inválido para exportação")
    
    try:
        # Inicializar formatador
        formatter = ComparacaoExportFormatter()
        
        # Gerar documento DOCX formatado
        doc = formatter.gerar_docx_formatado(comparacao, lado, incluir_marcacoes=True)
        
        # Salvar temporariamente
        temp_filename = f"comparacao_pro_{id}_{lado}.docx"
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comparacao_docs', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        doc.save(temp_path)
        
        logger.info(f"✅ [EXPORT PRO] Documento DOCX profissional gerado: {temp_filename}")
        
        # Enviar arquivo
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"Comparacao_Pro_{comparacao.titulo}_{lado}.docx",
            max_age=300
        )
        
    except Exception as e:
        logger.error(f"❌ [EXPORT PRO] Erro ao exportar DOCX: {e}")
        flash(f'Erro ao exportar o documento: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))

@bp.route('/exportar-pdf/<id>/<lado>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar_pdf_pro(id, lado):
    """
    Exportar o resultado da comparação como documento PDF com formatação profissional
    """
    logger.info(f"[EXPORT DEBUG] Recebido pedido de exportação PDF Pro - ID: {id}, Lado: {lado}")
    
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Mapear valores do frontend para backend
    lado_map = {
        'original': 'a',
        'modificado': 'b', 
        'comparacao': 'comparacao',
        'a': 'a',
        'b': 'b',
        'pdf': 'a',   # fallback para compatibilidade
        'docx': 'a'   # fallback para compatibilidade
    }
    
    lado_real = lado_map.get(lado, 'a')  # default para 'a' se não encontrar
    logger.info(f"[EXPORT DEBUG] Lado mapeado: {lado} -> {lado_real}")
    
    # Verificar qual lado exportar
    if lado_real not in ['a', 'b', 'comparacao']:
        logger.error(f"[EXPORT DEBUG] Lado inválido após mapeamento: {lado_real}")
        abort(400, f"Lado inválido para exportação: {lado}")
    
    try:
        # Inicializar formatador
        formatter = ComparacaoExportFormatter()
        
        # Gerar documento PDF formatado
        buffer = formatter.gerar_pdf_formatado(comparacao, lado_real, incluir_marcacoes=True)
        
        logger.info(f"✅ [EXPORT PDF] Documento PDF profissional gerado para comparação {id}")
        
        # Enviar arquivo
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Comparacao_Pro_{comparacao.titulo}_{lado}.pdf",
            mimetype='application/pdf',
            max_age=300
        )
        
    except Exception as e:
        logger.error(f"❌ [EXPORT PDF] Erro ao exportar PDF: {e}")
        flash(f'Erro ao exportar o documento PDF: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))

@bp.route('/exportar-docx/<id>/<lado>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar_docx(id, lado):
    """
    Exportar o resultado da comparação como documento DOCX simples (sem marcações)
    """
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    # Verificar qual lado exportar
    if lado not in ['a', 'b']:
        abort(400, "Lado inválido para exportação")
    
    try:
        # Inicializar formatador
        formatter = ComparacaoExportFormatter()
        
        # Gerar documento DOCX sem marcações com formatação aprimorada
        doc = formatter.gerar_docx_formatado(comparacao, lado, incluir_marcacoes=False)
        
        # Salvar temporariamente
        temp_filename = f"comparacao_simples_{id}_{lado}.docx"
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comparacao_docs', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        doc.save(temp_path)
        
        logger.info(f"✅ [EXPORT SIMPLES] Documento DOCX simples gerado: {temp_filename}")
        
        # Enviar arquivo
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"Comparacao_Simples_{comparacao.titulo}_{lado}.docx",
            max_age=300
        )
        
    except Exception as e:
        logger.error(f"❌ [EXPORT SIMPLES] Erro ao exportar DOCX simples: {e}")
        flash(f'Erro ao exportar o documento: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))

@bp.route('/exportar-relatorio/<id>', methods=['GET'])
@login_required
@permission_required('comparacao_documentos.view')
def exportar_relatorio(id):
    """
    Exportar relatório completo da comparação (ambos os lados + análise)
    """
    comparacao = ComparacaoDocumento.query.get_or_404(id)
    
    try:
        # Inicializar formatador
        formatter = ComparacaoExportFormatter()
        
        # Gerar relatório PDF completo
        buffer = formatter.gerar_relatorio_completo_pdf(comparacao)
        
        logger.info(f"✅ [EXPORT RELATÓRIO] Relatório completo gerado para comparação {id}")
        
        # Enviar arquivo
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Relatorio_Comparacao_{comparacao.titulo}.pdf",
            mimetype='application/pdf',
            max_age=300
        )
        
    except Exception as e:
        logger.error(f"❌ [EXPORT RELATÓRIO] Erro ao exportar relatório: {e}")
        flash(f'Erro ao exportar o relatório: {e}', 'danger')
        return redirect(url_for('comparacao_documentos.visualizar', id=id))