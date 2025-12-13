"""
Agentes jurídicos especializados para análise de documentos legais.

Inclui agentes especializados em diversas áreas jurídicas:
- Direito Trabalhista
- Direito Previdenciário
- Análise de Riscos Jurídicos
- Direito Bancário
- Direito Securitário
"""
import os
import json
import logging
import time

logger = logging.getLogger('multiagent.agents.juridicos')

# Importamos a classe base jurídica específica
from multiagent.agents.base_juridico import BaseJuridicoAgent as BaseAgent

class EspecialistaDireitoBancarioAgent(BaseAgent):
    """
    Agente especialista em análise de questões de direito bancário.
    
    Este agente analisa contratos bancários, financiamentos, operações de crédito,
    procedimentos de cobrança e outros documentos relacionados ao sistema financeiro,
    identificando cláusulas abusivas, riscos jurídicos e oportunidades de defesa.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito bancário.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "bancario"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento bancário: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito bancário brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (contrato de financiamento, abertura de conta, cartão de crédito, etc.)
2. Partes envolvidas e seus papéis (cliente, instituição financeira, garantidor)
3. Cláusulas relevantes e suas implicações jurídicas
4. Identificação de cláusulas potencialmente abusivas
5. Taxas e encargos aplicados e sua conformidade legal
6. Riscos jurídicos para as partes
7. Conformidade com o Código de Defesa do Consumidor e normas do Banco Central
8. Recomendações e estratégias de defesa (se aplicável)

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto."""

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
            
- Precedentes jurisprudenciais relevantes do STJ e outros tribunais
- Análise doutrinária aplicável
- Cálculo detalhado dos encargos e verificação de capitalização de juros
- Possíveis estratégias processuais e administrativas
- Estimativa de valores e riscos financeiros
- Probabilidade de sucesso em diferentes cenários
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'cláusulas', 'taxas', 'riscos', 'conformidade', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Bancária</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'cláusulas', 'taxas', 'riscos', 'conformidade', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Bancária

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA BANCÁRIA

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoSecuritarioAgent(BaseAgent):
    """
    Agente especialista em análise de questões de direito securitário.
    
    Este agente analisa contratos de seguro, apólices, sinistros, regulações,
    e procedimentos relativos ao mercado de seguros, identificando coberturas,
    exclusões, direitos dos segurados e estratégias para resolução de conflitos.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito securitário.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "securitario"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento securitário: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito securitário brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (apólice, contrato de seguro, aviso de sinistro, regulação, etc.)
2. Partes envolvidas (segurador, segurado, beneficiários, terceiros)
3. Tipo de seguro e coberturas contratadas
4. Exclusões e limitações de cobertura
5. Cláusulas relevantes e suas implicações jurídicas
6. Conformidade com o Código Civil, SUSEP e normas regulatórias
7. Riscos jurídicos e possíveis vulnerabilidades
8. Recomendações e estratégias para o segurado/beneficiário

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto do mercado securitário."""

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
            
- Precedentes jurisprudenciais relevantes do STJ e outros tribunais
- Circulares e normativos relevantes da SUSEP
- Análise doutrinária aplicável
- Interpretação detalhada das exclusões e limitações
- Possíveis estratégias administrativas e judiciais
- Estimativa de valores envolvidos e chances de sucesso
- Cálculo de indenizações com base nos termos da apólice
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'tipo de seguro', 'exclusões', 'cláusulas', 'conformidade', 'riscos', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Securitária</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'tipo de seguro', 'exclusões', 'cláusulas', 'conformidade', 'riscos', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Securitária

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA SECURITÁRIA

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoTrabalhistaAgent(BaseAgent):
    """
    Agente especialista em análise de documentos de direito trabalhista.
    
    Este agente utiliza LLMs para analisar contratos, reclamações, recursos 
    e outros documentos relacionados ao direito do trabalho, identificando
    cláusulas críticas, riscos, precedentes relevantes e recomendações.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito trabalhista.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "trabalhista"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento trabalhista: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito trabalhista brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (contrato, reclamação, recurso, etc.)
2. Partes envolvidas e seus papéis
3. Questões principais em disputa
4. Fundamentos legais relevantes (artigos, súmulas, etc.)
5. Riscos jurídicos identificados
6. Recomendações estratégicas

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto."""

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
            
