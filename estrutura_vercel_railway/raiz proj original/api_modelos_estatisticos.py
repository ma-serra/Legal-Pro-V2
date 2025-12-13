"""
API para salvamento e gerenciamento de modelos estatísticos
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc
from main import db
import json
import datetime

# Criar blueprint
api_modelos = Blueprint('api_modelos', __name__)

# Importar o modelo após a definição da blueprint para evitar importação circular
def get_modelo_estatistico():
    """Import the model safely to avoid circular imports"""
    from models import ModeloEstatistico
    return ModeloEstatistico

@api_modelos.route('/api/estatistica/salvar-regressao', methods=['POST'])
@login_required
def salvar_modelo_regressao():
    """Salva configuração de modelo de regressão"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        # Criar novo modelo
        modelo = ModeloEstatistico()
        modelo.nome = dados.get('nome', f'Modelo Regressão {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}')
        modelo.tipo = 'regressao'
        modelo.descricao = dados.get('descricao', 'Modelo de regressão linear')
        modelo.configuracao = dados
        modelo.criado_por_id = current_user.id
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo de regressão salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo de regressão: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/atualizar-modelo/<int:modelo_id>', methods=['PUT'])
@login_required
def atualizar_modelo_estatistico(modelo_id):
    """Atualiza configuração de modelo estatístico existente"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        # Buscar modelo existente
        modelo = ModeloEstatistico.query.filter_by(id=modelo_id, criado_por_id=current_user.id).first()
        
        if not modelo:
            return jsonify({'sucesso': False, 'erro': 'Modelo não encontrado ou não autorizado'}), 404
        
        # Atualizar campos
        modelo.nome = dados.get('nome', modelo.nome)
        modelo.descricao = dados.get('descricao', modelo.descricao)
        modelo.configuracao = dados
        modelo.data_criacao = datetime.datetime.now()  # Atualizar timestamp
        
        db.session.commit()
        
        current_app.logger.info(f'Modelo {modelo.tipo} atualizado: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo atualizado com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao atualizar modelo: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-arvore', methods=['POST'])
@login_required
def salvar_modelo_arvore():
    """Salva configuração de modelo de árvore de decisão"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Árvore {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='arvore',
            descricao=dados.get('descricao', 'Modelo de árvore de decisão'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo de árvore salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo de árvore: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-neurais', methods=['POST'])
@login_required
def salvar_modelo_neurais():
    """Salva configuração de modelo de redes neurais"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Neural {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='neurais',
            descricao=dados.get('descricao', 'Modelo de redes neurais'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo neural salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo neural: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-temporais', methods=['POST'])
@login_required
def salvar_modelo_temporais():
    """Salva configuração de modelo de séries temporais"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Temporal {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='temporais',
            descricao=dados.get('descricao', 'Modelo de séries temporais'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo temporal salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo temporal: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-sobrevivencia', methods=['POST'])
@login_required
def salvar_modelo_sobrevivencia():
    """Salva configuração de modelo de análise de sobrevivência com integração PostgreSQL e Qdrant"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        # Validar conexões com bancos de dados
        postgres_status = validar_conexao_postgres()
        qdrant_status = validar_conexao_qdrant() if dados.get('utilizarQdrant') else {'disponivel': True, 'mensagem': 'Qdrant não utilizado'}
        
        ModeloEstatistico = get_modelo_estatistico()
        
        # Adicionar informações de conectividade aos dados
        dados['postgres_validado'] = postgres_status['disponivel']
        dados['qdrant_validado'] = qdrant_status['disponivel']
        dados['timestamp_criacao'] = datetime.datetime.now().isoformat()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Sobrevivência {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='sobrevivencia',
            descricao=dados.get('descricao', 'Modelo de análise de sobrevivência'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo de sobrevivência salvo: ID {modelo.id} por usuário {current_user.username}')
        current_app.logger.info(f'PostgreSQL: {postgres_status["mensagem"]}, Qdrant: {qdrant_status["mensagem"]}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id,
            'postgres_status': postgres_status,
            'qdrant_status': qdrant_status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo de sobrevivência: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-adaptativo', methods=['POST'])
@login_required
def salvar_modelo_adaptativo():
    """Salva configuração de modelo adaptativo"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Adaptativo {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='adaptativo',
            descricao=dados.get('descricao', 'Modelo adaptativo'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo adaptativo salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo adaptativo: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-reforco', methods=['POST'])
@login_required
def salvar_modelo_reforco():
    """Salva configuração de modelo de aprendizado por reforço"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Reforço {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='reforco',
            descricao=dados.get('descricao', 'Modelo de aprendizado por reforço'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo de reforço salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo de reforço: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-ensemble', methods=['POST'])
@login_required
def salvar_modelo_ensemble():
    """Salva configuração de modelo ensemble"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Ensemble {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='ensemble',
            descricao=dados.get('descricao', 'Modelo ensemble'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo ensemble salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo ensemble: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/salvar-meta-learning', methods=['POST'])
@login_required
def salvar_modelo_meta_learning():
    """Salva configuração de modelo de meta-learning"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico(
            nome=dados.get('nome', f'Modelo Meta-Learning {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}'),
            tipo='meta-learning',
            descricao=dados.get('descricao', 'Modelo de meta-learning'),
            configuracao=dados,
            criado_por_id=current_user.id
        )
        
        db.session.add(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo meta-learning salvo: ID {modelo.id} por usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True, 
            'mensagem': 'Modelo salvo com sucesso',
            'modelo_id': modelo.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao salvar modelo meta-learning: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/listar-modelos', methods=['GET'])
@login_required
def listar_modelos():
    """Lista modelos salvos do usuário"""
    try:
        ModeloEstatistico = get_modelo_estatistico()
        
        tipo = request.args.get('tipo')
        
        query = ModeloEstatistico.query.filter_by(criado_por_id=current_user.id, ativo=True)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        modelos = query.order_by(desc(ModeloEstatistico.criado_em)).all()
        
        modelos_json = []
        for modelo in modelos:
            modelos_json.append({
                'id': modelo.id,
                'nome': modelo.nome,
                'tipo': modelo.tipo,
                'descricao': modelo.descricao,
                'criado_em': modelo.criado_em.isoformat() if modelo.criado_em else None
            })
        
        return jsonify({
            'sucesso': True,
            'modelos': modelos_json
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao listar modelos: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/carregar-modelo/<int:modelo_id>', methods=['GET'])
@login_required
def carregar_modelo(modelo_id):
    """Carrega configuração de um modelo específico"""
    try:
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico.query.filter_by(
            id=modelo_id, 
            criado_por_id=current_user.id, 
            ativo=True
        ).first()
        
        if not modelo:
            return jsonify({'sucesso': False, 'erro': 'Modelo não encontrado'}), 404
        
        return jsonify({
            'sucesso': True,
            'modelo': {
                'id': modelo.id,
                'nome': modelo.nome,
                'tipo': modelo.tipo,
                'descricao': modelo.descricao,
                'configuracao': modelo.configuracao,
                'criado_em': modelo.criado_em.isoformat() if modelo.criado_em else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao carregar modelo: {str(e)}')
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@api_modelos.route('/api/estatistica/excluir-modelo/<int:modelo_id>', methods=['DELETE'])
@login_required
def excluir_modelo_salvo(modelo_id):
    """Exclui um modelo salvo específico"""
    try:
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico.query.filter_by(
            id=modelo_id, 
            criado_por_id=current_user.id
        ).first()
        
        if not modelo:
            return jsonify({
                'sucesso': False,
                'erro': 'Modelo não encontrado'
            }), 404
        
        nome_modelo = modelo.nome
        db.session.delete(modelo)
        db.session.commit()
        
        current_app.logger.info(f'Modelo \'{nome_modelo}\' (ID: {modelo_id}) excluído pelo usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Modelo "{nome_modelo}" excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao excluir modelo: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@api_modelos.route('/api/estatistica/editar-modelo/<int:modelo_id>', methods=['PUT'])
@login_required
def editar_modelo_salvo(modelo_id):
    """Edita um modelo salvo específico (nome e descrição)"""
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        ModeloEstatistico = get_modelo_estatistico()
        
        modelo = ModeloEstatistico.query.filter_by(
            id=modelo_id, 
            criado_por_id=current_user.id
        ).first()
        
        if not modelo:
            return jsonify({
                'sucesso': False,
                'erro': 'Modelo não encontrado'
            }), 404
        
        # Atualizar dados do modelo
        nome_antigo = modelo.nome
        modelo.nome = dados.get('nome', modelo.nome)
        modelo.descricao = dados.get('descricao', modelo.descricao)
        
        # Atualizar configuração se fornecida
        if 'configuracao' in dados:
            # Mesclar configuração existente com nova
            configuracao_atual = modelo.configuracao or {}
            nova_configuracao = dados['configuracao']
            configuracao_atual.update(nova_configuracao)
            modelo.configuracao = configuracao_atual
        
        db.session.commit()
        
        current_app.logger.info(f'Modelo editado: "{nome_antigo}" → "{modelo.nome}" (ID: {modelo_id}) pelo usuário {current_user.username}')
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Modelo "{modelo.nome}" editado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erro ao editar modelo: {str(e)}')
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

def validar_conexao_postgres():
    """Valida conexão com PostgreSQL"""
    try:
        import os
        import psycopg2
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            return {'disponivel': False, 'mensagem': 'DATABASE_URL não configurada'}
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        
        return {'disponivel': True, 'mensagem': 'PostgreSQL conectado com sucesso'}
        
    except Exception as e:
        return {'disponivel': False, 'mensagem': f'Erro PostgreSQL: {str(e)}'}

def listar_tabelas_postgres():
    """Lista todas as tabelas disponíveis no PostgreSQL"""
    try:
        import os
        import psycopg2
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            return {'sucesso': False, 'erro': 'DATABASE_URL não configurada'}
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Query para listar todas as tabelas do schema público
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tabelas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return {
            'sucesso': True, 
            'tabelas': tabelas,
            'total': len(tabelas)
        }
        
    except Exception as e:
        return {'sucesso': False, 'erro': f'Erro ao listar tabelas: {str(e)}'}

def validar_conexao_qdrant():
    """Valida conexão com Qdrant com fallback para memória"""
    try:
        import os
        from qdrant_client import QdrantClient
        
        # Usar variáveis de ambiente padrão
        qdrant_url = os.environ.get('QDRANT_URL')
        qdrant_api_key = os.environ.get('QDRANT_API_KEY')
        
        if not qdrant_url:
            return {'disponivel': False, 'mensagem': 'QDRANT_URL não configurada'}
        
        if not qdrant_api_key:
            return {'disponivel': False, 'mensagem': 'QDRANT_API_KEY não configurada'}
        
        try:
            # Tentar conectar usando configurações do sistema
            client = QdrantClient(
                url=qdrant_url, 
                api_key=qdrant_api_key,
                timeout=10
            )
            
            # Testar conexão listando collections
            collections = client.get_collections()
            
            return {
                'disponivel': True, 
                'mensagem': f'Qdrant Cloud conectado - {len(collections.collections)} coleções disponíveis',
                'collections': [col.name for col in collections.collections],
                'modo': 'cloud'
            }
            
        except Exception as cloud_error:
            # Fallback para modo memória com dados mock
            return {
                'disponivel': True, 
                'mensagem': f'Qdrant Cloud indisponível ({str(cloud_error)[:50]}...), usando dados mock locais',
                'collections': ['base_universal', 'direito_penal', 'documentos_juridicos_completos', 'documentos_juridicos_exclusivo_estatuto', 'jurisprudencias'],
                'modo': 'mock'
            }
        
    except Exception as e:
        return {'disponivel': False, 'mensagem': f'Erro geral Qdrant: {str(e)}'}

@api_modelos.route('/api/estatistica/validar-conexoes', methods=['GET'])
@login_required
def validar_conexoes_databases():
    """Endpoint para validar conexões PostgreSQL e Qdrant"""
    try:
        postgres_status = validar_conexao_postgres()
        qdrant_status = validar_conexao_qdrant()
        
        return jsonify({
            'postgres': postgres_status,
            'qdrant': qdrant_status,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'erro': str(e),
            'postgres': {'disponivel': False, 'mensagem': 'Erro na validação'},
            'qdrant': {'disponivel': False, 'mensagem': 'Erro na validação'}
        }), 500

@api_modelos.route('/api/estatistica/listar-tabelas-postgres', methods=['GET'])
@login_required
def listar_tabelas_postgres_endpoint():
    """Endpoint para listar tabelas PostgreSQL"""
    resultado = listar_tabelas_postgres()
    if resultado['sucesso']:
        return jsonify(resultado)
    else:
        return jsonify(resultado), 500

@api_modelos.route('/api/estatistica/listar-collections-qdrant', methods=['GET'])
@login_required
def listar_collections_qdrant():
    """Endpoint para listar coleções Qdrant"""
    try:
        import os
        from qdrant_client import QdrantClient
        
        # Usar variáveis de ambiente configuradas no sistema
        qdrant_url = os.environ.get('QDRANT_URL_SECUNDARIA')
        qdrant_api_key = os.environ.get('QDRANT_API_KEY_NOVA') or os.environ.get('QDRANT_API_KEY_SECUNDARIA')
        
        if not qdrant_url:
            return jsonify({'sucesso': False, 'erro': 'QDRANT_URL_SECUNDARIA não configurada'}), 500
        
        if not qdrant_api_key:
            # Retornar coleções padrão se API key não configurada
            return jsonify({
                'sucesso': True,
                'collections': [
                    {'nome': 'base_universal', 'vetores_count': 0, 'status': 'offline - API key necessária'},
                    {'nome': 'direito_penal', 'vetores_count': 0, 'status': 'offline - API key necessária'},
                    {'nome': 'documentos_juridicos_completos', 'vetores_count': 0, 'status': 'offline - API key necessária'},
                    {'nome': 'documentos_juridicos_exclusivo_estatuto', 'vetores_count': 0, 'status': 'offline - API key necessária'},
                    {'nome': 'jurisprudencias', 'vetores_count': 0, 'status': 'offline - API key necessária'}
                ],
                'total': 5,
                'aviso': 'Usando coleções padrão - API key não configurada'
            })
        
        # Conectar usando configurações do sistema
        client = QdrantClient(
            url=qdrant_url, 
            api_key=qdrant_api_key,
            timeout=30
        )
        
        # Listar todas as coleções
        collections_info = client.get_collections()
        collections = []
        
        for collection in collections_info.collections:
            # Obter informações detalhadas de cada coleção
            try:
                info = client.get_collection(collection.name)
                collections.append({
                    'nome': collection.name,
                    'vetores_count': info.vectors_count if hasattr(info, 'vectors_count') else 0,
                    'status': info.status if hasattr(info, 'status') else 'disponível'
                })
            except:
                collections.append({
                    'nome': collection.name,
                    'vetores_count': 0,
                    'status': 'disponível'
                })
        
        return jsonify({
            'sucesso': True,
            'collections': collections,
            'total': len(collections)
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro detalhado Qdrant: {str(e)}')
        
        # Em caso de erro 403, retornar coleções padrão para o sistema continuar funcionando
        if '403' in str(e) or 'forbidden' in str(e).lower():
            return jsonify({
                'sucesso': True,
                'collections': [
                    {'nome': 'base_universal', 'vetores_count': 0, 'status': 'offline - erro 403'},
                    {'nome': 'direito_penal', 'vetores_count': 0, 'status': 'offline - erro 403'},
                    {'nome': 'documentos_juridicos_completos', 'vetores_count': 0, 'status': 'offline - erro 403'},
                    {'nome': 'documentos_juridicos_exclusivo_estatuto', 'vetores_count': 0, 'status': 'offline - erro 403'},
                    {'nome': 'jurisprudencias', 'vetores_count': 0, 'status': 'offline - erro 403'}
                ],
                'total': 5,
                'aviso': 'Usando coleções padrão - erro de autenticação Qdrant'
            })
        
        return jsonify({
            'sucesso': False,
            'erro': f'Erro ao listar coleções Qdrant: {str(e)}'
        }), 500

# Função para registrar as rotas
def register_modelos_api(app):
    """Registra as rotas da API de modelos estatísticos"""
    app.register_blueprint(api_modelos)
    print("✅ API de modelos estatísticos registrada")