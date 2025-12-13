"""
Implementação de acesso a banco de dados PostgreSQL com Connection Pool e Cache.
"""
import os
import json
import logging
import psycopg2
import psycopg2.extras
import psycopg2.pool
import uuid
import datetime
import time
import hashlib
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from functools import wraps

# Configuração de logging
logger = logging.getLogger('multiagent.db.postgres')

# Connection Pool Global (Singleton)
_connection_pool = None

# Cache em memória para queries frequentes
_query_cache = {}
_cache_max_size = 1000  # Máximo de 1000 entradas em cache
_cache_ttl = 300  # 5 minutos

def _limpar_cache_expirado():
    """Limpa entradas expiradas do cache automaticamente."""
    global _query_cache
    now = time.time()
    keys_to_remove = [
        k for k, (_, timestamp) in _query_cache.items()
        if now - timestamp > _cache_ttl
    ]
    for k in keys_to_remove:
        del _query_cache[k]
    
    # Se ainda exceder tamanho máximo, remover as mais antigas
    if len(_query_cache) > _cache_max_size:
        sorted_cache = sorted(_query_cache.items(), key=lambda x: x[1][1])
        to_remove = len(_query_cache) - _cache_max_size
        for k, _ in sorted_cache[:to_remove]:
            del _query_cache[k]

def query_cache(ttl=300):
    """
    Decorator para cache de queries.
    
    Args:
        ttl: Tempo de vida do cache em segundos (padrão: 300s)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Limpar cache expirado periodicamente
            if len(_query_cache) % 100 == 0:
                _limpar_cache_expirado()
            
            # Gerar chave única baseada na função e argumentos
            cache_key = hashlib.md5(
                f"{func.__name__}:{str(args)}:{str(kwargs)}".encode()
            ).hexdigest()
            
            # Verificar se existe em cache e não expirou
            if cache_key in _query_cache:
                cached_data, timestamp = _query_cache[cache_key]
                if time.time() - timestamp < ttl:
                    logger.debug(f"✅ Cache HIT: {func.__name__}")
                    return cached_data
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            _query_cache[cache_key] = (result, time.time())
            logger.debug(f"💾 Cache MISS: {func.__name__}")
            return result
        
        return wrapper
    return decorator

def limpar_cache():
    """Limpa todo o cache de queries."""
    global _query_cache
    _query_cache = {}
    logger.info("🗑️ Cache de queries limpo")

def _init_connection_pool():
    """
    Inicializa o Connection Pool uma única vez.
    Otimização: Reutiliza conexões TCP ao invés de criar/fechar a cada query.
    """
    global _connection_pool
    
    if _connection_pool is not None:
        return _connection_pool
    
    # Tentar usar DATABASE_URL primeiro
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('NEON_DATABASE_URL')
    
    try:
        if db_url:
            # Pool com 5-20 conexões (otimizado para produção)
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=5,
                maxconn=20,
                dsn=db_url
            )
            logger.info("✅ Connection Pool inicializado com DATABASE_URL (5-20 conexões)")
        else:
            # Usar variáveis individuais do Replit
            pghost = os.environ.get('PGHOST')
            pguser = os.environ.get('PGUSER')
            pgpassword = os.environ.get('PGPASSWORD')
            pgdatabase = os.environ.get('PGDATABASE')
            pgport = os.environ.get('PGPORT', '5432')
            
            if not all([pghost, pguser, pgpassword, pgdatabase]):
                raise ValueError("Variáveis de ambiente do PostgreSQL não definidas")
            
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=5,
                maxconn=20,
                host=pghost,
                user=pguser,
                password=pgpassword,
                database=pgdatabase,
                port=pgport
            )
            logger.info("✅ Connection Pool inicializado com variáveis individuais (5-20 conexões)")
        
        return _connection_pool
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Connection Pool: {str(e)}")
        raise

class PooledConnection:
    """
    Wrapper que sobrescreve close() para devolver conexão ao pool.
    Mantém compatibilidade com código existente que chama conn.close().
    """
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        self._closed = False
    
    def close(self):
        """Devolve conexão ao pool ao invés de fechar."""
        if not self._closed:
            self._pool.putconn(self._conn)
            self._closed = True
    
    def __getattr__(self, name):
        """Redireciona todos os outros métodos para a conexão real."""
        return getattr(self._conn, name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

def obter_conexao():
    """
    Obtém uma conexão do Connection Pool.
    A conexão retornada automaticamente devolve-se ao pool quando close() é chamado.
    
    Returns:
        PooledConnection (compatível com psycopg2.connection)
    """
    pool = _init_connection_pool()
    conn = pool.getconn()
    return PooledConnection(conn, pool)

def devolver_conexao(conn):
    """
    DEPRECATED: Não é mais necessário - close() já devolve ao pool.
    Mantido para compatibilidade.
    
    Args:
        conn: Conexão a ser devolvida ao pool
    """
    if isinstance(conn, PooledConnection):
        conn.close()
    else:
        pool = _init_connection_pool()
        pool.putconn(conn)

@contextmanager
def obter_conexao_ctx():
    """
    Context manager para obter conexão do pool (modo seguro).
    Uso: with obter_conexao_ctx() as conn:
    
    Yields:
        Conexão do pool
    """
    pool = _init_connection_pool()
    conn = pool.getconn()
    
    try:
        yield conn
    finally:
        pool.putconn(conn)

def obter_fluxo_por_id(fluxo_id):
    """
    Obtém um fluxo específico pelo ID.
    
    Args:
        fluxo_id: ID do fluxo
        
    Returns:
        Dicionário com dados do fluxo ou None se não encontrado
    """
    try:
        logger.info(f"🔍 Obtendo fluxo {fluxo_id}...")
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, nome, descricao, agentes, conexoes, configuracao, 
                   ativo, data_criacao, data_atualizacao, criado_por_id, ultima_execucao
            FROM fluxo 
            WHERE id = %s
        """, (fluxo_id,))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not resultado:
            logger.warning(f"⚠️ Fluxo {fluxo_id} não encontrado no banco")
            return None
            
        # Converter para dicionário
        fluxo = dict(resultado)
        logger.info(f"✅ Fluxo {fluxo_id} obtido - agentes tipo RAW: {type(fluxo.get('agentes'))}, tamanho string: {len(str(fluxo.get('agentes', '')))}")
        
        # Converter campos JSON de string para lista/dict
        if isinstance(fluxo.get('agentes'), str):
            try:
                fluxo['agentes'] = json.loads(fluxo['agentes'] or '[]')
                logger.info(f"✅ Agentes convertidos - tipo: {type(fluxo['agentes'])}, quantidade: {len(fluxo['agentes'])}")
            except Exception as e:
                logger.error(f"❌ Erro ao converter agentes: {e}")
                fluxo['agentes'] = []
        elif not isinstance(fluxo.get('agentes'), list):
            logger.warning(f"⚠️ Agentes não é string nem lista: {type(fluxo.get('agentes'))}")
            fluxo['agentes'] = []
            
        if isinstance(fluxo.get('conexoes'), str):
            try:
                fluxo['conexoes'] = json.loads(fluxo['conexoes'] or '[]')
                logger.info(f"✅ Conexoes convertidas - tipo: {type(fluxo['conexoes'])}, quantidade: {len(fluxo['conexoes'])}")
            except Exception as e:
                logger.error(f"❌ Erro ao converter conexoes: {e}")
                fluxo['conexoes'] = []
        elif not isinstance(fluxo.get('conexoes'), list):
            logger.warning(f"⚠️ Conexoes não é string nem lista: {type(fluxo.get('conexoes'))}")
            fluxo['conexoes'] = []
            
        if isinstance(fluxo.get('configuracao'), str):
            try:
                fluxo['configuracao'] = json.loads(fluxo['configuracao'] or '{}')
            except Exception as e:
                logger.error(f"❌ Erro ao converter configuracao: {e}")
                fluxo['configuracao'] = {}
        elif not isinstance(fluxo.get('configuracao'), dict):
            fluxo['configuracao'] = {}
        
        logger.info(f"🎯 Retornando fluxo {fluxo_id} com {len(fluxo.get('agentes', []))} agentes e {len(fluxo.get('conexoes', []))} conexoes")
        return fluxo
        
    except Exception as e:
        logger.error(f"❌ ERRO ao obter fluxo {fluxo_id}: {str(e)}", exc_info=True)
        return None

