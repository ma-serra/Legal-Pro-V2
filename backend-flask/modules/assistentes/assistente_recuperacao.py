"""
Assistente Especializado em Recuperação de Crédito
Integrado com base vetorial para consultas fundamentadas
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from .assistente_base import AssistenteBase

logger = logging.getLogger(__name__)


    def processar_consulta_completa(self, pergunta: str, api_escolhida: str = "openai", 
                                  estilo: str = "juridico_tecnico", 
                                  usar_base_vetorial: bool = True):
        """Processa consulta completa usando assistente base"""
        try:
            # Usar o método da classe base
            return super().processar_consulta_completa(pergunta, api_escolhida, estilo, usar_base_vetorial)
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            return {
                'resposta': f"Erro ao processar consulta: {str(e)}",
                'contexto_usado': False,
                'resultados_busca': [],
                'api_utilizada': api_escolhida,
                'status': 'erro'
            }

class AssistenteRecuperacao(AssistenteBase):
    """Assistente especializado em Recuperação de Crédito"""
    
    def __init__(self):
        super().__init__("recuperacao_credito")
        self.area = "recuperacao_credito"
        self.nome = "Assistente de Recuperação de Crédito"
        self.descricao = "Especialista em cobrança, execução e negociação de dívidas"
        self.cor_destaque = "#20c997"
        self.icone = "fas fa-money-bill-wave"
        
        # Configurações específicas da área
        self.base_vetorial = "embeddings_recuperacao_credito"
        self.categoria_juridica = "Recuperação de Crédito"
        
        # IDs dos agentes especializados (conforme banco de dados)
        self.agentes_especializados = [2, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209]
        
        logger.info(f"✅ {self.nome} inicializado com sucesso")
    
    def get_prompt_especializado(self, estilo: str = "juridico_tecnico") -> str:
        """Retorna prompt especializado para recuperação de crédito"""
        prompts = {
            "juridico_tecnico": """
            Você é um especialista em Recuperação de Crédito com profundo conhecimento em:
            
            ÁREAS DE ESPECIALIZAÇÃO:
            • Cobrança extrajudicial e judicial
            • Execução de títulos executivos
            • Negociação de dívidas e acordos
            • Protestos de títulos
            • Recuperação de crédito empresarial
            • Direito falimentar e recuperação judicial
            • Garantias reais e pessoais
            • Prescrição e decadência de créditos
            
            LEGISLAÇÃO APLICÁVEL:
            • Código Civil (arts. 389-420 - Inadimplemento das obrigações)
            • Código de Processo Civil (Livro II - Processo de Execução)
            • Lei de Falências (Lei 11.101/2005)
            • Lei de Protestos (Lei 9.492/1997)
            • CDC (proteção ao consumidor)
            
            INSTRUÇÕES:
            • Forneça respostas técnicas e fundamentadas juridicamente
            • Cite sempre os artigos de lei aplicáveis
            • Considere aspectos práticos da cobrança
            • Avalie riscos e benefícios de cada estratégia
            • Sugira alternativas de recuperação quando aplicável
            """,
            
            "consultoria_empresarial": """
            Como consultor em recuperação de crédito, foque em:
            • Estratégias de cobrança eficientes
            • Análise de risco de inadimplência
            • Estruturação de garantias
            • Políticas de crédito e cobrança
            • Gestão de carteira de recebíveis
            • Aspectos tributários da recuperação
            """,
            
            "orientacao_pratica": """
            Forneça orientações práticas sobre:
            • Procedimentos de cobrança
            • Documentação necessária
            • Prazos e procedimentos
            • Custos e benefícios
            • Alternativas extrajudiciais
            • Mediação e conciliação
            """
        }
        
        return prompts.get(estilo, prompts["juridico_tecnico"])
    
    def get_contexto_especializado(self) -> Dict[str, Any]:
        """Retorna contexto específico para recuperação de crédito"""
        return {
            "area": self.area,
            "especialidades": [
                "Cobrança Extrajudicial",
                "Execução Judicial",
                "Negociação de Dívidas",
                "Protestos",
                "Direito Falimentar",
                "Garantias",
                "Prescrição e Decadência",
                "Recuperação Empresarial"
            ],
            "legislacao_principal": [
                "Código Civil - Inadimplemento",
                "Código de Processo Civil - Execução",
                "Lei de Falências",
                "Lei de Protestos",
                "CDC"
            ],
            "procedimentos_comuns": [
                "Notificação extrajudicial",
                "Protesto de títulos",
                "Ação de execução",
                "Penhora de bens",
                "Acordo judicial",
                "Recuperação judicial"
            ]
        }
    
    def processar_consulta_especializada(self, pergunta: str, contexto: str = "", 
                                       api: str = "openai") -> Dict[str, Any]:
        """Processa consulta específica de recuperação de crédito"""
        try:
            # Adicionar contexto específico da área
            contexto_completo = f"""
            CONTEXTO: Consulta sobre Recuperação de Crédito
            
            ESPECIALIZAÇÃO: {self.get_contexto_especializado()}
            
            CONTEXTO ADICIONAL: {contexto}
            
            PERGUNTA: {pergunta}
            """
            
            # Processar com a base da classe pai
            resultado = super().processar_consulta_completa(
                pergunta=contexto_completo,
                api_escolhida=api,
                usar_base_vetorial=True
            )
            
            # Enriquecer resposta com informações específicas
            if resultado.get('sucesso'):
                resultado['area_especializada'] = self.area
                resultado['legislacao_aplicavel'] = self._extrair_legislacao_aplicavel(resultado.get('resposta', ''))
                resultado['proximos_passos'] = self._sugerir_proximos_passos(pergunta)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta de recuperação de crédito: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro no processamento: {str(e)}',
                'area': self.area
            }
    
    def _extrair_legislacao_aplicavel(self, resposta: str) -> List[str]:
        """Extrai referências legais da resposta"""
        legislacao = []
        
        # Padrões comuns em recuperação de crédito
        if "código civil" in resposta.lower():
            legislacao.append("Código Civil")
        if "código de processo civil" in resposta.lower() or "cpc" in resposta.lower():
            legislacao.append("Código de Processo Civil")
        if "lei de falências" in resposta.lower() or "11.101" in resposta:
            legislacao.append("Lei de Falências (11.101/2005)")
        if "lei de protestos" in resposta.lower() or "9.492" in resposta:
            legislacao.append("Lei de Protestos (9.492/1997)")
        if "cdc" in resposta.lower() or "código de defesa do consumidor" in resposta.lower():
            legislacao.append("Código de Defesa do Consumidor")
        
        return legislacao
    
    def _sugerir_proximos_passos(self, pergunta: str) -> List[str]:
        """Sugere próximos passos baseados na consulta"""
        passos = []
        pergunta_lower = pergunta.lower()
        
        if "cobrança" in pergunta_lower:
            passos.extend([
                "Verificar documentação do crédito",
                "Analisar prazo prescricional",
                "Considerar notificação extrajudicial"
            ])
        
        if "execução" in pergunta_lower:
            passos.extend([
                "Verificar título executivo",
                "Localizar bens do devedor",
                "Avaliar viabilidade da execução"
            ])
        
        if "acordo" in pergunta_lower or "negociação" in pergunta_lower:
            passos.extend([
                "Avaliar capacidade de pagamento",
                "Propor condições viáveis",
                "Formalizar acordo juridicamente"
            ])
        
        if "protesto" in pergunta_lower:
            passos.extend([
                "Verificar requisitos do título",
                "Calcular custos do protesto",
                "Avaliar efetividade da medida"
            ])
        
        return passos[:5]  # Limitar a 5 passos
    
    def analisar_documento_credito(self, texto_documento: str) -> Dict[str, Any]:
        """Analisa documento relacionado a crédito"""
        try:
            prompt_analise = f"""
            Analise o seguinte documento sob a perspectiva da recuperação de crédito:
            
            {texto_documento}
            
            Forneça:
            1. Tipo de documento identificado
            2. Valor do crédito (se identificável)
            3. Prazo de vencimento
            4. Garantias existentes
            5. Viabilidade de execução
            6. Estratégia de cobrança recomendada
            7. Aspectos legais relevantes
            """
            
            resultado = self.processar_consulta_especializada(
                pergunta=prompt_analise,
                api="openai"
            )
            
            if resultado.get('sucesso'):
                return {
                    'sucesso': True,
                    'analise': resultado['resposta'],
                    'tipo': 'analise_documento_credito',
                    'area': self.area
                }
            else:
                return resultado
                
        except Exception as e:
            logger.error(f"Erro ao analisar documento de crédito: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro na análise: {str(e)}',
                'area': self.area
            }
    
    def get_modelos_documentos(self) -> List[Dict[str, str]]:
        """Retorna modelos de documentos para recuperação de crédito"""
        return [
            {
                'nome': 'Notificação Extrajudicial',
                'descricao': 'Modelo de notificação para cobrança amigável',
                'tipo': 'notificacao'
            },
            {
                'nome': 'Carta de Cobrança',
                'descricao': 'Modelo de carta para cobrança de dívida',
                'tipo': 'carta_cobranca'
            },
            {
                'nome': 'Acordo de Parcelamento',
                'descricao': 'Modelo de acordo para parcelamento de dívida',
                'tipo': 'acordo'
            },
            {
                'nome': 'Petição de Execução',
                'descricao': 'Modelo de petição inicial de execução',
                'tipo': 'peticao_execucao'
            },
            {
                'nome': 'Termo de Confissão de Dívida',
                'descricao': 'Modelo de confissão de dívida',
                'tipo': 'confissao_divida'
            }
        ]
    
    def calcular_custos_recuperacao(self, valor_credito: float, tipo_procedimento: str) -> Dict[str, Any]:
        """Calcula custos estimados de recuperação"""
        try:
            custos = {
                'valor_credito': valor_credito,
                'procedimento': tipo_procedimento,
                'custos_estimados': {}
            }
            
            if tipo_procedimento == "extrajudicial":
                custos['custos_estimados'] = {
                    'notificacao': valor_credito * 0.01,  # 1%
                    'protesto': 50.0,  # Valor fixo estimado
                    'honorarios': valor_credito * 0.05,  # 5%
                    'total_estimado': valor_credito * 0.06 + 50.0
                }
            
            elif tipo_procedimento == "judicial":
                custos['custos_estimados'] = {
                    'custas_iniciais': valor_credito * 0.01,
                    'honorarios_advocaticios': valor_credito * 0.10,
                    'custas_execucao': valor_credito * 0.005,
                    'total_estimado': valor_credito * 0.115
                }
            
            custos['viabilidade'] = "VIÁVEL" if custos['custos_estimados']['total_estimado'] < valor_credito * 0.3 else "ANÁLISE NECESSÁRIA"
            
            return {
                'sucesso': True,
                'calculo': custos,
                'area': self.area
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular custos de recuperação: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro no cálculo: {str(e)}',
                'area': self.area
            }