"""
Rotas para o sistema de gestão de componentes do editor de fluxos.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import ComponenteEditor
from main import db
import json
import datetime


def init_componentes_routes(app):
    """Inicializa as rotas do sistema de componentes do editor"""
    
    @app.route('/componentes-editor')
    @app.route('/componentes_editor')
    @login_required
    def componentes_editor():
        """Página principal do sistema de componentes do editor"""
        try:
            # Buscar todos os componentes agrupados por categoria
            componentes = ComponenteEditor.query.filter_by(ativo=True).order_by(
                ComponenteEditor.categoria, ComponenteEditor.nome
            ).all()
            
            # Agrupar por categoria
            componentes_por_categoria = {}
            for componente in componentes:
                categoria = componente.categoria
                if categoria not in componentes_por_categoria:
                    componentes_por_categoria[categoria] = []
                componentes_por_categoria[categoria].append(componente)
            
            # Estatísticas
            total_componentes = len(componentes)
            categorias_ativas = len(componentes_por_categoria)
            
            return render_template('componentes_editor/lista_real.html',
                                 componentes_por_categoria=componentes_por_categoria,
                                 total_componentes=total_componentes,
                                 categorias_ativas=categorias_ativas)
        
        except Exception as e:
            print(f"Erro ao carregar componentes do editor: {e}")
            flash('Erro ao carregar componentes do editor', 'error')
            return redirect(url_for('home'))

    # APIs para integração Canvas-Database
    @app.route('/componentes_editor/api/componentes', methods=['GET', 'POST'])
    @login_required
    def api_componentes():
        """API para gerenciar componentes via Canvas Editor"""
        if request.method == 'GET':
            # Listar todos os componentes
            try:
                componentes = ComponenteEditor.query.filter_by(ativo=True).all()
                return jsonify([{
                    'id': c.id,
                    'nome': c.nome,
                    'categoria': c.categoria,
                    'tipo': c.tipo,
                    'descricao': c.descricao,
                    'codigo_html': c.codigo_html,
                    'codigo_css': c.codigo_css,
                    'codigo_js': c.codigo_js,
                    'configuracao_visual': c.configuracao_visual,
                    'canvas_generated': getattr(c, 'canvas_generated', False),
                    'criado_em': c.criado_em.isoformat() if c.criado_em else None
                } for c in componentes])
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'POST':
            # Criar novo componente via Canvas
            try:
                data = request.json
                
                # Criar novo componente
                componente = ComponenteEditor(
                    nome=data.get('nome'),
                    categoria=data.get('categoria'),
                    tipo=data.get('tipo'),
                    descricao=data.get('descricao'),
                    codigo_html=data.get('codigo_html'),
                    codigo_css=data.get('codigo_css'),
                    codigo_js=data.get('codigo_js'),
                    configuracao_visual=data.get('configuracao_visual'),
                    cor='#007bff',
                    icone='fas fa-cube',
                    ativo=True,
                    capacidades=data.get('capacidades', []),
                    configuracao=data.get('configuracao', {}),
                    criado_em=datetime.datetime.now()
                )
                
                db.session.add(componente)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'id': componente.id,
                    'message': 'Componente criado com sucesso'
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/componentes_editor/api/layouts', methods=['GET', 'POST'])
    @login_required
    def api_layouts():
        """API para gerenciar layouts de design"""
        if request.method == 'POST':
            try:
                data = request.json
                
                # Salvar layout no cache ou banco (simplificado para localStorage)
                return jsonify({
                    'success': True,
                    'message': 'Layout salvo com sucesso',
                    'layout_id': f"layout_{datetime.datetime.now().timestamp()}"
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        elif request.method == 'GET':
            # Listar layouts salvos
            return jsonify({'layouts': []})  # Implementar conforme necessidade

    @app.route('/componentes_editor/<int:componente_id>')
    @app.route('/componentes-editor/<int:componente_id>')
    @login_required
    def ver_componente(componente_id):
        """Visualizar detalhes de um componente específico"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            return render_template('componentes_editor/detalhe.html',
                                 componente=componente)
        
        except Exception as e:
            print(f"Erro ao visualizar componente {componente_id}: {e}")
            flash('Erro ao carregar componente', 'error')
            return redirect(url_for('componentes_editor'))

    @app.route('/componentes_editor/<int:componente_id>/editar')
    @app.route('/componentes-editor/<int:componente_id>/editar')
    @login_required
    def editar_componente(componente_id):
        """Página de edição de componente"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            return render_template('componentes_editor/editar.html',
                                 componente=componente)
        
        except Exception as e:
            print(f"Erro ao carregar edição do componente {componente_id}: {e}")
            flash('Erro ao carregar edição do componente', 'error')
            return redirect(url_for('componentes_editor'))

    @app.route('/componentes_editor/<int:componente_id>/editar', methods=['POST'])
    @app.route('/componentes-editor/<int:componente_id>/editar', methods=['POST'])
    @login_required
    def salvar_componente(componente_id):
        """Salvar alterações de um componente"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Atualizar dados básicos
            componente.nome = request.form.get('nome', componente.nome)
            componente.descricao = request.form.get('descricao', componente.descricao)
            componente.descricao_detalhada = request.form.get('descricao_detalhada', componente.descricao_detalhada)
            componente.icone = request.form.get('icone', componente.icone)
            componente.cor = request.form.get('cor', componente.cor)
            componente.prompt_sistema = request.form.get('prompt_sistema', componente.prompt_sistema)
            componente.prompt_usuario = request.form.get('prompt_usuario', componente.prompt_usuario)
            componente.base_conhecimento = request.form.get('base_conhecimento', componente.base_conhecimento)
            componente.provedor = request.form.get('provedor', componente.provedor)
            componente.modelo = request.form.get('modelo', componente.modelo)
            
            # Atualizar parâmetros técnicos
            try:
                componente.temperatura = float(request.form.get('temperatura', 0.7))
                componente.max_tokens = int(request.form.get('max_tokens', 4000))
                componente.top_k = int(request.form.get('top_k', 5))
                componente.chunk_size = int(request.form.get('chunk_size', 1000))
                componente.chunk_overlap = int(request.form.get('chunk_overlap', 200))
            except (ValueError, TypeError):
                pass  # Manter valores padrão se conversão falhar
            
            # Atualizar capacidades (JSON)
            capacidades_text = request.form.get('capacidades', '[]')
            try:
                if capacidades_text.strip():
                    # Se for texto separado por vírgulas, converter para lista
                    if '[' not in capacidades_text:
                        capacidades = [cap.strip() for cap in capacidades_text.split(',') if cap.strip()]
                    else:
                        capacidades = json.loads(capacidades_text)
                    componente.capacidades = capacidades
            except json.JSONDecodeError:
                pass  # Manter capacidades existentes se JSON inválido
            
            # Atualizar parâmetros (JSON)
            parametros_text = request.form.get('parametros', '{}')
            try:
                if parametros_text.strip():
                    componente.parametros = json.loads(parametros_text)
            except json.JSONDecodeError:
                pass  # Manter parâmetros existentes se JSON inválido
            
            # Atualizar configuração (JSON)
            configuracao_text = request.form.get('configuracao', '{}')
            try:
                if configuracao_text.strip():
                    componente.configuracao = json.loads(configuracao_text)
            except json.JSONDecodeError:
                pass  # Manter configuração existente se JSON inválido
            
            # Atualizar timestamp
            componente.atualizado_em = datetime.datetime.utcnow()
            
            # Salvar no banco
            db.session.commit()
            
            flash(f'Componente "{componente.nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('ver_componente', componente_id=componente.id))
        
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar componente {componente_id}: {e}")
            flash(f'Erro ao salvar componente: {str(e)}', 'error')
            return redirect(url_for('editar_componente', componente_id=componente_id))

    @app.route('/componentes_editor/novo')
    @login_required
    def novo_componente():
        """Página para criar novo componente"""
        return render_template('componentes_editor/novo.html')

    @app.route('/componentes_editor/novo', methods=['POST'])
    @login_required
    def criar_componente():
        """Criar novo componente"""
        try:
            # Validar dados obrigatórios
            nome = request.form.get('nome', '').strip()
            categoria = request.form.get('categoria', '').strip()
            
            if not nome or not categoria:
                flash('Nome e categoria são obrigatórios', 'error')
                return redirect(url_for('novo_componente'))
            
            # Verificar se já existe componente com mesmo nome
            existe = ComponenteEditor.query.filter_by(nome=nome).first()
            if existe:
                flash(f'Já existe um componente com o nome "{nome}"', 'error')
                return redirect(url_for('novo_componente'))
            
            # Criar novo componente
            componente = ComponenteEditor(
                nome=nome,
                categoria=categoria,
                tipo=request.form.get('tipo', nome.lower().replace(' ', '_')),
                descricao=request.form.get('descricao', ''),
                descricao_detalhada=request.form.get('descricao_detalhada', ''),
                icone=request.form.get('icone', 'fas fa-cog'),
                cor=request.form.get('cor', '#47b6b5'),
                prompt_sistema=request.form.get('prompt_sistema', ''),
                prompt_usuario=request.form.get('prompt_usuario', ''),
                base_conhecimento=request.form.get('base_conhecimento', ''),
                provedor=request.form.get('provedor', 'openai'),
                modelo=request.form.get('modelo', 'gpt-4o'),
                temperatura=float(request.form.get('temperatura', 0.7)),
                max_tokens=int(request.form.get('max_tokens', 4000)),
                top_k=int(request.form.get('top_k', 5)),
                chunk_size=int(request.form.get('chunk_size', 1000)),
                chunk_overlap=int(request.form.get('chunk_overlap', 200)),
                ativo=request.form.get('ativo') == 'on',
                capacidades=[],
                parametros={},
                configuracao={}
            )
            
            # Processar capacidades
            capacidades_text = request.form.get('capacidades', '')
            if capacidades_text.strip():
                try:
                    if '[' not in capacidades_text:
                        capacidades = [cap.strip() for cap in capacidades_text.split(',') if cap.strip()]
                    else:
                        capacidades = json.loads(capacidades_text)
                    componente.capacidades = capacidades
                except json.JSONDecodeError:
                    pass
            
            # Processar parâmetros
            parametros_text = request.form.get('parametros', '')
            if parametros_text.strip():
                try:
                    componente.parametros = json.loads(parametros_text)
                except json.JSONDecodeError:
                    pass
            
            # Salvar no banco
            db.session.add(componente)
            db.session.commit()
            
            flash(f'Componente "{componente.nome}" criado com sucesso!', 'success')
            return redirect(url_for('ver_componente', componente_id=componente.id))
        
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar componente: {e}")
            flash(f'Erro ao criar componente: {str(e)}', 'error')
            return redirect(url_for('novo_componente'))

    @app.route('/componentes_editor/<int:componente_id>/toggle_ativo', methods=['POST'])
    @login_required
    def toggle_ativo_componente(componente_id):
        """Ativar/desativar componente"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            componente.ativo = not componente.ativo
            
            db.session.commit()
            
            status = "ativado" if componente.ativo else "desativado"
            flash(f'Componente "{componente.nome}" {status} com sucesso!', 'success')
            
            return jsonify({'success': True, 'ativo': componente.ativo})
        
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao alterar status do componente {componente_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/componentes_editor/<int:componente_id>/atualizar', methods=['POST'])
    @login_required
    def atualizar_componente(componente_id):
        """Atualizar componente"""
        try:
            componente = ComponenteEditor.query.get_or_404(componente_id)
            
            # Atualizar timestamp
            from datetime import datetime
            componente.atualizado_em = datetime.now()
            
            # Se houver configurações específicas para atualizar, adicione aqui
            # Por exemplo: recarregar capacidades, atualizar base de conhecimento, etc.
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Componente "{componente.nome}" atualizado com sucesso!'
            })
        
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar componente {componente_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/componentes-editor/api/buscar')
    @login_required
    def api_buscar_componentes():
        """API para buscar componentes (usado no editor de fluxos)"""
        try:
            categoria = request.args.get('categoria')
            termo = request.args.get('q', '').strip()
            
            query = ComponenteEditor.query.filter_by(ativo=True)
            
            if categoria:
                query = query.filter_by(categoria=categoria)
            
            if termo:
                query = query.filter(
                    ComponenteEditor.nome.ilike(f'%{termo}%') |
                    ComponenteEditor.descricao.ilike(f'%{termo}%')
                )
            
            componentes = query.order_by(ComponenteEditor.categoria, ComponenteEditor.nome).all()
            
            # Converter para formato JSON
            resultado = []
            for comp in componentes:
                resultado.append({
                    'id': comp.id,
                    'nome': comp.nome,
                    'categoria': comp.categoria,
                    'tipo': comp.tipo,
                    'descricao': comp.descricao,
                    'icone': comp.icone,
                    'cor': comp.cor,
                    'capacidades': comp.capacidades or [],
                    'base_conhecimento': comp.base_conhecimento
                })
            
            return jsonify(resultado)
        
        except Exception as e:
            print(f"Erro na API de busca de componentes: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/componentes_editor/popular', methods=['POST'])
    @login_required
    def popular_componentes_inicial():
        """Popular componentes iniciais no banco de dados"""
        try:
            # Verificar se já existem componentes
            count_existente = ComponenteEditor.query.count()
            if count_existente > 0:
                return jsonify({
                    'success': False, 
                    'message': f'Já existem {count_existente} componentes cadastrados.'
                })
            
            # Executar a população dos componentes
            from popular_componentes_editor import popular_componentes
            popular_componentes()
            
            return jsonify({
                'success': True,
                'message': 'Componentes populados com sucesso!'
            })
        
        except Exception as e:
            print(f"Erro ao popular componentes: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

def configurar_rotas_componentes(app):
    """Função de compatibilidade para configurar rotas de componentes"""
    return init_componentes_routes(app)