- Precedentes jurisprudenciais relevantes
- Análise doutrinária aplicável
- Possíveis estratégias processuais
- Estimativa de valores e riscos financeiros
- Probabilidade de sucesso em diferentes cenários
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'questões', 'fundamentos', 'riscos', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Trabalhista</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'questões', 'fundamentos', 'riscos', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Trabalhista

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA TRABALHISTA

{analise}
"""
            return resultado_formatado

class ConsultorDireitoPrevidenciarioAgent(BaseAgent):
    """
    Agente especialista em consultorias previdenciárias.
    
    Este agente analisa documentos relacionados à previdência social,
    identificando direitos, requisitos, cálculos de benefícios e estratégias
    para maximizar os benefícios previdenciários.
    """
    
    def _processar(self, data):
        """
        Processa consultas previdenciárias.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
        Returns:
            Dicionário com os resultados da análise
        """
        texto = data.get('texto', '')
        if not texto:
            return {"erro": "Nenhum texto fornecido para análise"}
        
        # Parâmetros de configuração
        provider = self.config.get('llm_provider', 'openai')
        formato_saida = self.config.get('formato_saida', 'html')
        
        # Usa o LLM apropriado conforme a configuração
        try:
            if provider == 'openai':
                resultado = self._analisar_openai(texto)
            elif provider == 'anthropic':
                resultado = self._analisar_anthropic(texto)
            else:
                resultado = self._analisar_fallback(texto)
                
            # Formata o resultado conforme solicitado
            resultado_formatado = self._formatar_saida(resultado, formato_saida)
            
            return {
                "resultado": resultado,
                "resultado_formatado": resultado_formatado,
                "formato": formato_saida,
                "provider": provider,
                "tipo_documento": "previdenciario"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento previdenciário: {str(e)}")
            return {
                "erro": f"Falha na análise: {str(e)}",
                "texto_original": texto[:500] + "..." if len(texto) > 500 else texto
            }
    
    def _analisar_openai(self, texto):
        """Analisa o documento utilizando OpenAI"""
        try:
            import openai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {"erro": "API key da OpenAI não configurada"}
                
            # Configura cliente OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Sistema de prompt para análise previdenciária
            system_prompt = """Você é um especialista em direito previdenciário brasileiro com mais de 20 anos de experiência.
            
Analise o documento fornecido e identifique:

1. Tipo de documento ou consulta (processo administrativo, pedido de aposentadoria, etc.)
2. Situação previdenciária do segurado (tempo de contribuição, idade, qualidade de segurado)
3. Direitos e benefícios aplicáveis
4. Requisitos legais necessários
5. Cálculos estimados de benefícios (quando aplicável)
6. Estratégias recomendadas para otimizar os benefícios
7. Riscos e limitações identificados
8. Fundamentos legais (leis, decretos, jurisprudências)

Seja preciso, objetivo e didático, explicando conceitos técnicos em linguagem acessível ao segurado."""
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",
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
            return self._analisar_fallback(texto)
        except Exception as e:
            logger.error(f"Erro no processamento com OpenAI: {str(e)}")
            raise
    
    def _analisar_anthropic(self, texto):
        """Analisa o documento utilizando Anthropic"""
        try:
            import anthropic
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return {"erro": "API key da Anthropic não configurada"}
                
            # Configura cliente Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Sistema de prompt para análise previdenciária
            system_prompt = """Você é um especialista em direito previdenciário brasileiro com mais de 20 anos de experiência.
            
Analise o documento fornecido e identifique:

1. Tipo de documento ou consulta (processo administrativo, pedido de aposentadoria, etc.)
2. Situação previdenciária do segurado (tempo de contribuição, idade, qualidade de segurado)
3. Direitos e benefícios aplicáveis
4. Requisitos legais necessários
5. Cálculos estimados de benefícios (quando aplicável)
6. Estratégias recomendadas para otimizar os benefícios
7. Riscos e limitações identificados
8. Fundamentos legais (leis, decretos, jurisprudências)

