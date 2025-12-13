"""
Analisador Legal com processamento NLP otimizado para CPU
========================================================
Sistema de análise de documentos jurídicos usando técnicas de processamento 
de linguagem natural otimizadas para ambiente sem GPU.
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LegalAnalyzer:
    """
    Analisador de documentos jurídicos otimizado
    Análise baseada em padrões e heurísticas para documentos jurídicos
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões regex para diferentes tipos de entidades jurídicas
        self.patterns = self._initialize_patterns()
        
        # Classificadores por tipo de documento
        self.document_classifiers = self._initialize_classifiers()
        
        # Cache para evitar reprocessamento
        self.cache = {}
        
        self.logger.info("✅ LegalAnalyzer inicializado com otimizações para CPU")
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Inicializa padrões regex para extração de entidades"""
        return {
            'cpf': re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
            'cnpj': re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
            'rg': re.compile(r'\bRG:?\s*[\d\.\-X]+\b', re.IGNORECASE),
            'data': re.compile(r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4})\b'),
            'valor_monetario': re.compile(r'R\$\s*[\d\.,]+|\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*reais?\b', re.IGNORECASE),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'telefone': re.compile(r'\b(?:\(\d{2}\)\s*)?\d{4,5}-?\d{4}\b'),
            'endereco': re.compile(r'(?:Rua|Avenida|Av|R\.|Travessa|Tr\.)\s+[^,\n]+(?:,\s*\d+)?', re.IGNORECASE),
            'cep': re.compile(r'\b\d{5}-?\d{3}\b'),
            'processo': re.compile(r'\b\d{7}-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b'),
            'lei': re.compile(r'Lei\s+n[ºª°]?\s*[\d\.,]+(?:\/\d{2,4})?', re.IGNORECASE),
            'artigo': re.compile(r'art(?:igo)?\.?\s*\d+[ºª°]?(?:,\s*§\s*\d+[ºª°]?)?(?:,\s*inc(?:iso)?\.?\s*[IVX]+)?', re.IGNORECASE)
        }
    
    def _initialize_classifiers(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa classificadores baseados em palavras-chave"""
        return {
            'contrato': {
                'keywords': [
                    'contrato', 'contratante', 'contratado', 'cláusula', 'vigência',
                    'partes', 'objeto', 'prazo', 'valor', 'pagamento', 'rescisão',
                    'arrendamento', 'locação', 'prestação de serviços', 'compra e venda'
                ],
                'subcategorias': {
                    'arrendamento': ['arrendamento', 'arrendante', 'arrendatário', 'terra', 'hectare'],
                    'locacao': ['locação', 'locador', 'locatário', 'aluguel', 'imóvel'],
                    'prestacao_servicos': ['prestação', 'serviços', 'executar', 'atividade'],
                    'compra_venda': ['compra', 'venda', 'vendedor', 'comprador', 'propriedade']
                }
            },
            'peticao': {
                'keywords': [
                    'petição', 'requer', 'requerente', 'excelentíssimo', 'juiz',
                    'direito', 'preliminar', 'mérito', 'tutela', 'liminar',
                    'mandado', 'inicial', 'contestação', 'recurso'
                ],
                'subcategorias': {
                    'inicial': ['inicial', 'ação', 'autora', 'réu', 'causa de pedir'],
                    'contestacao': ['contestação', 'defesa', 'impugnação', 'refutação'],
                    'recurso': ['recurso', 'apelação', 'agravo', 'embargos', 'revista']
                }
            },
            'sentenca': {
                'keywords': [
                    'sentença', 'julgo', 'dispositivo', 'fundamentação', 'procedente',
                    'improcedente', 'parcialmente procedente', 'extingo', 'condeno',
                    'absolvo', 'decreto', 'decisão'
                ],
                'subcategorias': {
                    'procedente': ['julgo procedente', 'procedente o pedido', 'acolho'],
                    'improcedente': ['julgo improcedente', 'improcedente o pedido', 'rejeito'],
                    'parcial': ['parcialmente procedente', 'em parte procedente']
                }
            },
            'acordo': {
                'keywords': [
                    'acordo', 'transação', 'composição', 'consenso', 'conciliação',
                    'mediação', 'compromisso', 'ajuste', 'entendimento'
                ],
                'subcategorias': {
                    'extrajudicial': ['extrajudicial', 'particular', 'amigável'],
                    'judicial': ['judicial', 'homologação', 'termo', 'audiência']
                }
            }
        }
    
    def analyze_document(self, content: str, title: str = "Documento", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Análise completa de documento jurídico
        
        Args:
            content: Conteúdo do documento
            title: Título do documento
            
        Returns:
            Resultado completo da análise
        """
        start_time = time.time()
        
        try:
            # Configurações padrão se não fornecidas
            if config is None:
                config = {
                    'tipoDocumento': 'auto',
                    'extrairEntidades': True,
                    'classificarDocumento': True,
                    'gerarResumo': True,
                    'detectarProblemas': True,
                    'analiseSentimento': False,
                    'buscarSimilaridade': False
                }
            
            # Cache key baseado no hash do conteúdo e configurações
            cache_key = f"doc_{hash(content)}_{hash(str(config))}"
            if cache_key in self.cache:
                self.logger.info(f"📋 Usando resultado em cache para {title}")
                return self.cache[cache_key]
            
            self.logger.info(f"🔍 Iniciando análise de: {title} com configurações específicas")
            
            # 1. Pré-processamento
            processed_content = self._preprocess_text(content)
            
            # 2. Extração de entidades (se habilitada)
            entities = []
            if config.get('extrairEntidades', True):
                entities = self._extract_entities(processed_content)
            
            # 3. Classificação do documento (se habilitada)
            classification = {'categoria': 'indefinido', 'confianca': 0.0}
            if config.get('classificarDocumento', True):
                classification = self._classify_document(processed_content)
                # Se tipo específico foi escolhido, sobrescrever
                if config.get('tipoDocumento') and config['tipoDocumento'] != 'auto':
                    classification['categoria'] = config['tipoDocumento']
                    classification['forcado'] = True
            
            # 4. Análise específica por tipo
            specific_analysis = self._analyze_by_type_advanced(processed_content, classification['categoria'], config)
            
            # 5. Geração de resumo (se habilitada)
            summary = ''
            if config.get('gerarResumo', True):
                summary = self._generate_summary(processed_content, entities, classification)
            
            # 6. Análise de problemas jurídicos (se habilitada)
            legal_issues = []
            if config.get('detectarProblemas', True):
                legal_issues = self._identify_legal_issues_advanced(processed_content, classification['categoria'])
            
            # 7. Análise de sentimento jurídico (se habilitada)
            sentiment_analysis = {}
            if config.get('analiseSentimento', False):
                sentiment_analysis = self._analyze_legal_sentiment(processed_content, classification['categoria'])
            
            # 8. Busca por similaridade (se habilitada)
            similarity_analysis = {}
            if config.get('buscarSimilaridade', False):
                similarity_analysis = self._analyze_document_similarity(processed_content, title)
            
            # 9. Score de confiança geral
            confidence_score = self._calculate_confidence(entities, classification, specific_analysis)
            
            # Resultado final
            result = {
                'titulo': title,
                'status': 'concluida',
                'tempo_processamento': time.time() - start_time,
                'modelo_utilizado': 'legal_analyzer_v2.0',
                'score_confianca': confidence_score,
                'resumo_automatico': summary,
                'classificacao': classification,
                'entidades': entities,
                'analise_especifica': specific_analysis,
                'problemas_identificados': legal_issues,
                'analise_sentimento': sentiment_analysis,
                'analise_similaridade': similarity_analysis,
                'configuracoes_aplicadas': config,
                'estatisticas': {
                    'total_entidades': len(entities),
                    'total_palavras': len(processed_content.split()),
                    'total_caracteres': len(processed_content)
                },
                'metadados': {
                    'processado_em': datetime.now().isoformat(),
                    'versao_sistema': '2.1',
                    'motor_processamento': 'legal_analyzer_optimized',
                    'funcionalidades_ativas': [k for k, v in config.items() if v]
                }
            }
            
            # Armazenar em cache
            self.cache[cache_key] = result
            
            self.logger.info(f"✅ Análise concluída em {result['tempo_processamento']:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise: {e}")
            return {
                'titulo': title,
                'status': 'erro',
                'tempo_processamento': time.time() - start_time,
                'erro': str(e),
                'score_confianca': 0.0,
                'resumo_automatico': 'Erro no processamento do documento.',
                'entidades': [],
                'classificacao': {'categoria': 'erro', 'confianca': 0.0}
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Pré-processamento do texto"""
        # Normalizar espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remover caracteres especiais desnecessários
        text = re.sub(r'[^\w\s\.,;:!\?\-\(\)\/]', '', text)
        
        return text
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrai entidades do texto usando regex"""
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                entity = {
                    'tipo': entity_type.upper(),
                    'texto': match.group().strip(),
                    'posicao_inicio': match.start(),
                    'posicao_fim': match.end(),
                    'confianca': self._calculate_entity_confidence(entity_type, match.group()),
                    'contexto': self._extract_context(text, match.start(), match.end()),
                    'normalizada': self._normalize_entity(entity_type, match.group())
                }
                entities.append(entity)
        
        # Remover duplicatas e ordenar por posição
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x['posicao_inicio'])
        
        return entities
    
    def _calculate_entity_confidence(self, entity_type: str, text: str) -> float:
        """Calcula confiança da extração de entidade"""
        if entity_type == 'cpf':
            return 0.95 if self._validate_cpf(text) else 0.6
        elif entity_type == 'cnpj':
            return 0.95 if self._validate_cnpj(text) else 0.6
        elif entity_type == 'email':
            return 0.9
        elif entity_type == 'data':
            return 0.85 if len(text) > 8 else 0.6
        elif entity_type == 'valor_monetario':
            return 0.8
        else:
            return 0.7
    
    def _validate_cpf(self, cpf: str) -> bool:
        """Validação básica de CPF"""
        cpf = re.sub(r'[^\d]', '', cpf)
        return len(cpf) == 11 and not cpf == cpf[0] * 11
    
    def _validate_cnpj(self, cnpj: str) -> bool:
        """Validação básica de CNPJ"""
        cnpj = re.sub(r'[^\d]', '', cnpj)
        return len(cnpj) == 14
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extrai contexto ao redor da entidade"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _normalize_entity(self, entity_type: str, text: str) -> str:
        """Normaliza entidades extraídas"""
        if entity_type in ['cpf', 'cnpj']:
            return re.sub(r'[^\d]', '', text)
        elif entity_type == 'email':
            return text.lower()
        elif entity_type == 'telefone':
            return re.sub(r'[^\d]', '', text)
        else:
            return text.strip()
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove entidades duplicadas"""
        unique_entities = []
        seen = set()
        
        for entity in entities:
            key = (entity['tipo'], entity['normalizada'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classifica o tipo de documento"""
        text_lower = text.lower()
        scores = {}
        
        # Calcular score para cada categoria
        for category, config in self.document_classifiers.items():
            score = 0
            matched_keywords = []
            
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                # Normalizar score baseado no número total de keywords
                normalized_score = score / len(config['keywords'])
                scores[category] = {
                    'score': normalized_score,
                    'matched_keywords': matched_keywords
                }
        
        # Determinar categoria principal
        if scores:
            best_category = max(scores.keys(), key=lambda x: scores[x]['score'])
            best_score = scores[best_category]['score']
            
            # Determinar subcategoria
            subcategory = self._determine_subcategory(text_lower, best_category)
            
            return {
                'categoria': best_category,
                'subcategoria': subcategory,
                'confianca': min(best_score, 1.0),
                'todas_categorias': scores,
                'palavras_chave': scores[best_category]['matched_keywords']
            }
        else:
            return {
                'categoria': 'indefinido',
                'subcategoria': None,
                'confianca': 0.0,
                'todas_categorias': {},
                'palavras_chave': []
            }
    
    def _determine_subcategory(self, text: str, category: str) -> Optional[str]:
        """Determina subcategoria baseada na categoria principal"""
        if category not in self.document_classifiers:
            return None
        
        subcats = self.document_classifiers[category].get('subcategorias', {})
        subcat_scores = {}
        
        for subcat, keywords in subcats.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            if score > 0:
                subcat_scores[subcat] = score / len(keywords)
        
        if subcat_scores:
            return max(subcat_scores.keys(), key=lambda x: subcat_scores[x])
        
        return None
    
    def _analyze_by_type_advanced(self, text: str, document_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Análise específica avançada por tipo de documento"""
        if document_type == 'contrato':
            return self._analyze_contract_advanced(text, config)
        elif document_type == 'peticao':
            return self._analyze_petition_advanced(text, config)
        elif document_type == 'sentenca':
            return self._analyze_sentence_advanced(text, config)
        elif document_type == 'acordo':
            return self._analyze_agreement(text)
        else:
            return self._analyze_generic_document(text, config)
    
    def _analyze_by_type(self, text: str, document_type: str) -> Dict[str, Any]:
        """Análise específica por tipo de documento (método legado)"""
        return self._analyze_by_type_advanced(text, document_type, {})
    
    def _analyze_contract(self, text: str) -> Dict[str, Any]:
        """Análise específica de contratos"""
        clausulas = self._extract_clauses(text)
        partes = self._extract_parties(text)
        prazos = self._extract_deadlines(text)
        valores = self._extract_values(text)
        
        return {
            'tipo': 'contrato',
            'clausulas_identificadas': clausulas,
            'partes_contratuais': partes,
            'prazos_vigencia': prazos,
            'valores_identificados': valores,
            'total_clausulas': len(clausulas)
        }
    
    def _analyze_petition(self, text: str) -> Dict[str, Any]:
        """Análise específica de petições"""
        pedidos = self._extract_requests(text)
        fundamentos = self._extract_legal_grounds(text)
        
        return {
            'tipo': 'peticao',
            'pedidos_identificados': pedidos,
            'fundamentos_legais': fundamentos,
            'total_pedidos': len(pedidos)
        }
    
    def _analyze_sentence(self, text: str) -> Dict[str, Any]:
        """Análise específica de sentenças"""
        dispositivo = self._extract_dispositivo(text)
        fundamentacao = self._extract_fundamentacao(text)
        
        return {
            'tipo': 'sentenca',
            'dispositivo': dispositivo,
            'fundamentacao': fundamentacao,
            'resultado': self._determine_sentence_result(text)
        }
    
    def _analyze_agreement(self, text: str) -> Dict[str, Any]:
        """Análise específica de acordos"""
        termos = self._extract_agreement_terms(text)
        condicoes = self._extract_conditions(text)
        
        return {
            'tipo': 'acordo',
            'termos_acordo': termos,
            'condicoes': condicoes,
            'total_termos': len(termos)
        }
    
    def _extract_clauses(self, text: str) -> List[str]:
        """Extrai cláusulas de contratos"""
        # Padrões para identificar cláusulas
        clause_patterns = [
            r'cl[áa]usula\s+\d+[ªº°]?[:\-]\s*([^.]+)',
            r'parágrafo\s+\d+[ªº°]?[:\-]\s*([^.]+)',
            r'item\s+\d+[:\-]\s*([^.]+)'
        ]
        
        clauses = []
        for pattern in clause_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                clauses.append(match.group().strip())
        
        return clauses[:10]  # Limitar a 10 cláusulas principais
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extrai partes contratuais"""
        party_patterns = [
            r'(contratante|contratado|locador|locatário|arrendante|arrendatário|vendedor|comprador):\s*([^,\n]+)',
            r'(parte\s+\w+):\s*([^,\n]+)'
        ]
        
        parties = []
        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                parties.append(f"{match.group(1)}: {match.group(2).strip()}")
        
        return parties
    
    def _extract_deadlines(self, text: str) -> List[str]:
        """Extrai prazos e vigências"""
        deadline_patterns = [
            r'(prazo|vigência|duração)\s+de\s+([^,\n.]+)',
            r'(válido|vigente)\s+(?:por|até)\s+([^,\n.]+)',
            r'(vencimento|término)\s+em\s+([^,\n.]+)'
        ]
        
        deadlines = []
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                deadlines.append(f"{match.group(1)}: {match.group(2).strip()}")
        
        return deadlines
    
    def _extract_values(self, text: str) -> List[str]:
        """Extrai valores monetários com contexto"""
        value_matches = self.patterns['valor_monetario'].finditer(text)
        values = []
        
        for match in value_matches:
            context = self._extract_context(text, match.start(), match.end(), 30)
            values.append({
                'valor': match.group().strip(),
                'contexto': context
            })
        
        return values
    
    def _extract_requests(self, text: str) -> List[str]:
        """Extrai pedidos de petições"""
        request_patterns = [
            r'(requer|pede|solicita|pleiteia)[^.]+',
            r'(seja\s+\w+)[^.]+',
            r'(tutela\s+\w+)[^.]+'
        ]
        
        requests = []
        for pattern in request_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                requests.append(match.group().strip())
        
        return requests[:5]  # Limitar a 5 pedidos principais
    
    def _extract_legal_grounds(self, text: str) -> List[str]:
        """Extrai fundamentos legais"""
        legal_matches = self.patterns['lei'].finditer(text)
        article_matches = self.patterns['artigo'].finditer(text)
        
        grounds = []
        for match in legal_matches:
            context = self._extract_context(text, match.start(), match.end(), 50)
            grounds.append(context)
        
        for match in article_matches:
            context = self._extract_context(text, match.start(), match.end(), 50)
            grounds.append(context)
        
        return grounds[:10]
    
    def _extract_dispositivo(self, text: str) -> str:
        """Extrai dispositivo da sentença"""
        dispositivo_patterns = [
            r'(julgo\s+\w+)[^.]+',
            r'(condeno|absolvo|decreto)[^.]+',
            r'(extingo\s+o\s+processo)[^.]+'
        ]
        
        for pattern in dispositivo_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return "Dispositivo não identificado claramente"
    
    def _extract_fundamentacao(self, text: str) -> str:
        """Extrai fundamentação da sentença"""
        # Busca por seções de fundamentação
        fund_patterns = [
            r'(fundamentação|fundamentos?)[^.]{100,500}',
            r'(considerando\s+que)[^.]{100,500}',
            r'(pelos\s+motivos\s+expostos)[^.]{100,500}'
        ]
        
        for pattern in fund_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return "Fundamentação não identificada claramente"
    
    def _determine_sentence_result(self, text: str) -> str:
        """Determina o resultado da sentença"""
        text_lower = text.lower()
        
        if 'julgo procedente' in text_lower:
            return 'procedente'
        elif 'julgo improcedente' in text_lower:
            return 'improcedente'
        elif 'parcialmente procedente' in text_lower:
            return 'parcialmente_procedente'
        elif 'extingo' in text_lower:
            return 'extincao'
        else:
            return 'indeterminado'
    
    def _extract_agreement_terms(self, text: str) -> List[str]:
        """Extrai termos do acordo"""
        term_patterns = [
            r'(ficam\s+acordados?)[^.]+',
            r'(comprometem-se)[^.]+',
            r'(as\s+partes\s+\w+)[^.]+'
        ]
        
        terms = []
        for pattern in term_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                terms.append(match.group().strip())
        
        return terms
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extrai condições do acordo"""
        condition_patterns = [
            r'(desde\s+que)[^.]+',
            r'(condicionado\s+a)[^.]+',
            r'(caso\s+\w+)[^.]+'
        ]
        
        conditions = []
        for pattern in condition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conditions.append(match.group().strip())
        
        return conditions
    
    def _generate_summary(self, text: str, entities: List, classification: Dict) -> str:
        """Gera resumo automático do documento"""
        doc_type = classification.get('categoria', 'documento')
        doc_subtype = classification.get('subcategoria', '')
        
        # Estatísticas básicas
        word_count = len(text.split())
        entity_count = len(entities)
        
        # Entidades principais
        main_entities = []
        for entity in entities[:5]:  # Top 5 entidades
            if entity['confianca'] > 0.7:
                main_entities.append(f"{entity['tipo']}: {entity['texto']}")
        
        # Gerar resumo baseado no tipo
        if doc_type == 'contrato':
            summary = f"Contrato {doc_subtype if doc_subtype else 'genérico'} identificado com {entity_count} entidades extraídas. "
            summary += f"Documento contém {word_count} palavras. "
            if main_entities:
                summary += f"Principais elementos: {', '.join(main_entities[:3])}."
        
        elif doc_type == 'peticao':
            summary = f"Petição {doc_subtype if doc_subtype else 'genérica'} com {word_count} palavras. "
            summary += f"Identificadas {entity_count} entidades relevantes. "
            if main_entities:
                summary += f"Elementos principais: {', '.join(main_entities[:3])}."
        
        elif doc_type == 'sentenca':
            summary = f"Sentença judicial com {word_count} palavras. "
            summary += f"Extraídas {entity_count} entidades do documento. "
            if main_entities:
                summary += f"Informações principais: {', '.join(main_entities[:3])}."
        
        else:
            summary = f"Documento jurídico ({doc_type}) com {word_count} palavras e {entity_count} entidades identificadas."
            if main_entities:
                summary += f" Elementos principais: {', '.join(main_entities[:3])}."
        
        return summary
    
    # ==================== ANÁLISES ESPECÍFICAS AVANÇADAS ====================
    
    def _identify_abusive_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Identifica cláusulas abusivas em contratos"""
        abusive_patterns = [
            {
                'pattern': r'(exclusão|isenção)\s+(?:total|completa)\s+de\s+responsabilidade',
                'tipo': 'Exclusão total de responsabilidade',
                'gravidade': 'alta',
                'explicacao': 'Cláusula que exclui totalmente a responsabilidade pode ser considerada abusiva'
            },
            {
                'pattern': r'juros\s+(?:de\s+)?(?:\d+%|\d+\s+por\s+cento)\s+(?:ao\s+mês|mensais?)',
                'tipo': 'Juros excessivos',
                'gravidade': 'media',
                'explicacao': 'Verificar se os juros estão dentro dos limites legais'
            },
            {
                'pattern': r'(multa|penalidade)\s+(?:de\s+)?(?:\d+%|\d+\s+por\s+cento)',
                'tipo': 'Multa desproporcional',
                'gravidade': 'media',
                'explicacao': 'Multas excessivas podem ser consideradas abusivas'
            }
        ]
        
        abusive_clauses = []
        for pattern_info in abusive_patterns:
            matches = re.finditer(pattern_info['pattern'], text, re.IGNORECASE)
            for match in matches:
                context = self._extract_context(text, match.start(), match.end(), 100)
                abusive_clauses.append({
                    'texto': match.group().strip(),
                    'tipo': pattern_info['tipo'],
                    'gravidade': pattern_info['gravidade'],
                    'explicacao': pattern_info['explicacao'],
                    'contexto': context,
                    'posicao': match.start()
                })
        
        return abusive_clauses
    
    def _classify_contract_type(self, text: str) -> Dict[str, Any]:
        """Classifica o tipo específico de contrato"""
        contract_types = {
            'arrendamento_rural': {
                'keywords': ['arrendamento', 'terra', 'hectare', 'produção', 'safra', 'agrícola'],
                'confidence_threshold': 3
            },
            'locacao_urbana': {
                'keywords': ['locação', 'imóvel', 'aluguel', 'urbano', 'residencial', 'comercial'],
                'confidence_threshold': 3
            },
            'prestacao_servicos': {
                'keywords': ['prestação', 'serviços', 'executar', 'atividade', 'prazo', 'remuneração'],
                'confidence_threshold': 3
            }
        }
        
        text_lower = text.lower()
        best_match = {'tipo': 'generico', 'confianca': 0.0, 'keywords_encontradas': []}
        
        for contract_type, config in contract_types.items():
            matches = 0
            found_keywords = []
            
            for keyword in config['keywords']:
                if keyword in text_lower:
                    matches += 1
                    found_keywords.append(keyword)
            
            if matches >= config['confidence_threshold']:
                confidence = min(matches / len(config['keywords']), 1.0)
                if confidence > best_match['confianca']:
                    best_match = {
                        'tipo': contract_type,
                        'confianca': confidence,
                        'keywords_encontradas': found_keywords
                    }
        
        return best_match
    
    def _analyze_legal_sentiment(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Análise de sentimento jurídico"""
        sentiment_indicators = {
            'positivo': ['procedente', 'acolho', 'reconheço', 'concedo', 'favorável'],
            'negativo': ['improcedente', 'rejeito', 'nego', 'desfavorável', 'inadmissível'],
            'neutro': ['analiso', 'considero', 'verifico', 'examino', 'observo'],
            'assertivo': ['determino', 'ordeno', 'condeno', 'declaro', 'julgo'],
            'cauteloso': ['pode', 'talvez', 'possível', 'provável', 'eventual']
        }
        
        text_lower = text.lower()
        sentiment_scores = {}
        
        for sentiment, words in sentiment_indicators.items():
            score = sum(1 for word in words if word in text_lower)
            sentiment_scores[sentiment] = score
        
        total_indicators = sum(sentiment_scores.values())
        if total_indicators == 0:
            return {'tom_predominante': 'neutro', 'confianca': 0.5, 'detalhes': sentiment_scores}
        
        predominant = max(sentiment_scores.keys(), key=lambda x: sentiment_scores[x])
        confidence = sentiment_scores[predominant] / total_indicators
        
        return {
            'tom_predominante': predominant,
            'confianca': confidence,
            'detalhes': sentiment_scores,
            'interpretacao': self._interpret_legal_sentiment(predominant, doc_type)
        }
    
    def _interpret_legal_sentiment(self, sentiment: str, doc_type: str) -> str:
        """Interpreta sentimento no contexto jurídico"""
        interpretations = {
            'contrato': {
                'positivo': 'Linguagem colaborativa e equilibrada',
                'negativo': 'Termos restritivos ou punitivos',
                'assertivo': 'Cláusulas claras e determinativas',
                'cauteloso': 'Linguagem defensiva ou condicional'
            },
            'peticao': {
                'positivo': 'Argumentação confiante',
                'negativo': 'Tom crítico ou contestatório',
                'assertivo': 'Pedidos claros e diretos',
                'cauteloso': 'Argumentação defensiva'
            },
            'sentenca': {
                'positivo': 'Decisão favorável à parte',
                'negativo': 'Decisão desfavorável',
                'assertivo': 'Decisão firme e clara',
                'cauteloso': 'Decisão ponderada'
            }
        }
        
        return interpretations.get(doc_type, {}).get(sentiment, 'Tom neutro')
    
    def _analyze_document_similarity(self, text: str, title: str) -> Dict[str, Any]:
        """Análise de similaridade com documentos existentes"""
        # Extrair características únicas do documento
        characteristics = {
            'palavras_chave': self._extract_key_phrases(text),
            'estrutura': self._get_structure_fingerprint(text),
            'entidades_unicas': self._get_unique_entities(text)
        }
        
        # Simular documentos similares
        similar_docs = self._simulate_similar_documents(characteristics)
        
        return {
            'documentos_similares': similar_docs,
            'nivel_similaridade': 'medio' if similar_docs else 'baixo',
            'caracteristicas_comparadas': characteristics,
            'recomendacao': 'Verificar documentos similares para consistência' if similar_docs else 'Documento com características únicas'
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extrai frases-chave do documento"""
        key_patterns = [
            r'(?:cláusula|artigo|parágrafo)\s+\d+[^.]{20,100}',
            r'(?:considerando|visto|dado)\s+que[^.]{30,150}',
            r'(?:julgo|declaro|condeno)[^.]{20,100}'
        ]
        
        key_phrases = []
        for pattern in key_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                key_phrases.append(match.group().strip())
        
        return key_phrases[:5]
    
    def _get_structure_fingerprint(self, text: str) -> Dict[str, Any]:
        """Cria impressão digital da estrutura"""
        return {
            'comprimento': len(text),
            'paragrafos': len(text.split('\n\n')),
            'sentencas': len(re.findall(r'[.!?]+', text)),
            'numeros': len(re.findall(r'\d+', text))
        }
    
    def _get_unique_entities(self, text: str) -> List[str]:
        """Obtém entidades únicas do documento"""
        entities = self._extract_entities(text)
        unique_entities = []
        
        for entity in entities[:5]:
            if entity['tipo'] in ['CPF', 'CNPJ', 'PROCESSO']:
                unique_entities.append(f"{entity['tipo']}: {entity['normalizada']}")
        
        return unique_entities
    
    def _simulate_similar_documents(self, characteristics: Dict) -> List[Dict[str, Any]]:
        """Simula documentos similares"""
        if len(characteristics['palavras_chave']) > 3:
            return [
                {
                    'titulo': 'Documento Similar 1',
                    'similaridade': 0.78,
                    'data': '2024-01-15',
                    'motivo': 'Estrutura e palavras-chave similares'
                }
            ]
        return []
    
    # ==================== MÉTODOS AVANÇADOS POR TIPO ====================
    
    def _analyze_contract_advanced(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Análise avançada de contratos"""
        # Análise básica
        clausulas = self._extract_clauses(text)
        partes = self._extract_parties(text)
        prazos = self._extract_deadlines(text)
        valores = self._extract_values(text)
        
        # Análises específicas para contratos
        clausulas_abusivas = self._identify_abusive_clauses(text)
        tipos_contrato = self._classify_contract_type(text)
        conformidade_legal = self._check_legal_compliance(text, 'contrato')
        riscos_identificados = self._identify_contract_risks(text)
        
        return {
            'tipo': 'contrato',
            'subtipo': tipos_contrato,
            'clausulas_identificadas': clausulas,
            'clausulas_abusivas': clausulas_abusivas,
            'partes_contratuais': partes,
            'prazos_vigencia': prazos,
            'valores_identificados': valores,
            'conformidade_legal': conformidade_legal,
            'riscos_identificados': riscos_identificados,
            'total_clausulas': len(clausulas),
            'alertas_importantes': self._generate_contract_alerts(clausulas_abusivas, riscos_identificados)
        }
    
    def _analyze_petition_advanced(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Análise avançada de petições"""
        # Análise básica
        pedidos = self._extract_requests(text)
        fundamentos = self._extract_legal_grounds(text)
        
        # Análises específicas para petições
        pedidos_principais = self._identify_main_requests(text, pedidos)
        urgencia_prioridade = self._classify_petition_urgency(text)
        argumentos_centrais = self._summarize_central_arguments(text)
        qualidade_juridica = self._assess_legal_quality(text, 'peticao')
        
        return {
            'tipo': 'peticao',
            'pedidos_identificados': pedidos,
            'pedidos_principais': pedidos_principais,
            'fundamentos_legais': fundamentos,
            'urgencia_prioridade': urgencia_prioridade,
            'argumentos_centrais': argumentos_centrais,
            'qualidade_juridica': qualidade_juridica,
            'total_pedidos': len(pedidos),
            'recomendacoes': self._generate_petition_recommendations(urgencia_prioridade, qualidade_juridica)
        }
    
    def _analyze_sentence_advanced(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Análise avançada de sentenças"""
        # Análise básica
        dispositivo = self._extract_dispositivo(text)
        fundamentacao = self._extract_fundamentacao(text)
        resultado = self._determine_sentence_result(text)
        
        # Análises específicas para sentenças
        fundamentacao_detalhada = self._analyze_legal_reasoning(text)
        procedencia_classificacao = self._classify_sentence_merit(text, resultado)
        decisao_resumida = self._summarize_main_decision(text, dispositivo)
        impactos_juridicos = self._identify_legal_impacts(text, resultado)
        
        return {
            'tipo': 'sentenca',
            'dispositivo': dispositivo,
            'fundamentacao': fundamentacao,
            'fundamentacao_detalhada': fundamentacao_detalhada,
            'resultado': resultado,
            'procedencia_classificacao': procedencia_classificacao,
            'decisao_resumida': decisao_resumida,
            'impactos_juridicos': impactos_juridicos,
            'analise_decisao': self._generate_decision_analysis(resultado, fundamentacao_detalhada)
        }
    
    def _analyze_generic_document(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Análise genérica para documentos não específicos"""
        return {
            'tipo': 'generico',
            'elementos_juridicos': self._extract_legal_elements(text),
            'estrutura_documento': self._analyze_document_structure(text),
            'pontos_atencao': self._identify_attention_points(text)
        }
    
    # ==================== MÉTODOS DE SUPORTE AVANÇADOS ====================
    
    def _check_legal_compliance(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Verifica conformidade legal básica"""
        compliance_checks = {
            'contrato': [
                {
                    'item': 'Identificação das partes',
                    'pattern': r'(contratante|contratado|locador|locatário|arrendante|arrendatário)',
                    'obrigatorio': True
                },
                {
                    'item': 'Objeto do contrato',
                    'pattern': r'(objeto|finalidade|objetivo)',
                    'obrigatorio': True
                },
                {
                    'item': 'Prazo ou vigência',
                    'pattern': r'(prazo|vigência|duração|período)',
                    'obrigatorio': True
                }
            ]
        }
        
        checks = compliance_checks.get(doc_type, [])
        results = []
        compliance_score = 0
        
        for check in checks:
            found = bool(re.search(check['pattern'], text, re.IGNORECASE))
            results.append({
                'item': check['item'],
                'conforme': found,
                'obrigatorio': check['obrigatorio'],
                'status': 'OK' if found else ('CRÍTICO' if check['obrigatorio'] else 'ATENÇÃO')
            })
            
            if found:
                compliance_score += 1
        
        return {
            'score': compliance_score / len(checks) if checks else 1.0,
            'detalhes': results,
            'status_geral': 'Conforme' if compliance_score == len(checks) else 'Não conforme'
        }
    
    def _identify_contract_risks(self, text: str) -> List[Dict[str, Any]]:
        """Identifica riscos em contratos"""
        risk_patterns = [
            {
                'pattern': r'sem\s+garantia',
                'risco': 'Ausência de garantias',
                'nivel': 'medio',
                'recomendacao': 'Considerar inclusão de garantias adequadas'
            },
            {
                'pattern': r'prazo\s+indeterminado',
                'risco': 'Prazo indeterminado',
                'nivel': 'baixo',
                'recomendacao': 'Estabelecer prazos claros para maior segurança jurídica'
            }
        ]
        
        identified_risks = []
        for risk_info in risk_patterns:
            if re.search(risk_info['pattern'], text, re.IGNORECASE):
                identified_risks.append({
                    'risco': risk_info['risco'],
                    'nivel': risk_info['nivel'],
                    'recomendacao': risk_info['recomendacao']
                })
        
        return identified_risks
    
    def _generate_contract_alerts(self, abusive_clauses: List, risks: List) -> List[str]:
        """Gera alertas importantes para contratos"""
        alerts = []
        
        high_risk_clauses = [c for c in abusive_clauses if c['gravidade'] == 'alta']
        if high_risk_clauses:
            alerts.append(f"⚠️ {len(high_risk_clauses)} cláusula(s) potencialmente abusiva(s) identificada(s)")
        
        medium_risks = [r for r in risks if r['nivel'] == 'medio']
        if medium_risks:
            alerts.append(f"⚡ {len(medium_risks)} risco(s) de nível médio identificado(s)")
        
        if not abusive_clauses and not risks:
            alerts.append("✅ Nenhum risco crítico identificado na análise inicial")
        
        return alerts
    
    def _identify_main_requests(self, text: str, all_requests: List) -> List[Dict[str, Any]]:
        """Identifica pedidos principais em petições"""
        main_indicators = [
            'tutela antecipada', 'liminar', 'medida cautelar',
            'procedência', 'condenação', 'declaração',
            'anulação', 'rescisão', 'indenização'
        ]
        
        main_requests = []
        for request in all_requests:
            request_lower = request.lower()
            importance = 'secundario'
            
            for indicator in main_indicators:
                if indicator in request_lower:
                    importance = 'principal'
                    break
            
            main_requests.append({
                'texto': request,
                'importancia': importance,
                'categoria': self._categorize_request(request)
            })
        
        return main_requests
    
    def _categorize_request(self, request: str) -> str:
        """Categoriza tipo de pedido"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['tutela', 'liminar', 'cautelar']):
            return 'urgente'
        elif any(word in request_lower for word in ['procedência', 'julgar']):
            return 'merito'
        elif any(word in request_lower for word in ['condenação', 'indenização']):
            return 'condenatoria'
        elif any(word in request_lower for word in ['declaração', 'declarar']):
            return 'declaratoria'
        else:
            return 'outros'
    
    def _classify_petition_urgency(self, text: str) -> Dict[str, Any]:
        """Classifica urgência de petições"""
        urgency_indicators = {
            'muito_alta': ['tutela antecipada', 'liminar', 'perigo de dano', 'urgência', 'habeas'],
            'alta': ['prazo fatal', 'prescrição', 'decadência', 'recurso'],
            'media': ['contestação', 'impugnação', 'defesa'],
            'baixa': ['inicial', 'manifestação', 'informações']
        }
        
        text_lower = text.lower()
        urgency_score = 0
        found_indicators = []
        
        for level, indicators in urgency_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    if level == 'muito_alta':
                        urgency_score = max(urgency_score, 4)
                    elif level == 'alta':
                        urgency_score = max(urgency_score, 3)
                    elif level == 'media':
                        urgency_score = max(urgency_score, 2)
                    else:
                        urgency_score = max(urgency_score, 1)
                    found_indicators.append(indicator)
        
        urgency_levels = ['baixa', 'baixa', 'media', 'alta', 'muito_alta']
        return {
            'nivel': urgency_levels[min(urgency_score, 4)],
            'score': urgency_score,
            'indicadores': found_indicators
        }
    
    def _identify_legal_issues_advanced(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        """Identifica problemas jurídicos avançados"""
        issues = []
        
        # Problemas por tipo de documento
        if doc_type == 'contrato':
            issues.extend(self._identify_contract_issues(text))
        elif doc_type == 'peticao':
            issues.extend(self._identify_petition_issues(text))
        elif doc_type == 'sentenca':
            issues.extend(self._identify_sentence_issues(text))
        
        # Problemas gerais
        issues.extend(self._identify_general_issues(text))
        
        return issues
    
    def _identify_contract_issues(self, text: str) -> List[Dict[str, Any]]:
        """Identifica problemas específicos de contratos"""
        issues = []
        
        # Verificar cláusulas abusivas já identificadas
        abusive_clauses = self._identify_abusive_clauses(text)
        for clause in abusive_clauses:
            issues.append({
                'tipo': 'clausula_abusiva',
                'gravidade': clause['gravidade'],
                'descricao': clause['explicacao'],
                'localizacao': clause['posicao']
            })
        
        return issues
    
    def _identify_petition_issues(self, text: str) -> List[Dict[str, Any]]:
        """Identifica problemas específicos de petições"""
        issues = []
        
        # Verificar fundamentação legal
        legal_grounds = len(self.patterns['lei'].findall(text)) + len(self.patterns['artigo'].findall(text))
        if legal_grounds < 2:
            issues.append({
                'tipo': 'fundamentacao_fraca',
                'gravidade': 'alta',
                'descricao': 'Fundamentação legal insuficiente',
                'localizacao': 0
            })
        
        return issues
    
    def _identify_sentence_issues(self, text: str) -> List[Dict[str, Any]]:
        """Identifica problemas específicos de sentenças"""
        issues = []
        
        # Verificar dispositivo claro
        if not re.search(r'julgo|condeno|absolvo|extingo', text, re.IGNORECASE):
            issues.append({
                'tipo': 'dispositivo_unclear',
                'gravidade': 'alta',
                'descricao': 'Dispositivo da sentença não claramente identificado',
                'localizacao': 0
            })
        
        return issues
    
    def _identify_general_issues(self, text: str) -> List[Dict[str, Any]]:
        """Identifica problemas gerais"""
        issues = []
        
        # Inconsistências textuais
        inconsistencies = self._detect_text_inconsistencies(text)
        for inconsistency in inconsistencies:
            issues.append({
                'tipo': 'inconsistencia_textual',
                'gravidade': 'baixa',
                'descricao': inconsistency,
                'localizacao': 0
            })
        
        return issues
    
    def _detect_text_inconsistencies(self, text: str) -> List[str]:
        """Detecta inconsistências textuais"""
        inconsistencies = []
        
        # Verificar datas inconsistentes
        dates = self.patterns['data'].findall(text)
        if len(set(dates)) != len(dates) and len(dates) > 1:
            inconsistencies.append('Datas repetidas encontradas no documento')
        
        return inconsistencies
    
    # ==================== MÉTODOS ESPECÍFICOS PARA PETIÇÕES ====================
    
    def _summarize_central_arguments(self, text: str) -> List[Dict[str, Any]]:
        """Resume argumentos centrais de petições"""
        argument_patterns = [
            r'(?:considerando|visto|dado)\s+que[^.]{50,200}',
            r'(?:portanto|assim|desta\s+forma)[^.]{30,150}',
            r'(?:fundamento|base|razão)[^.]{40,180}'
        ]
        
        arguments = []
        for i, pattern in enumerate(argument_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                arguments.append({
                    'argumento': match.group().strip(),
                    'tipo': ['premissa', 'conclusao', 'fundamento'][i],
                    'posicao': match.start()
                })
        
        # Ordenar por posição e limitar
        arguments.sort(key=lambda x: x['posicao'])
        return arguments[:5]
    
    def _assess_legal_quality(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Avalia qualidade jurídica do documento"""
        quality_indicators = {
            'peticao': {
                'fundamentacao_legal': r'(?:lei|artigo|código|decreto)\s+n[ºª°]?\s*[\d\.]+',
                'jurisprudencia': r'(?:stf|stj|tj|tribunal)\s+[^.]{20,100}',
                'doutrina': r'(?:segundo|conforme|ensina)\s+\w+[^.]{20,100}',
                'pedido_claro': r'(?:requer|pede|solicita|pleiteia)\s+[^.]{30,}'
            }
        }
        
        indicators = quality_indicators.get(doc_type, {})
        quality_score = 0
        found_elements = {}
        
        for element, pattern in indicators.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            found_elements[element] = matches
            if matches > 0:
                quality_score += 1
        
        return {
            'score': quality_score / len(indicators) if indicators else 0.5,
            'elementos_encontrados': found_elements,
            'nivel': 'Alta' if quality_score >= len(indicators) * 0.8 else 'Média' if quality_score >= len(indicators) * 0.5 else 'Baixa'
        }
    
    def _generate_petition_recommendations(self, urgency: Dict, quality: Dict) -> List[str]:
        """Gera recomendações para petições"""
        recommendations = []
        
        if urgency['nivel'] in ['alta', 'muito_alta']:
            recommendations.append("⚡ Petição de alta urgência - verificar prazos processuais")
        
        if quality['score'] < 0.6:
            recommendations.append("📚 Considerar reforçar fundamentação legal")
        
        if quality['elementos_encontrados'].get('jurisprudencia', 0) == 0:
            recommendations.append("⚖️ Incluir jurisprudência relevante pode fortalecer a argumentação")
        
        return recommendations
    
    # ==================== MÉTODOS ESPECÍFICOS PARA SENTENÇAS ====================
    
    def _analyze_legal_reasoning(self, text: str) -> Dict[str, Any]:
        """Analisa fundamentação legal detalhada"""
        reasoning_elements = {
            'fatos': self._extract_facts(text),
            'direito_aplicavel': self._extract_applicable_law(text),
            'precedentes': self._extract_precedents(text),
            'argumentacao': self._extract_legal_reasoning_text(text)
        }
        
        return reasoning_elements
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extrai fatos relevantes"""
        fact_patterns = [
            r'(?:restou\s+comprovado|ficou\s+demonstrado|verificou-se)[^.]{30,150}',
            r'(?:conforme\s+(?:auto|prova|documento))[^.]{20,120}'
        ]
        
        facts = []
        for pattern in fact_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                facts.append(match.group().strip())
        
        return facts[:5]
    
    def _extract_applicable_law(self, text: str) -> List[str]:
        """Extrai direito aplicável"""
        law_matches = self.patterns['lei'].finditer(text)
        article_matches = self.patterns['artigo'].finditer(text)
        
        applicable_law = []
        for match in law_matches:
            context = self._extract_context(text, match.start(), match.end(), 80)
            applicable_law.append(context)
        
        for match in article_matches:
            context = self._extract_context(text, match.start(), match.end(), 80)
            applicable_law.append(context)
        
        return applicable_law[:8]
    
    def _extract_precedents(self, text: str) -> List[str]:
        """Extrai precedentes jurisprudenciais"""
        precedent_patterns = [
            r'(?:stf|supremo\s+tribunal\s+federal)[^.]{20,150}',
            r'(?:stj|superior\s+tribunal)[^.]{20,150}',
            r'(?:tj|tribunal\s+de\s+justiça)[^.]{20,150}'
        ]
        
        precedents = []
        for pattern in precedent_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                precedents.append(match.group().strip())
        
        return precedents[:3]
    
    def _extract_legal_reasoning_text(self, text: str) -> List[str]:
        """Extrai texto de argumentação jurídica"""
        reasoning_patterns = [
            r'(?:nesse\s+sentido|desta\s+forma|portanto)[^.]{40,200}',
            r'(?:considerando|tendo\s+em\s+vista)[^.]{40,200}'
        ]
        
        reasoning = []
        for pattern in reasoning_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                reasoning.append(match.group().strip())
        
        return reasoning[:5]
    
    def _classify_sentence_merit(self, text: str, result: str) -> Dict[str, Any]:
        """Classifica mérito da sentença detalhadamente"""
        merit_analysis = {
            'resultado_principal': result,
            'tipo_decisao': self._determine_decision_type(text),
            'fundamentos_principais': self._extract_main_grounds(text),
            'impacto_partes': self._analyze_impact_on_parties(text, result)
        }
        
        return merit_analysis
    
    def _determine_decision_type(self, text: str) -> str:
        """Determina tipo de decisão"""
        text_lower = text.lower()
        
        if 'extingo' in text_lower and 'mérito' not in text_lower:
            return 'extincao_sem_merito'
        elif 'julgo' in text_lower:
            return 'merito'
        elif 'homologação' in text_lower:
            return 'homologatoria'
        else:
            return 'outros'
    
    def _extract_main_grounds(self, text: str) -> List[str]:
        """Extrai fundamentos principais"""
        grounds_patterns = [
            r'(?:pelos\s+motivos\s+expostos|pelos\s+fundamentos)[^.]{50,200}',
            r'(?:ante\s+o\s+exposto|isto\s+posto)[^.]{30,150}'
        ]
        
        grounds = []
        for pattern in grounds_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                grounds.append(match.group().strip())
        
        return grounds[:3]
    
    def _analyze_impact_on_parties(self, text: str, result: str) -> Dict[str, Any]:
        """Analisa impacto nas partes"""
        text_lower = text.lower()
        
        impacts = {
            'autor': 'favoravel' if result in ['procedente', 'parcialmente_procedente'] else 'desfavoravel',
            'reu': 'desfavoravel' if result in ['procedente', 'parcialmente_procedente'] else 'favoravel',
            'custas': 'autor' if 'custas' in text_lower and 'autor' in text_lower else 'ré' if 'custas' in text_lower else 'indefinido',
            'honorarios': self._extract_fee_info(text)
        }
        
        return impacts
    
    def _extract_fee_info(self, text: str) -> str:
        """Extrai informações sobre honorários"""
        if 'honorários' in text.lower():
            fee_match = re.search(r'honorários[^.]{20,100}', text, re.IGNORECASE)
            return fee_match.group().strip() if fee_match else 'Mencionados'
        return 'Não mencionados'
    
    def _summarize_main_decision(self, text: str, dispositivo: str) -> str:
        """Resume decisão principal"""
        # Simplificar o dispositivo para um resumo claro
        if len(dispositivo) > 200:
            return dispositivo[:150] + "..."
        return dispositivo
    
    def _identify_legal_impacts(self, text: str, result: str) -> List[Dict[str, Any]]:
        """Identifica impactos jurídicos"""
        impacts = []
        
        # Impacto baseado no resultado
        if result == 'procedente':
            impacts.append({
                'tipo': 'Procedência total',
                'descricao': 'Todos os pedidos foram acolhidos',
                'consequencia': 'Direitos do autor reconhecidos integralmente'
            })
        elif result == 'parcialmente_procedente':
            impacts.append({
                'tipo': 'Procedência parcial',
                'descricao': 'Alguns pedidos foram acolhidos',
                'consequencia': 'Direitos parcialmente reconhecidos'
            })
        
        # Verificar outras consequências
        text_lower = text.lower()
        if 'condenação' in text_lower:
            impacts.append({
                'tipo': 'Condenação',
                'descricao': 'Há condenação pecuniária',
                'consequencia': 'Obrigação de pagamento estabelecida'
            })
        
        return impacts
    
    def _generate_decision_analysis(self, result: str, detailed_reasoning: Dict) -> Dict[str, Any]:
        """Gera análise da decisão"""
        return {
            'consistencia': 'Alta' if len(detailed_reasoning.get('direito_aplicavel', [])) > 2 else 'Média',
            'fundamentacao_adequada': len(detailed_reasoning.get('fatos', [])) > 0,
            'precedentes_utilizados': len(detailed_reasoning.get('precedentes', [])) > 0,
            'qualidade_geral': self._assess_decision_quality(result, detailed_reasoning)
        }
    
    def _assess_decision_quality(self, result: str, reasoning: Dict) -> str:
        """Avalia qualidade geral da decisão"""
        quality_score = 0
        
        if len(reasoning.get('fatos', [])) > 0:
            quality_score += 1
        if len(reasoning.get('direito_aplicavel', [])) > 2:
            quality_score += 1
        if len(reasoning.get('argumentacao', [])) > 0:
            quality_score += 1
        if result != 'indeterminado':
            quality_score += 1
        
        if quality_score >= 3:
            return 'Alta'
        elif quality_score >= 2:
            return 'Média'
        else:
            return 'Baixa'
    
    def _extract_legal_elements(self, text: str) -> List[str]:
        """Extrai elementos jurídicos gerais"""
        legal_elements = []
        
        # Combinação de padrões já existentes
        for pattern_name, pattern in self.patterns.items():
            if pattern_name in ['lei', 'artigo', 'processo']:
                matches = pattern.finditer(text)
                for match in matches:
                    legal_elements.append({
                        'tipo': pattern_name,
                        'texto': match.group().strip()
                    })
        
        return legal_elements[:10]
    
    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analisa estrutura do documento"""
        structure = {
            'paragrafos': len(text.split('\n\n')),
            'tem_numeracao': bool(re.search(r'\d+\.\s', text)),
            'tem_assinatura': bool(re.search(r'(assinatura|assinado)', text, re.IGNORECASE)),
            'tem_data': bool(self.patterns['data'].search(text)),
            'extensao': 'longo' if len(text) > 5000 else 'medio' if len(text) > 1000 else 'curto'
        }
        
        return structure
    
    def _identify_attention_points(self, text: str) -> List[str]:
        """Identifica pontos que merecem atenção"""
        attention_points = []
        
        if len(text) < 100:
            attention_points.append('Documento muito curto - verificar se está completo')
        
        if not self.patterns['data'].search(text):
            attention_points.append('Nenhuma data identificada no documento')
        
        return attention_points
    
    def _identify_legal_issues(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        """Identifica possíveis problemas jurídicos"""
        issues = []
        text_lower = text.lower()
        
        # Problemas gerais
        if 'sem garantia' in text_lower or 'isento de garantia' in text_lower:
            issues.append({
                'tipo': 'clausula_abusiva',
                'descricao': 'Possível cláusula de isenção de garantia',
                'gravidade': 'media',
                'sugestao': 'Revisar cláusulas de garantia conforme CDC'
            })
        
        if 'foro de' not in text_lower and doc_type == 'contrato':
            issues.append({
                'tipo': 'falta_clausula',
                'descricao': 'Foro de eleição não especificado',
                'gravidade': 'baixa',
                'sugestao': 'Incluir cláusula de foro de eleição'
            })
        
        # Problemas específicos por tipo
        if doc_type == 'contrato':
            if 'prazo' not in text_lower and 'vigência' not in text_lower:
                issues.append({
                    'tipo': 'falta_informacao',
                    'descricao': 'Prazo ou vigência não especificados',
                    'gravidade': 'alta',
                    'sugestao': 'Definir claramente prazo de vigência'
                })
        
        # Verificar datas inconsistentes
        dates = self.patterns['data'].findall(text)
        if len(dates) > 1:
            issues.append({
                'tipo': 'verificacao_datas',
                'descricao': f'Múltiplas datas encontradas ({len(dates)})',
                'gravidade': 'baixa',
                'sugestao': 'Verificar consistência entre as datas'
            })
        
        return issues
    
    def _calculate_confidence(self, entities: List, classification: Dict, specific_analysis: Dict) -> float:
        """Calcula score de confiança geral da análise"""
        # Score baseado em múltiplos fatores
        entity_score = min(len(entities) / 10, 1.0)  # Normalizado para 10 entidades
        classification_score = classification.get('confianca', 0.0)
        analysis_score = 0.8 if specific_analysis.get('tipo') != 'analise_generica' else 0.3
        
        # Média ponderada
        overall_score = (entity_score * 0.3 + classification_score * 0.5 + analysis_score * 0.2)
        
        return round(overall_score, 2)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        return {
            'nome': 'Legal Analyzer v2.1',
            'tipo': 'Regex + NLP Tradicional',
            'otimizado_para': 'Cloud Production',
            'motor_processamento': 'optimized_heuristics',
            'tipos_suportados': list(self.document_classifiers.keys()),
            'entidades_suportadas': list(self.patterns.keys()),
            'cache_ativo': len(self.cache) > 0
        }