#!/usr/bin/env python3
"""
Transferência rápida e otimizada das bases penal e civil para base universal
"""

import logging
import os
import psycopg2
import uuid
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferenciaRapida:
    def __init__(self):
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
    
    def transferir_direito_penal_sql(self):
        """Transfere via SQL direto para maior velocidade"""
        try:
            cursor = self.db_conn.cursor()
            
            # Inserir dados de direito penal diretamente
            cursor.execute("""
                INSERT INTO base_vetorial_universal 
                (chunk_id, documento, artigo, titulo, conteudo, categoria, 
                 areas_relacionadas, tipo_documento, fonte, prioridade, created_at)
                SELECT 
                    gen_random_uuid()::text as chunk_id,
                    COALESCE(referencia, 'Código Penal') as documento,
                    COALESCE(artigo_numero, 'N/A') as artigo,
                    COALESCE(titulo, 'Dispositivo Penal') as titulo,
                    conteudo,
                    CASE 
                        WHEN LOWER(COALESCE(capitulo, '')) LIKE '%crime%' THEN 'crimes_delitos'
                        WHEN LOWER(COALESCE(capitulo, '')) LIKE '%pena%' THEN 'penas_sancoes'
                        WHEN LOWER(COALESCE(capitulo, '')) LIKE '%processo%' THEN 'processo_penal'
                        ELSE 'direito_penal_geral'
                    END as categoria,
                    ARRAY['direito_penal', 'direito_criminal'] as areas_relacionadas,
                    COALESCE(tipo_documento, 'codigo_penal') as tipo_documento,
                    COALESCE(referencia, 'Código Penal Brasileiro') as fonte,
                    'alta' as prioridade,
                    CURRENT_TIMESTAMP as created_at
                FROM embeddings_direito_penal_integrado
                WHERE conteudo IS NOT NULL 
                AND LENGTH(TRIM(conteudo)) > 10
                ON CONFLICT (chunk_id) DO NOTHING
            """)
            
            penal_count = cursor.rowcount
            self.db_conn.commit()
            
            logger.info(f"✅ Transferidos {penal_count} documentos de Direito Penal via SQL")
            cursor.close()
            return penal_count
            
        except Exception as e:
            logger.error(f"Erro ao transferir Direito Penal: {e}")
            self.db_conn.rollback()
            return 0
    
    def transferir_direito_civil_sql(self):
        """Transfere via SQL direto para maior velocidade"""
        try:
            cursor = self.db_conn.cursor()
            
            # Inserir dados de direito civil diretamente
            cursor.execute("""
                INSERT INTO base_vetorial_universal 
                (chunk_id, documento, artigo, titulo, conteudo, categoria, 
                 areas_relacionadas, tipo_documento, fonte, prioridade, created_at)
                SELECT 
                    gen_random_uuid()::text as chunk_id,
                    COALESCE(COALESCE(referencia, source), 'Código Civil') as documento,
                    CASE 
                        WHEN COALESCE(conteudo, content) ~ 'Art\.?\s*(\d+)' 
                        THEN substring(COALESCE(conteudo, content) from 'Art\.?\s*(\d+)')
                        ELSE 'N/A'
                    END as artigo,
                    CASE 
                        WHEN LENGTH(split_part(COALESCE(conteudo, content), E'\n', 1)) BETWEEN 10 AND 200 
                        THEN split_part(COALESCE(conteudo, content), E'\n', 1)
                        ELSE 'Dispositivo Civil'
                    END as titulo,
                    COALESCE(conteudo, content) as conteudo,
                    CASE 
                        WHEN LOWER(COALESCE(conteudo, content)) LIKE '%pessoa%' THEN 'pessoa_personalidade'
                        WHEN LOWER(COALESCE(conteudo, content)) LIKE '%bem%' THEN 'bens_patrimonio'
                        WHEN LOWER(COALESCE(conteudo, content)) LIKE '%obrigação%' THEN 'obrigacoes_contratos'
                        WHEN LOWER(COALESCE(conteudo, content)) LIKE '%família%' THEN 'direito_familia'
                        ELSE 'direito_civil_geral'
                    END as categoria,
                    ARRAY['direito_civil', 'direito_empresarial'] as areas_relacionadas,
                    'codigo_civil' as tipo_documento,
                    COALESCE(COALESCE(referencia, source), 'Código Civil Brasileiro') as fonte,
                    'alta' as prioridade,
                    CURRENT_TIMESTAMP as created_at
                FROM embeddings_direito_civil
                WHERE COALESCE(conteudo, content) IS NOT NULL 
                AND LENGTH(TRIM(COALESCE(conteudo, content))) > 10
                ON CONFLICT (chunk_id) DO NOTHING
            """)
            
            civil_count = cursor.rowcount
            self.db_conn.commit()
            
            logger.info(f"✅ Transferidos {civil_count} documentos de Direito Civil via SQL")
            cursor.close()
            return civil_count
            
        except Exception as e:
            logger.error(f"Erro ao transferir Direito Civil: {e}")
            self.db_conn.rollback()
            return 0
    
    def verificar_transferencia(self):
        """Verifica resultado da transferência"""
        try:
            cursor = self.db_conn.cursor()
            
            # Contagem total
            cursor.execute("SELECT COUNT(*) FROM base_vetorial_universal")
            total = cursor.fetchone()[0]
            
            # Contagem por documento
            cursor.execute("""
                SELECT documento, COUNT(*) as chunks
                FROM base_vetorial_universal 
                GROUP BY documento 
                ORDER BY COUNT(*) DESC
            """)
            docs = cursor.fetchall()
            
            # Contagem por categoria
            cursor.execute("""
                SELECT categoria, COUNT(*) as chunks
                FROM base_vetorial_universal 
                GROUP BY categoria 
                ORDER BY COUNT(*) DESC
            """)
            cats = cursor.fetchall()
            
            cursor.close()
            
            logger.info(f"📊 Relatório da Base Universal:")
            logger.info(f"   Total de documentos: {total}")
            logger.info(f"   Documentos por tipo:")
            for doc, count in docs:
                logger.info(f"     - {doc}: {count} chunks")
            logger.info(f"   Categorias:")
            for cat, count in cats:
                logger.info(f"     - {cat}: {count} chunks")
            
            return total
            
        except Exception as e:
            logger.error(f"Erro ao verificar transferência: {e}")
            return 0
    
    def executar_transferencia_completa(self):
        """Executa transferência completa"""
        try:
            logger.info("🚀 Iniciando transferência rápida para Base Universal")
            
            # Transferir bases
            penal_count = self.transferir_direito_penal_sql()
            civil_count = self.transferir_direito_civil_sql()
            
            # Verificar resultado
            total = self.verificar_transferencia()
            
            logger.info(f"✅ Transferência concluída:")
            logger.info(f"   - Direito Penal: {penal_count} documentos")
            logger.info(f"   - Direito Civil: {civil_count} documentos")
            logger.info(f"   - Total na Base Universal: {total} documentos")
            
            return total
            
        except Exception as e:
            logger.error(f"Erro na transferência: {e}")
            return 0
        finally:
            self.db_conn.close()

if __name__ == "__main__":
    transferencia = TransferenciaRapida()
    transferencia.executar_transferencia_completa()