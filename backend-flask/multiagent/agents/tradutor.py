from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider

class TradutorAgent(BaseAgent):
    """
    Agente que traduz texto de um idioma para outro.
    
    Este agente utiliza LLMs para traduzir conteúdo entre diferentes idiomas,
    mantendo o formato e estilo originais.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Idiomas padrão
        self.idioma_origem = self.config.get("idioma_origem", "auto")
        self.idioma_destino = self.config.get("idioma_destino", "inglês")
        
        # Nível de formalidade
        self.formalidade = self.config.get("formalidade", "neutro")
        
        # Configuração de logging
        self.registrar_prompt = self.config.get("registrar_prompt", True)
        
    def _processar(self, data):
        """
        Traduz o texto recebido.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            Dicionário com o texto traduzido
        """
        # Obtém o texto a ser traduzido
        texto = data.get("texto") or data.get("conteudo")
        if not texto:
            texto = data.get("sintese", {}).get("conteudo", "")
            
        if not texto:
            raise ValueError("Não há texto para traduzir")
        
        # Constrói o prompt para tradução
        prompt = f"""
        Traduza o seguinte texto {f'de {self.idioma_origem}' if self.idioma_origem != 'auto' else ''} para {self.idioma_destino}.
        Use um tom {self.formalidade} na tradução.
        
        {texto}
        
        Mantenha o formato, estilo e estrutura originais na tradução.
        Não adicione comentários ou explicações adicionais, apenas forneça o texto traduzido.
        """
        
        # Realiza a tradução
        try:
            self.logger.info(f"Traduzindo texto de {self.idioma_origem} para {self.idioma_destino}")
            
            if self.registrar_prompt:
                self.logger.debug(f"Prompt de tradução: {prompt}")
                
            resultado_traducao = self.llm.gerar_texto(
                prompt=prompt,
                temperatura=0.2  # Baixa temperatura para maior precisão na tradução
            )
            
            # Constrói o resultado
            resultado = data.copy()  # Mantém os dados originais
            resultado["traducao"] = {
                "idioma_origem": self.idioma_origem,
                "idioma_destino": self.idioma_destino,
                "texto_traduzido": resultado_traducao,
                "texto_original": texto
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na tradução: {str(e)}")
            raise