#!/usr/bin/env python3
"""
Script para restaurar templates, componentes e fluxos do backup
Restaura dados do arquivo db_original_hub_legal_pro.sql
"""

import re
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Configuração do banco
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def extract_insert_statements(sql_file, table_name):
    """Extrai todos os INSERTs de uma tabela do arquivo SQL"""
    print(f"\n🔍 Buscando INSERTs da tabela '{table_name}'...")
    
    inserts = []
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar INSERTs
    pattern = rf"INSERT INTO {table_name}\s*\([^)]+\)\s*VALUES\s*\([^;]+\);"
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        inserts.append(match)
    
    print(f"✅ Encontrados {len(inserts)} registros para {table_name}")
    return inserts

def restore_table_data(table_name, inserts):
    """Restaura dados de uma tabela"""
    if not inserts:
        print(f"⚠️ Nenhum dado para restaurar em {table_name}")
        return 0
    
    print(f"\n📥 Restaurando {len(inserts)} registros em {table_name}...")
    
    with engine.connect() as conn:
        # Começar transação
        trans = conn.begin()
        
        try:
            # Limpar tabela primeiro
            conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
            print(f"   🗑️ Tabela {table_name} limpa")
            
            # Inserir registros
            count = 0
            for insert_stmt in inserts:
                try:
                    conn.execute(text(insert_stmt))
                    count += 1
                    if count % 50 == 0:
                        print(f"   📊 {count}/{len(inserts)} registros inseridos...")
                except Exception as e:
                    print(f"   ⚠️ Erro ao inserir registro: {str(e)[:100]}")
                    continue
            
            # Commit da transação
            trans.commit()
            print(f"✅ {count} registros restaurados com sucesso em {table_name}")
            
            # Atualizar sequence
            conn.execute(text(f"""
                SELECT setval('{table_name}_id_seq', 
                    COALESCE((SELECT MAX(id) FROM {table_name}), 1), 
                    true);
            """))
            conn.commit()
            
            return count
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Erro ao restaurar {table_name}: {e}")
            return 0

def main():
    """Função principal"""
    print("="*60)
    print("🔄 RESTAURAÇÃO DE DADOS DO BACKUP")
    print("="*60)
    
    backup_file = 'db_original_hub_legal_pro.sql'
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return
    
    print(f"📁 Arquivo de backup: {backup_file}")
    print(f"📊 Tamanho: {os.path.getsize(backup_file) / 1024 / 1024:.2f} MB")
    
    # Tabelas para restaurar
    tables = [
        'componente_editor',
        'template_juridico',
        'fluxo'
    ]
    
    total_restored = 0
    
    for table in tables:
        # Extrair INSERTs
        inserts = extract_insert_statements(backup_file, table)
        
        # Restaurar dados
        count = restore_table_data(table, inserts)
        total_restored += count
    
    print("\n" + "="*60)
    print(f"✅ RESTAURAÇÃO CONCLUÍDA")
    print(f"📊 Total de registros restaurados: {total_restored}")
    print("="*60)
    
    # Verificar dados restaurados
    print("\n📋 VERIFICAÇÃO DOS DADOS RESTAURADOS:")
    with engine.connect() as conn:
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"   ✅ {table}: {count} registros")

if __name__ == "__main__":
    main()
