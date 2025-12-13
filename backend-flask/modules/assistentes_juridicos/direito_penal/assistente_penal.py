"""
Assistente Especializado em Direito Penal
Integração com pgvector e APIs de IA
"""

from ..assistente_base import AssistenteJuridicoBase
from ..upload_handler import ProcessadorArquivos
import logging

logger = logging.getLogger(__name__)

class AssistenteDireitoPenal(AssistenteJuridicoBase):
    """
    Assistente especializado em Direito Penal
    """
    
    def __init__(self):
        super().__init__('direito_penal')
        self.processador_arquivos = ProcessadorArquivos()
        self._inicializar_base_conhecimento()
        
    def _inicializar_base_conhecimento(self):
        """Inicializa base de conhecimento específica do Direito Penal"""
        conhecimentos_base = [
            {
                'conteudo': """Código Penal Brasileiro - Artigos fundamentais sobre crimes contra a pessoa, patrimônio, 
                administração pública e outros. Inclui tipificação penal, penas e medidas de segurança.""",
                'referencia': 'Código Penal - Lei 2.848/1940',
                'metadata': {'tipo': 'legislacao', 'area': 'direito_penal'}
            },
            {
                'conteudo': """Código de Processo Penal - Procedimentos para investigação, processo e julgamento de crimes. 
                Inquérito policial, ação penal, provas, recursos e execução penal.""",
                'referencia': 'Código de Processo Penal - Decreto-Lei 3.689/1941',
                'metadata': {'tipo': 'legislacao', 'area': 'processo_penal'}
            },
            {
                'conteudo': """Lei de Execução Penal - Regras para cumprimento de penas privativas de liberdade, 
                restritivas de direitos e medidas de segurança. Progressão de regime, livramento condicional.""",
                'referencia': 'Lei de Execução Penal - Lei 7.210/1984',
                'metadata': {'tipo': 'legislacao', 'area': 'execucao_penal'}
            }
        ]
        
        # Verificar se já existem dados na base
        try:
            resultados_existentes = self.buscar_semantica("código penal", limite=1)
            if not resultados_existentes:
                for conhecimento in conhecimentos_base:
                    self.adicionar_documento(
                        conhecimento['conteudo'],
                        conhecimento['referencia'],
                        conhecimento['metadata']
                    )
                logger.info("Base de conhecimento do Direito Penal inicializada")
        except Exception as e:
            logger.error(f"Erro ao inicializar base de conhecimento: {e}")
    
    def analisar_caso_penal(self, descricao_caso: str, api: str = "openai", estilo: str = "juridico_tecnico") -> dict:
        """Analisa caso penal específico"""
        pergunta_estruturada = f"""
        Analise o seguinte caso penal e forneça:
        1. Possível tipificação penal
        2. Elementos do tipo penal
        3. Causas de aumento ou diminuição de pena
        4. Possíveis defesas
        5. Jurisprudência relevante
        
        Caso: {descricao_caso}
        """
        
        return self.processar_consulta_completa(
            pergunta_estruturada, 
            api_escolhida=api, 
            estilo=estilo
        )
    
    def gerar_peca_processual(self, tipo_peca: str, dados: dict, api: str = "openai") -> str:
        """Gera peça processual baseada em template"""
        templates_peca = {
            'denuncia': """
            Elabore uma denúncia criminal seguindo a estrutura:
            1. Qualificação do denunciado
            2. Exposição do fato criminoso
            3. Classificação legal
            4. Pedidos
            """,
            'defesa_previa': """
            Elabore defesa prévia seguindo:
            1. Preliminares
            2. Negativa de autoria/materialidade
            3. Excludentes de ilicitude
            4. Atenuantes
            5. Pedidos
            """,
            'alegacoes_finais': """
            Elabore alegações finais com:
            1. Resumo processual
            2. Análise das provas
            3. Teses defensivas
            4. Pedidos finais
            """
        }
        
        if tipo_peca not in templates_peca:
            return "Tipo de peça não reconhecido"
        
        prompt = f"{templates_peca[tipo_peca]}\n\nDados: {dados}"
        
        if api == "openai":
            return self.chat_openai(prompt, estilo="juridico_tecnico")
        elif api == "anthropic":
            return self.chat_anthropic(prompt, estilo="juridico_tecnico")
        elif api == "gemini":
            return self.chat_gemini(prompt, estilo="juridico_tecnico")
        
        return "API não disponível"
    
    def processar_upload_documento(self, arquivo_path: str, tipo_analise: str = "geral") -> dict:
        """Processa upload de documento jurídico"""
        try:
            texto_extraido = self.processador_arquivos.extrair_texto(arquivo_path)
            
            if tipo_analise == "tipificacao":
                pergunta = f"Analise este documento e identifique possíveis crimes e tipificações: {texto_extraido[:2000]}"
            elif tipo_analise == "defesa":
                pergunta = f"Analise este documento e sugira estratégias de defesa: {texto_extraido[:2000]}"
            else:
                pergunta = f"Faça análise jurídica geral deste documento: {texto_extraido[:2000]}"
            
            resultado = self.processar_consulta_completa(pergunta)
            resultado['texto_extraido'] = texto_extraido
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar upload: {e}")
            return {'erro': str(e)}