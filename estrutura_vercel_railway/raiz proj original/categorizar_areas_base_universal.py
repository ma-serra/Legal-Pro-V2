#!/usr/bin/env python3
"""
Categoriza documentos na base universal por área jurídica específica
Adiciona coluna area_especializada para identificar origem dos documentos
"""

import logging
import os
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategorizadorAreasUniversal:
    def __init__(self):
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
        
        # Mapeamento das 18 áreas jurídicas
        self.areas_juridicas = {
            'direito_penal': 'Direito Penal',
            'direito_civil': 'Direito Civil', 
            'direito_constitucional': 'Direito Constitucional',
            'direito_trabalhista': 'Direito Trabalhista',
            'direito_tributario': 'Direito Tributário',
            'direito_empresarial': 'Direito Empresarial',
            'direito_administrativo': 'Direito Administrativo',
            'direito_familia': 'Direito de Família',
            'direito_ambiental': 'Direito Ambiental',
            'direito_consumidor': 'Direito do Consumidor',
            'direito_previdenciario': 'Direito Previdenciário',
            'direito_digital': 'Direito Digital',
            'direito_internacional': 'Direito Internacional',
            'direito_agrario': 'Direito Agrário',
            'seguros': 'Direito de Seguros',
            'conflitos_mediacao': 'Conflitos e Mediação',
            'analise_riscos': 'Análise de Riscos',
            'direito_processual': 'Direito Processual'
        }
    
    def adicionar_coluna_area_especializada(self):
        """Adiciona coluna para identificar área de origem"""
        try:
            cursor = self.db_conn.cursor()
            
            # Verificar se coluna já existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'base_vetorial_universal' 
                AND column_name = 'area_especializada'
            """)
            
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE base_vetorial_universal 
                    ADD COLUMN area_especializada VARCHAR(100),
                    ADD COLUMN multiplas_areas TEXT[]
                """)
                logger.info("✅ Colunas area_especializada e multiplas_areas adicionadas")
            else:
                logger.info("Colunas já existem")
            
            self.db_conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar colunas: {e}")
            return False
    
    def categorizar_documentos_por_area(self):
        """Categoriza documentos existentes por área jurídica"""
        try:
            cursor = self.db_conn.cursor()
            
            # Categorizar Direito Penal
            cursor.execute("""
                UPDATE base_vetorial_universal 
                SET area_especializada = 'direito_penal',
                    multiplas_areas = ARRAY['direito_penal', 'direito_processual_penal']
                WHERE documento ILIKE '%penal%' 
                   OR documento ILIKE '%código penal%'
                   OR documento ILIKE '%processo penal%'
            """)
            penal_count = cursor.rowcount
            
            # Categorizar Direito Civil
            cursor.execute("""
                UPDATE base_vetorial_universal 
                SET area_especializada = 'direito_civil',
                    multiplas_areas = ARRAY['direito_civil', 'direito_familia', 'direito_empresarial']
                WHERE documento ILIKE '%civil%' 
                   OR documento ILIKE '%código civil%'
            """)
            civil_count = cursor.rowcount
            
            # Categorizar Direito Constitucional
            cursor.execute("""
                UPDATE base_vetorial_universal 
                SET area_especializada = 'direito_constitucional',
                    multiplas_areas = ARRAY['direito_constitucional', 'direito_administrativo', 'direito_tributario']
                WHERE documento ILIKE '%constituição%' 
                   OR documento ILIKE '%constitucional%'
            """)
            const_count = cursor.rowcount
            
            # Categorizar Direito Digital (LGPD)
            cursor.execute("""
                UPDATE base_vetorial_universal 
                SET area_especializada = 'direito_digital',
                    multiplas_areas = ARRAY['direito_digital', 'direito_civil', 'direito_consumidor']
                WHERE documento ILIKE '%lgpd%' 
                   OR documento ILIKE '%proteção de dados%'
                   OR documento ILIKE '%lei geral%'
            """)
            digital_count = cursor.rowcount
            
            self.db_conn.commit()
            cursor.close()
            
            logger.info(f"✅ Documentos categorizados:")
            logger.info(f"   - Direito Penal: {penal_count} documentos")
            logger.info(f"   - Direito Civil: {civil_count} documentos")
            logger.info(f"   - Direito Constitucional: {const_count} documentos")
            logger.info(f"   - Direito Digital: {digital_count} documentos")
            
            return penal_count + civil_count + const_count + digital_count
            
        except Exception as e:
            logger.error(f"Erro ao categorizar documentos: {e}")
            return 0
    
    def criar_indices_areas(self):
        """Cria índices para otimizar consultas por área"""
        try:
            cursor = self.db_conn.cursor()
            
            # Índice para área especializada
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_base_universal_area_especializada 
                ON base_vetorial_universal(area_especializada)
            """)
            
            # Índice para múltiplas áreas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_base_universal_multiplas_areas 
                ON base_vetorial_universal USING GIN(multiplas_areas)
            """)
            
            # Índice composto para consultas otimizadas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_base_universal_area_categoria 
                ON base_vetorial_universal(area_especializada, categoria)
            """)
            
            self.db_conn.commit()
            cursor.close()
            logger.info("✅ Índices de áreas criados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            return False
    
    def gerar_mapeamento_areas_documentos(self):
        """Gera mapeamento detalhado de áreas e documentos"""
        try:
            cursor = self.db_conn.cursor()
            
            # Estatísticas por área
            cursor.execute("""
                SELECT 
                    area_especializada,
                    COUNT(*) as total_documentos,
                    COUNT(DISTINCT documento) as tipos_documento,
                    array_agg(DISTINCT categoria) as categorias
                FROM base_vetorial_universal 
                WHERE area_especializada IS NOT NULL
                GROUP BY area_especializada
                ORDER BY COUNT(*) DESC
            """)
            
            stats_areas = cursor.fetchall()
            
            # Documentos que se aplicam a múltiplas áreas
            cursor.execute("""
                SELECT 
                    documento,
                    area_especializada,
                    multiplas_areas,
                    COUNT(*) as chunks
                FROM base_vetorial_universal 
                WHERE multiplas_areas IS NOT NULL
                GROUP BY documento, area_especializada, multiplas_areas
                ORDER BY COUNT(*) DESC
            """)
            
            docs_multiplos = cursor.fetchall()
            
            cursor.close()
            
            logger.info("📊 Mapeamento de Áreas na Base Universal:")
            for area, total, tipos, cats in stats_areas:
                area_nome = self.areas_juridicas.get(area, area)
                logger.info(f"   {area_nome}: {total} chunks, {tipos} documentos")
                logger.info(f"     Categorias: {cats}")
            
            logger.info("\n📄 Documentos Multi-Área:")
            for doc, area, multiplas, chunks in docs_multiplos:
                logger.info(f"   {doc}: {chunks} chunks")
                logger.info(f"     Área principal: {area}")
                logger.info(f"     Áreas relacionadas: {multiplas}")
            
            return len(stats_areas)
            
        except Exception as e:
            logger.error(f"Erro ao gerar mapeamento: {e}")
            return 0
    
    def executar_categorizacao_completa(self):
        """Executa categorização completa da base universal"""
        try:
            logger.info("🚀 Iniciando categorização por áreas da Base Universal")
            
            # Adicionar colunas
            if not self.adicionar_coluna_area_especializada():
                return False
            
            # Categorizar documentos
            docs_categorizados = self.categorizar_documentos_por_area()
            
            # Criar índices
            self.criar_indices_areas()
            
            # Gerar mapeamento
            areas_mapeadas = self.gerar_mapeamento_areas_documentos()
            
            logger.info(f"✅ Categorização concluída:")
            logger.info(f"   - {docs_categorizados} documentos categorizados")
            logger.info(f"   - {areas_mapeadas} áreas mapeadas")
            logger.info("   - Índices otimizados criados")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na categorização: {e}")
            return False
        finally:
            self.db_conn.close()

if __name__ == "__main__":
    categorizador = CategorizadorAreasUniversal()
    categorizador.executar_categorizacao_completa()