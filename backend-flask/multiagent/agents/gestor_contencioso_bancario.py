"""
Agente especializado em Contencioso e Recuperação Bancária.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.gestor_contencioso_bancario')

class GestorContenciosoBancarioAgent(BaseJuridicoAgent):
    """
    Agente especializado em Contencioso e Recuperação Bancária.
    
    Este agente analisa estratégias processuais, execução de garantias, recuperação de crédito
    e gestão de carteiras em contencioso bancário.
    """
    
    def _processar(self, data):
        """
        Processa análises de Contencioso e Recuperação Bancária.
        
        Args:
            data: Dicionário com o texto a ser analisado e configurações
            
        Returns:
            Dicionário com os resultados da análise de contencioso
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
            logger.error(f"Erro ao analisar contencioso bancário: {str(e)}")
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO BANCÁRIO:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2,  # Baixa temperatura para análise processual precisa
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
                "area_juridica": "Contencioso Bancário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO BANCÁRIO:\n\n{texto}"
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
                    "estrategias_processuais": ["Análise baseada na legislação processual vigente"],
                    "provider": "anthropic",
                    "modelo": "claude-sonnet-4-20250514",
                    "area_juridica": "Contencioso Bancário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "anthropic",
                "modelo": "claude-sonnet-4-20250514",
                "area_juridica": "Contencioso Bancário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO BANCÁRIO:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
                
            prompt_completo = f"{system_prompt}\n\n{user_content}\n\nResponda em formato JSON seguindo esta estrutura: {{\"analise\": \"análise completa\", \"estrategias_processuais\": [\"estratégia 1\", \"estratégia 2\"], \"riscos_processuais\": [\"risco 1\", \"risco 2\"], \"garantias_colaterais\": [\"garantia 1\", \"garantia 2\"], \"recomendacoes\": [\"recomendação 1\", \"recomendação 2\"]}}"
            
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
                    "estrategias_processuais": ["Análise baseada na legislação processual vigente"],
                    "provider": "google",
                    "modelo": "gemini-2.5-flash",
                    "area_juridica": "Contencioso Bancário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "google",
                "modelo": "gemini-2.5-flash",
                "area_juridica": "Contencioso Bancário",
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
        """Obtém o prompt de sistema para análise de contencioso bancário"""
        base_prompt = """Você é um especialista sênior em Contencioso e Recuperação Bancária, com mais de 20 anos de experiência em estratégias processuais, execução de garantias e recuperação de crédito no Sistema Financeiro Nacional.

Sua expertise inclui:
- Código de Processo Civil (Lei 13.105/2015)
- Lei de Execução Fiscal (Lei 6.830/1980)
- Lei de Recuperação Judicial e Falência (Lei 11.101/2005)
- Decreto-Lei 70/66 (Execução Extrajudicial)
- Jurisprudência do STJ sobre execução bancária
- Estratégias de cobrança e negociação
- Avaliação e execução de garantias reais e fidejussórias

INSTRUÇÕES ESPECÍFICAS:

1. Analise ESTRATEGICAMENTE o documento sob a perspectiva do contencioso bancário
2. Identifique viabilidade processual e riscos de execução
3. Cite dispositivos legais específicos (CPC, LEF, Lei 11.101/05, etc.)
4. Avalie garantias, colaterais e possibilidades de recuperação
5. Forneça estratégias práticas de cobrança e execução
6. Mantenha foco na efetividade da recuperação de crédito"""

        if tipo_analise == 'execucao':
            return base_prompt + """

Foque especialmente em:
- Análise de viabilidade da execução judicial/extrajudicial
- Avaliação de garantias reais e pessoais
- Estratégias de penhora e expropriação
- Procedimentos de arrematação e adjudicação
- Defesas processuais possíveis do devedor"""

        elif tipo_analise == 'recuperacao':
            return base_prompt + """

Foque especialmente em:
- Análise de processos de recuperação judicial/falência
- Classificação e habilitação de créditos
- Estratégias para maximizar recuperação
- Planos de recuperação e suas viabilidades
- Liquidação extrajudicial de instituições"""

        elif tipo_analise == 'negociacao':
            return base_prompt + """

Foque especialmente em:
- Estratégias de negociação e acordo
- Avaliação de propostas de renegociação
- Estruturação de parcelamentos
- Análise de capacidade de pagamento
- Formalização de acordos judiciais/extrajudiciais"""

        else:
            return base_prompt + """

Realize uma análise abrangente de contencioso, identificando estratégias processuais, riscos e oportunidades de recuperação de crédito."""