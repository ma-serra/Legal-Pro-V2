"""
Script para reorganizar IDs dos agentes jurídicos, removendo lacunas
e criando sequência contínua de 1 a 309
"""

import psycopg2
import os
from datetime import datetime

def get_database_connection():
    """Conecta ao banco PostgreSQL"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=os.environ.get('PGPORT', 5432)
    )

def reorganizar_ids_agentes():
    """Reorganiza os IDs dos agentes para sequência contínua"""
    print("🔄 REORGANIZAÇÃO DOS IDs DOS AGENTES")
    print("=" * 60)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Desabilitar constraints temporariamente
        print("1. Desabilitando constraints...")
        cursor.execute("SET session_replication_role = replica;")
        
        # 2. Criar tabela temporária com nova numeração
        print("2. Criando mapeamento de novos IDs...")
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_id_mapping AS
            WITH ranked_agents AS (
                SELECT 
                    id as old_id,
                    ROW_NUMBER() OVER (ORDER BY id) as new_id
                FROM agente_juridico
                ORDER BY id
            )
            SELECT old_id, new_id FROM ranked_agents;
        """)
        
        # 3. Verificar mapeamento
        cursor.execute("SELECT COUNT(*) FROM temp_id_mapping")
        total_mapping = cursor.fetchone()[0]
        print(f"   Total de agentes mapeados: {total_mapping}")
        
        # 4. Atualizar tabela principal com novos IDs
        print("3. Aplicando nova numeração...")
        
        # Primeiro, mover para IDs temporários (negativos) para evitar conflitos
        cursor.execute("""
            UPDATE agente_juridico 
            SET id = -mapping.new_id
            FROM temp_id_mapping mapping
            WHERE agente_juridico.id = mapping.old_id;
        """)
        
        # Depois, converter de volta para positivos
        cursor.execute("""
            UPDATE agente_juridico 
            SET id = -id
            WHERE id < 0;
        """)
        
        # 5. Atualizar sequência para próximo ID disponível
        print("4. Atualizando sequência...")
        cursor.execute("""
            SELECT setval('agente_juridico_id_seq', 
                         (SELECT MAX(id) FROM agente_juridico) + 1);
        """)
        
        # 6. Reabilitar constraints
        print("5. Reabilitando constraints...")
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # 7. Verificar resultado
        cursor.execute("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_agentes,
                MAX(id) - MIN(id) + 1 as range_esperado
            FROM agente_juridico
        """)
        
        result = cursor.fetchone()
        min_id, max_id, total, range_expected = result
        
        print("=" * 60)
        print("✅ REORGANIZAÇÃO CONCLUÍDA")
        print("=" * 60)
        print(f"ID mínimo: {min_id}")
        print(f"ID máximo: {max_id}")
        print(f"Total de agentes: {total}")
        print(f"Range esperado: {range_expected}")
        
        if total == range_expected and min_id == 1:
            print("🎯 Sequência perfeita: 1 a {} sem lacunas!".format(max_id))
        else:
            print("⚠️  Ainda existem lacunas na sequência")
        
        # 8. Commit das alterações
        conn.commit()
        print("\n💾 Alterações salvas no banco de dados")
        
    except Exception as e:
        print(f"❌ Erro durante reorganização: {str(e)}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()

def verificar_integridade():
    """Verifica integridade após reorganização"""
    print("\n🔍 VERIFICAÇÃO DE INTEGRIDADE")
    print("=" * 60)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar agentes por categoria
        cursor.execute("""
            SELECT 
                c.nome as categoria,
                COUNT(a.id) as total_agentes,
                MIN(a.id) as menor_id,
                MAX(a.id) as maior_id
            FROM categoria_juridica c 
            LEFT JOIN agente_juridico a ON c.id = a.categoria_id AND a.ativo = true
            WHERE a.id IS NOT NULL
            GROUP BY c.id, c.nome 
            ORDER BY c.nome
        """)
        
        print("Distribuição por categoria:")
        for row in cursor.fetchall():
            categoria, total, min_id, max_id = row
            print(f"  {categoria}: {total} agentes (IDs {min_id}-{max_id})")
        
        # Verificar se existem lacunas
        cursor.execute("""
            WITH id_series AS (
                SELECT generate_series(1, (SELECT MAX(id) FROM agente_juridico)) as expected_id
            )
            SELECT COUNT(*) as lacunas
            FROM id_series s
            LEFT JOIN agente_juridico a ON s.expected_id = a.id
            WHERE a.id IS NULL
        """)
        
        lacunas = cursor.fetchone()[0]
        if lacunas == 0:
            print("✅ Nenhuma lacuna encontrada - sequência perfeita!")
        else:
            print(f"⚠️  {lacunas} lacunas ainda existem")
            
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    print(f"Início da reorganização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        reorganizar_ids_agentes()
        verificar_integridade()
        
        print(f"\nFim da reorganização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🎉 Reorganização dos IDs concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro na reorganização: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()