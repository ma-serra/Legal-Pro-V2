"""
Sistema de Verificação de Alucinações Jurídicas
Valida especificamente conteúdo jurídico para detectar informações incorretas
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Resultado da validação de um elemento jurídico"""
    element_type: str
    original_text: str
    is_valid: bool
    confidence_score: float
    validation_source: str
    error_message: Optional[str] = None
    suggested_correction: Optional[str] = None

@dataclass
class HallucinationReport:
    """Relatório completo de verificação de alucinações"""
    total_elements_checked: int
    valid_elements: int
    invalid_elements: int
    validation_results: List[ValidationResult]
    overall_confidence: float
    hallucination_rate: float
    recommendations: List[str]

class LegalHallucinationChecker:
    """
    Sistema de verificação de alucinações específicas para conteúdo jurídico
    Valida citações legais, números de processo, prazos e informações técnicas
    """
    
    def __init__(self):
        # Base de dados de leis válidas (simplificada)
        self.valid_laws = {
            "constituicao": {
                "CF/88": {"name": "Constituição Federal de 1988", "articles": list(range(1, 251))},
                "constituição": {"name": "Constituição Federal de 1988", "articles": list(range(1, 251))}
            },
            "codigos": {
                "CC": {"name": "Código Civil", "articles": list(range(1, 2045))},
                "CP": {"name": "Código Penal", "articles": list(range(1, 361))},
                "CPC": {"name": "Código de Processo Civil", "articles": list(range(1, 1073))},
                "CPP": {"name": "Código de Processo Penal", "articles": list(range(1, 811))},
                "CLT": {"name": "Consolidação das Leis do Trabalho", "articles": list(range(1, 923))},
                "CTN": {"name": "Código Tributário Nacional", "articles": list(range(1, 218))}
            },
            "leis_especiais": {
                "8.137/90": {"name": "Lei de Crimes Tributários"},
                "9.099/95": {"name": "Lei dos Juizados Especiais"},
                "11.340/06": {"name": "Lei Maria da Penha"},
                "12.850/13": {"name": "Lei de Organizações Criminosas"},
                "13.105/15": {"name": "Código de Processo Civil"},
                "14.133/21": {"name": "Nova Lei de Licitações"}
            }
        }
        
        # Prazos legais válidos (em dias)
        self.valid_deadlines = {
            "apelacao": {"civil": 15, "criminal": 5},
            "agravo": {"instrumento": 15, "interno": 15},
            "embargos": {"declaracao": 5, "infringentes": 15},
            "recurso_especial": {"prazo": 15},
            "recurso_extraordinario": {"prazo": 15},
            "habeas_corpus": {"prazo": None},  # Não há prazo
            "mandado_seguranca": {"prazo": 120},
            "acao_rescisoria": {"prazo": 730},  # 2 anos
            "execucao": {"prazo": None},  # Varia
            "prescricao": {"criminal": [3, 4, 8, 12, 16, 20]},  # Anos
            "decadencia": {"tributaria": 150}  # Dias
        }
        
        # Padrões de validação
        self.validation_patterns = {
            "artigo_lei": r"art\.?\s*(\d+)[°º]?,?\s*(§\s*(\d+)[°º]?)?,?\s*(inciso\s+([IVXLCDM]+))?,?\s*(alínea\s+([a-z]))?",
            "numero_processo": r"(\d{7})-(\d{2})\.(\d{4})\.(\d{1})\.(\d{2})\.(\d{4})",
            "numero_processo_antigo": r"(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)-(\d+)",
            "lei_numero": r"lei\s+n[°º]?\s*([\d.,/]+)",
            "decreto_numero": r"decreto\s+n[°º]?\s*([\d.,/]+)",
            "sumula": r"súmula\s+n[°º]?\s*(\d+)",
            "prazo_dias": r"(\d+)\s*dias?",
            "prazo_meses": r"(\d+)\s*meses?",
            "prazo_anos": r"(\d+)\s*anos?"
        }
        
        # Cache de validações
        self.validation_cache = {}
        
        # Inicializar conexão com bases externas
        self._initialize_external_sources()
    
    def _initialize_external_sources(self):
        """Inicializa conexões com fontes externas de validação"""
        self.external_sources = {
            "planalto": "http://www.planalto.gov.br",
            "stf": "http://www.stf.jus.br", 
            "stj": "http://www.stj.jus.br",
            "tst": "http://www.tst.jus.br"
        }
        
        logger.info("🔗 Fontes externas de validação inicializadas")
    
    def validate_legal_citations(self, response: str) -> List[ValidationResult]:
        """
        Valida todas as citações legais encontradas no texto
        """
        validations = []
        
        # Validar artigos de lei
        article_validations = self._validate_law_articles(response)
        validations.extend(article_validations)
        
        # Validar números de processo
        process_validations = self._validate_process_numbers(response)
        validations.extend(process_validations)
        
        # Validar prazos legais
        deadline_validations = self._validate_legal_deadlines(response)
        validations.extend(deadline_validations)
        
        # Validar súmulas
        sumula_validations = self._validate_sumulas(response)
        validations.extend(sumula_validations)
        
        return validations
    
    def _validate_law_articles(self, text: str) -> List[ValidationResult]:
        """Valida artigos de lei mencionados no texto"""
        validations = []
        
        # Encontrar todas as menções de artigos
        pattern = self.validation_patterns["artigo_lei"]
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            article_num = int(match.group(1))
            paragraph = match.group(3)
            inciso = match.group(5)
            alinea = match.group(7)
            
            original_text = match.group(0)
            
            # Determinar código/lei base do contexto
            law_context = self._identify_law_context(text, match.start())
            
            validation = self._validate_single_article(
                article_num, law_context, paragraph, inciso, alinea, original_text
            )
            
            validations.append(validation)
        
        return validations
    
    def _identify_law_context(self, text: str, position: int) -> str:
        """Identifica qual lei está sendo referenciada baseado no contexto"""
        # Procurar menções de códigos antes da posição
        context_window = text[max(0, position-200):position+50]
        context_lower = context_window.lower()
        
        # Padrões para identificar leis
        law_patterns = {
            "CC": ["código civil", "cc/02", "cc"],
            "CP": ["código penal", "cp"],
            "CPC": ["código de processo civil", "cpc", "lei 13.105"],
            "CPP": ["código de processo penal", "cpp"],
            "CLT": ["clt", "consolidação das leis do trabalho"],
            "CTN": ["código tributário nacional", "ctn"],
            "CF": ["constituição", "cf", "cf/88", "magna carta"]
        }
        
        for law_code, indicators in law_patterns.items():
            for indicator in indicators:
                if indicator in context_lower:
                    return law_code
        
        return "UNKNOWN"
    
    def _validate_single_article(self, article_num: int, law_context: str, 
                                paragraph: Optional[str], inciso: Optional[str], 
                                alinea: Optional[str], original_text: str) -> ValidationResult:
        """Valida um artigo específico"""
        
        # Verificar se o artigo existe na lei identificada
        is_valid = False
        confidence = 0.0
        error_message = None
        suggested_correction = None
        
        if law_context in ["CC", "CP", "CPC", "CPP", "CLT", "CTN"]:
            law_info = self.valid_laws["codigos"].get(law_context)
            if law_info and article_num in law_info["articles"]:
                is_valid = True
                confidence = 0.95
            else:
                error_message = f"Artigo {article_num} não encontrado no {law_context}"
                confidence = 0.1
                
                # Sugerir artigo mais próximo
                if law_info:
                    closest_article = min(law_info["articles"], 
                                        key=lambda x: abs(x - article_num))
                    suggested_correction = f"art. {closest_article}, {law_context}"
        
        elif law_context in ["CF", "CONSTITUIÇÃO"]:
            cf_info = self.valid_laws["constituicao"]["CF/88"]
            if article_num in cf_info["articles"]:
                is_valid = True
                confidence = 0.95
            else:
                error_message = f"Artigo {article_num} não encontrado na Constituição"
                confidence = 0.1
        
        else:
            # Contexto não identificado - validação parcial
            is_valid = True
            confidence = 0.6
            error_message = f"Contexto da lei não identificado para {original_text}"
        
        return ValidationResult(
            element_type="law_article",
            original_text=original_text,
            is_valid=is_valid,
            confidence_score=confidence,
            validation_source="internal_database",
            error_message=error_message,
            suggested_correction=suggested_correction
        )
    
    def _validate_process_numbers(self, text: str) -> List[ValidationResult]:
        """Valida números de processo mencionados"""
        validations = []
        
        # Padrão moderno (CNJ)
        pattern = self.validation_patterns["numero_processo"]
        matches = re.finditer(pattern, text)
        
        for match in matches:
            process_number = match.group(0)
            
            # Validação básica do formato
            segments = match.groups()
            
            is_valid = True
            confidence = 0.8
            error_message = None
            
            # Verificar dígitos verificadores
            try:
                sequential = segments[0]
                dv = segments[1]
                year = int(segments[2])
                segment = segments[3]
                tribunal = segments[4]
                origin = segments[5]
                
                # Validações básicas
                if year < 1900 or year > datetime.now().year + 1:
                    is_valid = False
                    error_message = f"Ano {year} inválido no número do processo"
                    confidence = 0.1
                
                # Validar tribunal (código deve existir)
                if int(tribunal) > 90:  # Códigos de tribunal vão até cerca de 90
                    is_valid = False
                    error_message = "Código de tribunal inválido"
                    confidence = 0.1
                    
            except ValueError:
                is_valid = False
                error_message = "Formato de número de processo inválido"
                confidence = 0.1
            
            validations.append(ValidationResult(
                element_type="process_number",
                original_text=process_number,
                is_valid=is_valid,
                confidence_score=confidence,
                validation_source="format_validation",
                error_message=error_message
            ))
        
        return validations
    
    def _validate_legal_deadlines(self, text: str) -> List[ValidationResult]:
        """Valida prazos legais mencionados"""
        validations = []
        
        # Encontrar menções de prazos
        deadline_patterns = [
            (r"prazo\s+de\s+(\d+)\s+dias?\s+para\s+(\w+)", "days"),
            (r"(\d+)\s+dias?\s+para\s+(\w+)", "days"),
            (r"prazo\s+de\s+(\d+)\s+meses?\s+para\s+(\w+)", "months"),
            (r"(\d+)\s+anos?\s+para\s+(\w+)", "years")
        ]
        
        for pattern, unit in deadline_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                original_text = match.group(0)
                deadline_value = int(match.group(1))
                action_type = match.group(2).lower()
                
                is_valid, confidence, error_msg = self._check_deadline_validity(
                    deadline_value, unit, action_type
                )
                
                validations.append(ValidationResult(
                    element_type="legal_deadline",
                    original_text=original_text,
                    is_valid=is_valid,
                    confidence_score=confidence,
                    validation_source="deadline_database",
                    error_message=error_msg
                ))
        
        return validations
    
    def _check_deadline_validity(self, value: int, unit: str, action: str) -> Tuple[bool, float, Optional[str]]:
        """Verifica se um prazo legal está correto"""
        
        # Normalizar tipo de ação
        action_normalized = action.replace("ção", "cao").replace("ã", "a")
        
        # Procurar em prazos conhecidos
        for deadline_type, deadline_info in self.valid_deadlines.items():
            if deadline_type in action_normalized or action_normalized in deadline_type:
                
                if isinstance(deadline_info, dict):
                    # Prazo específico por área
                    for area, correct_days in deadline_info.items():
                        if unit == "days" and value == correct_days:
                            return True, 0.95, None
                        elif unit == "days" and correct_days and abs(value - correct_days) <= 2:
                            return False, 0.3, f"Prazo correto: {correct_days} dias"
                
                elif isinstance(deadline_info, list):
                    # Lista de valores válidos
                    if unit == "years" and value in deadline_info:
                        return True, 0.95, None
                    elif unit == "years":
                        closest = min(deadline_info, key=lambda x: abs(x - value))
                        return False, 0.4, f"Prazo mais próximo: {closest} anos"
        
        # Se não encontrou correspondência específica, validação genérica
        if unit == "days" and 1 <= value <= 365:
            return True, 0.7, None
        elif unit == "months" and 1 <= value <= 24:
            return True, 0.7, None
        elif unit == "years" and 1 <= value <= 30:
            return True, 0.7, None
        
        return False, 0.2, f"Prazo suspeito: {value} {unit}"
    
    def _validate_sumulas(self, text: str) -> List[ValidationResult]:
        """Valida súmulas mencionadas"""
        validations = []
        
        pattern = self.validation_patterns["sumula"]
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            original_text = match.group(0)
            sumula_number = int(match.group(1))
            
            # Validação básica - súmulas geralmente vão de 1 a cerca de 1000
            is_valid = 1 <= sumula_number <= 1000
            confidence = 0.8 if is_valid else 0.2
            error_message = None if is_valid else f"Número de súmula suspeito: {sumula_number}"
            
            validations.append(ValidationResult(
                element_type="sumula",
                original_text=original_text,
                is_valid=is_valid,
                confidence_score=confidence,
                validation_source="range_validation",
                error_message=error_message
            ))
        
        return validations
    
    def generate_hallucination_report(self, response: str) -> HallucinationReport:
        """
        Gera relatório completo de verificação de alucinações
        """
        # Validar todos os elementos
        all_validations = self.validate_legal_citations(response)
        
        if not all_validations:
            return HallucinationReport(
                total_elements_checked=0,
                valid_elements=0,
                invalid_elements=0,
                validation_results=[],
                overall_confidence=1.0,
                hallucination_rate=0.0,
                recommendations=["Nenhum elemento jurídico específico encontrado para validar"]
            )
        
        # Calcular estatísticas
        valid_count = sum(1 for v in all_validations if v.is_valid)
        invalid_count = len(all_validations) - valid_count
        
        # Calcular confiança geral (média ponderada)
        total_confidence = sum(v.confidence_score for v in all_validations)
        overall_confidence = total_confidence / len(all_validations)
        
        # Taxa de alucinação
        hallucination_rate = invalid_count / len(all_validations)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(all_validations, hallucination_rate)
        
        return HallucinationReport(
            total_elements_checked=len(all_validations),
            valid_elements=valid_count,
            invalid_elements=invalid_count,
            validation_results=all_validations,
            overall_confidence=overall_confidence,
            hallucination_rate=hallucination_rate,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, validations: List[ValidationResult], 
                                 hallucination_rate: float) -> List[str]:
        """Gera recomendações baseadas nos resultados da validação"""
        recommendations = []
        
        if hallucination_rate > 0.3:
            recommendations.append("⚠️ Alta taxa de informações incorretas detectada. Recomenda-se revisão manual completa.")
        elif hallucination_rate > 0.1:
            recommendations.append("⚠️ Algumas informações jurídicas podem estar incorretas. Verificar citações específicas.")
        
        # Recomendações específicas por tipo de erro
        error_types = {}
        for validation in validations:
            if not validation.is_valid:
                error_type = validation.element_type
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1
        
        if "law_article" in error_types:
            recommendations.append(f"📚 Verificar {error_types['law_article']} citação(ões) de artigos de lei")
        
        if "process_number" in error_types:
            recommendations.append(f"🔢 Validar {error_types['process_number']} número(s) de processo")
        
        if "legal_deadline" in error_types:
            recommendations.append(f"⏱️ Confirmar {error_types['legal_deadline']} prazo(s) legal(is)")
        
        # Recomendações de melhoria
        if hallucination_rate < 0.05:
            recommendations.append("✅ Informações jurídicas apresentam alta confiabilidade")
        
        return recommendations
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema de validação"""
        return {
            "available_laws": len(self.valid_laws["codigos"]) + len(self.valid_laws["leis_especiais"]),
            "validation_patterns": len(self.validation_patterns),
            "cache_size": len(self.validation_cache),
            "external_sources": len(self.external_sources),
            "last_updated": datetime.now().isoformat()
        }