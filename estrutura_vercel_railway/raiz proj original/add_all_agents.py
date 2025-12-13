#!/usr/bin/env python3
"""
Script simplificado para adicionar todos os agentes ao banco de dados
"""

import os
import psycopg2
from datetime import datetime

# Conectar ao banco usando a variável de ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

# Lista completa de agentes a serem inseridos
AGENTES = [
    # DIREITO PENAL
    ('Especialista em Direito Penal', 'especialista_direito_criminal', 'Análise de casos criminais com foco no Código Penal e jurisprudência.', 1, 'fas fa-balance-scale-right', '#c41e3a'),
    ('Especialista em Júri Criminal', 'especialista_juri_criminal', 'Análise de casos de tribunal do júri e preparação de estratégias de defesa.', 1, 'fas fa-user-friends', '#c41e3a'),
    ('Analista de Evidências Criminais', 'analista_evidencias_criminais', 'Avaliação crítica de provas e evidências em processos criminais.', 1, 'fas fa-microscope', '#c41e3a'),
    ('Especialista em Execução Penal', 'especialista_execucao_penal', 'Análise de processos de execução, progressão de regime e direitos do apenado.', 1, 'fas fa-user-lock', '#c41e3a'),
    ('Especialista em Defesa Criminal', 'especialista_defesa_criminal', 'Análise técnica de defesas criminais e estratégias processuais.', 1, 'fas fa-shield-alt', '#c41e3a'),
    ('Especialista em Crimes de Trânsito', 'especialista_crimes_transito', 'Análise de casos envolvendo delitos de trânsito, homicídio culposo e CTB.', 1, 'fas fa-car-crash', '#c41e3a'),
    ('Especialista em Crimes de Drogas', 'especialista_crimes_drogas', 'Análise técnica de casos de tráfico e posse de entorpecentes, Lei 11.343/06.', 1, 'fas fa-pills', '#c41e3a'),
    ('Especialista em Violência Doméstica', 'especialista_violencia_domestica', 'Análise de casos de violência doméstica e familiar, Lei Maria da Penha.', 1, 'fas fa-home', '#c41e3a'),
    
    # DIREITO BANCÁRIO
    ('Especialista em Direito Bancário', 'especialista_direito_bancario', 'Análise de contratos bancários, operações financeiras e regulamentação do SFN.', 4, 'fas fa-university', '#b8860b'),
    ('Gestor de Contencioso Bancário', 'gestor_contencioso_bancario', 'Estratégias processuais, execução de garantias e recuperação de crédito.', 4, 'fas fa-money-bill-wave', '#b8860b'),
    ('Gestor de Compliance Bancário', 'gestor_compliance_bancario', 'Monitoramento e interpretação de normas BACEN, CVM e adequação regulatória.', 4, 'fas fa-shield-virus', '#b8860b'),
    ('Analista de Revisão Contratual Bancária', 'analista_revisao_contratual_bancaria', 'Detecção de cláusulas abusivas, anatocismo e práticas ilegais em contratos.', 4, 'fas fa-file-contract', '#b8860b'),
    ('Agente de Defesa do Consumidor Bancário', 'agente_defesa_consumidor_bancario', 'Demandas contra práticas bancárias abusivas, PROCON e BACEN.', 4, 'fas fa-user-shield', '#b8860b'),
    ('Consultor em Mercado de Capitais', 'consultor_mercado_capitais', 'Especialista em mercado de capitais e valores mobiliários.', 4, 'fas fa-chart-line', '#b8860b'),
    
    # DIREITO EMPRESARIAL
    ('Especialista em Direito Empresarial', 'especialista_direito_empresarial', 'Análise de contratos empresariais, sociedades e direito comercial.', 2, 'fas fa-building', '#1565c0'),
    ('Agente de Compliance e Governança', 'agente_compliance_governanca', 'Estruturação de boas práticas, políticas internas e conformidade regulatória.', 2, 'fas fa-clipboard-check', '#1565c0'),
    ('Especialista em Startups e VC', 'especialista_startups_venture_capital', 'Estruturação jurídica de startups e operações com investidores anjo.', 2, 'fas fa-rocket', '#1565c0'),
    ('Agente de Recuperação Empresarial', 'agente_recuperacao_empresarial', 'Empresas em crise, negociações com credores e recuperação judicial.', 2, 'fas fa-chart-area', '#1565c0'),
    
    # DIREITO DO CONSUMIDOR
    ('Especialista em Direito do Consumidor', 'especialista_direito_consumidor', 'Análise de relações de consumo, CDC e defesa do consumidor.', 5, 'fas fa-shopping-cart', '#ec7000'),
    ('Agente de Litígios Coletivos', 'agente_litigios_coletivos', 'Identifica práticas abusivas e estrutura ações civis públicas.', 5, 'fas fa-bullhorn', '#ec7000'),
    ('Especialista em Conciliação', 'especialista_atendimento_conciliacao', 'Resolução amigável de conflitos entre consumidores e empresas.', 5, 'fas fa-handshake', '#ec7000'),
    ('Agente de Fiscalização', 'agente_fiscalizacao_sancoes', 'Autuações PROCON, ANATEL e ANVISA, defesas administrativas.', 5, 'fas fa-search-plus', '#ec7000'),
    
    # DIREITO TRABALHISTA
    ('Especialista em Direito Trabalhista', 'especialista_direito_trabalhista', 'Análise de relações trabalhistas, CLT e jurisprudência trabalhista.', 3, 'fas fa-hard-hat', '#a94513'),
    
    # RECUPERAÇÃO DE CRÉDITO
    ('Especialista em Recuperação de Crédito', 'especialista_recuperacao_credito', 'Estratégias de cobrança, execução fiscal e recuperação judicial.', 6, 'fas fa-coins', '#455a64'),
    
    # DIREITO SECURITÁRIO
    ('Especialista em Direito Securitário', 'especialista_direito_securitario', 'Análise de contratos de seguros, resseguros e regulamentação SUSEP.', 7, 'fas fa-shield-check', '#3f51b5'),
    ('Gestor de Compliance SUSEP', 'gestor_compliance_susep', 'Monitoramento regulatório SUSEP e adequação às normas securitárias.', 7, 'fas fa-bell', '#3f51b5'),
    ('Gestor de Sinistros Securitários', 'gestor_sinistros_securitario', 'Análise técnica de sinistros, liquidação e disputas entre seguradoras.', 7, 'fas fa-file-medical', '#3f51b5'),
    ('Gestor de Contencioso Securitário', 'gestor_contencioso_securitario', 'Litígios securitários, ações regressivas e estratégias de defesa.', 7, 'fas fa-balance-scale', '#3f51b5'),
    
    # DIREITO AGRÁRIO
    ('Agente de Regularização Fundiária', 'agente_regularizacao_fundiaria', 'Especialista em regularização de imóveis rurais, INCRA e órgãos estaduais.', 8, 'fas fa-map', '#00734d'),
    ('Especialista em Contratos Rurais', 'especialista_contratos_rurais', 'Elaboração e análise de contratos do agronegócio, arrendamento e parceria rural.', 8, 'fas fa-tractor', '#00734d'),
    ('Consultor em Crédito Rural', 'consultor_credito_rural', 'Financiamento agrícola, subvenções BNDES e PRONAF, linhas de crédito.', 8, 'fas fa-hand-holding-usd', '#2e7d32'),
]

