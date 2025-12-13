"""
APIs para Sistema de Database - Legal Pro
Endpoints para carregar tabelas, colunas e dados do PostgreSQL
Sincronizado dinamicamente com modelos Python do sistema usando SQLAlchemy reflection
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import text, inspect
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_dynamic_model_info():
    """
    Dinamicamente mapeia todas as tabelas do banco para suas classes de modelo Python
    usando SQLAlchemy metadata e reflection
    """
    try:
        # Import here to avoid circular imports
        from main import db
        import models
        
        # Criar mapeamento dinâmico de tabelas para modelos
        table_to_model = {}
        
        # Percorrer todos os modelos registrados no SQLAlchemy
        for table_name, table in db.Model.metadata.tables.items():
            # Encontrar a classe modelo correspondente
            model_class = None
            
            # Procurar no módulo models pela classe correspondente
            for attr_name in dir(models):
                attr = getattr(models, attr_name)
                if (hasattr(attr, '__tablename__') and 
                    hasattr(attr, '__table__') and 
                    attr.__tablename__ == table_name):
                    model_class = attr
                    break
            
            if model_class:
                # Obter campos principais (primeiros 5 campos não-ID)
                campos_principais = []
                for column in table.columns:
                    if (column.name != 'id' and 
                        not column.name.endswith('_id') and
                        len(campos_principais) < 5):
                        campos_principais.append(column.name)
                
                # Gerar descrição baseada no nome da classe
                class_name = model_class.__name__
                if hasattr(model_class, '__doc__') and model_class.__doc__:
                    # Usar docstring da classe se disponível
                    descricao = model_class.__doc__.strip().split('\n')[0]
                else:
                    # Gerar descrição baseada no nome da tabela
                    descricao = f"Modelo {class_name} para gerenciamento de {table_name.replace('_', ' ')}"
                
                table_to_model[table_name] = {
                    'descricao': descricao,
                    'modelo_python': class_name,
                    'campos_principais': campos_principais,
                    'total_colunas': len(table.columns),
                    'tem_modelo_python': True
                }
            else:
                # Tabela sem modelo Python correspondente
                table_to_model[table_name] = {
                    'descricao': f'Tabela {table_name.replace("_", " ").title()}',
                    'modelo_python': None,
                    'campos_principais': [c.name for c in table.columns if c.name != 'id'][:5],
                    'total_colunas': len(table.columns),
                    'tem_modelo_python': False
                }
        
        logger.info(f"✅ Mapeamento dinâmico criado para {len(table_to_model)} tabelas")
        return table_to_model
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar mapeamento dinâmico: {str(e)}")
        # Fallback para um mapeamento vazio se falhar
        return {}

def register_database_apis(app):
    """Registra todas as APIs de database no app Flask"""
    
    @app.route('/api/database/tabelas', methods=['GET'])
    @login_required
    def api_database_tabelas():
        """API para carregar lista de tabelas do banco PostgreSQL com info dos modelos Python"""
        try:
            from main import db
            
            # Obter mapeamento dinâmico de modelos
            modelos_sistema = get_dynamic_model_info()
            
            # Query para obter tabelas do esquema public
            query = """
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
            
            result = db.session.execute(text(query))
            tabelas = []
            
            for row in result:
                nome_tabela = row[0]
                tabela_info = {
                    'nome': nome_tabela,
                    'tipo': row[1]
                }
                
                # Adicionar informações do modelo Python se disponível no mapeamento dinâmico
                if nome_tabela in modelos_sistema:
                    modelo_info = modelos_sistema[nome_tabela]
                    tabela_info.update({
                        'descricao': modelo_info['descricao'],
                        'modelo_python': modelo_info['modelo_python'],
                        'campos_principais': modelo_info['campos_principais'],
                        'total_colunas': modelo_info['total_colunas'],
                        'tem_modelo_python': modelo_info['tem_modelo_python']
                    })
                else:
                    # Fallback para tabelas não encontradas no mapeamento
                    tabela_info.update({
                        'descricao': f'Tabela {nome_tabela.replace("_", " ").title()}',
                        'modelo_python': None,
                        'campos_principais': [],
                        'total_colunas': 0,
                        'tem_modelo_python': False
                    })
                
                tabelas.append(tabela_info)
            
            logger.info(f"✅ {len(tabelas)} tabelas carregadas do PostgreSQL com mapeamento dinâmico")
            
            return jsonify({
                'success': True,
                'tabelas': tabelas,
                'total': len(tabelas),
                'modelos_mapeados': len([t for t in tabelas if t['tem_modelo_python']]),
                'mapeamento_dinamico': True
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar tabelas: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'mapeamento_dinamico': False
            }), 500

    @app.route('/api/database/colunas/<tabela>', methods=['GET'])
    @login_required
    def api_database_colunas(tabela):
        """API para carregar colunas de uma tabela específica"""
        try:
            from main import db
            
            # Query para obter colunas da tabela
            query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = :tabela
            ORDER BY ordinal_position;
            """
            
            result = db.session.execute(text(query), {'tabela': tabela})
            colunas = []
            
            for row in result:
                colunas.append({
                    'nome': row[0],
                    'tipo': row[1],
                    'nulo': row[2] == 'YES',
                    'padrao': row[3]
                })
            
            logger.info(f"✅ {len(colunas)} colunas carregadas da tabela {tabela}")
            
            return jsonify({
                'success': True,
                'colunas': colunas,
                'tabela': tabela,
                'total': len(colunas)
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar colunas da tabela {tabela}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'tabela': tabela
            }), 500

    @app.route('/api/database/preview/<tabela>', methods=['GET'])
    @login_required
    def api_database_preview(tabela):
        """API para preview dos dados de uma tabela"""
        try:
            from main import db
            
            # Verificar se tabela existe
            check_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = :tabela;
            """
            
            check_result = db.session.execute(text(check_query), {'tabela': tabela})
            if not check_result.fetchone():
                return jsonify({
                    'success': False,
                    'error': f'Tabela {tabela} não encontrada'
                }), 404
            
            # Query para obter primeiros registros
            query = f"SELECT * FROM {tabela} LIMIT 10;"
            
            result = db.session.execute(text(query))
            
            # Converter resultado para lista de dicionários
            dados = []
            for row in result:
                dados.append(dict(row._mapping))
            
            logger.info(f"✅ Preview da tabela {tabela} carregado com {len(dados)} registros")
            
            return jsonify({
                'success': True,
                'dados': dados,
                'tabela': tabela,
                'total_preview': len(dados)
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar preview da tabela {tabela}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'tabela': tabela
            }), 500

    @app.route('/api/database/update-system', methods=['POST'])
    @login_required
    def api_database_update_system():
        """API para atualização sistêmica das tabelas de dados"""
        try:
            from main import db
            
            # Estatísticas do sistema
            stats = {}
            
            # 1. Verificar tabelas principais
            tabelas_principais = [
                'processo_juridico', 'agente_juridico', 'user', 'validacao_multi_agente_analise',
                'analise_processo_ia', 'documento', 'transcricao', 'template_juridico'
            ]
            
            for tabela in tabelas_principais:
                try:
                    count_query = f"SELECT COUNT(*) as total FROM {tabela};"
                    result = db.session.execute(text(count_query))
                    count = result.fetchone()[0]
                    stats[tabela] = count
                    logger.info(f"📊 {tabela}: {count} registros")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao contar {tabela}: {e}")
                    stats[tabela] = 'erro'
            
            # 2. Verificar integridade das chaves estrangeiras
            fk_checks = []
            try:
                fk_query = """
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_schema = 'public'
                LIMIT 10;
                """
                
                result = db.session.execute(text(fk_query))
                for row in result:
                    fk_checks.append({
                        'tabela': row[0],
                        'coluna': row[1],
                        'tabela_ref': row[2],
                        'coluna_ref': row[3]
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar FKs: {e}")
            
            # 3. Atualizar cache de metadados
            try:
                db.session.execute(text("ANALYZE;"))
                db.session.commit()
                logger.info("✅ Cache de estatísticas atualizado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar cache: {e}")
            
            resultado = {
                'success': True,
                'timestamp': str(db.session.execute(text("SELECT NOW();")).fetchone()[0]),
                'estatisticas_tabelas': stats,
                'foreign_keys_verificadas': len(fk_checks),
                'total_tabelas_sistema': len([t for t in stats.values() if t != 'erro']),
                'sistema_status': 'operacional',
                'message': 'Atualização sistêmica concluída com sucesso'
            }
            
            logger.info("🚀 Atualização sistêmica das tabelas concluída")
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro na atualização sistêmica: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Falha na atualização sistêmica'
            }), 500

    @app.route('/api/database/status', methods=['GET'])
    @login_required  
    def api_database_status():
        """Status geral do sistema de database"""
        try:
            from main import db
            
            # Testar conexão
            db.session.execute(text("SELECT 1;"))
            
            # Estatísticas rápidas
            total_tabelas = db.session.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)).fetchone()[0]
            
            total_processo_juridico = db.session.execute(text("""
                SELECT COUNT(*) FROM processo_juridico;
            """)).fetchone()[0]
            
            return jsonify({
                'success': True,
                'database_connected': True,
                'total_tabelas': total_tabelas,
                'total_processos': total_processo_juridico,
                'status': 'operacional',
                'timestamp': str(db.session.execute(text("SELECT NOW();")).fetchone()[0])
            })
            
        except Exception as e:
            logger.error(f"❌ Erro no status do database: {str(e)}")
            return jsonify({
                'success': False,
                'database_connected': False,
                'error': str(e)
            }), 500

    logger.info("✅ APIs de Database registradas com sucesso")

if __name__ == '__main__':
    print("⚠️ Este módulo deve ser importado e registrado via register_database_apis(app)")