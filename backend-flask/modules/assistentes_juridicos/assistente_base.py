"""
Assistente Juridico Base com Lazy Loading
Versão otimizada que evita erros de inicialização
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Importar psycopg2 para conexão com banco
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Usar sistema de lazy loading
try:
    from utils.lazy_imports import create_lazy_api_client, safe_import
    LAZY_IMPORTS_AVAILABLE = True
except ImportError:
    LAZY_IMPORTS_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Reduzir verbosidade

class AssistenteJuridicoBase:
    """Classe base corrigida para assistentes jurídicos"""
    
    def __init__(self, area_juridica: str):
        self.area_juridica = area_juridica
        self.tabela_embeddings = f"embeddings_{area_juridica}"
        self.configurar_apis_lazy()
        self.configurar_qdrant_lazy()
        
    def configurar_apis_lazy(self):
        """Configura APIs com lazy loading - evita erros de inicialização"""
        if LAZY_IMPORTS_AVAILABLE:
            # Usar lazy clients que inicializam apenas quando necessário
            self.openai_client = create_lazy_api_client('openai', self.area_juridica)
            self.anthropic_client = create_lazy_api_client('anthropic', self.area_juridica)  
            self.gemini_client = create_lazy_api_client('gemini', self.area_juridica)
            
            # Configurar cliente Grok X.AI
            try:
                xai_api_key = os.environ.get('XAI_API_KEY')
                if xai_api_key:
                    import requests
                    self.grok_client = {
                        'api_key': xai_api_key,
                        'endpoint': 'https://api.x.ai/v1/chat/completions',
                        'session': requests.Session()
                    }
                    logger.info(f"✅ Grok X.AI client configurado para {self.area_juridica}")
                else:
                    self.grok_client = None
                    logger.warning("⚠️ XAI_API_KEY não encontrada - Grok X.AI não disponível")
            except Exception as e:
                logger.error(f"❌ Erro configurando Grok X.AI: {e}")
                self.grok_client = None
            
            # Validar inicialização básica
            try:
                if hasattr(self.openai_client, 'get_client'):
                    test_client = self.openai_client.get_client()
                    if test_client:
                        logger.info(f"✅ OpenAI lazy client configurado para {self.area_juridica}")
                    else:
                        logger.warning(f"⚠️ OpenAI lazy client não inicializou para {self.area_juridica}")
            except Exception as e:
                logger.error(f"❌ Erro testando OpenAI lazy client: {e}")
        else:
            # Fallback para método tradicional com proteções
            self.configurar_apis_fallback()
    
    def configurar_apis_fallback(self):
        """Método fallback com proteções extras"""
        self.openai_client = None
        self.anthropic_client = None 
        self.gemini_client = None
        
        # OpenAI com proteção
        try:
            if os.environ.get('OPENAI_API_KEY'):
                import openai
                self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        except Exception:
            pass
            
        # Anthropic com proteção  
        try:
            if os.environ.get('ANTHROPIC_API_KEY'):
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        except Exception:
            pass
            
        # Gemini com proteção - usar GOOGLE_API_KEY que já existe
        try:
            if os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY'):
                import google.generativeai as genai
                # Priorizar GOOGLE_API_KEY que já existe no sistema
                api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info(f"✅ Gemini configurado com chave disponível para {self.area_juridica}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar Gemini para {self.area_juridica}: {e}")
            pass
    
    def configurar_qdrant_lazy(self):
        """Configura Qdrant com lazy loading"""
        if LAZY_IMPORTS_AVAILABLE:
            self.qdrant_client = create_lazy_api_client('qdrant', self.area_juridica)
        else:
            self.configurar_qdrant_fallback()
            
        # Nome da coleção baseado na área jurídica
        self.qdrant_collection = f"juridico_{self.area_juridica}"
    
    def configurar_qdrant_fallback(self):
        """Método fallback para Qdrant"""
        self.qdrant_client = None
        try:
            qdrant_url = os.getenv('QDRANT_URL')
            qdrant_api_key = os.getenv('QDRANT_API_KEY')
            
            if qdrant_url and qdrant_api_key:
                from qdrant_client import QdrantClient
                self.qdrant_client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    timeout=30
                )
        except Exception:
            pass
    
    def _conectar_db(self):
        """Conecta ao banco usando psycopg2 diretamente"""
        if not PSYCOPG2_AVAILABLE:
            logger.error("psycopg2 não está disponível")
            return None
            
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logger.error("DATABASE_URL não encontrada")
                return None
            return psycopg2.connect(database_url)
        except Exception as e:
            logger.error(f"Erro na conexão com banco: {e}")
            return None
    
    def buscar_documentos_relevantes(self, query: str, limit: int = 5) -> list:
        """Busca documentos usando arquitetura vetorial híbrida PostgreSQL + Qdrant"""
        try:
            # Busca paralela em ambas as fontes
            documentos_postgres = self._buscar_postgresql(query, limit)
            documentos_qdrant = self._buscar_qdrant(query, limit)
            
            # Combina e ranqueia resultados
            documentos_combinados = self._combinar_resultados(documentos_postgres, documentos_qdrant, limit)
            
            logger.info(f"Busca híbrida por '{query}': {len(documentos_postgres)} PostgreSQL + {len(documentos_qdrant)} Qdrant = {len(documentos_combinados)} final")
            return documentos_combinados
            
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            # Fallback para PostgreSQL apenas
            return self._buscar_postgresql(query, limit)
    
    def _buscar_postgresql(self, query: str, limit: int = 5) -> list:
        """Busca documentos no PostgreSQL usando as tabelas existentes"""
        try:
            conn = self._conectar_db()
            if not conn:
                logger.warning("❌ Conexão com banco não estabelecida")
                return []
            
            cursor = conn.cursor()
            resultados = []
            
            # 1. Buscar DIRETAMENTE em processo_juridico (prioridade máxima)
            # CORREÇÃO CRÍTICA: Filtrar SEMPRE pela área jurídica correta
            try:
                cursor.execute("""
                    SELECT numero_processo_cnj, resumo_dos_fatos, status, area_juridica, data_registro, id,
                           tema, valor_da_causa, comarca, instancia
                    FROM processo_juridico 
                    WHERE area_juridica = %s
                    AND (resumo_dos_fatos ILIKE %s OR numero_processo_cnj ILIKE %s OR tema ILIKE %s)
                    ORDER BY data_registro DESC 
                    LIMIT %s
                """, (self.area_juridica, f'%{query}%', f'%{query}%', f'%{query}%', limit))
                
                for row in cursor.fetchall():
                    valor_formatado = f"R$ {row[7]:,.2f}" if row[7] else "Valor não informado"
                    conteudo_processo = f"""
