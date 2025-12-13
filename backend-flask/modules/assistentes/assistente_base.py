"""
Classe base para todos os assistentes jurídicos especializados
"""
import os
import json
import logging
import psycopg2
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)

class AssistenteBase:
    """Classe base para assistentes jurídicos especializados"""
    
    def __init__(self, area_juridica: str):
        self.area_juridica = area_juridica
        self.nome = f"Assistente de {area_juridica.title()}"
        self.descricao = f"Assistente especializado em {area_juridica}"
        
        # Configuração de APIs
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        self.base_vetorial = None
        
        # Configurações do assistente
        self.tons_voz = ["formal", "técnico", "pedagógico", "estratégico"]
        self.tipos_resposta = ["resumo", "análise_técnica", "fundamentação", "sugestão_alteração"]
        
        # Inicializar conexões
        self._inicializar_apis()
        self._configurar_banco_vetorial()
    
    def _inicializar_apis(self):
        """Inicializa as conexões com as APIs de IA"""
        try:
            # OpenAI
            if os.getenv('OPENAI_API_KEY'):
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info(f"✅ OpenAI inicializada para {self.area_juridica}")
            
            # Anthropic
            if os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info(f"✅ Anthropic inicializada para {self.area_juridica}")
            
            # Google seria inicializado aqui se necessário
            
        except Exception as e:
            logger.error(f"Erro ao inicializar APIs para {self.area_juridica}: {e}")
    
    def _configurar_banco_vetorial(self):
        """Configura banco vetorial PostgreSQL com pgvector"""
        try:
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cur = conn.cursor()
            
            # Verificar se a extensão pgvector já existe
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            if not cur.fetchone():
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("Extensão pgvector criada")
            
            # Configurar tabela específica por área
            if self.area_juridica == 'criminal':
                # Para criminal, usar a tabela já existente
                self.base_vetorial = "documentos_criminais"
                
                # Verificar se a tabela existe
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'documentos_criminais'
                    );
                """)
                
                if not cur.fetchone()[0]:
                    # Criar tabela criminal se não existir
                    cur.execute("""
                        CREATE TABLE documentos_criminais (
                            id SERIAL PRIMARY KEY,
                            titulo TEXT NOT NULL,
                            conteudo TEXT NOT NULL,
                            artigo TEXT,
                            codigo TEXT,
                            categoria TEXT,
                            embedding vector(1536),
                            metadata JSONB,
                            criado_em TIMESTAMP DEFAULT NOW(),
                            atualizado_em TIMESTAMP DEFAULT NOW()
                        );
                    """)
                    
                    # Criar índices
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_docs_criminais_embedding 
                        ON documentos_criminais USING ivfflat (embedding vector_cosine_ops) 
                        WITH (lists = 100);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_docs_criminais_categoria 
                        ON documentos_criminais(categoria);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_docs_criminais_codigo 
                        ON documentos_criminais(codigo);
                    """)
            else:
                # Para outras áreas, criar tabela específica
                tabela = f"documentos_{self.area_juridica}"
                self.base_vetorial = tabela
                
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {tabela} (
                        id SERIAL PRIMARY KEY,
                        titulo TEXT NOT NULL,
                        conteudo TEXT NOT NULL,
                        categoria TEXT,
                        subcategoria TEXT,
                        tipo_documento TEXT,
                        fonte TEXT,
                        embedding vector(1536),
                        metadata JSONB,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        atualizado_em TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Criar índices específicos da área
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{tabela}_embedding 
                    ON {tabela} USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100);
                """)
                
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{tabela}_categoria 
                    ON {tabela}(categoria);
                """)
                
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{tabela}_tipo 
                    ON {tabela}(tipo_documento);
                """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Banco vetorial inicializado para {self.area_juridica}")
            
        except Exception as e:
            logger.warning(f"Banco vetorial não disponível para {self.area_juridica}: {e}")
            self.base_vetorial = None
    
    def processar_consulta(self, mensagem: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa uma consulta jurídica"""
        try:
            # Buscar no banco vetorial
            documentos_relevantes = self._buscar_documentos_vetoriais(mensagem)
            
            # Preparar contexto
            contexto_completo = self._preparar_contexto(mensagem, documentos_relevantes, contexto)
            
            # Gerar resposta usando IA
            resposta = self._gerar_resposta_ia(mensagem, contexto_completo)
            
            return {
                'sucesso': True,
                'resposta': resposta,
                'documentos_consultados': len(documentos_relevantes),
                'area_juridica': self.area_juridica,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar consulta em {self.area_juridica}: {e}")
            return {
                'sucesso': False,
                'erro': str(e),
                'area_juridica': self.area_juridica
            }
    
    def _buscar_documentos_vetoriais(self, consulta: str, limite: int = 5) -> List[Dict]:
        """Busca documentos relevantes no banco vetorial PostgreSQL"""
        if not self.base_vetorial:
            return []
        
        try:
            # Gerar embedding da consulta
            embedding = self._gerar_embedding(consulta)
            if not embedding:
                return []
            
            # Buscar documentos similares usando pgvector
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            cur = conn.cursor()
            
            # Query de busca por similaridade
            query = f"""
                SELECT titulo, conteudo, categoria, metadata, 
                       (embedding <=> %s::vector) as distancia
                FROM {self.base_vetorial}
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """
            
            # Converter embedding para formato PostgreSQL
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            cur.execute(query, (embedding_str, embedding_str, limite))
            resultados = cur.fetchall()
            
            # Converter resultados para lista de dicionários
            documentos = []
            for resultado in resultados:
                documento = {
                    'titulo': resultado[0],
                    'conteudo': resultado[1],
                    'categoria': resultado[2],
                    'metadata': resultado[3] if resultado[3] else {},
                    'similaridade': 1 - resultado[4]  # Converter distância para similaridade
                }
                documentos.append(documento)
            
            cur.close()
            conn.close()
            
            logger.info(f"Encontrados {len(documentos)} documentos relevantes para: {consulta[:50]}...")
            return documentos
            
        except Exception as e:
            logger.warning(f"Erro na busca vetorial: {e}")
            return []
    
    def _gerar_embedding(self, texto: str) -> List[float]:
        """Gera embedding usando OpenAI"""
        if not self.openai_client:
            return []
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texto
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def _preparar_contexto(self, mensagem: str, documentos: List[Dict], contexto_extra: Dict = None) -> str:
        """Prepara o contexto para a consulta de IA"""
        contexto_base = f"""
Você é um assistente jurídico especializado em {self.area_juridica}.

CONSULTA DO USUÁRIO:
{mensagem}

DOCUMENTOS RELEVANTES:
"""
        
        for i, doc in enumerate(documentos[:3], 1):
            contexto_base += f"\n{i}. {doc.get('titulo', 'Documento')}: {doc.get('conteudo', '')[:500]}...\n"
        
        if contexto_extra:
            contexto_base += f"\nCONTEXTO ADICIONAL:\n{json.dumps(contexto_extra, indent=2)}"
        
        contexto_base += f"""

INSTRUÇÕES:
- Responda baseado nos documentos fornecidos
- Cite as fontes quando aplicável
- Use linguagem jurídica apropriada
- Se não encontrar informação relevante, seja honesto sobre isso
- Área de especialização: {self.area_juridica}
"""
        
        return contexto_base
    
    def _gerar_resposta_ia(self, mensagem: str, contexto: str, modelo: str = "gpt-4o") -> str:
        """Gera resposta usando IA"""
        if self.openai_client and modelo.startswith('gpt'):
            return self._gerar_resposta_openai(contexto, modelo)
        elif self.anthropic_client and modelo.startswith('claude'):
            return self._gerar_resposta_anthropic(contexto, modelo)
        else:
            return "Não foi possível processar sua consulta no momento. Verifique a configuração das APIs."
    
    def _gerar_resposta_openai(self, contexto: str, modelo: str) -> str:
        """Gera resposta usando OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": f"Você é um assistente jurídico especializado em {self.area_juridica}."},
                    {"role": "user", "content": contexto}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro OpenAI: {e}")
            return f"Erro ao processar com OpenAI: {e}"
    
    def _gerar_resposta_anthropic(self, contexto: str, modelo: str) -> str:
        """Gera resposta usando Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model=modelo,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": contexto}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Erro Anthropic: {e}")
            return f"Erro ao processar com Anthropic: {e}"
    
    def obter_templates_area(self) -> List[Dict]:
        """Retorna templates específicos da área jurídica"""
        # Implementação básica - será sobrescrita nas classes especializadas
        return []
    
    def gerar_documento(self, template_id: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera documento baseado em template"""
        # Implementação básica - será sobrescrita nas classes especializadas
        return {
            'sucesso': False,
            'erro': 'Funcionalidade não implementada para esta área'
        }
    def processar_consulta_completa(self, pergunta: str, contexto: str = "", modelo: str = "openai") -> dict:
        """Método obrigatório para processar consultas"""
        try:
            # Implementação básica
            return {
                "resposta": f"Consulta sobre {self.__class__.__name__}: {pergunta}",
                "area": getattr(self, 'area_juridica', 'geral'),
                "status": "sucesso"
            }
        except Exception as e:
            return {
                "resposta": "Erro no processamento",
                "status": "erro",
                "erro": str(e)
            }
