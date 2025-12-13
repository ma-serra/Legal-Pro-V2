#!/usr/bin/env python3
"""
Sistema de Upload Qdrant Integrado
Upload inteligente para a estrutura híbrida PostgreSQL + Qdrant Cloud
"""

import os
import psycopg2
import requests
import json
import logging
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentoUpload:
    nome: str
    conteudo: str
    area_especializada: str
    tipo_documento: str
    documento_pai_id: Optional[str] = None
    metadata: Optional[Dict] = None

class UploadQdrantIntegrado:
    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']
        self.qdrant_url = os.environ.get('QDRANT_URL')
        self.qdrant_key = os.environ.get('QDRANT_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        if self.openai_key:
            openai.api_key = self.openai_key
    
    def conectar_postgresql(self):
        """Conecta ao PostgreSQL"""
        return psycopg2.connect(self.db_url)
    
    def gerar_embedding(self, texto: str, modelo: str = "text-embedding-3-small") -> List[float]:
        """Gera embedding usando OpenAI"""
        try:
            if not self.openai_key:
                raise Exception("OpenAI API key não configurada")
            
            response = openai.embeddings.create(
                input=texto,
                model=modelo
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def chunkinizar_documento(self, documento: DocumentoUpload, tamanho_chunk: int = 1000) -> List[DocumentoUpload]:
        """Divide documento em chunks menores"""
        chunks = []
        conteudo = documento.conteudo
        
        # Dividir por parágrafos primeiro
        paragrafos = conteudo.split('\n\n')
        chunk_atual = ""
        numero_chunk = 1
        
        for paragrafo in paragrafos:
            if len(chunk_atual) + len(paragrafo) <= tamanho_chunk:
                chunk_atual += paragrafo + "\n\n"
            else:
                if chunk_atual.strip():
                    chunk_doc = DocumentoUpload(
                        nome=f"{documento.nome} - Chunk {numero_chunk}",
                        conteudo=chunk_atual.strip(),
                        area_especializada=documento.area_especializada,
                        tipo_documento="chunk",
                        documento_pai_id=documento.documento_pai_id,
                        metadata={
                            'chunk_numero': numero_chunk,
                            'documento_origem': documento.nome,
                            'is_chunk_filho': True
                        }
                    )
                    chunks.append(chunk_doc)
                    numero_chunk += 1
                
                chunk_atual = paragrafo + "\n\n"
        
        # Adicionar último chunk
        if chunk_atual.strip():
            chunk_doc = DocumentoUpload(
                nome=f"{documento.nome} - Chunk {numero_chunk}",
                conteudo=chunk_atual.strip(),
                area_especializada=documento.area_especializada,
                tipo_documento="chunk",
                documento_pai_id=documento.documento_pai_id,
                metadata={
                    'chunk_numero': numero_chunk,
                    'documento_origem': documento.nome,
                    'is_chunk_filho': True
                }
            )
            chunks.append(chunk_doc)
        
        logger.info(f"Documento dividido em {len(chunks)} chunks")
        return chunks
    
    def salvar_postgresql(self, documento: DocumentoUpload, embedding: List[float]) -> str:
        """Salva documento no PostgreSQL"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            # Gerar ID único
            conteudo_hash = hashlib.md5(documento.conteudo.encode()).hexdigest()
            chunk_id = f"{documento.area_especializada}_{conteudo_hash}_{int(datetime.now().timestamp())}"
            
            # Inserir na base vetorial universal
            cursor.execute("""
                INSERT INTO base_vetorial_universal (
                    chunk_id, titulo, conteudo, area_especializada, 
                    documento_pai_id, chunk_numero, is_chunk_filho, 
                    nivel_hierarquia, embedding_vetor, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                chunk_id,
                documento.nome,
                documento.conteudo,
                documento.area_especializada,
                documento.documento_pai_id,
                documento.metadata.get('chunk_numero', 1) if documento.metadata else 1,
                documento.metadata.get('is_chunk_filho', False) if documento.metadata else False,
                2 if documento.metadata and documento.metadata.get('is_chunk_filho') else 1,
                json.dumps(embedding) if embedding else None,
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"Documento salvo no PostgreSQL: {chunk_id}")
            return chunk_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao salvar no PostgreSQL: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def upload_qdrant(self, chunk_id: str, embedding: List[float], documento: DocumentoUpload) -> bool:
        """Faz upload para Qdrant Cloud"""
        try:
            if not self.qdrant_url or not self.qdrant_key:
                logger.warning("Qdrant não configurado, pulando upload")
                return True
            
            headers = {
                'api-key': self.qdrant_key,
                'Content-Type': 'application/json'
            }
            
            # Nome da collection baseado na área
            collection_name = f"juridico_{documento.area_especializada.replace(' ', '_').lower()}"
            
            # Verificar/criar collection
            self.garantir_collection_existe(collection_name, headers)
            
            # Gerar UUID válido para Qdrant
            qdrant_id = str(uuid.uuid4())
            
            # Preparar payload
            payload = {
                "points": [{
                    "id": qdrant_id,
                    "vector": embedding,
                    "payload": {
                        "titulo": documento.nome,
                        "area_especializada": documento.area_especializada,
                        "tipo_documento": documento.tipo_documento,
                        "documento_pai_id": documento.documento_pai_id,
                        "conteudo_preview": documento.conteudo[:200] + "..." if len(documento.conteudo) > 200 else documento.conteudo,
                        "metadata": documento.metadata or {},
                        "created_at": datetime.now().isoformat()
                    }
                }]
            }
            
            # Upload para Qdrant
            response = requests.put(
                f"{self.qdrant_url}/collections/{collection_name}/points",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Upload Qdrant bem-sucedido: {chunk_id}")
                return True
            else:
                logger.error(f"Erro no upload Qdrant: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao fazer upload para Qdrant: {e}")
            return False
    
    def garantir_collection_existe(self, collection_name: str, headers: Dict[str, str]):
        """Garante que a collection existe no Qdrant"""
        try:
            # Verificar se collection existe
            response = requests.get(
                f"{self.qdrant_url}/collections/{collection_name}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return  # Collection já existe
            
            # Criar collection
            collection_config = {
                "vectors": {
                    "size": 1536,  # OpenAI text-embedding-3-small
                    "distance": "Cosine"
                },
                "optimizers_config": {
                    "default_segment_number": 2
                },
                "replication_factor": 1
            }
            
            create_response = requests.put(
                f"{self.qdrant_url}/collections/{collection_name}",
                headers=headers,
                json=collection_config,
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                logger.info(f"Collection criada: {collection_name}")
            else:
                logger.error(f"Erro ao criar collection: {create_response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao verificar/criar collection: {e}")
    
    def processar_documento_completo(self, documento: DocumentoUpload, dividir_chunks: bool = True) -> Dict[str, Any]:
        """Processa documento completo com upload híbrido"""
        resultado = {
            'sucesso': False,
            'documento_pai_id': None,
            'chunks_processados': 0,
            'chunks_qdrant': 0,
            'erros': []
        }
        
        try:
            # Se é documento mestre, criar entrada na tabela documentos_mestres
            if not documento.documento_pai_id and documento.tipo_documento != "chunk":
                documento_pai_id = self.criar_documento_mestre(documento)
                documento.documento_pai_id = documento_pai_id
                resultado['documento_pai_id'] = documento_pai_id
            
            # Dividir em chunks se necessário
            if dividir_chunks and len(documento.conteudo) > 1000:
                chunks = self.chunkinizar_documento(documento)
            else:
                chunks = [documento]
            
            # Processar cada chunk
            for chunk in chunks:
                try:
                    # Gerar embedding
                    embedding = self.gerar_embedding(chunk.conteudo)
                    
                    if not embedding:
                        resultado['erros'].append(f"Falha ao gerar embedding para {chunk.nome}")
                        continue
                    
                    # Salvar no PostgreSQL
                    chunk_id = self.salvar_postgresql(chunk, embedding)
                    resultado['chunks_processados'] += 1
                    
                    # Upload para Qdrant
                    if self.upload_qdrant(chunk_id, embedding, chunk):
                        resultado['chunks_qdrant'] += 1
                    
                except Exception as e:
                    erro_msg = f"Erro ao processar chunk {chunk.nome}: {e}"
                    resultado['erros'].append(erro_msg)
                    logger.error(erro_msg)
            
            resultado['sucesso'] = resultado['chunks_processados'] > 0
            
            logger.info(f"Processamento concluído: {resultado['chunks_processados']} chunks PostgreSQL, {resultado['chunks_qdrant']} chunks Qdrant")
            return resultado
            
        except Exception as e:
            erro_msg = f"Erro no processamento completo: {e}"
            resultado['erros'].append(erro_msg)
            logger.error(erro_msg)
            return resultado
    
    def criar_documento_mestre(self, documento: DocumentoUpload) -> str:
        """Cria entrada na tabela documentos_mestres"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        try:
            # Gerar ID único para documento mestre
            nome_hash = hashlib.md5(documento.nome.encode()).hexdigest()
            documento_id = f"{documento.area_especializada.replace(' ', '_').lower()}_{nome_hash}"
            
            # Verificar se já existe
            cursor.execute("SELECT documento_id FROM documentos_mestres WHERE documento_id = %s", (documento_id,))
            if cursor.fetchone():
                return documento_id
            
            # Inserir novo documento mestre
            cursor.execute("""
                INSERT INTO documentos_mestres (
                    documento_id, nome_completo, area_especializada, 
                    tipo_documento, ano_publicacao, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                documento_id,
                documento.nome,
                documento.area_especializada,
                documento.tipo_documento,
                datetime.now().year,
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"Documento mestre criado: {documento_id}")
            return documento_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar documento mestre: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def upload_arquivo_texto(self, arquivo_path: str, area_especializada: str, tipo_documento: str = "legislacao") -> Dict[str, Any]:
        """Upload de arquivo de texto"""
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            nome_arquivo = os.path.basename(arquivo_path)
            
            documento = DocumentoUpload(
                nome=nome_arquivo,
                conteudo=conteudo,
                area_especializada=area_especializada,
                tipo_documento=tipo_documento
            )
            
            return self.processar_documento_completo(documento)
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo: {e}")
            return {'sucesso': False, 'erros': [str(e)]}
    
    def upload_texto_direto(self, titulo: str, conteudo: str, area_especializada: str, tipo_documento: str = "documento") -> Dict[str, Any]:
        """Upload de texto direto"""
        documento = DocumentoUpload(
            nome=titulo,
            conteudo=conteudo,
            area_especializada=area_especializada,
            tipo_documento=tipo_documento
        )
        
        return self.processar_documento_completo(documento)
    
    def sincronizar_postgresql_qdrant(self) -> Dict[str, Any]:
        """Sincroniza documentos do PostgreSQL para Qdrant"""
        conn = self.conectar_postgresql()
        cursor = conn.cursor()
        
        resultado = {
            'sincronizados': 0,
            'erros': 0,
            'detalhes': []
        }
        
        try:
            # Buscar documentos sem embedding no Qdrant
            cursor.execute("""
                SELECT chunk_id, titulo, conteudo, area_especializada, 
                       documento_pai_id, chunk_numero, is_chunk_filho,
                       embedding_vetor
                FROM base_vetorial_universal
                WHERE embedding_vetor IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 100
            """)
            
            documentos = cursor.fetchall()
            
            for doc in documentos:
                try:
                    chunk_id, titulo, conteudo, area, pai_id, chunk_num, is_filho, embedding_json = doc
                    
                    # Converter embedding de JSON
                    embedding = json.loads(embedding_json) if embedding_json else []
                    
                    if not embedding:
                        continue
                    
                    # Criar objeto documento para upload
                    documento = DocumentoUpload(
                        nome=titulo,
                        conteudo=conteudo,
                        area_especializada=area,
                        tipo_documento="chunk" if is_filho else "documento",
                        documento_pai_id=pai_id,
                        metadata={
                            'chunk_numero': chunk_num,
                            'is_chunk_filho': is_filho
                        }
                    )
                    
                    # Upload para Qdrant
                    if self.upload_qdrant(chunk_id, embedding, documento):
                        resultado['sincronizados'] += 1
                    else:
                        resultado['erros'] += 1
                        
                except Exception as e:
                    resultado['erros'] += 1
                    resultado['detalhes'].append(f"Erro em {chunk_id}: {e}")
            
            logger.info(f"Sincronização concluída: {resultado['sincronizados']} sincronizados, {resultado['erros']} erros")
            
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            resultado['detalhes'].append(f"Erro geral: {e}")
        finally:
            cursor.close()
            conn.close()
        
        return resultado

def executar_teste_upload():
    """Executa teste de upload"""
    uploader = UploadQdrantIntegrado()
    
    # Teste com texto simples
    resultado = uploader.upload_texto_direto(
        titulo="Teste de Upload Qdrant",
        conteudo="Este é um teste do sistema de upload integrado PostgreSQL + Qdrant Cloud. O sistema deve processar este texto, gerar embeddings e salvar em ambas as bases.",
        area_especializada="direito_constitucional",
        tipo_documento="teste"
    )
    
    print(f"Resultado do teste:")
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Chunks processados: {resultado['chunks_processados']}")
    print(f"Chunks Qdrant: {resultado['chunks_qdrant']}")
    
    if resultado['erros']:
        print(f"Erros: {resultado['erros']}")
    
    return resultado

if __name__ == "__main__":
    executar_teste_upload()