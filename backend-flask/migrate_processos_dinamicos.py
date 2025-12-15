"""
Migration COMPLETA: Criar sistema de processos dinâmicos do zero
Data: 15 Dezembro 2025
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def executar_migration():
    print("="*80)
    print("MIGRATION: Criando Sistema de Processos COMPLETO")
    print("="*80)
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        print("\n[1] Criando tabela PROCESSOS principal...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processos (
                id_processo SERIAL PRIMARY KEY,
                uuid UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
                tenant_id INTEGER,
                numero_cnj VARCHAR(25),
                pasta VARCHAR(50),
                status_id INTEGER,
                natureza_id INTEGER,
                cliente_id INTEGER,
                posicao_cliente_id INTEGER,
                acao_id INTEGER,
                procedimento_id INTEGER,
                fase_id INTEGER,
                orgao_id INTEGER,
                comarca_id INTEGER,
                vara_turma_id INTEGER,
                justica_cnj_id INTEGER,
                instancia_cnj_id INTEGER,
                classe_cnj_id INTEGER,
                data_distribuicao DATE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                valor_causa NUMERIC(18,2),
                valor_causa_atualizado NUMERIC(18,2),
                valor_envolvido NUMERIC(18,2),
                valor_envolvido_atualizado NUMERIC(18,2),
                contingencia NUMERIC(18,2),
                tipo_probabilidade_id INTEGER,
                risco_id INTEGER,
                titulo TEXT,
                observacao_pasta TEXT,
                ativo BOOLEAN DEFAULT TRUE NOT NULL
            )
        """)
        print("  ✓ processos criada")
        
        print("\n[2] Criando índices em processos...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_cnj ON processos(numero_cnj)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_natureza ON processos(natureza_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_cliente ON processos(cliente_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_processos_ativo ON processos(ativo) WHERE ativo = TRUE")
        print("  ✓ 4 índices criados")
        
        print("\n[3] Criando tabela processo_campos_especificos...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_campos_especificos (
                id_campo_especifico BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                natureza_id INTEGER,
                campos_tributario JSONB,
                campos_trabalhista JSONB,
                campos_civel JSONB,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT uk_processo_natureza UNIQUE(processo_id, natureza_id)
            )
        """)
        print("  ✓ processo_campos_especificos")
        
        print("\n[4] Módulo TRIBUTÁRIO...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tributos (
                id_tributo SERIAL PRIMARY KEY,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                nome VARCHAR(200) NOT NULL,
                descricao TEXT,
                esfera VARCHAR(20) CHECK (esfera IN ('Federal', 'Estadual', 'Municipal')),
                ativo BOOLEAN DEFAULT TRUE NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ tributos")
        
        cur.execute("""
            INSERT INTO tributos (codigo, nome, esfera) VALUES
            ('ICMS', 'Imposto sobre Circulação de Mercadorias e Serviços', 'Estadual'),
            ('ISS', 'Imposto sobre Serviços', 'Municipal'),
            ('IRPJ', 'Imposto de Renda Pessoa Jurídica', 'Federal'),
            ('CSLL', 'Contribuição Social sobre Lucro Líquido', 'Federal'),
            ('PIS', 'Programa de Integração Social', 'Federal'),
            ('COFINS', 'Contribuição para Financiamento da Seguridade Social', 'Federal'),
            ('IPI', 'Imposto sobre Produtos Industrializados', 'Federal'),
            ('IPTU', 'Imposto Predial e Territorial Urbano', 'Municipal'),
            ('IPVA', 'Imposto sobre Propriedade de Veículos Automotores', 'Estadual')
            ON CONFLICT (codigo) DO NOTHING
        """)
        print("  ✓ 9 tributos inseridos")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teses_tributarias (
                id_tese SERIAL PRIMARY KEY,
                tenant_id INTEGER,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                titulo VARCHAR(500) NOT NULL,
                descricao TEXT,
                tributo_id INTEGER REFERENCES tributos(id_tributo),
                tema_repercussao_geral VARCHAR(50),
                tema_repetitivo VARCHAR(50),
                tribunal_origem VARCHAR(100),
                probabilidade_sucesso NUMERIC(5,2),
                fundamentacao TEXT,
                situacao VARCHAR(50),
                ativo BOOLEAN DEFAULT TRUE NOT NULL,
                criado_por INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ teses_tributarias")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_tributario (
                id_processo_tributario BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tributo_id INTEGER REFERENCES tributos(id_tributo),
                numero_aiim VARCHAR(100),
                numero_cda VARCHAR(100),
                data_lancamento DATE,
                valor_inscrito_cda NUMERIC(18,2),
                valor_principal NUMERIC(18,2),
                valor_multa NUMERIC(18,2),
                percentual_multa NUMERIC(5,2),
                base_calculo_multa VARCHAR(100),
                valor_juros NUMERIC(18,2),
                indice_juros VARCHAR(50),
                descricao_indice_juros TEXT,
                vara_primeira_instancia_id INTEGER,
                turma_segunda_instancia_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_processo_tributario UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_tributario")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_tese (
                id_processo_tese BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tese_id INTEGER REFERENCES teses_tributarias(id_tese) ON DELETE CASCADE,
                ordem INTEGER DEFAULT 1,
                status VARCHAR(50),
                data_vinculacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_processo_tese UNIQUE(processo_id, tese_id)
            )
        """)
        print("  ✓ processo_tese")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_prognostico_tributario (
                id_prognostico BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tese_provavel_id INTEGER REFERENCES teses_tributarias(id_tese),
                valor_provavel NUMERIC(18,2),
                percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
                tese_possivel_id INTEGER REFERENCES teses_tributarias(id_tese),
                valor_possivel NUMERIC(18,2),
                percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
                tese_remota_id INTEGER REFERENCES teses_tributarias(id_tese),
                valor_remoto NUMERIC(18,2),
                percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
                observacoes TEXT,
                data_avaliacao DATE,
                avaliado_por INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_prognostico_trib UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_prognostico_tributario")
        
        print("\n[5] Módulo TRABALHISTA...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_trabalhista (
                id_processo_trabalhista BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tolerancia_acordo NUMERIC(18,2),
                acordo_realizado NUMERIC(18,2),
                data_acordo DATE,
                observacoes_acordo TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_processo_trabalhista UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_trabalhista")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_prognostico_trabalhista (
                id_prognostico BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tese_provavel TEXT,
                valor_provavel NUMERIC(18,2),
                percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
                tese_possivel TEXT,
                valor_possivel NUMERIC(18,2),
                percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
                tese_remota TEXT,
                valor_remoto NUMERIC(18,2),
                percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
                observacoes TEXT,
                data_avaliacao DATE,
                avaliado_por INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_prognostico_trab UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_prognostico_trabalhista")
        
        print("\n[6] Módulo CÍVEL...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_civel (
                id_processo_civel BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tolerancia_acordo NUMERIC(18,2),
                acordo_realizado NUMERIC(18,2),
                data_acordo DATE,
                observacoes_acordo TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_processo_civel UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_civel")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_prognostico_civel (
                id_prognostico BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                tese_provavel TEXT,
                valor_provavel NUMERIC(18,2),
                percentual_provavel NUMERIC(5,2) DEFAULT 70.00,
                tese_possivel TEXT,
                valor_possivel NUMERIC(18,2),
                percentual_possivel NUMERIC(5,2) DEFAULT 50.00,
                tese_remota TEXT,
                valor_remoto NUMERIC(18,2),
                percentual_remoto NUMERIC(5,2) DEFAULT 25.00,
                observacoes TEXT,
                data_avaliacao DATE,
                avaliado_por INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_prognostico_civ UNIQUE(processo_id)
            )
        """)
        print("  ✓ processo_prognostico_civel")
        
        print("\n[7] Módulo ATUALIZAÇÃO MONETÁRIA...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS indices_monetarios (
                id_indice SERIAL PRIMARY KEY,
                nome VARCHAR(50) UNIQUE NOT NULL,
                descricao TEXT,
                fonte_oficial VARCHAR(200),
                ativo BOOLEAN DEFAULT TRUE NOT NULL
            )
        """)
        print("  ✓ indices_monetarios")
        
        cur.execute("""
            INSERT INTO indices_monetarios (nome, descricao, fonte_oficial) VALUES
            ('SELIC', 'Sistema Especial de Liquidação e Custódia', 'Banco Central do Brasil'),
            ('IPCA', 'Índice de Preços ao Consumidor Amplo', 'IBGE'),
            ('INPC', 'Índice Nacional de Preços ao Consumidor', 'IBGE'),
            ('IGP-M', 'Índice Geral de Preços do Mercado', 'FGV'),
            ('CDI', 'Certificado de Depósito Interbancário', 'CETIP'),
            ('TR', 'Taxa Referencial', 'Banco Central do Brasil')
            ON CONFLICT (nome) DO NOTHING
        """)
        print("  ✓ 6 índices monetários inseridos")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historico_indices (
                id_historico BIGSERIAL PRIMARY KEY,
                indice_id INTEGER NOT NULL REFERENCES indices_monetarios(id_indice),
                data_referencia DATE NOT NULL,
                valor NUMERIC(10,6) NOT NULL,
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uk_indice_data UNIQUE(indice_id, data_referencia)
            )
        """)
        print("  ✓ historico_indices")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processo_atualizacao_monetaria (
                id_atualizacao BIGSERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id_processo) ON DELETE CASCADE,
                indice_id INTEGER NOT NULL REFERENCES indices_monetarios(id_indice),
                data_base DATE NOT NULL,
                valor_base NUMERIC(18,2) NOT NULL,
                data_atualizacao DATE NOT NULL DEFAULT CURRENT_DATE,
                valor_atualizado NUMERIC(18,2),
                percentual_correcao NUMERIC(10,6),
                calculado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ processo_atualizacao_monetaria")
        
        print("\n[8] Tabela CONFIGURAÇÃO DINÂMICA...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS configuracao_formulario (
                id_configuracao SERIAL PRIMARY KEY,
                tenant_id INTEGER,
                natureza_id INTEGER,
                campos_obrigatorios JSONB NOT NULL DEFAULT '[]',
                campos_opcionais JSONB NOT NULL DEFAULT '[]',
                validacoes JSONB NOT NULL DEFAULT '{}',
                layout JSONB NOT NULL DEFAULT '{}',
                versao INTEGER DEFAULT 1,
                ativo BOOLEAN DEFAULT TRUE NOT NULL,
                criado_por INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ configuracao_formulario")
        
        print("\n" + "="*80)
        print("✅ MIGRATION CONCLUÍDA COM SUCESSO!")
        print("="*80)
        print("\nTabelas criadas: 18")
        print("- processos (principal)")
        print("- processo_campos_especificos")
        print("- 5 tabelas tributário")
        print("- 2 tabelas trabalhista")  
        print("- 2 tabelas cível")
        print("- 3 tabelas monetária")
        print("- 1 tabela configuração")
        print(f"\nDados: 9 tributos + 6 índices monetários")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    executar_migration()
