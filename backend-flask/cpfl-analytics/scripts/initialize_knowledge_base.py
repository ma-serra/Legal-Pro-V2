#!/usr/bin/env python3
"""
Script de inicialização da base de conhecimento CPFL
Carrega os 3.216 processos e indexa no Qdrant para RAG
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cpfl_analytics.services.knowledge_base import (
    load_processos_from_json, 
    prepare_processos_for_embedding,
    chunk_processo
)
from cpfl_analytics.services.qdrant_service import qdrant_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Executa inicialização da base de conhecimento"""
    
    print("\n" + "="*70)
    print("🚀 INICIALIZAÇÃO DA BASE DE CONHECIMENTO CPFL")
    print("="*70 + "\n")
    
    try:
        print("📊 Passo 1: Carregando processos do JSON...")
        processos_raw = load_processos_from_json()
        
        if not processos_raw:
            print("❌ Nenhum processo encontrado!")
            return 1
        
        print(f"✅ {len(processos_raw)} processos carregados\n")
        
        print("🔧 Passo 2: Preparando processos para embeddings...")
        processos_prepared = prepare_processos_for_embedding(processos_raw)
        
        processos_chunked = []
        for processo in processos_prepared:
            chunks = chunk_processo(processo, max_tokens=512)
            processos_chunked.extend(chunks)
        
        print(f"✅ {len(processos_chunked)} documentos preparados")
        print(f"   ({len(processos_chunked) - len(processos_prepared)} chunks adicionais)\n")
        
        print("🗄️ Passo 3: Inicializando Qdrant...")
        success = qdrant_service.initialize_collection()
        
        if not success:
            print("❌ Falha ao inicializar Qdrant!")
            return 1
        
        print("✅ Qdrant pronto\n")
        
        print("🔮 Passo 4: Gerando embeddings e indexando...")
        print("⚠️ Este processo pode levar alguns minutos...\n")
        
        total_indexed = qdrant_service.index_processos(
            processos_chunked, 
            batch_size=50
        )
        
        print(f"\n✅ {total_indexed} documentos indexados com sucesso!\n")
        
        print("✓ Passo 5: Validando base de conhecimento...")
        stats = qdrant_service.get_collection_stats()
        
        print("\n📊 Estatísticas da Base de Conhecimento:")
        print(f"   • Total de vetores: {stats.get('total_pontos', 0)}")
        print(f"   • Dimensão vetorial: {stats.get('vector_size', 0)}")
        print(f"   • Métrica de distância: {stats.get('distancia', 'N/A')}")
        
        if stats.get('total_pontos', 0) != len(processos_chunked):
            print("\n⚠️ ATENÇÃO: Número de vetores não corresponde ao esperado!")
            return 1
        
        print("\n" + "="*70)
        print("🎉 BASE DE CONHECIMENTO CRIADA COM SUCESSO!")
        print("="*70 + "\n")
        
        print("💡 Próximos passos:")
        print("   1. Configure QDRANT_URL e QDRANT_API_KEY no .env")
        print("   2. Acesse /cpfl/agente para usar o chat")
        print("   3. Faça consultas jurídicas inteligentes\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ ERRO CRÍTICO: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
