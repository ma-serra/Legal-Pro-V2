#!/usr/bin/env python3
"""
Transfere todos os documentos das bases direito_penal_integrado e direito_civil
para a base vetorial universal (juridico_base_universal)
"""

import logging
import os
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import openai
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferirBasesUniversal:
    def __init__(self):
        self.db_conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.qdrant_client = QdrantClient(
            url=os.environ['QDRANT_URL'],
            api_key=os.environ['QDRANT_API_KEY']
        )
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.collection = "juridico_base_universal"
    
    def transferir_direito_penal(self):
        """Transfere documentos da base direito_penal_integrado"""
        try:
            cursor = self.db_conn.cursor()
            
            # Buscar todos os documentos do direito penal
            cursor.execute("""
                SELECT id, conteudo, referencia, area_origem, tipo_documento,
                       artigo_numero, capitulo, titulo, livro, metadata
                FROM embeddings_direito_penal_integrado
                ORDER BY id
            """)
            
            documentos_penal = cursor.fetchall()
            logger.info(f"Encontrados {len(documentos_penal)} documentos de Direito Penal")
            
            chunks_transferidos = []
            points_qdrant = []
            
            for doc in documentos_penal:
                id_doc, conteudo, referencia, area_origem, tipo_documento, artigo_numero, capitulo, titulo, livro, metadata = doc
                
                # Criar chunk para base universal
                chunk_id = str(uuid.uuid4())
                
                chunk = {
                    'chunk_id': chunk_id,
                    'documento': referencia or 'Código Penal',
                    'artigo': artigo_numero or 'N/A',
                    'titulo': titulo or f"Artigo {artigo_numero}" if artigo_numero else "Dispositivo Penal",
                    'conteudo': conteudo,
                    'categoria': self._categorizar_penal(capitulo, titulo, artigo_numero),
                    'areas_relacionadas': ['direito_penal', 'direito_criminal', 'direito_processual_penal'],
                    'tipo_documento': tipo_documento or 'codigo_penal',
                    'fonte': referencia or 'Código Penal Brasileiro',
                    'prioridade': 'alta',
                    'origem': 'direito_penal_integrado',
                    'capitulo': capitulo,
                    'livro': livro
                }
                chunks_transferidos.append(chunk)
                
                # Gerar embedding para Qdrant
                try:
                    response = self.openai_client.embeddings.create(
                        input=conteudo,
                        model="text-embedding-3-small"
                    )
                    embedding = response.data[0].embedding
                    
                    point = PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload={
                            'conteudo': conteudo,
                            'titulo': chunk['titulo'],
                            'documento': chunk['documento'],
                            'artigo': chunk['artigo'],
                            'categoria': chunk['categoria'],
                            'areas_relacionadas': chunk['areas_relacionadas'],
                            'tipo_documento': chunk['tipo_documento'],
                            'fonte': chunk['fonte'],
                            'prioridade': chunk['prioridade'],
                            'origem': 'direito_penal_integrado',
                            'capitulo': capitulo,
                            'livro': livro,
                            'processado_em': datetime.now().isoformat()
                        }
                    )
                    points_qdrant.append(point)
                    
                except Exception as e:
                    logger.warning(f"Erro ao gerar embedding para documento {id_doc}: {e}")
            
            # Inserir chunks no PostgreSQL
            self._inserir_chunks_postgresql(chunks_transferidos)
            
            # Inserir pontos no Qdrant em lotes
            if points_qdrant:
                self._inserir_lotes_qdrant(points_qdrant)
            
            cursor.close()
            logger.info(f"✅ Transferidos {len(chunks_transferidos)} documentos de Direito Penal")
            return len(chunks_transferidos)
            
        except Exception as e:
            logger.error(f"Erro ao transferir Direito Penal: {e}")
            return 0
    
    def transferir_direito_civil(self):
        """Transfere documentos da base direito_civil"""
        try:
            cursor = self.db_conn.cursor()
            
            # Buscar todos os documentos do direito civil
            cursor.execute("""
                SELECT id, COALESCE(conteudo, content) as conteudo, 
                       COALESCE(referencia, source) as referencia,
                       area, documento_id, metadata
                FROM embeddings_direito_civil
                WHERE COALESCE(conteudo, content) IS NOT NULL
                ORDER BY id
            """)
            
            documentos_civil = cursor.fetchall()
            logger.info(f"Encontrados {len(documentos_civil)} documentos de Direito Civil")
            
            chunks_transferidos = []
            points_qdrant = []
            
            for doc in documentos_civil:
                id_doc, conteudo, referencia, area, documento_id, metadata = doc
                
                if not conteudo or len(conteudo.strip()) < 10:
                    continue
                
                # Criar chunk para base universal
                chunk_id = str(uuid.uuid4())
                
                chunk = {
                    'chunk_id': chunk_id,
                    'documento': referencia or 'Código Civil',
                    'artigo': self._extrair_artigo_civil(conteudo),
                    'titulo': self._extrair_titulo_civil(conteudo),
                    'conteudo': conteudo,
                    'categoria': self._categorizar_civil(conteudo),
                    'areas_relacionadas': ['direito_civil', 'direito_empresarial', 'direito_familia'],
                    'tipo_documento': 'codigo_civil',
                    'fonte': referencia or 'Código Civil Brasileiro',
                    'prioridade': 'alta',
                    'origem': 'direito_civil',
                    'documento_id': documento_id
                }
                chunks_transferidos.append(chunk)
                
                # Gerar embedding para Qdrant
                try:
                    response = self.openai_client.embeddings.create(
                        input=conteudo,
                        model="text-embedding-3-small"
                    )
                    embedding = response.data[0].embedding
                    
                    point = PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload={
                            'conteudo': conteudo,
                            'titulo': chunk['titulo'],
                            'documento': chunk['documento'],
                            'artigo': chunk['artigo'],
                            'categoria': chunk['categoria'],
                            'areas_relacionadas': chunk['areas_relacionadas'],
                            'tipo_documento': chunk['tipo_documento'],
                            'fonte': chunk['fonte'],
                            'prioridade': chunk['prioridade'],
                            'origem': 'direito_civil',
                            'documento_id': documento_id,
                            'processado_em': datetime.now().isoformat()
                        }
                    )
                    points_qdrant.append(point)
                    
                except Exception as e:
                    logger.warning(f"Erro ao gerar embedding para documento {id_doc}: {e}")
            
            # Inserir chunks no PostgreSQL
            self._inserir_chunks_postgresql(chunks_transferidos)
            
            # Inserir pontos no Qdrant em lotes
            if points_qdrant:
                self._inserir_lotes_qdrant(points_qdrant)
            
            cursor.close()
            logger.info(f"✅ Transferidos {len(chunks_transferidos)} documentos de Direito Civil")
            return len(chunks_transferidos)
            
        except Exception as e:
            logger.error(f"Erro ao transferir Direito Civil: {e}")
            return 0
    
    def _categorizar_penal(self, capitulo, titulo, artigo):
        """Categoriza documentos penais"""
        texto = f"{capitulo or ''} {titulo or ''}".lower()
        
        if any(palavra in texto for palavra in ['crime', 'delito', 'infração']):
            return 'crimes_delitos'
        elif any(palavra in texto for palavra in ['pena', 'punição', 'sanção']):
            return 'penas_sancoes'
        elif any(palavra in texto for palavra in ['processo', 'procedimento']):
            return 'processo_penal'
        elif any(palavra in texto for palavra in ['prisão', 'liberdade']):
            return 'prisao_liberdade'
        else:
            return 'direito_penal_geral'
    
    def _categorizar_civil(self, conteudo):
        """Categoriza documentos civis"""
        texto = conteudo.lower()
        
        if any(palavra in texto for palavra in ['pessoa', 'personalidade', 'capacidade']):
            return 'pessoa_personalidade'
        elif any(palavra in texto for palavra in ['bem', 'patrimônio', 'propriedade']):
            return 'bens_patrimonio'
        elif any(palavra in texto for palavra in ['obrigação', 'contrato', 'negócio']):
            return 'obrigacoes_contratos'
        elif any(palavra in texto for palavra in ['família', 'casamento', 'divórcio']):
            return 'direito_familia'
        elif any(palavra in texto for palavra in ['sucessão', 'herança', 'testamento']):
            return 'direito_sucessoes'
        else:
            return 'direito_civil_geral'
    
    def _extrair_artigo_civil(self, conteudo):
        """Extrai número do artigo do conteúdo civil"""
        import re
        match = re.search(r'Art\.?\s*(\d+)', conteudo, re.IGNORECASE)
        return match.group(1) if match else 'N/A'
    
    def _extrair_titulo_civil(self, conteudo):
        """Extrai título do conteúdo civil"""
        linhas = conteudo.split('\n')
        primeira_linha = linhas[0].strip()
        if len(primeira_linha) > 10 and len(primeira_linha) < 200:
            return primeira_linha
        return f"Dispositivo Civil"
    
    def _inserir_chunks_postgresql(self, chunks):
        """Insere chunks no PostgreSQL"""
        cursor = self.db_conn.cursor()
        
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO base_vetorial_universal 
                (chunk_id, documento, artigo, titulo, conteudo, categoria, 
                 areas_relacionadas, tipo_documento, fonte, prioridade)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    conteudo = EXCLUDED.conteudo,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                chunk['chunk_id'],
                chunk['documento'],
                chunk['artigo'],
                chunk['titulo'],
                chunk['conteudo'],
                chunk['categoria'],
                chunk['areas_relacionadas'],
                chunk['tipo_documento'],
                chunk['fonte'],
                chunk['prioridade']
            ))
        
        self.db_conn.commit()
        cursor.close()
    
    def _inserir_lotes_qdrant(self, points):
        """Insere pontos no Qdrant em lotes de 100"""
        lote_size = 100
        for i in range(0, len(points), lote_size):
            lote = points[i:i + lote_size]
            try:
                self.qdrant_client.upsert(
                    collection_name=self.collection,
                    points=lote
                )
                logger.info(f"Inserido lote {i//lote_size + 1}: {len(lote)} pontos")
            except Exception as e:
                logger.error(f"Erro ao inserir lote no Qdrant: {e}")
    
    def executar_transferencia(self):
        """Executa transferência completa"""
        try:
            logger.info("🚀 Iniciando transferência das bases para Universal")
            
            # Transferir Direito Penal
            total_penal = self.transferir_direito_penal()
            
            # Transferir Direito Civil  
            total_civil = self.transferir_direito_civil()
            
            # Verificar resultado final
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM base_vetorial_universal")
            total_final = cursor.fetchone()[0]
            cursor.close()
            
            logger.info(f"✅ Transferência concluída:")
            logger.info(f"   - Direito Penal: {total_penal} documentos")
            logger.info(f"   - Direito Civil: {total_civil} documentos")
            logger.info(f"   - Total na Base Universal: {total_final} documentos")
            
            return total_penal + total_civil
            
        except Exception as e:
            logger.error(f"Erro na transferência: {e}")
            return 0

if __name__ == "__main__":
    transferidor = TransferirBasesUniversal()
    transferidor.executar_transferencia()