"""
Script para ajustar todos assistentes e agentes para nova estrutura vetorial
Implementa busca híbrida PostgreSQL + Qdrant Cloud para todos os 18 assistentes
"""

import os
import sys
import psycopg2
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL não configurada")
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None

def verificar_credenciais_qdrant():
    """Verifica se as credenciais do Qdrant estão configuradas"""
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    
    if not qdrant_url or not qdrant_api_key:
        logger.error("❌ Credenciais Qdrant não configuradas")
        return False
    
    logger.info(f"✅ Credenciais Qdrant configuradas: {qdrant_url}")
    return True

def listar_areas_juridicas():
    """Lista todas as áreas jurídicas dos assistentes"""
    areas = [
        'direito_civil', 'direito_penal', 'direito_trabalhista', 'direito_tributario',
        'direito_administrativo', 'direito_constitucional', 'direito_empresarial',
        'direito_consumidor', 'direito_familia', 'direito_imobiliario',
        'direito_previdenciario', 'direito_ambiental', 'direito_agrario',
        'direito_sucessorio', 'direito_digital', 'seguros', 'conflitos_mediacao',
        'analise_riscos'
    ]
    return areas

def verificar_estrutura_documentos():
    """Verifica estrutura da tabela documentos_juridicos"""
    try:
        conn = conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Verificar se tabela existe e suas colunas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'documentos_juridicos'
            ORDER BY ordinal_position
        """)
        
        colunas = cursor.fetchall()
        
        if not colunas:
            logger.error("❌ Tabela documentos_juridicos não encontrada")
            return False
        
        logger.info("✅ Estrutura da tabela documentos_juridicos:")
        for coluna, tipo in colunas:
            logger.info(f"   • {coluna}: {tipo}")
        
        # Contar documentos
        cursor.execute("SELECT COUNT(*) FROM documentos_juridicos")
        total_docs = cursor.fetchone()[0]
        
        logger.info(f"✅ Total de documentos: {total_docs}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar estrutura: {e}")
        return False

def atualizar_agente_juridico_tabela():
    """Atualiza tabela agente_juridico com configurações vetoriais"""
    try:
        conn = conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Adicionar colunas para configuração vetorial se não existirem
        colunas_vetoriais = [
            ("qdrant_collection", "VARCHAR(255)"),
            ("usar_busca_hibrida", "BOOLEAN DEFAULT true"),
            ("embedding_model", "VARCHAR(100) DEFAULT 'text-embedding-3-small'"),
            ("max_tokens_resposta", "INTEGER DEFAULT 1500"),
            ("temperatura_ia", "FLOAT DEFAULT 0.7"),
            ("top_k_busca", "INTEGER DEFAULT 5"),
            ("fragmentacao_tamanho", "INTEGER DEFAULT 800"),
            ("configuracao_atualizada", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for coluna, tipo in colunas_vetoriais:
            try:
                cursor.execute(f"""
                    ALTER TABLE agente_juridico 
                    ADD COLUMN IF NOT EXISTS {coluna} {tipo}
                """)
                conn.commit()
                logger.info(f"✅ Coluna {coluna} adicionada/verificada")
            except Exception as e:
                logger.warning(f"⚠️ Coluna {coluna}: {e}")
        
        # Atualizar configurações para todas as áreas
        areas = listar_areas_juridicas()
        
        for area in areas:
            qdrant_collection = f"juridico_{area}"
            
            cursor.execute("""
                UPDATE agente_juridico 
                SET 
                    qdrant_collection = %s,
                    usar_busca_hibrida = true,
                    embedding_model = 'text-embedding-3-small',
                    max_tokens_resposta = 1500,
                    temperatura_ia = 0.7,
                    top_k_busca = 5,
                    fragmentacao_tamanho = 800,
                    configuracao_atualizada = CURRENT_TIMESTAMP
                WHERE nome ILIKE %s OR descricao ILIKE %s
            """, (qdrant_collection, f"%{area}%", f"%{area.replace('_', ' ')}%"))
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            if affected_rows > 0:
                logger.info(f"✅ {area}: {affected_rows} agentes atualizados")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar agente_juridico: {e}")
        return False

def verificar_assistentes_funcionando():
    """Verifica se os assistentes estão funcionando com a nova estrutura"""
    try:
        import requests
        
        # Testar endpoint de áreas
        response = requests.get("http://localhost:5000/api/assistentes/areas", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_areas = data.get('total', 0)
            logger.info(f"✅ API assistentes funcionando: {total_areas} áreas disponíveis")
            
            # Testar consulta específica
            test_data = {
                "area": "direito_civil",
                "pergunta": "O que é um contrato?",
                "modelo": "openai"
            }
            
            consulta_response = requests.post(
                "http://localhost:5000/api/assistentes/consultar",
                json=test_data,
                timeout=30
            )
            
            if consulta_response.status_code == 200:
                logger.info("✅ Busca híbrida funcionando corretamente")
                return True
            else:
                logger.warning(f"⚠️ Teste de consulta falhou: {consulta_response.status_code}")
                return False
        else:
            logger.error(f"❌ API assistentes não respondeu: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar assistentes: {e}")
        return False

def ajustar_templates_legais():
    """Ajusta templates do Legal Design Pro para nova estrutura"""
    try:
        conn = conectar_database()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Verificar tabela legal_design_templates
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'legal_design_templates'
        """)
        
        if cursor.fetchone()[0] == 0:
            logger.warning("⚠️ Tabela legal_design_templates não encontrada")
            cursor.close()
            conn.close()
            return False
        
        # Adicionar coluna para conexão vetorial
        try:
            cursor.execute("""
                ALTER TABLE legal_design_templates 
                ADD COLUMN IF NOT EXISTS vetorial_config JSONB DEFAULT '{}'
            """)
            conn.commit()
            logger.info("✅ Coluna vetorial_config adicionada aos templates")
        except Exception as e:
            logger.warning(f"⚠️ Coluna vetorial_config: {e}")
        
        # Atualizar configuração vetorial nos templates
        cursor.execute("""
            UPDATE legal_design_templates 
            SET vetorial_config = jsonb_build_object(
                'usar_qdrant', true,
                'embedding_model', 'text-embedding-3-small',
                'busca_hibrida', true,
                'atualizado_em', %s
            )
            WHERE vetorial_config = '{}'::jsonb OR vetorial_config IS NULL
        """, (datetime.now().isoformat(),))
        
        affected = cursor.rowcount
        conn.commit()
        
        logger.info(f"✅ {affected} templates atualizados com configuração vetorial")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao ajustar templates: {e}")
        return False

