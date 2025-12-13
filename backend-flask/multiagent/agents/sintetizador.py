import logging
import json
from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider

logger = logging.getLogger(__name__)

class SintetizadorAgent(BaseAgent):
    """
    Agente responsável por sintetizar as informações analisadas e gerar um resultado coerente.
    
    Este agente combina todas as análises anteriores para gerar uma síntese clara e concisa,
    adequada ao formato e objetivo definidos na configuração.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Configurações específicas de síntese
        self.formato_sintese = self.config.get("formato_sintese", "resumo")
        self.nivel_detalhe = self.config.get("nivel_detalhe", "medio")
        self.foco_sintese = self.config.get("foco_sintese", None)
        self.max_palavras = self.config.get("max_palavras", None)
        
        # Mapeamento de nível de detalhe para configuração de tokens
        self.detalhes_config = {
            "minimo": {"max_tokens": 100, "temperatura": 0.3},
            "baixo": {"max_tokens": 200, "temperatura": 0.4},
            "medio": {"max_tokens": 400, "temperatura": 0.5},
            "alto": {"max_tokens": 800, "temperatura": 0.6},
            "completo": {"max_tokens": 1500, "temperatura": 0.7}
        }
        
        # Formatos de síntese suportados
        self.formatos_suportados = ["resumo", "pontos", "relatorio", "narrativa", "resposta", "json"]
        
        # Normaliza formato para um dos suportados
        if self.formato_sintese not in self.formatos_suportados:
            self.logger.warning(f"Formato {self.formato_sintese} não suportado, usando 'resumo'")
            self.formato_sintese = "resumo"
            
        # Normaliza nível de detalhe
        if self.nivel_detalhe not in self.detalhes_config:
            self.logger.warning(f"Nível de detalhe {self.nivel_detalhe} não suportado, usando 'medio'")
            self.nivel_detalhe = "medio"
            
        self.logger.info(f"SintetizadorAgent inicializado com formato {self.formato_sintese} e nível {self.nivel_detalhe}")
    
    def _gerar_prompt_sintese(self, data):
        """
        Gera o prompt para síntese baseado nos dados e configurações.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            String com o prompt de síntese
        """
        # Obtém os dados relevantes
        infos_extraidas = data.get("informacoes_extraidas", {})
        texto_original = data.get("texto_original", "")
        classificacao = data.get("classificacao", {})
        analises = data.get("analises", {})
        tags = data.get("tags", [])
        
        # Constrói um contexto estruturado com as informações disponíveis
        contexto = "Contexto da análise:\n"
        
        # Adiciona classificação se disponível
        if classificacao and "categorias" in classificacao:
            categorias = classificacao["categorias"]
            contexto += "\nCategorias identificadas:\n"
            for cat, score in categorias.items():
                contexto += f"- {cat}: {score:.2f}\n"
                
        # Adiciona análise de sentimento se disponível
        if analises and "sentimento" in analises:
            sentimento = analises["sentimento"]
            contexto += "\nAnálise de sentimento:\n"
            contexto += f"- Polaridade: {sentimento.get('polaridade', 'N/A')}\n"
            contexto += f"- Intensidade: {sentimento.get('intensidade', 'N/A')}\n"
            if "emocoes" in sentimento and sentimento["emocoes"]:
                contexto += f"- Emoções: {', '.join(sentimento.get('emocoes', []))}\n"
                
        # Adiciona entidades se disponível
        if analises and "entidades" in analises:
            entidades = analises["entidades"]
            has_entities = False
            
            for tipo, lista in entidades.items():
                if lista and tipo != "erro":
                    if not has_entities:
                        contexto += "\nEntidades identificadas:\n"
                        has_entities = True
                    if isinstance(lista, list) and lista:
                        contexto += f"- {tipo.capitalize()}: {', '.join(lista[:5])}\n"
                        
        # Adiciona insights se disponível
        if analises and "insights" in analises:
            insights = analises["insights"]
            if "pontos_principais" in insights and insights["pontos_principais"]:
                contexto += "\nPontos principais:\n"
                if isinstance(insights["pontos_principais"], list):
                    for ponto in insights["pontos_principais"][:3]:
                        contexto += f"- {ponto}\n"
                        
            if "conclusoes" in insights and insights["conclusoes"]:
                contexto += "\nConclusões:\n"
                if isinstance(insights["conclusoes"], list):
                    for conclusao in insights["conclusoes"][:2]:
                        contexto += f"- {conclusao}\n"
                        
        # Constrói o prompt baseado no formato solicitado
        if self.formato_sintese == "resumo":
            prompt = f"""
            Com base nas informações e análises a seguir, crie um resumo coeso e bem estruturado.
            
            {contexto}
            
            {f"Foco específico da síntese: {self.foco_sintese}" if self.foco_sintese else ""}
            {f"Limite: máximo de {self.max_palavras} palavras." if self.max_palavras else ""}
            
            Sintetize todas as informações relevantes em um texto fluido e informativo.
            """
            
        elif self.formato_sintese == "pontos":
            prompt = f"""
            Com base nas informações e análises a seguir, crie uma lista de pontos-chave.
            
            {contexto}
            
            {f"Foco específico da síntese: {self.foco_sintese}" if self.foco_sintese else ""}
            
            Organize os pontos mais importantes em tópicos claros e concisos.
            Comece cada ponto com um marcador e mantenha cada item direto e informativo.
            """
            
        elif self.formato_sintese == "relatorio":
            prompt = f"""
            Com base nas informações e análises a seguir, crie um relatório estruturado.
            
            {contexto}
            
            {f"Foco específico do relatório: {self.foco_sintese}" if self.foco_sintese else ""}
            
            O relatório deve incluir:
            1. Introdução - contextualizando o assunto
            2. Análise dos dados - detalhando os principais insights
            3. Conclusões - sintetizando as descobertas principais
            4. Recomendações - quando aplicável
            
            Estruture o relatório com títulos claros para cada seção.
            """
            
        elif self.formato_sintese == "narrativa":
            prompt = f"""
            Com base nas informações e análises a seguir, crie uma narrativa engajante.
            
            {contexto}
            
            {f"Foco específico da narrativa: {self.foco_sintese}" if self.foco_sintese else ""}
            
            Apresente as informações em forma de história, com início, meio e fim.
            Mantenha um tom envolvente mas informativo, conectando os diversos elementos analisados.
            """
            
        elif self.formato_sintese == "resposta":
            prompt = f"""
            Com base nas informações e análises a seguir, crie uma resposta direta e objetiva.
            
            {contexto}
            
            {f"Foco específico da resposta: {self.foco_sintese}" if self.foco_sintese else ""}
            
            Formule uma resposta clara e concisa que aborde os pontos principais identificados.
            A resposta deve ser direta e focada nos aspectos mais relevantes.
            """
            
        elif self.formato_sintese == "json":
            prompt = f"""
            Com base nas informações e análises a seguir, crie um objeto JSON estruturado.
            
            {contexto}
            
            {f"Foco específico da síntese: {self.foco_sintese}" if self.foco_sintese else ""}
            
            O JSON deve incluir os seguintes campos:
            - resumo: Um resumo conciso do conteúdo
            - pontos_principais: Lista dos pontos mais importantes
            - categorias: As categorias identificadas com seus respectivos scores
            - sentimento: A análise de sentimento
            - entidades: As principais entidades identificadas
            - conclusoes: As principais conclusões da análise
            
            Retorne apenas o objeto JSON, sem comentários adicionais.
            """
            
        else:
            # Formato padrão como fallback
            prompt = f"""
            Com base nas informações e análises a seguir, crie uma síntese abrangente.
            
            {contexto}
            
            {f"Foco específico da síntese: {self.foco_sintese}" if self.foco_sintese else ""}
            {f"Limite: máximo de {self.max_palavras} palavras." if self.max_palavras else ""}
            
            Combine as informações e análises em um texto coerente que capture os pontos mais importantes.
            """
            
        return prompt.strip()
    
    def _processar(self, data):
        """
        Processa os dados para gerar a síntese final.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            Dicionário com a síntese gerada
        """
        # Gera o prompt para síntese
        prompt_sintese = self._gerar_prompt_sintese(data)
        
        # Define sistema adequado ao formato
        system_prompt = f"""
        Você é um especialista em sintetização de informações, focado em criar conteúdo no formato '{self.formato_sintese}'.
        
        Seu objetivo é combinar diversas análises e informações em uma síntese coerente,
        mantendo um nível de detalhe '{self.nivel_detalhe}'.
        
        Seja conciso, claro e estruturado. Foque apenas nas informações mais relevantes.
        """
        
        # Obtém configurações baseadas no nível de detalhe
        config = self.detalhes_config.get(self.nivel_detalhe, self.detalhes_config["medio"])
        
        # Determina se deve usar formato JSON
        formato_json = self.formato_sintese == "json"
        
        # Realiza a síntese usando o LLM
        try:
            resultado_sintese = self.llm.gerar_texto(
                prompt=prompt_sintese,
                system_prompt=system_prompt,
                temperatura=config["temperatura"],
                max_tokens=config["max_tokens"],
                formato_json=formato_json
            )
            
            # Processa o resultado
            if formato_json:
                # Tenta converter para dicionário se veio como string
                if isinstance(resultado_sintese, str):
                    try:
                        resultado_sintese = json.loads(resultado_sintese)
                    except json.JSONDecodeError:
                        self.logger.warning("Falha ao decodificar JSON, retornando texto bruto")
            
            # Constrói o resultado final
            resultado = data.copy()  # Mantém os dados dos agentes anteriores
            resultado["sintese"] = {
                "formato": self.formato_sintese,
                "nivel_detalhe": self.nivel_detalhe,
                "conteudo": resultado_sintese
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na síntese: {str(e)}")
            raise
