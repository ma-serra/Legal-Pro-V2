"""
Script para corrigir o sistema de monitoramento vetorial
para trabalhar com a estrutura real do banco de dados
"""

import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def update_vectorial_monitoring():
    """Atualiza as rotas de monitoramento vetorial para usar a estrutura real"""
    
    with app.app_context():
        # Listar todas as tabelas de embeddings disponíveis
        embedding_tables = [
            'embeddings_direito_penal',
            'embeddings_direito_trabalhista', 
            'embeddings_direito_tributario',
            'embeddings_direito_empresarial',
            'embeddings_direito_agrario',
            'embeddings_direito_bancario',
            'embeddings_direito_consumidor',
            'embeddings_direito_digital',
            'embeddings_direito_imobiliario',
            'embeddings_direito_previdenciario',
            'embeddings_direito_securitario',
            'embeddings_negociacao_conflitos',
            'embeddings_recuperacao_credito'
        ]
        
        print("📊 Verificando dados reais das tabelas de embeddings:")
        
        total_embeddings = 0
        areas_with_data = []
        
        for table in embedding_tables:
            try:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
                if count > 0:
                    area_name = table.replace('embeddings_', '').replace('_', ' ').title()
                    areas_with_data.append({
                        'table': table,
                        'area': area_name,
                        'count': count
                    })
                    total_embeddings += count
                    print(f"  ✅ {area_name}: {count} embeddings")
                else:
                    print(f"  ⚪ {table.replace('embeddings_', '').replace('_', ' ').title()}: 0 embeddings")
            except Exception as e:
                print(f"  ❌ Erro ao verificar {table}: {e}")
        
        print(f"\n📈 Total de embeddings no sistema: {total_embeddings}")
        print(f"📂 Áreas com dados: {len(areas_with_data)}")
        
        return {
            'total_embeddings': total_embeddings,
            'areas_with_data': areas_with_data,
            'embedding_tables': embedding_tables
        }

if __name__ == "__main__":
    print("🔧 Iniciando correção do sistema de monitoramento vetorial...")
    data = update_vectorial_monitoring()
    print(f"\n✅ Sistema analisado com sucesso!")
    print(f"   - Total de embeddings: {data['total_embeddings']}")
    print(f"   - Áreas ativas: {len(data['areas_with_data'])}")