"""
Módulo de Inferência BERT Português
Sistema de análise de documentos usando neuralmind/bert-base-portuguese-cased
"""

import os
import torch
import logging
from transformers import AutoTokenizer, AutoModel
# from sentence_transformers import SentenceTransformer  # Removido para economia de espaço
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BERTPortugueseInference:
    """
    Sistema de inferência usando BERT português para análise de documentos jurídicos
    """
    
    def __init__(self):
        """Inicializar o sistema BERT"""
        self.model_name = "neuralmind/bert-base-portuguese-cased"
        
        # Modelo BERT português será carregado sob demanda (otimizado)
        self.tokenizer = None
        self.bert_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"🤖 BERT Português inicializado - Device: {self.device}")
    
    def _load_bert_model(self):
        """Carregar modelo BERT português (lazy loading)"""
        if self.tokenizer is None or self.bert_model is None:
            try:
                logger.info(f"📥 Carregando modelo BERT: {self.model_name}")
                
                # Carregar tokenizer e modelo
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    trust_remote_code=True
                )
                
                self.bert_model = AutoModel.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                ).to(self.device)
                
                # Definir modo de avaliação
                self.bert_model.eval()
                
                logger.info("✅ Modelo BERT carregado com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar BERT: {e}")
                # Fallback para modelo alternativo
                self._load_fallback_model()
    
    # Método removido - usando apenas BERT português otimizado
    
    def _load_fallback_model(self):
        """Carregar modelo alternativo em caso de falha"""
        try:
            logger.info("🔄 Tentando modelo alternativo: distilbert-base-multilingual-cased")
            
            self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-multilingual-cased')
            self.bert_model = AutoModel.from_pretrained('distilbert-base-multilingual-cased').to(self.device)
            self.bert_model.eval()
            
            logger.info("✅ Modelo alternativo carregado")
            
        except Exception as e:
            logger.error(f"❌ Falha completa no carregamento de modelos: {e}")
    
    def extract_embeddings(self, text: str) -> Optional[np.ndarray]:
        """
        Extrair embeddings BERT de um texto
        
        Args:
            text (str): Texto para análise
            
        Returns:
            np.ndarray: Vetor de embeddings ou None se falhar
        """
        try:
            self._load_bert_model()
            
            if self.tokenizer is None or self.bert_model is None:
                logger.error("❌ Modelos BERT não carregados")
                return None
            
            # Tokenizar texto
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Gerar embeddings
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                
                # Usar o embedding da classe [CLS] ou pooling médio
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
                
                # Converter para numpy
                embeddings_np = embeddings.cpu().numpy()
                
            return embeddings_np
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair embeddings: {e}")
            return None
    
    def extract_sentence_embeddings(self, text: str) -> Optional[np.ndarray]:
        """
        Extrair embeddings usando BERT português (método unificado)
        
        Args:
            text (str): Texto para análise
            
        Returns:
            np.ndarray: Vetor de embeddings ou None se falhar
        """
        # Usar o método BERT padrão para economia de recursos
        return self.extract_embeddings(text)
    
    def analyze_legal_document(self, document_text: str) -> Dict[str, Any]:
        """
        Análise completa de documento jurídico usando BERT
        
        Args:
            document_text (str): Texto do documento
            
        Returns:
            Dict com análise completa
        """
        try:
            # Preprocessar texto (primeiros 2000 caracteres para análise inicial)
            text_sample = document_text[:2000] if len(document_text) > 2000 else document_text
            
            # Extrair diferentes tipos de embeddings
            bert_embeddings = self.extract_embeddings(text_sample)
            sentence_embeddings = self.extract_sentence_embeddings(text_sample)
            
            # Análise de características do documento
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'document_length': len(document_text),
                'sample_length': len(text_sample),
                'embeddings_extracted': {
                    'bert_available': bert_embeddings is not None,
                    'sentence_available': sentence_embeddings is not None,
                    'bert_dimensions': bert_embeddings.shape[0] if bert_embeddings is not None else 0,
                    'sentence_dimensions': sentence_embeddings.shape[0] if sentence_embeddings is not None else 0
                },
                'text_characteristics': {
                    'word_count': len(text_sample.split()),
                    'char_count': len(text_sample),
                    'avg_word_length': sum(len(word) for word in text_sample.split()) / len(text_sample.split()) if text_sample.split() else 0,
                    'contains_legal_terms': self._detect_legal_terms(text_sample)
                },
                'legal_analysis': self._analyze_legal_content(text_sample),
                'embeddings': {
                    'bert': bert_embeddings.tolist() if bert_embeddings is not None else None,
                    'sentence': sentence_embeddings.tolist() if sentence_embeddings is not None else None
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de documento: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'document_length': len(document_text) if document_text else 0
            }
    
    def _detect_legal_terms(self, text: str) -> Dict[str, Any]:
        """Detectar termos jurídicos específicos"""
        
        legal_terms = {
            'civil': ['contrato', 'obrigação', 'direito civil', 'responsabilidade civil', 'danos'],
            'penal': ['crime', 'delito', 'pena', 'código penal', 'processo penal', 'réu'],
            'trabalhista': ['clt', 'trabalhador', 'empregado', 'salário', 'direito do trabalho'],
            'constitucional': ['constituição', 'direitos fundamentais', 'constitucional'],
            'processual': ['processo', 'procedimento', 'recurso', 'petição', 'decisão judicial'],
            'administrativo': ['administração pública', 'ato administrativo', 'servidor público']
        }
        
        text_lower = text.lower()
        detected = {}
        
        for area, terms in legal_terms.items():
            matches = [term for term in terms if term in text_lower]
            if matches:
                detected[area] = {
                    'count': len(matches),
                    'terms_found': matches
                }
        
        return detected
    
    def _analyze_legal_content(self, text: str) -> Dict[str, Any]:
        """Análise de conteúdo jurídico específico"""
        
        # Padrões jurídicos comuns
        patterns = {
            'artigos_lei': len([w for w in text.split() if w.lower().startswith('art')]),
            'paragrafos': text.count('§'),
            'incisos': text.count('inciso'),
            'referencias_lei': len([w for w in text.split() if 'lei' in w.lower()]),
            'citacoes_jurisprudencia': text.lower().count('tribunal'),
            'mencoes_codigo': len([w for w in text.split() if 'código' in w.lower()])
        }
        
        # Classificação de complexidade
        complexity_score = sum(patterns.values())
        
        if complexity_score > 10:
            complexity = 'alta'
        elif complexity_score > 5:
            complexity = 'média'
        else:
            complexity = 'baixa'
        
        return {
            'patterns': patterns,
            'complexity_score': complexity_score,
            'complexity_level': complexity,
            'estimated_legal_density': min(complexity_score / len(text.split()) * 100, 100) if text.split() else 0
        }
    
    def compare_documents(self, doc1: str, doc2: str) -> Dict[str, Any]:
        """
        Comparar similaridade entre dois documentos usando embeddings BERT
        
        Args:
            doc1, doc2 (str): Textos dos documentos
            
        Returns:
            Dict com análise de similaridade
        """
        try:
            # Extrair embeddings dos dois documentos
            embeddings1 = self.extract_sentence_embeddings(doc1[:1000])
            embeddings2 = self.extract_sentence_embeddings(doc2[:1000])
            
            if embeddings1 is None or embeddings2 is None:
                return {
                    'error': 'Falha ao extrair embeddings',
                    'similarity_score': 0.0
                }
            
            # Calcular similaridade coseno
            similarity = np.dot(embeddings1, embeddings2) / (
                np.linalg.norm(embeddings1) * np.linalg.norm(embeddings2)
            )
            
            return {
                'similarity_score': float(similarity),
                'similarity_percentage': float(similarity * 100),
                'similarity_level': self._classify_similarity(similarity),
                'doc1_length': len(doc1),
                'doc2_length': len(doc2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na comparação de documentos: {e}")
            return {
                'error': str(e),
                'similarity_score': 0.0
            }
    
    def _classify_similarity(self, score: float) -> str:
        """Classificar nível de similaridade"""
        if score > 0.9:
            return 'muito_alta'
        elif score > 0.7:
            return 'alta'
        elif score > 0.5:
            return 'média'
        elif score > 0.3:
            return 'baixa'
        else:
            return 'muito_baixa'
    
    def get_model_info(self) -> Dict[str, Any]:
        """Informações sobre os modelos carregados"""
        return {
            'bert_model': self.model_name,
            'model': self.model_name,
            'device': str(self.device),
            'models_loaded': {
                'bert': self.bert_model is not None
            },
            'status': 'ready' if self.bert_model is not None else 'not_loaded'
        }

# Instância global para reutilização
bert_inference = BERTPortugueseInference()

def analyze_document_with_bert(document_text: str) -> Dict[str, Any]:
    """Função auxiliar para análise de documento"""
    return bert_inference.analyze_legal_document(document_text)

def compare_documents_with_bert(doc1: str, doc2: str) -> Dict[str, Any]:
    """Função auxiliar para comparação de documentos"""
    return bert_inference.compare_documents(doc1, doc2)

def get_bert_embeddings(text: str) -> Optional[np.ndarray]:
    """Função auxiliar para obter embeddings"""
    return bert_inference.extract_sentence_embeddings(text)