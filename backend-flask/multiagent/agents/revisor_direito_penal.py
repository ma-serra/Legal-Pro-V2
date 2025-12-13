"""
Agente revisor especializado em Direito Penal para segunda opinião jurídica.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.revisor_direito_penal')

class RevisorDireitoPenalAgent(BaseJuridicoAgent):
    """
    Agente especializado em revisar análises de Direito Penal.
    
    Este agente analisa análises já realizadas por outros especialistas em direito penal,
    identificando pontos de concordância, divergência, complementações necessárias, 
    e validando com base em jurisprudência atual e doutrina especializada.
    """
    
    def _processar(self, data):
        """
        Processa revisões de análises de Direito Penal.
        
        Args:
            data: Dicionário com a análise original e contexto opcional
            
        Returns:
            Dicionário com os resultados da revisão
        """
        analise_original = data.get('analise_original', '')
        contexto = data.get('contexto', '')
        
        if not analise_original:
            return {"erro": "Nenhuma análise original fornecida para revisão"}
        
        # Parâmetros de configuração
        provider = self.config.get('llm_provider', 'openai')
        
        # Usa o LLM apropriado conforme a configuração
        try:
            if provider == 'openai':
                resultado = self._revisar_openai(analise_original, contexto)
            elif provider == 'anthropic':
                resultado = self._revisar_anthropic(analise_original, contexto)
            else:
                resultado = self._revisar_fallback(analise_original, contexto)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao revisar análise penal: {str(e)}")
            return {
                "erro": f"Falha na revisão: {str(e)}",
                "success": False
            }
    
    def _revisar_openai(self, analise_original, contexto):
        """Revisa a análise utilizando OpenAI"""
        try:
            import openai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {"erro": "API key da OpenAI não configurada", "success": False}
                
            # Configura cliente OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Monta o prompt para revisão
            system_prompt = self._get_system_prompt()
            
            # Define o conteúdo a ser analisado, incluindo contexto se disponível
            user_content = f"ANÁLISE ORIGINAL A SER REVISADA:\n\n{analise_original}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=3000,
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
                "modelo": "gpt-4o"
            })
            
            return resultado_json
            
        except ImportError:
            logger.warning("Módulo OpenAI não instalado. Usando fallback.")
            return self._revisar_fallback(analise_original, contexto)
        except Exception as e:
            logger.error(f"Erro no processamento com OpenAI: {str(e)}")
            raise
    
    def _revisar_anthropic(self, analise_original, contexto):
        """Revisa a análise utilizando Anthropic"""
        try:
            import anthropic
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return {"erro": "API key da Anthropic não configurada", "success": False}
                
            # Configura cliente Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Monta o prompt para revisão
            system_prompt = self._get_system_prompt()
            
            # Define o conteúdo a ser analisado, incluindo contexto se disponível
            user_content = f"ANÁLISE ORIGINAL A SER REVISADA:\n\n{analise_original}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
            
            # Realiza a análise
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": user_content}
                ]
            )
            
            # Extrai o resultado - tentar processar como JSON
            try:
                conteudo = response.content[0].text
                resultado_json = json.loads(conteudo)
            except (json.JSONDecodeError, AttributeError, IndexError):
                # Caso falhe, tenta extrair manualmente
                conteudo = response.content[0].text if hasattr(response, 'content') and response.content else str(response)
                return {
                    "success": True,
                    "revisao": conteudo,
                    "nivel_concordancia": 3,  # valor padrão
                    "pontos_divergentes": ["Não foi possível extrair pontos divergentes automaticamente"],
                    "pontos_complementares": ["Não foi possível extrair pontos complementares automaticamente"],
                    "provider": "anthropic",
                    "modelo": "claude-sonnet-4-20250514"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "anthropic",
                "modelo": "claude-sonnet-4-20250514"
            })
            
            return resultado_json
            
        except ImportError:
            logger.warning("Módulo Anthropic não instalado. Usando fallback.")
            return self._revisar_fallback(analise_original, contexto)
        except Exception as e:
            logger.error(f"Erro no processamento com Anthropic: {str(e)}")
            raise
    
    def _revisar_fallback(self, analise_original, contexto):
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
            
            # Monta o prompt para revisão
            system_prompt = self._get_system_prompt()
            
            # Define o conteúdo a ser analisado, incluindo contexto se disponível
            user_content = f"ANÁLISE ORIGINAL A SER REVISADA:\n\n{analise_original}"
            if contexto:
                user_content += f"\n\nCONTEXTO ADICIONAL:\n\n{contexto}"
                
            prompt_completo = f"{system_prompt}\n\n{user_content}\n\nResponda em formato JSON estritamente seguindo esta estrutura: {{\"nivel_concordancia\": número de 1 a 5, \"revisao\": \"texto da revisão completa\", \"pontos_divergentes\": [\"ponto 1\", \"ponto 2\"], \"pontos_complementares\": [\"ponto 1\", \"ponto 2\"]}}"
            
            # Realiza a análise
            response = model.generate_content(prompt_completo)
            
            # Tenta extrair o JSON da resposta
            try:
                texto_resposta = response.text
                # Encontra o JSON na resposta
                inicio_json = texto_resposta.find('{')
                fim_json = texto_resposta.rfind('}') + 1
                
                if inicio_json >= 0 and fim_json > inicio_json:
                    json_str = texto_resposta[inicio_json:fim_json]
                    resultado_json = json.loads(json_str)
                else:
                    raise ValueError("Não foi possível encontrar JSON válido na resposta")
                
            except (ValueError, json.JSONDecodeError):
                # Fallback se não conseguir extrair JSON
                return {
                    "success": True,
                    "revisao": response.text,
                    "nivel_concordancia": 3,  # valor padrão
                    "pontos_divergentes": ["Não foi possível extrair pontos divergentes automaticamente"],
                    "pontos_complementares": ["Não foi possível extrair pontos complementares automaticamente"],
                    "provider": "google",
                    "modelo": "gemini-2.5-flash"
                }
            
            # Adiciona metadados
            resultado_json.update({
                "success": True,
                "provider": "google",
                "modelo": "gemini-2.5-flash"
            })
            
            return resultado_json
            
        except ImportError:
            logger.error("Nenhum módulo LLM disponível")
            return {
                "success": False,
                "erro": "Não foi possível realizar a revisão: nenhum provider LLM disponível"
            }
        except Exception as e:
            logger.error(f"Erro no processamento fallback: {str(e)}")
            return {
                "success": False,
                "erro": f"Falha na revisão: {str(e)}"
            }
    
    def _get_system_prompt(self):
        """Obtém o prompt de sistema para revisão"""
        return """Você é um especialista sênior em Direito Penal e Processo Penal brasileiro, com mais de 25 anos de experiência acadêmica e profissional, incluindo atuação como Desembargador e Professor de Direito Penal.

