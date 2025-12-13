#!/usr/bin/env python3
"""
Script para adicionar função de busca na legislacao_tributaria_brasileira
ao sistema de análise IA de processos
"""

codigo_nova_funcao = '''
def buscar_legislacao_tributaria_qdrant(query_text, limit=5):
    """
    Busca semântica na base de legislação tributária brasileira (74 documentos)
    Collection: legislacao_tributaria_brasileira
    
    Conteúdo:
    - CF/88 (Arts. 145-162)
    - CTN (Lei 5.172/1966)
    - LC 214/2025 (Reforma Tributária)
    - EC 132/2023
    - Legislação sobre todos os tributos
    """
    try:
        from qdrant_client import QdrantClient
        from openai import OpenAI
        import os
        
        # Conectar ao Qdrant
        qdrant_url = os.getenv("QDRANT_URL", "https://c21e6a5b-298d-483b-82f4-00aeff5edabe.us-east4-0.gcp.cloud.qdrant.io:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        client_qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=30)
        
        # Gerar embedding da query
        client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        query_vector = response.data[0].embedding
        
        # Buscar no Qdrant
        results = client_qdrant.search(
            collection_name="legislacao_tributaria_brasileira",
            query_vector=query_vector,
            limit=limit
        )
        
        # Formatar resultados
        contextos = []
        for hit in results:
            payload = hit.payload
            contexto = {
                'text': payload.get('text', ''),
                'score': hit.score,
                'doc_id': payload.get('doc_id', ''),
                'categoria': payload.get('categoria', ''),
                'tipo_normativo': payload.get('tipo_normativo', ''),
                'artigos': payload.get('artigos', []),
                'ano': payload.get('ano', ''),
                'topico': payload.get('topico', '')
            }
            contextos.append(contexto)
        
        logger.info(f"✅ Encontrados {len(contextos)} documentos de legislação tributária (scores: {[c['score'] for c in contextos]})")
        return contextos
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar legislação tributária: {str(e)}")
        return []
'''

print(codigo_nova_funcao)
print("\n" + "="*80)
print("✅ FUNÇÃO GERADA COM SUCESSO!")
print("="*80)
print("\n📋 PRÓXIMOS PASSOS:")
print("1. Adicionar a função acima ao main.py (próximo à função buscar_contexto_tributario_qdrant)")
print("2. Integrar essa busca no endpoint /api/processos/<id>/gerar-analise-ia")
print("3. Usar nos prompts de análise técnica para processos tributários")
print("\n💡 SUGESTÃO DE INTEGRAÇÃO:")
print("""
# No endpoint de análise IA, adicionar:
if area_juridica == 'Direito Tributário':
    # Buscar legislação específica
    query_legislacao = f"{tema} {acao} {resumo_fatos[:200]}"
    contexto_legislacao = buscar_legislacao_tributaria_qdrant(query_legislacao, limit=5)
    
    # Adicionar ao prompt de análise técnica
    if contexto_legislacao:
        legislacao_citacoes = "\\n\\n".join([
            f"📜 {ctx['tipo_normativo'].upper()} ({ctx['ano']}) - Arts. {', '.join(ctx['artigos'])}:\\n{ctx['text']}"
            for ctx in contexto_legislacao[:3]
        ])
        prompt_tecnica += f"\\n\\nLEGISLAÇÃO APLICÁVEL:\\n{legislacao_citacoes}"
""")
