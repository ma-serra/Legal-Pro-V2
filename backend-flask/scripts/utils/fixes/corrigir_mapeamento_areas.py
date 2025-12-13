"""
Script para corrigir o mapeamento de áreas jurídicas e padronizar rotas
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Obtém conexão com o banco de dados"""
    database_url = os.environ.get('DATABASE_URL')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def corrigir_areas_criminais():
    """Corrige templates criminais que estão como 'geral'"""
    session, engine = get_database_connection()
    
    try:
        # Identificar templates criminais baseado no nome
        templates_criminais = [
            'Petição Inicial Criminal', 'Defesa Prévia', 'Habeas Corpus',
            'Alegações Finais', 'Recurso de Apelação', 'Parecer Criminal',
            'Recurso Criminal', 'Medida Protetiva', 'Sustentação Oral',
            'Denúncia Criminal', 'Petição de Liberdade Provisória',
            'Memoriais do Júri', 'Embargos de Declaração', 'Recurso Especial',
            'Recurso Extraordinário', 'Mandado de Segurança', 'Queixa-Crime'
        ]
        
        for nome_template in templates_criminais:
            # Atualizar área jurídica e rotas
            update_query = text("""
                UPDATE template_juridico 
                SET 
                    area_juridica = 'Direito Penal',
                    rota_detalhe = REPLACE(rota_detalhe, '/geral/', '/criminal/'),
                    rota_editar = REPLACE(rota_editar, '/geral/', '/criminal/'),
                    rota_utilizar = REPLACE(rota_utilizar, '/geral/', '/criminal/'),
                    modificado_em = CURRENT_TIMESTAMP
                WHERE nome = :nome_template AND ativo = true
            """)
            
            result = session.execute(update_query, {'nome_template': nome_template})
            if result.rowcount > 0:
                logger.info(f"✅ Corrigido: {nome_template}")
        
        session.commit()
        logger.info("✅ Templates criminais corrigidos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir templates criminais: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def validar_consistencia_rotas():
    """Valida consistência das rotas"""
    session, engine = get_database_connection()
    
    try:
        # Verificar rotas inconsistentes
        inconsistencias = session.execute(text("""
            SELECT id, nome, area_juridica, rota_detalhe, rota_editar, rota_utilizar
            FROM template_juridico 
            WHERE ativo = true 
            AND (
                (area_juridica = 'Direito Penal' AND rota_detalhe NOT LIKE '%/criminal/%') OR
                (area_juridica = 'Direito Empresarial' AND rota_detalhe NOT LIKE '%/empresarial/%') OR
                (area_juridica = 'Direito Trabalhista' AND rota_detalhe NOT LIKE '%/trabalhista/%') OR
                (area_juridica = 'Direito Bancário' AND rota_detalhe NOT LIKE '%/bancario/%') OR
                (area_juridica = 'Direito Agrário' AND rota_detalhe NOT LIKE '%/agrario/%') OR
                (area_juridica = 'Direito do Consumidor' AND rota_detalhe NOT LIKE '%/consumidor/%') OR
                (area_juridica = 'Recuperação de Crédito' AND rota_detalhe NOT LIKE '%/recuperacao/%')
            )
        """)).fetchall()
        
        if inconsistencias:
            logger.warning(f"⚠️  {len(inconsistencias)} inconsistências encontradas:")
            for inc in inconsistencias:
                logger.warning(f"   Template {inc[0]} ({inc[1]}): {inc[2]} -> {inc[3]}")
        else:
            logger.info("✅ Todas as rotas estão consistentes")
        
        return len(inconsistencias) == 0
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}")
        return False
    finally:
        session.close()

def gerar_relatorio_rotas():
    """Gera relatório final das rotas"""
    session, engine = get_database_connection()
    
    try:
        # Estatísticas por área
        stats = session.execute(text("""
            SELECT 
                area_juridica,
                COUNT(*) as total,
                COUNT(CASE WHEN rota_detalhe IS NOT NULL THEN 1 END) as com_rotas
            FROM template_juridico 
            WHERE ativo = true 
            GROUP BY area_juridica
            ORDER BY area_juridica
        """)).fetchall()
        
        logger.info("📊 RELATÓRIO FINAL DE ROTAS:")
        logger.info("=" * 50)
        
        total_geral = 0
        total_com_rotas = 0
        
        for stat in stats:
            area = stat[0] or 'Não Definida'
            total = stat[1]
            com_rotas = stat[2]
            percentual = (com_rotas/total*100) if total > 0 else 0
            
            total_geral += total
            total_com_rotas += com_rotas
            
            logger.info(f"{area:.<30} {com_rotas:>3}/{total:<3} ({percentual:>5.1f}%)")
        
        logger.info("=" * 50)
        percentual_geral = (total_com_rotas/total_geral*100) if total_geral > 0 else 0
        logger.info(f"{'TOTAL':.<30} {total_com_rotas:>3}/{total_geral:<3} ({percentual_geral:>5.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no relatório: {e}")
        return False
    finally:
        session.close()

def main():
    """Função principal"""
    logger.info("🔧 Iniciando correção de mapeamentos de área...")
    
    # Corrigir templates criminais
    if not corrigir_areas_criminais():
        logger.error("❌ Falha na correção de templates criminais")
        return False
    
    # Validar consistência
    if not validar_consistencia_rotas():
        logger.warning("⚠️  Algumas inconsistências foram encontradas")
    
    # Gerar relatório
    gerar_relatorio_rotas()
    
    logger.info("✅ Correção de mapeamentos concluída!")
    return True

if __name__ == "__main__":
    main()