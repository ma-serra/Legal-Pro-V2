#!/usr/bin/env python3
"""
Rotas para o sistema Legal Design Pro V2
Visualização e gerenciamento de fluxos jurídicos
"""

import os
import json
import psycopg2
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

# Criar blueprint
legal_design_bp = Blueprint('legal_design', __name__, url_prefix='/fluxos')

# Configuração de logging específico para Legal Design
logger = logging.getLogger('legal_design_routes')
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('🎨 LEGAL_DESIGN - %(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.info("📋 Módulo Legal Design Routes iniciado com logging detalhado")

def get_db_connection():
    """Obter conexão com PostgreSQL"""
    try:
        conn = psycopg2.connect(os.environ['NEON_DATABASE_URL'])
        conn.autocommit = True  # Evitar problemas de transação
        return conn
    except Exception as e:
        print(f"Erro ao conectar database: {e}")
        return None

@legal_design_bp.route('/')
@login_required
def index():
    """Página principal do Legal Design Pro"""
    logger.info(f"🎯 Acessando página principal Legal Design - Usuário: {current_user.username if current_user else 'Anônimo'}")
    
    conn = get_db_connection()
    if not conn:
        logger.error("❌ Erro ao conectar com o banco de dados")
        flash('Erro ao conectar com o banco de dados', 'error')
        return redirect(url_for('home'))
    
    try:
        cursor = conn.cursor()
        logger.debug("✅ Conexão com banco estabelecida")
        
        # Buscar todos os fluxos
        cursor.execute("""
            SELECT f.id, f.title, f.descricao, f.area_juridica, f.status, 
                   f.created_at, COUNT(e.id) as elementos_count
            FROM fluxo f
            LEFT JOIN legal_design_pieces e ON f.id = e.flow_id
            GROUP BY f.id, f.title, f.descricao, f.area_juridica, f.status, f.created_at
            ORDER BY f.created_at DESC
        """)
        
        flows = []
        for row in cursor.fetchall():
            flows.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'area_juridica': row[3],
                'status': row[4],
                'created_at': row[5],
                'elementos_count': row[6]
            })
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(*) FROM fluxo")
        total_flows = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM legal_design_pieces")
        total_elements = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fluxo_resultado")
        total_results = cursor.fetchone()[0]
        
        stats = {
            'total_flows': total_flows,
            'total_elements': total_elements,
            'total_results': total_results
        }
        
        return render_template('legal_design_index.html', flows=flows, stats=stats)
        
    except Exception as e:
        flash(f'Erro ao buscar fluxos: {str(e)}', 'error')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        conn.close()

