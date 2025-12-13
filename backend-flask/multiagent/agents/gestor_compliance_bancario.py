"""
Agente especializado em Compliance e Regulamentação Bancária.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.gestor_compliance_bancario')

class GestorComplianceBancarioAgent(BaseJuridicoAgent):
    """
    Agente especializado em Compliance e Regulamentação Bancária.
    
    Este agente monitora e interpreta normas do Banco Central, CVM e demais órgãos reguladores,
    fornecendo orientações sobre adequação regulatória e gestão de compliance.
    """
    
    def _processar(self, data):
        """
        Processa análises de Compliance e Regulamentação Bancária.
        
        Args:
            data: Dicionário com o texto a ser analisado e configurações
            
        Returns:
            Dicionário com os resultados da análise de compliance
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
            logger.error(f"Erro ao analisar compliance bancário: {str(e)}")
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE COMPLIANCE BANCÁRIO:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,  # Baixa temperatura para análise regulatória precisa
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
                "area_juridica": "Compliance Bancário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE COMPLIANCE BANCÁRIO:\n\n{texto}"
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
                    "normas_aplicaveis": ["Análise baseada na regulamentação bancária vigente"],
                    "provider": "anthropic",
                    "modelo": "claude-sonnet-4-20250514",
                    "area_juridica": "Compliance Bancário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "anthropic",
                "modelo": "claude-sonnet-4-20250514",
                "area_juridica": "Compliance Bancário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE COMPLIANCE BANCÁRIO:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
                
            prompt_completo = f"{system_prompt}\n\n{user_content}\n\nResponda em formato JSON seguindo esta estrutura: {{\"analise\": \"análise completa\", \"normas_aplicaveis\": [\"norma 1\", \"norma 2\"], \"obrigacoes_compliance\": [\"obrigação 1\", \"obrigação 2\"], \"alertas_regulatorios\": [\"alerta 1\", \"alerta 2\"], \"recomendacoes\": [\"recomendação 1\", \"recomendação 2\"]}}"
            
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
                    "normas_aplicaveis": ["Análise baseada na regulamentação bancária vigente"],
                    "provider": "google",
                    "modelo": "gemini-2.5-flash",
                    "area_juridica": "Compliance Bancário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "google",
                "modelo": "gemini-2.5-flash",
                "area_juridica": "Compliance Bancário",
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
        """Obtém o prompt de sistema para análise de compliance bancário"""
        base_prompt = """Você é um especialista sênior em Compliance e Regulamentação Bancária, com mais de 15 anos de experiência em adequação regulatória, monitoramento de normas e gestão de compliance no Sistema Financeiro Nacional.

Sua expertise inclui:
- Resoluções e Circulares do Banco Central do Brasil (BACEN)
- Instruções Normativas da Comissão de Valores Mobiliários (CVM)
- Lei 4.595/64 (Sistema Financeiro Nacional)
- Lei 12.846/13 (Lei Anticorrupção)
- Regulamentação de Prevenção à Lavagem de Dinheiro (PLD)
- Normas de Governança Corporativa e Gestão de Riscos
- Procedimentos de Due Diligence e KYC

INSTRUÇÕES ESPECÍFICAS:

1. Analise METICULOSAMENTE o documento sob a perspectiva regulatória bancária
2. Identifique obrigações de compliance e adequações regulamentares necessárias
3. Cite normas específicas (Resoluções BACEN, IN CVM, Circulares, etc.)
4. Avalie riscos regulatórios e de não conformidade
5. Forneça orientações práticas sobre adequação às normas
6. Mantenha foco na gestão proativa de compliance"""

        if tipo_analise == 'monitoramento':
            return base_prompt + """

Foque especialmente em:
- Identificação de mudanças regulatórias recentes
- Mapeamento de impactos operacionais das novas normas
- Elaboração de alertas regulatórios prioritários
- Definição de prazos de adequação
- Análise de precedentes em processos administrativos"""

        elif tipo_analise == 'adequacao':
            return base_prompt + """

Foque especialmente em:
- Avaliação do nível atual de conformidade
- Identificação de gaps regulatórios
- Plano de adequação às normas aplicáveis
- Gestão de prazos regulatórios
- Implementação de controles de compliance"""

        else:
            return base_prompt + """

Realize uma análise abrangente de compliance, identificando todos os aspectos regulatórios relevantes e fornecendo orientações para adequação normativa."""