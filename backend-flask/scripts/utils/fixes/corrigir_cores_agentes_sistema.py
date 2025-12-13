"""
Script para corrigir cores e ícones de todos os agentes no sistema
Aplica cores consistentes baseadas nas áreas jurídicas
"""

import psycopg2
import os
from datetime import datetime

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def obter_cores_areas():
    """Define cores e ícones para cada área jurídica"""
    return {
        'Direito Civil': {'cor': '#3b82f6', 'icone': 'fas fa-balance-scale'},
        'Direito Criminal': {'cor': '#dc2626', 'icone': 'fas fa-gavel'},
        'Direito do Trabalho': {'cor': '#059669', 'icone': 'fas fa-hard-hat'},
        'Direito Trabalhista': {'cor': '#059669', 'icone': 'fas fa-hard-hat'},
        'Direito Empresarial': {'cor': '#7c3aed', 'icone': 'fas fa-building'},
        'Direito do Consumidor': {'cor': '#0891b2', 'icone': 'fas fa-shopping-cart'},
        'Direito de Família': {'cor': '#ec4899', 'icone': 'fas fa-heart'},
        'Direito Constitucional': {'cor': '#dc2626', 'icone': 'fas fa-landmark'},
        'Direito Administrativo': {'cor': '#7c2d12', 'icone': 'fas fa-university'},
        'Direito Tributário': {'cor': '#8b5cf6', 'icone': 'fas fa-calculator'},
        'Direito Previdenciário': {'cor': '#0369a1', 'icone': 'fas fa-user-shield'},
        'Direito Ambiental': {'cor': '#16a34a', 'icone': 'fas fa-leaf'},
        'Direito Bancário': {'cor': '#1d4ed8', 'icone': 'fas fa-university'},
        'Direito Imobiliário': {'cor': '#0f766e', 'icone': 'fas fa-home'},
        'Direito dos Seguros': {'cor': '#0f766e', 'icone': 'fas fa-shield-alt'},
        'Direito Securitário': {'cor': '#0f766e', 'icone': 'fas fa-shield-alt'},
        'Direito Digital': {'cor': '#6366f1', 'icone': 'fas fa-laptop'},
        'Direito Agrário': {'cor': '#a3a000', 'icone': 'fas fa-seedling'},
        'Resolução de Conflitos': {'cor': '#f59e0b', 'icone': 'fas fa-handshake'},
        'Análise de Riscos Jurídicos': {'cor': '#df3542', 'icone': 'fas fa-chart-line'}
    }

def atualizar_cores_agentes():
    """Atualiza cores e ícones de todos os agentes"""
    conn = conectar_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cores_areas = obter_cores_areas()
        
        # Buscar todos os agentes com suas categorias
        cursor.execute("""
            SELECT aj.id, aj.nome, c.nome as categoria, aj.cor_destaque, aj.icone
            FROM agente_juridico aj
            LEFT JOIN categoria_juridica c ON aj.categoria_id = c.id
            ORDER BY c.nome, aj.nome
        """)
        
        agentes = cursor.fetchall()
        agentes_atualizados = 0
        
        print(f"🔄 Atualizando cores de {len(agentes)} agentes...")
        
        for agente_id, nome, categoria, cor_atual, icone_atual in agentes:
            if categoria in cores_areas:
                nova_cor = cores_areas[categoria]['cor']
                novo_icone = cores_areas[categoria]['icone']
                
                # Atualizar apenas se não tem cor/ícone ou se está vazio
                precisa_atualizar = False
                
                if not cor_atual or cor_atual.strip() == '':
                    precisa_atualizar = True
                if not icone_atual or icone_atual.strip() == '':
                    precisa_atualizar = True
                
                if precisa_atualizar:
                    cursor.execute("""
                        UPDATE agente_juridico 
                        SET cor_destaque = %s, icone = %s
                        WHERE id = %s
                    """, (nova_cor, novo_icone, agente_id))
                    
                    agentes_atualizados += 1
                    print(f"✅ {nome} ({categoria}): {nova_cor} {novo_icone}")
        
        conn.commit()
        print(f"\n✅ {agentes_atualizados} agentes atualizados com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar agentes: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verificar_cores_aplicadas():
    """Verifica se as cores foram aplicadas corretamente"""
    conn = conectar_database()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Verificar agentes sem cor
        cursor.execute("""
            SELECT COUNT(*) 
            FROM agente_juridico 
            WHERE cor_destaque IS NULL OR cor_destaque = ''
        """)
        
        sem_cor = cursor.fetchone()[0]
        
        # Verificar agentes sem ícone
        cursor.execute("""
            SELECT COUNT(*) 
            FROM agente_juridico 
            WHERE icone IS NULL OR icone = ''
        """)
        
        sem_icone = cursor.fetchone()[0]
        
        # Total de agentes
        cursor.execute("SELECT COUNT(*) FROM agente_juridico")
        total = cursor.fetchone()[0]
        
        print(f"\n📊 Relatório de Cores:")
        print(f"   • Total de agentes: {total}")
        print(f"   • Agentes sem cor: {sem_cor}")
        print(f"   • Agentes sem ícone: {sem_icone}")
        print(f"   • Agentes completos: {total - max(sem_cor, sem_icone)}")
        
        if sem_cor == 0 and sem_icone == 0:
            print("✅ Todos os agentes têm cores e ícones definidos!")
        
    except Exception as e:
        print(f"❌ Erro ao verificar cores: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Função principal"""
    print("🎨 Correção de Cores e Ícones dos Agentes")
    print("=" * 50)
    
    if atualizar_cores_agentes():
        verificar_cores_aplicadas()
        print("\n✅ Correção de cores concluída com sucesso!")
    else:
        print("\n❌ Falha na correção de cores")

if __name__ == "__main__":
    main()