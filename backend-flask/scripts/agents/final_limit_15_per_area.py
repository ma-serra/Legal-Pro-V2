#!/usr/bin/env python3
"""
Script final para limitar cada área a exatamente 15 agentes
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def final_limit_agents():
    """Limita cada área a exatamente 15 agentes"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar distribuição atual
        result = session.execute(text("""
            SELECT c.nome, COUNT(a.id) as total, array_agg(a.id ORDER BY a.id) as ids
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON a.categoria_id = c.id
            GROUP BY c.id, c.nome
            HAVING COUNT(a.id) > 15
            ORDER BY COUNT(a.id) DESC
        """))
        
        areas_excesso = result.fetchall()
        print(f"🔍 Áreas com mais de 15 agentes: {len(areas_excesso)}")
        
        total_removed = 0
        
        for area_nome, total, ids in areas_excesso:
            ids_to_remove = ids[15:]  # Manter apenas os 15 primeiros IDs
            
            print(f"\n📝 {area_nome}: {total} → 15 agentes (removendo {len(ids_to_remove)})")
            
            for agent_id in ids_to_remove:
                # Remover referências primeiro
                try:
                    session.execute(
                        text("DELETE FROM agente_conexoes WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                        {"id": agent_id}
                    )
                except:
                    pass
                
                try:
                    session.execute(
                        text("DELETE FROM agente_mensagens WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                        {"id": agent_id}
                    )
                except:
                    pass
                
                # Remover agente
                session.execute(
                    text("DELETE FROM agente_juridico WHERE id = :id"),
                    {"id": agent_id}
                )
                total_removed += 1
                print(f"   ❌ Removido ID {agent_id}")
        
        session.commit()
        print(f"\n🎉 {total_removed} agentes removidos")
        
        # Verificar resultado final
        result = session.execute(text("""
            SELECT c.nome, COUNT(a.id) as total
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON a.categoria_id = c.id
            GROUP BY c.id, c.nome
            ORDER BY total DESC
        """))
        
        areas_final = result.fetchall()
        print(f"\n📊 Distribuição final:")
        total_agentes = 0
        for area, count in areas_final:
            print(f"   {area}: {count} agentes")
            total_agentes += count
        
        print(f"\n📈 Total final: {total_agentes} agentes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Limitação final para 15 agentes por área...")
    success = final_limit_agents()
    
    if success:
        print("✅ Limitação final concluída!")
    else:
        print("❌ Falha na limitação final")
        sys.exit(1)