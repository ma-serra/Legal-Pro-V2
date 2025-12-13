import os
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic
import google.generativeai as genai

# Configuração de logging
logger = logging.getLogger(__name__)

# Inicialização de APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class LLMProvider:
    """
    Classe para gerenciar as requisições para diferentes providers de LLM.
    """
    
    # Tipos de providers suportados
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    
    def __init__(self, provider=None, model=None):
        """
        Inicializa o provider LLM.
        
        Args:
            provider: Provider a ser utilizado (openai, anthropic, google)
            model: Modelo específico a ser utilizado
        """
        # Configura provider padrão baseado nas chaves disponíveis
        if provider is None:
            if OPENAI_API_KEY:
                provider = self.OPENAI
            elif ANTHROPIC_API_KEY:
                provider = self.ANTHROPIC
            elif GOOGLE_API_KEY:
                provider = self.GOOGLE
            else:
                raise ValueError("Nenhuma chave de API encontrada. Configure OPENAI_API_KEY, ANTHROPIC_API_KEY ou GOOGLE_API_KEY.")
        
        self.provider = provider
        
        # Configura clientes baseado no provider
        if provider == self.OPENAI:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY não configurada")
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            # o modelo mais recente é "gpt-4o" que foi lançado em 13 de maio de 2024
            self.model = model or "gpt-4o"
        
        elif provider == self.ANTHROPIC:
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY não configurada")
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            # o modelo mais recente é "claude-3-5-sonnet-20241022" que foi lançado em 22 de outubro de 2024
            self.model = model or "claude-3-5-sonnet-20241022"
        
        elif provider == self.GOOGLE:
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY não configurada")
            genai.configure(api_key=GOOGLE_API_KEY)
            self.client = genai
            self.model = model or "gemini-pro"
        
        else:
            raise ValueError(f"Provider não suportado: {provider}")
            
        logger.info(f"LLMProvider inicializado com {provider} usando modelo {self.model}")
    
    def gerar_texto(self, prompt: str, 
                   system_prompt: Optional[str] = None,
                   temperatura: float = 0.7,
                   max_tokens: Optional[int] = None,
                   stop_sequences: Optional[List[str]] = None,
                   formato_json: bool = False,
                   mensagens_adicionais: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Gera texto usando o provider e modelo configurado.
        
        Args:
            prompt: Texto do prompt principal
            system_prompt: Instruções de sistema (opcional)
            temperatura: Nível de aleatoriedade (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
            stop_sequences: Sequências que finalizam a geração
            formato_json: Se deve retornar em formato JSON
            mensagens_adicionais: Lista de mensagens adicionais no formato [{role: "user|assistant", content: "texto"}]
            
        Returns:
            Texto gerado pelo modelo
        """
        start_time = time.time()
        
        try:
            # OpenAI
            if self.provider == self.OPENAI:
                messages = []
                
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                
                # Adiciona mensagens adicionais se houver
                if mensagens_adicionais:
                    messages.extend(mensagens_adicionais)
                
                # Adiciona o prompt principal
                messages.append({"role": "user", "content": prompt})
                
                response_format = {"type": "json_object"} if formato_json else None
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperatura,
                    max_tokens=max_tokens,
                    stop=stop_sequences,
                    response_format=response_format
                )
                
                return response.choices[0].message.content
            
            # Anthropic
            elif self.provider == self.ANTHROPIC:
                messages = []
                
                # Adiciona mensagens adicionais se houver
                if mensagens_adicionais:
                    for msg in mensagens_adicionais:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Adiciona o prompt principal
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=messages,
                    temperature=temperatura,
                    max_tokens=max_tokens or 1024,
                    stop_sequences=stop_sequences
                )
                
                return response.content[0].text
            
            # Google Gemini
            elif self.provider == self.GOOGLE:
                genai_model = self.client.GenerativeModel(
                    model_name=self.model,
                    generation_config={
                        "temperature": temperatura,
                        "max_output_tokens": max_tokens or 1024,
                        "stop_sequences": stop_sequences
                    }
                )
                
                messages = []
                
                if system_prompt:
                    messages.append({"role": "system", "parts": [system_prompt]})
                
                # Adiciona mensagens adicionais se houver
                if mensagens_adicionais:
                    for msg in mensagens_adicionais:
                        role = "user" if msg["role"] == "user" else "model"
                        messages.append({"role": role, "parts": [msg["content"]]})
                
                # Adiciona o prompt principal
                messages.append({"role": "user", "parts": [prompt]})
                
                response = genai_model.generate_content(messages)
                return response.text
            
        except Exception as e:
            logger.error(f"Erro ao gerar texto com {self.provider}: {str(e)}")
            raise
        finally:
            elapsed_time = time.time() - start_time
            logger.info(f"Geração com {self.provider} ({self.model}) completada em {elapsed_time:.2f}s")
    
    def classificar(self, texto: str, categorias: List[str], instrucoes: Optional[str] = None) -> Dict[str, float]:
        """
        Classifica um texto entre categorias dadas.
        
        Args:
            texto: Texto a ser classificado
            categorias: Lista de categorias possíveis
            instrucoes: Instruções adicionais para classificação
            
        Returns:
            Dicionário com scores para cada categoria
        """
        system_prompt = f"""
        Você é um classificador de texto especialista. 
        Analise o texto e classifique-o entre as seguintes categorias: {', '.join(categorias)}.
        
        Retorne apenas um objeto JSON com as categorias como chaves e scores de 0.0 a 1.0 como valores, 
        onde 1.0 significa total correspondência e 0.0 nenhuma correspondência.
        
        {instrucoes or ''}
        """
        
        try:
            resultado = self.gerar_texto(
                prompt=texto,
                system_prompt=system_prompt,
                temperatura=0.1,
                formato_json=True
            )
            
            # Converte resultado para dicionário
            if isinstance(resultado, str):
                return json.loads(resultado)
            return resultado
        
        except Exception as e:
            logger.error(f"Erro na classificação: {str(e)}")
            # Retorna classificação vazia em caso de erro
            return {categoria: 0.0 for categoria in categorias}
    
    def resumir(self, texto: str, max_palavras: Optional[int] = None, 
               foco: Optional[str] = None) -> str:
        """
        Gera um resumo do texto fornecido.
        
        Args:
            texto: Texto a ser resumido
            max_palavras: Limite máximo de palavras
            foco: Foco específico para o resumo
            
        Returns:
            Texto resumido
        """
        instrucoes = f"""
        Resuma o seguinte texto de forma clara e concisa
        {f'em no máximo {max_palavras} palavras' if max_palavras else ''}.
        {f'Foque especialmente em: {foco}' if foco else ''}
        """
        
        return self.gerar_texto(
            prompt=f"{instrucoes}\n\nTexto: {texto}",
            temperatura=0.3
        )