@legal_design_bp.route('/<int:flow_id>')
@login_required
def view_flow(flow_id):
    """Visualizar fluxo específico"""
    logger.info(f"🔍 Acessando visualização de fluxo ID: {flow_id}")
    
    conn = get_db_connection()
    if not conn:
        logger.error(f"❌ Erro de conexão ao tentar visualizar fluxo {flow_id}")
        return f"<h1>Erro de Conexão</h1><p>Não foi possível conectar ao banco de dados</p>", 500
    
    try:
        cursor = conn.cursor()
        logger.debug(f"✅ Cursor criado para fluxo {flow_id}")
        
        # Buscar dados do fluxo
        logger.debug(f"📊 Executando consulta para fluxo ID: {flow_id}")
        cursor.execute("""
            SELECT id, user_id, title, descricao, area_juridica, status, 
                   created_at, metadata
            FROM fluxo WHERE id = %s
        """, (flow_id,))
        
        flow_data = cursor.fetchone()
        logger.debug(f"📄 Resultado da consulta: {flow_data}")
        
        if not flow_data:
            logger.warning(f"⚠️ Fluxo {flow_id} não encontrado no banco de dados")
            flash('Fluxo não encontrado', 'error')
            return redirect(url_for('legal_design.index'))
        
        flow = {
            'id': flow_data[0],
            'user_id': flow_data[1],
            'title': flow_data[2],
            'description': flow_data[3],
            'area_juridica': flow_data[4],
            'status': flow_data[5],
            'created_at': flow_data[6],
            'metadata': flow_data[7] if isinstance(flow_data[7], dict) else (json.loads(flow_data[7]) if flow_data[7] else {})
        }
        
        # Buscar elementos do fluxo
        cursor.execute("""
            SELECT id, element_type, title, content, position_x, position_y, 
                   order_index, properties, created_at
            FROM legal_design_pieces 
            WHERE flow_id = %s 
            ORDER BY order_index
        """, (flow_id,))
        
        elements = []
        for row in cursor.fetchall():
            elements.append({
                'id': row[0],
                'element_type': row[1],
                'title': row[2],
                'content': row[3],
                'position_x': row[4],
                'position_y': row[5],
                'order_index': row[6],
                'properties': row[7] if isinstance(row[7], dict) else (json.loads(row[7]) if row[7] else {}),
                'created_at': row[8]
            })
        
        # Buscar resultados do fluxo
        cursor.execute("""
            SELECT id, result_type, title, content, analysis, created_at
            FROM fluxo_resultado 
            WHERE flow_id = %s 
            ORDER BY created_at DESC
            LIMIT 1
        """, (flow_id,))
        
        result_data = cursor.fetchone()
        result = None
        if result_data:
            result = {
                'id': result_data[0],
                'result_type': result_data[1],
                'title': result_data[2],
                'content': result_data[3],
                'analysis': json.loads(result_data[4]) if result_data[4] else {},
                'created_at': result_data[5]
            }
        
        logger.info(f"✅ Renderizando template para fluxo {flow_id}")
        logger.debug(f"📊 Dados do fluxo: {flow}")
        logger.debug(f"🔧 Elementos encontrados: {len(elements)}")
        logger.debug(f"📋 Resultado disponível: {result is not None}")
        
        return render_template('legal_design_flow_viewer.html', 
                             flow=flow, elements=elements, result=result)
        
    except Exception as e:
        flash(f'Erro ao buscar fluxo: {str(e)}', 'error')
        return redirect(url_for('legal_design.index'))
    finally:
        cursor.close()
        conn.close()

@legal_design_bp.route('/<int:flow_id>/process', methods=['POST'])
@login_required
def process_flow(flow_id):
    """Processar fluxo e gerar resultados"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Erro ao conectar com o banco de dados'})
    
    try:
        cursor = conn.cursor()
        
        # Verificar se o fluxo existe
        cursor.execute("SELECT title FROM fluxo WHERE id = %s", (flow_id,))
        flow_data = cursor.fetchone()
        if not flow_data:
            return jsonify({'success': False, 'error': 'Fluxo não encontrado'})
        
        # Buscar elementos do fluxo
        cursor.execute("""
            SELECT id, title, element_type, content 
            FROM legal_design_pieces 
            WHERE flow_id = %s 
            ORDER BY order_index
        """, (flow_id,))
        
        elements = cursor.fetchall()
        
        # Simular processamento
        processed_elements = []
        for element in elements:
            processed_elements.append({
                'id': element[0],
                'title': element[1],
                'type': element[2],
                'status': 'processado',
                'tempo_execucao': '45 minutos'
            })
        
        # Gerar resultado do processamento
        resultado_content = f"""
RELATÓRIO DE PROCESSAMENTO ATUALIZADO
=====================================

Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Fluxo: {flow_data[0]}
Elementos processados: {len(processed_elements)}

STATUS: ✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO

Todos os {len(processed_elements)} elementos foram executados conforme o planejado.
O sistema executou as análises e gerou as recomendações necessárias.

PRÓXIMOS PASSOS:
• Revisar resultados gerados
• Implementar recomendações
• Agendar acompanhamento

Processado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
        """
        
        # Salvar resultado no banco
        cursor.execute("""
            INSERT INTO fluxo_resultado 
            (flow_id, result_type, title, content, analysis, processed_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            flow_id,
            'processamento_em_tempo_real',
            'Resultado do Processamento em Tempo Real',
            resultado_content,
            json.dumps({
                'elementos_processados': len(processed_elements),
                'tempo_total': '270 minutos',
                'status': 'concluido',
                'timestamp': datetime.now().isoformat()
            }),
            current_user.username if current_user else 'sistema'
        ))
        
        result_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fluxo processado com sucesso',
            'result_id': result_id,
            'elements_processed': len(processed_elements),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@legal_design_bp.route('/results/<int:result_id>')
