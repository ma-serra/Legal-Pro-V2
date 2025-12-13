"""
Agente especializado em Sinistros e Liquidação Securitária.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.gestor_sinistros_securitario')

class GestorSinistrosSecuritarioAgent(BaseJuridicoAgent):
    """
    Agente especializado em Sinistros e Liquidação Securitária.
    
    Este agente analisa a legitimidade de sinistros, avalia coberturas, calcula indenizações
    e gerencia processos de liquidação no mercado securitário.
    """
    
    def _processar(self, data):
        """
        Processa análises de Sinistros e Liquidação Securitária.
        
        Args:
            data: Dicionário com o texto a ser analisado e configurações
            
        Returns:
            Dicionário com os resultados da análise de sinistros
        """
        texto = data.get('texto', '')
        contexto = data.get('contexto', '')
        tipo_analise = data.get('tipo_analise', 'geral')
        
        if not texto:
            return {"erro": "Nenhum texto fornecido para análise"}
        
        # Parâmetros de configuração
        provider = self.config.get('llm_provider', 'openai')
        
        # Usa o LLM apropriado conforme a configuração
        try:
            if provider == 'openai':
                resultado = self._analisar_openai(texto, contexto, tipo_analise)
            elif provider == 'anthropic':
                resultado = self._analisar_anthropic(texto, contexto, tipo_analise)
            else:
                resultado = self._analisar_fallback(texto, contexto, tipo_analise)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao analisar sinistros securitários: {str(e)}")
            return {
                "erro": f"Falha na análise: {str(e)}",
                "success": False
            }
    
    def _analisar_openai(self, texto, contexto, tipo_analise):
        """Analisa o texto utilizando OpenAI"""
        try:
            import openai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {"erro": "API key da OpenAI não configurada", "success": False}
                
            # Configura cliente OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Monta o prompt para análise
            system_prompt = self._get_system_prompt(tipo_analise)
            
            # Define o conteúdo a ser analisado
            user_content = f"DOCUMENTO PARA ANÁLISE DE SINISTROS SECURITÁRIOS:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,  # Baixa temperatura para análise técnica precisa
                max_tokens=3500,
                response_format={"type": "json_object"}
            )
            
            # Extrai o resultado
            resultado_json = json.loads(response.choices[0].message.content)
            
            # Garante a estrutura esperada do resultado
            if not isinstance(resultado_json, dict):
                return {"erro": "Formato de resposta inválido", "success": False}
                
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "openai",
                "modelo": "gpt-4o",
                "area_juridica": "Sinistros Securitários",
                "timestamp": time.time()
            })
            
            return resultado_json
            
        except ImportError:
            logger.warning("Módulo OpenAI não instalado. Usando fallback.")
            return self._analisar_fallback(texto, contexto, tipo_analise)
        except Exception as e:
            logger.error(f"Erro no processamento com OpenAI: {str(e)}")
            raise
    
    def _analisar_anthropic(self, texto, contexto, tipo_analise):
        """Analisa o texto utilizando Anthropic"""
        try:
            import anthropic
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return {"erro": "API key da Anthropic não configurada", "success": False}
                
            # Configura cliente Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Monta o prompt para análise
            system_prompt = self._get_system_prompt(tipo_analise)
            
            # Define o conteúdo a ser analisado
            user_content = f"DOCUMENTO PARA ANÁLISE DE SINISTROS SECURITÁRIOS:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                max_tokens=3500,
                messages=[
                    {"role": "user", "content": user_content}
                ]
            )
            
            # Extrai o resultado
            try:
                conteudo = response.content[0].text
                resultado_json = json.loads(conteudo)
            except (json.JSONDecodeError, AttributeError, IndexError):
                conteudo = response.content[0].text if hasattr(response, 'content') and response.content else str(response)
                return {
                    "success": True,
                    "analise": conteudo,
                    "legitimidade_sinistro": ["Análise baseada na legislação securitária vigente"],
                    "provider": "anthropic",
                    "modelo": "claude-sonnet-4-20250514",
                    "area_juridica": "Sinistros Securitários"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "anthropic",
                "modelo": "claude-sonnet-4-20250514",
                "area_juridica": "Sinistros Securitários",
                "timestamp": time.time()
            })
            
            return resultado_json
            
        except ImportError:
            logger.warning("Módulo Anthropic não instalado. Usando fallback.")
            return self._analisar_fallback(texto, contexto, tipo_analise)
        except Exception as e:
            logger.error(f"Erro no processamento com Anthropic: {str(e)}")
            raise
    
    def _analisar_fallback(self, texto, contexto, tipo_analise):
        """Método de fallback quando nenhum dos providers está disponível"""
        try:
            import google.generativeai as genai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return {
                    "success": False,
                    "erro": "API keys não configuradas para nenhum provider"
                }
                
            # Configura Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Monta o prompt para análise
            system_prompt = self._get_system_prompt(tipo_analise)
            
            # Define o conteúdo a ser analisado
            user_content = f"DOCUMENTO PARA ANÁLISE DE SINISTROS SECURITÁRIOS:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
                
            prompt_completo = f"{system_prompt}\n\n{user_content}\n\nResponda em formato JSON seguindo esta estrutura: {{\"analise\": \"análise completa\", \"legitimidade_sinistro\": \"análise de legitimidade\", \"coberturas_aplicaveis\": [\"cobertura 1\", \"cobertura 2\"], \"calculo_indenizacao\": \"valor e cálculo\", \"recomendacoes\": [\"recomendação 1\", \"recomendação 2\"]}}"
            
            # Realiza a análise
            response = model.generate_content(prompt_completo)
            
            # Tenta extrair o JSON da resposta
            try:
                texto_resposta = response.text
                inicio_json = texto_resposta.find('{')
                fim_json = texto_resposta.rfind('}') + 1
                
                if inicio_json >= 0 and fim_json > inicio_json:
                    json_str = texto_resposta[inicio_json:fim_json]
                    resultado_json = json.loads(json_str)
                else:
                    raise ValueError("Não foi possível encontrar JSON válido na resposta")
                
            except (ValueError, json.JSONDecodeError):
                return {
                    "success": True,
                    "analise": response.text,
                    "legitimidade_sinistro": ["Análise baseada na legislação securitária vigente"],
                    "provider": "google",
                    "modelo": "gemini-2.5-flash",
                    "area_juridica": "Sinistros Securitários"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "google",
                "modelo": "gemini-2.5-flash",
                "area_juridica": "Sinistros Securitários",
                "timestamp": time.time()
            })
            
            return resultado_json
            
        except ImportError:
            logger.error("Nenhum módulo LLM disponível")
            return {
                "success": False,
                "erro": "Não foi possível realizar a análise: nenhum provider LLM disponível"
            }
        except Exception as e:
            logger.error(f"Erro no processamento fallback: {str(e)}")
            return {
                "success": False,
                "erro": f"Falha na análise: {str(e)}"
            }
    
    def _get_system_prompt(self, tipo_analise):
        """Obtém o prompt de sistema para análise de sinistros securitários"""
        base_prompt = """Você é um especialista sênior em Sinistros e Liquidação Securitária, com mais de 20 anos de experiência em análise técnica de sinistros, avaliação de coberturas e processos de liquidação no mercado brasileiro de seguros.

