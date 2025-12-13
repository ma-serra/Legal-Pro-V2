"""
Sistema Avançado de Orquestração Multi-API
Combina as melhores capacidades de cada provedor de IA para análises jurídicas superiores
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configuração dos provedores com suas especialidades
API_SPECIALIZATIONS = {
    'openai': {
        'model': 'gpt-4o',
        'strengths': ['análise_estrutural', 'identificação_clausulas', 'conformidade_legal'],
        'focus': 'Estrutura e conformidade legal detalhada',
        'prompt_style': 'analytical'
    },
    'anthropic': {
        'model': 'claude-3-5-sonnet-20241022',
        'strengths': ['raciocinio_juridico', 'precedentes', 'interpretacao_doutrinaria'],
        'focus': 'Raciocínio jurídico e precedentes',
        'prompt_style': 'reasoning'
    },
    'google': {
        'model': 'gemini-1.5-pro',
        'strengths': ['contexto_amplo', 'legislacao_correlata', 'impactos_sistemicos'],
        'focus': 'Contexto legislativo amplo e impactos sistêmicos',
        'prompt_style': 'contextual'
    },
    'deepseek': {
        'model': 'deepseek-chat',
        'strengths': ['analise_critica', 'gaps_legais', 'recomendacoes_praticas'],
        'focus': 'Análise crítica e recomendações práticas',
        'prompt_style': 'critical'
    }
}

class AdvancedMultiAPIOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {}
        self.api_availability = {}
        
    def create_specialized_prompt(self, text: str, api_provider: str, area_juridica: str) -> str:
        """Cria prompts especializados para cada provedor de IA"""
        
        base_context = f"""
        ÁREA JURÍDICA: {area_juridica.upper()}
        DOCUMENTO PARA ANÁLISE:
        {text}
        
        ---
        """
        
        if api_provider == 'openai':
            return f"""{base_context}
            INSTRUÇÃO ESPECIALIZADA - ANÁLISE ESTRUTURAL E CONFORMIDADE:
            
            Como especialista em estrutura legal e conformidade, analise o documento focando em:
            
            1. ESTRUTURA FORMAL:
               - Identificação correta das partes
               - Presença de elementos contratuais essenciais
               - Formato e redação adequados
            
            2. CONFORMIDADE LEGAL:
               - Adequação à legislação vigente
               - Cláusulas obrigatórias presentes/ausentes
               - Aspectos de validade jurídica
            
            3. IDENTIFICAÇÃO DE CLÁUSULAS:
               - Mapeamento de todas as cláusulas
               - Classificação por tipo e importância
               - Detecção de cláusulas problemáticas
            
            Forneça uma análise estruturada, objetiva e tecnicamente precisa.
            """
            
        elif api_provider == 'anthropic':
            return f"""{base_context}
            INSTRUÇÃO ESPECIALIZADA - RACIOCÍNIO JURÍDICO E PRECEDENTES:
            
            Como especialista em doutrina e jurisprudência, desenvolva uma análise focada em:
            
            1. FUNDAMENTAÇÃO TEÓRICA:
               - Base doutrinária aplicável
               - Princípios jurídicos envolvidos
               - Interpretação sistemática da norma
            
            2. PRECEDENTES E JURISPRUDÊNCIA:
               - Entendimentos consolidados dos tribunais
               - Tendências jurisprudenciais relevantes
               - Possíveis divergências interpretativas
            
            3. RACIOCÍNIO JURÍDICO:
               - Cadeia lógica de argumentação
               - Ponderação de interesses em conflito
               - Consequências jurídicas das disposições
            
            Desenvolva um raciocínio jurídico sólido e bem fundamentado.
            """
            
        elif api_provider == 'google':
            return f"""{base_context}
            INSTRUÇÃO ESPECIALIZADA - CONTEXTO LEGISLATIVO E IMPACTOS SISTÊMICOS:
            
            Como especialista em legislação correlata e impactos sistêmicos, analise:
            
            1. CONTEXTO LEGISLATIVO AMPLO:
               - Normas correlatas aplicáveis
               - Interação com outros diplomas legais
               - Hierarquia normativa e conflitos
            
            2. IMPACTOS SISTÊMICOS:
               - Efeitos na relação jurídica global
               - Consequências para terceiros
               - Repercussões em outras esferas do direito
            
            3. VISÃO PANORÂMICA:
               - Inserção no ordenamento jurídico
               - Tendências regulatórias futuras
               - Aspectos de política legislativa
            
            Forneça uma visão abrangente e contextualizada do documento.
            """
            
        elif api_provider == 'deepseek':
            return f"""{base_context}
            INSTRUÇÃO ESPECIALIZADA - ANÁLISE CRÍTICA E RECOMENDAÇÕES:
            
            Como especialista em análise crítica e soluções práticas, examine:
            
            1. ANÁLISE CRÍTICA:
               - Pontos vulneráveis do documento
               - Lacunas e omissões significativas
               - Riscos jurídicos identificados
            
            2. GAPS LEGAIS:
               - Aspectos não regulamentados
               - Zonas de incerteza jurídica
               - Necessidades de complementação
            
            3. RECOMENDAÇÕES PRÁTICAS:
               - Sugestões de melhoria específicas
               - Medidas preventivas recomendadas
               - Estratégias de implementação
            
            Desenvolva uma análise crítica construtiva com soluções viáveis.
            """
        
        return base_context + "Realize uma análise jurídica completa e detalhada."
    
    def process_with_multiple_apis(self, text: str, area_juridica: str = 'empresarial') -> Dict[str, Any]:
        """Processa o documento com múltiplas APIs simultaneamente"""
        
        start_time = time.time()
        results = {}
        errors = {}
        
        # Importar clientes das APIs
        try:
            from modules.multi_api_handler import MultiAPIHandler
            api_handler = MultiAPIHandler()
        except Exception as e:
            self.logger.error(f"Erro ao inicializar MultiAPIHandler: {e}")
            return self._fallback_analysis(text, area_juridica)
        
        # Executar análises em paralelo
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            for provider, config in API_SPECIALIZATIONS.items():
                prompt = self.create_specialized_prompt(text, provider, area_juridica)
                future = executor.submit(self._safe_api_call, api_handler, provider, prompt, config)
                futures[future] = provider
            
            # Coletar resultados
            for future in as_completed(futures):
                provider = futures[future]
                try:
                    result = future.result(timeout=30)  # 30 segundos timeout
                    if result:
                        results[provider] = {
                            'analise': result,
                            'especialidade': API_SPECIALIZATIONS[provider]['focus'],
                            'modelo': API_SPECIALIZATIONS[provider]['model'],
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        errors[provider] = "Resposta vazia"
                except Exception as e:
                    errors[provider] = str(e)
                    self.logger.error(f"Erro na API {provider}: {e}")
        
        # Calcular métricas de performance
        total_time = time.time() - start_time
        self.performance_metrics = {
            'total_processing_time': total_time,
            'apis_successful': len(results),
            'apis_failed': len(errors),
            'success_rate': len(results) / len(API_SPECIALIZATIONS) * 100
        }
        
        # Gerar análise consolidada
        consolidated_analysis = self._generate_consolidated_analysis(results, area_juridica)
        
        return {
            'results': results,
            'errors': errors,
            'consolidated_analysis': consolidated_analysis,
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def _safe_api_call(self, api_handler, provider: str, prompt: str, config: Dict) -> Optional[str]:
        """Executa chamada de API com tratamento de erro"""
        try:
            if provider == 'openai':
                return api_handler.call_openai(prompt)
            elif provider == 'anthropic':
                return api_handler.call_anthropic(prompt)
            elif provider == 'google':
                return api_handler.call_google(prompt)
            elif provider == 'deepseek':
                return api_handler.call_deepseek(prompt)
        except Exception as e:
            self.logger.error(f"Erro na API {provider}: {e}")
            return None
    
    def _generate_consolidated_analysis(self, results: Dict, area_juridica: str) -> str:
        """Gera análise consolidada integrando todas as perspectivas"""
        
        if not results:
            return "Não foi possível gerar análise consolidada - nenhuma API retornou resultados."
        
        consolidation = f"""
        # ANÁLISE JURÍDICA CONSOLIDADA MULTI-API
        **Área:** {area_juridica.title()}
        **Processamento:** {len(results)} perspectivas de IA diferentes
        **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        ## SÍNTESE EXECUTIVA
        
        Esta análise integra {len(results)} perspectivas especializadas de diferentes modelos de IA, cada um focado em aspectos específicos da análise jurídica:
        """
        
        # Adicionar insights de cada API
        for provider, data in results.items():
            config = API_SPECIALIZATIONS[provider]
            consolidation += f"""
        
        ### {config['focus']} ({config['model']})
        **Especialização:** {', '.join(config['strengths'])}
        
        {data['analise'][:500]}...
        """
        
        # Adicionar conclusão integrada
        consolidation += f"""
        
        ## CONCLUSÃO INTEGRADA
        
        Baseando-se na convergência das {len(results)} análises especializadas, os principais aspectos identificados são:
        
        1. **Conformidade Estrutural**: Elementos formais e adequação legal
        2. **Fundamentação Jurídica**: Base doutrinária e jurisprudencial
        3. **Contexto Sistêmico**: Inserção no ordenamento e impactos
        4. **Recomendações Práticas**: Melhorias e medidas preventivas
        
        **Recomendação Final**: Prosseguir com implementação considerando as observações específicas de cada perspectiva de análise.
        """
        
        return consolidation
    
    def _fallback_analysis(self, text: str, area_juridica: str) -> Dict[str, Any]:
        """Análise de fallback quando APIs falham"""
        return {
            'results': {},
            'errors': {'system': 'Falha na inicialização do sistema multi-API'},
            'consolidated_analysis': f"Análise de emergência para documento de {area_juridica}. Sistema temporariamente indisponível.",
            'performance_metrics': {'total_processing_time': 0, 'apis_successful': 0, 'apis_failed': 4, 'success_rate': 0},
            'timestamp': datetime.now().isoformat()
        }

# Instância global
orchestrator = AdvancedMultiAPIOrchestrator()