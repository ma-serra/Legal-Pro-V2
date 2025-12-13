"""
Módulo de Extração de Entidades Jurídicas
Sistema de identificação e extração de entidades específicas do direito brasileiro.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def extrair_entidades(texto: str, tipo_documento: str = "geral") -> Dict[str, Any]:
    """
    Extrai entidades jurídicas de um texto.
    
    Args:
        texto: Texto para análise
        tipo_documento: Tipo do documento (geral, sentenca, peticao, etc.)
        
    Returns:
        Dict com entidades extraídas
    """
    try:
        entidades = {
            "pessoas_fisicas": _extrair_pessoas_fisicas(texto),
            "pessoas_juridicas": _extrair_pessoas_juridicas(texto),
            "processos": _extrair_numeros_processo(texto),
            "legislacao": _extrair_referencias_legais(texto),
            "valores_monetarios": _extrair_valores_monetarios(texto),
            "datas": _extrair_datas(texto),
            "orgaos_publicos": _extrair_orgaos_publicos(texto),
            "contratos": _extrair_referencias_contratos(texto),
            "enderecos": _extrair_enderecos(texto)
        }
        
        logger.info(f"Entidades extraídas com sucesso de texto com {len(texto)} caracteres")
        return {
            "success": True,
            "entidades": entidades,
            "total_entidades": sum(len(v) for v in entidades.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na extração de entidades: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "entidades": {}
        }


def extrair_citacoes(texto: str) -> Dict[str, Any]:
    """
    Extrai citações jurisprudenciais e doutrinárias.
    
    Args:
        texto: Texto para análise
        
    Returns:
        Dict com citações extraídas
    """
    try:
        citacoes = {
            "jurisprudencia": _extrair_jurisprudencia(texto),
            "doutrina": _extrair_doutrina(texto),
            "precedentes": _extrair_precedentes(texto),
            "sumulas": _extrair_sumulas(texto)
        }
        
        return {
            "success": True,
            "citacoes": citacoes,
            "total_citacoes": sum(len(v) for v in citacoes.values())
        }
        
    except Exception as e:
        logger.error(f"Erro na extração de citações: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "citacoes": {}
        }


def _extrair_pessoas_fisicas(texto: str) -> List[str]:
    """Extrai nomes de pessoas físicas."""
    # Padrões para identificar nomes de pessoas
    padroes = [
        r'\b[A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)*\b',  # Nomes próprios
    ]
    
    nomes = set()
    for padrao in padroes:
        matches = re.findall(padrao, texto)
        nomes.update(matches)
    
    # Filtrar nomes muito comuns que podem não ser pessoas
    filtros = {'Estado', 'União', 'Município', 'Fazenda', 'Justiça', 'Tribunal'}
    return [nome for nome in nomes if nome not in filtros]


def _extrair_pessoas_juridicas(texto: str) -> List[str]:
    """Extrai nomes de pessoas jurídicas."""
    padroes = [
        r'\b[A-Z][a-zA-Z\s&]+ (?:S\.?A\.?|LTDA\.?|ME|EPP|EIRELI)\b',
        r'\b[A-Z][a-zA-Z\s]+ (?:Sociedade|Empresa|Companhia|Organizações?)\b',
    ]
    
    empresas = set()
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        empresas.update(matches)
    
    return list(empresas)


def _extrair_numeros_processo(texto: str) -> List[str]:
    """Extrai números de processos judiciais."""
    # Padrão CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
    padrao_cnj = r'\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b'
    return re.findall(padrao_cnj, texto)


def _extrair_referencias_legais(texto: str) -> List[Dict[str, str]]:
    """Extrai referências a leis, decretos, etc."""
    padroes = {
        'lei': r'\bLei n?º?\s*(\d+(?:\.\d+)*(?:/\d{4})?)\b',
        'decreto': r'\bDecreto n?º?\s*(\d+(?:\.\d+)*(?:/\d{4})?)\b',
        'medida_provisoria': r'\bMedida Provisória n?º?\s*(\d+(?:\.\d+)*(?:/\d{4})?)\b',
        'portaria': r'\bPortaria n?º?\s*(\d+(?:\.\d+)*(?:/\d{4})?)\b',
        'resolucao': r'\bResolução n?º?\s*(\d+(?:\.\d+)*(?:/\d{4})?)\b',
        'constituicao': r'\bConstituição Federal\b',
        'codigo': r'\bCódigo (?:Civil|Penal|de Processo Civil|de Processo Penal|Tributário|do Consumidor)\b'
    }
    
    referencias = []
    for tipo, padrao in padroes.items():
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            referencias.append({
                'tipo': tipo,
                'numero': match.group(1) if match.groups() else match.group(0),
                'texto_completo': match.group(0),
                'posicao': match.start()
            })
    
    return referencias


def _extrair_valores_monetarios(texto: str) -> List[Dict[str, Any]]:
    """Extrai valores monetários."""
    padroes = [
        r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?) reais?',
    ]
    
    valores = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            valor_str = match.group(1)
            try:
                # Converter para float
                valor_num = float(valor_str.replace('.', '').replace(',', '.'))
                valores.append({
                    'valor_texto': match.group(0),
                    'valor_numerico': valor_num,
                    'posicao': match.start()
                })
            except ValueError:
                continue
    
    return valores


def _extrair_datas(texto: str) -> List[Dict[str, str]]:
    """Extrai datas do texto."""
    padroes = [
        r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',
        r'\b(\d{1,2}) de (\w+) de (\d{4})\b',
        r'\b(\w+) de (\d{4})\b',
    ]
    
    datas = []
    for i, padrao in enumerate(padroes):
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            datas.append({
                'data_texto': match.group(0),
                'formato': ['dd/mm/aaaa', 'dd de mês de aaaa', 'mês de aaaa'][i],
                'posicao': match.start()
            })
    
    return datas


def _extrair_orgaos_publicos(texto: str) -> List[str]:
    """Extrai nomes de órgãos públicos."""
    padroes = [
        r'\b(?:Tribunal|TJ|STJ|STF|TST|TRF|TRT)\b[A-Z\s]*',
        r'\bMinistério Público\b[A-Z\s]*',
        r'\bDefensoria Pública\b[A-Z\s]*',
        r'\bAdvocacia[- ]Geral\b[A-Z\s]*',
        r'\bProcuradoria\b[A-Z\s]*',
        r'\bSecretaria\b[A-Z\s]*',
        r'\bDepartamento\b[A-Z\s]*',
    ]
    
    orgaos = set()
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        orgaos.update(matches)
    
    return list(orgaos)


def _extrair_referencias_contratos(texto: str) -> List[Dict[str, str]]:
    """Extrai referências a contratos."""
    padroes = [
        r'\bContrato n?º?\s*(\d+(?:/\d{4})?)',
        r'\bInstrumento Particular\b[^.]*',
        r'\bEscritura Pública\b[^.]*',
    ]
    
    contratos = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            contratos.append({
                'tipo': 'contrato',
                'referencia': match.group(0),
                'posicao': match.start()
            })
    
    return contratos


def _extrair_enderecos(texto: str) -> List[str]:
    """Extrai endereços."""
    padroes = [
        r'\b(?:Rua|Av\.|Avenida|Praça|Alameda)\s+[A-Za-z\s,]+,?\s*\d+',
        r'\bCEP:?\s*\d{5}-?\d{3}\b',
    ]
    
    enderecos = set()
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        enderecos.update(matches)
    
    return list(enderecos)


def _extrair_jurisprudencia(texto: str) -> List[Dict[str, str]]:
    """Extrai citações jurisprudenciais."""
    padroes = [
        r'\b(?:STF|STJ|TST|TRF|TRT|TJ)[^.]*Rel\.[^.]*',
        r'\bAgravo\s+(?:de\s+)?Instrumento\s+n?º?\s*\d+',
        r'\bRecurso\s+Especial\s+n?º?\s*\d+',
        r'\bRecurso\s+Extraordinário\s+n?º?\s*\d+',
    ]
    
    citacoes = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            citacoes.append({
                'tipo': 'jurisprudencia',
                'citacao': match.group(0),
                'posicao': match.start()
            })
    
    return citacoes


def _extrair_doutrina(texto: str) -> List[Dict[str, str]]:
    """Extrai citações doutrinárias."""
    padroes = [
        r'\b[A-Z][a-z]+,\s+[A-Z][a-z]+\.[^.]*\.\s*\d{4}',
        r'\bApud\s+[A-Z][a-z]+[^.]*',
    ]
    
    citacoes = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto)
        for match in matches:
            citacoes.append({
                'tipo': 'doutrina',
                'citacao': match.group(0),
                'posicao': match.start()
            })
    
    return citacoes


def _extrair_precedentes(texto: str) -> List[Dict[str, str]]:
    """Extrai referências a precedentes."""
    padroes = [
        r'\bPrecedente\s+[^.]*',
        r'\bTese\s+fixada\s+[^.]*',
        r'\bIncidente\s+de\s+Resolução\s+de\s+Demandas\s+Repetitivas\s+[^.]*',
    ]
    
    precedentes = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            precedentes.append({
                'tipo': 'precedente',
                'referencia': match.group(0),
                'posicao': match.start()
            })
    
    return precedentes


def _extrair_sumulas(texto: str) -> List[Dict[str, str]]:
    """Extrai referências a súmulas."""
    padroes = [
        r'\bSúmula\s+(?:Vinculante\s+)?n?º?\s*\d+\s+do\s+(?:STF|STJ)',
        r'\bEnunciado\s+n?º?\s*\d+',
    ]
    
    sumulas = []
    for padrao in padroes:
        matches = re.finditer(padrao, texto, re.IGNORECASE)
        for match in matches:
            sumulas.append({
                'tipo': 'sumula',
                'referencia': match.group(0),
                'posicao': match.start()
            })
    
    return sumulas