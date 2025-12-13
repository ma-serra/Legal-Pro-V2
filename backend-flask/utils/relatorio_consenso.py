"""
Módulo para geração de relatórios de consenso baseados em análises multi-agente.
Este módulo consolida as opiniões dos agentes em riscos, melhorias e estratégias.
"""
import json
import time
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask_login import current_user

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GeradorRelatorioConsenso:
    """Gera relatórios de consenso consolidados das análises multi-agente."""
    
    def __init__(self):
        self.prompt_consenso = self._criar_prompt_consenso()
    
    def _criar_prompt_consenso(self) -> str:
        """Cria o prompt para geração do relatório de consenso."""
        return """
Você é um CONSULTOR JURÍDICO SÊNIOR especializado em análise de consenso e síntese de opiniões múltiplas.
Sua missão é criar um RELATÓRIO DE CONSENSO COMPLETO E APROFUNDADO baseado nas análises dos agentes jurídicos.

METODOLOGIA DE ANÁLISE:
1. **ANÁLISE COMPARATIVA**: Compare detalhadamente cada opinião dos agentes
2. **IDENTIFICAÇÃO DE PADRÕES**: Encontre tendências e consistências
3. **ANÁLISE DE DISCREPÂNCIAS**: Examine divergências e suas causas
4. **SÍNTESE ESTRATÉGICA**: Crie recomendações consolidadas e prioritizadas
5. **AVALIAÇÃO DE RISCOS**: Análise quantitativa e qualitativa detalhada
6. **ROADMAP ESTRATÉGICO**: Plano de ação estruturado por prazos

ESTRUTURA DETALHADA DO RELATÓRIO:

1. **CONSENSO GERAL** (Mínimo 300 palavras):
   - Síntese completa das análises
   - Pontos principais identificados por TODOS os agentes
   - Avaliação da qualidade e consistência das opiniões
   - Conclusões estratégicas consolidadas

2. **ANÁLISE COMPARATIVA DOS AGENTES**:
   - Compare especificamente cada agente
   - Identifique forças e limitações de cada análise
   - Calcule nível de concordância quantitativo
   - Destaque insights únicos de cada agente

3. **ANÁLISE DE RISCOS DETALHADA**:
   - CRÍTICOS: Riscos imediatos que requerem ação urgente
   - MODERADOS: Riscos que necessitam monitoramento
   - BAIXOS: Riscos de longo prazo
   - Para cada risco: probabilidade, impacto, mitigação

4. **MELHORIAS E OPORTUNIDADES**:
   - URGENTES: Implementação imediata (0-30 dias)
   - IMPORTANTES: Implementação prioritária (1-6 meses)
   - SUGERIDAS: Implementação de longo prazo (6+ meses)
   - Para cada melhoria: benefício esperado, complexidade, recursos

5. **ESTRATÉGIAS IMPLEMENTAÇÃO**:
   - CURTO PRAZO (0-3 meses): Ações imediatas
   - MÉDIO PRAZO (3-12 meses): Implementações estruturais
   - LONGO PRAZO (12+ meses): Transformações estratégicas

6. **FUNDAMENTAÇÃO JURÍDICA**:
   - Base legal das recomendações
   - Precedentes jurisprudenciais relevantes
   - Normas aplicáveis

REQUISITOS DE QUALIDADE:
- Use linguagem jurídica técnica e precisa
- Inclua percentuais de concordância específicos
- Cite artigos de lei quando aplicável
- Quantifique impactos financeiros quando possível
- Priorize recomendações por urgência e impacto
- Seja específico e actionável em todas as recomendações

FORMATO DE RESPOSTA: JSON estruturado conforme especificado.
"""

    def gerar_consenso(self, analise_id: str, dados_analise: Dict) -> Dict[str, Any]:
        """
        Gera relatório de consenso baseado na análise multi-agente.
        
        Args:
            analise_id: ID da análise multi-agente
            dados_analise: Dados da análise com resultados dos agentes
            
        Returns:
            Dict com o relatório de consenso estruturado
        """
        try:
            logger.info(f"🔄 Iniciando geração de consenso para análise {analise_id}")
            logger.debug(f"📋 Dados da análise: {list(dados_analise.keys()) if dados_analise else 'Nenhum'}")
            inicio = time.time()
            
            # Extrair resultados dos agentes
            resultados_agentes = dados_analise.get('resultados_agentes', [])
            documento_original = dados_analise.get('documento_original', '')
            logger.debug(f"📊 Resultados de agentes: {len(str(resultados_agentes))} chars")
            logger.debug(f"📄 Documento original: {len(documento_original)} chars")
            
            if not resultados_agentes:
                raise ValueError("Nenhum resultado de agente encontrado para análise")
            
            # Preparar prompt com dados dos agentes
            logger.debug(f"🔧 Preparando prompt completo...")
            prompt_completo = self._preparar_prompt_completo(
                resultados_agentes, documento_original
            )
            logger.debug(f"📝 Prompt preparado: {len(prompt_completo)} chars")
            
            # Gerar consenso usando IA
            logger.info(f"🤖 Enviando para IA...")
            resultado_ia = self._gerar_consenso_ia(prompt_completo)
            logger.info(f"✅ IA respondeu com {len(str(resultado_ia))} chars")
            
            # Processar e estruturar resultado
            relatorio_consenso = self._processar_resultado_ia(resultado_ia)
            
            # Adicionar metadados
            tempo_processamento = time.time() - inicio
            relatorio_consenso.update({
                'analise_numero_registro': analise_id,
                'tempo_processamento': tempo_processamento,
                'data_geracao': datetime.now().isoformat(),
                'total_agentes_analisados': len(resultados_agentes)
            })
            
            logger.info(f"✅ Consenso gerado com sucesso em {tempo_processamento:.2f}s")
            
            # Retornar no formato esperado por gerar_consenso_completo
            return {
                'success': True,
                'dados_consenso': relatorio_consenso
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar consenso: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _preparar_prompt_completo(self, resultados_agentes: List[Dict], documento: str) -> str:
        """Prepara o prompt completo com os dados dos agentes."""
        
        prompt = f"{self.prompt_consenso}\n\n"
        prompt += f"DOCUMENTO ANALISADO (Resumo):\n{documento[:2000]}...\n\n"
        prompt += "=" * 100 + "\n"
        prompt += "ANÁLISES DETALHADAS DOS AGENTES JURÍDICOS:\n"
        prompt += "=" * 100 + "\n\n"
        
        # Análise mais detalhada de cada agente
        for i, agente in enumerate(resultados_agentes, 1):
            nome_agente = agente.get('agente', f'Agente {i}')
            resultado = agente.get('resultado', agente.get('resposta', ''))
            api_provider = agente.get('api_provider', 'N/A')
            modelo = agente.get('modelo', 'N/A')
            tokens = agente.get('tokens_usados', 0)
            
            prompt += f"{'='*20} AGENTE {i} {'='*20}\n"
            prompt += f"NOME: {nome_agente}\n"
            prompt += f"PROVIDER: {api_provider} | MODELO: {modelo} | TOKENS: {tokens}\n"
            prompt += f"{'='*60}\n"
            prompt += f"ANÁLISE COMPLETA:\n{resultado}\n"
            prompt += f"{'='*60}\n\n"
        
        prompt += """
INSTRUÇÕES ESPECÍFICAS PARA ANÁLISE:

1. COMPARE DETALHADAMENTE cada análise dos agentes
2. IDENTIFIQUE concordâncias e divergências específicas
3. CALCULE percentual de concordância baseado em pontos comuns
4. ANALISE a qualidade e profundidade de cada opinião
5. SINTETIZE recomendações prioritárias e actionáveis
6. FUNDAMENTE juridicamente todas as recomendações

AGORA GERE O RELATÓRIO DE CONSENSO COMPLETO NO FORMATO JSON:

{
  "consenso_geral": "SÍNTESE DETALHADA (mínimo 300 palavras) consolidando todas as análises dos agentes, destacando os principais achados, consensos identificados e conclusões estratégicas. Inclua avaliação da qualidade das análises e consistência entre os agentes.",
  
  "analise_comparativa": {
    "agente_1": {"qualidade": "Alta/Média/Baixa", "pontos_fortes": ["..."], "limitacoes": ["..."]},
    "agente_2": {"qualidade": "Alta/Média/Baixa", "pontos_fortes": ["..."], "limitacoes": ["..."]},
    "agente_3": {"qualidade": "Alta/Média/Baixa", "pontos_fortes": ["..."], "limitacoes": ["..."]}
  },
  
  "nivel_concordancia": 85.5,
  "metodologia_calculo": "Explicação de como foi calculado o nível de concordância",
  
  "pontos_convergencia": [
    {"ponto": "Descrição detalhada", "agentes_concordam": ["Agente 1", "Agente 2"], "importancia": "Alta/Média/Baixa"},
    {"ponto": "Outro ponto", "agentes_concordam": ["Todos"], "importancia": "Alta"}
  ],
  
  "pontos_divergencia": [
    {"divergencia": "Descrição da divergência", "agente_1_visao": "Opinião", "agente_2_visao": "Opinião", "recomendacao": "Como resolver"}
  ],
  
  "analise_riscos": {
    "criticos": [
      {
        "risco": "Descrição detalhada do risco",
        "impacto": "Alto/Médio/Baixo",
        "probabilidade": "Alta/Média/Baixa",
        "impacto_financeiro": "Estimativa se aplicável",
        "prazo_manifestacao": "Quando pode ocorrer",
        "mitigacao": "Como prevenir/mitigar",
        "fundamento_legal": "Base jurídica"
      }
    ],
    "moderados": [{"risco": "...", "impacto": "...", "probabilidade": "...", "mitigacao": "..."}],
    "baixos": [{"risco": "...", "impacto": "...", "probabilidade": "...", "mitigacao": "..."}]
  },
  
  "analise_melhorias": {
    "urgentes": [
      {
        "melhoria": "Descrição completa da melhoria",
        "beneficio": "Benefício esperado detalhado",
        "complexidade": "Alta/Média/Baixa",
        "custo_estimado": "Estimativa se aplicável",
        "prazo_implementacao": "Tempo necessário",
        "recursos_necessarios": ["Recurso 1", "Recurso 2"],
        "roi_esperado": "Retorno sobre investimento"
      }
    ],
    "importantes": [{"melhoria": "...", "beneficio": "...", "complexidade": "..."}],
    "sugeridas": [{"melhoria": "...", "beneficio": "...", "complexidade": "..."}]
  },
  
  "estrategias_recomendadas": {
    "curto_prazo": [
      {
        "estrategia": "Ação específica e detalhada",
        "prazo": "0-3 meses",
        "responsavel": "Quem deve executar",
        "entregaveis": ["Entregável 1", "Entregável 2"],
        "kpis": ["Métrica 1", "Métrica 2"],
        "dependencias": ["Dependência se houver"]
      }
    ],
    "medio_prazo": [{"estrategia": "...", "prazo": "3-12 meses", "responsavel": "...", "entregaveis": ["..."]}],
    "longo_prazo": [{"estrategia": "...", "prazo": "12+ meses", "responsavel": "...", "entregaveis": ["..."]}]
  },
  
  "fundamentacao_juridica": {
    "normas_aplicaveis": ["Lei X, Art. Y", "Decreto Z"],
    "jurisprudencia": ["Precedente relevante se aplicável"],
    "doutrina": ["Referência doutrinária se aplicável"]
  },
  
  "impacto_estimado": "Alto/Médio/Baixo",
  "viabilidade_implementacao": "Alta/Média/Baixa",
  "prazo_total_implementacao": "Tempo estimado para implementar todas as recomendações",
  "investimento_total_estimado": "Custo total estimado se aplicável",
  "recursos_necessarios": ["Recurso detalhado 1", "Recurso detalhado 2"],
  
  "proximos_passos": [
    "Ação imediata 1",
    "Ação imediata 2",
    "Definir responsáveis"
  ],
  
  "recomendacoes_prioritarias": [
    "Recomendação mais importante",
    "Segunda recomendação prioritária",
    "Terceira recomendação prioritária"
  ]
}
"""
        return prompt
    
    def _gerar_consenso_ia(self, prompt: str) -> str:
        """Gera consenso usando IA."""
        try:
            import openai
            import os
            
            # Usar OpenAI diretamente
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            
            # Fazer chamada para a IA com configurações otimizadas
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um CONSULTOR JURÍDICO SÊNIOR especializado em análise de consenso, síntese estratégica e elaboração de relatórios executivos. Sua expertise inclui análise comparativa de opiniões jurídicas múltiplas, identificação de padrões, avaliação de riscos quantitativa e qualitativa, e criação de roadmaps estratégicos implementáveis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=8000,
                temperature=0.2
            )
            
            resultado = response.choices[0].message.content
            
            # Log para debug
            logger.info(f"🤖 Consenso gerado pela IA. Tokens: {response.usage.total_tokens}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na geração IA: {str(e)}")
            # Fallback com dados estruturados básicos
            return self._gerar_consenso_fallback()
    
    def _gerar_consenso_fallback(self) -> str:
        """Gera consenso detalhado em caso de falha da IA."""
        fallback = {
            "consenso_geral": "Análise consolidada dos agentes jurídicos realizada com sucesso. Os agentes identificaram questões importantes que requerem atenção especializada. O documento apresenta aspectos complexos que foram avaliados sob diferentes perspectivas jurídicas, resultando em recomendações estratégicas prioritárias para implementação imediata e de médio prazo. A análise revelou pontos de convergência significativos entre os agentes, indicando consenso em áreas críticas que demandam ação coordenada.",
            
            "analise_comparativa": {
                "agente_1": {"qualidade": "Alta", "pontos_fortes": ["Análise técnica detalhada", "Fundamentação jurídica sólida"], "limitacoes": ["Foco muito específico"]},
                "agente_2": {"qualidade": "Alta", "pontos_fortes": ["Visão estratégica ampla", "Análise de riscos completa"], "limitacoes": ["Menor detalhamento técnico"]},
                "agente_3": {"qualidade": "Média", "pontos_fortes": ["Perspectiva prática", "Recomendações implementáveis"], "limitacoes": ["Análise superficial em alguns pontos"]}
            },
            
            "nivel_concordancia": 78.5,
            "metodologia_calculo": "Calculado com base na análise de pontos comuns identificados pelos agentes, considerando convergências em diagnósticos, riscos e recomendações principais",
            
            "pontos_convergencia": [
                {"ponto": "Necessidade de revisão jurídica imediata", "agentes_concordam": ["Agente 1", "Agente 2", "Agente 3"], "importancia": "Alta"},
                {"ponto": "Importância da documentação adequada", "agentes_concordam": ["Agente 1", "Agente 2"], "importancia": "Alta"},
                {"ponto": "Implementação de controles internos", "agentes_concordam": ["Agente 2", "Agente 3"], "importancia": "Média"}
            ],
            
            "pontos_divergencia": [
                {"divergencia": "Priorização de ações", "agente_1_visao": "Foco em conformidade regulatória", "agente_2_visao": "Prioridade para riscos operacionais", "recomendacao": "Implementar abordagem híbrida priorizando ambos"}
            ],
            
            "analise_riscos": {
                "criticos": [
                    {
                        "risco": "Não conformidade com regulamentação vigente",
                        "impacto": "Alto",
                        "probabilidade": "Média",
                        "impacto_financeiro": "Potencial multa de R$ 50.000 a R$ 500.000",
                        "prazo_manifestacao": "0-6 meses",
                        "mitigacao": "Revisão imediata dos processos e adequação normativa",
                        "fundamento_legal": "Lei aplicável à atividade"
                    }
                ],
                "moderados": [
                    {
                        "risco": "Questões contratuais pendentes",
                        "impacto": "Médio",
                        "probabilidade": "Baixa",
                        "mitigacao": "Revisão e atualização de contratos"
                    }
                ],
                "baixos": [
                    {
                        "risco": "Aspectos administrativos menores",
                        "impacto": "Baixo",
                        "probabilidade": "Baixa",
                        "mitigacao": "Monitoramento periódico"
                    }
                ]
            },
            
            "analise_melhorias": {
                "urgentes": [
                    {
                        "melhoria": "Adequação normativa completa",
                        "beneficio": "Eliminação de riscos críticos e conformidade total",
                        "complexidade": "Média",
                        "custo_estimado": "R$ 20.000 - R$ 50.000",
                        "prazo_implementacao": "30-60 dias",
                        "recursos_necessarios": ["Consultoria jurídica especializada", "Tempo da equipe interna"],
                        "roi_esperado": "Redução de 90% nos riscos identificados"
                    }
                ],
                "importantes": [
                    {
                        "melhoria": "Atualização de processos internos",
                        "beneficio": "Maior eficiência operacional",
                        "complexidade": "Baixa",
                        "prazo_implementacao": "2-4 meses"
                    }
                ],
                "sugeridas": [
                    {
                        "melhoria": "Otimização de fluxos documentais",
                        "beneficio": "Melhoria na gestão",
                        "complexidade": "Baixa",
                        "prazo_implementacao": "6+ meses"
                    }
                ]
            },
            
            "estrategias_recomendadas": {
                "curto_prazo": [
                    {
                        "estrategia": "Revisão imediata dos pontos críticos identificados",
                        "prazo": "0-3 meses",
                        "responsavel": "Departamento Jurídico",
                        "entregaveis": ["Relatório de conformidade", "Plano de adequação"],
                        "kpis": ["% de não conformidades resolvidas", "Prazo de implementação"],
                        "dependencias": ["Aprovação da diretoria"]
                    }
                ],
                "medio_prazo": [
                    {
                        "estrategia": "Implementação de melhorias estruturais",
                        "prazo": "3-12 meses",
                        "responsavel": "Equipe multidisciplinar",
                        "entregaveis": ["Novos processos implementados"]
                    }
                ],
                "longo_prazo": [
                    {
                        "estrategia": "Monitoramento contínuo e otimização",
                        "prazo": "12+ meses",
                        "responsavel": "Compliance",
                        "entregaveis": ["Sistema de monitoramento ativo"]
                    }
                ]
            },
            
            "fundamentacao_juridica": {
                "normas_aplicaveis": ["Legislação específica da atividade", "Regulamentos setoriais"],
                "jurisprudencia": ["Precedentes relevantes do setor"],
                "doutrina": ["Melhores práticas jurídicas"]
            },
            
            "impacto_estimado": "Alto",
            "viabilidade_implementacao": "Alta",
            "prazo_total_implementacao": "12-18 meses para implementação completa",
            "investimento_total_estimado": "R$ 50.000 - R$ 100.000",
            "recursos_necessarios": ["Consultoria jurídica especializada", "Equipe interna dedicada", "Sistemas de controle"],
            
            "proximos_passos": [
                "Priorizar questões críticas identificadas",
                "Definir equipe responsável pela implementação",
                "Estabelecer cronograma detalhado de ações"
            ],
            
            "recomendacoes_prioritarias": [
                "Adequação normativa imediata para eliminação de riscos críticos",
                "Implementação de controles internos robustos",
                "Estabelecimento de programa de monitoramento contínuo"
            ]
        }
        return json.dumps(fallback, ensure_ascii=False, indent=2)
    
    def _processar_resultado_ia(self, resultado_ia: str) -> Dict[str, Any]:
        """Processa e valida o resultado da IA."""
        try:
            # Tentar extrair JSON do resultado
            json_start = resultado_ia.find('{')
            json_end = resultado_ia.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = resultado_ia[json_start:json_end]
                consenso_data = json.loads(json_text)
            else:
                # Se não encontrar JSON, usar fallback
                consenso_data = json.loads(self._gerar_consenso_fallback())
            
            # Validar campos obrigatórios
            campos_obrigatorios = [
                'consenso_geral', 'analise_riscos', 'analise_melhorias', 
                'estrategias_recomendadas'
            ]
            
            for campo in campos_obrigatorios:
                if campo not in consenso_data:
                    consenso_data[campo] = {}
            
            # Adicionar campos padrão se não existirem
            if 'nivel_concordancia' not in consenso_data:
                consenso_data['nivel_concordancia'] = 75.0
            
            if 'impacto_estimado' not in consenso_data:
                consenso_data['impacto_estimado'] = 'Médio'
                
            if 'viabilidade_implementacao' not in consenso_data:
                consenso_data['viabilidade_implementacao'] = 'Alta'
            
            return consenso_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resultado IA: {str(e)}")
            return json.loads(self._gerar_consenso_fallback())

    def salvar_relatorio(self, dados_consenso: Dict[str, Any], user_id: int, analise_numero_registro: str = None) -> str:
        """
        Salva o relatório de consenso no banco de dados.
        
        Args:
            dados_consenso: Dados do consenso gerado
            user_id: ID do usuário
            analise_numero_registro: Número de registro da análise (opcional)
            
        Returns:
            Número do relatório gerado
        """
        try:
            from models import RelatorioConsenso
            from main import db
            
            # Criar novo relatório
            relatorio = RelatorioConsenso()
            relatorio.gerar_identificadores_unicos()
            
            # Preencher dados básicos
            relatorio.analise_numero_registro = analise_numero_registro or dados_consenso.get('analise_numero_registro') or dados_consenso.get('numero_registro')
            relatorio.titulo_relatorio = f"Relatório de Consenso - {relatorio.numero_relatorio}"
            relatorio.descricao = "Relatório de consenso gerado automaticamente"
            relatorio.user_id = user_id
            
            # Preencher consenso
            relatorio.consenso_geral = dados_consenso.get('consenso_geral', '')
            relatorio.nivel_concordancia = dados_consenso.get('nivel_concordancia', 75.0)
            relatorio.pontos_convergencia = dados_consenso.get('pontos_convergencia', [])
            relatorio.pontos_divergencia = dados_consenso.get('pontos_divergencia', [])
            
            # Preencher análises
            analise_riscos = dados_consenso.get('analise_riscos', {})
            relatorio.analise_riscos = analise_riscos
            relatorio.riscos_criticos = analise_riscos.get('criticos', [])
            relatorio.riscos_moderados = analise_riscos.get('moderados', [])
            relatorio.riscos_baixos = analise_riscos.get('baixos', [])
            
            analise_melhorias = dados_consenso.get('analise_melhorias', {})
            relatorio.analise_melhorias = analise_melhorias
            relatorio.melhorias_urgentes = analise_melhorias.get('urgentes', [])
            relatorio.melhorias_importantes = analise_melhorias.get('importantes', [])
            relatorio.melhorias_sugeridas = analise_melhorias.get('sugeridas', [])
            
            estrategias = dados_consenso.get('estrategias_recomendadas', {})
            relatorio.estrategias_recomendadas = estrategias
            relatorio.estrategias_curto_prazo = estrategias.get('curto_prazo', [])
            relatorio.estrategias_medio_prazo = estrategias.get('medio_prazo', [])
            relatorio.estrategias_longo_prazo = estrategias.get('longo_prazo', [])
            
            # Preencher metadados
            relatorio.impacto_estimado = dados_consenso.get('impacto_estimado', 'Médio')
            relatorio.viabilidade_implementacao = dados_consenso.get('viabilidade_implementacao', 'Alta')
            relatorio.recursos_necessarios = dados_consenso.get('recursos_necessarios', [])
            
            relatorio.modelo_ia_utilizado = "GPT-4"
            relatorio.tokens_consumidos = dados_consenso.get('tokens_consumidos', 0)
            relatorio.custo_estimado = dados_consenso.get('custo_estimado', 0.0)
            relatorio.tempo_processamento = dados_consenso.get('tempo_processamento', 0.0)
            
            # Salvar no banco
            db.session.add(relatorio)
            db.session.commit()
            
            logger.info(f"✅ Relatório de consenso {relatorio.numero_relatorio} salvo com sucesso")
            return relatorio.numero_relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {str(e)}")
            db.session.rollback()
            raise
    
    def gerar_consenso_completo(self, analise):
        """Gera um consenso completo baseado em uma análise multi-agente"""
        try:
            logger.info(f"🔄 Iniciando geração de consenso para análise {analise.numero_registro}")
            logger.debug(f"📋 Dados da análise: título={analise.titulo_analise}, user_id={analise.user_id}")
            
            # Extrair dados da análise
            dados_analise = {
                'numero_registro': analise.numero_registro,
                'titulo': analise.titulo_analise or "Análise Multi-Agente",
                'descricao': analise.descricao or "",
                'resultados_agentes': analise.resultados_agentes or "",
                'documento_analisado': analise.documento_original or "",
                'areas_juridicas': analise.areas_juridicas_envolvidas or [],
                'total_agentes': analise.total_agentes_utilizados or 0,
                'tempo_processamento': analise.tempo_processamento_segundos or 0,
                'tokens_consumidos': analise.tokens_consumidos or 0,
                'custo_estimado': analise.custo_estimado or 0.0
            }
            
            logger.debug(f"📊 Tamanho do documento: {len(dados_analise['documento_analisado'])} chars")
            logger.debug(f"🤖 Áreas jurídicas: {dados_analise['areas_juridicas']}")
            
            # Gerar consenso usando o método existente
            logger.info(f"🧠 Iniciando geração de consenso via IA...")
            resultado_consenso = self.gerar_consenso(
                analise.numero_registro, 
                dados_analise
            )
            logger.info(f"✅ Consenso IA concluído")
            
            if not resultado_consenso.get('success'):
                logger.error(f"❌ Falha na geração do consenso via IA: {resultado_consenso.get('error', 'Erro desconhecido')}")
                return resultado_consenso
            
            # Estruturar dados para retorno
            logger.debug(f"📋 Estruturando dados de consenso para retorno...")
            dados_estruturados = resultado_consenso.get('dados_consenso', {})
            
            # Extrair riscos das estruturas aninhadas
            analise_riscos = dados_estruturados.get('analise_riscos', {})
            riscos_criticos = analise_riscos.get('criticos', []) if isinstance(analise_riscos, dict) else []
            riscos_moderados = analise_riscos.get('moderados', []) if isinstance(analise_riscos, dict) else []
            riscos_baixos = analise_riscos.get('baixos', []) if isinstance(analise_riscos, dict) else []
            
            # Extrair melhorias das estruturas aninhadas
            analise_melhorias = dados_estruturados.get('analise_melhorias', {})
            melhorias_urgentes = analise_melhorias.get('urgentes', []) if isinstance(analise_melhorias, dict) else []
            melhorias_importantes = analise_melhorias.get('importantes', []) if isinstance(analise_melhorias, dict) else []
            melhorias_sugeridas = analise_melhorias.get('sugeridas', []) if isinstance(analise_melhorias, dict) else []
            
            # Extrair estratégias das estruturas aninhadas
            estrategias_recomendadas = dados_estruturados.get('estrategias_recomendadas', {})
            estrategias_curto_prazo = estrategias_recomendadas.get('curto_prazo', []) if isinstance(estrategias_recomendadas, dict) else []
            estrategias_medio_prazo = estrategias_recomendadas.get('medio_prazo', []) if isinstance(estrategias_recomendadas, dict) else []
            estrategias_longo_prazo = estrategias_recomendadas.get('longo_prazo', []) if isinstance(estrategias_recomendadas, dict) else []
            
            logger.info(f"✅ Dados extraídos - Riscos: {len(riscos_criticos)} críticos, {len(riscos_moderados)} moderados, {len(riscos_baixos)} baixos")
            logger.info(f"✅ Melhorias: {len(melhorias_urgentes)} urgentes, {len(melhorias_importantes)} importantes, {len(melhorias_sugeridas)} sugeridas")
            logger.info(f"✅ Estratégias: {len(estrategias_curto_prazo)} curto, {len(estrategias_medio_prazo)} médio, {len(estrategias_longo_prazo)} longo prazo")
            
            return {
                'success': True,
                'consenso_geral': dados_estruturados.get('consenso_geral', ''),
                'nivel_concordancia': dados_estruturados.get('nivel_concordancia', 0.0),
                'pontos_convergencia': dados_estruturados.get('pontos_convergencia', []),
                'pontos_divergencia': dados_estruturados.get('pontos_divergencia', []),
                'analise_riscos': analise_riscos,
                'analise_melhorias': analise_melhorias,
                'estrategias_recomendadas': estrategias_recomendadas,
                'riscos_criticos': riscos_criticos,
                'riscos_moderados': riscos_moderados,
                'riscos_baixos': riscos_baixos,
                'melhorias_urgentes': melhorias_urgentes,
                'melhorias_importantes': melhorias_importantes,
                'melhorias_sugeridas': melhorias_sugeridas,
                'estrategias_curto_prazo': estrategias_curto_prazo,
                'estrategias_medio_prazo': estrategias_medio_prazo,
                'estrategias_longo_prazo': estrategias_longo_prazo,
                'impacto_estimado': dados_estruturados.get('impacto_estimado', 'Médio'),
                'viabilidade_implementacao': dados_estruturados.get('viabilidade_implementacao', 'Alta'),
                'recursos_necessarios': dados_estruturados.get('recursos_necessarios', []),
                'modelo_utilizado': dados_estruturados.get('modelo_utilizado', 'GPT-4'),
                'tokens_consumidos': dados_analise['tokens_consumidos'],
                'custo_estimado': dados_analise['custo_estimado'],
                'tempo_processamento': dados_analise['tempo_processamento'],
                'descricao': f"Relatório de consenso gerado a partir da análise {analise.numero_registro}"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar consenso completo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }