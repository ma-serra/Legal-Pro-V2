import logging
from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider

logger = logging.getLogger(__name__)

class ClassificadorAgent(BaseAgent):
    """
    Agente responsável por classificar dados em categorias pré-definidas.
    
    Este agente recebe informações estruturadas do ExtratorAgent e as classifica
    conforme as categorias e regras definidas na configuração.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Configurações específicas de classificação
        self.categorias = self.config.get("categorias", [])
        self.multi_rotulo = self.config.get("multi_rotulo", False)
        self.limite_confianca = self.config.get("limite_confianca", 0.7)
        
        # Se não houver categorias definidas, usa algumas padrão
        if not self.categorias:
            self.categorias = ["Informativo", "Pergunta", "Solicitação", "Problema", "Outro"]
            
        self.logger.info(f"ClassificadorAgent inicializado com {len(self.categorias)} categorias")
        
    def should_run(self, data):
        """
        Determina se o classificador deve ser executado.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            bool: True se o classificador deve ser executado
        """
        # Verifica se há texto ou informações extraídas para classificar
        if not data:
            return False
            
        # Obtém dados extraídos do agente anterior
        infos_extraidas = data.get("informacoes_extraidas")
        if not infos_extraidas:
            return False
            
        return True
    
    def _processar(self, data):
        """
        Processa os dados para classificação.
        
        Args:
            data: Dados recebidos do agente anterior (ExtratorAgent)
            
        Returns:
            Dicionário com as classificações geradas
        """
        # Obtém os dados extraídos do agente anterior
        infos_extraidas = data.get("informacoes_extraidas", {})
        texto_original = data.get("texto_original", "")
        
        # Texto a ser classificado (combina as informações extraídas)
        texto_para_classificar = ""
        
        # Se as infos extraídas já vierem em formato de texto, usa diretamente
        if isinstance(infos_extraidas, str):
            texto_para_classificar = infos_extraidas
        # Se for um dicionário, combina os valores em um único texto
        elif isinstance(infos_extraidas, dict):
            for campo, valor in infos_extraidas.items():
                if isinstance(valor, str):
                    texto_para_classificar += f"{campo}: {valor}\n"
                else:
                    texto_para_classificar += f"{campo}: {str(valor)}\n"
        
        # Se não houver texto para classificar, usa o texto original
        if not texto_para_classificar:
            texto_para_classificar = texto_original
            
        # Verifica se tem texto para classificar
        if not texto_para_classificar:
            raise ValueError("Não há texto para classificar")
            
        # Realiza a classificação usando o LLM
        try:
            # Usa o método específico de classificação do LLMProvider
            classificacao = self.llm.classificar(
                texto=texto_para_classificar,
                categorias=self.categorias,
                instrucoes="""
                Analise o texto e atribua um score de confiança para cada categoria.
                Considere o contexto completo e não apenas palavras-chave.
                """
            )
            
            # Filtra as categorias com base no limite de confiança
            categorias_acima_limite = {}
            for categoria, score in classificacao.items():
                if score >= self.limite_confianca:
                    categorias_acima_limite[categoria] = score
                    
            # Se não for multi-rótulo, mantém apenas a categoria com maior score
            if not self.multi_rotulo and categorias_acima_limite:
                max_categoria = max(categorias_acima_limite.items(), key=lambda x: x[1])
                categorias_acima_limite = {max_categoria[0]: max_categoria[1]}
                
            # Se nenhuma categoria atingiu o limite, usa a com maior score
            if not categorias_acima_limite and classificacao:
                max_categoria = max(classificacao.items(), key=lambda x: x[1])
                categorias_acima_limite = {max_categoria[0]: max_categoria[1]}
                
            # Constrói o resultado final
            resultado = data.copy()  # Mantém os dados do agente anterior
            resultado["classificacao"] = {
                "categorias": categorias_acima_limite,
                "todas_pontuacoes": classificacao,
                "multi_rotulo": self.multi_rotulo,
                "limite_confianca": self.limite_confianca
            }
            
            # Para facilitar o acesso direto, adiciona as categorias como tags
            resultado["tags"] = list(categorias_acima_limite.keys())
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na classificação: {str(e)}")
            raise