Seja preciso, objetivo e didático, explicando conceitos técnicos em linguagem acessível ao segurado."""
            
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
            return self._analisar_fallback(texto)
        except Exception as e:
            logger.error(f"Erro no processamento com Anthropic: {str(e)}")
            raise
    
    def _analisar_fallback(self, texto):
        """Método de fallback quando nenhum dos providers está disponível"""
        try:
            # Tenta usar Google Gemini se disponível
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
            
            # Sistema de prompt para análise previdenciária
            system_prompt = """Você é um especialista em direito previdenciário brasileiro.
            
Analise o documento fornecido e identifique:
1. Tipo de documento ou consulta
2. Situação previdenciária do segurado
3. Direitos e benefícios aplicáveis
4. Requisitos legais necessários
5. Estratégias recomendadas
6. Fundamentos legais"""
            
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
    
    def _formatar_saida(self, resultado, formato):
        """Formata o resultado no formato solicitado"""
        analise = resultado.get('analise', '')
        
        if formato == 'html':
            # Converte quebras de linha em parágrafos HTML
            html = ''
            for paragrafo in analise.split('\n\n'):
                if paragrafo.strip():
                    # Detecta títulos (linhas que começam com números ou palavras-chave)
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'situação previdenciária', 'direitos', 'requisitos', 'cálculos', 'estratégias', 'riscos', 'fundamentos']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-previdenciaria">
                <h2>Análise Previdenciária</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'situação previdenciária', 'direitos', 'requisitos', 'cálculos', 'estratégias', 'riscos', 'fundamentos']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Previdenciária

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE PREVIDENCIÁRIA

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoTributarioAgent(BaseAgent):
    """
    Agente especialista em direito tributário.
    
    Este agente analisa documentos fiscais, autos de infração, planilhas de cálculo,
    procedimentos administrativos e ações tributárias, identificando obrigações,
    contingências, riscos fiscais e oportunidades de economia tributária.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito tributário.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "tributario"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento tributário: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito tributário brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (auto de infração, recurso administrativo, planejamento tributário, etc.)
2. Tributos envolvidos (ICMS, ISS, IRPJ, CSLL, PIS/COFINS, etc.)
3. Fatos geradores e operações tributáveis
4. Questões principais em disputa ou análise
5. Principais legislações aplicáveis (leis, decretos, IN, etc.)
6. Riscos tributários identificados
7. Oportunidades de economia tributária (se aplicável)
8. Recomendações estratégicas para o contribuinte

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto da área tributária."""

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
            
- Precedentes administrativos e judiciais relevantes do STF, STJ e tribunais administrativos
- Análise doutrinária aplicável
- Cálculo detalhado dos valores em discussão, incluindo principal, multa e juros
- Possíveis estratégias administrativas e judiciais
- Estimativa de tempo de tramitação e custos
- Probabilidade de sucesso em diferentes cenários
- Sugestões de provas e argumentos complementares
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'tributos', 'fatos geradores', 'questões', 'legislações', 'riscos', 'oportunidades', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Tributária</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'tributos', 'fatos geradores', 'questões', 'legislações', 'riscos', 'oportunidades', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Tributária

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA TRIBUTÁRIA

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoImobiliarioAgent(BaseAgent):
    """
    Agente especialista em direito imobiliário.
    
    Este agente analisa contratos de compra e venda, locação, financiamentos imobiliários,
    processos de usucapião, incorporações e outros documentos relacionados ao
    mercado imobiliário, identificando riscos, direitos e obrigações das partes.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito imobiliário.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "imobiliario"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento imobiliário: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito imobiliário brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (contrato de compra e venda, locação, financiamento, etc.)
