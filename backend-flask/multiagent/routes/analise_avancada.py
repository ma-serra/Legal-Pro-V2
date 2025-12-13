"""
Rotas para recursos avançados de análise e gestão de documentos.

Este módulo contém todas as rotas relacionadas aos recursos avançados:
1. Análise Comparativa
2. Histórico de Versões
3. Extração de Entidades
4. Cache Otimizado
"""
import json
import datetime
import logging
import os
from typing import Dict, Any, Optional, List

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app, session

# ✅ CORRIGIDO: Usar database.py ao invés de main.py para evitar circular import
try:
    from database import db
except ImportError:
    # Fallback: usar current_app se database.py não existir
    from flask import current_app
    db = None
    def get_db():
        if db is None:
            return current_app.extensions['sqlalchemy'].db
        return db

from flask_login import login_required, current_user
from models import Documento, VersaoDocumento, AnaliseDocumento, AnaliseComparativa, EntidadeDocumento

# ✅ CORRIGIDO: Usar auth.py da raiz que tem todas as funções necessárias
from auth import admin_required, permission_required, log_audit

# Importa os módulos avançados
from multiagent.modules.analise_comparativa import comparar_analises, listar_analises_documento, listar_comparacoes_analise
from multiagent.modules.his

torico_versoes import (
    criar_documento, adicionar_versao, listar_documentos
)
from multiagent.modules.extracao_entidades import (
    extrair_entidades, extrair_citacoes
)


# Funções simuladas para desenvolvimento até que os módulos reais sejam implementados
def listar_versoes(documento_id):
    """Simulação temporária da função listar_versoes"""
    return {"success": True, "versoes": []}

def obter_versao(documento_id, numero_versao):
    """Simulação temporária da função obter_versao"""
    return {"success": True, "versao": {}}

def comparar_versoes(documento_id, versao1, versao2):
    """Simulação temporária da função comparar_versoes"""
    return {
        "success": True, 
        "versao1": {"numero_versao": versao1},
        "versao2": {"numero_versao": versao2},
        "diff_html": "<p>Simulação de comparação de versões</p>",
        "estatisticas": {"adicionados": 0, "removidos": 0, "modificados": 0}
    }

def buscar_entidades_similares(termo, tipo=None):
    """Simulação temporária da função buscar_entidades_similares"""
    return {"success": True, "entidades": []}

# Configuração de logging
logger = logging.getLogger(__name__)

# Cria o blueprint
analise_avancada = Blueprint('analise_avancada', __name__)

# ==================================================
# Rota principal para recursos avançados
# ==================================================

@analise_avancada.route('/', methods=['GET'])
@login_required
def pagina_principal():
    """
    Página principal dos recursos avançados.
    """
    current_app.logger.info("Renderizando página principal de recursos avançados")
    return render_template('avancado/index.html')

# ==================================================
# Rotas para Análise Comparativa
# ==================================================

@analise_avancada.route('/comparativa', methods=['GET'])
@login_required
def pagina_analise_comparativa():
    """
    Página principal de análise comparativa.
    """
    return render_template('avancado/comparativa/index.html')

@analise_avancada.route('/comparativa/documento/<int:documento_id>', methods=['GET'])
@login_required
def pagina_analise_comparativa_documento(documento_id):
    """
    Página de análise comparativa para um documento específico.
    """
    documento = Documento.query.get_or_404(documento_id)
    analises = listar_analises_documento(documento_id)
    
    return render_template(
        'avancado/comparativa/documento.html',
        documento=documento,
        analises=analises
    )

@analise_avancada.route('/comparativa/analise/<int:analise_id>', methods=['GET'])
@login_required
def pagina_analise_comparativa_analise(analise_id):
    """
    Página de análise comparativa mostrando uma análise específica e suas comparações.
    """
    analise = AnaliseDocumento.query.get_or_404(analise_id)
    documento = Documento.query.get(analise.documento_id)
    comparacoes = listar_comparacoes_analise(analise_id)
    
    return render_template(
        'avancado/comparativa/analise.html',
        analise=analise,
        documento=documento,
        comparacoes=comparacoes
    )

