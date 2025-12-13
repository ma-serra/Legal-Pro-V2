import os
import logging
import json
import base64
import requests
from multiagent.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GeradorImagensAgent(BaseAgent):
    """
    Agente que gera imagens a partir de descrições textuais.
    
    Este agente utiliza APIs de geração de imagens para criar visualizações
    com base em prompts textuais.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configurações da API
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key não configurada. Configure a variável de ambiente OPENAI_API_KEY.")
        
        # Configurações de geração de imagem
        self.modelo = self.config.get("modelo", "dall-e-3")
        self.tamanho = self.config.get("tamanho", "1024x1024")
        self.formato = self.config.get("formato", "url")  # url ou b64_json
        self.qualidade = self.config.get("qualidade", "standard")  # standard ou hd
        self.quantidade = min(self.config.get("quantidade", 1), 4)  # API limita a 4 imagens por request
        
        # Configurações de prompt
        self.melhorar_prompt = self.config.get("melhorar_prompt", True)
        
    def _melhorar_descricao(self, descricao):
        """
        Aprimora a descrição da imagem usando LLM para gerar prompts melhores.
        
        Args:
            descricao: Descrição original da imagem
            
        Returns:
            Descrição melhorada e mais detalhada
        """
        if not self.melhorar_prompt:
            return descricao
            
        try:
            # Configura a API do OpenAI para melhorar o prompt
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista em aprimorar prompts para geração de imagens. "
                                   "Seu trabalho é transformar descrições simples em prompts detalhados que resultem "
                                   "em imagens de alta qualidade. Adicione detalhes sobre iluminação, ângulo, "
                                   "expressões, cores, atmosfera e estilo artístico. Responda apenas com o prompt "
                                   "aprimorado, sem comentários ou explicações. Não use aspas ou delimitadores." 
                    },
                    {
                        "role": "user",
                        "content": descricao
                    }
                ],
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            response_data = response.json()
            prompt_melhorado = response_data["choices"][0]["message"]["content"].strip()
            
            self.logger.info("Prompt aprimorado com sucesso")
            return prompt_melhorado
            
        except Exception as e:
            self.logger.warning(f"Erro ao aprimorar prompt: {str(e)}. Usando prompt original.")
            return descricao
        
    def _gerar_imagem_openai(self, prompt):
        """
        Gera imagem usando a API DALL-E da OpenAI.
        
        Args:
            prompt: Descrição da imagem a ser gerada
            
        Returns:
            URLs ou dados base64 das imagens geradas
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.modelo,
                "prompt": prompt,
                "n": self.quantidade,
                "size": self.tamanho,
                "quality": self.qualidade,
                "response_format": self.formato
            }
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload
            )
            
            response_data = response.json()
            
            if "error" in response_data:
                raise ValueError(f"Erro na API de geração de imagens: {response_data['error']['message']}")
                
            return response_data["data"]
            
        except Exception as e:
            self.logger.error(f"Erro na geração da imagem: {str(e)}")
            raise
        
    def _processar(self, data):
        """
        Gera imagens com base em descrições textuais.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            Dicionário com as imagens geradas
        """
        # Obtém a descrição da imagem
        descricao = data.get("descricao_imagem") or data.get("prompt_imagem")
        
        # Se não houver descrição específica, tenta extrair do texto
        if not descricao:
            texto = data.get("texto") or data.get("conteudo")
            if texto:
                descricao = f"Crie uma imagem representativa para o seguinte texto: {texto[:500]}"
            else:
                raise ValueError("Não há descrição para gerar imagem")
                
        self.logger.info(f"Gerando imagem a partir da descrição: {descricao[:100]}...")
        
        # Aprimora o prompt se a configuração estiver ativada
        prompt_final = self._melhorar_descricao(descricao)
        
        # Gera a imagem
        imagens_geradas = self._gerar_imagem_openai(prompt_final)
        
        # Constrói o resultado
        resultado = data.copy()  # Mantém os dados originais
        resultado["imagens"] = {
            "prompt_original": descricao,
            "prompt_aprimorado": prompt_final if self.melhorar_prompt else None,
            "configuracao": {
                "modelo": self.modelo,
                "tamanho": self.tamanho,
                "qualidade": self.qualidade
            },
            "resultados": imagens_geradas
        }
        
        return resultado