def salvar_resultado_fluxo(fluxo_id, resultado_data):
    """
    Salva o resultado de execução de um fluxo.
    
    Args:
        fluxo_id: ID do fluxo
        resultado_data: Dados do resultado da execução
        
    Returns:
        ID do resultado salvo ou None se erro
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Criar tabela se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fluxo_resultado (
                id SERIAL PRIMARY KEY,
                uuid_resultado UUID DEFAULT gen_random_uuid() UNIQUE,
                fluxo_id INTEGER NOT NULL,
                input_original TEXT,
                template_gerado TEXT,
                analise_juridica TEXT,
                componentes_processados INTEGER DEFAULT 0,
                tempo_execucao VARCHAR(50),
                data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resultado_completo JSONB,
                status VARCHAR(20) DEFAULT 'concluido',
                hash_resultado VARCHAR(64)
            )
        """)
        
        # Gerar hash único do resultado para evitar duplicatas
        import hashlib
        conteudo_hash = f"{fluxo_id}_{resultado_data.get('input_original', '')}_{resultado_data.get('template_gerado', '')}"
        hash_resultado = hashlib.sha256(conteudo_hash.encode()).hexdigest()
        
        # Inserir resultado
        cursor.execute("""
            INSERT INTO fluxo_resultado 
            (fluxo_id, input_original, template_gerado, analise_juridica, 
             componentes_processados, resultado_completo, hash_resultado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, uuid_resultado
        """, (
            fluxo_id,
            resultado_data.get('input_original'),
            resultado_data.get('template_gerado'),
            resultado_data.get('analise_juridica'),
            resultado_data.get('componentes_processados', 0),
            json.dumps(resultado_data),
            hash_resultado
        ))
        
        resultado = cursor.fetchone()
        resultado_id = resultado[0]
        uuid_resultado = resultado[1]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Resultado do fluxo {fluxo_id} salvo com ID {resultado_id} e UUID {uuid_resultado}")
        return {
            'id': resultado_id,
            'uuid': str(uuid_resultado),
            'hash': hash_resultado
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultado do fluxo {fluxo_id}: {str(e)}")
        return None

def obter_ultimo_resultado_fluxo(fluxo_id):
    """
    Obtém o último resultado de execução de um fluxo.
    
    Args:
        fluxo_id: ID do fluxo
        
    Returns:
        Dicionário com dados do resultado ou None se não encontrado
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, uuid_resultado, fluxo_id, input_original, template_gerado, analise_juridica,
                   componentes_processados, tempo_execucao, data_execucao, 
                   resultado_completo, status, hash_resultado
            FROM fluxo_resultado 
            WHERE fluxo_id = %s 
            ORDER BY data_execucao DESC 
            LIMIT 1
        """, (fluxo_id,))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if resultado:
            return dict(resultado)
        return None
        
    except Exception as e:
        logger.error(f"Erro ao obter resultado do fluxo {fluxo_id}: {str(e)}")
        return None