Sua tarefa é revisar tecnicamente uma análise jurídica na área penal, fornecendo uma segunda opinião especializada sobre ela.

INSTRUÇÕES TÉCNICAS ESPECÍFICAS:

1. Analise ESTRITAMENTE o conteúdo da análise original fornecida, sem acrescentar suposições ou criar fatos fictícios
2. Forneça uma segunda opinião técnico-jurídica, utilizando a terminologia exata da doutrina e jurisprudência penal
3. Identifique dispositivos legais específicos relevantes (artigos do CP, CPP e legislação penal especial)
4. Evite análises genéricas - suas observações devem estar diretamente relacionadas à análise original
5. Não utilize templates ou respostas prontas - cada revisão deve ser única e específica
6. Cite jurisprudência concreta quando relevante, preferencialmente com números de processos/súmulas
7. Mantenha foco exclusivo nos aspectos jurídicos levantados na análise original

Após analisar o documento, você deve fornecer sua revisão em formato JSON com os seguintes campos:

1. "nivel_concordancia": Um número de 1 a 5 que representa seu nível geral de concordância com a análise original (1 = discordância significativa, 5 = concordância total)

2. "revisao": Uma análise técnica completa que detalhe sua segunda opinião, tratando tanto de pontos de concordância quanto de divergência, sempre com fundamento legal e jurisprudencial específico

3. "pontos_divergentes": Uma lista detalhada dos pontos específicos onde você discorda da análise original, com fundamentação técnica, limitando-se a no máximo 5 pontos principais

4. "pontos_complementares": Uma lista de aspectos relevantes que a análise original não abordou ou poderia ter desenvolvido melhor, também com fundamentação técnica, limitando-se a no máximo 5 pontos principais

IMPORTANTE: Sua resposta deve ser em formato JSON válido e deve basear-se ESTRITAMENTE na análise original fornecida. Não invente fatos, não adicione contexto fictício, e não presuma informações que não estejam claras no texto original."""