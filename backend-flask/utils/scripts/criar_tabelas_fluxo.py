"""
Script para criar as tabelas do modelo de fluxo.
"""
import os
import psycopg2
import psycopg2.extras
from psycopg2 import sql

# Obtém a URL de conexão do ambiente
DB_URL = os.environ.get('DATABASE_URL')

def criar_tabela_fluxo():
    """Cria a tabela fluxo no banco de dados."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    try:
        # Verifica se a tabela já existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'fluxo')")
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            # Cria a tabela fluxo
            cursor.execute("""
            CREATE TABLE fluxo (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                agentes TEXT,
                conexoes TEXT,
                configuracao TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_execucao TIMESTAMP,
                criado_por_id INTEGER REFERENCES "user" (id) ON DELETE SET NULL
            )
            """)
            print("Tabela 'fluxo' criada com sucesso!")
        else:
            print("Tabela 'fluxo' já existe.")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar tabela fluxo: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def criar_tabela_execucao_fluxo():
    """Cria a tabela execucao_fluxo no banco de dados."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    try:
        # Verifica se a tabela já existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'execucao_fluxo')")
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            # Cria a tabela execucao_fluxo
            cursor.execute("""
            CREATE TABLE execucao_fluxo (
                id SERIAL PRIMARY KEY,
                fluxo_id INTEGER REFERENCES fluxo (id) ON DELETE CASCADE,
                usuario_id INTEGER REFERENCES "user" (id) ON DELETE SET NULL,
                dados_entrada TEXT,
                resultado TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'iniciada',
                mensagem_erro TEXT,
                data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_conclusao TIMESTAMP,
                duracao_segundos FLOAT,
                log_execucao TEXT
            )
            """)
            print("Tabela 'execucao_fluxo' criada com sucesso!")
        else:
            print("Tabela 'execucao_fluxo' já existe.")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar tabela execucao_fluxo: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Criando tabelas para módulo de fluxos...")
    criar_tabela_fluxo()
    criar_tabela_execucao_fluxo()
    print("Tabelas do módulo de fluxos criadas com sucesso!")