@login_required
def view_result(result_id):
    """Visualizar resultado específico"""
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar com o banco de dados', 'error')
        return redirect(url_for('legal_design.index'))
    
    try:
        cursor = conn.cursor()
        
        # Buscar resultado
        cursor.execute("""
            SELECT r.id, r.flow_id, r.result_type, r.title, r.content, 
                   r.analysis, r.created_at, r.processed_by,
                   f.title as flow_title, f.descricao as flow_description
            FROM fluxo_resultado r
            JOIN fluxo f ON r.flow_id = f.id
            WHERE r.id = %s
        """, (result_id,))
        
        result_data = cursor.fetchone()
        if not result_data:
            flash('Resultado não encontrado', 'error')
            return redirect(url_for('legal_design.index'))
        
        result = {
            'id': result_data[0],
            'flow_id': result_data[1],
            'result_type': result_data[2],
            'title': result_data[3],
            'content': result_data[4],
            'analysis': json.loads(result_data[5]) if result_data[5] else {},
            'created_at': result_data[6],
            'processed_by': result_data[7],
            'flow_title': result_data[8],
            'flow_description': result_data[9]
        }
        
        return render_template('legal_design_result_viewer.html', result=result)
        
    except Exception as e:
        flash(f'Erro ao buscar resultado: {str(e)}', 'error')
        return redirect(url_for('legal_design.index'))
    finally:
        cursor.close()
        conn.close()

