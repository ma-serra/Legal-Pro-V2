import logging
import json
import re
from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider

logger = logging.getLogger(__name__)

class ExtratorAgent(BaseAgent):
    """
    Agente responsável por extrair informações estruturadas de dados de entrada.
    
    Este agente analisa texto não estruturado e extrai entidades, conceitos e informações
    relevantes de acordo com a configuração fornecida.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Configurações específicas de extração
        self.campos_alvo = self.config.get("campos_alvo", [])
        self.tipo_extracao = self.config.get("tipo_extracao", "geral")
        self.formato_saida = self.config.get("formato_saida", "json")
        
        self.logger.info(f"ExtratorAgent inicializado com provider {provider} e {len(self.campos_alvo)} campos alvo")
        
    def _gerar_prompt_extracao(self, texto):
        """Gera prompt para extração de informações baseado na configuração"""
        
        # Prompt base
        prompt = "Extraia as seguintes informações do texto abaixo:\n\n"
        
        # Adiciona especificação de campos alvo se existirem
        if self.campos_alvo:
            prompt += "Campos a extrair:\n"
            for campo in self.campos_alvo:
                prompt += f"- {campo}\n"
        
        # Instruções de formato
        if self.formato_saida == "json":
            prompt += "\nForneça o resultado em formato JSON estruturado, com cada campo como uma chave."
            
        # Adiciona texto para análise
        prompt += f"\n\nTEXTO PARA ANÁLISE:\n{texto}"
        
        return prompt
        
    def _processar(self, data):
        """
        Processa os dados de entrada para extrair informações.
        
        Args:
            data: Dicionário contendo os dados de entrada
                Deve conter pelo menos a chave "texto" ou "conteudo"
                
        Returns:
            Dicionário com as informações extraídas
        """
        # Obtém o texto a ser analisado
        texto = data.get("texto") or data.get("conteudo")
        if not texto:
            raise ValueError("Dados de entrada não contêm texto para extração")
            
        # Verifica se o texto é muito longo e faz truncamento se necessário
        max_chars = 12000  # Ajuste conforme necessário
        if len(texto) > max_chars:
            self.logger.warning(f"Texto muito longo ({len(texto)} caracteres), truncando para {max_chars}")
            texto = texto[:max_chars] + "..."
            
        # Gera o prompt para extração
        prompt_extracao = self._gerar_prompt_extracao(texto)
        
        # Instruções específicas do sistema
        system_prompt = f"""
        Você é um especialista em extração de informações. 
        Seu trabalho é analisar o texto fornecido e extrair dados específicos de maneira precisa.
        Tipo de extração: {self.tipo_extracao}
        
        Siga estritamente o formato solicitado e extraia apenas as informações presentes no texto.
        Não invente ou adicione informações que não estejam explicitamente no texto.
        """
        
        # Realiza a extração usando o LLM
        try:
            resultado_extracao = self.llm.gerar_texto(
                prompt=prompt_extracao,
                system_prompt=system_prompt,
                temperatura=0.1,  # Temperatura baixa para maior precisão
                formato_json=self.formato_saida == "json"
            )
            
            # Processa o resultado
            if self.formato_saida == "json":
                # Tenta converter para dicionário se veio como string
                if isinstance(resultado_extracao, str):
                    try:
                        # Busca por blocos JSON no texto se necessário
                        json_match = re.search(r'```json\n(.*?)\n```', resultado_extracao, re.DOTALL)
                        if json_match:
                            resultado_extracao = json.loads(json_match.group(1))
                        else:
                            resultado_extracao = json.loads(resultado_extracao)
                    except json.JSONDecodeError:
                        self.logger.warning("Falha ao decodificar JSON, retornando texto bruto")
                        resultado_extracao = {"texto_extraido": resultado_extracao}
            
            # Constrói o resultado final
            resultado = {
                "texto_original": texto[:100] + "..." if len(texto) > 100 else texto,  # Versão truncada
                "informacoes_extraidas": resultado_extracao,
                "metadados": {
                    "tipo_extracao": self.tipo_extracao,
                    "campos_extraidos": self.campos_alvo if self.campos_alvo else ["texto completo"]
                }
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na extração: {str(e)}")
            raise