2. Partes envolvidas e seus papéis (comprador, vendedor, locador, locatário, etc.)
3. Objeto/imóvel descrito e suas características principais
4. Cláusulas relevantes e suas implicações jurídicas
5. Possíveis problemas ou cláusulas desfavoráveis
6. Riscos jurídicos para as partes
7. Conformidade com o Código Civil, Lei de Locações e demais legislações aplicáveis
8. Recomendações estratégicas para proteção jurídica das partes envolvidas

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto do direito imobiliário."""

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
            
- Verificação detalhada de cada cláusula contratual
- Análise da documentação necessária para segurança jurídica da operação
- Precedentes jurisprudenciais relevantes sobre questões similares
- Recomendações para diligências adicionais (certidões, matrículas, etc.)
- Possíveis estratégias em caso de litígio
- Sugestões de alterações contratuais para maior proteção
- Implicações fiscais da operação
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'objeto', 'cláusulas', 'problemas', 'riscos', 'conformidade', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Imobiliária</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'objeto', 'cláusulas', 'problemas', 'riscos', 'conformidade', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Imobiliária

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA IMOBILIÁRIA

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoDigitalAgent(BaseAgent):
    """
    Agente especialista em direito digital e proteção de dados.
    
    Este agente analisa políticas de privacidade, termos de uso, relatórios de impacto,
    contratos de processamento de dados e documentos relacionados à privacidade,
    segurança da informação e direito digital, identificando conformidade com LGPD e outras
    legislações digitais.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito digital.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "digital"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento de direito digital: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito digital e proteção de dados brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (política de privacidade, termos de uso, contrato de processamento, etc.)
2. Partes envolvidas e seus papéis (controlador, operador, encarregado, titular, etc.)
3. Finalidades de tratamento de dados pessoais mencionadas
4. Bases legais utilizadas para o tratamento
5. Conformidade com a LGPD e outras legislações aplicáveis (Marco Civil, etc.)
6. Direitos dos titulares mencionados e mecanismos de exercício
7. Riscos de privacidade e pontos de não conformidade
8. Recomendações para adequação e melhoria da proteção de dados

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto da proteção de dados."""

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
            
- Avaliação detalhada dos mecanismos de segurança mencionados
- Análise de transferências internacionais de dados
- Verificação de medidas de accountability documentadas
- Avaliação de riscos de multas da ANPD e outras autoridades
- Sugestões específicas para cada ponto de não conformidade
- Recomendações para implementação de privacy by design/default
- Implicações em casos de incidentes de segurança
- Análise comparativa com melhores práticas de mercado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'finalidades', 'bases legais', 'conformidade', 'direitos', 'riscos', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica de Privacidade e Dados</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'partes envolvidas', 'finalidades', 'bases legais', 'conformidade', 'direitos', 'riscos', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica de Privacidade e Dados

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA DE PRIVACIDADE E DADOS

{analise}
"""
            return resultado_formatado

class EspecialistaDireitoEmpresarialAgent(BaseAgent):
    """
    Agente especialista em direito empresarial e societário.
    
    Este agente analisa contratos sociais, alterações contratuais, atas de reunião,
    acordos de acionistas, operações societárias e outros documentos corporativos,
    identificando riscos, conformidade e oportunidades de otimização societária.
    """
    
    def _processar(self, data):
        """
        Processa documentos de direito empresarial.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
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
                "tipo_documento": "empresarial"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento empresarial: {str(e)}")
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
                model="gpt-4o",
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
        # Base prompt
        prompt = """Você é um especialista em direito empresarial e societário brasileiro com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento (contrato social, estatuto, ata, acordo de acionistas, etc.)
2. Natureza societária (Ltda, S.A., EIRELI, etc.) e regime aplicável
3. Estrutura de capital e governança
4. Cláusulas relevantes e suas implicações jurídicas
5. Direitos e obrigações dos sócios/acionistas
6. Conformidade com o Código Civil, Lei das S.A. e legislações aplicáveis
7. Riscos jurídicos para a empresa e sócios
8. Oportunidades de otimização societária e melhorias contratuais