Sua expertise inclui:
- Código Civil Brasileiro (Lei 10.406/2002) - Contratos de Seguro
- Código de Defesa do Consumidor (Lei 8.078/1990)
- Lei Complementar 126/2007 (Microsseguros)
- Resoluções CNSP e Circulares SUSEP
- Jurisprudência do STJ sobre contratos de seguro
- Análise atuarial e cálculos de indenização
- Investigação de fraudes e perícias técnicas

INSTRUÇÕES ESPECÍFICAS:

1. Analise TECNICAMENTE o documento sob a perspectiva de sinistros securitários
2. Avalie legitimidade do sinistro com base nas coberturas contratadas
3. Identifique exclusões aplicáveis e cláusulas restritivas
4. Calcule indenizações considerando franquias e participação obrigatória
5. Detecte possíveis indícios de fraude ou inconsistências
6. Forneça orientações práticas sobre liquidação e pagamento"""

        if tipo_analise == 'legitimidade':
            return base_prompt + """

Foque especialmente em:
- Análise detalhada da legitimidade do sinistro
- Verificação de coberturas e exclusões aplicáveis
- Análise de documentação e comprovação do sinistro
- Identificação de possíveis agravamentos de risco
- Avaliação de nexo causal entre evento e dano"""

        elif tipo_analise == 'calculo':
            return base_prompt + """

Foque especialmente em:
- Cálculo preciso da indenização devida
- Aplicação de franquias e participação obrigatória
- Análise de depreciação e valor atual
- Verificação de limites máximos de indenização
- Cálculo de juros e correção monetária"""

        elif tipo_analise == 'fraude':
            return base_prompt + """

Foque especialmente em:
- Identificação de indícios de fraude
- Análise de inconsistências na documentação
- Verificação de agravamento doloso do risco
- Avaliação de má-fé do segurado
- Recomendações para investigação adicional"""

        else:
            return base_prompt + """

Realize uma análise abrangente do sinistro, cobrindo legitimidade, cálculo de indenização e possíveis irregularidades."""