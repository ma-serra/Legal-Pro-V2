import os
import logging
import json
import numpy as np
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

class SimpleEmbedding:
    """
    Uma implementação simples de embedding que não depende de modelos externos.
    Usa técnicas básicas de processamento de texto.
    """
    
    def __init__(self, vector_size=512):
        self.vector_size = vector_size
        
    def encode(self, text):
        """
        Cria um pseudo-embedding para o texto usando hash.
        Isso é apenas uma aproximação para demonstração.
        
        Args:
            text: Texto para codificar
            
        Returns:
            Um vetor de tamanho vector_size
        """
        # Normaliza o texto
        text = text.lower()
        
        # Cria um hash do texto
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Converte o hash para um vetor de números
        seed = int.from_bytes(hash_bytes[:4], byteorder='big')
        np.random.seed(seed)
        
        # Gera um vetor pseudo-aleatório baseado no hash
        vector = np.random.normal(0, 1, self.vector_size)
        
        # Normaliza o vetor
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
        
    def get_sentence_embedding_dimension(self):
        return self.vector_size

class VetorialDB:
    """
    Versão simplificada do banco vetorial que não depende de serviços externos.
    
    Esta classe simula um banco vetorial em memória para fins de demonstração.
    """
    
    def __init__(self, collection_name="documentos", embedding_model=None):
        """
        Inicializa o banco vetorial em memória.
        
        Args:
            collection_name: Nome da coleção (apenas para consistência de API)
            embedding_model: Ignorado, usa SimpleEmbedding internamente
        """
        self.collection_name = collection_name
        self.embedding_model = SimpleEmbedding(vector_size=512)
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        
        # Armazenamento em memória
        self.documents = {}
        self.next_id = 1
        
        logger.info(f"Banco vetorial simplificado inicializado (coleção: {collection_name})")
        
    def _criar_collection(self):
        """Método mantido para compatibilidade de API"""
        pass  # Não faz nada, pois é tudo em memória
        
    def gerar_embedding(self, texto):
        """
        Gera um embedding para o texto usando SimpleEmbedding.
        
        Args:
            texto: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
        """
        return self.embedding_model.encode(texto).tolist()
        
    def indexar_documento(self, texto, metadados=None, id_doc=None):
        """
        Indexa um documento no banco em memória.
        
        Args:
            texto: Texto a ser indexado
            metadados: Dicionário com metadados adicionais
            id_doc: ID opcional para o documento
            
        Returns:
            ID do documento indexado
        """
        if metadados is None:
            metadados = {}
            
        # Certifica que o texto está nos metadados
        metadados["texto"] = texto
        
        try:
            # Gera embedding para o texto
            embedding = self.gerar_embedding(texto)
            
            # Usa o ID fornecido ou gera um novo
            doc_id = id_doc if id_doc is not None else self.next_id
            if id_doc is None:
                self.next_id += 1
                
            # Armazena o documento
            self.documents[doc_id] = {
                "vector": embedding,
                "payload": metadados
            }
            
            logger.info(f"Documento indexado com sucesso: ID={doc_id}")
            return {"status": "success", "id": doc_id}
            
        except Exception as e:
            logger.error(f"Erro ao indexar documento: {str(e)}")
            raise
            
    def _cosine_similarity(self, v1, v2):
        """Calcula a similaridade de cosseno entre dois vetores"""
        v1 = np.array(v1)
        v2 = np.array(v2)
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return np.dot(v1, v2) / (norm1 * norm2)
            
    def pesquisar_similares(self, query, limite=5, filter_condition=None):
        """
        Pesquisa documentos similares à query.
        
        Args:
            query: Texto da consulta
            limite: Número máximo de resultados
            filter_condition: Filtro opcional (ignorado nesta implementação simples)
            
        Returns:
            Lista de documentos similares com scores
        """
        try:
            # Gera embedding para a query
            query_vector = self.gerar_embedding(query)
            
            # Calcula similaridade com todos os documentos
            similarities = []
            for doc_id, doc_data in self.documents.items():
                score = self._cosine_similarity(query_vector, doc_data["vector"])
                similarities.append({
                    "id": doc_id,
                    "score": score,
                    "payload": doc_data["payload"]
                })
                
            # Ordena por score (decrescente) e limita o número de resultados
            similarities.sort(key=lambda x: x["score"], reverse=True)
            return similarities[:limite]
            
        except Exception as e:
            logger.error(f"Erro ao pesquisar documentos similares: {str(e)}")
            return []  # Retorna lista vazia em caso de erro
            
    def deletar_documento(self, id_doc):
        """
        Deleta um documento pelo ID.
        
        Args:
            id_doc: ID do documento a ser deletado
            
        Returns:
            True se deletado com sucesso
        """
        try:
            if id_doc in self.documents:
                del self.documents[id_doc]
                logger.info(f"Documento {id_doc} deletado com sucesso")
                return True
            else:
                logger.warning(f"Documento {id_doc} não encontrado para exclusão")
                return False
        except Exception as e:
            logger.error(f"Erro ao deletar documento {id_doc}: {str(e)}")
            raise