def obter_resultado_por_uuid(uuid_resultado):
    """
    Obtém um resultado de execução pelo UUID.
    
    Args:
        uuid_resultado: UUID do resultado
        
    Returns:
        Dicionário com dados do resultado ou None se não encontrado
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, uuid_resultado, fluxo_id, input_original, template_gerado, analise_juridica,
                   componentes_processados, tempo_execucao, data_execucao, 
                   resultado_completo, status, hash_resultado
            FROM fluxo_resultado 
            WHERE uuid_resultado = %s
        """, (uuid_resultado,))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if resultado:
            return dict(resultado)
        return None
        
    except Exception as e:
        logger.error(f"Erro ao obter resultado por UUID {uuid_resultado}: {str(e)}")
        return None

def listar_resultados_fluxo(fluxo_id, limite=10):
    """
    Lista todos os resultados de um fluxo.
    
    Args:
        fluxo_id: ID do fluxo
        limite: Limite de resultados a retornar
        
    Returns:
        Lista de resultados
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, uuid_resultado, fluxo_id, input_original, template_gerado, analise_juridica,
                   componentes_processados, tempo_execucao, data_execucao, 
                   resultado_completo, status, hash_resultado
            FROM fluxo_resultado 
            WHERE fluxo_id = %s 
            ORDER BY data_execucao DESC 
            LIMIT %s
        """, (fluxo_id, limite))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(resultado) for resultado in resultados]
        
    except Exception as e:
        logger.error(f"Erro ao listar resultados do fluxo {fluxo_id}: {str(e)}")
        return []