Processo: {row[0] or 'N/I'}
Área: {row[3]} | Status: {row[2] or 'Em andamento'}
Comarca: {row[8] or 'N/I'} | Instância: {row[9] or 'N/I'}
Valor da Causa: {valor_formatado}
Tema: {row[6] or 'N/I'}
Resumo dos Fatos: {row[1] or 'Não informado'}
                    """.strip()
                    
                    resultados.append({
                        'id': f"processo_{row[5]}",
                        'conteudo': conteudo_processo,
                        'referencia': f"Processo {row[0] or 'N/I'}",
                        'titulo': f"Processo {row[0]} - {row[6] or 'Processo Jurídico'}",
                        'area_juridica': row[3] or '',
                        'status': row[2] or '',
                        'numero_processo': row[0] or '',
                        'valor_causa': row[7],
                        'relevancia': self._calcular_relevancia_texto(query, conteudo_processo),
                        'fonte': 'PostgreSQL-processos',
                        'metadata': {
                            'fonte': 'processo_juridico', 
                            'processo_id': row[5],
                            'tribunal': row[8],
                            'instancia': row[9],
                            'data_inicio': str(row[4]) if row[4] else None
                        }
                    })
                    
                logger.info(f"✅ Encontrados {len(resultados)} processos jurídicos")
                    
            except Exception as e:
                logger.error(f"❌ Erro buscando processos: {e}")
                
            # 2. Buscar em template_juridico como complemento
            # CORREÇÃO CRÍTICA: Filtrar SEMPRE pela área jurídica correta
            if len(resultados) < limit:
                try:
                    cursor.execute("""
                        SELECT conteudo, nome, area_juridica, categoria, created_at, id
                        FROM template_juridico 
                        WHERE area_juridica = %s
                        AND (conteudo ILIKE %s OR nome ILIKE %s)
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (self.area_juridica, f'%{query}%', f'%{query}%', limit - len(resultados)))
                    
                    for row in cursor.fetchall():
                        resultados.append({
                            'id': f"template_{row[5]}",
                            'conteudo': row[0] or '',
                            'referencia': f"Template: {row[1]}",
                            'titulo': row[1] or 'Template Jurídico',
                            'area_juridica': row[2] or '',
                            'categoria': row[3] or '',
                            'relevancia': self._calcular_relevancia_texto(query, row[0] or ''),
                            'fonte': 'PostgreSQL-templates',
                            'metadata': {'fonte': 'template_juridico', 'template_id': row[5]}
                        })
                        
                    logger.info(f"✅ Encontrados {len([r for r in resultados if r['fonte'] == 'PostgreSQL-templates'])} templates complementares")
                        
                except Exception as e:
                    logger.error(f"❌ Erro buscando templates: {e}")
            

            
            cursor.close()
            conn.close()
            
            logger.info(f"📊 Busca PostgreSQL finalizada: {len(resultados)} resultados para '{query}'")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na busca PostgreSQL: {e}")
            return []
    
    def _buscar_qdrant(self, query: str, limit: int = 5) -> list:
        """Busca documentos no Qdrant Cloud"""
        try:
            if not self.qdrant_client:
                return []
            
            # Gera embedding da query
            embedding = self._gerar_embedding(query)
            if not embedding:
                return []
            
            # Busca por similaridade no Qdrant usando query_points
            search_result = self.qdrant_client.query_points(
                collection_name=self.qdrant_collection,
                query=embedding,
                limit=limit
            ).points
            
            resultados = []
            for hit in search_result:
                payload = hit.payload
                resultados.append({
                    'id': f"qd_{hit.id}",
                    'conteudo': payload.get('conteudo', payload.get('text', ''))[:800],
                    'referencia': payload.get('referencia', payload.get('source', '')),
                    'titulo': payload.get('titulo', payload.get('title', 'Documento Qdrant')),
                    'artigo_numero': payload.get('artigo_numero', payload.get('article', '')),
                    'relevancia': float(hit.score),
                    'fonte': 'Qdrant Cloud',
                    'metadata': {
                        'fonte': 'qdrant_cloud',
                        'score': hit.score,
                        'collection': self.qdrant_collection
                    }
                })
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro na busca Qdrant: {e}")
            return []
    
    def _gerar_embedding(self, texto: str) -> list:
        """Gera embedding usando OpenAI"""
        try:
            if not self.openai_client:
                return []
                
            response = self.openai_client.embeddings.create(
                input=texto,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embedding: {e}")
            return []
    
    def _combinar_resultados(self, postgres_docs: list, qdrant_docs: list, limit: int) -> list:
        """Combina e ranqueia resultados de ambas as fontes"""
        try:
            # Normaliza scores para [0,1]
            for doc in postgres_docs:
                doc['score_normalizado'] = min(doc['relevancia'], 1.0)
            
            for doc in qdrant_docs:
                doc['score_normalizado'] = doc['relevancia']
            
            # Combina listas
            todos_documentos = postgres_docs + qdrant_docs
            
            # Remove duplicatas baseado em conteúdo similar
            documentos_unicos = self._remover_duplicatas(todos_documentos)
            
            # Ordena por score combinado
            documentos_unicos.sort(key=lambda x: x['score_normalizado'], reverse=True)
            
            return documentos_unicos[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erro ao combinar resultados: {e}")
            return (postgres_docs + qdrant_docs)[:limit]
    
    def _calcular_relevancia_texto(self, query: str, texto: str) -> float:
        """Calcula relevância baseada em correspondência de texto"""
        try:
            if not query or not texto:
                return 0.0
            
            query_lower = query.lower()
            texto_lower = texto.lower()
            
            # Contagem de palavras da query no texto
            palavras_query = query_lower.split()
            correspondencias = sum(1 for palavra in palavras_query if palavra in texto_lower)
            
            # Score baseado na proporção de palavras encontradas
            relevancia = correspondencias / len(palavras_query) if palavras_query else 0.0
            
            return min(relevancia, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de relevância: {e}")
            return 0.0
    
    def _remover_duplicatas(self, documentos: list) -> list:
        """Remove documentos duplicados baseado em similaridade de conteúdo"""
        try:
            if len(documentos) <= 1:
                return documentos
            
            documentos_unicos = []
            
            for doc in documentos:
                is_duplicate = False
                for doc_unico in documentos_unicos:
                    # Verifica similaridade de título e conteúdo
                    if (self._similaridade_texto(doc['titulo'], doc_unico['titulo']) > 0.8 or
                        self._similaridade_texto(doc['conteudo'][:200], doc_unico['conteudo'][:200]) > 0.9):
                        is_duplicate = True
                        # Mantém o documento com melhor score
                        if doc['score_normalizado'] > doc_unico['score_normalizado']:
                            documentos_unicos.remove(doc_unico)
                            documentos_unicos.append(doc)
                        break
                
                if not is_duplicate:
                    documentos_unicos.append(doc)
            
            return documentos_unicos
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover duplicatas: {e}")
            return documentos
    
    def _similaridade_texto(self, texto1: str, texto2: str) -> float:
        """Calcula similaridade básica entre dois textos"""
        try:
            if not texto1 or not texto2:
                return 0.0
            
            # Converte para minúsculas e divide em palavras
            palavras1 = set(texto1.lower().split())
            palavras2 = set(texto2.lower().split())
            
            # Jaccard similarity
            intersecao = len(palavras1.intersection(palavras2))
            uniao = len(palavras1.union(palavras2))
            
            return intersecao / uniao if uniao > 0 else 0.0
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de similaridade: {e}")
            return 0.0
    
    def _get_persona_texto(self, personalidade: str, tom: str) -> str:
        """Gera texto de persona baseado na personalidade e tom selecionados"""
        personalidades = {
            'advogado': 'Você é um(a) advogado(a) experiente em conversa técnica com colegas.',
            'juiz': 'Você é um(a) magistrado(a) experiente fornecendo análise técnica imparcial.',
            'professor': 'Você é um(a) professor(a) acadêmico(a) de Direito em discussão técnica.',
            'promotor': 'Você é um(a) promotor(a) do Ministério Público em análise técnica especializada.'
        }
        
        tons = {
            'objetivo': 'Seja direto e objetivo nas suas colocações técnicas.',
            'sistematico': 'Estruture sua análise de forma sistemática e organizada.',
            'natural': 'Use linguagem técnica mas fluida e conversacional.'
        }
        
        persona_base = personalidades.get(personalidade, personalidades['advogado'])
        tom_texto = tons.get(tom, tons['sistematico'])
        
        return f"{persona_base} {tom_texto}"
    
    def processar_com_ia(self, pergunta: str, documentos: list, modelo: str = "openai", personalidade: str = "advogado", tom: str = "sistematico", temperatura: float = 0.3, max_tokens: int = 2000) -> str:
        """Processa pergunta com IA usando documentos encontrados"""
        try:
            # Preparar contexto com informações específicas dos processos
            contexto_docs = []
            processos_encontrados = []
            
            for doc in documentos[:3]:
                if doc.get('fonte') == 'PostgreSQL-processos':
                    processos_encontrados.append({
                        'numero': doc.get('numero_processo', 'N/I'),
                        'status': doc.get('status', 'N/I'),
                        'valor': doc.get('valor_causa', 0),
                        'tribunal': doc.get('metadata', {}).get('tribunal', 'N/I')
                    })
                contexto_docs.append(doc.get('conteudo', '')[:500])
            
            contexto = "\n\n".join(contexto_docs)
            
            # Verificar se há documentos disponíveis
            if documentos and contexto.strip():
                # Prompt específico se há processos jurídicos
                if processos_encontrados:
                    info_processos = "\n".join([
                        f"- Processo {p['numero']}: Status {p['status']}, Tribunal: {p['tribunal']}"
                        for p in processos_encontrados
                    ])
                    
                    # Ajustar o prompt com base na personalidade e tom
                    persona_texto = self._get_persona_texto(personalidade, tom)
                    
                    prompt = f"""{persona_texto} Especialista técnico em {self.area_juridica.replace('_', ' ').title()} em reunião técnica com colegas. A questão apresentada é:

"{pergunta}"

Base empírica disponível - processos do escritório:
{info_processos}

Análise dos dados processuais:
{contexto}

Forneça análise técnica especializada considerando: precedentes identificados nos casos, fundamentação legal aplicável, estratégia processual recomendada, e prognóstico baseado nos padrões observados. Use terminologia jurídica adequada para profissionais da área."""
                else:
                    # Ajustar o prompt com base na personalidade e tom
                    persona_texto = self._get_persona_texto(personalidade, tom)
                    
                    prompt = f"""{persona_texto} Como especialista em {self.area_juridica.replace('_', ' ').title()}, analise tecnicamente a questão:

"{pergunta}"

Referências doutrinárias e jurisprudenciais disponíveis:
{contexto}

Elabore parecer técnico fundamentado, citando dispositivos legais específicos, posicionamento jurisprudencial dominante quando aplicável, e considerações práticas para a atuação advocatícia. Mantenha rigor técnico adequado para profissionais do direito."""
            else:
                # Ajustar o prompt com base na personalidade e tom
                persona_texto = self._get_persona_texto(personalidade, tom)
                
                prompt = f"""{persona_texto} Como especialista em {self.area_juridica.replace('_', ' ').title()}, forneça análise técnica sobre:

"{pergunta}"

Estruture resposta considerando: fundamentação legal específica, interpretação doutrinária consolidada, entendimento jurisprudencial atual, e implicações práticas processuais. Utilize terminologia jurídica precisa e cite dispositivos legais aplicáveis. Se houver controvérsias doutrinárias ou jurisprudenciais, apresente as correntes e seus respectivos fundamentos."""
            
            # Tentar APIs disponíveis com modelo dinâmico
            if self.openai_client and (modelo.startswith("gpt") or modelo.startswith("o1")):
                try:
                    # Verificar se o cliente está funcionando
                    if not hasattr(self.openai_client, 'chat'):
                        logger.error(f"❌ Cliente OpenAI não tem atributo 'chat', forçando reinicialização")
                        # Forçar reinicialização
                        self.openai_client._initialized = False
                        self.openai_client._error = None
                    
                    # Mapear modelo para OpenAI
                    openai_model = modelo
                    if modelo == "gpt-4.1":
                        openai_model = "gpt-4o"  # Fallback para modelo disponível
                    elif modelo == "gpt-4.1-mini":
                        openai_model = "gpt-4o-mini"
                    
                    logger.info(f"🤖 Usando OpenAI modelo: {modelo} → {openai_model}")
                    
                    # GPT-5 e modelos futuros usam max_completion_tokens, modelos anteriores usam max_tokens
                    if openai_model in ["gpt-5", "gpt-5-turbo"]:
                        # Limitar max_completion_tokens para GPT-5 (máximo 128000)
                        safe_max_tokens = min(max_tokens, 128000)
                        response = self.openai_client.chat.completions.create(
                            model=openai_model,
                            messages=[{"role": "user", "content": prompt}],
                            max_completion_tokens=safe_max_tokens,
                            temperature=temperatura
                        )
                    else:
                        # Limitar max_tokens para modelos OpenAI anteriores (máximo 16384)
                        safe_max_tokens = min(max_tokens, 16384)
                        response = self.openai_client.chat.completions.create(
                            model=openai_model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=safe_max_tokens,
                            temperature=temperatura
                        )
                    
                    resposta = response.choices[0].message.content
                    return f"[Processado com {modelo}]\n\n{resposta}"
                    
                except Exception as openai_error:
                    logger.error(f"❌ Erro específico OpenAI: {openai_error}")
                    # Tentar fallback direto
                    try:
                        import openai
                        api_key = os.environ.get('OPENAI_API_KEY')
                        if api_key:
                            logger.info("🔄 Usando cliente OpenAI direto como fallback")
                            # Inicialização simples e limpa
                            direct_client = openai.OpenAI(api_key=api_key)
                            # Limitar max_tokens para GPT-4o (máximo 16384)
                            safe_max_tokens = min(max_tokens, 16384)
                            response = direct_client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=safe_max_tokens,
                                temperature=temperatura
                            )
                            return f"[Fallback OpenAI]\n\n{response.choices[0].message.content}"
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback OpenAI também falhou: {fallback_error}")
                        # Continuar para próxima opção ao invés de falhar
                
            elif self.anthropic_client and modelo.startswith("claude"):
                # Usar modelo Anthropic selecionado com tratamento de erro
                try:
                    anthropic_model = modelo
                    if modelo == "claude-opus-4":
                        anthropic_model = "claude-3-opus-20240229"  # Fallback
                    elif modelo == "claude-sonnet-4":
                        anthropic_model = "claude-sonnet-4-20250514"  # Modelo Claude 4 Sonnet
                    elif modelo == "claude-3-7-sonnet":
                        anthropic_model = "claude-3-7-sonnet-20250219"  # Modelo Claude 3.7 Sonnet
                    elif modelo == "claude-sonnet-4-20250514":
                        anthropic_model = "claude-sonnet-4-20250514"  # Modelo completo Claude 4 Sonnet
                    elif modelo == "claude-3-7-sonnet-20250219":
                        anthropic_model = "claude-3-7-sonnet-20250219"  # Modelo completo Claude 3.7 Sonnet
                    
                    logger.info(f"🤖 Usando Anthropic modelo: {modelo} → {anthropic_model}")
                    # Limitar max_tokens para modelos Claude (máximo 64000)
                    safe_max_tokens = min(max_tokens, 64000)
                    
                    # Usar streaming para análises longas (prompt > 5000 caracteres)
                    if len(prompt) > 5000:
                        logger.info("📡 Usando streaming para análise longa")
                        response = self.anthropic_client.messages.create(
                            model=anthropic_model,
                            max_tokens=safe_max_tokens,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperatura,
                            stream=True,
                            timeout=300  # 5 minutos de timeout
                        )
                        # Coletar resposta do stream
                        resposta_completa = ""
                        for chunk in response:
                            if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                                resposta_completa += chunk.delta.text
                        response = type('obj', (object,), {'content': [type('obj', (object,), {'text': resposta_completa})]})()
                    else:
                        response = self.anthropic_client.messages.create(
                            model=anthropic_model,
                            max_tokens=safe_max_tokens,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperatura,
                            timeout=60  # 1 minuto para análises curtas
                        )
                    resposta = response.content[0].text
                    return f"[Processado com {modelo}]\n\n{resposta}"
                    
                except Exception as anthropic_error:
                    logger.warning(f"⚠️ Erro com Anthropic ({modelo}): {anthropic_error}")
                    # Fallback para OpenAI GPT-4o
                    if self.openai_client:
                        logger.info("🔄 Usando fallback OpenAI GPT-4o para modelo Anthropic")
                        try:
                            # Limitar max_tokens para GPT-4o (máximo 16384)
                            safe_max_tokens = min(max_tokens, 16384)
                            response = self.openai_client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=safe_max_tokens,
                                temperature=temperatura
                            )
                            resposta = response.choices[0].message.content
                            return f"[Fallback OpenAI para {modelo}]\n\n{resposta}"
                        except Exception as openai_fallback_error:
                            logger.error(f"❌ Fallback OpenAI também falhou: {openai_fallback_error}")
                            # Continuar para próxima opção
                    else:
                        logger.error("❌ OpenAI não disponível para fallback")
                
            elif self.gemini_client and modelo.startswith("gemini"):
                # Usar modelo Gemini selecionado
                logger.info(f"🤖 Usando Google Gemini modelo: {modelo}")
                response = self.gemini_client.generate_content(prompt)
                resposta = response.text
                return f"[Processado com {modelo}]\n\n{resposta}"
                
            elif self.grok_client and modelo.startswith("grok"):
                # Usar modelo Grok X.AI selecionado
                try:
                    import requests
                    import json
                    
                    # Mapear nomes dos modelos
                    grok_model = modelo
                    if modelo == "grok-2-vision-1212-us":
                        grok_model = "grok-2-vision-1212"  # US region
                    elif modelo == "grok-2-vision-1212-eu":
                        grok_model = "grok-2-vision-1212"  # EU region
                    
                    logger.info(f"🤖 Usando Grok X.AI modelo: {modelo} → {grok_model}")
                    
                    # Preparar payload para Grok API
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"Bearer {self.grok_client['api_key']}"
                    }
                    
                    # Limitar max_tokens baseado no modelo
                    if modelo in ['grok-4-fast-reasoning', 'grok-4-fast-non-reasoning']:
                        safe_max_tokens = min(max_tokens, 4000000)  # 4M tokens de saída
                    elif modelo in ['grok-4-latest', 'grok-4-0709', 'grok-code-fast-1']:
                        safe_max_tokens = min(max_tokens, 2000000)  # 2M tokens de saída
                    else:
                        safe_max_tokens = min(max_tokens, 65536)  # Limite padrão
                    
                    payload = {
                        'model': grok_model,
                        'messages': [
                            {
                                'role': 'system',
                                'content': f'Você é um assistente jurídico especializado em {self.area_juridica.replace("_", " ").title()}.'
                            },
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ],
                        'temperature': temperatura,
                        'max_tokens': safe_max_tokens,
                        'stream': False
                    }
                    
                    # Fazer requisição à API do Grok
                    response = requests.post(
                        self.grok_client['endpoint'],
                        headers=headers,
                        json=payload,
                        timeout=600  # 10 minutos para modelos de raciocínio
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        resposta = result['choices'][0]['message']['content']
                        return f"[Processado com {modelo}]\n\n{resposta}"
                    else:
                        logger.error(f"❌ Erro na API Grok: {response.status_code} - {response.text}")
                        raise Exception(f"Grok API error: {response.status_code}")
                    
                except Exception as grok_error:
                    logger.warning(f"⚠️ Erro com Grok X.AI ({modelo}): {grok_error}")
                    # Fallback para OpenAI GPT-4o
                    if self.openai_client:
                        logger.info("🔄 Usando fallback OpenAI GPT-4o para modelo Grok")
                        try:
                            safe_max_tokens = min(max_tokens, 16384)
                            response = self.openai_client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=safe_max_tokens,
                                temperature=temperatura
                            )
                            resposta = response.choices[0].message.content
                            return f"[Solicitado: {modelo} - Fallback GPT-4o]\n\n{resposta}"
                        except Exception as openai_fallback_error:
                            logger.error(f"❌ Fallback OpenAI também falhou: {openai_fallback_error}")
                
            elif modelo.startswith("deepseek"):
                # Para DeepSeek, implementar quando API estiver disponível
                logger.info(f"🤖 DeepSeek {modelo} solicitado - usando fallback OpenAI GPT-4o")
                if self.openai_client:
                    # Limitar max_tokens para GPT-4o (máximo 16384)
                    safe_max_tokens = min(max_tokens, 16384)
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=safe_max_tokens,
                        temperature=temperatura
                    )
                    resposta = response.choices[0].message.content
                    return f"[Solicitado: {modelo} - Processado com GPT-4o por compatibilidade]\n\n{resposta}"
                
            else:
                # Resposta usando conhecimento jurídico base quando não há documentos
                if documentos and contexto.strip():
                    return f"Baseado nos documentos encontrados sobre {self.area_juridica}: {contexto[:200]}..."
                else:
                    # Conhecimento base para áreas jurídicas
                    conhecimento_base = {
                        'direito_penal': {
                            'prescrição': 'A prescrição penal é a perda do direito de punir do Estado pelo decurso do tempo. Os prazos estão previstos nos arts. 109 a 119 do Código Penal, variando conforme a pena máxima cominada ao crime.',
                            'crimes': 'Crimes são condutas típicas, antijurídicas e culpáveis previstas no Código Penal e legislação especial. Devem atender aos elementos: tipicidade, antijuridicidade e culpabilidade.',
                            'pena': 'As penas podem ser privativas de liberdade, restritivas de direitos ou multa, conforme art. 32 do CP. A aplicação segue o sistema trifásico do art. 68.'
                        },
                        'direito_civil': {
                            'contratos': 'Contratos são negócios jurídicos bilaterais que geram direitos e obrigações entre as partes, regidos pelos arts. 421 e seguintes do Código Civil.',
                            'responsabilidade': 'A responsabilidade civil decorre da violação de direito e dano, gerando dever de indenizar (art. 927 CC). Pode ser objetiva ou subjetiva.',
                            'família': 'Direito de família regula relações familiares, casamento, união estável e filiação, conforme arts. 1511 e seguintes do CC.'
                        },
                        'direito_trabalhista': {
                            'contrato': 'Contrato de trabalho é acordo pelo qual pessoa física se obriga a prestar serviços subordinados, mediante salário (arts. 2º e 3º da CLT).',
                            'rescisão': 'Na rescisão são devidas verbas como aviso prévio, 13º salário, férias proporcionais e FGTS, conforme arts. 477 e seguintes da CLT.',
                            'jornada': 'Jornada normal é de 8h diárias e 44h semanais, com limite de 2h extras, conforme art. 7º, XIII da CF e art. 58 da CLT.'
                        },
                        'direito_empresarial': {
                            'sociedade': 'Sociedades empresárias são pessoas jurídicas de direito privado que exploram atividade econômica, regidas pelos arts. 981 e seguintes do CC.',
                            'falência': 'A falência é processo de execução coletiva para liquidação do patrimônio do devedor empresário, regida pela Lei 11.101/2005.',
                            'recuperação': 'A recuperação judicial visa superar crise econômico-financeira, preservando atividade econômica e emprego (Lei 11.101/2005).'
                        }
                    }
                    
                    # Buscar por palavras-chave na área específica
                    area_conhecimento = conhecimento_base.get(self.area_juridica, {})
                    resposta_encontrada = None
                    
                    for palavra_chave, definicao in area_conhecimento.items():
                        if palavra_chave.lower() in pergunta.lower():
                            resposta_encontrada = definicao
                            break
                    
                    if resposta_encontrada:
                        return f"Análise técnica: {resposta_encontrada}\n\nPara aprofundamento específico ou discussão de aspectos processuais correlatos, disponibilizo expertise adicional conforme necessário."
                    else:
                        area_nome = self.area_juridica.replace('_', ' ').title()
                        temas_disponiveis = list(area_conhecimento.keys())
                        if temas_disponiveis:
                            return f"Especialização em {area_nome}. Posso fornecer análises técnicas sobre: {', '.join(temas_disponiveis)}, além de outros institutos da área. Especifique a questão jurídica para elaboração de parecer técnico."
                        else:
                            return f"Especialista em {area_nome}. Para análise técnica adequada, detalhe a questão jurídica específica, contexto fático relevante e eventual urgência processual."
                
        except Exception as e:
            logger.error(f"Erro no processamento com IA: {e}")
            return "Indisponibilidade temporária do sistema. Reformule a consulta ou reenvie para processamento. Mantenho disponibilidade para análise técnica especializada."
    
    def processar_consulta_completa(self, pergunta: str, contexto: str = "", modelo: str = "gpt-4o", personalidade: str = "advogado", tom: str = "sistematico", temperatura: float = 0.3, max_tokens: int = 2000, documento_anexado: str = None) -> dict:
        """Método obrigatório para processar consultas completas"""
        try:
            # SE HÁ DOCUMENTO ANEXADO - PRIORIZAR ANÁLISE ESPECÍFICA
            if documento_anexado and documento_anexado.strip():
                try:
                    from .document_analyzer import DocumentAnalyzer
                    
                    # Criar analisador específico para documentos
                    analyzer = DocumentAnalyzer(
                        openai_client=self.openai_client,
                        anthropic_client=self.anthropic_client
                    )
                    
                    # Analisar especificamente o documento anexado
                    resposta_especifica = analyzer.analisar_documento_especifico(
                        documento_anexado, pergunta, self.area_juridica
                    )
                    
                    return {
                        "resposta": resposta_especifica,
                        "fontes": [{"tipo": "documento_anexado", "conteudo": "Análise específica do documento enviado"}],
                        "area": self.area_juridica,
                        "status": "sucesso",
                        "total_documentos": 1,
                        "personalidade": personalidade,
                        "tom": tom,
                        "modo": "analise_documento_especifico"
                    }
                    
                except Exception as e:
                    logger.error(f"Erro na análise específica do documento: {e}")
                    # Continuar com busca tradicional se análise específica falhar
            
            # MÉTODO TRADICIONAL - Buscar documentos relevantes no banco
            docs_relevantes = self.buscar_documentos_relevantes(pergunta)
            
            # Processar com IA incluindo personalidade e tom
            resposta = self.processar_com_ia(pergunta, docs_relevantes, modelo, personalidade, tom, temperatura, max_tokens)
            
            return {
                "resposta": resposta,
                "fontes": docs_relevantes,
                "area": self.area_juridica,
                "status": "sucesso",
                "total_documentos": len(docs_relevantes),
                "personalidade": personalidade,
                "tom": tom,
                "modo": "busca_tradicional"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
            return {
                "resposta": "Não foi possível processar sua consulta no momento.",
                "fontes": [],
                "area": self.area_juridica,
                "status": "erro",
                "erro": str(e)
            }

    def buscar_documentos_relevantes_qdrant(self, query: str, limit: int = 5) -> list:
        """Busca documentos usando Qdrant"""
        try:
            from busca_qdrant_juridica import buscar_juridico_qdrant
            
            resultado = buscar_juridico_qdrant(
                area=self.area_juridica,
                consulta=query,
                limite=limit
            )
            
            if resultado.get("status") == "sucesso":
                return resultado.get("resultados", [])
            else:
                # Fallback para busca PostgreSQL se Qdrant falhar
                return self.buscar_documentos_relevantes(query, limit)
                
        except Exception as e:
            logger.error(f"Erro na busca Qdrant: {e}")
            # Fallback para busca tradicional
            return self.buscar_documentos_relevantes(query, limit)
