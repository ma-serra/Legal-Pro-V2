"""
Assistente Especializado em Análise de Riscos Jurídicos
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

class AssistenteAnaliseRiscos(AssistenteBase):
    """Assistente especializado em Análise de Riscos Jurídicos"""
    
    def __init__(self):
        super().__init__("analise_riscos")
        self.area = "analise_riscos"
        self.nome = "Assistente de Análise de Riscos Jurídicos"
        self.descricao = "Especialista em identificação, avaliação e mitigação de riscos jurídicos empresariais"
        self.cor_destaque = "#dc3545"
        self.icone = "fas fa-chart-line"
        
        # Configurações específicas da área
        self.base_vetorial = "embeddings_analise_riscos"
        self.categoria_juridica = "Análise de Riscos Jurídicos"
        
        # IDs dos agentes especializados (conforme banco de dados)
        self.agentes_especializados = [9, 193, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323]
        
        logger.info(f"✅ {self.nome} inicializado com sucesso")
    
    def get_prompt_especializado(self, estilo: str = "juridico_tecnico") -> str:
        """Retorna prompt especializado para análise de riscos jurídicos"""
        prompts = {
            "juridico_tecnico": """
            Você é um especialista em Análise de Riscos Jurídicos com profundo conhecimento em:
            
            ÁREAS DE ESPECIALIZAÇÃO:
            • Identificação e mapeamento de riscos jurídicos
            • Avaliação de probabilidade e impacto de riscos
            • Mitigação e controle de riscos legais
            • Compliance e conformidade regulatória
            • Riscos contratuais e operacionais
            • Análise de passivos jurídicos
            • Due diligence legal em M&A
            • Gestão de riscos empresariais
            
            TIPOS DE RISCOS ANALISADOS:
            • Riscos contratuais e obrigacionais
            • Riscos trabalhistas e previdenciários
            • Riscos tributários e fiscais
            • Riscos regulatórios e de compliance
            • Riscos societários e de governança
            • Riscos ambientais e de sustentabilidade
            • Riscos de propriedade intelectual
            • Riscos em fusões e aquisições
            
            METODOLOGIAS:
            • Matriz de riscos (probabilidade x impacto)
            • Análise SWOT jurídica
            • Due diligence legal
            • Mapeamento de processos de risco
            • Indicadores de risco (KRIs)
            • Cenários de stress test legal
            
            INSTRUÇÕES:
            • Forneça análises estruturadas e quantificadas quando possível
            • Identifique riscos críticos, altos, médios e baixos
            • Sugira medidas de mitigação específicas e práticas
            • Considere impactos financeiros e reputacionais
            • Referencie marcos regulatórios relevantes
            """,
            
            "consultoria_empresarial": """
            Como consultor em riscos jurídicos empresariais, foque em:
            • Análise de exposição legal da empresa
            • Mapeamento de vulnerabilidades jurídicas
            • Estratégias de prevenção e mitigação
            • Políticas de gestão de riscos
            • Compliance e programas de integridade
            • Métricas e indicadores de risco
            """,
            
            "due_diligence": """
            Para análises de due diligence, concentre-se em:
            • Identificação de passivos jurídicos
            • Avaliação de contingências legais
            • Análise de contratos e obrigações
            • Verificação de compliance regulatório
            • Mapeamento de riscos ocultos
            • Recomendações para estruturação de negócios
            """
        }
        
        return prompts.get(estilo, prompts["juridico_tecnico"])
    
    def get_contexto_especializado(self) -> Dict[str, Any]:
        """Retorna contexto específico para análise de riscos jurídicos"""
        return {
            "area": self.area,
            "categorias_risco": [
                "Riscos Contratuais",
                "Riscos Trabalhistas", 
                "Riscos Tributários",
                "Riscos Regulatórios",
                "Riscos Societários",
                "Riscos Ambientais",
                "Riscos de PI",
                "Riscos em M&A"
            ],
            "metodologias": [
                "Matriz de Riscos",
                "Análise SWOT Jurídica",
                "Due Diligence Legal",
                "Mapeamento de Processos",
                "KRIs (Key Risk Indicators)",
                "Stress Test Legal"
            ],
            "niveis_risco": [
                "Crítico (Impacto Alto + Probabilidade Alta)",
                "Alto (Impacto Alto + Probabilidade Média)",
                "Médio (Impacto Médio + Probabilidade Média)",
                "Baixo (Impacto Baixo + Probabilidade Baixa)"
            ],
            "frameworks": [
                "ISO 31000 (Gestão de Riscos)",
                "COSO ERM (Enterprise Risk Management)", 
                "Lei Sarbanes-Oxley",
                "Lei Anticorrupção (12.846/2013)",
                "Marco Civil da Internet"
            ]
        }
    
    def processar_consulta_especializada(self, pergunta: str, contexto: str = "", 
                                       api: str = "openai") -> Dict[str, Any]:
        """Processa consulta específica de análise de riscos jurídicos"""
        try:
            # Adicionar contexto específico da área
            contexto_completo = f"""
            CONTEXTO: Consulta sobre Análise de Riscos Jurídicos
            
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
            
            # Enriquecer resposta com análise de riscos estruturada
            if resultado.get('sucesso'):
                resultado['area_especializada'] = self.area
                resultado['categorias_risco'] = self._identificar_categorias_risco(pergunta)
                resultado['nivel_risco'] = self._avaliar_nivel_risco(resultado.get('resposta', ''))
                resultado['medidas_mitigacao'] = self._sugerir_mitigacao(pergunta)
                resultado['indicadores_monitoramento'] = self._definir_indicadores(pergunta)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta de análise de riscos: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro no processamento: {str(e)}',
                'area': self.area
            }
    
    def _identificar_categorias_risco(self, pergunta: str) -> List[str]:
        """Identifica categorias de risco baseadas na consulta"""
        categorias = []
        pergunta_lower = pergunta.lower()
        
        mapeamento_categorias = {
            "contrato": "Riscos Contratuais",
            "trabalhista": "Riscos Trabalhistas",
            "tributário": "Riscos Tributários",
            "regulatório": "Riscos Regulatórios",
            "societário": "Riscos Societários", 
            "ambiental": "Riscos Ambientais",
            "propriedade intelectual": "Riscos de Propriedade Intelectual",
            "fusão": "Riscos em M&A",
            "aquisição": "Riscos em M&A",
            "compliance": "Riscos de Compliance"
        }
        
        for termo, categoria in mapeamento_categorias.items():
            if termo in pergunta_lower:
                categorias.append(categoria)
        
        return list(set(categorias)) if categorias else ["Análise Geral de Riscos"]
    
    def _avaliar_nivel_risco(self, resposta: str) -> str:
        """Avalia nível de risco baseado na resposta"""
        resposta_lower = resposta.lower()
        
        # Indicadores de risco crítico
        indicadores_criticos = ["multa", "sanção", "penalidade", "responsabilização", "crime"]
        if any(termo in resposta_lower for termo in indicadores_criticos):
            return "CRÍTICO"
        
        # Indicadores de risco alto
        indicadores_altos = ["violação", "descumprimento", "irregularidade", "passivo"]
        if any(termo in resposta_lower for termo in indicadores_altos):
            return "ALTO"
        
        # Indicadores de risco médio
        indicadores_medios = ["adequação", "conformidade", "revisão", "ajuste"]
        if any(termo in resposta_lower for termo in indicadores_medios):
            return "MÉDIO"
        
        return "A AVALIAR"
    
    def _sugerir_mitigacao(self, pergunta: str) -> List[str]:
        """Sugere medidas de mitigação baseadas na consulta"""
        medidas = []
        pergunta_lower = pergunta.lower()
        
        if "contrato" in pergunta_lower:
            medidas.extend([
                "Revisar cláusulas contratuais críticas",
                "Implementar controles de gestão contratual",
                "Estabelecer processo de due diligence de contrapartes"
            ])
        
        if "trabalhista" in pergunta_lower:
            medidas.extend([
                "Auditar práticas trabalhistas",
                "Implementar programa de compliance trabalhista",
                "Treinar gestores em legislação trabalhista"
            ])
        
        if "tributário" in pergunta_lower:
            medidas.extend([
                "Implementar controles fiscais robustos",
                "Estabelecer processo de monitoramento tributário",
                "Buscar orientação especializada em planejamento fiscal"
            ])
        
        if "compliance" in pergunta_lower:
            medidas.extend([
                "Desenvolver programa de integridade",
                "Implementar canal de denúncias",
                "Estabelecer treinamentos periódicos"
            ])
        
        return medidas[:5]  # Limitar a 5 medidas
    
    def _definir_indicadores(self, pergunta: str) -> List[str]:
        """Define indicadores de monitoramento de risco"""
        indicadores = []
        pergunta_lower = pergunta.lower()
        
        indicadores_base = [
            "Número de não-conformidades identificadas",
            "Tempo médio de resolução de questões legais",
            "Valor de contingências jurídicas",
            "Taxa de compliance em auditorias"
        ]
        
        if "contrato" in pergunta_lower:
            indicadores.append("Percentual de contratos revisados no prazo")
        
        if "trabalhista" in pergunta_lower:
            indicadores.append("Número de ações trabalhistas")
        
        if "tributário" in pergunta_lower:
            indicadores.append("Percentual de conformidade tributária")
        
        return indicadores_base + indicadores[:3]
    
    def realizar_matriz_riscos(self, riscos_identificados: List[Dict]) -> Dict[str, Any]:
        """Cria matriz de riscos estruturada"""
        try:
            matriz = {
                'criticos': [],
                'altos': [],
                'medios': [],
                'baixos': [],
                'metodologia': 'Matriz Probabilidade x Impacto'
            }
            
            for risco in riscos_identificados:
                probabilidade = risco.get('probabilidade', 'media')
                impacto = risco.get('impacto', 'medio')
                
                # Lógica de classificação
                if probabilidade == 'alta' and impacto == 'alto':
                    matriz['criticos'].append(risco)
                elif (probabilidade == 'alta' and impacto == 'medio') or (probabilidade == 'media' and impacto == 'alto'):
                    matriz['altos'].append(risco)
                elif probabilidade == 'media' and impacto == 'medio':
                    matriz['medios'].append(risco)
                else:
                    matriz['baixos'].append(risco)
            
            return {
                'sucesso': True,
                'matriz_riscos': matriz,
                'resumo': {
                    'total_riscos': len(riscos_identificados),
                    'criticos': len(matriz['criticos']),
                    'altos': len(matriz['altos']),
                    'medios': len(matriz['medios']),
                    'baixos': len(matriz['baixos'])
                },
                'area': self.area
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar matriz de riscos: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro na análise: {str(e)}',
                'area': self.area
            }
    
    def analisar_documento_riscos(self, texto_documento: str, tipo_analise: str = "geral") -> Dict[str, Any]:
        """Analisa documento sob perspectiva de riscos jurídicos"""
        try:
            prompt_analise = f"""
            Analise o seguinte documento identificando riscos jurídicos:
            
            {texto_documento}
            
            Forneça análise estruturada com:
            1. Riscos identificados (classificados por categoria)
            2. Nível de cada risco (crítico/alto/médio/baixo)
            3. Impacto potencial (financeiro, reputacional, operacional)
            4. Probabilidade de ocorrência
            5. Medidas de mitigação recomendadas
            6. Indicadores de monitoramento
            7. Marcos regulatórios aplicáveis
            
            Tipo de análise: {tipo_analise}
            """
            
            resultado = self.processar_consulta_especializada(
                pergunta=prompt_analise,
                api="openai"
            )
            
            if resultado.get('sucesso'):
                return {
                    'sucesso': True,
                    'analise_riscos': resultado['resposta'],
                    'tipo_analise': tipo_analise,
                    'categorias_identificadas': resultado.get('categorias_risco', []),
                    'nivel_geral': resultado.get('nivel_risco', 'A AVALIAR'),
                    'area': self.area
                }
            else:
                return resultado
                
        except Exception as e:
            logger.error(f"Erro ao analisar documento de riscos: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro na análise: {str(e)}',
                'area': self.area
            }
    
    def get_modelos_analise(self) -> List[Dict[str, str]]:
        """Retorna modelos de análise de riscos"""
        return [
            {
                'nome': 'Matriz de Riscos Corporativos',
                'descricao': 'Modelo de matriz probabilidade x impacto',
                'tipo': 'matriz_riscos'
            },
            {
                'nome': 'Checklist de Due Diligence Legal',
                'descricao': 'Lista de verificação para análise legal',
                'tipo': 'due_diligence'
            },
            {
                'nome': 'Relatório de Análise de Riscos',
                'descricao': 'Modelo de relatório estruturado',
                'tipo': 'relatorio_riscos'
            },
            {
                'nome': 'Plano de Mitigação de Riscos',
                'descricao': 'Template para planos de ação',
                'tipo': 'plano_mitigacao'
            },
            {
                'nome': 'Dashboard de Indicadores de Risco',
                'descricao': 'Painel de controle de KRIs',
                'tipo': 'dashboard_kri'
            }
        ]
    
    def calcular_score_risco(self, fatores_risco: Dict[str, int]) -> Dict[str, Any]:
        """Calcula score quantitativo de risco"""
        try:
            # Pesos para diferentes categorias de risco
            pesos = {
                'contratual': 0.20,
                'trabalhista': 0.15,
                'tributario': 0.20,
                'regulatorio': 0.15,
                'societario': 0.10,
                'ambiental': 0.10,
                'reputacional': 0.10
            }
            
            score_total = 0
            detalhes = {}
            
            for categoria, valor in fatores_risco.items():
                peso = pesos.get(categoria, 0.05)
                score_ponderado = valor * peso
                score_total += score_ponderado
                
                detalhes[categoria] = {
                    'valor_bruto': valor,
                    'peso': peso,
                    'score_ponderado': score_ponderado
                }
            
            # Classificação do score
            if score_total >= 80:
                classificacao = "RISCO CRÍTICO"
                cor = "#dc3545"
            elif score_total >= 60:
                classificacao = "RISCO ALTO" 
                cor = "#fd7e14"
            elif score_total >= 40:
                classificacao = "RISCO MÉDIO"
                cor = "#ffc107"
            else:
                classificacao = "RISCO BAIXO"
                cor = "#20c997"
            
            return {
                'sucesso': True,
                'score_total': round(score_total, 2),
                'classificacao': classificacao,
                'cor_indicador': cor,
                'detalhes_calculo': detalhes,
                'recomendacao': self._gerar_recomendacao_score(score_total),
                'area': self.area
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de risco: {e}")
            return {
                'sucesso': False,
                'erro': f'Erro no cálculo: {str(e)}',
                'area': self.area
            }
    
    def _gerar_recomendacao_score(self, score: float) -> str:
        """Gera recomendação baseada no score de risco"""
        if score >= 80:
            return "Ação imediata necessária. Implementar plano de contingência e medidas de mitigação urgentes."
        elif score >= 60:
            return "Monitoramento intensivo e implementação de controles adicionais recomendados."
        elif score >= 40:
            return "Manter monitoramento regular e considerar melhorias nos controles existentes."
        else:
            return "Manter controles atuais e monitoramento periódico."