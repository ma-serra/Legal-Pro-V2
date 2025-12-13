"""
Agentes revisores (segunda opinião) para áreas jurídicas especializadas.
Estes agentes são responsáveis por fornecer uma revisão independente
das análises feitas pelos agentes especialistas primários.
"""

import os
import logging
import json
from datetime import datetime

import anthropic
from anthropic import Anthropic

from multiagent.core.base_agent import BaseAgent
from multiagent.agents.base_juridico import BaseJuridicoAgent
from multiagent.utils.api_key_manager import APIKeyManager

logger = logging.getLogger('multiagent.agents.revisores')

class BaseRevisorJuridicoAgent(BaseJuridicoAgent):
    """
    Classe base para todos os agentes revisores jurídicos.
    Fornece a estrutura padrão para revisão de análises jurídicas.
    """
    
    def __init__(self, config):
        """Inicializa o agente revisor com configurações específicas."""
        super().__init__(config)
        self.api_key_manager = APIKeyManager()
        self.anthropic_key = self.api_key_manager.get_api_key('anthropic')
        self.client = None
        self._inicializar_cliente_ai()
        
    def _inicializar_cliente_ai(self):
        """Inicializa o cliente da API Anthropic."""
        if self.anthropic_key:
            self.client = Anthropic(api_key=self.anthropic_key)
        else:
            logger.warning("Chave da API Anthropic não disponível para o revisor")
    
    def revisar_analise(self, analise_original, contexto=None):
        """
        Revisa a análise original e fornece uma segunda opinião.
        
        Args:
            analise_original: Texto da análise original
            contexto: Informações adicionais sobre o contexto (opcional)
            
        Returns:
            dict: Resultado da revisão com os campos:
                - revisao: Texto da revisão
                - nivel_concordancia: Nível de concordância (1-5)
                - pontos_divergentes: Lista de pontos divergentes
                - pontos_complementares: Lista de pontos complementares
        """
        if not self.client:
            return {
                "erro": "Cliente Anthropic não inicializado",
                "revisao": "Não foi possível realizar a revisão. Verifique a chave da API."
            }
        
        # Prompts especializados para revisão jurídica
        sistema_prompt = self._obter_sistema_prompt()
        
        # Preparar o contexto
        contexto_str = ""
        if contexto:
            if isinstance(contexto, dict):
                contexto_str = json.dumps(contexto, ensure_ascii=False)
            else:
                contexto_str = str(contexto)
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # O modelo mais recente
                max_tokens=4000,
                system=sistema_prompt,
                messages=[
                    {
                        "role": "user", 
                        "content": f"""
# Análise Original
{analise_original}

# Contexto Adicional
{contexto_str if contexto_str else "Nenhum contexto adicional fornecido."}

Por favor, realize uma revisão completa desta análise jurídica baseada nas suas instruções.
"""
                    }
                ]
            )
            
            revisao_texto = response.content[0].text
            
            # Analisar resultado para extrair metadados estruturados
            nivel_concordancia, pontos_divergentes, pontos_complementares = self._estruturar_revisao(revisao_texto)
            
            return {
                "revisao": revisao_texto,
                "nivel_concordancia": nivel_concordancia,
                "pontos_divergentes": pontos_divergentes,
                "pontos_complementares": pontos_complementares,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao realizar revisão: {str(e)}")
            return {
                "erro": str(e),
                "revisao": "Ocorreu um erro ao processar a revisão."
            }
    
    def _obter_sistema_prompt(self):
        """
        Retorna o prompt de sistema para o revisor jurídico.
        Deve ser sobrescrito por classes específicas.
        """
        return """
Você é um revisor jurídico especializado que fornece segundas opiniões sobre análises jurídicas.
Sua tarefa é revisar criticamente a análise fornecida, identificando:

1. Pontos de concordância e discordância
2. Elementos ausentes ou incompletamente abordados
3. Perspectivas alternativas ou complementares
4. Possíveis erros ou imprecisões jurídicas

Ao final da sua revisão, você deve:

- Atribuir um nível de concordância geral de 1 a 5 (onde 1 = discordância significativa e 5 = concordância total)
- Listar explicitamente os pontos divergentes entre sua análise e a original
- Listar pontos complementares que deveriam ser considerados

Formate sua revisão de forma clara e estruturada, incluindo as seções:
- REVISÃO GERAL
- NÍVEL DE CONCORDÂNCIA: [1-5]
- PONTOS DIVERGENTES:
- PONTOS COMPLEMENTARES:
"""
    
    def _estruturar_revisao(self, revisao_texto):
        """
        Extrai os metadados estruturados da revisão em texto.
        
        Args:
            revisao_texto: Texto completo da revisão
            
        Returns:
            tuple: (nivel_concordancia, pontos_divergentes, pontos_complementares)
        """
        nivel_concordancia = 3  # Valor padrão médio
        pontos_divergentes = []
        pontos_complementares = []
        
        # Extrair nível de concordância
        import re
        concordancia_match = re.search(r'NÍVEL DE CONCORDÂNCIA:\s*(\d)', revisao_texto)
        if concordancia_match:
            nivel_str = concordancia_match.group(1)
            if nivel_str.isdigit() and 1 <= int(nivel_str) <= 5:
                nivel_concordancia = int(nivel_str)
        
        # Extrair pontos divergentes
        divergentes_section = re.search(r'PONTOS DIVERGENTES:(.*?)(?:PONTOS COMPLEMENTARES:|$)', 
                                       revisao_texto, re.DOTALL)
        if divergentes_section:
            divergentes_text = divergentes_section.group(1).strip()
            # Extrair itens em lista
            pontos_divergentes = [
                item.strip().strip('*-•') for item in divergentes_text.split('\n') 
                if item.strip() and not item.strip().startswith('#')
            ]
        
        # Extrair pontos complementares
        complementares_section = re.search(r'PONTOS COMPLEMENTARES:(.*?)(?:$)', 
                                          revisao_texto, re.DOTALL)
        if complementares_section:
            complementares_text = complementares_section.group(1).strip()
            # Extrair itens em lista
            pontos_complementares = [
                item.strip().strip('*-•') for item in complementares_text.split('\n') 
                if item.strip() and not item.strip().startswith('#')
            ]
        
        return nivel_concordancia, pontos_divergentes, pontos_complementares
    
    def _processar(self, data):
        """
        Método para processar os dados. Funciona como revisor ou agente especializado.
        """
        # Se há análise original, funciona como revisor
        if 'analise_original' in data:
            return self.revisar_analise(
                analise_original=data['analise_original'],
                contexto=data.get('contexto')
            )
        
        # Se não há análise original, funciona como agente especializado
        texto = data.get('texto', '')
        if not texto:
            return {"erro": "Texto para análise não fornecido"}
        
        try:
            if not self.client:
                return {
                    "erro": "Cliente Anthropic não inicializado",
                    "analise": "Não foi possível realizar a análise. Verifique a chave da API."
                }
            
            # Usar o prompt do sistema específico da área
            sistema_prompt = self._obter_sistema_prompt()
            
            # Adaptar prompt para análise direta (não revisão)
            sistema_prompt_adaptado = sistema_prompt.replace(
                "revisar a análise jurídica fornecida", 
                "analisar o documento jurídico fornecido"
            ).replace(
                "análise original", 
                "documento"
            )
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=sistema_prompt_adaptado,
                messages=[
                    {
                        "role": "user", 
                        "content": f"Por favor, analise o seguinte documento jurídico:\n\n{texto}"
                    }
                ]
            )
            
            return {
                "analise": response.content[0].text,
                "timestamp": datetime.now().isoformat(),
                "modo": "analise_especializada"
            }
            
        except Exception as e:
            logger.error(f"Erro ao realizar análise: {str(e)}")
            return {
                "erro": str(e),
                "analise": "Ocorreu um erro ao processar a análise."
            }


