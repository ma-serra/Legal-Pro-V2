from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider

class ResumidorAgent(BaseAgent):
    """
    Agente que gera resumos de textos.
    
    Este agente utiliza LLMs para criar resumos concisos de textos longos,
    mantendo os pontos principais e a informação essencial.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Configurações de resumo
        self.tamanho_resumo = self.config.get("tamanho_resumo", "médio")  # curto, médio, longo
        self.estilo_resumo = self.config.get("estilo_resumo", "informativo")  # informativo, narrativo, bullet-points
        self.incluir_citacoes = self.config.get("incluir_citacoes", False)
        
        # Mapeamento de tamanhos para instruções
        self.tamanhos = {
            "curto": "muito conciso (máximo 10% do tamanho original)",
            "médio": "moderadamente detalhado (máximo 25% do tamanho original)",
            "longo": "abrangente (máximo 40% do tamanho original)"
        }
        
        # Mapeamento de estilos para instruções
        self.estilos = {
            "informativo": "em formato de texto corrido com foco em fatos e informações objetivas",
            "narrativo": "em formato de texto narrativo mantendo um estilo fluido e envolvente",
            "bullet-points": "em formato de tópicos (bullet-points) destacando os pontos principais"
        }
        
    def _gerar_instrucoes_resumo(self):
        """Gera as instruções para o resumo com base nas configurações"""
        tamanho = self.tamanhos.get(self.tamanho_resumo, self.tamanhos["médio"])
        estilo = self.estilos.get(self.estilo_resumo, self.estilos["informativo"])
        
        instrucoes = f"Crie um resumo {tamanho}, {estilo}."
        
        if self.incluir_citacoes:
            instrucoes += " Inclua citações relevantes do texto original entre aspas."
            
        return instrucoes
        
    def _processar(self, data):
        """
        Gera um resumo do texto recebido.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            Dicionário com o resumo gerado
        """
        # Obtém o texto a ser resumido
        texto = data.get("texto") or data.get("conteudo")
        if not texto:
            texto = data.get("traducao", {}).get("texto_traduzido", "")
            
        if not texto:
            raise ValueError("Não há texto para resumir")
            
        # Obtém as instruções específicas para o tipo de resumo
        instrucoes_resumo = self._gerar_instrucoes_resumo()
        
        # Constrói o prompt para resumo
        prompt = f"""
        {instrucoes_resumo}
        
        O texto a ser resumido é o seguinte:
        
        {texto}
        
        Mantenha apenas as informações mais importantes e relevantes no resumo.
        Preserve a essência e os pontos-chave do texto original.
        """
        
        # Realiza o resumo
        try:
            self.logger.info(f"Resumindo texto com estilo '{self.estilo_resumo}' e tamanho '{self.tamanho_resumo}'")
            
            resultado_resumo = self.llm.gerar_texto(
                prompt=prompt,
                temperatura=0.3  # Temperatura baixa para manter fidelidade ao original
            )
            
            # Constrói o resultado
            resultado = data.copy()  # Mantém os dados originais
            resultado["resumo"] = {
                "conteudo": resultado_resumo,
                "tamanho": self.tamanho_resumo,
                "estilo": self.estilo_resumo,
                "texto_original": texto[:500] + ("..." if len(texto) > 500 else "")  # Guarda o início do texto original
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na geração do resumo: {str(e)}")
            raise