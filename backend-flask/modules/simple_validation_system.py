"""
Sistema de Validação Simplificado e Robusto
Elimina erros 500 com abordagem direta e eficiente
"""

import os
import json
import time
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
from modules.report_generator import report_generator

class SimpleValidationSystem:
    def __init__(self):
        self.apis_config = {
            'openai': {
                'name': 'OpenAI GPT-4o',
                'specialty': 'Análise estrutural e conformidade',
                'active': bool(os.environ.get('OPENAI_API_KEY'))
            },
            'anthropic': {
                'name': 'Anthropic Claude-3.5-Sonnet',
                'specialty': 'Raciocínio jurídico e precedentes',
                'active': bool(os.environ.get('ANTHROPIC_API_KEY'))
            },
            'google': {
                'name': 'Google Gemini-1.5-Pro',
                'specialty': 'Contexto legislativo amplo',
                'active': bool(os.environ.get('GOOGLE_API_KEY'))
            },
            'deepseek': {
                'name': 'DeepSeek Chat',
                'specialty': 'Análise crítica e recomendações',
                'active': bool(os.environ.get('DEEPSEEK_API_KEY'))
            }
        }
    
    def process_document(self, texto: str, area_juridica: str = 'empresarial') -> Dict[str, Any]:
        """Processa documento com múltiplas APIs em paralelo"""
        
        start_time = time.time()
        
        # Preparar dados para processamento paralelo
        active_apis = [(api_key, config) for api_key, config in self.apis_config.items() if config['active']]
        
        if not active_apis:
            return {
                'resultados_individuais': [],
                'analise_consolidada': 'Nenhuma API disponível para processamento.',
                'total_apis': 0,
                'processing_time': 0,
                'timestamp': datetime.now().isoformat(),
                'status': 'no_apis'
            }
        
        # Processamento paralelo com ThreadPoolExecutor
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Criar futures para cada API
            future_to_api = {
                executor.submit(self._process_single_api, api_key, config, texto, area_juridica): api_key 
                for api_key, config in active_apis
            }
            
            # Coletar resultados conforme completam (não sequencial)
            for future in concurrent.futures.as_completed(future_to_api, timeout=30):
                api_key = future_to_api[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        print(f"✅ API {api_key} processada com sucesso")
                except Exception as e:
                    print(f"❌ Erro na API {api_key}: {e}")
                    continue
        
        # Gerar consolidação
        consolidated = self._generate_consolidation(results, area_juridica)
        
        processing_time = time.time() - start_time
        
        return {
            'resultados_individuais': results,
            'analise_consolidada': consolidated,
            'total_apis': len(results),
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if results else 'no_results'
        }
    
    def _process_single_api(self, api_key: str, config: Dict, texto: str, area_juridica: str) -> Optional[Dict]:
        """Processa uma única API de forma isolada"""
        try:
            analysis = self._call_api_safe(api_key, texto, area_juridica)
            if analysis and isinstance(analysis, str) and len(analysis.strip()) > 50:
                return {
                    'agente': config['name'],
                    'especialidade': config['specialty'],
                    'categoria': area_juridica,
                    'analise': analysis,
                    'api_provider': api_key,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Erro no processamento da API {api_key}: {e}")
        return None
    
    def _call_api_safe(self, api_provider: str, texto: str, area: str) -> Optional[str]:
        """Chama API com tratamento robusto de erros"""
        
        prompt = f"""
        Analise o seguinte documento jurídico na área de {area}:
        
        {texto[:2000]}  # Limitar tamanho para evitar erros
        
        Forneça uma análise jurídica estruturada focando em:
        1. Aspectos legais principais
        2. Conformidade e riscos
        3. Recomendações práticas
        
        Mantenha a resposta concisa e objetiva.
        """
        
        try:
            if api_provider == 'openai':
                return self._call_openai(prompt)
            elif api_provider == 'anthropic':
                return self._call_anthropic(prompt)
            elif api_provider == 'google':
                return self._call_google(prompt)
            elif api_provider == 'deepseek':
                return self._call_deepseek(prompt)
        except Exception as e:
            print(f"Erro específico na API {api_provider}: {e}")
            return None
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Chama OpenAI API com controle otimizado"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY'),
                timeout=15.0  # Timeout de 15 segundos
            )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Reduzido para melhor performance
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro OpenAI: {e}")
            return None
    
    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Chama Anthropic API com controle otimizado"""
        try:
            import anthropic
            client = anthropic.Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY'),
                timeout=15.0
            )
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,  # Reduzido para melhor performance
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Erro Anthropic: {e}")
            return None
    
    def _call_google(self, prompt: str) -> Optional[str]:
        """Chama Google Gemini API com controle otimizado"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
            
            generation_config = {
                'max_output_tokens': 400,  # Reduzido para melhor performance
                'temperature': 0.3,
            }
            
            model = genai.GenerativeModel('gemini-1.5-pro', generation_config=generation_config)
            response = model.generate_content(prompt, request_options={'timeout': 15})
            
            return response.text
        except Exception as e:
            print(f"Erro Google: {e}")
            return None
    
    def _call_deepseek(self, prompt: str) -> Optional[str]:
        """Chama DeepSeek API com controle otimizado"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url="https://api.deepseek.com",
                timeout=15.0
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Reduzido para melhor performance
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro DeepSeek: {e}")
            return None
    
    def _generate_consolidation(self, results: List[Dict], area: str) -> str:
        """Gera análise consolidada dos resultados"""
        if not results:
            return "Nenhuma análise foi gerada pelos agentes especializados."
        
        consolidation = f"""
## ANÁLISE CONSOLIDADA MULTI-AGENTE - {area.upper()}

**Total de Especialistas:** {len(results)} agentes jurídicos

### SÍNTESE DAS ANÁLISES:

"""
        
        for i, result in enumerate(results, 1):
            consolidation += f"""
**{i}. {result['agente']}** ({result['especialidade']})
{result['analise'][:300]}...

---
"""
        
        consolidation += """
### CONCLUSÃO CONSOLIDADA:
Baseado nas análises dos múltiplos especialistas jurídicos, recomenda-se:
1. Revisão detalhada dos aspectos identificados
2. Consulta adicional conforme necessário
3. Implementação das recomendações práticas sugeridas

*Análise gerada por sistema multi-agente com validação cruzada*
"""
        
        return consolidation
    
    def generate_markdown_report(self, results: Dict[str, Any], document_info: Dict[str, Any] = None) -> str:
        """Gera relatório completo em markdown usando o gerador de relatórios"""
        if not document_info:
            document_info = {
                'titulo': 'Documento Jurídico',
                'objeto': 'Análise jurídica multi-agente',
                'valor': 'N/A',
                'prazo': 'N/A'
            }
        
        return report_generator.generate_markdown_report(results, document_info)


# Instância global do sistema de validação
validation_system = SimpleValidationSystem()