Seja preciso, objetivo e utilize o vocabulário técnico-jurídico correto do direito empresarial."""

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
            
- Análise detalhada da estrutura de capital e impactos fiscais
- Pontos de atenção relacionados à responsabilidade dos sócios/administradores
- Verificação de cláusulas de proteção em operações críticas
- Implicações na sucessão empresarial e planejamento patrimonial 
- Comparativo com melhores práticas de governança corporativa
- Possíveis conflitos entre documentos societários
- Sugestões para reorganização societária mais eficiente
- Recomendações detalhadas para cada aspecto identificado
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'natureza societária', 'estrutura', 'cláusulas', 'direitos', 'conformidade', 'riscos', 'oportunidades']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-juridica">
                <h2>Análise Jurídica Empresarial</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'natureza societária', 'estrutura', 'cláusulas', 'direitos', 'conformidade', 'riscos', 'oportunidades']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise Jurídica Empresarial

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE JURÍDICA EMPRESARIAL

{analise}
"""
            return resultado_formatado

class AnalistaRiscosJuridicosAgent(BaseAgent):
    """
    Agente especialista em análise de riscos jurídicos.
    
    Este agente identifica, quantifica e prioriza riscos legais em documentos,
    contratos e processos, oferecendo estratégias de mitigação.
    """
    
    def _processar(self, data):
        """
        Processa análises de riscos jurídicos.
        
        Args:
            data: Dicionário com o texto e/ou informações a serem analisadas
            
        Returns:
            Dicionário com os resultados da análise
        """
        texto = data.get('texto', '')
        if not texto:
            return {"erro": "Nenhum texto fornecido para análise"}
        
        # Parâmetros de configuração
        provider = self.config.get('llm_provider', 'openai')
        formato_saida = self.config.get('formato_saida', 'html')
        nivel_risco = self.config.get('nivel_risco', 'moderado')  # básico, moderado, detalhado
        
        # Usa o LLM apropriado conforme a configuração
        try:
            if provider == 'openai':
                resultado = self._analisar_openai(texto, nivel_risco)
            elif provider == 'anthropic':
                resultado = self._analisar_anthropic(texto, nivel_risco)
            else:
                resultado = self._analisar_fallback(texto, nivel_risco)
                
            # Formata o resultado conforme solicitado
            resultado_formatado = self._formatar_saida(resultado, formato_saida)
            
            return {
                "resultado": resultado,
                "resultado_formatado": resultado_formatado,
                "formato": formato_saida,
                "provider": provider,
                "nivel_risco": nivel_risco,
                "tipo_documento": "riscos_juridicos"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar riscos jurídicos: {str(e)}")
            return {
                "erro": f"Falha na análise: {str(e)}",
                "texto_original": texto[:500] + "..." if len(texto) > 500 else texto
            }
    
    def _analisar_openai(self, texto, nivel_risco):
        """Analisa o documento utilizando OpenAI"""
        try:
            import openai
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {"erro": "API key da OpenAI não configurada"}
                
            # Configura cliente OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Sistema de prompt baseado no nível de risco
            system_prompt = self._get_system_prompt(nivel_risco)
            
            # Realiza a análise
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto}
                ],
                temperature=0.1,  # Menor temperatura para análise de risco (mais conservador)
                max_tokens=2500
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
            return self._analisar_fallback(texto, nivel_risco)
        except Exception as e:
            logger.error(f"Erro no processamento com OpenAI: {str(e)}")
            raise
    
    def _analisar_anthropic(self, texto, nivel_risco):
        """Analisa o documento utilizando Anthropic"""
        try:
            import anthropic
            
            # Verifica se há API key configurada
            api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return {"erro": "API key da Anthropic não configurada"}
                
            # Configura cliente Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Sistema de prompt baseado no nível de risco
            system_prompt = self._get_system_prompt(nivel_risco)
            
            # Realiza a análise
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                max_tokens=2500,
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
            return self._analisar_fallback(texto, nivel_risco)
        except Exception as e:
            logger.error(f"Erro no processamento com Anthropic: {str(e)}")
            raise
    
    def _analisar_fallback(self, texto, nivel_risco):
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
            
            # Sistema de prompt simplificado para Gemini
            system_prompt = """Você é um especialista em análise de riscos jurídicos.
            
Analise o documento fornecido e identifique:
1. Tipo de documento e seu contexto
2. Principais riscos jurídicos
3. Probabilidade e impacto de cada risco
4. Estratégias recomendadas de mitigação
5. Conformidade legal"""
            
            # Realiza a análise
            response = model.generate_content(
                [system_prompt, texto],
                generation_config={"temperature": 0.1}
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
    
    def _get_system_prompt(self, nivel_risco):
        """Obtém o prompt de sistema adequado ao nível de risco"""
        # Base prompt para análise de riscos
        prompt = """Você é um especialista em análise de riscos jurídicos com mais de 20 anos de experiência.
        
Analise o documento fornecido e identifique:

1. Tipo de documento e seu contexto legal
2. Riscos jurídicos identificados (listar em ordem de prioridade)
3. Para cada risco identificado:
   - Probabilidade de ocorrência (alta, média, baixa)
   - Impacto potencial (alto, médio, baixo)
   - Base legal relacionada
4. Conformidade com a legislação aplicável
5. Recomendações para mitigação de riscos

Seja preciso, objetivo e abrangente na sua análise."""

        # Ajusta conforme o nível de risco
        if nivel_risco == 'basico':
            prompt += """
            
Forneça uma análise básica focada apenas nos riscos mais críticos e imediatos, com recomendações simples e diretas."""
        elif nivel_risco == 'moderado':
            prompt += """
            
Forneça uma análise moderadamente detalhada, cobrindo os principais riscos com recomendações específicas de mitigação."""
        elif nivel_risco == 'detalhado':
            prompt += """
            
Forneça uma análise exaustiva e detalhada, incluindo:
- Análise aprofundada de cada cláusula ou elemento relevante
- Quantificação numérica dos riscos (probabilidade e impacto em percentuais)
- Precedentes jurisprudenciais relevantes
- Análise de tendências regulatórias que podem afetar a situação
- Plano detalhado de mitigação com cronograma sugerido
- Estimativa de custos/perdas potenciais
- Considerações sobre seguros e resseguros aplicáveis"""

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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'riscos', 'probabilidade', 'impacto', 'conformidade', 'recomendações']):
                        html += f'<h3>{paragrafo}</h3>'
                    else:
                        html += f'<p>{paragrafo}</p>'
            
            # Adiciona estrutura básica e estilo
            resultado_formatado = f"""
            <div class="analise-riscos">
                <h2>Análise de Riscos Jurídicos</h2>
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
                    if paragrafo.strip()[0].isdigit() or any(keyword in paragrafo.lower() for keyword in ['tipo de documento', 'riscos', 'probabilidade', 'impacto', 'conformidade', 'recomendações']):
                        markdown += f'### {paragrafo}\n\n'
                    else:
                        markdown += f'{paragrafo}\n\n'
            
            resultado_formatado = f"""
