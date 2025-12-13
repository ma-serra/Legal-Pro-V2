"""
Sistema de Controle de Bases Vetoriais
Monitora arquivos, percentuais de processamento e status das bases vetoriais
"""

import psycopg2
import os
from datetime import datetime
import json
from typing import Dict, List, Tuple

def get_database_connection():
    """Conecta ao banco PostgreSQL"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT', 5432)
    )

def get_all_vector_tables():
    """Obtém todas as tabelas de embeddings"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE 'embeddings_%' 
        ORDER BY table_name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return tables

def analyze_vector_table(table_name: str) -> Dict:
    """Analisa uma tabela de embeddings específica"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Informações básicas da tabela
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as processed_records,
                COUNT(CASE WHEN embedding IS NULL THEN 1 END) as pending_records
            FROM {table_name}
        """)
        
        counts = cursor.fetchone()
        total, processed, pending = counts if counts else (0, 0, 0)
        
        # Colunas da tabela para identificar campos de arquivo
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        # Buscar arquivos únicos se existir coluna de arquivo
        file_columns = [col[0] for col in columns if 'arquivo' in col[0] or 'file' in col[0] or 'documento' in col[0]]
        unique_files = []
        
        if file_columns:
            file_col = file_columns[0]
            cursor.execute(f"""
                SELECT DISTINCT {file_col}, COUNT(*) as chunk_count
                FROM {table_name}
                WHERE {file_col} IS NOT NULL
                GROUP BY {file_col}
                ORDER BY {file_col}
            """)
            unique_files = cursor.fetchall()
        
        # Calcular percentual de processamento
        processing_percentage = (processed / total * 100) if total > 0 else 0
        
        # Tamanho da tabela
        cursor.execute(f"""
            SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
        """)
        table_size = cursor.fetchone()[0] if cursor.rowcount > 0 else 'N/A'
        
        # Data da última atualização
        cursor.execute(f"""
            SELECT MAX(created_at) as last_update
            FROM {table_name}
            WHERE created_at IS NOT NULL
        """)
        
        last_update_result = cursor.fetchone()
        last_update = last_update_result[0] if last_update_result and last_update_result[0] else None
        
        return {
            'base_name': table_name,
            'total_records': total,
            'processed_records': processed,
            'pending_records': pending,
            'processing_percentage': round(processing_percentage, 2),
            'unique_files': len(unique_files),
            'files_list': [{'name': file[0], 'chunks': file[1]} for file in unique_files],
            'table_size': table_size,
            'last_update': last_update.isoformat() if last_update else None,
            'columns': [col[0] for col in columns]
        }
        
    except Exception as e:
        return {
            'base_name': table_name,
            'error': str(e),
            'total_records': 0,
            'processed_records': 0,
            'pending_records': 0,
            'processing_percentage': 0,
            'unique_files': 0,
            'files_list': [],
            'table_size': 'N/A',
            'last_update': None
        }
    finally:
        cursor.close()
        conn.close()

def generate_comprehensive_report():
    """Gera relatório completo das bases vetoriais"""
    print("🔍 Iniciando análise das bases vetoriais...")
    
    # Obter todas as tabelas
    tables = get_all_vector_tables()
    print(f"📊 Encontradas {len(tables)} bases vetoriais")
    
    # Analisar cada tabela
    report_data = []
    total_files = 0
    total_records = 0
    total_processed = 0
    
    for i, table in enumerate(tables, 1):
        print(f"⚡ Analisando {table} ({i}/{len(tables)})...")
        analysis = analyze_vector_table(table)
        report_data.append(analysis)
        
        if 'error' not in analysis:
            total_files += analysis['unique_files']
            total_records += analysis['total_records']
            total_processed += analysis['processed_records']
    
    # Calcular estatísticas gerais
    overall_percentage = (total_processed / total_records * 100) if total_records > 0 else 0
    
    # Gerar relatório
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_bases': len(tables),
            'total_files': total_files,
            'total_records': total_records,
            'total_processed': total_processed,
            'overall_processing_percentage': round(overall_percentage, 2)
        },
        'bases': report_data
    }
    
    return report