@analise_avancada.route('/api/comparativa/comparar', methods=['POST'])
@login_required
def api_comparar_analises():
    """
    API para comparar duas análises.
    """
    # Extrai dados do JSON da requisição
    data = request.get_json() or {}
    
    analise_principal_id = data.get('analise_principal_id')
    analise_comparada_id = data.get('analise_comparada_id')
    
    if not analise_principal_id or not analise_comparada_id:
        return jsonify({"success": False, "error": "IDs das análises são obrigatórios"})
    
    try:
        resultado = comparar_analises(analise_principal_id, analise_comparada_id, current_user.id)
        
        # Registra a operação para auditoria
        log_audit(
            action="comparar_analises", 
            entity_type="analise_comparativa", 
            entity_id=str(resultado.get("comparacao", {}).get("id")),
            details=f"Comparação entre análises {analise_principal_id} e {analise_comparada_id}"
        )
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao comparar análises: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao comparar análises: {str(e)}"})

@analise_avancada.route('/comparativa/resultado/<int:comparacao_id>', methods=['GET'])
@login_required
def pagina_resultado_comparacao(comparacao_id):
    """
    Página mostrando o resultado de uma comparação.
    """
    comparacao = AnaliseComparativa.query.get_or_404(comparacao_id)
    analise_principal = AnaliseDocumento.query.get(comparacao.analise_principal_id)
    analise_comparada = AnaliseDocumento.query.get(comparacao.analise_comparada_id)
    documento = Documento.query.get(analise_principal.documento_id) if analise_principal else None
    
    # Converte para objetos Python
    pontos_concordantes = json.loads(comparacao.pontos_concordantes) if comparacao.pontos_concordantes else []
    pontos_divergentes = json.loads(comparacao.pontos_divergentes) if comparacao.pontos_divergentes else []
    pontos_complementares = json.loads(comparacao.pontos_complementares) if comparacao.pontos_complementares else []
    
    return render_template(
        'avancado/comparativa/resultado.html',
        comparacao=comparacao,
        analise_principal=analise_principal,
        analise_comparada=analise_comparada,
        documento=documento,
        pontos_concordantes=pontos_concordantes,
        pontos_divergentes=pontos_divergentes,
        pontos_complementares=pontos_complementares
    )

# ==================================================
# Rotas para Histórico de Versões
# ==================================================

@analise_avancada.route('/historico', methods=['GET'])
@login_required
def pagina_historico_versoes():
    """
    Página principal de histórico de versões.
    """
    # Obtém documentos do usuário
    documentos_usuario = listar_documentos(usuario_id=current_user.id)
    
    return render_template(
        'avancado/historico/index.html',
        documentos=documentos_usuario
    )

@analise_avancada.route('/historico/documento/<int:documento_id>', methods=['GET'])
@login_required
def pagina_historico_documento(documento_id):
    """
    Página de histórico de versões para um documento específico.
    """
    documento = Documento.query.get_or_404(documento_id)
    
    # Verifica se o usuário tem acesso ao documento
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        flash("Você não tem permissão para acessar este documento.", "error")
        return redirect(url_for('analise_avancada.pagina_historico_versoes'))
    
    resultado = listar_versoes(documento_id)
    versoes = resultado.get("versoes", [])
    
    return render_template(
        'avancado/historico/documento.html',
        documento=documento,
        versoes=versoes
    )

@analise_avancada.route('/historico/versao/<int:documento_id>/<int:numero_versao>', methods=['GET'])
@login_required
def pagina_visualizar_versao(documento_id, numero_versao):
    """
    Página para visualizar uma versão específica de um documento.
    """
    documento = Documento.query.get_or_404(documento_id)
    
    # Verifica se o usuário tem acesso ao documento
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        flash("Você não tem permissão para acessar este documento.", "error")
        return redirect(url_for('analise_avancada.pagina_historico_versoes'))
    
    # Busca a versão específica
    versao = VersaoDocumento.query.filter_by(
        documento_id=documento_id,
        numero_versao=numero_versao
    ).first_or_404()
    
    return render_template(
        'avancado/historico/versao.html',
        documento=documento,
        versao=versao
    )

