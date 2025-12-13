#!/usr/bin/env python3
"""
Script para adicionar dados sintéticos ao banco de dados
Executa no contexto da aplicação Flask
"""

import os
import sys
from datetime import datetime

# Configurar ambiente
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'true')

# Importar aplicação
from main import app, db
from models import ProcessoJuridico
from modules.synthetic_data_generator import LegalSyntheticDataGenerator
from modules.populate_database import popular_banco_dados_sinteticos

def adicionar_dados_sinteticos(quantidade=25):
    """Adiciona dados sintéticos ao banco"""
    
    print(f"🚀 Adicionando {quantidade} processos sintéticos ao banco de dados...")
    
    with app.app_context():
        # Verificar dados existentes
        total_existente = ProcessoJuridico.query.count()
        print(f"📊 Processos existentes: {total_existente}")
        
        # Configurar distribuição focada em trabalhista e civil
        areas_personalizadas = {
            "Direito Trabalhista": 35,
            "Direito Civil": 25,
            "Direito do Consumidor": 15,
            "Direito Empresarial": 10,
            "Direito Tributário": 8,
            "Direito Criminal": 5,
            "Direito Previdenciário": 2
        }
        
        # Gerar e inserir dados
        resultado = popular_banco_dados_sinteticos(
            app, db, ProcessoJuridico,
            quantidade, areas_personalizadas, False
        )
        
        if resultado['sucesso']:
            print(f"✅ {resultado['processos_inseridos']} processos sintéticos inseridos com sucesso")
            
            # Estatísticas detalhadas
            stats = resultado['estatisticas']
            print(f"💰 Valor total das causas: R$ {stats['valor_total_causas']:,.2f}")
            print("\n📈 Distribuição por área:")
            for area, quantidade in sorted(stats['distribuicao_por_area'].items()):
                print(f"   {area}: {quantidade} processos")
            
            # Verificar total após inserção
            total_final = ProcessoJuridico.query.count()
            print(f"\n📊 Total de processos no banco: {total_final}")
            
            return True
        else:
            print(f"❌ Erro na inserção: {resultado['erro']}")
            return False

if __name__ == "__main__":
    # Executar adição de dados
    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    sucesso = adicionar_dados_sinteticos(quantidade)
    
    if sucesso:
        print("🎉 Operação concluída com sucesso!")
    else:
        print("💥 Operação falhou!")
        sys.exit(1)