class RevisorDireitoBancarioAgent(BaseRevisorJuridicoAgent):
    """
    Revisor especializado em Direito Bancário.
    Fornece segunda opinião sobre análises relacionadas a contratos bancários,
    operações financeiras e direitos do consumidor bancário.
    """
    
    def _obter_sistema_prompt(self):
        return """
Você é um revisor especializado em Direito Bancário, encarregado de analisar pareceres jurídicos 
sobre contratos bancários, operações financeiras, produtos bancários, e direitos do consumidor bancário.

Ao revisar a análise jurídica fornecida, você deve:

1. Verificar se a análise original abordou adequadamente os aspectos regulatórios bancários relevantes
2. Avaliar se a interpretação das cláusulas contratuais está em conformidade com a jurisprudência atual
3. Identificar possíveis vulnerabilidades ou pontos de atenção em operações bancárias analisadas
4. Verificar a aplicação correta das normas do Sistema Financeiro Nacional
5. Avaliar a análise de riscos para o consumidor ou instituição financeira

Estruture sua revisão nos seguintes blocos:
- REVISÃO GERAL: Uma análise abrangente da qualidade e completude do parecer original
- NÍVEL DE CONCORDÂNCIA: [1-5] Indique seu nível de concordância geral
- PONTOS DIVERGENTES: Liste especificamente onde você discorda da análise original e por quê
- PONTOS COMPLEMENTARES: Aspectos importantes que não foram considerados ou que merecem maior destaque

Sua revisão deve ser tecnicamente precisa, referenciando quando apropriado as normas do Banco Central, 
resoluções do CMN, e jurisprudência relevante do STJ sobre contratos bancários.
"""

    def _processar(self, data):
        """Implementação específica para direito bancário."""
        resultado = super()._processar(data)
        
        # Adicionar metadados específicos para direito bancário
        if 'erro' not in resultado:
            resultado['area_juridica'] = "Direito Bancário"
            resultado['especialidade'] = "Revisor Bancário"
        
        return resultado


