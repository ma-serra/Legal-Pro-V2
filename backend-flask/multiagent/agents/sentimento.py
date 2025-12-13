from multiagent.core.base_agent import BaseAgent
from multiagent.utils.llm import LLMProvider
import json

class SentimentoAgent(BaseAgent):
    """
    Agente para análise de sentimento em textos.
    
    Este agente utiliza LLMs para identificar a carga emocional 
    predominante em um texto, classificando-o em positivo, negativo ou neutro,
    além de identificar emoções específicas expressas no conteúdo.
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configura o provedor LLM
        provider = self.config.get("llm_provider", "openai")
        modelo = self.config.get("llm_model", None)
        
        self.llm = LLMProvider(provider=provider, model=modelo)
        
        # Configurações da análise
        self.detalhar_emocoes = self.config.get("detalhar_emocoes", True)
        self.analisar_frases = self.config.get("analisar_frases", False)
        self.escala = self.config.get("escala", "padrao")  # padrao, intensidade, estrelas
        self.explicar = self.config.get("explicar", True)
        
    def _gerar_prompt_sentimento(self, texto):
        """
        Gera o prompt para análise de sentimento baseado nas configurações.
        
        Args:
            texto: Texto a ser analisado
            
        Returns:
            String contendo o prompt para a API
        """
        prompt = f"""
        Analise o sentimento do seguinte texto, identificando se é predominantemente positivo, negativo ou neutro.
        
        Texto para análise:
        "{texto}"
        
        """
        
        # Adiciona instruções para escala específica
        if self.escala == "intensidade":
            prompt += """
            Classifique a intensidade do sentimento em uma escala de -5 a +5, onde:
            -5 = extremamente negativo
            0 = neutro
            +5 = extremamente positivo
            """
        elif self.escala == "estrelas":
            prompt += """
            Classifique o sentimento em uma escala de 1 a 5 estrelas, onde:
            1 = muito negativo
            3 = neutro
            5 = muito positivo
            """
            
        # Adiciona instruções para detalhamento de emoções
        if self.detalhar_emocoes:
            prompt += """
            Identifique as principais emoções presentes no texto (por exemplo: alegria, tristeza, raiva, medo, surpresa, etc.)
            e atribua um nível de confiança para cada uma (percentual de 0 a 100%).
            """
            
        # Adiciona instruções para análise por frases
        if self.analisar_frases:
            prompt += """
            Divida o texto em frases e analise o sentimento de cada uma separadamente.
            """
            
        # Adiciona instruções para explicação
        if self.explicar:
            prompt += """
            Explique brevemente as razões para sua classificação de sentimento, citando palavras
            ou expressões chave que influenciaram sua análise.
            """
            
        # Adiciona instruções para formato da resposta
        prompt += """
        Responda em formato JSON estruturado com os seguintes campos:
        {
            "sentimento_geral": "positivo|negativo|neutro",
            "pontuacao": número (conforme a escala solicitada),
            "emocoes": [{"emocao": "nome da emoção", "confianca": percentual}, ...],
            "analise_frases": [{"frase": "texto da frase", "sentimento": "classificação", "pontuacao": número}, ...],
            "explicacao": "explicação para a classificação",
            "palavras_chave": ["palavra1", "palavra2", ...]
        }
        
        Inclua apenas os campos solicitados nas instruções acima.
        """
        
        return prompt
    
    def _formatar_resultado(self, resultado_api, texto_original):
        """
        Formata o resultado bruto da API para um formato consistente.
        
        Args:
            resultado_api: Resposta da API
            texto_original: Texto analisado
            
        Returns:
            Dicionário formatado com os resultados da análise
        """
        try:
            # Tenta parsear a resposta como JSON
            if isinstance(resultado_api, str):
                # Identifica e extrai apenas a parte JSON da resposta
                json_inicio = resultado_api.find('{')
                json_fim = resultado_api.rfind('}') + 1
                
                if json_inicio >= 0 and json_fim > json_inicio:
                    json_str = resultado_api[json_inicio:json_fim]
                    resultado = json.loads(json_str)
                else:
                    # Fallback para resposta em texto
                    resultado = {
                        "sentimento_geral": "não identificado",
                        "explicacao": resultado_api
                    }
            else:
                resultado = resultado_api
                
            # Adiciona campos padrão se não existirem
            defaults = {
                "sentimento_geral": "neutro",
                "pontuacao": 0,
                "emocoes": [],
                "analise_frases": [],
                "explicacao": "",
                "palavras_chave": []
            }
            
            for key, default_value in defaults.items():
                if key not in resultado:
                    resultado[key] = default_value
                    
            # Adiciona metadados
            resultado["texto_analisado"] = texto_original[:200] + "..." if len(texto_original) > 200 else texto_original
            resultado["configuracao"] = {
                "escala": self.escala,
                "detalhar_emocoes": self.detalhar_emocoes,
                "analisar_frases": self.analisar_frases
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar resultado: {str(e)}")
            # Retorna um resultado básico em caso de erro
            return {
                "sentimento_geral": "erro",
                "explicacao": f"Erro ao processar resultado: {str(e)}",
                "resultado_bruto": resultado_api
            }
    
    def _processar(self, data):
        """
        Processa o texto para análise de sentimento.
        
        Args:
            data: Dados recebidos do agente anterior
            
        Returns:
            Dicionário com os resultados da análise de sentimento
        """
        # Obtém o texto a ser analisado
        texto = data.get("texto") or data.get("conteudo")
        
        # Tenta outras chaves comuns
        if not texto:
            if "traducao" in data and "texto_traduzido" in data["traducao"]:
                texto = data["traducao"]["texto_traduzido"]
            elif "resumo" in data and "conteudo" in data["resumo"]:
                texto = data["resumo"]["conteudo"]
            
        if not texto:
            raise ValueError("Não há texto para analisar o sentimento")
            
        # Gera o prompt para análise
        prompt = self._gerar_prompt_sentimento(texto)
        
        # Configuração para resposta em formato JSON
        try:
            # Adiciona a instrução para formato de resposta JSON na API do OpenAI
            # que não fica bem no prompt por questões de formato
            options = {}
            if self.llm.provider == "openai":
                options["response_format"] = {"type": "json_object"}
                
            # Realiza a análise
            self.logger.info(f"Analisando sentimento de texto com {len(texto)} caracteres")
            
            resultado_api = self.llm.gerar_texto(
                prompt=prompt,
                temperatura=0.2,  # Baixa temperatura para análises mais consistentes
                **options
            )
            
            # Formata o resultado
            resultado = self._formatar_resultado(resultado_api, texto)
            
            # Constrói o resultado final
            resultado_final = data.copy()  # Mantém os dados originais
            resultado_final["analise_sentimento"] = resultado
            
            return resultado_final
            
        except Exception as e:
            self.logger.error(f"Erro na análise de sentimento: {str(e)}")
            raise