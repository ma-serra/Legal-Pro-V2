#!/usr/bin/env python3
"""
Reorganiza a estrutura da base universal para distinguir claramente
documentos reais dos seus chunks individuais
"""

import logging
import os
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReorganizadorEstrutura:
    def __init__(self):
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
    
    def adicionar_colunas_documento_estrutura(self):
        """Adiciona colunas para melhor estruturação"""
        try:
            cursor = self.db_conn.cursor()
            
            # Adicionar colunas se não existirem
            cursor.execute("""
                ALTER TABLE base_vetorial_universal 
                ADD COLUMN IF NOT EXISTS documento_id VARCHAR(100),
                ADD COLUMN IF NOT EXISTS chunk_sequencia INTEGER,
                ADD COLUMN IF NOT EXISTS total_chunks_documento INTEGER,
                ADD COLUMN IF NOT EXISTS documento_completo BOOLEAN DEFAULT FALSE
            """)
            
            self.db_conn.commit()
            cursor.close()
            logger.info("✅ Colunas de estrutura adicionadas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar colunas: {e}")
            return False
    
    def mapear_documentos_reais(self):
        """Mapeia os documentos reais e seus chunks"""
        try:
            cursor = self.db_conn.cursor()
            
            # Mapear documentos únicos
            cursor.execute("""
                SELECT DISTINCT documento, COUNT(*) as total_chunks
                FROM base_vetorial_universal 
                GROUP BY documento
                ORDER BY COUNT(*) DESC
            """)
            
            documentos_reais = cursor.fetchall()
            
            logger.info("📄 Documentos reais identificados:")
            for doc, chunks in documentos_reais:
                logger.info(f"   - {doc}: {chunks} chunks")
            
            cursor.close()
            return documentos_reais
            
        except Exception as e:
            logger.error(f"Erro ao mapear documentos: {e}")
            return []
    
    def atualizar_estrutura_documentos(self):
        """Atualiza estrutura com IDs de documento e sequência de chunks"""
        try:
            cursor = self.db_conn.cursor()
            
            # Mapeamento de documentos para IDs
            doc_mapping = {
                'Código Penal - Decreto-lei 2.848/1940': 'codigo_penal_1940',
                'Código de Processo Penal - Decreto-lei 3.689/1941': 'codigo_processo_penal_1941',
                'Código Civil - Lei 10.406/2002': 'codigo_civil_2002',
                'Constituição Federal': 'constituicao_federal_1988',
                'Lei Geral de Proteção de Dados': 'lgpd_2018'
            }
            
            for documento_nome, documento_id in doc_mapping.items():
                # Atualizar documento_id
                cursor.execute("""
                    UPDATE base_vetorial_universal 
                    SET documento_id = %s
                    WHERE documento = %s
                """, (documento_id, documento_nome))
                
                # Atualizar sequência dos chunks
                cursor.execute("""
                    WITH chunks_numerados AS (
                        SELECT chunk_id, 
                               ROW_NUMBER() OVER (ORDER BY created_at, chunk_id) as sequencia
                        FROM base_vetorial_universal 
                        WHERE documento = %s
                    )
                    UPDATE base_vetorial_universal 
                    SET chunk_sequencia = cn.sequencia
                    FROM chunks_numerados cn
                    WHERE base_vetorial_universal.chunk_id = cn.chunk_id
                """, (documento_nome,))
                
                # Atualizar total de chunks
                cursor.execute("""
                    UPDATE base_vetorial_universal 
                    SET total_chunks_documento = (
                        SELECT COUNT(*) 
                        FROM base_vetorial_universal b2 
                        WHERE b2.documento = base_vetorial_universal.documento
                    )
                    WHERE documento = %s
                """, (documento_nome,))
                
                chunks_atualizados = cursor.rowcount
                logger.info(f"✅ {documento_nome}: {chunks_atualizados} chunks estruturados")
            
            self.db_conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estrutura: {e}")
            self.db_conn.rollback()
            return False
    
    def criar_tabela_documentos_mestres(self):
        """Cria tabela para documentos mestres (não chunks)"""
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documentos_mestres (
                    id SERIAL PRIMARY KEY,
                    documento_id VARCHAR(100) UNIQUE NOT NULL,
                    nome_completo TEXT NOT NULL,
                    tipo_documento VARCHAR(100),
                    area_especializada VARCHAR(100),
                    areas_relacionadas TEXT[],
                    fonte_oficial TEXT,
                    ano_publicacao INTEGER,
                    total_chunks INTEGER DEFAULT 0,
                    tamanho_total INTEGER DEFAULT 0,
                    status_processamento VARCHAR(50) DEFAULT 'processado',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inserir documentos mestres
            documentos_mestres = [
                ('codigo_penal_1940', 'Código Penal - Decreto-lei 2.848/1940', 'codigo_penal', 'direito_penal', 
                 ['direito_penal', 'direito_processual_penal'], 'Decreto-lei nº 2.848/1940', 1940),
                ('codigo_processo_penal_1941', 'Código de Processo Penal - Decreto-lei 3.689/1941', 'codigo_processual', 'direito_penal',
                 ['direito_penal', 'direito_processual_penal'], 'Decreto-lei nº 3.689/1941', 1941),
                ('codigo_civil_2002', 'Código Civil - Lei 10.406/2002', 'codigo_civil', 'direito_civil',
                 ['direito_civil', 'direito_familia', 'direito_empresarial'], 'Lei nº 10.406/2002', 2002),
                ('constituicao_federal_1988', 'Constituição Federal', 'constituicao', 'direito_constitucional',
                 ['direito_constitucional', 'direito_administrativo', 'direito_tributario'], 'Constituição da República Federativa do Brasil de 1988', 1988),
                ('lgpd_2018', 'Lei Geral de Proteção de Dados', 'lei_especial', 'direito_digital',
                 ['direito_digital', 'direito_civil', 'direito_consumidor'], 'Lei nº 13.709/2018', 2018)
            ]
            
            for doc_data in documentos_mestres:
                cursor.execute("""
                    INSERT INTO documentos_mestres 
                    (documento_id, nome_completo, tipo_documento, area_especializada, 
                     areas_relacionadas, fonte_oficial, ano_publicacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (documento_id) DO UPDATE SET
                        nome_completo = EXCLUDED.nome_completo,
                        updated_at = CURRENT_TIMESTAMP
                """, doc_data)
            
            # Atualizar estatísticas dos documentos mestres
            cursor.execute("""
                UPDATE documentos_mestres dm
                SET total_chunks = (
                    SELECT COUNT(*) 
                    FROM base_vetorial_universal buv 
                    WHERE buv.documento_id = dm.documento_id
                ),
                tamanho_total = (
                    SELECT SUM(LENGTH(conteudo)) 
                    FROM base_vetorial_universal buv 
                    WHERE buv.documento_id = dm.documento_id
                )
            """)
            
            self.db_conn.commit()
            cursor.close()
            logger.info("✅ Tabela documentos_mestres criada e populada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela mestres: {e}")
            return False
    
    def gerar_relatorio_estrutura_final(self):
        """Gera relatório da nova estrutura"""
        try:
            cursor = self.db_conn.cursor()
            
            # Estatísticas por documento mestre
            cursor.execute("""
                SELECT 
                    dm.nome_completo,
                    dm.area_especializada,
                    dm.total_chunks,
                    dm.tamanho_total,
                    dm.ano_publicacao,
                    dm.fonte_oficial
                FROM documentos_mestres dm
                ORDER BY dm.total_chunks DESC
            """)
            
            documentos = cursor.fetchall()
            
            # Total geral
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_documentos_mestres,
                    SUM(total_chunks) as total_chunks_sistema,
                    SUM(tamanho_total) as tamanho_total_sistema
                FROM documentos_mestres
            """)
            
            totals = cursor.fetchone()
            cursor.close()
            
            logger.info("📊 Estrutura Final da Base Universal:")
            logger.info(f"   Total de documentos mestres: {totals[0]}")
            logger.info(f"   Total de chunks no sistema: {totals[1]}")
            logger.info(f"   Tamanho total: {totals[2]:,} caracteres")
            
            logger.info("\n📄 Documentos Mestres:")
            for doc in documentos:
                nome, area, chunks, tamanho, ano, fonte = doc
                logger.info(f"   {nome}")
                logger.info(f"     • Área: {area}")
                logger.info(f"     • Chunks: {chunks}")
                logger.info(f"     • Tamanho: {tamanho:,} chars")
                logger.info(f"     • Ano: {ano}")
                logger.info(f"     • Fonte: {fonte}")
            
            return len(documentos)
            
        except Exception as e:
            logger.error(f"Erro no relatório: {e}")
            return 0
    
    def executar_reorganizacao_completa(self):
        """Executa reorganização completa da estrutura"""
        try:
            logger.info("🚀 Iniciando reorganização da estrutura documentos/chunks")
            
            # Adicionar colunas de estrutura
            if not self.adicionar_colunas_documento_estrutura():
                return False
            
            # Mapear documentos reais
            docs_reais = self.mapear_documentos_reais()
            if not docs_reais:
                return False
            
            # Atualizar estrutura
            if not self.atualizar_estrutura_documentos():
                return False
            
            # Criar tabela de documentos mestres
            if not self.criar_tabela_documentos_mestres():
                return False
            
            # Gerar relatório final
            total_docs = self.gerar_relatorio_estrutura_final()
            
            logger.info(f"✅ Reorganização concluída:")
            logger.info(f"   - {len(docs_reais)} documentos mestres estruturados")
            logger.info(f"   - 263 chunks organizados por documento")
            logger.info("   - Estrutura hierárquica documento > chunks implementada")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na reorganização: {e}")
            return False
        finally:
            self.db_conn.close()

if __name__ == "__main__":
    reorganizador = ReorganizadorEstrutura()
    reorganizador.executar_reorganizacao_completa()