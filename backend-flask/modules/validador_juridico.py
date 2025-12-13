"""
Módulo de Validação Jurídica para Respostas do Assistente Penal
Garante que todas as respostas tenham embasamento jurídico correto
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from .consulta_direta_codigos import ConsultaDiretaCodigos

logger = logging.getLogger(__name__)

class ValidadorJuridico:
    """Validador de respostas jurídicas baseado nos códigos penais"""
    
    def __init__(self):
        self.consultor_codigos = ConsultaDiretaCodigos()
        
        # Padrões obrigatórios para respostas válidas
        self.padroes_obrigatorios = {
            'citacao_artigo': r'[Aa]rt\.?\s*\d+',
            'mencao_codigo': r'[Cc]ódigo\s+(?:Penal|de\s+Processo\s+Penal)',
            'fundamentacao': r'(?:fundamenta|baseia|prevê|estabelece|dispõe)',
            'estrutura_resposta': [
                r'ANÁLISE\s+LEGAL',
                r'FUNDAMENTAÇÃO',
                r'PROCEDIMENTO',
                r'ORIENTAÇÃO\s+PRÁTICA'
            ]
        }
        
        # Critérios de qualidade jurídica
        self.criterios_qualidade = {
            'minimo_artigos': 1,
            'citacao_precisa': True,
            'contexto_adequado': True,
            'linguagem_tecnica': True
        }
    
    def validar_resposta_completa(self, resposta: str, consulta_original: str) -> Dict[str, Any]:
        """Valida completamente uma resposta jurídica"""
        validacao = {
            'aprovada': False,
            'score_juridico': 0.0,
            'problemas_encontrados': [],
            'sugestoes_melhoria': [],
            'artigos_validados': [],
            'estrutura_adequada': False,
            'fundamentacao_suficiente': False
        }
        
        try:
            # 1. Validação estrutural
            estrutura_ok = self._validar_estrutura_resposta(resposta)
            validacao['estrutura_adequada'] = estrutura_ok
            
            # 2. Validação de citações jurídicas
            citacoes_validas = self._validar_citacoes_juridicas(resposta)
            validacao['artigos_validados'] = citacoes_validas
            
            # 3. Validação de fundamentação
            fundamentacao_ok = self._validar_fundamentacao(resposta, consulta_original)
            validacao['fundamentacao_suficiente'] = fundamentacao_ok
            
            # 4. Cálculo do score jurídico
            score = self._calcular_score_juridico(resposta, citacoes_validas, estrutura_ok, fundamentacao_ok)
            validacao['score_juridico'] = score
            
            # 5. Decisão final de aprovação
            validacao['aprovada'] = (
                score >= 0.7 and 
                len(citacoes_validas) >= 1 and 
                estrutura_ok and 
                fundamentacao_ok
            )
            
            # 6. Geração de problemas e sugestões
            if not validacao['aprovada']:
                validacao['problemas_encontrados'] = self._identificar_problemas(
                    resposta, citacoes_validas, estrutura_ok, fundamentacao_ok
                )
                validacao['sugestoes_melhoria'] = self._gerar_sugestoes_melhoria(validacao['problemas_encontrados'])
            
        except Exception as e:
            logger.error(f"Erro na validação jurídica: {e}")
            validacao['problemas_encontrados'].append(f"Erro interno de validação: {e}")
        
        return validacao
    
    def _validar_estrutura_resposta(self, resposta: str) -> bool:
        """Valida se a resposta segue a estrutura obrigatória"""
        secoes_encontradas = 0
        
        for padrao_secao in self.padroes_obrigatorios['estrutura_resposta']:
            if re.search(padrao_secao, resposta, re.IGNORECASE):
                secoes_encontradas += 1
        
        # Exige pelo menos 3 das 4 seções obrigatórias
        return secoes_encontradas >= 3
    
    def _validar_citacoes_juridicas(self, resposta: str) -> List[Dict[str, Any]]:
        """Valida todas as citações jurídicas presentes na resposta"""
        citacoes_validas = []
        
        # Encontra todas as citações de artigos
        matches_artigos = re.finditer(r'[Aa]rt\.?\s*(\d+)(?:\s*(?:,\s*§\s*(\d+)[°º]?)?(?:\s*,\s*(?:inciso\s*)?([IVX]+))?)?', resposta)
        
        for match in matches_artigos:
            numero_artigo = match.group(1)
            paragrafo = match.group(2) if match.group(2) else None
            inciso = match.group(3) if match.group(3) else None
            
            # Valida o artigo nos códigos
            artigos_encontrados = self.consultor_codigos.buscar_artigo_especifico(numero_artigo)
            
            if artigos_encontrados:
                for artigo in artigos_encontrados:
                    validacao_artigo = {
                        'artigo': numero_artigo,
                        'fonte': artigo['fonte'],
                        'titulo': artigo['titulo'],
                        'validado': True,
                        'paragrafo_especificado': paragrafo,
                        'inciso_especificado': inciso,
                        'conteudo_referencia': artigo['conteudo_completo'][:500]
                    }
                    
                    # Validação adicional de parágrafos e incisos
                    if paragrafo:
                        validacao_artigo['paragrafo_valido'] = self.consultor_codigos._validar_paragrafo(
                            artigo['conteudo_completo'], paragrafo
                        )
                    
                    if inciso:
                        validacao_artigo['inciso_valido'] = self.consultor_codigos._validar_inciso(
                            artigo['conteudo_completo'], inciso
                        )
                    
                    citacoes_validas.append(validacao_artigo)
        
        return citacoes_validas
    
    def _validar_fundamentacao(self, resposta: str, consulta_original: str) -> bool:
        """Valida se a resposta tem fundamentação jurídica adequada"""
        # Verifica presença de palavras-chave de fundamentação
        fundamentacao_presente = bool(re.search(self.padroes_obrigatorios['fundamentacao'], resposta, re.IGNORECASE))
        
        # Verifica menção aos códigos
        codigo_mencionado = bool(re.search(self.padroes_obrigatorios['mencao_codigo'], resposta, re.IGNORECASE))
        
        # Verifica se responde adequadamente à consulta
        resposta_adequada = self._verificar_adequacao_resposta(resposta, consulta_original)
        
        return fundamentacao_presente and codigo_mencionado and resposta_adequada
    
    def _verificar_adequacao_resposta(self, resposta: str, consulta: str) -> bool:
        """Verifica se a resposta aborda adequadamente a consulta"""
        # Extrai termos principais da consulta
        termos_consulta = self.consultor_codigos._extrair_termos_juridicos(consulta)
        
        if not termos_consulta:
            return True  # Se não há termos específicos, considera adequada
        
        # Verifica se pelo menos metade dos termos são abordados na resposta
        termos_abordados = 0
        resposta_lower = resposta.lower()
        
        for termo in termos_consulta:
            if termo.lower() in resposta_lower:
                termos_abordados += 1
        
        return termos_abordados >= len(termos_consulta) * 0.5
    
    def _calcular_score_juridico(self, resposta: str, citacoes_validas: List[Dict], 
                                estrutura_ok: bool, fundamentacao_ok: bool) -> float:
        """Calcula score de qualidade jurídica da resposta"""
        score = 0.0
        
        # Pontuação por estrutura (25%)
        if estrutura_ok:
            score += 0.25
        
        # Pontuação por fundamentação (25%)
        if fundamentacao_ok:
            score += 0.25
        
        # Pontuação por citações válidas (40%)
        if citacoes_validas:
            score_citacoes = min(len(citacoes_validas) * 0.1, 0.4)
            score += score_citacoes
        
        # Pontuação por qualidade do texto (10%)
        score_qualidade = self._avaliar_qualidade_texto(resposta)
        score += score_qualidade * 0.1
        
        return min(score, 1.0)
    
    def _avaliar_qualidade_texto(self, resposta: str) -> float:
        """Avalia qualidade geral do texto jurídico"""
        score = 0.0
        
        # Verifica comprimento adequado
        if 200 <= len(resposta) <= 3000:
            score += 0.3
        
        # Verifica uso de terminologia jurídica
        termos_juridicos = ['dispõe', 'prevê', 'estabelece', 'configura', 'tipifica', 'penaliza']
        termos_encontrados = sum(1 for termo in termos_juridicos if termo in resposta.lower())
        score += min(termos_encontrados * 0.1, 0.4)
        
        # Verifica organização (presença de listas, parágrafos)
        if re.search(r'[1-9]\.\s*\*\*', resposta) or re.search(r'\*\*[^*]+\*\*', resposta):
            score += 0.3
        
        return min(score, 1.0)
    
    def _identificar_problemas(self, resposta: str, citacoes_validas: List[Dict], 
                              estrutura_ok: bool, fundamentacao_ok: bool) -> List[str]:
        """Identifica problemas específicos na resposta"""
        problemas = []
        
        if not estrutura_ok:
            problemas.append("Resposta não segue a estrutura obrigatória (ANÁLISE LEGAL, FUNDAMENTAÇÃO, PROCEDIMENTO, ORIENTAÇÃO PRÁTICA)")
        
        if not fundamentacao_ok:
            problemas.append("Fundamentação jurídica insuficiente ou ausente")
        
        if not citacoes_validas:
            problemas.append("Nenhum artigo jurídico válido citado")
        
        if len(resposta) < 200:
            problemas.append("Resposta muito superficial (menos de 200 caracteres)")
        
        if not re.search(self.padroes_obrigatorios['mencao_codigo'], resposta, re.IGNORECASE):
            problemas.append("Não menciona explicitamente o Código Penal ou Código de Processo Penal")
        
        return problemas
    
    def _gerar_sugestoes_melhoria(self, problemas: List[str]) -> List[str]:
        """Gera sugestões específicas de melhoria"""
        sugestoes = []
        
        for problema in problemas:
            if "estrutura obrigatória" in problema:
                sugestoes.append("Organize a resposta com as seções: 🔍 ANÁLISE LEGAL, ⚖️ FUNDAMENTAÇÃO, 📋 PROCEDIMENTO, 🎯 ORIENTAÇÃO PRÁTICA")
            
            elif "fundamentação" in problema:
                sugestoes.append("Inclua fundamentação baseada nos artigos do CP ou CPP, explicando o dispositivo legal")
            
            elif "artigo jurídico" in problema:
                sugestoes.append("Cite artigos específicos do Código Penal ou Código de Processo Penal relevantes")
            
            elif "superficial" in problema:
                sugestoes.append("Desenvolva melhor a resposta com análise mais detalhada dos aspectos jurídicos")
            
            elif "não menciona" in problema:
                sugestoes.append("Referencie explicitamente o 'Código Penal' ou 'Código de Processo Penal' como fonte")
        
        return sugestoes
    
    def corrigir_resposta_automaticamente(self, resposta: str, consulta_original: str) -> str:
        """Aplica correções automáticas básicas na resposta"""
        resposta_corrigida = resposta
        
        # Adiciona estrutura básica se ausente
        if not re.search(r'ANÁLISE\s+LEGAL', resposta_corrigida, re.IGNORECASE):
            # Busca fundamentação para a consulta
            fundamentacao = self.consultor_codigos.gerar_fundamentacao_completa(consulta_original)
            
            prefixo_estrutural = self._gerar_prefixo_estrutural(fundamentacao)
            resposta_corrigida = prefixo_estrutural + "\n\n" + resposta_corrigida
        
        # Adiciona citações se necessário
        if not re.search(self.padroes_obrigatorios['citacao_artigo'], resposta_corrigida):
            citacoes_sugeridas = self._sugerir_citacoes(consulta_original)
            if citacoes_sugeridas:
                resposta_corrigida += "\n\n" + citacoes_sugeridas
        
        return resposta_corrigida
    
    def _gerar_prefixo_estrutural(self, fundamentacao: Dict[str, Any]) -> str:
        """Gera prefixo com estrutura baseada na fundamentação encontrada"""
        prefixo = "**🔍 ANÁLISE LEGAL:**\n"
        
        if fundamentacao['artigos_diretos']:
            for artigo in fundamentacao['artigos_diretos'][:2]:
                prefixo += f"- {artigo['fonte']}, Art. {artigo['artigo']}: {artigo['titulo']}\n"
        
        return prefixo
    
    def _sugerir_citacoes(self, consulta: str) -> str:
        """Sugere citações relevantes baseadas na consulta"""
        termos = self.consultor_codigos._extrair_termos_juridicos(consulta)
        citacoes = []
        
        for termo in termos[:2]:  # Limita a 2 termos
            resultados = self.consultor_codigos.buscar_por_termo(termo, limite=1)
            if resultados:
                artigo = resultados[0]
                citacoes.append(f"**Referência Legal:** {artigo['fonte']}, Art. {artigo['artigo']} - {artigo['titulo']}")
        
        return "\n".join(citacoes) if citacoes else ""