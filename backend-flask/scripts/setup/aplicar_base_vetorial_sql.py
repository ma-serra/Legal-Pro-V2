#!/usr/bin/env python3
"""
Script SQL direto para padronizar base vetorial dos agentes
"""

import os
import psycopg2
from datetime import datetime

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL não encontrada")
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def aplicar_padronizacao_base_vetorial():
    """Aplica padronização via SQL direto"""
    
    # Mapeamento de bases vetoriais corretas
    updates = [
        # Direito Penal/Criminal
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_penal' WHERE (nome ILIKE '%criminal%' OR nome ILIKE '%penal%' OR nome ILIKE '%júri%' OR nome ILIKE '%juri%' OR nome ILIKE '%defesa%' OR classe ILIKE '%criminal%' OR classe ILIKE '%penal%' OR classe ILIKE '%juri%' OR base_vetorial = 'direito_penal') AND ativo = true;", "Direito Penal"),
        
        # Direito Trabalhista
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_trabalhista' WHERE (nome ILIKE '%trabalhista%' OR nome ILIKE '%clt%' OR nome ILIKE '%fgts%' OR nome ILIKE '%ferias%' OR nome ILIKE '%horas%' OR nome ILIKE '%salario%' OR nome ILIKE '%rescisao%' OR classe ILIKE '%trabalhista%' OR base_vetorial = 'direito_trabalhista') AND ativo = true;", "Direito Trabalhista"),
        
        # Direito Tributário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_tributario' WHERE (nome ILIKE '%tributario%' OR nome ILIKE '%imposto%' OR nome ILIKE '%icms%' OR nome ILIKE '%ipi%' OR nome ILIKE '%iss%' OR nome ILIKE '%iptu%' OR nome ILIKE '%ipva%' OR nome ILIKE '%cofins%' OR nome ILIKE '%pis%' OR nome ILIKE '%csll%' OR classe ILIKE '%tributario%' OR base_vetorial = 'direito_tributario') AND ativo = true;", "Direito Tributário"),
        
        # Direito Bancário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_bancario' WHERE (nome ILIKE '%bancario%' OR nome ILIKE '%banco%' OR nome ILIKE '%financeiro%' OR nome ILIKE '%cartao%' OR nome ILIKE '%credito%' OR nome ILIKE '%capital%' OR classe ILIKE '%bancario%' OR base_vetorial = 'direito_bancario') AND ativo = true;", "Direito Bancário"),
        
        # Direito do Consumidor
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_consumidor' WHERE (nome ILIKE '%consumidor%' OR nome ILIKE '%cdc%' OR nome ILIKE '%procon%' OR nome ILIKE '%produtos%' OR nome ILIKE '%servicos%' OR nome ILIKE '%telefonia%' OR nome ILIKE '%planos%' OR nome ILIKE '%ecommerce%' OR classe ILIKE '%consumidor%' OR base_vetorial = 'direito_consumidor') AND ativo = true;", "Direito do Consumidor"),
        
        # Direito Imobiliário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_imobiliario' WHERE (nome ILIKE '%imobiliario%' OR nome ILIKE '%imovel%' OR nome ILIKE '%locacao%' OR nome ILIKE '%financiamento%' OR nome ILIKE '%compra%' OR nome ILIKE '%venda%' OR nome ILIKE '%condominio%' OR nome ILIKE '%usucapiao%' OR nome ILIKE '%registro%' OR classe ILIKE '%imobiliario%' OR base_vetorial = 'direito_imobiliario') AND ativo = true;", "Direito Imobiliário"),
        
        # Direito Empresarial
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_empresarial' WHERE (nome ILIKE '%empresarial%' OR nome ILIKE '%sociedade%' OR nome ILIKE '%startup%' OR nome ILIKE '%compliance%' OR nome ILIKE '%contratos%' OR nome ILIKE '%fusoes%' OR nome ILIKE '%aquisicoes%' OR nome ILIKE '%governanca%' OR nome ILIKE '%antitruste%' OR nome ILIKE '%joint%' OR nome ILIKE '%franquia%' OR classe ILIKE '%empresarial%' OR base_vetorial = 'direito_empresarial') AND ativo = true;", "Direito Empresarial"),
        
        # Direito Agrário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_agrario' WHERE (nome ILIKE '%agrario%' OR nome ILIKE '%rural%' OR nome ILIKE '%incra%' OR nome ILIKE '%mst%' OR nome ILIKE '%agricultura%' OR nome ILIKE '%agronegocio%' OR nome ILIKE '%reforma%' OR nome ILIKE '%recursos%' OR nome ILIKE '%hidricos%' OR nome ILIKE '%preservacao%' OR classe ILIKE '%agrario%' OR base_vetorial = 'direito_agrario') AND ativo = true;", "Direito Agrário"),
        
        # Direito Securitário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_securitario' WHERE (nome ILIKE '%securitario%' OR nome ILIKE '%seguro%' OR nome ILIKE '%susep%' OR nome ILIKE '%sinistro%' OR classe ILIKE '%securitario%' OR base_vetorial = 'direito_securitario') AND ativo = true;", "Direito Securitário"),
        
        # Direito Digital
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_digital' WHERE (nome ILIKE '%digital%' OR nome ILIKE '%tecnologia%' OR classe ILIKE '%digital%' OR base_vetorial = 'direito_digital') AND ativo = true;", "Direito Digital"),
        
        # Direito Previdenciário
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_previdenciario' WHERE (nome ILIKE '%previdenciario%' OR nome ILIKE '%previdencia%' OR nome ILIKE '%aposentadoria%' OR classe ILIKE '%previdenciario%' OR base_vetorial = 'direito_previdenciario') AND ativo = true;", "Direito Previdenciário"),
        
        # Negociação e Conflitos
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_negociacao_conflitos' WHERE (nome ILIKE '%mediacao%' OR nome ILIKE '%arbitragem%' OR nome ILIKE '%conciliacao%' OR nome ILIKE '%negociacao%' OR nome ILIKE '%acordos%' OR nome ILIKE '%vizinhanca%' OR nome ILIKE '%restaurativa%' OR nome ILIKE '%resolucao%' OR classe ILIKE '%mediacao%' OR classe ILIKE '%arbitragem%' OR classe ILIKE '%conciliacao%' OR base_vetorial = 'negociacao_conflitos') AND ativo = true;", "Negociação e Conflitos"),
        
        # Recuperação de Crédito
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_recuperacao_credito' WHERE (nome ILIKE '%credito%' OR nome ILIKE '%cobranca%' OR nome ILIKE '%recuperacao%' OR nome ILIKE '%protesto%' OR nome ILIKE '%bloqueio%' OR nome ILIKE '%penhora%' OR nome ILIKE '%execucao%' OR nome ILIKE '%falencia%' OR nome ILIKE '%insolvencia%' OR nome ILIKE '%leilao%' OR nome ILIKE '%precatorio%' OR nome ILIKE '%negativacao%' OR classe ILIKE '%credito%' OR classe ILIKE '%cobranca%' OR classe ILIKE '%recuperacao%' OR base_vetorial = 'recuperacao_credito') AND ativo = true;", "Recuperação de Crédito"),
        
        # Mapeamentos para classes específicas que podem estar sem base vetorial adequada
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_agrario' WHERE (nome ILIKE '%ambiental%' OR classe ILIKE '%ambiental%' OR base_vetorial = 'direito_ambiental') AND ativo = true;", "Direito Ambiental -> Agrário"),
        
        ("UPDATE agente_juridico SET base_vetorial = 'embeddings_direito_empresarial' WHERE (nome ILIKE '%risco%' OR classe ILIKE '%risco%' OR base_vetorial = 'analise_riscos') AND ativo = true;", "Análise de Riscos -> Empresarial")
    ]
    
    conn = conectar_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔧 Iniciando padronização de base vetorial...")
        
        total_atualizados = 0
        
        for sql, descricao in updates:
            try:
                cursor.execute(sql)
                rows_affected = cursor.rowcount
                total_atualizados += rows_affected
                print(f"✅ {descricao}: {rows_affected} agentes atualizados")
            except Exception as e:
                print(f"❌ Erro em {descricao}: {e}")
        
        # Commit das alterações
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("""
            SELECT base_vetorial, COUNT(*) as total
            FROM agente_juridico 
            WHERE ativo = true 
            GROUP BY base_vetorial 
            ORDER BY base_vetorial
        """)
        
        distribuicao = cursor.fetchall()
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"Total de agentes atualizados: {total_atualizados}")
        print(f"\nDistribuição por base vetorial:")
        
        for base, count in distribuicao:
            print(f"  {base}: {count} agentes")
        
        # Verificar agentes sem base vetorial adequada
        cursor.execute("""
            SELECT nome, classe, base_vetorial
            FROM agente_juridico 
            WHERE ativo = true 
            AND (base_vetorial IS NULL OR base_vetorial NOT LIKE 'embeddings_%')
            ORDER BY nome
        """)
        
        sem_base = cursor.fetchall()
        
        if sem_base:
            print(f"\n⚠️  Agentes que ainda precisam de ajuste manual:")
            for nome, classe, base in sem_base:
                print(f"  - {nome} ({classe}) -> {base}")
        else:
            print(f"\n✅ Todos os agentes têm base vetorial adequada!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante padronização: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Padronização de Base Vetorial via SQL")
    print("="*50)
    
    sucesso = aplicar_padronizacao_base_vetorial()
    
    if sucesso:
        print("\n🎉 Padronização concluída com sucesso!")
    else:
        print("\n❌ Falha na padronização.")