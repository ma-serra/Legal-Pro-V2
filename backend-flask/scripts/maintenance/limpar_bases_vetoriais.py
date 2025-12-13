"""
Script para manter apenas as 17 bases vetoriais especificadas
Remove todas as outras tabelas de embedding desnecessárias
"""

import os
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista das bases vetoriais que devem ser mantidas
BASES_PARA_MANTER = {
    'embeddings_direito_penal_integrado',
    'embeddings_direito_civil', 
    'embeddings_direito_agrario',
    'embeddings_direito_ambiental',
    'embeddings_direito_tributario',
    'embeddings_direito_constitucional',
    'embeddings_direito_administrativo',
    'embeddings_direito_familia',
    'embeddings_direito_sucessorio',
    'embeddings_direito_empresarial',
    'embeddings_direito_trabalhista',
    'embeddings_direito_previdenciario',
    'embeddings_direito_consumidor',
    'embeddings_direito_imobiliario',
    'embeddings_direito_digital',
    'embeddings_seguros',
    'embeddings_conflitos_mediacao'
}

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None

def listar_todas_tabelas_embedding():
    """Lista todas as tabelas de embedding existentes"""
    conn = conectar_database()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name LIKE '%embedding%' 
            ORDER BY table_name
        """)
        
        tabelas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return tabelas
        
    except Exception as e:
        logger.error(f"Erro ao listar tabelas: {e}")
        return []

def identificar_tabelas_para_remover(todas_tabelas):
    """Identifica quais tabelas devem ser removidas"""
    tabelas_para_remover = []
    tabelas_para_manter_encontradas = []
    
    for tabela in todas_tabelas:
        if tabela in BASES_PARA_MANTER:
            tabelas_para_manter_encontradas.append(tabela)
        else:
            tabelas_para_remover.append(tabela)
    
    return tabelas_para_remover, tabelas_para_manter_encontradas

def verificar_dependencias(tabela_nome):
    """Verifica se a tabela tem dependências (foreign keys, views, etc.)"""
    conn = conectar_database()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Verificar foreign keys que referenciam esta tabela
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND ccu.table_name = %s
        """, (tabela_nome,))
        
        dependencias = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dependencias
        
    except Exception as e:
        logger.error(f"Erro ao verificar dependências de {tabela_nome}: {e}")
        return []

def contar_registros_tabela(tabela_nome):
    """Conta registros em uma tabela antes de removê-la"""
    conn = conectar_database()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabela_nome}")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
        
    except Exception as e:
        logger.error(f"Erro ao contar registros de {tabela_nome}: {e}")
        return 0

def remover_tabela_segura(tabela_nome):
    """Remove uma tabela de forma segura"""
    conn = conectar_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Contar registros antes da remoção
        count = contar_registros_tabela(tabela_nome)
        
        # Verificar dependências
        dependencias = verificar_dependencias(tabela_nome)
        if dependencias:
            logger.warning(f"⚠️ Tabela {tabela_nome} tem dependências: {dependencias}")
        
        # Remover tabela com CASCADE para lidar com dependências
        cursor.execute(f"DROP TABLE IF EXISTS {tabela_nome} CASCADE")
        conn.commit()
        
        logger.info(f"✅ Tabela {tabela_nome} removida ({count} registros)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao remover tabela {tabela_nome}: {e}")
        return False

def gerar_relatorio_final():
    """Gera relatório final das bases vetoriais mantidas"""
    conn = conectar_database()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - BASES VETORIAIS MANTIDAS")
        print("="*70)
        
        total_registros = 0
        bases_encontradas = 0
        
        for base in sorted(BASES_PARA_MANTER):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {base}")
                count = cursor.fetchone()[0]
                print(f"✅ {base}: {count:,} registros")
                total_registros += count
                bases_encontradas += 1
            except Exception as e:
                print(f"❌ {base}: Não encontrada")
        
        print("-" * 70)
        print(f"Total de bases mantidas: {bases_encontradas}/{len(BASES_PARA_MANTER)}")
        print(f"Total de registros: {total_registros:,}")
        print("="*70)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando limpeza das bases vetoriais...")
    
    # 1. Listar todas as tabelas de embedding
    todas_tabelas = listar_todas_tabelas_embedding()
    if not todas_tabelas:
        logger.error("❌ Nenhuma tabela de embedding encontrada")
        return
    
    logger.info(f"📊 Encontradas {len(todas_tabelas)} tabelas de embedding")
    
    # 2. Identificar tabelas para remover
    tabelas_para_remover, tabelas_mantidas = identificar_tabelas_para_remover(todas_tabelas)
    
    logger.info(f"🎯 Manter: {len(tabelas_mantidas)} tabelas")
    logger.info(f"🗑️ Remover: {len(tabelas_para_remover)} tabelas")
    
    if not tabelas_para_remover:
        logger.info("✅ Não há tabelas desnecessárias para remover")
        gerar_relatorio_final()
        return
    
    # 3. Exibir tabelas que serão mantidas
    print("\n📌 TABELAS QUE SERÃO MANTIDAS:")
    for tabela in sorted(tabelas_mantidas):
        print(f"  ✅ {tabela}")
    
    # 4. Exibir tabelas que serão removidas
    print(f"\n🗑️ TABELAS QUE SERÃO REMOVIDAS ({len(tabelas_para_remover)}):")
    for tabela in sorted(tabelas_para_remover):
        count = contar_registros_tabela(tabela)
        print(f"  ❌ {tabela} ({count} registros)")
    
    # 5. Confirmação de segurança
    print(f"\n⚠️ ATENÇÃO: {len(tabelas_para_remover)} tabelas serão PERMANENTEMENTE removidas!")
    resposta = input("Confirma a remoção? Digite 'CONFIRMAR' para prosseguir: ")
    
    if resposta != 'CONFIRMAR':
        logger.info("❌ Operação cancelada pelo usuário")
        return
    
    # 6. Remover tabelas desnecessárias
    logger.info("🗑️ Iniciando remoção das tabelas desnecessárias...")
    
    removidas_com_sucesso = 0
    total_registros_removidos = 0
    
    for tabela in tabelas_para_remover:
        count = contar_registros_tabela(tabela)
        if remover_tabela_segura(tabela):
            removidas_com_sucesso += 1
            total_registros_removidos += count
        else:
            logger.error(f"❌ Falha ao remover {tabela}")
    
    # 7. Relatório final
    logger.info(f"✅ Limpeza concluída:")
    logger.info(f"  • {removidas_com_sucesso}/{len(tabelas_para_remover)} tabelas removidas")
    logger.info(f"  • {total_registros_removidos:,} registros removidos")
    logger.info(f"  • {len(tabelas_mantidas)} bases vetoriais mantidas")
    
    gerar_relatorio_final()

if __name__ == "__main__":
    main()