class RevisorDireitoTrabalhistaAgent(BaseRevisorJuridicoAgent):
    """
    Revisor especializado em Direito Trabalhista.
    Fornece segunda opinião sobre análises relacionadas a relações de trabalho,
    contratos trabalhistas e questões envolvendo empregados e empregadores.
    """
    
    def _obter_sistema_prompt(self):
        return """
Você é um revisor especializado em Direito Trabalhista, encarregado de analisar pareceres jurídicos 
sobre relações de trabalho, contratos trabalhistas, direitos dos trabalhadores, e obrigações dos empregadores.

Ao revisar a análise jurídica fornecida, você deve:

1. Verificar se a análise original considerou corretamente as normas da CLT e legislação trabalhista aplicável
2. Avaliar se a interpretação das cláusulas contratuais trabalhistas está alinhada com a jurisprudência atual dos tribunais trabalhistas
3. Identificar possíveis vulnerabilidades ou riscos em acordos ou condutas trabalhistas analisadas
4. Verificar se questões como jornada, remuneração, rescisão e direitos adicionais foram adequadamente avaliadas
5. Analisar se as súmulas e orientações jurisprudenciais do TST foram corretamente aplicadas

Estruture sua revisão nos seguintes blocos:
- REVISÃO GERAL: Uma análise abrangente da qualidade e completude do parecer original
- NÍVEL DE CONCORDÂNCIA: [1-5] Indique seu nível de concordância geral
- PONTOS DIVERGENTES: Liste especificamente onde você discorda da análise original e por quê
- PONTOS COMPLEMENTARES: Aspectos importantes que não foram considerados ou que merecem maior destaque

Sua revisão deve ser tecnicamente precisa, referenciando quando apropriado a CLT, 
súmulas do TST, e jurisprudência relevante das cortes trabalhistas.
"""

    def _processar(self, data):
        """Implementação específica para direito trabalhista."""
        resultado = super()._processar(data)
        
        # Adicionar metadados específicos para direito trabalhista
        if 'erro' not in resultado:
            resultado['area_juridica'] = "Direito Trabalhista"
            resultado['especialidade'] = "Revisor Trabalhista"
        
        return resultado


class RevisorDireitoEmpresarialAgent(BaseRevisorJuridicoAgent):
    """
    Revisor especializado em Direito Empresarial.
    Fornece segunda opinião sobre análises relacionadas a contratos empresariais,
    operações societárias, propriedade intelectual e questões regulatórias.
    """
    
    def _obter_sistema_prompt(self):
        return """
Você é um revisor especializado em Direito Empresarial, encarregado de analisar pareceres jurídicos 
sobre contratos empresariais, operações societárias, estruturação corporativa, governança, 
propriedade intelectual e compliance regulatório.

Ao revisar a análise jurídica fornecida, você deve:

1. Verificar se a análise original abordou adequadamente os aspectos societários e contratuais relevantes
2. Avaliar se a interpretação das cláusulas e estruturas corporativas está em conformidade com a legislação vigente
3. Identificar possíveis riscos ou vulnerabilidades em operações empresariais analisadas
4. Verificar a aplicação correta das normas do Código Civil, Lei das S.A., Lei de Propriedade Industrial, e regulações setoriais
5. Avaliar potenciais impactos tributários, concorrenciais e regulatórios das operações analisadas

Estruture sua revisão nos seguintes blocos:
- REVISÃO GERAL: Uma análise abrangente da qualidade e completude do parecer original
- NÍVEL DE CONCORDÂNCIA: [1-5] Indique seu nível de concordância geral
- PONTOS DIVERGENTES: Liste especificamente onde você discorda da análise original e por quê
- PONTOS COMPLEMENTARES: Aspectos importantes que não foram considerados ou que merecem maior destaque

Sua revisão deve ser tecnicamente precisa, referenciando quando apropriado as leis empresariais, 
jurisprudência relevante dos tribunais comerciais, e precedentes da CVM ou CADE quando aplicáveis.
"""

    def _processar(self, data):
        """Implementação específica para direito empresarial."""
        resultado = super()._processar(data)
        
        # Adicionar metadados específicos para direito empresarial
        if 'erro' not in resultado:
            resultado['area_juridica'] = "Direito Empresarial"
            resultado['especialidade'] = "Revisor Empresarial"
        
        return resultado