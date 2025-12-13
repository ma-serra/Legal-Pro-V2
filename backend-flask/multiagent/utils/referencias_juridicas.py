"""
Utilitário para extração e validação de referências jurídicas em textos.
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Padrões de regex para diferentes tipos de referências jurídicas
REGEX_PATTERNS = {
    # Leis Federais: Lei nº 8.112/90, Lei 8112/90, Lei 8.112, de 1990
    "leis": r'(?:Lei(?:\s+Federal)?(?:\s+Complementar)?(?:\s+nº|\s+n°|\s+n\.|\s+n|\s+))?\s*(\d{1,6}(?:\.\d{3})*(?:\/\d{2,4})?|\d{1,6}(?:\.?\d{3})*[,\s]+de\s+\d{1,2}\s+de\s+[a-zA-ZçÇ]+\s+de\s+\d{4})',
    
    # Códigos: Código Civil, Código Penal, etc.
    "codigos": r'C[oó]digo\s+(?:Civil|Penal|Comercial|Tribut[aá]rio|de\s+Processo\s+Civil|de\s+Processo\s+Penal|de\s+Defesa\s+do\s+Consumidor|de\s+Tr[aâ]nsito|Eleitoral|Florestal)',
    
    # Constituição: arts. 5º, 7º da CF, artigo 5, inciso X, da Constituição
    "constituicao": r'(?:artigo|art\.?)\s+(\d+)(?:º|\s*)?(?:\s*,\s*(?:inciso|inc\.)\s+([IVX]+))?(?:\s*da\s+(?:Constitui[çc][ãa]o|CF))',
    
    # Súmulas: Súmula 377 do STF, Súmula Vinculante nº 13
    "sumulas": r'S[úu]mula(?:\s+Vinculante)?\s+(?:n[°º\.]?\s*)?(\d+)(?:\s+do\s+(STF|STJ|TST|TSE|STM))?',
    
    # Recursos/Processos: REsp 1.234.567/SP, RE 123456, AgRg no REsp 123456/RS
    "processos": r'(?:RE(?:sp)?|HC|MS|ADI|ADPF|ACO|AREsp|CC|RMS|RHC|AgRg|AgInt|EDcl|AR|Rcl)\s+(?:no\s+)?(?:n[°º\.]?\s*)?(\d{1,7}(?:\.?\d{3})*(?:\/[A-Z]{2})?)(?:-\d+)?',
    
    # Artigos de leis: Art. 5º, X, Art 186 do CC, art. 927, parágrafo único, do CC
    "artigos": r'(?:artigo|art\.?)\s+(\d+)(?:[\.°ºª])?(?:\s*,\s*(?:inciso|inc\.)\s+([IVX]+|[a-z]))?(?:\s*,\s*(?:par[áa]grafo|§)(?:\s+[úu]nico|\s+(\d+))?)?(?:\s+d[ao]\s+([A-Za-z\s]+))?',
    
    # Decretos e Medidas Provisórias: Decreto 12.345/2022, MP 123/2023
    "decretos": r'(?:Decreto(?:-Lei)?|Medida\s+Provis[óo]ria|MP)(?:\s+n[°ºo.]?)?\s*(\d{1,6}(?:\.\d{3})*(?:\/\d{2,4})?)',

    # Normas da SUSEP e ANPD: Circular SUSEP 123/2022, Resolução ANPD 5/2023
    "normas_reguladoras": r'(?:Circular|Resolução|Instrução|Portaria)\s+(?:SUSEP|ANPD|BACEN|CVM|ANS|ANVISA|ANP|ANATEL|ANEEL)(?:\s+n[°ºo.]?)?\s*(\d{1,4}(?:\/\d{2,4})?)'
}

def extract_legal_references(text: str) -> List[Dict[str, Any]]:
    """
    Extrai referências jurídicas de um texto.
    
    Args:
        text: Texto a ser analisado
        
    Returns:
        Lista de referências encontradas com tipo, texto e posição no texto
    """
    references = []
    
    # Processa cada tipo de referência
    for ref_type, pattern in REGEX_PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            references.append({
                "tipo": ref_type,
                "texto": match.group(0),
                "posicao": match.span(),
                "capturado": match.groups(),
                "validado": False  # Será atualizado na fase de validação
            })
    
    # Ordena por posição no texto
    references.sort(key=lambda x: x["posicao"][0])
    
    return references

def validate_references(references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Valida referências jurídicas encontradas, marcando-as como válidas.
    
    Args:
        references: Lista de referências a serem validadas
        
    Returns:
        Lista de referências com status de validação atualizado
    """
    # Esta função pode ser expandida para validação mais complexa contra banco de dados
    # Por enquanto, implementamos validações básicas de estrutura
    
    for ref in references:
        try:
            if ref["tipo"] == "leis":
                # Validação básica de formato
                ref["validado"] = bool(re.match(r'Lei\s+(?:\d{1,6}(?:\.\d{3})*(?:\/\d{2,4})?)', ref["texto"], re.IGNORECASE))
                
            elif ref["tipo"] == "artigos":
                # Validação de número do artigo (faixa razoável)
                if ref["capturado"] and ref["capturado"][0]:
                    art_num = int(ref["capturado"][0])
                    ref["validado"] = 1 <= art_num <= 2000  # Limite arbitrário razoável
                
            elif ref["tipo"] == "sumulas":
                # Súmulas geralmente têm numeração menor
                if ref["capturado"] and ref["capturado"][0]:
                    sumula_num = int(ref["capturado"][0])
                    ref["validado"] = 1 <= sumula_num <= 800  # Limite arbitrário para súmulas
                    
            else:
                # Para outros casos, consideramos estruturalmente válidos sem validação adicional
                ref["validado"] = True
                
        except (ValueError, IndexError) as e:
            logger.warning(f"Erro ao validar referência: {ref['texto']} - {str(e)}")
            ref["validado"] = False
            ref["erro_validacao"] = str(e)
    
    return references

def find_legal_standards(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Encontra e categoriza padrões de referências jurídicas em um texto.
    
    Args:
        text: Texto a ser analisado
        
    Returns:
        Dicionário com referências categorizadas e validadas
    """
    # Extrai referências
    references = extract_legal_references(text)
    
    # Valida referências
    references = validate_references(references)
    
    # Organiza por tipo
    categorized = {}
    for ref in references:
        ref_type = ref["tipo"]
        if ref_type not in categorized:
            categorized[ref_type] = []
        categorized[ref_type].append(ref)
    
    return categorized