@analise_avancada.route('/api/historico/documento/novo', methods=['POST'])
@login_required
def api_criar_documento():
    """
    API para criar um novo documento.
    """
    # Extrai dados do JSON da requisição
    data = request.get_json() or {}
    
    titulo = data.get('titulo')
    conteudo = data.get('conteudo')
    tipo = data.get('tipo')
    tags = data.get('tags')
    descricao = data.get('descricao')
    
    if not titulo or not conteudo:
        return jsonify({"success": False, "error": "Título e conteúdo são obrigatórios"})
    
    try:
        resultado = criar_documento(
            titulo=titulo,
            conteudo=conteudo,
            usuario_id=current_user.id,
            tipo=tipo,
            tags=tags,
            descricao=descricao
        )
        
        if resultado.get("success"):
            # Registra a operação para auditoria
            log_audit(
                action="criar_documento", 
                entity_type="documento", 
                entity_id=str(resultado.get("documento", {}).get("id")),
                details=f"Documento '{titulo}' criado"
            )
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao criar documento: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao criar documento: {str(e)}"})

@analise_avancada.route('/api/historico/versao/nova', methods=['POST'])
@login_required
def api_adicionar_versao():
    """
    API para adicionar uma nova versão a um documento.
    """
    # Extrai dados do JSON da requisição
    data = request.get_json() or {}
    
    documento_id = data.get('documento_id')
    conteudo = data.get('conteudo')
    comentario = data.get('comentario')
    
    if not documento_id or not conteudo:
        return jsonify({"success": False, "error": "ID do documento e conteúdo são obrigatórios"})
    
    # Verifica se o usuário tem acesso ao documento
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"success": False, "error": "Documento não encontrado"})
    
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "error": "Você não tem permissão para modificar este documento"})
    
    try:
        resultado = adicionar_versao(
            documento_id=documento_id,
            conteudo=conteudo,
            usuario_id=current_user.id,
            comentario=comentario
        )
        
        if resultado.get("success"):
            # Registra a operação para auditoria
            log_audit(
                action="adicionar_versao", 
                entity_type="versao_documento", 
                entity_id=str(resultado.get("versao", {}).get("id")),
                details=f"Versão {resultado.get('versao', {}).get('numero')} adicionada ao documento {documento_id}"
            )
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao adicionar versão: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao adicionar versão: {str(e)}"})

@analise_avancada.route('/historico/comparar/<int:documento_id>/<int:versao1>/<int:versao2>', methods=['GET'])
@login_required
def pagina_comparar_versoes(documento_id, versao1, versao2):
    """
    Página para comparar duas versões de um documento.
    """
    documento = Documento.query.get_or_404(documento_id)
    
    # Verifica se o usuário tem acesso ao documento
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        flash("Você não tem permissão para acessar este documento.", "error")
        return redirect(url_for('analise_avancada.pagina_historico_versoes'))
    
    resultado = comparar_versoes(documento_id, versao1, versao2)
    
    if not resultado.get("success"):
        flash(resultado.get("error", "Erro ao comparar versões."), "error")
        return redirect(url_for('analise_avancada.pagina_historico_documento', documento_id=documento_id))
    
    return render_template(
        'avancado/historico/comparar.html',
        documento=documento,
        versao1=resultado.get("versao1"),
        versao2=resultado.get("versao2"),
        diff_html=resultado.get("diff_html"),
        estatisticas=resultado.get("estatisticas")
    )

# ==================================================
# Rotas para Extração de Entidades
# ==================================================

@analise_avancada.route('/entidades', methods=['GET'])
@login_required
def pagina_extracao_entidades():
    """
    Página principal de extração de entidades.
    """
    # Obtém documentos do usuário
    documentos_usuario = listar_documentos(usuario_id=current_user.id)
    
    return render_template(
        'avancado/entidades/index.html',
        documentos=documentos_usuario
    )

@analise_avancada.route('/entidades/documento/<int:documento_id>', methods=['GET'])
@login_required
def pagina_entidades_documento(documento_id):
    """
    Página de entidades extraídas para um documento específico.
    """
    documento = Documento.query.get_or_404(documento_id)
    
    # Verifica se o usuário tem acesso ao documento
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        flash("Você não tem permissão para acessar este documento.", "error")
        return redirect(url_for('analise_avancada.pagina_extracao_entidades'))
    
    # Busca entidades do documento
    entidades = EntidadeDocumento.query.filter_by(documento_id=documento_id).all()
    
    # Agrupa por tipo
    entidades_por_tipo = {}
    for entidade in entidades:
        tipo = entidade.tipo_entidade
        if tipo not in entidades_por_tipo:
            entidades_por_tipo[tipo] = []
        
        metadados = json.loads(entidade.metadados) if entidade.metadados else {}
        
        entidades_por_tipo[tipo].append({
            "id": entidade.id,
            "nome": entidade.nome_entidade,
            "contexto": entidade.contexto,
            "metadados": metadados
        })
    
    return render_template(
        'avancado/entidades/documento.html',
        documento=documento,
        entidades_por_tipo=entidades_por_tipo
    )

