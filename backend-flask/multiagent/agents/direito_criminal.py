"""
Agente especialista em Direito Criminal para análise de casos penais.
"""
import os
import json
import logging
import time
from multiagent.agents.base_juridico import BaseJuridicoAgent

logger = logging.getLogger('multiagent.agents.direito_criminal')

class EspecialistaDireitoCriminalAgent(BaseJuridicoAgent):
    """
    Agente especialista em Direito Criminal.
    
    Este agente analisa questões relacionadas ao Direito Penal brasileiro,
    incluindo análise de tipos penais, dosimetria da pena, circunstâncias
    agravantes e atenuantes, excludentes de ilicitude e culpabilidade,
    prescrição e outros institutos penais relevantes.
    """
    
    def _processar(self, data):
        """
        Processa análises relacionadas ao Direito Criminal.
        
        Args:
            data: Dicionário com o texto a ser analisado
            
        Returns:
            Dicionário com os resultados da análise
        """
        texto = data.get('texto', '')
        if not texto:
            return {"erro": "Nenhum texto fornecido para análise"}
        
        # Parâmetros de configuração
        provider = self.config.get('llm_provider', 'openai')
        formato_saida = self.config.get('formato_saida', 'html')
        nivel_detalhe = self.config.get('nivel_detalhe', 'medio')
        
        # Usa o LLM apropriado conforme a configuração
        try:
            if provider == 'openai':
                resultado = self._analisar_openai(texto, nivel_detalhe)
            elif provider == 'anthropic':
                resultado = self._analisar_anthropic(texto, nivel_detalhe)
            else:
                resultado = self._analisar_fallback(texto, nivel_detalhe)
                
            # Formata o resultado conforme solicitado
            resultado_formatado = self._formatar_saida(resultado, formato_saida)
            
            return {
                "resultado": resultado,
                "resultado_formatado": resultado_formatado,
                "formato": formato_saida,
                "provider": provider,
                "nivel_detalhe": nivel_detalhe,
                "tipo_documento": "direito_criminal"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar caso de Direito Criminal: {str(e)}")
            return {
                "erro": f"Falha na análise: {str(e)}",
                "texto_original": texto[:500] + "..." if len(texto) > 500 else texto
            }
    
    def _analisar_openai(self, texto, nivel_detalhe):
        """Analisa o documento utilizando OpenAI"""
        try:
            import openai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {"erro": "API key da OpenAI não configurada"}
                
            # Configura cliente OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Sistema de prompt baseado no nível de detalhe
            system_prompt = self._get_system_prompt(nivel_detalhe)
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Extrai o resultado
            conteudo = response.choices[0].message.content
            
            # Estrutura o resultado
            return {
                "analise": conteudo,
                "modelo": "gpt-4o",
                "provider": "openai"
            }
            
        except ImportError:
            logger.warning("Módulo OpenAI não instalado. Usando fallback.")
            return self._analisar_fallback(texto, nivel_detalhe)
        except Exception as e:
            logger.error(f"Erro no processamento com OpenAI: {str(e)}")
            raise
    
    def _analisar_anthropic(self, texto, nivel_detalhe):
        """Analisa o documento utilizando Anthropic"""
        try:
            import anthropic
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return {"erro": "API key da Anthropic não configurada"}
                
            # Configura cliente Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Sistema de prompt baseado no nível de detalhe
            system_prompt = self._get_system_prompt(nivel_detalhe)
            
            # Realiza a análise
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": texto}
                ]
            )
            
            # Extrai o resultado
            conteudo = response.content[0].text
            
            # Estrutura o resultado
            return {
                "analise": conteudo,
                "modelo": "claude-sonnet-4-20250514",
                "provider": "anthropic"
            }
            
        except ImportError:
            logger.warning("Módulo Anthropic não instalado. Usando fallback.")
            return self._analisar_fallback(texto, nivel_detalhe)
        except Exception as e:
            logger.error(f"Erro no processamento com Anthropic: {str(e)}")
            raise
    
    def _analisar_fallback(self, texto, nivel_detalhe):
        """Método de fallback quando nenhum dos providers está disponível"""
        try:
            import google.generativeai as genai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return {
                    "analise": "Não foi possível realizar a análise: nenhum provider LLM disponível",
                    "erro": "API keys não configuradas para nenhum provider"
                }
                
            # Configura Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Sistema de prompt baseado no nível de detalhe
            system_prompt = self._get_system_prompt(nivel_detalhe)
            
            # Realiza a análise
            response = model.generate_content(
                [system_prompt, texto],
                generation_config={"temperature": 0.2}
            )
            
            # Extrai o resultado
            conteudo = response.text
            
            # Estrutura o resultado
            return {
                "analise": conteudo,
                "modelo": "gemini-2.5-flash",
                "provider": "google"
            }
            
        except ImportError:
            logger.error("Nenhum módulo LLM disponível")
            return {
                "analise": "Não foi possível realizar a análise: nenhum provider LLM disponível",
                "erro": "Módulos LLM não instalados"
            }
        except Exception as e:
            logger.error(f"Erro no processamento fallback: {str(e)}")
            return {
                "analise": f"Falha na análise: {str(e)}",
                "erro": str(e)
            }
    
    def _get_system_prompt(self, nivel_detalhe):
        """Obtém o prompt de sistema adequado ao nível de detalhe"""
        # Base prompt específico para análise de Direito Criminal
        prompt = """Você é um especialista em Direito Penal brasileiro, com mais de 20 anos de experiência acadêmica e profissional, incluindo atuação como promotor, advogado criminalista e professor.

INSTRUÇÕES TÉCNICAS ESPECÍFICAS:

1. Analise ESTRITAMENTE o conteúdo do documento fornecido, sem acrescentar suposições ou criar fatos fictícios
2. Responda de forma técnico-jurídica, utilizando a nomenclatura exata presente no Código Penal e leis especiais
3. Identifique os dispositivos legais específicos aplicáveis (artigos do CP, CPP e legislação penal especial)
4. Evite análises genéricas - suas observações devem estar diretamente relacionadas ao texto analisado
5. Abstenha-se de criar "modelos" de análise - cada resposta deve ser integralmente baseada no documento específico
6. Utilize jurisprudência concreta e atual, citando números de recursos/processos quando aplicável
7. Não utilize templates ou respostas prontas - cada análise deve ser única e específica

Analise o documento fornecido e identifique APENAS:

1. O tipo penal específico discutido (artigo do CP ou lei específica)
2. Elementos do tipo objetivo e subjetivo presentes no caso concreto
3. Análise técnica da conduta, resultado, nexo causal e tipicidade
4. Eventuais causas excludentes de ilicitude ou culpabilidade mencionadas
5. Jurisprudência vinculante específica do STF/STJ aplicável ao caso concreto
6. Avaliação técnica das teses mencionadas no documento, usando terminologia penal precisa

IMPORTANTE: Responda SOMENTE com base no conteúdo do documento. Se algo não estiver explícito no texto, indique claramente que 'o documento não fornece informações suficientes sobre [tema]' em vez de presumir detalhes."""

        # Ajusta conforme o nível de detalhe
        if nivel_detalhe == 'minimo':
            prompt += "\n\nFaça uma análise rápida e superficial, focando apenas nos pontos mais críticos."
        elif nivel_detalhe == 'baixo':
            prompt += "\n\nMantenha a análise concisa, destacando apenas os elementos essenciais."
        elif nivel_detalhe == 'medio':
            prompt += "\n\nForneça uma análise equilibrada, cobrindo os pontos principais com detalhes moderados."
        elif nivel_detalhe == 'alto':
            prompt += "\n\nRealize uma análise detalhada, explorando nuances e implicações jurídicas mais profundas."
        elif nivel_detalhe == 'completo':
            prompt += """
\nFaça uma análise exaustiva e abrangente, incluindo:
            
- Precedentes jurisprudenciais detalhados do STF e STJ específicos para o caso
- Súmulas vinculantes ou orientações aplicáveis ao tema
- Análise técnica detalhada de cada elemento do tipo penal
- Discussão das diferentes correntes doutrinárias sobre o tema
- Análise da dosimetria da pena aplicável (quando relevante)
- Estratégias processuais detalhadas para diferentes cenários
- Recomendações específicas para cada ponto identificado
"""

        return prompt
    
    def _formatar_saida(self, resultado, formato):
        """Formata o resultado no formato solicitado"""
        analise = resultado.get('analise', '')
        
        if formato == 'html':
            # Converte quebras de linha em parágrafos HTML
            html = ''
            for paragrafo in analise.split('\n\n'):
                if paragrafo.strip():
                    # Detecta títulos (linhas que começam com números ou palavras-chave)
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo penal', 'elementos', 'conduta', 'excludentes', 'jurisprudência', 'estratégias', 'avaliação']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica analise-criminal">
                <h2>Análise Jurídica - Direito Criminal</h2>
                {html}
            </div>
            """
            return resultado_formatado
            
        elif formato == 'markdown':
            # Converte para markdown simples
            markdown = ''
            for paragrafo in analise.split('\n\n'):
                if paragrafo.strip():
                    # Detecta títulos
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo penal', 'elementos', 'conduta', 'excludentes', 'jurisprudência', 'estratégias', 'avaliação']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica - Direito Criminal

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA - DIREITO CRIMINAL

{analise}
"""
            return resultado_formatado