def listar_todos_resultados(limite=100):
    """
    Lista todos os resultados de execução do sistema.
    
    Args:
        limite: Limite de resultados a retornar
        
    Returns:
        Lista de todos os resultados
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, uuid_resultado, fluxo_id, input_original, template_gerado, analise_juridica,
                   componentes_processados, tempo_execucao, data_execucao, 
                   resultado_completo, status, hash_resultado
            FROM fluxo_resultado 
            ORDER BY data_execucao DESC 
            LIMIT %s
        """, (limite,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [dict(resultado) for resultado in resultados]
        
    except Exception as e:
        logger.error(f"Erro ao listar todos os resultados: {str(e)}")
        return []

def salvar_fluxo(dados_fluxo):
    """
    Salva um novo fluxo no banco de dados.
    
    Args:
        dados_fluxo: Dicionário com dados do fluxo
        
    Returns:
        ID do fluxo salvo
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Preparar dados para inserção
        nome = dados_fluxo.get('nome', 'Novo Fluxo')
        descricao = dados_fluxo.get('descricao', '')
        agentes = json.dumps(dados_fluxo.get('agentes', []))
        conexoes = json.dumps(dados_fluxo.get('conexoes', []))
        configuracao = json.dumps(dados_fluxo.get('configuracao', {}))
        ativo = dados_fluxo.get('ativo', True)
        prioridade = dados_fluxo.get('prioridade', 'normal')
        criado_por_id = dados_fluxo.get('criado_por_id', None)
        
        cursor.execute("""
            INSERT INTO fluxo (nome, descricao, agentes, conexoes, configuracao, ativo, prioridade, criado_por_id, data_criacao, data_atualizacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (nome, descricao, agentes, conexoes, configuracao, ativo, prioridade, criado_por_id))
        
        fluxo_id = cursor.fetchone()[0]
        conn.commit()
        
        logger.info(f"✅ Fluxo '{nome}' (ID: {fluxo_id}) salvo com sucesso no banco de dados")
        
        cursor.close()
        conn.close()
        
        return fluxo_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar fluxo: {str(e)}")
        if conn:
            conn.rollback()
        raise

def atualizar_fluxo(fluxo_id, dados_fluxo):
    """
    Atualiza um fluxo existente no banco de dados.
    
    Args:
        fluxo_id: ID do fluxo a ser atualizado
        dados_fluxo: Dicionário com novos dados do fluxo
        
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Preparar dados para atualização
        nome = dados_fluxo.get('nome')
        descricao = dados_fluxo.get('descricao')
        agentes = json.dumps(dados_fluxo.get('agentes', []))
        conexoes = json.dumps(dados_fluxo.get('conexoes', []))
        configuracao = json.dumps(dados_fluxo.get('configuracao', {}))
        ativo = dados_fluxo.get('ativo', True)
        prioridade = dados_fluxo.get('prioridade', 'normal')
        
        cursor.execute("""
            UPDATE fluxo 
            SET nome = %s, descricao = %s, agentes = %s, conexoes = %s, 
                configuracao = %s, ativo = %s, prioridade = %s, data_atualizacao = NOW()
            WHERE id = %s
        """, (nome, descricao, agentes, conexoes, configuracao, ativo, prioridade, fluxo_id))
        
        conn.commit()
        
        logger.info(f"✅ Fluxo ID {fluxo_id} atualizado com sucesso")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao atualizar fluxo {fluxo_id}: {str(e)}")
        if conn:
            conn.rollback()
        return False

def salvar_resultado_fluxo(fluxo_id, resultado):
    """
    Salva o resultado da execução de um fluxo.
    
    Args:
        fluxo_id: ID do fluxo executado
        resultado: Dicionário com resultado da execução
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO execucao_fluxo (fluxo_id, resultado, executado_em, status)
            VALUES (%s, %s, NOW(), 'concluido')
        """, (fluxo_id, json.dumps(resultado)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Resultado da execução do fluxo {fluxo_id} salvo com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultado do fluxo {fluxo_id}: {str(e)}")
        if conn:
            conn.rollback()

# Funções de acesso a execuções
def listar_execucoes_pg(limite=10, offset=0, tag=None, ordem='desc'):
    """
    Lista as execuções de fluxos armazenadas no PostgreSQL.
    
    Args:
        limite: Limite de itens por página
        offset: Quantos registros pular
        tag: Filtra por tag (opcional)
        ordem: Ordem de listagem ('asc' ou 'desc')
        
    Returns:
        Lista de execuções
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Monta a consulta SQL
        query = "SELECT id, fluxo, resultado, log, executado_em, tempo_execucao, status FROM execucoes"
        params = []
        
        # Adiciona condições de filtro
        where_clauses = []
        if tag:
            where_clauses.append("status = %s")
            params.append(tag)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        # Adiciona ordenação
        query += f" ORDER BY executado_em {'ASC' if ordem.lower() == 'asc' else 'DESC'}"
        
        # Adiciona limitação
        query += " LIMIT %s OFFSET %s"
        params.extend([limite, offset])
        
        # Executa a consulta
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Converte para lista de dicionários
        execucoes = []
        for row in resultados:
            execucao = dict(row)
            
            # Extrai título do resultado se disponível
            if execucao['resultado'] and isinstance(execucao['resultado'], dict):
                if 'titulo' in execucao['resultado']:
                    execucao['titulo'] = execucao['resultado']['titulo']
                elif 'mensagem' in execucao['resultado']:
                    execucao['titulo'] = execucao['resultado']['mensagem'][:50]
                else:
                    execucao['titulo'] = f"Execução {execucao['id']}"
            else:
                execucao['titulo'] = f"Execução {execucao['id']}"
                
            # Formata a data de execução
            if execucao['executado_em']:
                execucao['data_execucao'] = execucao['executado_em'].isoformat()
                
            execucoes.append(execucao)
            
        conn.close()
        return execucoes
        
    except Exception as e:
        logger.error(f"Erro ao listar execuções: {str(e)}")
        return []

def obter_execucao_por_id(execucao_id):
    """
    Obtém uma execução pelo ID.
    
    Args:
        execucao_id: ID da execução (pode ser int ou str)
        
    Returns:
        Execução ou None se não encontrada
    """
    if not execucao_id:
        return None
        
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Executa a consulta - permite buscar por ID ou UUID
        query = "SELECT id, fluxo, resultado, log, executado_em, tempo_execucao, status FROM execucoes WHERE id = %s OR CAST(id as TEXT) = %s"
        cursor.execute(query, (execucao_id, str(execucao_id)))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            conn.close()
            return None
            
        # Converte para dicionário
        execucao = dict(resultado)
        
        # Extrai título do resultado se disponível
        if execucao['resultado'] and isinstance(execucao['resultado'], dict):
            if 'titulo' in execucao['resultado']:
                execucao['titulo'] = execucao['resultado']['titulo']
            elif 'mensagem' in execucao['resultado']:
                execucao['titulo'] = execucao['resultado']['mensagem'][:50]
            else:
                execucao['titulo'] = f"Execução {execucao['id']}"
        else:
            execucao['titulo'] = f"Execução {execucao['id']}"
        
        # Adiciona campos compatíveis com a API anterior
        execucao['data_execucao'] = execucao['executado_em']
        if 'texto_entrada' not in execucao and execucao['resultado'] and isinstance(execucao['resultado'], dict):
            execucao['texto_entrada'] = execucao['resultado'].get('texto', '')
            
        # Formata a data de execução
        if execucao['executado_em']:
            execucao['data_execucao'] = execucao['executado_em'].isoformat()
            
        conn.close()
        return execucao
        
    except Exception as e:
        logger.error(f"Erro ao obter execução {execucao_id}: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
        return None
        
def excluir_execucao(execucao_id):
    """
    Exclui uma execução do banco de dados.
    
    Args:
        execucao_id: ID da execução a ser excluída
        
    Returns:
        bool: True se a exclusão foi bem-sucedida, False caso contrário
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Verifica se a execução existe
        cursor.execute("SELECT id FROM execucoes WHERE id = %s", (execucao_id,))
        if cursor.fetchone() is None:
            logger.warning(f"Tentativa de excluir execução inexistente: {execucao_id}")
            conn.close()
            return False
        
        # Exclui a execução
        cursor.execute("DELETE FROM execucoes WHERE id = %s", (execucao_id,))
        afetadas = cursor.rowcount
        conn.commit()
        
        logger.info(f"Execução {execucao_id} excluída com sucesso. Linhas afetadas: {afetadas}")
        return afetadas > 0
        
    except Exception as e:
        logger.error(f"Erro ao excluir execução {execucao_id}: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def salvar_execucao(titulo, texto_entrada, resultado, log=None, tags=None):
    """
    Salva uma execução de análise.
    
    Args:
        titulo: Título da execução
        texto_entrada: Texto analisado
        resultado: Resultado da análise (dict ou str JSON)
        log: Log da execução (dict ou str JSON)
        tags: Lista de tags para categorizar a execução
        
    Returns:
        ID da execução salva
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Prepara os dados
        now = datetime.datetime.now()
        
        # Adiciona o texto de entrada e título ao resultado para preservar esses dados
        if isinstance(resultado, dict):
            # Adiciona metadados ao resultado
            if texto_entrada and 'texto' not in resultado:
                resultado['texto'] = texto_entrada
            if titulo and 'titulo' not in resultado:
                resultado['titulo'] = titulo
            resultado_json = json.dumps(resultado)
        else:
            # Se o resultado já for string JSON, mantém como está
            resultado_json = resultado
            
        if log:
            if isinstance(log, dict):
                log_json = json.dumps(log)
            else:
                log_json = log
        else:
            log_json = json.dumps({})
            
        # Insere a execução
        query = """
        INSERT INTO execucoes
        (fluxo, resultado, log, executado_em, tempo_execucao, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        cursor.execute(query, (
            "analise_texto",  # fluxo
            resultado_json,   # resultado
            log_json,         # log
            now,              # executado_em
            0.0,              # tempo_execucao (placeholder)
            "concluido"       # status
        ))
        
        # Obtém o ID gerado
        result = cursor.fetchone()
        if result is None:
            raise ValueError("Falha ao obter ID da execução inserida")
        
        execucao_id = result[0]
        conn.commit()
        
        logger.info(f"Execução {titulo} (ID: {execucao_id}) salva com sucesso")
        return execucao_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar execução: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        raise 
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Funções de acesso a agentes
def listar_agentes(apenas_ativos=True):
    """
    Lista os agentes configurados.
    
    Args:
        apenas_ativos: Se True, lista apenas agentes ativos
        
    Returns:
        Lista de agentes
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Monta a consulta SQL
        query = "SELECT id, nome, descricao, tipo, prompt_template, configuracoes, criado_em, ativo FROM agentes_personalizados"
        params = []
        
        if apenas_ativos:
            query += " WHERE ativo = %s"
            params.append(True)
            
        query += " ORDER BY criado_em DESC"
        
        # Executa a consulta
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Converte para lista de dicionários
        agentes = []
        for row in resultados:
            agente = dict(row)
            
            # Converte campos JSONB para dicionários Python
            if isinstance(agente['configuracoes'], str):
                agente['configuracoes'] = json.loads(agente['configuracoes'])
                
            # Formata a data de criação
            if agente['criado_em']:
                agente['criado_em'] = agente['criado_em'].isoformat()
                
            agentes.append(agente)
            
        conn.close()
        return agentes
        
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {str(e)}")
        return []

def obter_agente_por_id(agente_id):
    """
    Obtém um agente pelo ID.
    
    Args:
        agente_id: ID do agente
        
    Returns:
        Agente ou None se não encontrado
    """
    if not agente_id:
        return None
        
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Executa a consulta
        query = "SELECT id, nome, descricao, tipo, prompt_template, configuracoes, criado_em, ativo FROM agentes_personalizados WHERE id = %s"
        cursor.execute(query, (agente_id,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            return None
            
        # Converte para dicionário
        agente = dict(resultado)
        
        # Converte campos JSONB para dicionários Python
        if isinstance(agente['configuracoes'], str):
            agente['configuracoes'] = json.loads(agente['configuracoes'])
            
        # Formata a data de criação
        if agente['criado_em']:
            agente['criado_em'] = agente['criado_em'].isoformat()
            
        return agente
        
    except Exception as e:
        logger.error(f"Erro ao obter agente {agente_id}: {str(e)}")
        return None

def salvar_agente(nome, descricao, tipo, prompt_template, configuracoes):
    """
    Salva um novo agente.
    
    Args:
        nome: Nome do agente
        descricao: Descrição do agente
        tipo: Tipo do agente
        prompt_template: Template de prompt do agente
        configuracoes: Configurações do agente
        
    Returns:
        ID do agente salvo
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Prepara os dados
        now = datetime.datetime.now()
        
        # Converte configurações para JSON se necessário
        if isinstance(configuracoes, dict):
            configuracoes_json = json.dumps(configuracoes)
        else:
            configuracoes_json = configuracoes
            
        # Insere o agente
        query = """
        INSERT INTO agentes_personalizados 
        (nome, descricao, tipo, prompt_template, configuracoes, criado_em, ativo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
        RETURNING id
        """
        
        cursor.execute(query, (
            nome,
            descricao,
            tipo,
            prompt_template,
            configuracoes_json,
            now,
            True
        ))
        
        # Obtém o ID gerado
        agente_id = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        logger.info(f"Agente {nome} (ID: {agente_id}) criado com sucesso")
        return agente_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar agente: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        raise

def atualizar_agente(agente_id, dados):
    """
    Atualiza um agente existente.
    
    Args:
        agente_id: ID do agente
        dados: Novos dados do agente
        
    Returns:
        True se atualizado com sucesso
    """
    if not agente_id or not dados:
        raise ValueError("ID do agente e dados são obrigatórios")
        
    try:
        # Obtém o agente atual
        agente_atual = obter_agente_por_id(agente_id)
        if not agente_atual:
            raise ValueError(f"Agente {agente_id} não encontrado")
            
        # Prepara os campos a serem atualizados
        campos_atualizados = {}
        
        # Nome
        if 'nome' in dados:
            campos_atualizados['nome'] = dados['nome']
            
        # Descrição
        if 'descricao' in dados:
            campos_atualizados['descricao'] = dados['descricao']
            
        # Tipo
        if 'tipo' in dados:
            campos_atualizados['tipo'] = dados['tipo']
            
        # Template de prompt
        if 'prompt_template' in dados:
            campos_atualizados['prompt_template'] = dados['prompt_template']
            
        # Configurações
        if 'configuracoes' in dados:
            if isinstance(dados['configuracoes'], dict):
                campos_atualizados['configuracoes'] = json.dumps(dados['configuracoes'])
            else:
                campos_atualizados['configuracoes'] = dados['configuracoes']
                
        # Status de ativo
        if 'ativo' in dados:
            campos_atualizados['ativo'] = dados['ativo']
            
        # Se não há campos para atualizar, retorna
        if not campos_atualizados:
            return True
            
        # Monta a consulta SQL
        sets = []
        params = []
        
        for campo, valor in campos_atualizados.items():
            sets.append(f"{campo} = %s")
            params.append(valor)
            
        query = f"UPDATE agentes_personalizados SET {', '.join(sets)} WHERE id = %s"
        params.append(agente_id)
        
        # Executa a atualização
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        afetadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Agente {agente_id} atualizado com sucesso. Linhas afetadas: {afetadas}")
        return afetadas > 0
        
    except Exception as e:
        logger.error(f"Erro ao atualizar agente {agente_id}: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        raise

# Funções de acesso a fluxos
# NOTA: A função obter_fluxo_por_id está definida no início do arquivo (linha 39)

def listar_fluxos():
    """
    Lista os fluxos configurados.
    
    Returns:
        Lista de fluxos
    """
    from models import FluxoModel, db
    from flask import current_app
    import json
    
    try:
        with current_app.app_context():
            # Buscar todos os fluxos ativos usando SQLAlchemy
            fluxos_db = FluxoModel.query.filter_by(ativo=True).order_by(FluxoModel.data_criacao.desc()).all()
            
            fluxos = []
            for fluxo_db in fluxos_db:
                fluxo = {
                    'id': fluxo_db.id,
                    'nome': fluxo_db.nome,
                    'descricao': fluxo_db.descricao,
                    'ativo': fluxo_db.ativo,
                    'data_criacao': fluxo_db.data_criacao,
                    'data_atualizacao': fluxo_db.data_atualizacao,
                    'ultima_execucao': fluxo_db.ultima_execucao,
                    'criado_por_id': fluxo_db.criado_por_id
                }
                
                # Converter agentes, conexões e configuração de JSON para dicionário/lista
                try:
                    fluxo['agentes'] = json.loads(fluxo_db.agentes or '[]')
                except:
                    fluxo['agentes'] = []
                    
                try:
                    fluxo['conexoes'] = json.loads(fluxo_db.conexoes or '[]')
                except:
                    fluxo['conexoes'] = []
                    
                try:
                    fluxo['configuracao'] = json.loads(fluxo_db.configuracao or '{}')
                except:
                    fluxo['configuracao'] = {}
                        
                fluxos.append(fluxo)
                
            print(f"✅ Listados {len(fluxos)} fluxos do banco de dados")
            return fluxos
            
    except Exception as e:
        print(f"❌ Erro ao listar fluxos: {str(e)}")
        return []

def salvar_fluxo(dados_fluxo):
    """
    Salva um novo fluxo.
    
    Args:
        dados_fluxo: Dicionário com os dados do fluxo
        
    Returns:
        ID do fluxo salvo
    """
    from models import FluxoModel, db
    from flask import current_app
    import json
    
    try:
        with current_app.app_context():
            # Extrair dados do fluxo
            nome = dados_fluxo.get('nome', 'Novo Fluxo')
            descricao = dados_fluxo.get('descricao', '')
            
            # Aceitar tanto 'components/connections' quanto 'agentes/conexoes'
            agentes_data = dados_fluxo.get('agentes', dados_fluxo.get('components', []))
            conexoes_data = dados_fluxo.get('conexoes', dados_fluxo.get('connections', []))
            
            configuracao = dados_fluxo.get('configuracao', {})
            user_id = dados_fluxo.get('user_id', dados_fluxo.get('criado_por_id'))
            
            # Converter listas e dicionários para JSON
            agentes_json = json.dumps(agentes_data)
            conexoes_json = json.dumps(conexoes_data)
            configuracao_json = json.dumps(configuracao)
            
            # Criar novo objeto FluxoModel usando SQL direto
            from sqlalchemy import text
            
            # Inserir usando SQL direto para evitar problemas de construtor
            query = text("""
                INSERT INTO fluxo (nome, descricao, agentes, conexoes, configuracao, ativo, criado_por_id, data_criacao, data_atualizacao)
                VALUES (:nome, :descricao, :agentes, :conexoes, :configuracao, :ativo, :criado_por_id, NOW(), NOW())
                RETURNING id
            """)
            
            result = db.session.execute(query, {
                'nome': nome,
                'descricao': descricao,
                'agentes': agentes_json,
                'conexoes': conexoes_json,
                'configuracao': configuracao_json,
                'ativo': True,
                'criado_por_id': user_id
            })
            
            row = result.fetchone()
            if row:
                fluxo_id = row[0]
            else:
                raise Exception("Erro ao obter ID do fluxo inserido")
            db.session.commit()
            
            print(f"✅ Fluxo '{nome}' (ID: {fluxo_id}) salvo com sucesso no banco de dados")
            return fluxo_id
    except Exception as e:
        print(f"❌ Erro ao salvar fluxo: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        raise e

def atualizar_fluxo(fluxo_id, dados):
    """
    Atualiza um fluxo existente.
    
    Args:
        fluxo_id: ID do fluxo
        dados: Novos dados do fluxo
        
    Returns:
        True se atualizado com sucesso
    """
    from models import FluxoModel, db
    from flask import current_app
    import json
    
    if not fluxo_id or not dados:
        logger.warning("ID do fluxo e dados são obrigatórios para atualização")
        return False
        
    try:
        with current_app.app_context():
            # Buscar o fluxo no banco de dados
            fluxo_model = FluxoModel.query.get(fluxo_id)
            
            if not fluxo_model:
                logger.warning(f"Fluxo {fluxo_id} não encontrado no banco de dados")
                return False
                
            # Atualizar os campos
            if 'nome' in dados:
                fluxo_model.nome = dados['nome']
                
            if 'descricao' in dados:
                fluxo_model.descricao = dados['descricao']
                
            if 'agentes' in dados:
                fluxo_model.agentes = json.dumps(dados['agentes'])
                
            if 'conexoes' in dados:
                fluxo_model.conexoes = json.dumps(dados['conexoes'])
                
            if 'configuracao' in dados:
                fluxo_model.configuracao = json.dumps(dados['configuracao'])
                
            if 'ativo' in dados:
                fluxo_model.ativo = bool(dados['ativo'])
                
            # Atualizar a data de modificação
            fluxo_model.data_atualizacao = datetime.datetime.now()
            
            # Salvar as alterações
            db.session.commit()
            
            logger.info(f"Fluxo {fluxo_id} atualizado com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao atualizar fluxo {fluxo_id}: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return False

def excluir_fluxo(fluxo_id):
    """
    Exclui um fluxo do banco de dados e suas execuções relacionadas.
    
    Args:
        fluxo_id: ID do fluxo a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida, False caso contrário
    """
    from models import FluxoModel, ExecucaoFluxo, db
    from flask import current_app
    
    if not fluxo_id:
        logger.warning("ID do fluxo é obrigatório para exclusão")
        return False
        
    try:
        with current_app.app_context():
            # Buscar o fluxo no banco de dados
            fluxo_model = FluxoModel.query.get(fluxo_id)
            
            if not fluxo_model:
                logger.warning(f"Fluxo {fluxo_id} não encontrado no banco de dados")
                return False
            
            # Primeiro, excluir todas as execuções relacionadas ao fluxo
            execucoes = ExecucaoFluxo.query.filter_by(fluxo_id=fluxo_id).all()
            for execucao in execucoes:
                db.session.delete(execucao)
            
            if execucoes:
                logger.info(f"Excluídas {len(execucoes)} execução(ões) do fluxo {fluxo_id}")
            
            # Depois, tentar excluir da tabela fluxo_resultado se existir
            try:
                from sqlalchemy import text
                db.session.execute(text("DELETE FROM fluxo_resultado WHERE fluxo_id = :fluxo_id"), {'fluxo_id': fluxo_id})
                logger.info(f"Resultados do fluxo {fluxo_id} excluídos da tabela fluxo_resultado")
            except Exception as e:
                logger.debug(f"Tabela fluxo_resultado não existe ou não tem dados para o fluxo {fluxo_id}: {str(e)}")
                
            # Por último, excluir o fluxo
            db.session.delete(fluxo_model)
            db.session.commit()
            
            logger.info(f"Fluxo {fluxo_id} excluído com sucesso")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao excluir fluxo {fluxo_id}: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return False

# Funções de acesso a execuções de fluxos
def listar_execucoes_fluxo(fluxo_id=None, pagina=1, limite=10):
    """
    Lista as execuções de fluxos.
    
    Args:
        fluxo_id: ID do fluxo (opcional)
        pagina: Número da página
        limite: Limite de itens por página
        
    Returns:
        Lista de execuções
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        offset = (pagina - 1) * limite
        
        # Monta a consulta SQL
        query = "SELECT id, fluxo, resultado, log, executado_em, tempo_execucao, status FROM execucoes"
        params = []
        
        # Adiciona condições de filtro se houver fluxo_id
        if fluxo_id:
            query += " WHERE fluxo = %s"
            params.append(fluxo_id)
            
        # Adiciona ordenação
        query += " ORDER BY executado_em DESC"
        
        # Adiciona limitação
        query += " LIMIT %s OFFSET %s"
        params.extend([limite, offset])
        
        # Executa a consulta
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Conta o total de registros para calcular o número total de páginas
        count_query = "SELECT COUNT(*) FROM execucoes"
        if fluxo_id:
            count_query += " WHERE fluxo = %s"
            cursor.execute(count_query, [fluxo_id])
        else:
            cursor.execute(count_query)
            
        total_registros = cursor.fetchone()[0]
        total_paginas = (total_registros + limite - 1) // limite  # Arredondamento para cima
        
        # Converte para lista de dicionários
        execucoes = []
        for row in resultados:
            execucao = dict(row)
            
            # Extrai título do resultado se disponível
            if execucao['resultado'] and isinstance(execucao['resultado'], dict):
                if 'titulo' in execucao['resultado']:
                    execucao['titulo'] = execucao['resultado']['titulo']
                elif 'mensagem' in execucao['resultado']:
                    execucao['titulo'] = execucao['resultado']['mensagem'][:50]
                else:
                    execucao['titulo'] = f"Execução {execucao['id']}"
            else:
                execucao['titulo'] = f"Execução {execucao['id']}"
                
            # Formata a data de execução
            if execucao['executado_em']:
                execucao['data_formatada'] = execucao['executado_em'].strftime('%d/%m/%Y %H:%M:%S')
                
            execucoes.append(execucao)
            
        conn.close()
        
        return {
            'execucoes': execucoes,
            'pagina_atual': pagina,
            'total_paginas': total_paginas,
            'total_registros': total_registros,
            'por_pagina': limite
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar execuções de fluxo: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
        return {'execucoes': [], 'pagina_atual': 1, 'total_paginas': 0, 'total_registros': 0, 'por_pagina': limite}

def obter_execucao_fluxo_por_id(execucao_id):
    """
    Obtém uma execução de fluxo pelo ID.
    
    Args:
        execucao_id: ID da execução
        
    Returns:
        Execução ou None se não encontrada
    """
    if not execucao_id:
        return None
        
    try:
        conn = obter_conexao()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Executa a consulta - permite buscar por ID ou UUID
        query = """
        SELECT id, fluxo, resultado, log, executado_em, tempo_execucao, status 
        FROM execucoes 
        WHERE id = %s OR CAST(id as TEXT) = %s
        """
        cursor.execute(query, (execucao_id, str(execucao_id)))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            conn.close()
            return None
            
        # Converte para dicionário
        execucao = dict(resultado)
        
        # Adiciona um título e descrição da execução
        if execucao['resultado'] and isinstance(execucao['resultado'], dict):
            if 'titulo' in execucao['resultado']:
                execucao['titulo'] = execucao['resultado']['titulo']
            elif 'mensagem' in execucao['resultado']:
                execucao['titulo'] = execucao['resultado']['mensagem'][:50]
            else:
                execucao['titulo'] = f"Execução {execucao['id']}"
                
            # Extrai o texto de entrada se estiver disponível
            if 'texto' in execucao['resultado']:
                execucao['texto_entrada'] = execucao['resultado']['texto']
        else:
            execucao['titulo'] = f"Execução {execucao['id']}"
        
        # Formata a data de execução
        if execucao['executado_em']:
            execucao['data_formatada'] = execucao['executado_em'].strftime('%d/%m/%Y %H:%M:%S')
            
        conn.close()
        return execucao
        
    except Exception as e:
        logger.error(f"Erro ao obter execução de fluxo {execucao_id}: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
        return None

def salvar_execucao_fluxo(execucao):
    """
    Salva uma execução de fluxo.
    
    Args:
        execucao: Dicionário com dados da execução 
                 (fluxo_id, resultado, log, tempo_execucao, texto_entrada, status)
        
    Returns:
        ID da execução salva
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        # Prepara os dados
        now = datetime.datetime.now()
        
        # Extrai dados da execução
        fluxo_id = execucao.get('fluxo_id', 'desconhecido')
        resultado = execucao.get('resultado', {})
        log = execucao.get('log', {})
        tempo_execucao = execucao.get('tempo_execucao', 0.0)
        status = execucao.get('status', 'concluido')
        texto_entrada = execucao.get('texto_entrada', '')
        
        # Se o resultado for um dicionário, adiciona o texto de entrada
        if isinstance(resultado, dict) and texto_entrada:
            if 'texto' not in resultado:
                resultado['texto'] = texto_entrada
        
        # Converte para JSON se necessário
        if isinstance(resultado, dict):
            resultado_json = json.dumps(resultado)
        else:
            resultado_json = resultado
            
        if isinstance(log, dict):
            log_json = json.dumps(log)
        else:
            log_json = log
            
        # Insere a execução
        query = """
        INSERT INTO execucoes
        (fluxo, resultado, log, executado_em, tempo_execucao, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        cursor.execute(query, (
            fluxo_id,           # fluxo
            resultado_json,     # resultado
            log_json,           # log
            now,                # executado_em
            tempo_execucao,     # tempo_execucao 
            status              # status
        ))
        
        # Obtém o ID gerado
        result = cursor.fetchone()
        if result is None:
            raise ValueError("Falha ao obter ID da execução inserida")
        
        execucao_id = result[0]
        conn.commit()
        
        logger.info(f"Execução de fluxo {fluxo_id} (ID: {execucao_id}) salva com sucesso")
        return execucao_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar execução de fluxo: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()