def adicionar_agentes():
    """Adiciona todos os agentes ao banco de dados"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔄 Conectado ao banco de dados")
        
        # Primeiro, verificar e criar categorias se necessário
        categorias = {
            1: ('Direito Penal', 'Categoria para agentes de Direito Penal'),
            2: ('Direito Empresarial', 'Categoria para agentes de Direito Empresarial'),
            3: ('Direito Trabalhista', 'Categoria para agentes de Direito Trabalhista'),
            4: ('Direito Bancário', 'Categoria para agentes de Direito Bancário'),
            5: ('Direito do Consumidor', 'Categoria para agentes de Direito do Consumidor'),
            6: ('Recuperação de Crédito', 'Categoria para agentes de Recuperação de Crédito'),
            7: ('Direito Securitário', 'Categoria para agentes de Direito Securitário'),
            8: ('Direito Agrário', 'Categoria para agentes de Direito Agrário'),
        }
        
        for cat_id, (nome, descricao) in categorias.items():
            cur.execute("SELECT id FROM categoria_juridica WHERE id = %s", (cat_id,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO categoria_juridica (id, nome, descricao, cor, ativo) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (cat_id, nome, descricao, '#333333', True))
                print(f"➕ Categoria criada: {nome}")
        
        conn.commit()
        
        # Agora inserir os agentes
        adicionados = 0
        atualizados = 0
        
        for nome, classe, descricao, categoria_id, icone, cor in AGENTES:
            # Verificar se já existe
            cur.execute("SELECT id FROM agente_juridico WHERE classe = %s", (classe,))
            agente_existe = cur.fetchone()
            
            if not agente_existe:
                # Inserir novo agente
                cur.execute("""
                    INSERT INTO agente_juridico 
                    (nome, classe, descricao, categoria_id, icone, cor_destaque, ativo, 
                     nivel_especializacao, modelo_ai, temperatura, top_p, max_tokens, 
                     data_criacao, data_atualizacao, template_prompt)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    nome, classe, descricao, categoria_id, icone, cor, True,
                    4, 'gpt-4', 0.7, 0.9, 2000,
                    datetime.now(), datetime.now(),
                    f'Você é um {nome}. {descricao}'
                ))
                adicionados += 1
                print(f"➕ Agente adicionado: {nome}")
            else:
                # Atualizar agente existente
                cur.execute("""
                    UPDATE agente_juridico 
                    SET nome = %s, descricao = %s, icone = %s, cor_destaque = %s, data_atualizacao = %s
                    WHERE classe = %s
                """, (nome, descricao, icone, cor, datetime.now(), classe))
                atualizados += 1
                print(f"🔄 Agente atualizado: {nome}")
        
        conn.commit()
        
        print(f"\n✅ Sincronização concluída!")
        print(f"➕ {adicionados} agentes adicionados")
        print(f"🔄 {atualizados} agentes atualizados")
        
        # Verificar total final
        cur.execute("SELECT COUNT(*) FROM agente_juridico")
        total = cur.fetchone()[0]
        print(f"📊 Total de agentes no banco: {total}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        raise e

if __name__ == '__main__':
    adicionar_agentes()