"""
Rotas do módulo Templates de Documentos Jurídicos
Migração dos 42 templates existentes da rota /juridico/especialistas
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from main import db
from .models import TemplateDocumento, CategoriaDocumento, HistoricoDocumento
from datetime import datetime
import json
import io
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

templates_documentos_bp = Blueprint('templates_documentos', __name__, 
                                   url_prefix='/documentos-juridicos',
                                   template_folder='templates')


@templates_documentos_bp.route('/')
@login_required
def index():
    """Página principal dos templates de documentos jurídicos"""
    categorias = CategoriaDocumento.query.filter_by(ativo=True).all()
    templates_recentes = TemplateDocumento.query.filter_by(ativo=True).order_by(
        TemplateDocumento.ultima_utilizacao.desc().nullslast(),
        TemplateDocumento.criado_em.desc()
    ).limit(8).all()
    
    # Estatísticas gerais
    total_templates = TemplateDocumento.query.filter_by(ativo=True).count()
    total_categorias = CategoriaDocumento.query.filter_by(ativo=True).count()
    total_documentos_gerados = HistoricoDocumento.query.count()
    
    return render_template('templates_documentos/index.html', 
                         categorias=categorias,
                         templates_recentes=templates_recentes,
                         total_templates=total_templates,
                         total_categorias=total_categorias,
                         total_documentos_gerados=total_documentos_gerados)


@templates_documentos_bp.route('/categoria/<int:categoria_id>')
@login_required
def templates_por_categoria(categoria_id):
    """Lista templates de uma categoria específica"""
    categoria = CategoriaDocumento.query.get_or_404(categoria_id)
    templates = TemplateDocumento.query.filter_by(
        categoria_id=categoria_id, 
        ativo=True
    ).order_by(TemplateDocumento.nome).all()
    
    return render_template('templates_documentos/categoria.html',
                         categoria=categoria,
                         templates=templates)


@templates_documentos_bp.route('/modulo/<modulo_origem>')
@login_required
def templates_por_modulo(modulo_origem):
    """Lista templates de um módulo jurídico específico"""
    templates = TemplateDocumento.query.filter_by(
        modulo_origem=modulo_origem,
        ativo=True
    ).order_by(TemplateDocumento.nome).all()
    
    if not templates:
        flash(f'Nenhum template encontrado para o módulo {modulo_origem}', 'info')
        return redirect(url_for('templates_documentos.index'))
    
    modulo_nome = templates[0].modulo_nome if templates else modulo_origem.title()
    
    return render_template('templates_documentos/modulo.html',
                         templates=templates,
                         modulo_origem=modulo_origem,
                         modulo_nome=modulo_nome)


@templates_documentos_bp.route('/template/<int:template_id>')
@login_required
def visualizar_template(template_id):
    """Visualiza detalhes de um template específico"""
    template = TemplateDocumento.query.get_or_404(template_id)
    
    # Templates relacionados da mesma categoria
    templates_relacionados = TemplateDocumento.query.filter(
        TemplateDocumento.categoria_id == template.categoria_id,
        TemplateDocumento.id != template_id,
        TemplateDocumento.ativo == True
    ).limit(4).all()
    
    return render_template('templates_documentos/visualizar.html',
                         template=template,
                         templates_relacionados=templates_relacionados)


@templates_documentos_bp.route('/template/<int:template_id>/usar', methods=['GET', 'POST'])
@login_required
def usar_template(template_id):
    """Interface para preenchimento e geração de documento"""
    template = TemplateDocumento.query.get_or_404(template_id)
    
    if request.method == 'GET':
        return render_template('templates_documentos/usar_template.html',
                             template=template)
    
    # POST - Gerar documento
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({
                'sucesso': False,
                'erro': 'Dados não fornecidos'
            }), 400
        
        campos_preenchidos = dados.get('campos', {})
        formato = dados.get('formato', 'pdf')
        titulo_documento = dados.get('titulo', template.nome)
        
        # Validar campos obrigatórios
        if template.campos_obrigatorios:
            for campo in template.campos_obrigatorios:
                if not campos_preenchidos.get(campo):
                    return jsonify({
                        'sucesso': False,
                        'erro': f'Campo obrigatório não preenchido: {campo}'
                    }), 400
        
        # Gerar documento
        documento_gerado = gerar_documento_template(template, campos_preenchidos, formato, titulo_documento)
        
        if not documento_gerado:
            return jsonify({
                'sucesso': False,
                'erro': 'Erro ao gerar documento'
            }), 500
        
        # Registrar no histórico
        historico = HistoricoDocumento(
            template_id=template_id,
            usuario_id=current_user.id,
            titulo_documento=titulo_documento,
            formato_exportacao=formato,
            campos_preenchidos=campos_preenchidos,
            ip_usuario=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(historico)
        template.incrementar_uso()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Documento gerado com sucesso!',
            'documento_id': historico.id,
            'download_url': url_for('templates_documentos.baixar_documento', documento_id=historico.id)
        })
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500


@templates_documentos_bp.route('/documento/<int:documento_id>/baixar')
@login_required
def baixar_documento(documento_id):
    """Baixa documento gerado"""
    documento = HistoricoDocumento.query.get_or_404(documento_id)
    
    # Verificar se o usuário pode baixar o documento
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        flash('Você não tem permissão para baixar este documento', 'error')
        return redirect(url_for('templates_documentos.meus_documentos'))
    
    try:
        # Gerar arquivo para download
        arquivo_gerado = gerar_arquivo_documento(documento)
        
        if not arquivo_gerado:
            flash('Erro ao gerar arquivo para download', 'error')
            return redirect(url_for('templates_documentos.meus_documentos'))
        
        documento.marcar_como_baixado()
        
        return send_file(
            arquivo_gerado['caminho'],
            as_attachment=True,
            download_name=arquivo_gerado['nome'],
            mimetype=arquivo_gerado['mimetype']
        )
        
    except Exception as e:
        flash(f'Erro ao baixar documento: {str(e)}', 'error')
        return redirect(url_for('templates_documentos.meus_documentos'))


@templates_documentos_bp.route('/pesquisar')
@login_required
def pesquisar():
    """Pesquisa templates"""
    termo = request.args.get('q', '').strip()
    categoria_id = request.args.get('categoria')
    modulo_origem = request.args.get('modulo')
    area_juridica = request.args.get('area')
    
    query = TemplateDocumento.query.filter_by(ativo=True)
    
    if termo:
        query = query.filter(
            db.or_(
                TemplateDocumento.nome.ilike(f'%{termo}%'),
                TemplateDocumento.descricao.ilike(f'%{termo}%'),
                TemplateDocumento.tipo_documento.ilike(f'%{termo}%')
            )
        )
    
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    
    if modulo_origem:
        query = query.filter_by(modulo_origem=modulo_origem)
    
    if area_juridica:
        query = query.filter_by(area_juridica=area_juridica)
    
    templates = query.order_by(TemplateDocumento.nome).all()
    categorias = CategoriaDocumento.query.filter_by(ativo=True).all()
    
    # Obter módulos únicos para filtro
    modulos = db.session.query(
        TemplateDocumento.modulo_origem,
        TemplateDocumento.modulo_nome
    ).filter_by(ativo=True).distinct().all()
    
    return render_template('templates_documentos/pesquisar.html',
                         templates=templates,
                         categorias=categorias,
                         modulos=modulos,
                         termo_pesquisa=termo,
                         categoria_selecionada=categoria_id,
                         modulo_selecionado=modulo_origem,
                         area_selecionada=area_juridica)


@templates_documentos_bp.route('/meus-documentos')
@login_required
def meus_documentos():
    """Lista documentos gerados pelo usuário"""
    historico = HistoricoDocumento.query.filter_by(
        usuario_id=current_user.id
    ).order_by(HistoricoDocumento.gerado_em.desc()).all()
    
    return render_template('templates_documentos/meus_documentos.html',
                         historico=historico)


@templates_documentos_bp.route('/estatisticas')
@login_required
def estatisticas():
    """Estatísticas de uso dos templates"""
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem ver estatísticas.', 'error')
        return redirect(url_for('templates_documentos.index'))
    
    # Templates mais utilizados
    templates_populares = TemplateDocumento.query.order_by(
        TemplateDocumento.total_utilizacoes.desc()
    ).limit(10).all()
    
    # Estatísticas por categoria
    stats_categorias = db.session.query(
        CategoriaDocumento.nome,
        db.func.count(TemplateDocumento.id).label('total_templates'),
        db.func.sum(TemplateDocumento.total_utilizacoes).label('total_usos')
    ).join(TemplateDocumento).filter(
        TemplateDocumento.ativo == True
    ).group_by(CategoriaDocumento.nome).all()
    
    # Estatísticas por módulo
    stats_modulos = db.session.query(
        TemplateDocumento.modulo_nome,
        db.func.count(TemplateDocumento.id).label('total_templates'),
        db.func.sum(TemplateDocumento.total_utilizacoes).label('total_usos')
    ).filter(TemplateDocumento.ativo == True).group_by(
        TemplateDocumento.modulo_nome
    ).all()
    
    # Estatísticas gerais
    total_templates = TemplateDocumento.query.filter_by(ativo=True).count()
    total_documentos = HistoricoDocumento.query.count()
    total_categorias = CategoriaDocumento.query.filter_by(ativo=True).count()
    
    return render_template('templates_documentos/estatisticas.html',
                         templates_populares=templates_populares,
                         stats_categorias=stats_categorias,
                         stats_modulos=stats_modulos,
                         total_templates=total_templates,
                         total_documentos=total_documentos,
                         total_categorias=total_categorias)


# Funções auxiliares
def gerar_documento_template(template, campos_preenchidos, formato, titulo):
    """Gera documento baseado no template e dados preenchidos"""
    try:
        # Substituir variáveis no conteúdo do template
        conteudo = template.conteudo_template or f"Documento: {template.nome}\n\nDescrição: {template.descricao}"
        
        # Substituir campos preenchidos no conteúdo
        for campo, valor in campos_preenchidos.items():
            conteudo = conteudo.replace(f"{{{{ {campo} }}}}", str(valor))
        
        return {
            'titulo': titulo,
            'conteudo': conteudo,
            'formato': formato,
            'template_id': template.id
        }
        
    except Exception as e:
        print(f"Erro ao gerar documento: {e}")
        return None


def gerar_arquivo_documento(documento):
    """Gera arquivo físico do documento para download"""
    try:
        template = documento.template
        conteudo = template.conteudo_template or f"Documento: {template.nome}"
        
        # Substituir campos preenchidos
        if documento.campos_preenchidos:
            for campo, valor in documento.campos_preenchidos.items():
                conteudo = conteudo.replace(f"{{{{ {campo} }}}}", str(valor))
        
        formato = documento.formato_exportacao
        nome_arquivo = f"{documento.titulo_documento}.{formato}"
        
        if formato == 'docx':
            # Gerar DOCX
            doc = Document()
            doc.add_heading(documento.titulo_documento, 0)
            doc.add_paragraph(conteudo)
            
            # Salvar em memória
            arquivo_io = io.BytesIO()
            doc.save(arquivo_io)
            arquivo_io.seek(0)
            
            return {
                'caminho': arquivo_io,
                'nome': nome_arquivo,
                'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        
        else:  # HTML ou texto
            return {
                'caminho': io.StringIO(conteudo),
                'nome': nome_arquivo,
                'mimetype': 'text/html' if formato == 'html' else 'text/plain'
            }
            
    except Exception as e:
        print(f"Erro ao gerar arquivo: {e}")
        return None