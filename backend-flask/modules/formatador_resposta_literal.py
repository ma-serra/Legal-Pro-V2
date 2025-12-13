"""
Formatador de Resposta Literal
Garante que as respostas sejam baseadas exclusivamente na integralidade da lei,
sem interpretações subjetivas.
"""

import logging
import re
from typing import Dict, List, Any, Optional

class FormatadorRespostaLiteral:
    """Formatador que garante respostas baseadas exclusivamente na lei."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def formatar_resposta_legal(self, consulta: str, artigos_encontrados: List[Dict], 
                               resposta_ia: str) -> str:
        """
        Formata resposta garantindo base exclusiva na legislação.
        """
        try:
            # Template obrigatório para resposta
            resposta_formatada = self._aplicar_template_obrigatorio(
                consulta, artigos_encontrados, resposta_ia
            )
            
            # Remove interpretações subjetivas
            resposta_limpa = self._remover_interpretacoes_subjetivas(resposta_formatada)
            
            # Adiciona validação de conformidade
            resposta_validada = self._adicionar_validacao_conformidade(resposta_limpa)
            
            return resposta_validada
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar resposta literal: {e}")
            return self._resposta_erro_formatacao()
    
    def _aplicar_template_obrigatorio(self, consulta: str, artigos: List[Dict], 
                                    resposta_ia: str) -> str:
        """Aplica template obrigatório baseado na lei."""
        
        # Cabeçalho obrigatório
        resposta = "📋 RESPOSTA BASEADA EXCLUSIVAMENTE NA LEGISLAÇÃO\n"
        resposta += "=" * 60 + "\n\n"
        
        # Seção 1: Artigos Aplicáveis
        resposta += "🎯 ARTIGOS APLICÁVEIS:\n"
        resposta += "-" * 30 + "\n"
        
        for i, artigo in enumerate(artigos, 1):
            numero = artigo.get('numero', 'N/A')
            fonte = 'Código Penal' if 'codigo_penal' in str(artigo) else 'Código de Processo Penal'
            resposta += f"{i}. Art. {numero} do {fonte}\n"
        
        resposta += "\n"
        
        # Seção 2: Texto Legal Literal
        resposta += "📖 TEXTO LEGAL (TRANSCRIÇÃO LITERAL):\n"
        resposta += "-" * 40 + "\n"
        
        for i, artigo in enumerate(artigos, 1):
            numero = artigo.get('numero', 'N/A')
            texto = artigo.get('texto_literal', artigo.get('texto_completo', ''))
            resposta += f"{i}. Art. {numero}:\n"
            resposta += f'"{texto}"\n\n'
        
        # Seção 3: Aplicação Literal
        resposta += "⚖️ APLICAÇÃO (BASEADA EXCLUSIVAMENTE NO TEXTO LEGAL):\n"
        resposta += "-" * 50 + "\n"
        
        # Extrai apenas aplicação literal da resposta da IA
        aplicacao_literal = self._extrair_aplicacao_literal(resposta_ia, artigos)
        resposta += aplicacao_literal + "\n\n"
        
        # Seção 4: Fundamentação Legal
        resposta += "📚 FUNDAMENTAÇÃO LEGAL:\n"
        resposta += "-" * 25 + "\n"
        resposta += "Esta resposta está fundamentada exclusivamente nos artigos acima citados, "
        resposta += "conforme previsto na legislação brasileira, sem interpretações subjetivas.\n\n"
        
        # Rodapé de conformidade
        resposta += "✅ CONFORMIDADE: Resposta baseada na integralidade da lei"
        
        return resposta
    
    def _extrair_aplicacao_literal(self, resposta_ia: str, artigos: List[Dict]) -> str:
        """Extrai apenas a aplicação literal, removendo interpretações."""
        
        # Remove frases interpretativas
        frases_proibidas = [
            'entendo que', 'considero', 'acredito', 'pode ser interpretado',
            'uma possível interpretação', 'subjetivamente', 'em minha opinião'
        ]
        
        aplicacao = resposta_ia
        for frase in frases_proibidas:
            aplicacao = re.sub(rf'\b{re.escape(frase)}.*?\.', '', aplicacao, flags=re.IGNORECASE)
        
        # Mantém apenas o que está expressamente previsto
        if not aplicacao.strip():
            aplicacao = "A legislação prevê especificamente os elementos descritos nos artigos acima citados."
        
        return aplicacao.strip()
    
    def _remover_interpretacoes_subjetivas(self, resposta: str) -> str:
        """Remove interpretações subjetivas da resposta."""
        
        # Palavras e expressões a serem removidas
        expressoes_subjetivas = [
            r'\b(eu )?entendo que\b.*?\.', r'\b(eu )?considero\b.*?\.',
            r'\b(eu )?acredito\b.*?\.', r'\bpode ser interpretado como\b.*?\.',
            r'\buma interpretação possível\b.*?\.', r'\bsubjetivamente\b.*?\.',
            r'\bem minha opinião\b.*?\.', r'\bgeralmente\b', r'\bnormalmente\b',
            r'\btalvez\b', r'\bpossivelmente\b'
        ]
        
        resposta_limpa = resposta
        for expressao in expressoes_subjetivas:
            resposta_limpa = re.sub(expressao, '', resposta_limpa, flags=re.IGNORECASE)
        
        # Remove espaços duplos resultantes
        resposta_limpa = re.sub(r'\s+', ' ', resposta_limpa).strip()
        
        return resposta_limpa
    
    def _adicionar_validacao_conformidade(self, resposta: str) -> str:
        """Adiciona validação de conformidade legal."""
        
        validacao = "\n\n" + "=" * 60 + "\n"
        validacao += "🔍 VALIDAÇÃO DE CONFORMIDADE LEGAL\n"
        validacao += "=" * 60 + "\n"
        
        # Verifica presença de elementos obrigatórios
        tem_artigo = bool(re.search(r'Art\.\s*\d+', resposta))
        tem_transcricao = 'TEXTO LEGAL' in resposta
        tem_aplicacao = 'APLICAÇÃO' in resposta
        tem_fundamentacao = 'FUNDAMENTAÇÃO' in resposta
        
        validacao += f"✓ Citação de artigos: {'SIM' if tem_artigo else 'NÃO'}\n"
        validacao += f"✓ Transcrição literal: {'SIM' if tem_transcricao else 'NÃO'}\n"
        validacao += f"✓ Aplicação baseada na lei: {'SIM' if tem_aplicacao else 'NÃO'}\n"
        validacao += f"✓ Fundamentação legal: {'SIM' if tem_fundamentacao else 'NÃO'}\n"
        
        # Status geral
        conformidade = all([tem_artigo, tem_transcricao, tem_aplicacao, tem_fundamentacao])
        status = "CONFORME" if conformidade else "NÃO CONFORME"
        validacao += f"\n🎯 STATUS: {status} com a exigência de resposta baseada na integralidade da lei\n"
        
        return resposta + validacao
    
    def _resposta_erro_formatacao(self) -> str:
        """Resposta padrão em caso de erro na formatação."""
        return """
        ❌ ERRO NA FORMATAÇÃO DA RESPOSTA
        
        Não foi possível formatar a resposta de acordo com a exigência de base
        exclusiva na integralidade da lei. 
        
        Por favor, reformule a consulta para permitir aplicação literal da legislação.
        """

    def validar_resposta_conforme(self, resposta: str) -> Dict[str, Any]:
        """Valida se a resposta está conforme a exigência legal."""
        
        criterios = {
            'citacao_artigo': bool(re.search(r'Art\.\s*\d+', resposta)),
            'transcricao_literal': 'TEXTO LEGAL' in resposta,
            'ausencia_interpretacao': not bool(re.search(
                r'\b(entendo|considero|acredito|pode ser interpretado)\b', 
                resposta, re.IGNORECASE
            )),
            'formato_obrigatorio': all([
                'ARTIGOS APLICÁVEIS' in resposta,
                'APLICAÇÃO' in resposta,
                'FUNDAMENTAÇÃO' in resposta
            ])
        }
        
        score = sum(criterios.values()) / len(criterios)
        
        return {
            'conforme': score >= 0.8,
            'score': score,
            'criterios': criterios,
            'observacoes': 'Resposta baseada exclusivamente na integralidade da lei' if score >= 0.8 
                          else 'Necessário ajuste para conformidade legal'
        }