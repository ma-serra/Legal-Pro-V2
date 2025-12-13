"""
Rotas para integração completa entre componentes do editor e sistema de fluxos
Compartilha componentes entre /componentes-editor/<id> e /fluxos/editor/<id>
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import ComponenteEditor, FluxoModel, db
from sqlalchemy import func
import json
import datetime

def configurar_rotas_integracao_componentes(app):
    """Configura todas as rotas para integração de componentes"""

    # ===== APIS DE INTEGRAÇÃO =====
    
    @app.route('/api/componentes/shared/listar', methods=['GET'])
    @login_required
    def api_componentes_compartilhados():
        """API para listar todos os componentes compartilhados entre editores"""
        try:
            categoria = request.args.get('categoria')
            tipo = request.args.get('tipo')
            termo_busca = request.args.get('q', '').strip()
            
            # Query base
            query = ComponenteEditor.query.filter_by(ativo=True)
            
            # Aplicar filtros
            if categoria:
                query = query.filter_by(categoria=categoria)
            if tipo:
                query = query.filter_by(tipo=tipo)
            if termo_busca:
                query = query.filter(
                    (ComponenteEditor.nome.ilike(f'%{termo_busca}%')) |
                    (ComponenteEditor.descricao.ilike(f'%{termo_busca}%'))
                )
            
            # Ordenar por categoria e nome
            componentes = query.order_by(
                ComponenteEditor.categoria,
                ComponenteEditor.nome
            ).all()
            
            # Converter para formato compatível com ambos editores
            resultado = []
            for comp in componentes:
                resultado.append({
                    'id': comp.id,
                    'nome': comp.nome,
                    'categoria': comp.categoria,
                    'tipo': comp.tipo,
                    'descricao': comp.descricao,
                    'descricao_detalhada': comp.descricao_detalhada,
                    'icone': comp.icone,
                    'cor': comp.cor,
                    'capacidades': comp.capacidades or [],
                    'parametros': comp.parametros or {},
                    'configuracao': comp.configuracao or {},
                    'base_conhecimento': comp.base_conhecimento,
                    'prompt_sistema': comp.prompt_sistema,
                    'prompt_usuario': comp.prompt_usuario,
                    'temperatura': comp.temperatura,
                    'max_tokens': comp.max_tokens,
                    'top_k': comp.top_k,
                    'chunk_size': comp.chunk_size,
                    'chunk_overlap': comp.chunk_overlap,
                    'ativo': comp.ativo,
                    'criado_em': comp.criado_em.isoformat() if comp.criado_em else None,
                    'atualizado_em': comp.atualizado_em.isoformat() if comp.atualizado_em else None
                })
            
            return jsonify({
                'success': True,
                'componentes': resultado,
                'total': len(resultado),
                'filtros_aplicados': {
                    'categoria': categoria,
                    'tipo': tipo,
                    'termo_busca': termo_busca
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao listar componentes compartilhados: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'componentes': [],
                'total': 0
            }), 500

    @app.route('/api/componentes/shared/<int:componente_id>', methods=['GET'])
    @login_required
    def api_componente_detalhes(componente_id):
        """API para obter detalhes completos de um componente específico"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Dados detalhados do componente
            detalhes = {
                'id': componente.id,
                'nome': componente.nome,
                'categoria': componente.categoria,
                'tipo': componente.tipo,
                'descricao': componente.descricao,
                'descricao_detalhada': componente.descricao_detalhada,
                'icone': componente.icone,
                'cor': componente.cor,
                'ativo': componente.ativo,
                'configuracao': componente.configuracao or {},
                'parametros': componente.parametros or {},
                'capacidades': componente.capacidades or [],
                'prompt_sistema': componente.prompt_sistema,
                'prompt_usuario': componente.prompt_usuario,
                'base_conhecimento': componente.base_conhecimento,
                'config_ia': {
                    'temperatura': componente.temperatura,
                    'max_tokens': componente.max_tokens,
                    'top_k': componente.top_k,
                    'chunk_size': componente.chunk_size,
                    'chunk_overlap': componente.chunk_overlap
                },
                'metadados': {
                    'criado_em': componente.criado_em.isoformat() if componente.criado_em else None,
                    'atualizado_em': componente.atualizado_em.isoformat() if componente.atualizado_em else None
                },
                # Formato para editor de fluxos
                'fluxo_format': {
                    'id': componente.id,
                    'type': componente.tipo,
                    'name': componente.nome,
                    'desc': componente.descricao,
                    'icon': componente.icone,
                    'color': componente.cor,
                    'x': 100,
                    'y': 100,
                    'connections': []
                }
            }
            
            return jsonify({
                'success': True,
                'componente': detalhes
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao obter detalhes do componente {componente_id}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/componentes/shared/salvar', methods=['POST'])
    @login_required
    def api_salvar_componente():
        """API para salvar/atualizar componente (usado por ambos editores)"""
        try:
            dados = request.json
            
            # Verificar se é atualização ou criação
            componente_id = dados.get('id')
            if componente_id:
                # Atualização
                componente = ComponenteEditor.query.get_or_404(componente_id)
                operacao = 'atualizado'
            else:
                # Criação
                componente = ComponenteEditor()
                db.session.add(componente)
                operacao = 'criado'
            
            # Atualizar campos básicos
            componente.nome = dados.get('nome', componente.nome)
            componente.categoria = dados.get('categoria', componente.categoria)
            componente.tipo = dados.get('tipo', componente.tipo)
            componente.descricao = dados.get('descricao', componente.descricao)
            componente.descricao_detalhada = dados.get('descricao_detalhada', componente.descricao_detalhada)
            componente.icone = dados.get('icone', componente.icone)
            componente.cor = dados.get('cor', componente.cor)
            componente.ativo = dados.get('ativo', True)
            
            # Configurações específicas
            if 'configuracao' in dados:
                componente.configuracao = dados['configuracao']
            if 'parametros' in dados:
                componente.parametros = dados['parametros']
            if 'capacidades' in dados:
                componente.capacidades = dados['capacidades']
                
            # Prompts
            componente.prompt_sistema = dados.get('prompt_sistema', componente.prompt_sistema)
            componente.prompt_usuario = dados.get('prompt_usuario', componente.prompt_usuario)
            componente.base_conhecimento = dados.get('base_conhecimento', componente.base_conhecimento)
            
            # Configurações de IA
            if 'config_ia' in dados:
                config_ia = dados['config_ia']
                componente.temperatura = config_ia.get('temperatura', componente.temperatura)
                componente.max_tokens = config_ia.get('max_tokens', componente.max_tokens)
                componente.top_k = config_ia.get('top_k', componente.top_k)
                componente.chunk_size = config_ia.get('chunk_size', componente.chunk_size)
                componente.chunk_overlap = config_ia.get('chunk_overlap', componente.chunk_overlap)
            
            # Atualizar timestamp
            componente.atualizado_em = datetime.datetime.utcnow()
            
            # Salvar no banco
            db.session.commit()
            
            app.logger.info(f"✅ Componente {operacao}: {componente.nome} (ID: {componente.id})")
            
            return jsonify({
                'success': True,
                'message': f'Componente {operacao} com sucesso!',
                'componente': {
                    'id': componente.id,
                    'nome': componente.nome,
                    'categoria': componente.categoria,
                    'tipo': componente.tipo
                }
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao salvar componente: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/componentes/shared/categorias', methods=['GET'])
    @login_required
    def api_categorias_componentes():
        """API para listar todas as categorias de componentes"""
        try:
            # Buscar categorias distintas com contagem
            categorias_query = db.session.query(
                ComponenteEditor.categoria,
                func.count(ComponenteEditor.id).label('total'),
                func.count(ComponenteEditor.id).filter(ComponenteEditor.ativo == True).label('ativos')
            ).filter(
                ComponenteEditor.categoria.is_not(None)
            ).group_by(
                ComponenteEditor.categoria
            ).order_by(
                ComponenteEditor.categoria
            ).all()
            
            # Definir cores por categoria
            cores_categorias = {
                'extrator': '#28a745',
                'classificador': '#17a2b8',
                'analisador': '#6f42c1',
                'processador': '#fd7e14',
                'especialista': '#dc3545',
                'transformador': '#e98132',
                'gerador': '#36bf9c',
                'agregador': '#1175e5',
                'conector': '#6d47b3',
                'validador': '#e83e8c',
                'otimizador': '#ffc107'
            }
            
            # Definir ícones por categoria
            icones_categorias = {
                'extrator': 'fas fa-file-export',
                'classificador': 'fas fa-filter',
                'analisador': 'fas fa-search',
                'processador': 'fas fa-cogs',
                'especialista': 'fas fa-user-tie',
                'transformador': 'fas fa-exchange-alt',
                'gerador': 'fas fa-magic',
                'agregador': 'fas fa-layer-group',
                'conector': 'fas fa-plug',
                'validador': 'fas fa-check-circle',
                'otimizador': 'fas fa-rocket'
            }
            
            categorias = []
            for categoria, total, ativos in categorias_query:
                categorias.append({
                    'nome': categoria,
                    'total': total,
                    'ativos': ativos,
                    'cor': cores_categorias.get(categoria, '#6c757d'),
                    'icone': icones_categorias.get(categoria, 'fas fa-cog')
                })
            
            return jsonify({
                'success': True,
                'categorias': categorias,
                'total_categorias': len(categorias)
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao listar categorias: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'categorias': []
            }), 500

    # ===== PÁGINAS DE CONFIGURAÇÃO =====
    
    @app.route('/componentes-editor/<int:componente_id>/configurar')
    @login_required
    def configurar_componente(componente_id):
        """Página para configurar um componente específico"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Determinar template específico baseado na categoria
            templates_categoria = {
                'extrator': {
                    'extrator_texto': 'componentes_editor/extrator_texto.html',
                    'extrator_entidades': 'componentes_editor/extrator_entidades.html',
                    'extrator_pdf': 'componentes_editor/extrator_texto.html'
                },
                'analisador': {
                    'analisador_sentimento': 'componentes_editor/analisador_sentimento.html'
                },
                'processador': {
                    'processador_documentos': 'componentes_editor/processador_documentos.html'
                }
            }
            
            # Selecionar template apropriado
            template_path = 'componentes_editor/configuracao_generica.html'  # template padrão
            
            if componente.categoria in templates_categoria:
                categoria_templates = templates_categoria[componente.categoria]
                if componente.tipo in categoria_templates:
                    template_path = categoria_templates[componente.tipo]
                elif f"{componente.categoria}_{componente.nome.lower().replace(' ', '_')}" in categoria_templates:
                    template_path = categoria_templates[f"{componente.categoria}_{componente.nome.lower().replace(' ', '_')}"]
            
            app.logger.info(f"📝 Configurando componente {componente.nome} usando template: {template_path}")
            
            return render_template(template_path, 
                                 componente=componente,
                                 titulo=f"Configurar {componente.nome}")
                                 
        except Exception as e:
            app.logger.error(f"Erro ao carregar página de configuração: {str(e)}")
            flash('Erro ao carregar configuração do componente', 'error')
            return redirect(url_for('componentes_editor'))

    @app.route('/fluxos/editor/<int:fluxo_id>/componente/<int:componente_id>')
    @login_required
    def fluxo_configurar_componente(fluxo_id, componente_id):
        """Configurar componente dentro do contexto de um fluxo específico"""
        try:
            fluxo = FluxoModel.query.get_or_404(fluxo_id)
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Template baseado no tipo do componente
            if componente.tipo == 'extrator_texto':
                template = 'componentes_editor/extrator_texto.html'
            elif componente.tipo == 'extrator_entidades':
                template = 'componentes_editor/extrator_entidades.html'
            elif componente.tipo == 'analisador_sentimento':
                template = 'componentes_editor/analisador_sentimento.html'
            elif componente.tipo == 'processador_documentos':
                template = 'componentes_editor/processador_documentos.html'
            else:
                template = 'componentes_editor/configuracao_generica.html'
            
            return render_template(template, 
                                 componente=componente, 
                                 fluxo=fluxo,
                                 contexto='fluxo_editor',
                                 titulo=f"Configurar {componente.nome} - Fluxo {fluxo.nome}")
                                 
        except Exception as e:
            app.logger.error(f"Erro ao configurar componente no fluxo: {str(e)}")
            flash('Erro ao configurar componente', 'error')
            return redirect(url_for('fluxos_editor', fluxo_id=fluxo_id))

    # ===== SINCRONIZAÇÃO ENTRE EDITORES =====
    
    @app.route('/api/componentes/sync/fluxo-to-editor', methods=['POST'])
    @login_required
    def sincronizar_fluxo_para_editor():
        """Sincroniza componentes do editor de fluxos para o editor de componentes"""
        try:
            dados = request.json
            fluxo_id = dados.get('fluxo_id')
            componentes_fluxo = dados.get('componentes', [])
            
            if not fluxo_id:
                return jsonify({'success': False, 'error': 'ID do fluxo não fornecido'}), 400
            
            fluxo = FluxoModel.query.get_or_404(fluxo_id)
            componentes_criados = []
            
            for comp_data in componentes_fluxo:
                # Verificar se componente já existe
                componente_existente = ComponenteEditor.query.filter_by(
                    nome=comp_data['name'],
                    tipo=comp_data['type']
                ).first()
                
                if not componente_existente:
                    # Criar novo componente
                    novo_componente = ComponenteEditor(
                        nome=comp_data['name'],
                        categoria=comp_data.get('category', comp_data['type']),
                        tipo=comp_data['type'],
                        descricao=comp_data.get('desc', ''),
                        icone=comp_data.get('icon', 'fas fa-cog'),
                        cor=comp_data.get('color', '#47b6b5'),
                        configuracao={'origem': 'fluxo', 'fluxo_id': fluxo_id}
                    )
                    
                    db.session.add(novo_componente)
                    componentes_criados.append(novo_componente.nome)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{len(componentes_criados)} componentes sincronizados',
                'componentes_criados': componentes_criados
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro na sincronização fluxo->editor: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/componentes/sync/editor-to-fluxo', methods=['POST'])
    @login_required
    def sincronizar_editor_para_fluxo():
        """Disponibiliza componentes do editor para uso em fluxos"""
        try:
            componente_id = request.json.get('componente_id')
            if not componente_id:
                return jsonify({'success': False, 'error': 'ID do componente não fornecido'}), 400
            
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Formato compatível com editor de fluxos
            componente_fluxo = {
                'id': componente.id,
                'type': componente.tipo,
                'name': componente.nome,
                'desc': componente.descricao,
                'category': componente.categoria,
                'icon': componente.icone,
                'color': componente.cor,
                'capabilities': componente.capacidades or [],
                'parameters': componente.parametros or {},
                'configuration': componente.configuracao or {}
            }
            
            return jsonify({
                'success': True,
                'componente': componente_fluxo,
                'message': f'Componente {componente.nome} pronto para uso em fluxos'
            })
            
        except Exception as e:
            app.logger.error(f"Erro na sincronização editor->fluxo: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===== SINCRONIZAÇÃO FLUXO PARA BIBLIOTECA =====
    
    @app.route('/api/fluxos/sync-to-library/<int:fluxo_id>', methods=['POST'])
    @login_required 
    def sync_fluxo_to_library(fluxo_id):
        """Sincroniza componentes de um fluxo para a biblioteca de componentes"""
        try:
            # Buscar o fluxo
            fluxo = Fluxo.query.get_or_404(fluxo_id)
            
            # Parse dos agentes do fluxo
            agentes = fluxo.agentes if isinstance(fluxo.agentes, list) else json.loads(fluxo.agentes or '[]')
            
            componentes_criados = []
            componentes_existentes = []
            
            for agente in agentes:
                nome_componente = agente.get('config', {}).get('titulo', f"Componente {agente.get('id', 'sem_id')}")
                
                # Verificar se já existe
                existe = ComponenteEditor.query.filter_by(nome=nome_componente).first()
                if existe:
                    componentes_existentes.append(nome_componente)
                    continue
                
                # Mapear tipo para categoria
                tipo = agente.get('tipo', 'processamento')
                categoria_map = {
                    'entrada': 'Extração',
                    'extrator': 'Extração', 
                    'classificador': 'Classificação',
                    'analisador': 'Análise',
                    'especialista': 'Especialização',
                    'transformador': 'Transformação',
                    'gerador': 'Geração',
                    'agregador': 'Agregação',
                    'conector': 'Conexão',
                    'saida': 'Geração'
                }
                
                categoria = categoria_map.get(tipo, 'Processamento')
                
                # Mapear cor por tipo
                cor_map = {
                    'entrada': '#47b6b5',
                    'extrator': '#20597f',
                    'classificador': '#fec208', 
                    'analisador': '#17a2b7',
                    'especialista': '#c4414f',
                    'transformador': '#e98132',
                    'gerador': '#36bf9c',
                    'agregador': '#1175e5',
                    'conector': '#6d47b3',
                    'saida': '#47b6b5'
                }
                
                cor = cor_map.get(tipo, '#47b6b5')
                
                # Mapear ícone por tipo
                icone_map = {
                    'entrada': 'fas fa-sign-in-alt',
                    'extrator': 'fas fa-file-text',
                    'classificador': 'fas fa-tags',
                    'analisador': 'fas fa-search',
                    'especialista': 'fas fa-user-tie',
                    'transformador': 'fas fa-exchange-alt',
                    'gerador': 'fas fa-file-plus',
                    'agregador': 'fas fa-layer-group',
                    'conector': 'fas fa-plug',
                    'saida': 'fas fa-file-export'
                }
                
                icone = icone_map.get(tipo, 'fas fa-cog')
                
                # Criar componente
                novo_componente = ComponenteEditor(
                    nome=nome_componente,
                    categoria=categoria,
                    tipo=tipo,
                    descricao=agente.get('config', {}).get('descricao', f'Componente {tipo} do fluxo'),
                    descricao_detalhada=f"Componente originado do fluxo '{fluxo.nome}' - {agente.get('config', {}).get('descricao', 'Processamento especializado')}",
                    icone=icone,
                    cor=cor,
                    ativo=True,
                    configuracao={
                        'origem': 'fluxo',
                        'fluxo_id': fluxo_id,
                        'agente_id': agente.get('id'),
                        'sincronizado_em': datetime.now().isoformat(),
                        'posicao_original': agente.get('posicao', {})
                    },
                    prompt_sistema=f'Você é um componente {tipo} especializado importado do fluxo {fluxo.nome}',
                    prompt_usuario=f'Execute a função de {tipo} conforme configurado no fluxo',
                    capacidades=[tipo, 'fluxo_integrado', categoria.lower()],
                    parametros=agente.get('config', {}),
                    base_conhecimento='direito_brasileiro',
                    temperatura=0.3,
                    max_tokens=4000,
                    top_k=4,
                    chunk_size=1000,
                    chunk_overlap=200
                )
                
                db.session.add(novo_componente)
                componentes_criados.append({
                    'nome': nome_componente,
                    'categoria': categoria,
                    'tipo': tipo,
                    'cor': cor
                })
            
            # Commit das mudanças
            if componentes_criados:
                db.session.commit()
                
            return jsonify({
                'success': True,
                'message': f'Sincronização concluída! {len(componentes_criados)} componentes criados.',
                'fluxo': {
                    'id': fluxo.id,
                    'nome': fluxo.nome,
                    'descricao': fluxo.descricao
                },
                'componentes_criados': componentes_criados,
                'componentes_existentes': componentes_existentes,
                'total_agentes_fluxo': len(agentes)
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro na sincronização fluxo->biblioteca: {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e),
                'message': 'Erro ao sincronizar componentes do fluxo'
            }), 500
    
    @app.route('/api/fluxos/sync-status/<int:fluxo_id>')
    @login_required
    def check_sync_status(fluxo_id):
        """Verifica status de sincronização de um fluxo"""
        try:
            fluxo = Fluxo.query.get_or_404(fluxo_id)
            agentes = fluxo.agentes if isinstance(fluxo.agentes, list) else json.loads(fluxo.agentes or '[]')
            
            status_componentes = []
            for agente in agentes:
                nome_componente = agente.get('config', {}).get('titulo', f"Componente {agente.get('id', 'sem_id')}")
                existe = ComponenteEditor.query.filter_by(nome=nome_componente).first()
                
                status_componentes.append({
                    'nome': nome_componente,
                    'tipo': agente.get('tipo'),
                    'sincronizado': bool(existe),
                    'id_biblioteca': existe.id if existe else None
                })
            
            total_sincronizados = sum(1 for comp in status_componentes if comp['sincronizado'])
            
            return jsonify({
                'success': True,
                'fluxo': {
                    'id': fluxo.id,
                    'nome': fluxo.nome
                },
                'total_componentes': len(status_componentes),
                'total_sincronizados': total_sincronizados,
                'componentes': status_componentes,
                'percentual_sincronizado': round((total_sincronizados / len(status_componentes)) * 100) if status_componentes else 0
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao verificar status de sincronização: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===== ESTATÍSTICAS E MONITORAMENTO =====
    
    @app.route('/api/componentes/shared/estatisticas')
    @login_required
    def estatisticas_componentes():
        """Estatísticas de uso dos componentes compartilhados"""
        try:
            # Contagem total por categoria
            stats_categoria = db.session.query(
                ComponenteEditor.categoria,
                func.count(ComponenteEditor.id).label('total')
            ).group_by(ComponenteEditor.categoria).all()
            
            # Componentes mais usados (simulado - implementar tracking real)
            componentes_populares = ComponenteEditor.query.filter_by(ativo=True).limit(5).all()
            
            # Total geral
            total_componentes = ComponenteEditor.query.filter_by(ativo=True).count()
            total_categorias = db.session.query(ComponenteEditor.categoria).distinct().count()
            
            return jsonify({
                'success': True,
                'estatisticas': {
                    'total_componentes': total_componentes,
                    'total_categorias': total_categorias,
                    'por_categoria': [
                        {'categoria': cat, 'total': total} 
                        for cat, total in stats_categoria
                    ],
                    'mais_usados': [
                        {
                            'id': comp.id,
                            'nome': comp.nome,
                            'categoria': comp.categoria,
                            'uso_simulado': 100 - (comp.id * 10)  # Placeholder
                        } 
                        for comp in componentes_populares
                    ]
                }
            })
            
        except Exception as e:
            app.logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    app.logger.info("✅ Rotas de integração de componentes configuradas com sucesso")