@analise_avancada.route('/api/entidades/extrair', methods=['POST'])
@login_required
def api_extrair_entidades():
    """
    API para extrair entidades de um documento.
    """
    data = request.json
    
    documento_id = data.get('documento_id')
    versao_id = data.get('versao_id')
    
    if not documento_id:
        return jsonify({"success": False, "error": "ID do documento é obrigatório"})
    
    # Verifica se o usuário tem acesso ao documento
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"success": False, "error": "Documento não encontrado"})
    
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "error": "Você não tem permissão para acessar este documento"})
    
    try:
        resultado = extrair_entidades(documento_id, versao_id)
        
        if resultado.get("success"):
            # Registra a operação para auditoria
            log_audit(
                action="extrair_entidades", 
                entity_type="documento", 
                entity_id=str(documento_id),
                details=f"Extração de entidades do documento: {resultado.get('total_entidades')} entidades extraídas"
            )
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao extrair entidades: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao extrair entidades: {str(e)}"})

@analise_avancada.route('/api/entidades/extrair-citacoes', methods=['POST'])
@login_required
def api_extrair_citacoes():
    """
    API para extrair citações de um documento.
    """
    data = request.json
    
    documento_id = data.get('documento_id')
    versao_id = data.get('versao_id')
    
    if not documento_id:
        return jsonify({"success": False, "error": "ID do documento é obrigatório"})
    
    # Verifica se o usuário tem acesso ao documento
    documento = Documento.query.get(documento_id)
    if not documento:
        return jsonify({"success": False, "error": "Documento não encontrado"})
    
    if documento.usuario_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "error": "Você não tem permissão para acessar este documento"})
    
    try:
        resultado = extrair_citacoes(documento_id, versao_id)
        
        if resultado.get("success"):
            # Registra a operação para auditoria
            log_audit(
                action="extrair_citacoes", 
                entity_type="documento", 
                entity_id=str(documento_id),
                details=f"Extração de citações do documento: {resultado.get('total_citacoes')} citações extraídas"
            )
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao extrair citações: {str(e)}")
        return jsonify({"success": False, "error": f"Erro ao extrair citações: {str(e)}"})

@analise_avancada.route('/entidades/busca', methods=['GET'])
@login_required
def pagina_busca_entidades():
    """
    Página de busca de entidades.
    """
    termo = request.args.get('termo', '')
    tipo = request.args.get('tipo', '')
    
    resultados = []
    if termo:
        # Constrói a query base
        query = EntidadeDocumento.query.filter(
            EntidadeDocumento.nome_entidade.ilike(f'%{termo}%')
        )
        
        # Aplica filtro de tipo
        if tipo:
            query = query.filter_by(tipo_entidade=tipo)
            
        # Executa a busca
        entidades = query.all()
        
        for entidade in entidades:
            documento = Documento.query.get(entidade.documento_id)
            if documento and (documento.usuario_id == current_user.id or current_user.is_admin):
                metadados = json.loads(entidade.metadados) if entidade.metadados else {}
                
                resultados.append({
                    "id": entidade.id,
                    "tipo": entidade.tipo_entidade,
                    "nome": entidade.nome_entidade,
                    "contexto": entidade.contexto,
                    "metadados": metadados,
                    "documento_id": documento.id,
                    "documento_titulo": documento.titulo
                })
    
    # Obtém tipos de entidades disponíveis
    tipos_entidades = db.session.query(EntidadeDocumento.tipo_entidade).distinct().all()
    tipos = [t[0] for t in tipos_entidades]
    
    return render_template(
        'avancado/entidades/busca.html',
        termo=termo,
        tipo=tipo,
        resultados=resultados,
        tipos=tipos
    )

def init_blueprint(app):
    """
    Inicializa o blueprint no aplicativo Flask.
    
    Args:
        app: Aplicativo Flask
    """
    app.register_blueprint(analise_avancada, url_prefix='/avancado')