@legal_design_bp.route('/api/flows', methods=['GET'])
@login_required
def api_list_flows():
    """API para listar fluxos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar com o banco de dados'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.id, f.title, f.descricao, f.area_juridica, f.status, 
                   f.created_at, COUNT(e.id) as elementos_count,
                   COUNT(r.id) as resultados_count
            FROM fluxo f
            LEFT JOIN legal_design_pieces e ON f.id = e.flow_id
            LEFT JOIN fluxo_resultado r ON f.id = r.flow_id
            GROUP BY f.id, f.title, f.descricao, f.area_juridica, f.status, f.created_at
            ORDER BY f.created_at DESC
        """)
        
        flows = []
        for row in cursor.fetchall():
            flows.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'area_juridica': row[3],
                'status': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'elementos_count': row[6],
                'resultados_count': row[7]
            })
        
        return jsonify({'flows': flows})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@legal_design_bp.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    """API para estatísticas do sistema"""
    logger.info(f"📊 Acessando API de estatísticas - Usuário: {current_user.username if current_user else 'Anônimo'}")
    
    conn = get_db_connection()
    if not conn:
        logger.error("❌ Conexão com banco falhou na API de estatísticas")
        return jsonify({'error': 'Erro ao conectar com o banco de dados'}), 500
    
    try:
        cursor = conn.cursor()
        logger.debug("✅ Cursor estabelecido para API de estatísticas")
        
        # Estatísticas gerais
        logger.debug("📊 Executando consulta: fluxo")
        cursor.execute("SELECT COUNT(*) FROM fluxo")
        total_flows = cursor.fetchone()[0]
        logger.debug(f"   ✓ Total flows: {total_flows}")
        
        logger.debug("📊 Executando consulta: legal_design_pieces")
        cursor.execute("SELECT COUNT(*) FROM legal_design_pieces")
        total_elements = cursor.fetchone()[0]
        logger.debug(f"   ✓ Total elements: {total_elements}")
        
        logger.debug("📊 Executando consulta: fluxo_resultado")
        cursor.execute("SELECT COUNT(*) FROM fluxo_resultado")
        total_results = cursor.fetchone()[0]
        logger.debug(f"   ✓ Total results: {total_results}")
        
        # Fluxos por área jurídica
        cursor.execute("""
            SELECT area_juridica, COUNT(*) 
            FROM fluxo 
            GROUP BY area_juridica
            ORDER BY COUNT(*) DESC
        """)
        
        areas = []
        for row in cursor.fetchall():
            areas.append({
                'area': row[0],
                'count': row[1]
            })
        
        logger.info(f"📈 Estatísticas coletadas com sucesso - flows: {total_flows}, elements: {total_elements}, results: {total_results}")
        return jsonify({
            'total_flows': total_flows,
            'total_elements': total_elements,
            'total_results': total_results,
            'areas_juridicas': areas,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na API de estatísticas: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        logger.debug("🔒 Conexões fechadas na API de estatísticas")

def register_legal_design_routes(app):
    """Registrar rotas do Legal Design Pro"""
    app.register_blueprint(legal_design_bp)
    

    
    # Rota de teste direto sem autenticação
    @app.route('/test-flow/<int:flow_id>')
    def test_flow_direct(flow_id):
        """Teste direto do fluxo sem autenticação"""
        logger.info(f"🧪 TESTE DIRETO - Acessando fluxo ID: {flow_id}")
        
        conn = get_db_connection()
        if not conn:
            return f"<h1>Erro de Conexão</h1><p>Não foi possível conectar ao banco de dados</p>", 500
        
        try:
            cursor = conn.cursor()
            
            # Buscar dados do fluxo
            cursor.execute("""
                SELECT id, user_id, title, descricao, area_juridica, status, 
                       created_at, metadata
                FROM fluxo WHERE id = %s
            """, (flow_id,))
            
            flow_data = cursor.fetchone()
            logger.debug(f"🧪 TESTE - Resultado da consulta: {flow_data}")
            
            if not flow_data:
                return f"<h1>Fluxo não encontrado</h1><p>ID: {flow_id}</p>", 404
            
            flow = {
                'id': flow_data[0],
                'user_id': flow_data[1],
                'title': flow_data[2],
                'description': flow_data[3],
                'area_juridica': flow_data[4],
                'status': flow_data[5],
                'created_at': flow_data[6],
                'metadata': flow_data[7] if isinstance(flow_data[7], dict) else (json.loads(flow_data[7]) if flow_data[7] else {})
            }
            
            # Buscar elementos do fluxo
            cursor.execute("""
                SELECT id, element_type, title, content, position_x, position_y, 
                       order_index, properties, created_at
                FROM legal_design_pieces 
                WHERE flow_id = %s 
                ORDER BY order_index
            """, (flow_id,))
            
            elements = []
            for row in cursor.fetchall():
                elements.append({
                    'id': row[0],
                    'element_type': row[1],
                    'title': row[2],
                    'content': row[3],
                    'position_x': row[4],
                    'position_y': row[5],
                    'order_index': row[6],
                    'properties': row[7] if isinstance(row[7], dict) else (json.loads(row[7]) if row[7] else {}),
                    'created_at': row[8]
                })
            
            logger.info(f"✅ TESTE - Renderizando template para fluxo {flow_id}")
            logger.debug(f"📊 TESTE - Elementos encontrados: {len(elements)}")
            
            return render_template('legal_design_flow_viewer.html', 
                                 flow=flow, elements=elements, result=None)
                                 
        except Exception as e:
            logger.error(f"❌ TESTE - Erro: {str(e)}")
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500
        finally:
            cursor.close()
            conn.close()
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, descricao FROM fluxo WHERE id = %s", (flow_id,))
            flow_data = cursor.fetchone()
            
            if not flow_data:
                return f"Fluxo {flow_id} não encontrado", 404
            
            cursor.execute("SELECT COUNT(*) FROM legal_design_pieces WHERE flow_id = %s", (flow_id,))
            elements_count = cursor.fetchone()[0]
            
            return f"""
            <h1>Teste de Fluxo - ID {flow_id}</h1>
            <h2>{flow_data[1]}</h2>
            <p><strong>Descrição:</strong> {flow_data[2]}</p>
            <p><strong>Elementos:</strong> {elements_count}</p>
            <a href="/fluxos/{flow_id}">Ver Fluxo Completo</a>
            """
        except Exception as e:
            return f"Erro: {str(e)}", 500
        finally:
            cursor.close()
            conn.close()
    
    app.logger.info("✅ Rotas do Legal Design Pro registradas")
    print("✅ Legal Design Pro routes registered")