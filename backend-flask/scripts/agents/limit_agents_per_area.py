#!/usr/bin/env python3
"""
Script para limitar agentes por área e remover capacidades similares
Mantém apenas 15 cards por área, removendo os com ID maior
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from difflib import SequenceMatcher

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def similarity(a, b):
    """Calcula similaridade entre duas strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def are_capabilities_similar(caps1, caps2, threshold=0.7):
    """Verifica se duas listas de capacidades são similares"""
    if not caps1 or not caps2:
        return False
    
    # Converter para lista se for string JSON
    if isinstance(caps1, str):
        try:
            caps1 = json.loads(caps1)
        except:
            return False
    if isinstance(caps2, str):
        try:
            caps2 = json.loads(caps2)
        except:
            return False
    
    # Verificar similaridade entre capacidades
    similar_count = 0
    total_comparisons = 0
    
    for cap1 in caps1:
        for cap2 in caps2:
            total_comparisons += 1
            if similarity(cap1, cap2) > threshold:
                similar_count += 1
    
    if total_comparisons == 0:
        return False
    
    # Se mais de 50% das capacidades são similares
    return (similar_count / total_comparisons) > 0.5

def limit_agents_per_area():
    """Limita agentes por área e remove similaridades"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar estrutura da tabela para identificar como agrupar por área
        result = session.execute(text("SELECT * FROM agente_juridico LIMIT 1"))
        columns = [col for col in result.keys()]
        print(f"🔍 Colunas disponíveis: {columns}")
        
        # Buscar todos os agentes com suas áreas
        result = session.execute(text("""
            SELECT id, nome, classe, categoria_id, capacidades
            FROM agente_juridico 
            ORDER BY id
        """))
        
        agents = result.fetchall()
        print(f"📊 Total de agentes: {len(agents)}")
        
        # Buscar nomes das categorias
        result_cat = session.execute(text("SELECT id, nome FROM categoria_juridica"))
        categorias = {cat[0]: cat[1] for cat in result_cat.fetchall()}
        
        # Agrupar por categoria
        areas_dict = {}
        for agent in agents:
            agent_id, nome, classe, categoria_id, capacidades = agent
            area_key = categorias.get(categoria_id, classe or "Geral")
            
            if area_key not in areas_dict:
                areas_dict[area_key] = []
            
            areas_dict[area_key].append({
                'id': agent_id,
                'nome': nome,
                'classe': classe,
                'categoria_id': categoria_id,
                'capacidades': capacidades
            })
        
        total_removed = 0
        
        for area_name, area_agents in areas_dict.items():
            print(f"\n📝 Área: {area_name} ({len(area_agents)} agentes)")
            
            if len(area_agents) <= 15:
                print(f"   ✅ Área já tem {len(area_agents)} agentes (≤ 15)")
                continue
            
            # Remover agentes similares primeiro
            filtered_agents = []
            removed_similar = 0
            
            for current_agent in area_agents:
                is_similar = False
                
                # Verificar se é similar a algum agente já filtrado
                for existing_agent in filtered_agents:
                    # Verificar similaridade do nome
                    name_similarity = similarity(current_agent['nome'], existing_agent['nome'])
                    
                    # Verificar similaridade das capacidades
                    caps_similar = are_capabilities_similar(
                        current_agent['capacidades'], 
                        existing_agent['capacidades']
                    )
                    
                    if name_similarity > 0.8 or caps_similar:
                        is_similar = True
                        # Manter o agente com ID menor
                        if current_agent['id'] < existing_agent['id']:
                            # Remover o existente e adicionar o atual
                            filtered_agents.remove(existing_agent)
                            filtered_agents.append(current_agent)
                            print(f"   🔄 Substituindo ID {existing_agent['id']} por ID {current_agent['id']} (similar)")
                        else:
                            print(f"   ❌ Removendo ID {current_agent['id']} (similar ao ID {existing_agent['id']})")
                        removed_similar += 1
                        break
                
                if not is_similar:
                    filtered_agents.append(current_agent)
            
            print(f"   📊 Após remoção de similares: {len(filtered_agents)} agentes")
            
            # Se ainda há mais de 15, manter apenas os 15 com menor ID
            if len(filtered_agents) > 15:
                filtered_agents.sort(key=lambda x: x['id'])
                agents_to_keep = filtered_agents[:15]
                agents_to_remove = filtered_agents[15:]
                
                print(f"   📉 Limitando para 15 agentes (removendo {len(agents_to_remove)})")
                
                for agent in agents_to_remove:
                    # Remover referências primeiro
                    try:
                        session.execute(
                            text("DELETE FROM agente_conexoes WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                            {"id": agent['id']}
                        )
                        session.execute(
                            text("DELETE FROM agente_mensagens WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                            {"id": agent['id']}
                        )
                    except:
                        pass
                    
                    # Remover agente
                    session.execute(
                        text("DELETE FROM agente_juridico WHERE id = :id"),
                        {"id": agent['id']}
                    )
                    total_removed += 1
                    print(f"   ❌ Removido ID {agent['id']}: {agent['nome']}")
            else:
                # Remover apenas os similares identificados
                for agent in area_agents:
                    if agent not in filtered_agents:
                        try:
                            session.execute(
                                text("DELETE FROM agente_conexoes WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                                {"id": agent['id']}
                            )
                            session.execute(
                                text("DELETE FROM agente_mensagens WHERE agente_origem_id = :id OR agente_destino_id = :id"),
                                {"id": agent['id']}
                            )
                        except:
                            pass
                        
                        session.execute(
                            text("DELETE FROM agente_juridico WHERE id = :id"),
                            {"id": agent['id']}
                        )
                        total_removed += 1
        
        session.commit()
        print(f"\n🎉 {total_removed} agentes removidos com sucesso")
        
        # Verificar resultado final
        result = session.execute(text("SELECT COUNT(*) FROM agente_juridico"))
        total_remaining = result.scalar()
        print(f"📊 Agentes restantes: {total_remaining}")
        
        # Mostrar distribuição final por área
        result = session.execute(text("""
            SELECT c.nome, COUNT(a.id) as total
            FROM categoria_juridica c
            LEFT JOIN agente_juridico a ON a.categoria_id = c.id
            GROUP BY c.id, c.nome
            ORDER BY total DESC
        """))
        
        areas_final = result.fetchall()
        print(f"\n📈 Distribuição final por área:")
        for area, count in areas_final:
            print(f"   {area}: {count} agentes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Limitando agentes por área e removendo similaridades...")
    success = limit_agents_per_area()
    
    if success:
        print("✅ Limitação concluída!")
    else:
        print("❌ Falha na limitação")
        sys.exit(1)