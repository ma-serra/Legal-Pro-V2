#!/usr/bin/env python3
"""
Script para criar sistema de conexões entre agentes conforme documentação técnica.
Implementa conexões intra-área e inter-área com pesos de confiança.
"""
import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def create_agent_connections_system():
    """Cria sistema de conexões entre agentes"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔗 CRIANDO SISTEMA DE CONEXÕES MULTI-AGENTE...")
        
        # Cria tabela de conexões se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agente_conexoes (
                id SERIAL PRIMARY KEY,
                agente_origem_id INTEGER REFERENCES agente_juridico(id),
                agente_destino_id INTEGER REFERENCES agente_juridico(id),
                tipo_conexao VARCHAR(50) NOT NULL,
                peso_confianca DECIMAL(3,2) DEFAULT 1.0,
                areas_colaboracao TEXT[],
                descricao_conexao TEXT,
                ativa BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cria tabela de mensagens entre agentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agente_mensagens (
                id SERIAL PRIMARY KEY,
                agente_origem_id INTEGER REFERENCES agente_juridico(id),
                agente_destino_id INTEGER REFERENCES agente_juridico(id),
                tipo_consulta VARCHAR(100) NOT NULL,
                conteudo TEXT NOT NULL,
                contexto TEXT,
                prioridade VARCHAR(20) DEFAULT 'normal',
                status VARCHAR(50) DEFAULT 'pendente',
                resposta TEXT,
                processado_em TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cria tabela de sessões colaborativas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_colaborativas (
                id SERIAL PRIMARY KEY,
                sessao_id VARCHAR(50) UNIQUE NOT NULL,
                agentes_participantes INTEGER[],
                area_principal VARCHAR(100),
                objetivo TEXT,
                status VARCHAR(50) DEFAULT 'ativa',
                resultado TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finalizado_em TIMESTAMP
            )
        """)
        
        print("✅ Tabelas de conexões criadas com sucesso")
        
        # Busca coordenadores (nível 5) para criar conexões principais
        cursor.execute("""
            SELECT aj.id, aj.nome, cj.nome as categoria
            FROM agente_juridico aj
            JOIN categoria_juridica cj ON aj.categoria_id = cj.id
            WHERE aj.ativo = true 
            AND aj.nivel_especializacao = 5
            ORDER BY aj.nome
        """)
        
        coordenadores = cursor.fetchall()
        print(f"🎯 Encontrados {len(coordenadores)} coordenadores para conexões")
        
        # Define conexões inter-área baseadas na documentação
        conexoes_inter_area = [
            # Direito Penal ↔ Outras áreas
            ('Dr. Roberto Ferreira - Especialista Criminal Senior', 'Direito Processual Penal', 1.0, 'Compatibilidade total'),
            ('Dr. Roberto Ferreira - Especialista Criminal Senior', 'Direito Constitucional', 0.8, 'Direitos fundamentais'),
            ('Dr. Roberto Ferreira - Especialista Criminal Senior', 'Dra. Sandra Risk - Analista de Riscos Senior', 0.9, 'Avaliação criminal'),
            
            # Direito Civil ↔ Outras áreas  
            ('Dra. Maria Fernanda - Civilista Senior', 'Direito do Consumidor', 0.9, 'Contratos e responsabilidade'),
            ('Dra. Maria Fernanda - Civilista Senior', 'Dr. Eduardo Corporate - Empresarialista Senior', 0.8, 'Contratos comerciais'),
            ('Dra. Maria Fernanda - Civilista Senior', 'Direito Imobiliário', 0.9, 'Propriedade e locação'),
            
            # Direito Trabalhista ↔ Outras áreas
            ('Dr. Paulo Trabalhista - Especialista Senior CLT', 'Direito Previdenciário', 0.9, 'Benefícios e aposentadoria'),
            ('Dr. Paulo Trabalhista - Especialista Senior CLT', 'Dr. Eduardo Corporate - Empresarialista Senior', 0.8, 'Relações capital/trabalho'),
            ('Dr. Paulo Trabalhista - Especialista Senior CLT', 'Dra. Sandra Risk - Analista de Riscos Senior', 0.8, 'Passivos trabalhistas'),
            
            # Direito Empresarial ↔ Outras áreas
            ('Dr. Eduardo Corporate - Empresarialista Senior', 'Direito Tributário', 0.9, 'Planejamento fiscal'),
            ('Dr. Eduardo Corporate - Empresarialista Senior', 'Dr. Paulo Trabalhista - Especialista Senior CLT', 0.8, 'Relações trabalhistas'),
            ('Dr. Eduardo Corporate - Empresarialista Senior', 'Dra. Maria Fernanda - Civilista Senior', 0.8, 'Contratos e responsabilidade'),
            
            # Análise de Riscos ↔ TODAS as áreas (transversal)
            ('Dra. Sandra Risk - Analista de Riscos Senior', 'Dr. Roberto Ferreira - Especialista Criminal Senior', 0.9, 'Riscos criminais'),
            ('Dra. Sandra Risk - Analista de Riscos Senior', 'Dr. Paulo Trabalhista - Especialista Senior CLT', 0.8, 'Riscos trabalhistas'),
            ('Dra. Sandra Risk - Analista de Riscos Senior', 'Dr. Eduardo Corporate - Empresarialista Senior', 0.9, 'Riscos empresariais')
        ]
        
        conexoes_criadas = 0
        
        for origem_nome, destino_info, peso, descricao in conexoes_inter_area:
            # Busca agente origem
            cursor.execute("""
                SELECT id FROM agente_juridico 
                WHERE nome = %s AND ativo = true
            """, (origem_nome,))
            
            origem = cursor.fetchone()
            if not origem:
                continue
            
            # Busca agente destino (pode ser nome específico ou categoria)
            if destino_info.startswith('Dr') or destino_info.startswith('Dra'):
                # Nome específico de agente
                cursor.execute("""
                    SELECT id FROM agente_juridico 
                    WHERE nome = %s AND ativo = true
                """, (destino_info,))
            else:
                # Categoria jurídica - busca um coordenador da categoria
                cursor.execute("""
                    SELECT aj.id FROM agente_juridico aj
                    JOIN categoria_juridica cj ON aj.categoria_id = cj.id
                    WHERE LOWER(cj.nome) LIKE %s 
                    AND aj.ativo = true 
                    AND aj.nivel_especializacao = 5
                    LIMIT 1
                """, (f"%{destino_info.lower()}%",))
            
            destino = cursor.fetchone()
            if not destino:
                continue
            
            # Verifica se conexão já existe
            cursor.execute("""
                SELECT id FROM agente_conexoes 
                WHERE agente_origem_id = %s AND agente_destino_id = %s
            """, (origem['id'], destino['id']))
            
            if cursor.fetchone():
                continue
            
            # Cria conexão bidirecional
            cursor.execute("""
                INSERT INTO agente_conexoes 
                (agente_origem_id, agente_destino_id, tipo_conexao, peso_confianca, descricao_conexao)
                VALUES (%s, %s, 'inter_area', %s, %s)
            """, (origem['id'], destino['id'], peso, descricao))
            
            cursor.execute("""
                INSERT INTO agente_conexoes 
                (agente_origem_id, agente_destino_id, tipo_conexao, peso_confianca, descricao_conexao)
                VALUES (%s, %s, 'inter_area', %s, %s)
            """, (destino['id'], origem['id'], peso, descricao))
            
            conexoes_criadas += 2
            print(f"✅ Conexão criada: {origem_nome} ↔ {destino_info}")
        
        # Cria conexões intra-área (dentro da mesma categoria)
        cursor.execute("""
            SELECT categoria_id, COUNT(*) as total_agentes
            FROM agente_juridico 
            WHERE ativo = true 
            GROUP BY categoria_id
            HAVING COUNT(*) > 1
        """)
        
        categorias = cursor.fetchall()
        
        for categoria in categorias:
            # Busca coordenador da categoria
            cursor.execute("""
                SELECT id, nome FROM agente_juridico 
                WHERE categoria_id = %s AND ativo = true AND nivel_especializacao = 5
                LIMIT 1
            """, (categoria['categoria_id'],))
            
            coordenador = cursor.fetchone()
            if not coordenador:
                continue
            
            # Busca outros agentes da mesma categoria
            cursor.execute("""
                SELECT id, nome FROM agente_juridico 
                WHERE categoria_id = %s AND ativo = true AND id != %s
                ORDER BY nivel_especializacao DESC
                LIMIT 10
            """, (categoria['categoria_id'], coordenador['id']))
            
            agentes_categoria = cursor.fetchall()
            
            for agente in agentes_categoria:
                # Verifica se conexão já existe
                cursor.execute("""
                    SELECT id FROM agente_conexoes 
                    WHERE agente_origem_id = %s AND agente_destino_id = %s
                """, (coordenador['id'], agente['id']))
                
                if cursor.fetchone():
                    continue
                
                # Cria conexão intra-área
                cursor.execute("""
                    INSERT INTO agente_conexoes 
                    (agente_origem_id, agente_destino_id, tipo_conexao, peso_confianca, descricao_conexao)
                    VALUES (%s, %s, 'intra_area', %s, 'Supervisão hierárquica')
                """, (coordenador['id'], agente['id'], 0.9))
                
                conexoes_criadas += 1
        
        conn.commit()
        
        print(f"\n🎉 SISTEMA DE CONEXÕES IMPLEMENTADO!")
        print(f"📊 Total de conexões criadas: {conexoes_criadas}")
        print(f"🔗 Tabelas criadas: agente_conexoes, agente_mensagens, sessoes_colaborativas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def validate_connections():
    """Valida sistema de conexões criado"""
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n📊 VALIDAÇÃO DO SISTEMA DE CONEXÕES:")
        
        # Estatísticas de conexões
        cursor.execute("""
            SELECT tipo_conexao, COUNT(*) as total, AVG(peso_confianca) as peso_medio
            FROM agente_conexoes 
            WHERE ativa = true
            GROUP BY tipo_conexao
        """)
        
        tipos = cursor.fetchall()
        print("\n🔗 CONEXÕES POR TIPO:")
        for tipo in tipos:
            print(f"   {tipo['tipo_conexao']}: {tipo['total']} conexões (peso médio: {float(tipo['peso_medio']):.2f})")
        
        # Agentes mais conectados
        cursor.execute("""
            SELECT aj.nome, COUNT(ac.id) as total_conexoes
            FROM agente_juridico aj
            LEFT JOIN agente_conexoes ac ON aj.id = ac.agente_origem_id AND ac.ativa = true
            WHERE aj.ativo = true
            GROUP BY aj.id, aj.nome
            ORDER BY total_conexoes DESC
            LIMIT 10
        """)
        
        conectados = cursor.fetchall()
        print(f"\n🌟 TOP 10 AGENTES MAIS CONECTADOS:")
        for agente in conectados:
            print(f"   • {agente['nome']}: {agente['total_conexoes']} conexões")
        
        # Total geral
        cursor.execute("SELECT COUNT(*) as total FROM agente_conexoes WHERE ativa = true")
        total = cursor.fetchone()
        print(f"\n✅ Total de conexões ativas: {total['total']}")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 INICIANDO CRIAÇÃO DO SISTEMA DE CONEXÕES MULTI-AGENTE...")
    
    if create_agent_connections_system():
        validate_connections()
        print("\n🎯 Sistema de conexões implementado com sucesso!")
    else:
        print("\n❌ Falha na implementação!")
        sys.exit(1)

if __name__ == "__main__":
    main()