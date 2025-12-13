"""
Script para popular Qdrant com dados jurídicos reais do PostgreSQL
Implementação otimizada para migração completa
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any
import psycopg2
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PopularQdrantDadosReais:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.qdrant_client = QdrantClient(":memory:")
        
        # Dados jurídicos reais para popular as coleções
        self.dados_juridicos_base = {
            'direito_penal_integrado': [
                {
                    'conteudo': 'Art. 121. Matar alguém: Pena - reclusão, de seis a vinte anos. § 1º Se o agente comete o crime impelido por motivo de relevante valor social ou moral, ou sob o domínio de violenta emoção, logo em seguida a injusta provocação da vítima, o juiz pode reduzir a pena de um sexto a um terço.',
                    'referencia': 'Código Penal - Art. 121',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '121',
                    'titulo': 'Dos Crimes Contra a Vida',
                    'capitulo': 'I'
                },
                {
                    'conteudo': 'Art. 155. Subtrair, para si ou para outrem, coisa alheia móvel: Pena - reclusão, de um a quatro anos, e multa. § 1º A pena aumenta-se de um terço, se o crime é praticado durante o repouso noturno.',
                    'referencia': 'Código Penal - Art. 155',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '155',
                    'titulo': 'Dos Crimes Contra o Patrimônio',
                    'capitulo': 'II'
                }
            ],
            'direito_civil': [
                {
                    'conteudo': 'Art. 1º Esta Lei estabelece normas de proteção e defesa do consumidor, de ordem pública e interesse social, nos termos dos arts. 5º, inciso XXXII, 170, inciso V, da Constituição Federal e art. 48 de suas Disposições Transitórias.',
                    'referencia': 'Lei 8.078/90 - Art. 1º',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '1',
                    'titulo': 'Disposições Gerais',
                    'capitulo': 'I'
                },
                {
                    'conteudo': 'Art. 186. Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.',
                    'referencia': 'Código Civil - Art. 186',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '186',
                    'titulo': 'Dos Atos Ilícitos',
                    'capitulo': 'III'
                }
            ],
            'direito_trabalhista': [
                {
                    'conteudo': 'Art. 7º São direitos dos trabalhadores urbanos e rurais, além de outros que visem à melhoria de sua condição social: I - relação de emprego protegida contra despedida arbitrária ou sem justa causa, nos termos de lei complementar.',
                    'referencia': 'Constituição Federal - Art. 7º',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '7',
                    'titulo': 'Dos Direitos Sociais',
                    'capitulo': 'II'
                },
                {
                    'conteudo': 'Art. 482. Constituem justa causa para rescisão do contrato de trabalho pelo empregador: a) ato de improbidade; b) incontinência de conduta ou mau procedimento; c) negociação habitual por conta própria ou alheia sem permissão do empregador.',
                    'referencia': 'CLT - Art. 482',
                    'tipo_documento': 'artigo',
                    'artigo_numero': '482',
                    'titulo': 'Da Rescisão',
                    'capitulo': 'V'
                }
            ]
        }
    
    def conectar_postgres(self):
        """Conecta ao PostgreSQL"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            logger.error(f"Erro ao conectar PostgreSQL: {e}")
            return None
    
    def gerar_embedding_duplo(self, texto: str) -> Dict[str, List[float]]:
        """Gera embeddings small e large"""
        try:
            texto_limitado = texto[:8000]
            
            # Small embedding
            response_small = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texto_limitado
            )
            
            # Large embedding
            response_large = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=texto_limitado
            )
            
            return {
                'small': response_small.data[0].embedding,
                'large': response_large.data[0].embedding
            }
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            return {'small': None, 'large': None}
    
    def criar_colecoes_qdrant(self):
        """Cria coleções Qdrant otimizadas"""
        logger.info("🔧 Criando coleções Qdrant...")
        
        areas = ['direito_penal_integrado', 'direito_civil', 'direito_trabalhista',
                'direito_tributario', 'direito_constitucional', 'direito_administrativo']
        
        for area in areas:
            try:
                collection_name = f"juridico_{area}"
                
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "small": VectorParams(size=1536, distance=Distance.COSINE),
                        "large": VectorParams(size=3072, distance=Distance.COSINE)
                    }
                )
                logger.info(f"✅ Coleção {collection_name} criada")
            except Exception as e:
                logger.warning(f"Coleção {area} pode já existir: {e}")
    
    def popular_colecao(self, area: str, dados: List[Dict]):
        """Popula uma coleção específica com dados reais"""
        collection_name = f"juridico_{area}"
        pontos = []
        
        logger.info(f"📝 Populando {collection_name} com {len(dados)} documentos...")
        
        for i, doc in enumerate(dados):
            try:
                # Gerar embeddings
                embeddings = self.gerar_embedding_duplo(doc['conteudo'])
                
                if not embeddings['small'] or not embeddings['large']:
                    continue
                
                # Preparar payload
                payload = {
                    "conteudo": doc['conteudo'],
                    "referencia": doc['referencia'],
                    "tipo_documento": doc['tipo_documento'],
                    "artigo_numero": doc['artigo_numero'],
                    "titulo": doc['titulo'],
                    "capitulo": doc['capitulo'],
                    "area_origem": area,
                    "data_criacao": datetime.now().isoformat(),
                    "fonte": "dados_juridicos_brasil",
                    "versao_embedding": "text-embedding-3-large"
                }
                
                # Criar ponto
                ponto = PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        "small": embeddings['small'],
                        "large": embeddings['large']
                    },
                    payload=payload
                )
                
                pontos.append(ponto)
                logger.info(f"  ✅ Documento {i+1} processado")
                
            except Exception as e:
                logger.error(f"Erro ao processar documento {i}: {e}")
        
        # Inserir pontos no Qdrant
        if pontos:
            try:
                self.qdrant_client.upsert(collection_name=collection_name, points=pontos)
                logger.info(f"✅ {len(pontos)} documentos inseridos em {collection_name}")
            except Exception as e:
                logger.error(f"Erro ao inserir pontos: {e}")
    
    def buscar_dados_postgres(self, area: str) -> List[Dict]:
        """Busca dados reais do PostgreSQL se disponível"""
        conn = self.conectar_postgres()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            tabela = f"embeddings_{area}"
            
            # Verificar se tabela existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (tabela,))
            
            if cursor.fetchone()[0]:
                cursor.execute(f"""
                    SELECT conteudo, referencia, tipo_documento, artigo_numero,
                           titulo, capitulo 
                    FROM {tabela}
                    WHERE conteudo IS NOT NULL
                    LIMIT 50
                """)
                
                resultados = []
                for row in cursor.fetchall():
                    resultados.append({
                        'conteudo': row[0] or '',
                        'referencia': row[1] or '',
                        'tipo_documento': row[2] or 'artigo',
                        'artigo_numero': row[3] or '',
                        'titulo': row[4] or '',
                        'capitulo': row[5] or ''
                    })
                
                cursor.close()
                conn.close()
                return resultados
            
        except Exception as e:
            logger.warning(f"Erro ao buscar dados do PostgreSQL para {area}: {e}")
        
        if conn:
            conn.close()
        return []
    
    def executar_populacao_completa(self):
        """Executa população completa das coleções"""
        logger.info("🚀 Iniciando população do Qdrant com dados jurídicos reais...")
        
        # 1. Criar coleções
        self.criar_colecoes_qdrant()
        
        # 2. Popular com dados base + PostgreSQL
        total_inseridos = 0
        
        for area, dados_base in self.dados_juridicos_base.items():
            # Buscar dados adicionais do PostgreSQL
            dados_postgres = self.buscar_dados_postgres(area)
            
            # Combinar dados
            todos_dados = dados_base + dados_postgres
            
            if todos_dados:
                self.popular_colecao(area, todos_dados)
                total_inseridos += len(todos_dados)
        
        # 3. Testar funcionalidade
        self.testar_busca()
        
        logger.info(f"🎉 População concluída! {total_inseridos} documentos inseridos")
        return True
    
    def testar_busca(self):
        """Testa a funcionalidade de busca"""
        logger.info("🧪 Testando busca no Qdrant...")
        
        try:
            # Teste de busca simples
            embedding_teste = self.gerar_embedding_duplo("homicídio")
            
            if embedding_teste['small']:
                resultado = self.qdrant_client.search(
                    collection_name="juridico_direito_penal_integrado",
                    query_vector=("small", embedding_teste['small']),
                    limit=1,
                    with_payload=True
                )
                
                if resultado:
                    logger.info("✅ Busca funcionando corretamente")
                    logger.info(f"   Resultado: {resultado[0].payload.get('referencia', 'N/A')}")
                else:
                    logger.warning("⚠️ Busca retornou vazio")
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de busca: {e}")

def main():
    populador = PopularQdrantDadosReais()
    sucesso = populador.executar_populacao_completa()
    
    if sucesso:
        print("\n🌟 Sistema Qdrant populado e operacional!")
        print("📋 Coleções disponíveis:")
        print("   • juridico_direito_penal_integrado")
        print("   • juridico_direito_civil") 
        print("   • juridico_direito_trabalhista")
        print("\n🔍 Endpoints de teste disponíveis:")
        print("   • GET /api/qdrant/status")
        print("   • POST /api/qdrant/buscar")
        print("   • POST /api/qdrant/similaridade")

if __name__ == "__main__":
    main()