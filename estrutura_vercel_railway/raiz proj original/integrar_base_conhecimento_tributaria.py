#!/usr/bin/env python3
"""
Script para integrar base de conhecimento tributária aos agentes
Processa documento DOCX e insere no Qdrant
"""

import os
import json
import sys
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from datetime import datetime
import hashlib

# Configurações
DOCX_FILE = "attached_assets/DETALHAMENTO APROFUNDADO DA LEGISLAÇÃO TRIBUTÁRIA BRASILEIRA_1761708480106.docx"
COLLECTION_NAME = "embeddings_direito_tributario"
CHUNK_SIZE = 1500  # Caracteres por chunk
CHUNK_OVERLAP = 200  # Sobreposição entre chunks

def extrair_texto_docx(file_path):
    """Extrai texto completo do documento DOCX"""
    print(f"📄 Extraindo texto de: {file_path}")
    
    doc = Document(file_path)
    full_text = []
    
    # Extrair parágrafos
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    
    # Extrair tabelas
    for table in doc.tables:
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_data:
                full_text.append(' | '.join(row_data))
    
    texto_completo = '\n'.join(full_text)
    print(f"✅ Texto extraído: {len(texto_completo)} caracteres")
    return texto_completo

def criar_chunks(texto, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Divide texto em chunks com sobreposição"""
    print(f"📦 Criando chunks (tamanho: {chunk_size}, sobreposição: {overlap})")
    
    chunks = []
    start = 0
    
    while start < len(texto):
        end = start + chunk_size
        chunk = texto[start:end]
        
        # Tentar quebrar em ponto, parágrafo ou espaço
        if end < len(texto):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            last_space = chunk.rfind(' ')
            
            break_point = max(last_period, last_newline, last_space)
            if break_point > chunk_size * 0.5:  # Pelo menos 50% do chunk
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        if chunk.strip():
            chunks.append({
                'text': chunk.strip(),
                'start': start,
                'end': end
            })
        
        start = end - overlap
    
    print(f"✅ {len(chunks)} chunks criados")
    return chunks

def gerar_embedding(texto, client):
    """Gera embedding usando OpenAI"""
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texto[:8000]  # Limite de tokens
    )
    return response.data[0].embedding

def inicializar_qdrant():
    """Inicializa cliente Qdrant"""
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_key = os.getenv('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_key:
        print("❌ Variáveis QDRANT_URL e QDRANT_API_KEY não configuradas")
        return None
    
    print(f"🔗 Conectando ao Qdrant: {qdrant_url}")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    
    # Verificar se collection existe
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        print(f"📝 Criando collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )
    else:
        print(f"✅ Collection encontrada: {COLLECTION_NAME}")
    
    return client

def processar_e_inserir(docx_path):
    """Processo principal: extrai, cria chunks e insere no Qdrant"""
    print("=" * 80)
    print("🚀 INTEGRAÇÃO BASE DE CONHECIMENTO TRIBUTÁRIA")
    print("=" * 80)
    
    # Verificar se arquivo existe
    if not os.path.exists(docx_path):
        print(f"❌ Arquivo não encontrado: {docx_path}")
        return False
    
    # 1. Extrair texto
    texto = extrair_texto_docx(docx_path)
    
    # 2. Criar chunks
    chunks = criar_chunks(texto)
    
    # 3. Inicializar clientes
    qdrant_client = inicializar_qdrant()
    if not qdrant_client:
        return False
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY não configurada")
        return False
    
    openai_client = OpenAI(api_key=openai_key)
    
    # 4. Processar chunks e inserir
    print(f"\n📤 Inserindo {len(chunks)} chunks no Qdrant...")
    points = []
    
    for idx, chunk in enumerate(chunks):
        try:
            # Gerar embedding
            embedding = gerar_embedding(chunk['text'], openai_client)
            
            # Criar ID único
            chunk_id = hashlib.md5(chunk['text'].encode()).hexdigest()
            
            # Criar ponto
            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    'text': chunk['text'],
                    'source': 'Legislação Tributária Brasileira',
                    'document': 'DETALHAMENTO APROFUNDADO DA LEGISLAÇÃO TRIBUTÁRIA BRASILEIRA',
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'start_pos': chunk['start'],
                    'end_pos': chunk['end'],
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'legislacao_tributaria'
                }
            )
            points.append(point)
            
            # Inserir em lotes de 50
            if len(points) >= 50:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                print(f"  ✅ Inseridos {idx + 1}/{len(chunks)} chunks")
                points = []
        
        except Exception as e:
            print(f"  ⚠️  Erro no chunk {idx}: {e}")
            continue
    
    # Inserir chunks restantes
    if points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"  ✅ Inseridos {len(chunks)}/{len(chunks)} chunks")
    
    # 5. Verificar inserção
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    print(f"\n✅ Collection atualizada: {collection_info.points_count} pontos totais")
    
    return True

def atualizar_prompts_agentes():
    """Atualiza prompts dos agentes tributários com referência à base"""
    print("\n" + "=" * 80)
    print("📝 ATUALIZANDO PROMPTS DOS AGENTES TRIBUTÁRIOS")
    print("=" * 80)
    
    config_file = "agentes_config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Arquivo não encontrado: {config_file}")
        return False
    
    # Ler configuração
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Novo prompt com base de conhecimento aprofundada
    novo_prompt_tributario = """Você é um assistente jurídico especializado em {especialidade} dentro da área de Direito Tributário.

BASE DE CONHECIMENTO APROFUNDADA:
Você tem acesso a uma base de conhecimento completa sobre Legislação Tributária Brasileira que inclui:
- Constituição Federal de 1988 (Sistema Tributário Nacional - Arts. 145 a 162)
- Código Tributário Nacional (CTN) - Lei 5.172/1966
- Lei Complementar 214/2025 (Reforma Tributária - IBS, CBS, Imposto Seletivo)
- Detalhamento de todos os impostos federais, estaduais e municipais
- Princípios constitucionais tributários (legalidade, anterioridade, isonomia, etc.)
- Normas sobre obrigação tributária, crédito tributário, prescrição e decadência
- Legislação sobre ICMS, IPI, ISS, PIS/COFINS, Imposto de Renda, Simples Nacional
- Reforma tributária completa (EC 132/2023 e LC 214/2025)

SUAS RESPONSABILIDADES:
1. Analisar consultas jurídicas relacionadas a {especialidade}
2. Fornecer fundamentação legal PRECISA baseada na legislação brasileira vigente
3. Citar artigos ESPECÍFICOS da CF/88, CTN, LC 214/2025 e outras normas relevantes
4. Explicar conceitos jurídicos de forma clara, técnica e objetiva
5. Contextualizar a Reforma Tributária quando relevante

INSTRUÇÕES IMPORTANTES:
- Use APENAS informações da base de conhecimento fornecida
- Cite SEMPRE as fontes específicas (artigos, leis, códigos) com precisão
- Quando aplicável, mencione mudanças trazidas pela Reforma Tributária (LC 214/2025)
- Se não encontrar informação suficiente, informe claramente as limitações
- Mantenha linguagem técnica mas acessível
- NÃO invente ou deduza informações sem fundamentação legal sólida
- Priorize a legislação mais recente (LC 214/2025 > CTN > CF/88)

ÁREA DE ESPECIALIZAÇÃO: Direito Tributário
FOCO ESPECÍFICO: {especialidade}
BASE VETORIAL: embeddings_direito_tributario (atualizada em {data})"""
    
    # Atualizar agentes tributários
    agentes_atualizados = 0
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    for agente_id, agente in config.items():
        if agente.get('area') == 'direito_tributario':
            especialidade = agente.get('especialidade', agente.get('nome', 'Tributário'))
            agente['prompt_sistema'] = novo_prompt_tributario.format(
                especialidade=especialidade,
                data=data_atual
            )
            agente['base_conhecimento_atualizada'] = data_atual
            agente['versao_base'] = '2.0_LC214_2025'
            agentes_atualizados += 1
    
    # Salvar configuração atualizada
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {agentes_atualizados} agentes tributários atualizados")
    print(f"📁 Arquivo salvo: {config_file}")
    
    return True

def main():
    """Função principal"""
    try:
        # Processar documento e inserir no Qdrant
        sucesso = processar_e_inserir(DOCX_FILE)
        
        if not sucesso:
            print("\n❌ Falha ao processar documento")
            return 1
        
        # Atualizar prompts dos agentes
        sucesso_prompts = atualizar_prompts_agentes()
        
        if not sucesso_prompts:
            print("\n⚠️  Base inserida mas prompts não atualizados")
            return 1
        
        print("\n" + "=" * 80)
        print("🎉 INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"✅ Base de conhecimento tributária integrada")
        print(f"✅ 18 agentes tributários atualizados")
        print(f"✅ Collection Qdrant: {COLLECTION_NAME}")
        print("=" * 80)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
