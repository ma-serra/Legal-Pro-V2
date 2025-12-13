import logging
import json
from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider
from multiagent.db.vetorial import VetorialDB

logger = logging.getLogger(__name__)

class AnalisadorAgent(BaseAgent):
    """
    Agente responsável por analisar os dados classificados em profundidade.
    
    Este agente realiza análises mais detalhadas, incluindo busca por conhecimento
    no banco vetorial, análise de sentimento, identificação de padrões, etc.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai") 
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Inicializa conexão com o banco vetorial se for usar
        self.usar_banco_vetorial = self.config.get("usar_banco_vetorial", False)
        self.max_documentos_similares = self.config.get("max_documentos_similares", 3)
        
        if self.usar_banco_vetorial:
            try:
                self.vetorial_db = VetorialDB(
                    collection_name=self.config.get("vetorial_collection", "documentos")
                )
                self.logger.info("Banco vetorial inicializado com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar banco vetorial: {str(e)}")
                self.usar_banco_vetorial = False
        
        # Configuração de análises a serem realizadas
        self.analises = self.config.get("analises", ["sentimento", "entidades", "insights"])
        
        self.logger.info(f"AnalisadorAgent inicializado para realizar {', '.join(self.analises)}")
        
    def _buscar_conhecimento_relevante(self, texto, tags=None):
        """
        Busca documentos relevantes no banco vetorial.
        
        Args:
            texto: Texto para buscar documentos similares
            tags: Tags para filtrar os resultados
            
        Returns:
            Lista de documentos similares
        """
        if not self.usar_banco_vetorial:
            return []
            
        try:
            # Constrói filtro baseado em tags se fornecidas
            filter_condition = None
            if tags and isinstance(tags, list):
                filter_condition = {
                    "must": [
                        {
                            "key": "tag",
                            "match": {
                                "any": tags
                            }
                        }
                    ]
                }
                
            # Busca documentos similares
            resultados = self.vetorial_db.pesquisar_similares(
                query=texto,
                limite=self.max_documentos_similares,
                filter_condition=filter_condition
            )
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar conhecimento: {str(e)}")
            return []
    
    def _analisar_sentimento(self, texto):
        """
        Analisa o sentimento do texto.
        
        Args:
            texto: Texto para análise
            
        Returns:
            Dicionário com análise de sentimento
        """
        prompt = f"""
        Analise o sentimento do seguinte texto:
        
        {texto}
        
        Forneça uma análise detalhada do sentimento expressado, incluindo:
        1. Polaridade (positivo, negativo, neutro)
        2. Intensidade (fraca, moderada, forte)
        3. Emoções predominantes
        4. Confiança na análise (0.0 a 1.0)
        
        Responda em formato JSON.
        """
        
        system_prompt = """
        Você é um especialista em análise de sentimento.
        Forneça uma análise precisa e detalhada baseada exclusivamente no texto fornecido.
        Sua resposta deve ser um objeto JSON com as chaves: polaridade, intensidade, emocoes e confianca.
        """
        
        try:
            resultado = self.llm.gerar_texto(
                prompt=prompt,
                system_prompt=system_prompt,
                temperatura=0.1,
                formato_json=True
            )
            
            # Converte resultado para dicionário se necessário
            if isinstance(resultado, str):
                resultado = json.loads(resultado)
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na análise de sentimento: {str(e)}")
            return {
                "polaridade": "neutro",
                "intensidade": "moderada",
                "emocoes": [],
                "confianca": 0.5,
                "erro": str(e)
            }
    
    def _extrair_entidades(self, texto):
        """
        Extrai entidades nomeadas do texto.
        
        Args:
            texto: Texto para extração
            
        Returns:
            Dicionário com entidades extraídas
        """
        prompt = f"""
        Extraia as entidades nomeadas do seguinte texto:
        
        {texto}
        
        Identifique e categorize todas as entidades encontradas nos seguintes tipos:
        - Pessoas
        - Organizações
        - Locais
        - Datas
        - Valores monetários
        - Produtos
        - Eventos
        
        Para cada entidade, forneça o tipo e seu contexto no texto.
        Responda em formato JSON.
        """
        
        system_prompt = """
        Você é um especialista em extração de entidades nomeadas (NER).
        Sua tarefa é identificar e categorizar todas as entidades presentes no texto.
        Forneça uma resposta em formato JSON organizando as entidades por tipo.
        """
        
        try:
            resultado = self.llm.gerar_texto(
                prompt=prompt,
                system_prompt=system_prompt,
                temperatura=0.1,
                formato_json=True
            )
            
            # Converte resultado para dicionário se necessário
            if isinstance(resultado, str):
                resultado = json.loads(resultado)
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na extração de entidades: {str(e)}")
            return {
                "pessoas": [],
                "organizacoes": [],
                "locais": [],
                "datas": [],
                "valores": [],
                "produtos": [],
                "eventos": [],
                "erro": str(e)
            }
    
    def _gerar_insights(self, texto, analises_anteriores=None):
        """
        Gera insights baseados no texto e análises anteriores.
        
        Args:
            texto: Texto para análise
            analises_anteriores: Resultados de análises anteriores
            
        Returns:
            Dicionário com insights gerados
        """
        # Constrói um contexto com as análises anteriores
        contexto = ""
        if analises_anteriores:
            if "sentimento" in analises_anteriores:
                sentimento = analises_anteriores["sentimento"]
                contexto += f"Sentimento: Polaridade {sentimento.get('polaridade')}, Intensidade {sentimento.get('intensidade')}\n"
            
            if "entidades" in analises_anteriores:
                entidades = analises_anteriores["entidades"]
                if entidades.get("pessoas"):
                    contexto += f"Pessoas mencionadas: {', '.join(entidades.get('pessoas', []))}\n"
                if entidades.get("organizacoes"):
                    contexto += f"Organizações mencionadas: {', '.join(entidades.get('organizacoes', []))}\n"
        
        prompt = f"""
        Analise o seguinte texto e gere insights relevantes:
        
        {texto}
        
        {"Contexto de análises anteriores:" + chr(10) + contexto if contexto else ""}
        
        Gere os seguintes insights:
        1. Principais pontos abordados
        2. Conclusões lógicas que podem ser tiradas
        3. Possíveis implicações ou consequências
        4. Tendências ou padrões identificados
        5. Sugestões ou recomendações relevantes
        
        Responda em formato JSON.
        """
        
        system_prompt = """
        Você é um analista especializado em extrair insights valiosos de textos.
        Sua análise deve ser objetiva, focada nos fatos apresentados, e oferecer conclusões acionáveis.
        Responda em formato JSON com as chaves: pontos_principais, conclusoes, implicacoes, tendencias, recomendacoes.
        """
        
        try:
            resultado = self.llm.gerar_texto(
                prompt=prompt,
                system_prompt=system_prompt,
                temperatura=0.3,
                formato_json=True
            )
            
            # Converte resultado para dicionário se necessário
            if isinstance(resultado, str):
                resultado = json.loads(resultado)
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na geração de insights: {str(e)}")
            return {
                "pontos_principais": [],
                "conclusoes": [],
                "implicacoes": [],
                "tendencias": [],
                "recomendacoes": [],
                "erro": str(e)
            }
    
    def _processar(self, data):
        """
        Processa os dados para análise detalhada.
        
        Args:
            data: Dados recebidos do agente anterior (ClassificadorAgent)
            
        Returns:
            Dicionário com os resultados das análises
        """
        # Obtém as informações já extraídas e classificadas
        infos_extraidas = data.get("informacoes_extraidas", {})
        texto_original = data.get("texto_original", "")
        classificacao = data.get("classificacao", {})
        tags = data.get("tags", [])
        
        # Texto a ser analisado (prioriza informações extraídas)
        texto_para_analise = ""
        
        # Se as infos extraídas já vierem em formato de texto, usa diretamente
        if isinstance(infos_extraidas, str):
            texto_para_analise = infos_extraidas
        # Se for um dicionário, combina os valores em um único texto
        elif isinstance(infos_extraidas, dict):
            for campo, valor in infos_extraidas.items():
                if isinstance(valor, str):
                    texto_para_analise += f"{campo}: {valor}\n"
                else:
                    texto_para_analise += f"{campo}: {str(valor)}\n"
        
        # Se não houver texto para analisar, usa o texto original
        if not texto_para_analise:
            texto_para_analise = texto_original
            
        # Verifica se tem texto para analisar
        if not texto_para_analise:
            raise ValueError("Não há texto para analisar")
            
        # Inicializa o dicionário de resultados
        resultado_analises = {}
        
        # 1. Busca conhecimento relevante no banco vetorial
        if self.usar_banco_vetorial:
            docs_similares = self._buscar_conhecimento_relevante(texto_para_analise, tags)
            resultado_analises["documentos_relacionados"] = docs_similares
            
        # 2. Realiza as análises configuradas
        if "sentimento" in self.analises:
            resultado_analises["sentimento"] = self._analisar_sentimento(texto_para_analise)
            
        if "entidades" in self.analises:
            resultado_analises["entidades"] = self._extrair_entidades(texto_para_analise)
            
        if "insights" in self.analises:
            # Usa resultados de análises anteriores para gerar insights mais ricos
            analises_anteriores = {
                k: v for k, v in resultado_analises.items() 
                if k in ["sentimento", "entidades"]
            }
            resultado_analises["insights"] = self._gerar_insights(texto_para_analise, analises_anteriores)
            
        # Constrói o resultado final mantendo os dados anteriores
        resultado = data.copy()  # Mantém os dados dos agentes anteriores
        resultado["analises"] = resultado_analises
        
        return resultado
