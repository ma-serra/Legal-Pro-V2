"""
API para buscar especialistas jurídicos para seleção na análise multi-agente
"""
from flask import Blueprint, jsonify, request
import psycopg2
import os
from urllib.parse import urlparse

# Criar blueprint
api_especialistas_bp = Blueprint('api_especialistas', __name__)

def get_database_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL não encontrada")
        
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            port=parsed.port or 5432
        )
        return conn
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

@api_especialistas_bp.route('/api/especialistas/categorias', methods=['GET'])
def get_categorias():
    """Retorna todas as categorias jurídicas com contagem de especialistas"""
    try:
        conn = get_database_connection()
        if not conn:
            return jsonify({'error': 'Erro na conexão com o banco'}), 500
            
        cursor = conn.cursor()
        
        # Buscar categorias com contagem de especialistas ativos (excluindo Assistentes e Orquestradores)
        query = """
        SELECT c.id, c.nome, COUNT(a.id) as total_agentes 
        FROM categoria_juridica c 
        LEFT JOIN agente_juridico a ON c.id = a.categoria_id 
            AND a.ativo = true 
            AND a.classe NOT IN ('AssistentePrincipal', 'orquestrador_multiagente')
        GROUP BY c.id, c.nome 
        ORDER BY c.nome
        """
        
        cursor.execute(query)
        categorias = []
        
        for row in cursor.fetchall():
            categorias.append({
                'id': row[0],
                'nome': row[1],
                'total_agentes': row[2]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'categorias': categorias})
        
    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_especialistas_bp.route('/api/especialistas', methods=['GET'])
def get_especialistas():
    """Retorna especialistas com filtros opcionais"""
    try:
        conn = get_database_connection()
        if not conn:
            return jsonify({'error': 'Erro na conexão com o banco'}), 500
            
        cursor = conn.cursor()
        
        # Parâmetros de filtro
        categoria_id = request.args.get('categoria_id', '')
        busca = request.args.get('busca', '')
        limite = int(request.args.get('limite', 500))  # Aumentar limite padrão
        
        # Query base com capacidades (excluindo Assistentes e Orquestradores da escolha inteligente)
        query = """
        SELECT a.id, a.nome, a.descricao, a.icone, a.cor_destaque, 
               c.nome as categoria, a.nivel_especializacao, c.cor, a.capacidades
        FROM agente_juridico a 
        JOIN categoria_juridica c ON a.categoria_id = c.id 
        WHERE a.ativo = true 
        AND a.classe NOT IN ('AssistentePrincipal', 'orquestrador_multiagente')
        """
        
        params = []
        
        # Aplicar filtros
        if categoria_id:
            query += " AND a.categoria_id = %s"
            params.append(categoria_id)
            
        if busca:
            query += " AND (LOWER(a.nome) LIKE %s OR LOWER(a.descricao) LIKE %s)"
            busca_param = f"%{busca.lower()}%"
            params.extend([busca_param, busca_param])
        
        # Se não há filtro específico (todas as áreas), carregar todos os especialistas
        if not categoria_id and not busca:
            query += " ORDER BY c.nome, a.nome"
        else:
            query += " ORDER BY c.nome, a.nome LIMIT %s"
            params.append(limite)
        
        cursor.execute(query, params)
        especialistas = []
        
        for row in cursor.fetchall():
            # Processar capacidades do banco de dados
            capacidades = []
            if row[8]:  # row[8] são as capacidades
                try:
                    import json
                    if isinstance(row[8], str):
                        capacidades = json.loads(row[8])
                    elif isinstance(row[8], list):
                        capacidades = row[8]
                except (json.JSONDecodeError, TypeError):
                    capacidades = []
            
            especialistas.append({
                'id': row[0],
                'nome': row[1],
                'descricao': row[2],
                'icone': row[3] or 'fas fa-user-tie',
                'cor_destaque': row[4] or '#5a8fa3',
                'categoria': row[5],
                'nivel_especializacao': row[6] or 'Intermediário',
                'cor_categoria': row[7] or '#5a8fa3',
                'capacidades': capacidades
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'especialistas': especialistas})
        
    except Exception as e:
        print(f"Erro ao buscar especialistas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

def registrar_api_especialistas(app):
    """Registra a API de especialistas na aplicação"""
    app.register_blueprint(api_especialistas_bp)
    print("✅ API de especialistas registrada com sucesso")