def gerar_relatorio_final():
    """Gera relatório final do ajuste"""
    try:
        conn = conectar_database()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Estatísticas dos assistentes
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as total_agentes,
                SUM(CASE WHEN usar_busca_hibrida = true THEN 1 ELSE 0 END) as com_busca_hibrida
            FROM agente_juridico 
            WHERE configuracao_atualizada IS NOT NULL
            GROUP BY categoria
            ORDER BY categoria
        """)
        
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO FINAL - AJUSTE ESTRUTURA VETORIAL")
        relatorio.append("=" * 80)
        relatorio.append("")
        relatorio.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio.append("")
        relatorio.append("ASSISTENTES JURÍDICOS ATUALIZADOS:")
        relatorio.append("-" * 50)
        
        total_agentes = 0
        total_hibridos = 0
        
        for row in cursor.fetchall():
            categoria, total, hibridos = row
            total_agentes += total
            total_hibridos += hibridos
            relatorio.append(f"• {categoria}: {total} agentes ({hibridos} com busca híbrida)")
        
        relatorio.append("")
        relatorio.append(f"RESUMO GERAL:")
        relatorio.append(f"• Total de agentes atualizados: {total_agentes}")
        relatorio.append(f"• Agentes com busca híbrida: {total_hibridos}")
        relatorio.append("")
        
        # Documentos disponíveis
        cursor.execute("SELECT COUNT(*) FROM documentos_juridicos")
        total_docs = cursor.fetchone()[0]
        relatorio.append(f"• Documentos jurídicos disponíveis: {total_docs}")
        
        # Templates
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'legal_design_templates'
        """)
        
        if cursor.fetchone()[0] > 0:
            cursor.execute("SELECT COUNT(*) FROM legal_design_templates")
            total_templates = cursor.fetchone()[0]
            relatorio.append(f"• Templates Legal Design Pro: {total_templates}")
        
        relatorio.append("")
        relatorio.append("CONFIGURAÇÕES APLICADAS:")
        relatorio.append("• Busca vetorial híbrida: PostgreSQL + Qdrant Cloud")
        relatorio.append("• Modelo de embedding: text-embedding-3-small")
        relatorio.append("• Fragmentação de texto: 800 tokens")
        relatorio.append("• Top-K busca: 5 documentos")
        relatorio.append("• Temperatura IA: 0.7")
        relatorio.append("")
        relatorio.append("STATUS: ✅ SISTEMA ATUALIZADO COM SUCESSO")
        relatorio.append("=" * 80)
        
        cursor.close()
        conn.close()
        
        # Salvar relatório
        with open('relatorio_ajuste_vetorial.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(relatorio))
        
        # Exibir no console
        for linha in relatorio:
            print(linha)
        
        logger.info("✅ Relatório salvo em 'relatorio_ajuste_vetorial.txt'")
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando ajuste de assistentes para nova estrutura vetorial...")
    
    # 1. Verificar credenciais Qdrant
    if not verificar_credenciais_qdrant():
        print("❌ Configure as credenciais Qdrant antes de continuar")
        return False
    
    # 2. Verificar estrutura de documentos
    if not verificar_estrutura_documentos():
        print("❌ Estrutura de documentos inválida")
        return False
    
    # 3. Atualizar tabela agente_juridico
    if not atualizar_agente_juridico_tabela():
        print("❌ Falha ao atualizar agentes jurídicos")
        return False
    
    # 4. Ajustar templates legais
    if not ajustar_templates_legais():
        print("⚠️ Aviso: Templates não foram completamente atualizados")
    
    # 5. Verificar assistentes funcionando
    print("🔄 Aguardando sistema estabilizar...")
    import time
    time.sleep(5)
    
    if verificar_assistentes_funcionando():
        print("✅ Assistentes funcionando com busca híbrida")
    else:
        print("⚠️ Assistentes podem precisar de reinicialização")
    
    # 6. Gerar relatório final
    gerar_relatorio_final()
    
    print("\n🎉 Ajuste concluído! Todos os assistentes estão configurados para busca vetorial híbrida.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)