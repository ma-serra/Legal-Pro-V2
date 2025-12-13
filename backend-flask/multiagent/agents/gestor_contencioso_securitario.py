"""
Agente especializado em Contencioso e Recuperação Securitária.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.gestor_contencioso_securitario')

class GestorContenciosoSecuritarioAgent(BaseJuridicoAgent):
    """
    Agente especializado em Contencioso e Recuperação Securitária.
    
    Este agente analisa litígios securitários, desenvolve estratégias de defesa
    e gerencia ações regressivas no mercado de seguros.
    """
    
    def _processar(self, data):
        """
        Processa análises de Contencioso e Recuperação Securitária.
        
        Args:
            data: Dicionário com o texto a ser analisado e configurações
            
        Returns:
            Dicionário com os resultados da análise de contencioso securitário
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
            logger.error(f"Erro ao analisar contencioso securitário: {str(e)}")
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO SECURITÁRIO:\n\n{texto}"
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
                "area_juridica": "Contencioso Securitário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO SECURITÁRIO:\n\n{texto}"
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
                    "estrategias_defesa": ["Análise baseada na legislação processual vigente"],
                    "provider": "anthropic",
                    "modelo": "claude-sonnet-4-20250514",
                    "area_juridica": "Contencioso Securitário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "anthropic",
                "modelo": "claude-sonnet-4-20250514",
                "area_juridica": "Contencioso Securitário",
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
            user_content = f"DOCUMENTO PARA ANÁLISE DE CONTENCIOSO SECURITÁRIO:\n\n{texto}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
                
            prompt_completo = f"{system_prompt}\n\n{user_content}\n\nResponda em formato JSON seguindo esta estrutura: {{\"analise\": \"análise completa\", \"estrategias_defesa\": [\"estratégia 1\", \"estratégia 2\"], \"riscos_processuais\": [\"risco 1\", \"risco 2\"], \"acoes_regressivas\": [\"ação 1\", \"ação 2\"], \"recomendacoes\": [\"recomendação 1\", \"recomendação 2\"]}}"
            
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
                    "estrategias_defesa": ["Análise baseada na legislação processual vigente"],
                    "provider": "google",
                    "modelo": "gemini-2.5-flash",
                    "area_juridica": "Contencioso Securitário"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "google",
                "modelo": "gemini-2.5-flash",
                "area_juridica": "Contencioso Securitário",
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
        """Obtém o prompt de sistema para análise de contencioso securitário"""
        base_prompt = """Você é um especialista sênior em Contencioso e Recuperação Securitária, com mais de 20 anos de experiência em litígios securitários, estratégias de defesa e ações regressivas no mercado brasileiro de seguros.

Sua expertise inclui:
- Código de Processo Civil (Lei 13.105/2015)
- Código Civil Brasileiro - Contratos de Seguro (arts. 757-802)
- Código de Defesa do Consumidor (Lei 8.078/1990)
- Lei de Arbitragem (Lei 9.307/1996)
- Jurisprudência do STJ sobre contratos de seguro
- Ações de cobrança e execução no setor securitário
- Sub-rogação e ações regressivas

INSTRUÇÕES ESPECÍFICAS:

1. Analise ESTRATEGICAMENTE o documento sob a perspectiva do contencioso securitário
2. Identifique viabilidade processual e riscos de demandas
3. Cite dispositivos legais específicos (CPC, CC, CDC, etc.)
4. Avalie estratégias de defesa e contramedidas processuais
5. Forneça orientações práticas sobre litígios securitários
6. Mantenha foco na efetividade da defesa e proteção patrimonial"""

        if tipo_analise == 'defesa':
            return base_prompt + """

Foque especialmente em:
- Análise de estratégias de defesa em ações contra seguradoras
- Identificação de vícios processuais e nulidades
- Avaliação de prescrição e decadência
- Análise de cláusulas contratuais e excludentes
- Estratégias para contestação e recursos"""

        elif tipo_analise == 'regressiva':
            return base_prompt + """

Foque especialmente em:
- Análise de viabilidade de ações regressivas
- Direito de sub-rogação e seus requisitos
- Identificação de terceiros responsáveis
- Estratégias de recuperação de valores pagos
- Cálculo de valores e correções devidas"""

        elif tipo_analise == 'arbitragem':
            return base_prompt + """

Foque especialmente em:
- Análise de cláusulas arbitrais em contratos de seguro
- Viabilidade e estratégias para arbitragem
- Procedimentos arbitrais específicos do setor
- Vantagens e desvantagens da arbitragem
- Execução de sentenças arbitrais"""

        else:
            return base_prompt + """

Realize uma análise abrangente de contencioso securitário, identificando estratégias processuais, riscos e oportunidades de defesa."""