def print_detailed_report():
    """Imprime relatório detalhado formatado"""
    report = generate_comprehensive_report()
    
    print("\n" + "="*80)
    print("📋 RELATÓRIO COMPLETO DAS BASES VETORIAIS")
    print("="*80)
    print(f"🕒 Gerado em: {report['generated_at']}")
    print(f"📊 Total de Bases: {report['summary']['total_bases']}")
    print(f"📁 Total de Arquivos: {report['summary']['total_files']}")
    print(f"📄 Total de Registros: {report['summary']['total_records']:,}")
    print(f"✅ Registros Processados: {report['summary']['total_processed']:,}")
    print(f"📈 Percentual Geral: {report['summary']['overall_processing_percentage']:.2f}%")
    print("="*80)
    
    # Relatório por base
    for base in sorted(report['bases'], key=lambda x: x['base_name']):
        if 'error' in base:
            print(f"\n❌ {base['base_name']}: ERRO - {base['error']}")
            continue
            
        print(f"\n📚 BASE: {base['base_name']}")
        print(f"   📁 Arquivos únicos: {base['unique_files']}")
        print(f"   📄 Total registros: {base['total_records']:,}")
        print(f"   ✅ Processados: {base['processed_records']:,}")
        print(f"   ⏳ Pendentes: {base['pending_records']:,}")
        print(f"   📈 Percentual: {base['processing_percentage']:.2f}%")
        print(f"   💾 Tamanho: {base['table_size']}")
        print(f"   🕒 Última atualização: {base['last_update'] or 'N/A'}")
        
        if base['files_list']:
            print(f"   📂 Arquivos processados:")
            for file_info in base['files_list'][:5]:  # Mostrar apenas os primeiros 5
                print(f"      • {file_info['name']} ({file_info['chunks']} chunks)")
            if len(base['files_list']) > 5:
                print(f"      ... e mais {len(base['files_list']) - 5} arquivos")

def save_report_to_file():
    """Salva relatório em arquivo JSON"""
    report = generate_comprehensive_report()
    
    filename = f"relatorio_bases_vetoriais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: {filename}")
    return filename

def get_top_bases_by_files():
    """Retorna as bases com mais arquivos"""
    report = generate_comprehensive_report()
    
    bases_with_files = [base for base in report['bases'] if 'error' not in base and base['unique_files'] > 0]
    top_bases = sorted(bases_with_files, key=lambda x: x['unique_files'], reverse=True)[:10]
    
    print("\n🏆 TOP 10 BASES COM MAIS ARQUIVOS:")
    print("-" * 50)
    for i, base in enumerate(top_bases, 1):
        print(f"{i:2d}. {base['base_name']}: {base['unique_files']} arquivos ({base['processing_percentage']:.1f}% processado)")

def get_processing_status():
    """Mostra status de processamento"""
    report = generate_comprehensive_report()
    
    # Categorizar bases por status de processamento
    completed = [base for base in report['bases'] if 'error' not in base and base['processing_percentage'] == 100]
    in_progress = [base for base in report['bases'] if 'error' not in base and 0 < base['processing_percentage'] < 100]
    empty = [base for base in report['bases'] if 'error' not in base and base['processing_percentage'] == 0]
    errors = [base for base in report['bases'] if 'error' in base]
    
    print("\n📊 STATUS DE PROCESSAMENTO:")
    print("-" * 50)
    print(f"✅ Bases Completas (100%): {len(completed)}")
    print(f"⚡ Bases em Progresso: {len(in_progress)}")
    print(f"📝 Bases Vazias: {len(empty)}")
    print(f"❌ Bases com Erro: {len(errors)}")
    
    if in_progress:
        print("\n⚡ BASES EM PROGRESSO:")
        for base in sorted(in_progress, key=lambda x: x['processing_percentage'], reverse=True):
            print(f"   • {base['base_name']}: {base['processing_percentage']:.1f}% ({base['processed_records']}/{base['total_records']})")

if __name__ == "__main__":
    print("🚀 Sistema de Controle de Bases Vetoriais")
    print_detailed_report()
    get_top_bases_by_files()
    get_processing_status()
    save_report_to_file()