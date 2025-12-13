"""
Orquestrador Multi-Agente Integrado
Combina agentes de processamento sequencial com validação multi-API
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.session = None
        self.engine = None
        self._setup_database()
        
        # APIs de validação disponíveis
        self.validation_apis = {
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
        
        # Ordem sequencial dos agentes de processamento
        self.processing_agents = [
            'Extrator',
            'Classificador', 
            'Analisador',
            'Sintetizador',
            'Formatador'
        ]
        
        # Áreas jurídicas padronizadas
        self.areas_juridicas = {
            'direito_civil': 'Direito Civil',
            'direito_penal': 'Direito Penal', 
            'direito_trabalhista': 'Direito Trabalhista',
            'direito_empresarial': 'Direito Empresarial',
            'direito_consumidor': 'Direito do Consumidor',
            'direito_familia': 'Direito de Família',
            'direito_administrativo': 'Direito Administrativo',
            'direito_constitucional': 'Direito Constitucional',
            'direito_tributario': 'Direito Tributário',
            'direito_imobiliario': 'Direito Imobiliário',
            'direito_securitario': 'Direito Securitário',
            'negociacao_conflitos': 'Negociação e Conflitos',
            'direito_bancario': 'Direito Bancário',
            'direito_previdenciario': 'Direito Previdenciário',
            'direito_ambiental': 'Direito Ambiental',
            'direito_digital': 'Direito Digital'
        }
    
    def _setup_database(self):
        """Configura conexão com banco de dados"""
        try:
            if self.database_url:
                self.engine = create_engine(self.database_url, pool_pre_ping=True)
                Session = sessionmaker(bind=self.engine)
                self.session = Session()
                logger.info("✅ Conexão com banco de dados estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """Busca configuração do agente no banco de dados"""
        try:
            query = text("""
                SELECT nome, classe, template_prompt, modelo_ai, temperatura, top_p, max_tokens, capacidades
                FROM agente_juridico 
                WHERE nome = :nome AND ativo = true
            """)
            result = self.session.execute(query, {'nome': agent_name}).fetchone()
            
            if result:
                capacidades = result[7]
                if isinstance(capacidades, str):
                    try:
                        capacidades = json.loads(capacidades)
                    except:
                        capacidades = {}
                
                return {
                    'nome': result[0],
                    'classe': result[1],
                    'template_prompt': result[2],
                    'modelo_ai': result[3],
                    'temperatura': result[4],
                    'top_p': result[5],
                    'max_tokens': result[6],
                    'capacidades': capacidades
                }
        except Exception as e:
            logger.error(f"❌ Erro ao buscar agente {agent_name}: {e}")
        return None
    
    def process_document_complete(self, texto: str, area_juridica: str = 'empresarial') -> Dict[str, Any]:
        """
        Processamento completo do documento:
        1. Fluxo sequencial dos agentes de processamento
        2. Validação multi-API paralela
        3. Consolidação final dos resultados
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Iniciando análise completa para documento (ID: {analysis_id})")
        
        # Fase 1: Processamento sequencial dos agentes
        processing_results = self._run_processing_pipeline(texto, area_juridica)
        
        # Fase 2: Validação multi-API dos resultados
        validation_results = self._run_validation_pipeline(texto, area_juridica, processing_results)
        
        # Fase 3: Consolidação final
        final_consolidation = self._generate_final_consolidation(
            processing_results, validation_results, area_juridica
        )
        
        processing_time = time.time() - start_time
        
        # Salvar resultado no banco
        result_data = {
            'id': analysis_id,
            'texto_original': texto,
            'area_juridica': area_juridica,
            'processamento_agentes': processing_results,
            'validacao_apis': validation_results,
            'consolidacao_final': final_consolidation,
            'total_processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        self._save_analysis_result(result_data)
        
        return result_data
    
    def _run_processing_pipeline(self, texto: str, area_juridica: str) -> Dict[str, Any]:
        """Executa pipeline sequencial dos agentes de processamento"""
        logger.info("🔄 Iniciando pipeline de processamento sequencial")
        
        pipeline_results = {}
        current_input = texto
        
        for agent_name in self.processing_agents:
            logger.info(f"⚙️ Executando agente: {agent_name}")
            
            agent_config = self.get_agent_config(agent_name)
            if not agent_config:
                logger.warning(f"⚠️ Configuração não encontrada para agente: {agent_name}")
                continue
            
            # Executar agente
            agent_result = self._execute_processing_agent(
                agent_config, current_input, area_juridica, pipeline_results
            )
            
            if agent_result:
                pipeline_results[agent_name.lower()] = agent_result
                # Para alguns agentes, o resultado se torna input do próximo
                if agent_name in ['Extrator', 'Classificador', 'Analisador']:
                    current_input = agent_result.get('resultado', current_input)
                logger.info(f"✅ Agente {agent_name} processado com sucesso")
            else:
                logger.error(f"❌ Falha no agente {agent_name}")
        
        return pipeline_results
    
    def _execute_processing_agent(self, agent_config: Dict, input_text: str, 
                                area_juridica: str, previous_results: Dict) -> Optional[Dict]:
        """Executa um agente de processamento específico"""
        try:
            # Preparar prompt baseado no tipo de agente
            prompt = self._prepare_agent_prompt(agent_config, input_text, area_juridica, previous_results)
            
            # Executar via API (usando OpenAI como padrão para agentes de processamento)
            result = self._call_openai_agent(prompt, agent_config)
            
            if result:
                return {
                    'agente': agent_config['nome'],
                    'tipo': agent_config['capacidades'].get('tipo', 'processamento'),
                    'resultado': result,
                    'timestamp': datetime.now().isoformat(),
                    'configuracao': {
                        'modelo': agent_config['modelo_ai'],
                        'temperatura': agent_config['temperatura']
                    }
                }
        except Exception as e:
            logger.error(f"❌ Erro ao executar agente {agent_config['nome']}: {e}")
        return None
    
    def _prepare_agent_prompt(self, agent_config: Dict, input_text: str, 
                            area_juridica: str, previous_results: Dict) -> str:
        """Prepara prompt específico para cada tipo de agente"""
        template = agent_config['template_prompt']
        
        # Obter nome da área jurídica padronizada
        area_nome = self.areas_juridicas.get(area_juridica, area_juridica)
        
        # Substituições básicas
        prompt = template.replace('{input}', input_text)
        prompt = prompt.replace('{area_juridica}', area_nome)
        prompt = prompt.replace('{area_id}', area_juridica)
        
        # Contexto específico por área jurídica
        contexto_area = self._get_area_context(area_juridica)
        prompt = prompt.replace('{contexto_area}', contexto_area)
        
        # Para agentes que dependem de resultados anteriores (Sintetizador, Formatador)
        if agent_config['nome'] == 'Sintetizador':
            extracao = previous_results.get('extrator', {}).get('resultado', 'Não disponível')
            classificacao = previous_results.get('classificador', {}).get('resultado', 'Não disponível') 
            analise = previous_results.get('analisador', {}).get('resultado', 'Não disponível')
            
            prompt = prompt.replace('{extracao}', extracao)
            prompt = prompt.replace('{classificacao}', classificacao)
            prompt = prompt.replace('{analise}', analise)
        
        elif agent_config['nome'] == 'Formatador':
            sintese = previous_results.get('sintetizador', {}).get('resultado', 'Não disponível')
            prompt = prompt.replace('{sintese}', sintese)
            prompt = prompt.replace('{formato_saida}', 'markdown')
        
        return prompt
    
    def _get_area_context(self, area_juridica: str) -> str:
        """Retorna contexto específico para cada área jurídica"""
        contextos = {
            'direito_civil': 'Foque em contratos, responsabilidade civil, direitos reais e obrigações.',
            'direito_penal': 'Analise tipificação penal, elementos do crime, causas excludentes e penas.',
            'direito_trabalhista': 'Considere CLT, direitos trabalhistas, relações de emprego e previdenciários.',
            'direito_empresarial': 'Avalie aspectos societários, contratos empresariais e compliance.',
            'direito_consumidor': 'Aplique CDC, direitos do consumidor e relações de consumo.',
            'direito_familia': 'Analise união estável, divórcio, guarda, alimentos e sucessões.',
            'direito_administrativo': 'Considere atos administrativos, licitações e serviço público.',
            'direito_constitucional': 'Foque em direitos fundamentais, organização do Estado e controle de constitucionalidade.',
            'direito_tributario': 'Analise impostos, tributos, planejamento tributário e obrigações fiscais.',
            'direito_imobiliario': 'Considere registro de imóveis, contratos imobiliários e direitos reais.',
            'direito_securitario': 'Avalie contratos de seguro, sinistros e regulamentação SUSEP.',
            'negociacao_conflitos': 'Foque em mediação, arbitragem e métodos alternativos de resolução.',
            'direito_bancario': 'Analise contratos bancários, Sistema Financeiro Nacional e crédito.',
            'direito_previdenciario': 'Considere benefícios INSS, aposentadorias e regime previdenciário.',
            'direito_ambiental': 'Avalie licenciamento ambiental, crimes ambientais e sustentabilidade.',
            'direito_digital': 'Analise LGPD, crimes cibernéticos e proteção de dados.'
        }
        return contextos.get(area_juridica, 'Analise conforme a legislação brasileira aplicável.')
    
    def _call_openai_agent(self, prompt: str, agent_config: Dict) -> Optional[str]:
        """Chama OpenAI para execução do agente"""
        try:
            import openai
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return None
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=agent_config.get('modelo_ai', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": f"Você é o agente {agent_config['nome']} especializado em análise jurídica."},
                    {"role": "user", "content": prompt}
                ],
                temperature=agent_config.get('temperatura', 0.3),
                top_p=agent_config.get('top_p', 0.9),
                max_tokens=agent_config.get('max_tokens', 2000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Erro na chamada OpenAI: {e}")
            return None
    
    def _run_validation_pipeline(self, texto: str, area_juridica: str, 
                               processing_results: Dict) -> List[Dict]:
        """Executa validação multi-API em paralelo"""
        logger.info("🔍 Iniciando validação multi-API")
        
        # Usar o resultado da síntese como base para validação
        synthesis_result = processing_results.get('sintetizador', {}).get('resultado', texto)
        
        validation_results = []
        
        # Executar APIs de validação em paralelo (simplificado para agora)
        for api_key, config in self.validation_apis.items():
            if config['active']:
                logger.info(f"🔍 Validando com {config['name']}")
                
                validation = self._execute_validation_api(api_key, config, synthesis_result, area_juridica)
                if validation:
                    validation_results.append(validation)
        
        return validation_results
    
    def _execute_validation_api(self, api_key: str, config: Dict, 
                              text: str, area_juridica: str) -> Optional[Dict]:
        """Executa validação com uma API específica"""
        try:
            # Obter nome e contexto da área jurídica
            area_nome = self.areas_juridicas.get(area_juridica, area_juridica)
            contexto_area = self._get_area_context(area_juridica)
            
            # Prompt de validação especializado
            validation_prompt = f"""
            Como especialista em {area_nome}, realize uma validação crítica da análise jurídica apresentada.

            CONTEXTO DA ÁREA: {contexto_area}

            ANÁLISE A VALIDAR:
            {text}

            Forneça uma validação estruturada com:
            1. VALIDAÇÃO TÉCNICA: Precisão jurídica e conformidade legal específica para {area_nome}
            2. PONTOS FORTES: Aspectos bem fundamentados da análise
            3. PONTOS DE ATENÇÃO: Lacunas ou inconsistências identificadas
            4. RECOMENDAÇÕES: Sugestões de melhorias específicas para {area_nome}
            5. AVALIAÇÃO GERAL: Nota de 1 a 10 para qualidade da análise

            Seja objetivo, tecnicamente rigoroso e focado na especialidade de {area_nome}.
            """
            
            result = self._call_validation_api(api_key, validation_prompt)
            
            if result:
                return {
                    'api': config['name'],
                    'especialidade': config['specialty'],
                    'validacao': result,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Erro na validação com {api_key}: {e}")
        return None
    
    def _call_validation_api(self, api_key: str, prompt: str) -> Optional[str]:
        """Chama API específica para validação"""
        try:
            if api_key == 'openai':
                import openai
                client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                return response.choices[0].message.content
            
            elif api_key == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            # Adicionar outras APIs conforme necessário
            
        except Exception as e:
            logger.error(f"❌ Erro na API {api_key}: {e}")
        return None
    
    def _generate_final_consolidation(self, processing_results: Dict, 
                                    validation_results: List[Dict], area_juridica: str) -> str:
        """Gera consolidação final integrando processamento e validação"""
        
        consolidation_prompt = f"""
        Como especialista em {area_juridica}, consolide os resultados do processamento multi-agente e das validações realizadas:

        RESULTADOS DO PROCESSAMENTO:
        """
        
        # Adicionar resultados de cada agente
        for agent_name, result in processing_results.items():
            consolidation_prompt += f"\n\n{agent_name.upper()}:\n{result.get('resultado', 'N/A')}"
        
        consolidation_prompt += "\n\nVALIDAÇÕES REALIZADAS:"
        
        # Adicionar validações
        for validation in validation_results:
            consolidation_prompt += f"\n\n{validation['api']} ({validation['especialidade']}):\n{validation['validacao']}"
        
        consolidation_prompt += """

        TAREFA: Elabore uma consolidação executiva final que:
        1. Integre harmoniosamente todos os resultados
        2. Destaque consensos e divergências entre validações
        3. Forneça recomendações finais baseadas no conjunto completo de análises
        4. Mantenha rigor técnico e precisão jurídica

        Formato: Markdown estruturado e profissional.
        """
        
        # Usar OpenAI para consolidação final
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": consolidation_prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Erro na consolidação final: {e}")
            return "Erro na geração da consolidação final."
    
    def _save_analysis_result(self, result_data: Dict):
        """Salva resultado da análise no banco de dados"""
        try:
            insert_query = text("""
                INSERT INTO resultado_analise_multi_agente (
                    id, texto_original, area_juridica, resultado_json, 
                    total_apis, processing_time, created_at
                ) VALUES (
                    :id, :texto_original, :area_juridica, :resultado_json,
                    :total_apis, :processing_time, CURRENT_TIMESTAMP
                )
            """)
            
            self.session.execute(insert_query, {
                'id': result_data['id'],
                'texto_original': result_data['texto_original'],
                'area_juridica': result_data['area_juridica'],
                'resultado_json': json.dumps(result_data, ensure_ascii=False),
                'total_apis': len(result_data.get('validacao_apis', [])),
                'processing_time': result_data['total_processing_time']
            })
            
            self.session.commit()
            logger.info(f"✅ Resultado salvo no banco com ID: {result_data['id']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no banco: {e}")
            self.session.rollback()
    
    def process_document_with_selected_agents(self, texto: str, area_juridica: str, agentes_ids: List[str], usar_validacao: bool = True) -> Dict[str, Any]:
        """
        Processa documento com agentes selecionados manualmente
        """
        try:
            start_time = time.time()
            result_id = str(uuid.uuid4())
            
            logger.info(f"🎯 Iniciando processamento com {len(agentes_ids)} agentes selecionados")
            
            # Buscar dados dos agentes selecionados
            agentes_info = self._get_agents_info(agentes_ids)
            if not agentes_info:
                return {'status': 'error', 'message': 'Nenhum agente válido encontrado'}
            
            # Organizar agentes por tipo
            agentes_processamento = []
            agentes_especialistas = []
            
            for agente in agentes_info:
                if agente['categoria_id'] == 17:  # Agentes de processamento
                    agentes_processamento.append(agente)
                else:  # Especialistas
                    agentes_especialistas.append(agente)
            
            # Executar processamento sequencial
            resultados_processamento = {}
            resultados_especialistas = []
            
            # 1. Agentes de processamento primeiro
            for agente in agentes_processamento:
                logger.info(f"🔄 Processando com {agente['nome']}")
                resultado = self._process_with_agent(texto, agente, area_juridica)
                if resultado:
                    resultados_processamento[agente['nome']] = resultado
            
            # 2. Agentes especialistas
            for agente in agentes_especialistas:
                logger.info(f"👨‍⚖️ Analisando com {agente['nome']}")
                resultado = self._process_with_agent(texto, agente, area_juridica)
                if resultado:
                    resultados_especialistas.append({
                        'agente': agente['nome'],
                        'area': self._get_categoria_nome(agente['categoria_id']),
                        'analise': resultado,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # 3. Validação multi-API (se solicitada)
            validacao_apis = []
            if usar_validacao:
                logger.info("🔍 Executando validação multi-API")
                validacao_apis = self._execute_api_validation(texto, area_juridica)
            
            # 4. Consolidação final
            consolidacao_final = self._generate_final_consolidation(
                texto, 
                resultados_processamento, 
                resultados_especialistas, 
                validacao_apis
            )
            
            # Preparar resultado final
            total_time = time.time() - start_time
            
            result_data = {
                'id': result_id,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'area_juridica': area_juridica,
                'tipo_processamento': 'agentes_selecionados',
                'agentes_utilizados': {
                    'processamento': [a['nome'] for a in agentes_processamento],
                    'especialistas': [a['nome'] for a in agentes_especialistas]
                },
                'processamento_agentes': resultados_processamento,
                'especialistas_analises': resultados_especialistas,
                'validacao_apis': validacao_apis,
                'consolidacao_final': consolidacao_final,
                'total_processing_time': round(total_time, 2),
                'total_agentes': len(agentes_ids),
                'metricas': {
                    'agentes_processamento': len(agentes_processamento),
                    'agentes_especialistas': len(agentes_especialistas),
                    'apis_validacao': len(validacao_apis),
                    'tempo_total': round(total_time, 2)
                }
            }
            
            # Salvar no banco de dados
            self._save_result_to_database(result_data)
            
            logger.info(f"✅ Processamento com agentes selecionados concluído em {total_time:.2f}s")
            return result_data
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento com agentes selecionados: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_agents_info(self, agentes_ids: List[str]) -> List[Dict[str, Any]]:
        """Busca informações dos agentes selecionados"""
        try:
            if not agentes_ids:
                return []
            
            # Converter IDs para inteiros
            ids_int = [int(id_str) for id_str in agentes_ids]
            ids_placeholder = ','.join(['%s'] * len(ids_int))
            
            query = text(f"""
                SELECT id, nome, classe, categoria_id, capacidades, template_prompt
                FROM agente_juridico 
                WHERE id IN ({ids_placeholder}) AND ativo = true
                ORDER BY categoria_id, nome
            """)
            
            result = self.session.execute(query, ids_int).fetchall()
            
            agentes = []
            for row in result:
                agentes.append({
                    'id': row[0],
                    'nome': row[1],
                    'classe': row[2],
                    'categoria_id': row[3],
                    'capacidades': row[4] if row[4] else {},
                    'template_prompt': row[5] or ''
                })
            
            logger.info(f"📋 Encontrados {len(agentes)} agentes válidos")
            return agentes
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar agentes: {e}")
            return []
    
    def _get_categoria_nome(self, categoria_id: int) -> str:
        """Retorna nome da categoria por ID"""
        categorias = {
            1: "Direito Bancário",
            2: "Direito Securitário", 
            3: "Direito Trabalhista",
            4: "Direito Previdenciário",
            5: "Direito Tributário",
            6: "Direito Imobiliário",
            7: "Direito Digital",
            8: "Direito Empresarial",
            9: "Direito Criminal",
            10: "Direito do Consumidor",
            11: "Recuperação de Crédito",
            12: "Direito Agrário",
            13: "Negociação e Conflitos",
            14: "Análise de Riscos",
            15: "Direito Ambiental",
            17: "Agentes de Processamento"
        }
        return categorias.get(categoria_id, f"Categoria {categoria_id}")

    def __del__(self):
        """Cleanup da conexão com banco"""
        if self.session:
            self.session.close()