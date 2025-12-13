"""
Agente Jurídico CPFL com RAG
Sistema de IA para análise jurídica e geração de peças processuais
Modelos 2025: GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, Gemini 2.5 Flash
"""

import os
import json
from typing import List, Dict, Any, Optional, Literal
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai  # type: ignore
import logging

try:
    from .qdrant_service import qdrant_service
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from qdrant_service import qdrant_service

logger = logging.getLogger(__name__)

class CPFLAgent:
    """Agente Jurídico Inteligente com RAG e modelos de IA de última geração"""
    
    MODELS = {
        # Modelos de 2025 - Última Geração
        "gpt-5": "gpt-5",
        "gpt-5-mini": "gpt-5-mini",
        "claude-sonnet-4.5": "claude-sonnet-4-5",
        "claude-haiku-4.5": "claude-haiku-4-5",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
        # Modelos anteriores (compatibilidade)
        "gpt-4o": "gpt-4o",
        "claude-sonnet-4": "claude-sonnet-4-5",  # Alias
        "gemini-1.5-flash": "gemini-1.5-flash"
    }
    
    def __init__(self):
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.anthropic = Anthropic(api_key=anthropic_key)
            self.anthropic_available = True
        else:
            self.anthropic = None
            self.anthropic_available = False
            logger.warning("⚠️ ANTHROPIC_API_KEY não configurada - Claude indisponível")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai = OpenAI(api_key=openai_key)
            self.openai_available = True
        else:
            self.openai = None
            self.openai_available = False
            logger.warning("⚠️ OPENAI_API_KEY não configurada - GPT indisponível")
        
        gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)  # type: ignore
            self.gemini_available = True
        else:
            self.gemini_available = False
            logger.warning("⚠️ GEMINI_API_KEY não configurada - Gemini indisponível")
        
        self.qdrant = qdrant_service
        
        self.system_prompt = """Você é um assistente jurídico especializado da CPFL Energia, com acesso a uma base de 3.216 processos jurídicos reais.

SUAS CAPACIDADES:
- Análise detalhada de processos judiciais da CPFL
- Identificação de precedentes e padrões jurisprudenciais
- Recomendações estratégicas baseadas em dados históricos
- Geração de peças processuais fundamentadas
- Análise preditiva de resultados

DIRETRIZES:
1. SEMPRE consulte a base de processos antes de responder
2. Cite números de processos específicos quando relevante
3. Fundamente suas análises em dados reais
4. Seja preciso e técnico em linguagem jurídica
5. Identifique padrões e tendências nos dados
6. Apresente estatísticas quando disponíveis

FORMATO DE RESPOSTA:
- Contexto: Processos similares encontrados
- Análise: Interpretação jurídica fundamentada
- Recomendação: Estratégia baseada em precedentes
- Referências: Processos específicos citados

Você se comunica de advogado para advogado, com rigor técnico e citação de precedentes."""
    
    def process_query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        model: str = "gpt-5",
        max_processos: int = 5
    ) -> Dict[str, Any]:
        """
        Processa consulta jurídica com RAG
        
        Args:
            query: Pergunta ou consulta do usuário
            filters: Filtros opcionais (causa_raiz, comarca, etc)
            model: Modelo de IA a ser usado (gpt-5, claude-sonnet-4.5, gemini-2.5-flash, etc)
            max_processos: Número máximo de processos similares a buscar
        
        Returns:
            Dict com resposta, processos consultados e metadata
        """
        try:
            # Tentar buscar processos similares no Qdrant
            similar_processos = []
            context = ""
            
            try:
                similar_processos = self.qdrant.search_similar_processos(
                    query=query,
                    filters=filters,
                    limit=max_processos
                )
                context = self._build_context(similar_processos)
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível buscar processos no Qdrant: {e}")
                context = "Base de dados de processos temporariamente indisponível. Fornecendo análise baseada em conhecimento jurídico geral."
            
            prompt = f"""CONSULTA DO USUÁRIO:
{query}

PROCESSOS RELEVANTES ENCONTRADOS:
{context}

Analise a consulta considerando as informações disponíveis. Forneça uma resposta completa e fundamentada."""
            
            # Detectar provedor e tentar usar com fallback automático
            model_name = self.MODELS.get(model, model)
            provider = self._detect_provider(model_name)
            
            response = None
            provider_used = None
            
            # Tentar o modelo solicitado primeiro
            if provider == "openai" and self.openai_available:
                try:
                    response = self._query_openai(prompt, model_name)
                    provider_used = "openai"
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao usar OpenAI: {e}")
            
            # Fallback para Claude se OpenAI falhar ou não estiver disponível
            if not response and provider == "claude" and self.anthropic_available:
                try:
                    response = self._query_claude(prompt, model_name)
                    provider_used = "claude"
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao usar Claude: {e}")
            
            # Fallback para Gemini se outros falharem ou não estiverem disponíveis
            if not response and self.gemini_available:
                try:
                    response = self._query_gemini(prompt, "gemini-2.5-flash")
                    provider_used = "gemini"
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao usar Gemini: {e}")
            
            # Se nenhum modelo funcionar, tentar OpenAI GPT-5 como último recurso
            if not response and self.openai_available and provider != "openai":
                try:
                    response = self._query_openai(prompt, "gpt-5")
                    provider_used = "openai"
                except Exception as e:
                    logger.error(f"❌ Todos os modelos falharam: {e}")
            
            if not response:
                return {
                    'success': False,
                    'error': 'Nenhum modelo de IA disponível no momento',
                    'response': 'Desculpe, os modelos de IA estão temporariamente indisponíveis. Por favor, verifique as configurações de API ou tente novamente mais tarde.'
                }
            
            return {
                'success': True,
                'response': response,
                'processos_consultados': len(similar_processos),
                'processos': similar_processos,
                'model_used': model_name,
                'provider': provider_used or provider
            }
            
        except Exception as e:
            logger.error(f"❌ Erro crítico ao processar consulta: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'response': 'Desculpe, ocorreu um erro crítico ao processar sua consulta.'
            }
    
    def _detect_provider(self, model_name: str) -> Literal["claude", "openai", "gemini"]:
        """Detecta o provedor baseado no nome do modelo"""
        if "claude" in model_name.lower():
            return "claude"
        elif "gpt" in model_name.lower():
            return "openai"
        elif "gemini" in model_name.lower():
            return "gemini"
        return "claude"
    
    def _build_context(self, processos: List[Dict[str, Any]]) -> str:
        """Constrói contexto a partir dos processos similares"""
        if not processos:
            return "Nenhum processo similar encontrado na base de dados."
        
        context_parts = []
        for i, item in enumerate(processos, 1):
            proc = item['processo']
            score = item['score']
            
            context_parts.append(f"""
PROCESSO {i} (Similaridade: {score:.2%}):
Número: {proc.get('numero_processo', 'N/A')}
Causa-Raiz: {proc.get('causa_raiz', 'N/A')}
Comarca: {proc.get('comarca', 'N/A')}
Valor: R$ {proc.get('valor_envolvido', 0):,.2f}
Decisão 1ª Instância: {proc.get('decisao_1_instancia', 'Pendente')}
Resultado: {proc.get('resultado_final', 'Em andamento')}
Fase: {proc.get('fase', 'N/A')}

Texto completo:
{proc.get('texto', '')}
---
""")
        
        return '\n'.join(context_parts)
    
    def _query_claude(self, prompt: str, model: str) -> str:
        """
        Consulta Claude Sonnet 4 ou 3.5 Sonnet
        Configuração otimizada para análise jurídica
        """
        if not self.anthropic_available or not self.anthropic:
            raise ValueError("Claude não está disponível - ANTHROPIC_API_KEY não configurada")
        
        try:
            response = self.anthropic.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.2,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content_block = response.content[0]  # type: ignore
            if hasattr(content_block, 'text'):
                return content_block.text  # type: ignore
            return str(content_block)
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar Claude: {e}")
            raise
    
    def _query_openai(self, prompt: str, model: str = "gpt-5") -> str:
        """
        Consulta GPT-5, GPT-5-mini ou GPT-4o
        Com configuração otimizada para precisão jurídica
        """
        if not self.openai_available or not self.openai:
            raise ValueError("OpenAI não está disponível - OPENAI_API_KEY não configurada")
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 8000,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.1
            }
            
            response = self.openai.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            return content if content else "Erro: resposta vazia do modelo"
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar OpenAI ({model}): {e}")
            raise
    
    def _query_gemini(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Consulta Gemini 2.5 Flash, 2.5 Flash Lite ou 1.5 Flash
        Com configuração otimizada para análise jurídica
        """
        if not self.gemini_available:
            raise ValueError("Gemini não está disponível. Configure GEMINI_API_KEY.")
        
        try:
            gemini_model = genai.GenerativeModel(  # type: ignore
                model_name=model,
                generation_config={  # type: ignore
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain"
                },
                safety_settings={  # type: ignore
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
                },
                system_instruction=self.system_prompt
            )
            
            response = gemini_model.generate_content(prompt)
            return response.text  # type: ignore
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar Gemini ({model}): {e}")
            raise
    
    def generate_peca_processual(
        self,
        tipo_peca: str,
        dados_processo: Dict[str, Any],
        model: str = "claude-sonnet-4.5"
    ) -> str:
        """
        Gera peça processual baseada em precedentes
        
        Args:
            tipo_peca: Tipo de peça (contestação, recurso, etc)
            dados_processo: Dados do processo atual
            model: Modelo de IA a usar
        
        Returns:
            Texto da peça processual gerada
        """
        query = f"Processos similares a: {dados_processo.get('causa_raiz', '')} em {dados_processo.get('comarca', '')}"
        
        similar = self.qdrant.search_similar_processos(query, limit=3)
        context = self._build_context(similar)
        
        prompt = f"""Gere uma {tipo_peca} para o seguinte processo:

DADOS DO PROCESSO:
{json.dumps(dados_processo, indent=2, ensure_ascii=False)}

PRECEDENTES SIMILARES:
{context}

Elabore uma {tipo_peca} profissional, técnica e fundamentada nos precedentes acima."""
        
        model_name = self.MODELS.get(model, model)
        provider = self._detect_provider(model_name)
        
        if provider == "claude":
            return self._query_claude(prompt, model_name)
        elif provider == "openai":
            return self._query_openai(prompt, model_name)
        elif provider == "gemini":
            return self._query_gemini(prompt, model_name)
        else:
            raise ValueError(f"Modelo não suportado: {model}")
    
    def generate_json_analysis(
        self,
        query: str,
        model: str = "gpt-5"
    ) -> Dict[str, Any]:
        """
        Gera análise estruturada em JSON (GPT-5/4o e Gemini 2.5)
        
        Returns:
            Dict com análise estruturada
        """
        if model not in ["gpt-5", "gpt-5-mini", "gpt-4o", "gemini-2.5-flash", "gemini-2.5-flash-lite"]:
            raise ValueError("JSON estruturado disponível para GPT-5, GPT-4o e Gemini 2.5")
        
        json_prompt = f"""Analise a seguinte consulta e retorne um JSON com:
- analise: análise detalhada (string)
- probabilidade_sucesso: probabilidade de sucesso 0-1 (float)
- recomendacao: recomendação estratégica (string)
- precedentes: array de processos similares

CONSULTA: {query}"""
        
        if model in ["gpt-5", "gpt-5-mini", "gpt-4o"]:
            response = self.openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": json_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content or "{}")
        
        else:
            gemini_model = genai.GenerativeModel(  # type: ignore
                model_name=model,
                generation_config={  # type: ignore
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                },
                system_instruction=self.system_prompt
            )
            
            response = gemini_model.generate_content(json_prompt)
            return json.loads(response.text)  # type: ignore

cpfl_agent = CPFLAgent()