# Análise de Riscos Jurídicos

{markdown}
"""
            return resultado_formatado
            
        elif formato == 'json':
            # Retorna o resultado estruturado diretamente
            return json.dumps(resultado, ensure_ascii=False)
            
        else:  # Formato texto
            resultado_formatado = f"""
ANÁLISE DE RISCOS JURÍDICOS

{analise}
"""
            return resultado_formatado

# Registra os agentes especializados no dicionário
AGENTES_JURIDICOS = {
    'especialista_direito_trabalhista': EspecialistaDireitoTrabalhistaAgent,
    'consultor_direito_previdenciario': ConsultorDireitoPrevidenciarioAgent,
    'analista_riscos_juridicos': AnalistaRiscosJuridicosAgent
}

def listar_agentes_por_categoria(categoria_nome):
    """
    Lista os agentes jurídicos por categoria.
    
    Args:
        categoria_nome: Nome da categoria
        
    Returns:
        Lista de agentes
    """
    # Mapeamento entre categorias e agentes
    mapeamento = {
        'Trabalhista': ['especialista_direito_trabalhista'],
        'Previdenciário': ['consultor_direito_previdenciario'],
        'Riscos': ['analista_riscos_juridicos'],
        'Bancário': ['especialista_direito_bancario'],
        'Securitário': ['especialista_direito_securitario']
    }
    
    # Retorna a lista de agentes da categoria ou lista vazia
    return mapeamento.get(categoria_nome, [])