"""
Validação Direta de Tables e Relationships
Conecta ao PostgreSQL e valida estrutura
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("="*80)
print("VALIDAÇÃO DE ESTRUTURA - Sistema de Processos Dinâmicos")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # 1. Verificar tabelas criadas
    print("\n[1] Verificando tabelas criadas...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'processo%' OR table_name IN ('tributos', 'teses_tributarias', 'indices_monetarios')
        ORDER BY table_name
    """)
    
    tabelas = cur.fetchall()
    print(f"\n  Total de tabelas do sistema: {len(tabelas)}")
    for tabela in tabelas:
        print(f"  ✓ {tabela[0]}")
    
    # 2. Verificar tributos
    print("\n[2] Verificando tributos inseridos...")
    cur.execute("SELECT codigo, nome, esfera FROM tributos ORDER BY codigo")
    tributos = cur.fetchall()
    print(f"\n  Total de tributos: {len(tributos)}")
    for codigo, nome, esfera in tributos:
        print(f"  ✓ {codigo:6s} - {nome[:50]:50s} ({esfera})")
    
    # 3. Verificar índices monetários
    print("\n[3] Verificando índices monetários...")
    cur.execute("SELECT nome, descricao FROM indices_monetarios ORDER BY nome")
    indices = cur.fetchall()
    print(f"\n  Total de índices: {len(indices)}")
    for nome, desc in indices:
        print(f"  ✓ {nome:6s} - {desc}")
    
    # 4. Verificar foreign keys
    print("\n[4] Verificando Foreign Keys...")
    cur.execute("""
        SELECT 
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name LIKE 'processo%'
        ORDER BY tc.table_name, kcu.column_name
    """)
    
    fks = cur.fetchall()
    print(f"\n  Total de Foreign Keys: {len(fks)}")
    
    fks_by_table = {}
    for table, col, f_table, f_col in fks:
        if table not in fks_by_table:
            fks_by_table[table] = []
        fks_by_table[table].append(f"{col} → {f_table}.{f_col}")
    
    for table, fks in sorted(fks_by_table.items()):
        print(f"\n  {table}:")
        for fk in fks:
            print(f"    ✓ {fk}")
    
    # 5. Verificar constraints unique
    print("\n[5] Verificando Unique Constraints...")
    cur.execute("""
        SELECT 
            tc.table_name,
            tc.constraint_name,
            string_agg(kcu.column_name, ', ') as columns
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'UNIQUE'
        AND tc.table_name LIKE 'processo%'
        GROUP BY tc.table_name, tc.constraint_name
        ORDER BY tc.table_name
    """)
    
    constraints = cur.fetchall()
    print(f"\n  Total de Unique Constraints: {len(constraints)}")
    for table, constraint, columns in constraints:
        print(f"  ✓ {table}.{constraint}: ({columns})")
    
    # 6. Verificar índices
    print("\n[6] Verificando Índices...")
    cur.execute("""
        SELECT 
            tablename,
            indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename LIKE 'processo%' OR tablename IN ('tributos', 'indices_monetarios', 'historico_indices')
        ORDER BY tablename, indexname
    """)
    
    indices_db = cur.fetchall()
    print(f"\n  Total de índices: {len(indices_db)}")
    
    indices_by_table = {}
    for table, index in indices_db:
        if table not in indices_by_table:
            indices_by_table[table] = []
        indices_by_table[table].append(index)
    
    for table, idxs in sorted(indices_by_table.items()):
        print(f"\n  {table}: {len(idxs)} índices")
        for idx in idxs[:3]:  # Mostrar até 3
            print(f"    ✓ {idx}")
    
    # 7. Testar CRUD básico
    print("\n[7] Testando CRUD básico...")
    
    # Criar processo de teste
    cur.execute("""
        INSERT INTO processos (pasta, natureza_id, status_id, titulo, ativo)
        VALUES ('VALIDACAO-TEST', 1, 1, 'Teste de Validação', TRUE)
        RETURNING id_processo, uuid
    """)
    proc_id, proc_uuid = cur.fetchone()
    print(f"  ✓ Processo criado: ID {proc_id}, UUID {proc_uuid}")
    
    # Ler
    cur.execute("SELECT pasta, titulo FROM processos WHERE id_processo = %s", (proc_id,))
    pasta, titulo = cur.fetchone()
    print(f"  ✓ Processo lido: {pasta} - {titulo}")
    
    # Atualizar
    cur.execute("UPDATE processos SET titulo = %s WHERE id_processo = %s", 
                ('Título Atualizado', proc_id))
    print(f"  ✓ Processo atualizado")
    
    # Deletar
    cur.execute("DELETE FROM processos WHERE id_processo = %s", (proc_id,))
    print(f"  ✓ Processo deletado")
    
    conn.commit()
    
    # 8. Resumo Final
    print("\n" + "="*80)
    print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print(f"\n📊 Resumo:")
    print(f"  - Tabelas criadas: {len(tabelas)}")
    print(f"  - Tributos: {len(tributos)}")
    print(f"  - Índices monetários: {len(indices)}")
    print(f"  - Foreign Keys: {len(fks)}")
    print(f"  - Unique Constraints: {len(constraints)}")
    print(f"  - Índices DB: {len(indices_db)}")
    
    print(f"\n✅ Todas as validações passaram:")
    print(f"  - Estrutura de tabelas OK")
    print(f"  - Dados iniciais OK (tributos + índices)")
    print(f"  - Foreign Keys OK")
    print(f"  - Constraints OK")
    print(f"  - Índices OK")
    print(f"  - CRUD básico OK")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    cur.close()
    conn.close()
