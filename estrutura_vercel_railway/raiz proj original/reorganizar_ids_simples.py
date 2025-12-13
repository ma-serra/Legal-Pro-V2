"""
Script simplificado para reorganizar IDs dos agentes sem modificar configurações de sistema
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
    """Reorganiza os IDs dos agentes para sequência contínua usando offset temporário"""
    print("Reorganização dos IDs dos agentes")
    print("=" * 50)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estado atual
        cursor.execute("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_agentes
            FROM agente_juridico
        """)
        
        min_id, max_id, total = cursor.fetchone()
        print(f"Estado atual: IDs de {min_id} a {max_id}, total: {total}")
        
        # 2. Criar mapeamento para nova sequência
        cursor.execute("""
            WITH ranked_agents AS (
                SELECT 
                    id as old_id,
                    ROW_NUMBER() OVER (ORDER BY id) as new_id
                FROM agente_juridico
                ORDER BY id
            )
            SELECT old_id, new_id FROM ranked_agents
            ORDER BY old_id
        """)
        
        mappings = cursor.fetchall()
        print(f"Mapeamentos criados: {len(mappings)}")
        
        # 3. Aplicar reorganização usando offset temporário
        OFFSET = 10000  # Usar offset alto para evitar conflitos
        
        print("Movendo para IDs temporários...")
        for old_id, new_id in mappings:
            temp_id = new_id + OFFSET
            cursor.execute("""
                UPDATE agente_juridico 
                SET id = %s 
                WHERE id = %s
            """, (temp_id, old_id))
        
        print("Aplicando IDs finais...")
        for old_id, new_id in mappings:
            temp_id = new_id + OFFSET
            cursor.execute("""
                UPDATE agente_juridico 
                SET id = %s 
                WHERE id = %s
            """, (new_id, temp_id))
        
        # 4. Atualizar sequência
        cursor.execute("""
            SELECT setval('agente_juridico_id_seq', 
                         (SELECT MAX(id) FROM agente_juridico) + 1)
        """)
        
        # 5. Verificar resultado
        cursor.execute("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_agentes
            FROM agente_juridico
        """)
        
        new_min, new_max, new_total = cursor.fetchone()
        
        print("=" * 50)
        print("Resultado da reorganização:")
        print(f"Novo range: {new_min} a {new_max}")
        print(f"Total: {new_total}")
        
        if new_min == 1 and new_max == new_total:
            print("Sequência perfeita criada: 1 a {} sem lacunas".format(new_max))
        else:
            print("Ainda existem lacunas na sequência")
        
        # Commit das alterações
        conn.commit()
        print("Alterações salvas")
        
        return True
        
    except Exception as e:
        print(f"Erro durante reorganização: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

def verificar_integridade():
    """Verifica se a reorganização foi bem-sucedida"""
    print("\nVerificação de integridade:")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se há lacunas
        cursor.execute("""
            WITH expected_ids AS (
                SELECT generate_series(1, (SELECT MAX(id) FROM agente_juridico)) as id
            )
            SELECT COUNT(*) as lacunas
            FROM expected_ids e
            LEFT JOIN agente_juridico a ON e.id = a.id
            WHERE a.id IS NULL
        """)
        
        lacunas = cursor.fetchone()[0]
        
        if lacunas == 0:
            print("✓ Sequência contínua confirmada - sem lacunas")
        else:
            print(f"✗ {lacunas} lacunas ainda existem")
        
        # Mostrar distribuição por categoria
        cursor.execute("""
            SELECT 
                c.nome as categoria,
                COUNT(a.id) as total,
                MIN(a.id) as min_id,
                MAX(a.id) as max_id
            FROM categoria_juridica c 
            JOIN agente_juridico a ON c.id = a.categoria_id
            GROUP BY c.id, c.nome 
            ORDER BY MIN(a.id)
        """)
        
        print("\nDistribuição reorganizada:")
        for categoria, total, min_id, max_id in cursor.fetchall():
            print(f"  {categoria}: {total} agentes (IDs {min_id}-{max_id})")
            
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    print(f"Início: {datetime.now().strftime('%H:%M:%S')}")
    
    sucesso = reorganizar_ids_agentes()
    
    if sucesso:
        verificar_integridade()
        print(f"\nConcluído: {datetime.now().strftime('%H:%M:%S')}")
        print("Reorganização concluída com sucesso")
    else:
        print("Falha na reorganização")

if __name__ == "__main__":
    main()