#!/usr/bin/env python3
"""
Script para remover agentes com especialidades semelhantes
Mantém sempre o agente com ID menor
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def remove_duplicate_specialists():
    """Remove agentes duplicados mantendo o de menor ID"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar grupos de agentes similares
        result = session.execute(text("""
            SELECT 
                REGEXP_REPLACE(nome, ' - (Sênior|Pleno|Júnior|Consultor|Analista).*$', '') as nome_base,
                array_agg(id ORDER BY id) as ids,
                array_agg(nome ORDER BY id) as nomes
            FROM agente_juridico 
            GROUP BY REGEXP_REPLACE(nome, ' - (Sênior|Pleno|Júnior|Consultor|Analista).*$', '')
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        """))
        
        groups = result.fetchall()
        print(f"🔍 Encontrados {len(groups)} grupos de especialistas similares")
        
        total_removed = 0
        
        for group in groups:
            nome_base, ids, nomes = group
            
            if len(ids) > 1:
                # Manter apenas o primeiro ID (menor)
                id_to_keep = ids[0]
                ids_to_remove = ids[1:]
                
                print(f"\n📝 Grupo: {nome_base}")
                print(f"   ✅ Mantendo: ID {id_to_keep} - {nomes[0]}")
                
                for i, id_to_remove in enumerate(ids_to_remove, 1):
                    print(f"   ❌ Removendo: ID {id_to_remove} - {nomes[i]}")
                    
                    # Remover todas as referências de chave estrangeira
                    try:
                        session.execute(
                            text("DELETE FROM agente_conexoes WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    try:
                        session.execute(
                            text("DELETE FROM agente_mensagens WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    try:
                        session.execute(
                            text("DELETE FROM avaliacao_agente WHERE agente_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    try:
                        session.execute(
                            text("DELETE FROM segunda_opiniao WHERE agente_original_id = :id OR agente_revisor_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    try:
                        session.execute(
                            text("DELETE FROM documento_carregado WHERE agent_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    try:
                        session.execute(
                            text("DELETE FROM analise_documento WHERE agente_id = :id"),
                            {"id": id_to_remove}
                        )
                    except:
                        pass
                    
                    # Agora remover o agente
                    session.execute(
                        text("DELETE FROM agente_juridico WHERE id = :id"),
                        {"id": id_to_remove}
                    )
                    total_removed += 1
        
        session.commit()
        print(f"\n🎉 {total_removed} agentes duplicados removidos com sucesso")
        
        # Verificar resultado final
        result = session.execute(text("SELECT COUNT(*) FROM agente_juridico"))
        total_remaining = result.scalar()
        print(f"📊 Agentes restantes: {total_remaining}")
        
        # Verificar se ainda há duplicatas
        result = session.execute(text("""
            SELECT COUNT(*) as grupos_duplicados FROM (
                SELECT REGEXP_REPLACE(nome, ' - (Sênior|Pleno|Júnior|Consultor|Analista).*$', '') as nome_base
                FROM agente_juridico 
                GROUP BY REGEXP_REPLACE(nome, ' - (Sênior|Pleno|Júnior|Consultor|Analista).*$', '')
                HAVING COUNT(*) > 1
            ) as duplicados
        """))
        
        remaining_duplicates = result.scalar()
        print(f"📈 Grupos duplicados restantes: {remaining_duplicates}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Removendo agentes com especialidades similares...")
    success = remove_duplicate_specialists()
    
    if success:
        print("✅ Remoção concluída!")
    else:
        print("❌ Falha na remoção")
        sys.exit(1)