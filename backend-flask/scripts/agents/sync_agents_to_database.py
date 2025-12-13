#!/usr/bin/env python3
"""
Script para sincronizar todos os agentes do template index.html com o banco de dados
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import AgenteJuridico, CategoriaJuridica

# Definir todos os agentes especialistas do sistema
AGENTES_COMPLETOS = [
    # DIREITO PENAL (8 agentes)
    {
        'nome': 'Especialista em Direito Penal',
        'classe': 'especialista_direito_criminal',
        'descricao': 'Análise de casos criminais com foco no Código Penal e jurisprudência.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-balance-scale-right',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Direito Penal. Analise casos criminais com base no Código Penal brasileiro.',
        'especialidades': ['Código Penal', 'Jurisprudência Criminal', 'Doutrina Penal']
    },
    {
        'nome': 'Especialista em Júri Criminal',
        'classe': 'especialista_juri_criminal',
        'descricao': 'Análise de casos de tribunal do júri e preparação de estratégias de defesa.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-user-friends',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Tribunal do Júri. Foque em estratégias de defesa e análise de casos.',
        'especialidades': ['Tribunal do Júri', 'Estratégias de Defesa', 'Procedimento Penal']
    },
    {
        'nome': 'Analista de Evidências Criminais',
        'classe': 'analista_evidencias_criminais',
        'descricao': 'Avaliação crítica de provas e evidências em processos criminais.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-microscope',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um analista de evidências criminais. Avalie provas e evidências com rigor técnico.',
        'especialidades': ['Prova Pericial', 'Cadeia de Custódia', 'Valoração da Prova']
    },
    {
        'nome': 'Especialista em Execução Penal',
        'classe': 'especialista_execucao_penal',
        'descricao': 'Análise de processos de execução, progressão de regime e direitos do apenado.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-user-lock',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Execução Penal. Analise progressão de regime e direitos do apenado.',
        'especialidades': ['Lei de Execução Penal', 'Progressão de Regime', 'Benefícios']
    },
    {
        'nome': 'Especialista em Defesa Criminal',
        'classe': 'especialista_defesa_criminal',
        'descricao': 'Análise técnica de defesas criminais e estratégias processuais.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-shield-alt',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Defesa Criminal. Desenvolva estratégias defensivas eficazes.',
        'especialidades': ['Defesa Criminal', 'Estratégias Processuais', 'Recursos']
    },
    {
        'nome': 'Especialista em Crimes de Trânsito',
        'classe': 'especialista_crimes_transito',
        'descricao': 'Análise de casos envolvendo delitos de trânsito, homicídio culposo e CTB.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-car-crash',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Crimes de Trânsito. Analise delitos no contexto do CTB.',
        'especialidades': ['Crimes de Trânsito', 'CTB', 'Homicídio Culposo']
    },
    {
        'nome': 'Especialista em Crimes de Drogas',
        'classe': 'especialista_crimes_drogas',
        'descricao': 'Análise técnica de casos de tráfico e posse de entorpecentes, Lei 11.343/06.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-pills',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Crimes de Drogas. Analise casos com base na Lei 11.343/06.',
        'especialidades': ['Lei de Drogas', 'Tráfico', 'Posse de Entorpecentes']
    },
    {
        'nome': 'Especialista em Violência Doméstica',
        'classe': 'especialista_violencia_domestica',
        'descricao': 'Análise de casos de violência doméstica e familiar, Lei Maria da Penha.',
        'categoria_nome': 'Direito Penal',
        'icone': 'fas fa-home',
        'cor_destaque': '#c41e3a',
        'template_prompt': 'Você é um especialista em Violência Doméstica. Analise casos com base na Lei Maria da Penha.',
        'especialidades': ['Lei Maria da Penha', 'Violência Doméstica', 'Medidas Protetivas']
    },

    # DIREITO BANCÁRIO (6 agentes)
    {
        'nome': 'Especialista em Direito Bancário',
        'classe': 'especialista_direito_bancario',
        'descricao': 'Análise de contratos bancários, operações financeiras e regulamentação do SFN.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-university',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um especialista em Direito Bancário. Analise contratos e operações financeiras.',
        'especialidades': ['Contratos Bancários', 'SFN', 'Operações Financeiras']
    },
    {
        'nome': 'Gestor de Contencioso Bancário',
        'classe': 'gestor_contencioso_bancario',
        'descricao': 'Estratégias processuais, execução de garantias e recuperação de crédito.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-money-bill-wave',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um gestor de contencioso bancário. Desenvolva estratégias processuais.',
        'especialidades': ['Contencioso', 'Execução', 'Garantias']
    },
    {
        'nome': 'Gestor de Compliance Bancário',
        'classe': 'gestor_compliance_bancario',
        'descricao': 'Monitoramento e interpretação de normas BACEN, CVM e adequação regulatória.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-shield-virus',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um gestor de compliance bancário. Monitore normas BACEN e CVM.',
        'especialidades': ['BACEN', 'CVM', 'Compliance']
    },
    {
        'nome': 'Analista de Revisão Contratual Bancária',
        'classe': 'analista_revisao_contratual_bancaria',
        'descricao': 'Detecção de cláusulas abusivas, anatocismo e práticas ilegais em contratos.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-file-contract',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um analista de revisão contratual bancária. Detecte cláusulas abusivas.',
        'especialidades': ['Revisão Contratual', 'Cláusulas Abusivas', 'Anatocismo']
    },
    {
        'nome': 'Agente de Defesa do Consumidor Bancário',
        'classe': 'agente_defesa_consumidor_bancario',
        'descricao': 'Demandas contra práticas bancárias abusivas, PROCON e BACEN.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-user-shield',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um agente de defesa do consumidor bancário. Combata práticas abusivas.',
        'especialidades': ['Defesa do Consumidor', 'PROCON', 'Práticas Abusivas']
    },
    {
        'nome': 'Consultor em Mercado de Capitais',
        'classe': 'consultor_mercado_capitais',
        'descricao': 'Especialista em mercado de capitais e valores mobiliários.',
        'categoria_nome': 'Direito Bancário',
        'icone': 'fas fa-chart-line',
        'cor_destaque': '#b8860b',
        'template_prompt': 'Você é um consultor em mercado de capitais. Analise valores mobiliários.',
        'especialidades': ['Mercado de Capitais', 'Valores Mobiliários', 'CVM']
    },

    # DIREITO EMPRESARIAL (4 agentes)
    {
        'nome': 'Especialista em Direito Empresarial',
        'classe': 'especialista_direito_empresarial',
        'descricao': 'Análise de contratos empresariais, sociedades e direito comercial.',
        'categoria_nome': 'Direito Empresarial',
        'icone': 'fas fa-building',
        'cor_destaque': '#1565c0',
        'template_prompt': 'Você é um especialista em Direito Empresarial. Analise contratos e sociedades.',
        'especialidades': ['Contratos Empresariais', 'Sociedades', 'Direito Comercial']
    },
    {
        'nome': 'Agente de Compliance e Governança',
        'classe': 'agente_compliance_governanca',
        'descricao': 'Estruturação de boas práticas, políticas internas e conformidade regulatória.',
        'categoria_nome': 'Direito Empresarial',
        'icone': 'fas fa-clipboard-check',
        'cor_destaque': '#1565c0',
        'template_prompt': 'Você é um agente de compliance e governança. Estruture boas práticas.',
        'especialidades': ['Compliance', 'Governança', 'Políticas Internas']
    },
    {
        'nome': 'Especialista em Startups e VC',
        'classe': 'especialista_startups_venture_capital',
        'descricao': 'Estruturação jurídica de startups e operações com investidores anjo.',
        'categoria_nome': 'Direito Empresarial',
        'icone': 'fas fa-rocket',
        'cor_destaque': '#1565c0',
        'template_prompt': 'Você é um especialista em startups e venture capital. Estruture operações.',
        'especialidades': ['Startups', 'Venture Capital', 'Investidores Anjo']
    },
    {
        'nome': 'Agente de Recuperação Empresarial',
        'classe': 'agente_recuperacao_empresarial',
        'descricao': 'Empresas em crise, negociações com credores e recuperação judicial.',
        'categoria_nome': 'Direito Empresarial',
        'icone': 'fas fa-chart-area',
        'cor_destaque': '#1565c0',
        'template_prompt': 'Você é um agente de recuperação empresarial. Negocie com credores.',
        'especialidades': ['Recuperação Judicial', 'Crise Empresarial', 'Negociação']
    },

    # DIREITO DO CONSUMIDOR (4 agentes)
    {
        'nome': 'Especialista em Direito do Consumidor',
        'classe': 'especialista_direito_consumidor',
        'descricao': 'Análise de relações de consumo, CDC e defesa do consumidor.',
        'categoria_nome': 'Direito do Consumidor',
        'icone': 'fas fa-shopping-cart',
        'cor_destaque': '#ec7000',
        'template_prompt': 'Você é um especialista em Direito do Consumidor. Analise relações de consumo.',
        'especialidades': ['CDC', 'Relações de Consumo', 'PROCON']
    },
    {
        'nome': 'Agente de Litígios Coletivos',
        'classe': 'agente_litigios_coletivos',
        'descricao': 'Identifica práticas abusivas e estrutura ações civis públicas.',
        'categoria_nome': 'Direito do Consumidor',
        'icone': 'fas fa-bullhorn',
        'cor_destaque': '#ec7000',
        'template_prompt': 'Você é um agente de litígios coletivos. Identifique práticas abusivas.',
        'especialidades': ['Ação Civil Pública', 'Práticas Abusivas', 'Litígios Coletivos']
    },
    {
        'nome': 'Especialista em Conciliação',
        'classe': 'especialista_atendimento_conciliacao',
        'descricao': 'Resolução amigável de conflitos entre consumidores e empresas.',
        'categoria_nome': 'Direito do Consumidor',
        'icone': 'fas fa-handshake',
        'cor_destaque': '#ec7000',
        'template_prompt': 'Você é um especialista em conciliação. Resolva conflitos amigavelmente.',
        'especialidades': ['Conciliação', 'Mediação', 'Resolução de Conflitos']
    },
    {
        'nome': 'Agente de Fiscalização',
        'classe': 'agente_fiscalizacao_sancoes',
        'descricao': 'Autuações PROCON, ANATEL e ANVISA, defesas administrativas.',
        'categoria_nome': 'Direito do Consumidor',
        'icone': 'fas fa-search-plus',
        'cor_destaque': '#ec7000',
        'template_prompt': 'Você é um agente de fiscalização. Analise autuações e defesas administrativas.',
        'especialidades': ['PROCON', 'ANATEL', 'ANVISA', 'Defesas Administrativas']
    },

    # DIREITO TRABALHISTA (1 agente)
    {
        'nome': 'Especialista em Direito Trabalhista',
        'classe': 'especialista_direito_trabalhista',
        'descricao': 'Análise de relações trabalhistas, CLT e jurisprudência trabalhista.',
        'categoria_nome': 'Direito Trabalhista',
        'icone': 'fas fa-hard-hat',
        'cor_destaque': '#a94513',
        'template_prompt': 'Você é um especialista em Direito Trabalhista. Analise relações trabalhistas.',
        'especialidades': ['CLT', 'Relações Trabalhistas', 'Jurisprudência']
    },

    # RECUPERAÇÃO DE CRÉDITO (1 agente)
    {
        'nome': 'Especialista em Recuperação de Crédito',
        'classe': 'especialista_recuperacao_credito',
        'descricao': 'Estratégias de cobrança, execução fiscal e recuperação judicial.',
        'categoria_nome': 'Recuperação de Crédito',
        'icone': 'fas fa-coins',
        'cor_destaque': '#455a64',
        'template_prompt': 'Você é um especialista em recuperação de crédito. Desenvolva estratégias de cobrança.',
        'especialidades': ['Cobrança', 'Execução Fiscal', 'Recuperação Judicial']
    },

    # DIREITO SECURITÁRIO (4 agentes)
    {
        'nome': 'Especialista em Direito Securitário',
        'classe': 'especialista_direito_securitario',
        'descricao': 'Análise de contratos de seguros, resseguros e regulamentação SUSEP.',
        'categoria_nome': 'Direito Securitário',
        'icone': 'fas fa-shield-check',
        'cor_destaque': '#3f51b5',
        'template_prompt': 'Você é um especialista em Direito Securitário. Analise contratos de seguros.',
        'especialidades': ['Contratos de Seguros', 'SUSEP', 'Resseguros']
    },
    {
        'nome': 'Gestor de Compliance SUSEP',
        'classe': 'gestor_compliance_susep',
        'descricao': 'Monitoramento regulatório SUSEP e adequação às normas securitárias.',
        'categoria_nome': 'Direito Securitário',
        'icone': 'fas fa-bell',
        'cor_destaque': '#3f51b5',
        'template_prompt': 'Você é um gestor de compliance SUSEP. Monitore normas securitárias.',
        'especialidades': ['SUSEP', 'Compliance', 'Normas Securitárias']
    },
    {
        'nome': 'Gestor de Sinistros Securitários',
        'classe': 'gestor_sinistros_securitario',
        'descricao': 'Análise técnica de sinistros, liquidação e disputas entre seguradoras.',
        'categoria_nome': 'Direito Securitário',
        'icone': 'fas fa-file-medical',
        'cor_destaque': '#3f51b5',
        'template_prompt': 'Você é um gestor de sinistros securitários. Analise sinistros tecnicamente.',
        'especialidades': ['Sinistros', 'Liquidação', 'Disputas']
    },
    {
        'nome': 'Gestor de Contencioso Securitário',
        'classe': 'gestor_contencioso_securitario',
        'descricao': 'Litígios securitários, ações regressivas e estratégias de defesa.',
        'categoria_nome': 'Direito Securitário',
        'icone': 'fas fa-balance-scale',
        'cor_destaque': '#3f51b5',
        'template_prompt': 'Você é um gestor de contencioso securitário. Desenvolva estratégias de defesa.',
        'especialidades': ['Contencioso', 'Ações Regressivas', 'Litígios']
    },

    # DIREITO AGRÁRIO (3 agentes)
    {
        'nome': 'Agente de Regularização Fundiária',
        'classe': 'agente_regularizacao_fundiaria',
        'descricao': 'Especialista em regularização de imóveis rurais, INCRA e órgãos estaduais.',
        'categoria_nome': 'Direito Agrário',
        'icone': 'fas fa-map',
        'cor_destaque': '#00734d',
        'template_prompt': 'Você é um agente de regularização fundiária. Regularize imóveis rurais.',
        'especialidades': ['Regularização Fundiária', 'INCRA', 'Imóveis Rurais']
    },
    {
        'nome': 'Especialista em Contratos Rurais',
        'classe': 'especialista_contratos_rurais',
        'descricao': 'Elaboração e análise de contratos do agronegócio, arrendamento e parceria rural.',
        'categoria_nome': 'Direito Agrário',
        'icone': 'fas fa-tractor',
        'cor_destaque': '#00734d',
        'template_prompt': 'Você é um especialista em contratos rurais. Elabore contratos do agronegócio.',
        'especialidades': ['Contratos Rurais', 'Agronegócio', 'Arrendamento']
    },
    {
        'nome': 'Consultor em Crédito Rural',
        'classe': 'consultor_credito_rural',
        'descricao': 'Financiamento agrícola, subvenções BNDES e PRONAF, linhas de crédito.',
        'categoria_nome': 'Direito Agrário',
        'icone': 'fas fa-hand-holding-usd',
        'cor_destaque': '#2e7d32',
        'template_prompt': 'Você é um consultor em crédito rural. Analise financiamentos agrícolas.',
        'especialidades': ['Crédito Rural', 'BNDES', 'PRONAF']
    }
]

def sincronizar_agentes():
    """Sincroniza todos os agentes com o banco de dados"""
    with app.app_context():
        try:
            print("🔄 Iniciando sincronização de agentes...")
            
            # Primeiro, criar as categorias necessárias se não existirem
            categorias_necessarias = {
                'Direito Penal': 1,
                'Direito Bancário': 4,
                'Direito Empresarial': 2,
                'Direito do Consumidor': 5,
                'Direito Trabalhista': 3,
                'Recuperação de Crédito': 6,
                'Direito Securitário': 7,
                'Direito Agrário': 8
            }
            
            for categoria_nome, categoria_id in categorias_necessarias.items():
                categoria = CategoriaJuridica.query.filter_by(id=categoria_id).first()
                if not categoria:
                    categoria = CategoriaJuridica(
                        id=categoria_id,
                        nome=categoria_nome,
                        descricao=f'Categoria para agentes de {categoria_nome}',
                        cor='#333333',
                        ativo=True
                    )
                    db.session.add(categoria)
                    print(f"➕ Categoria criada: {categoria_nome}")
            
            db.session.commit()
            
            # Agora sincronizar os agentes
            adicionados = 0
            atualizados = 0
            
            for config_agente in AGENTES_COMPLETOS:
                # Buscar categoria
                categoria = CategoriaJuridica.query.filter_by(nome=config_agente['categoria_nome']).first()
                if not categoria:
                    print(f"❌ Categoria não encontrada: {config_agente['categoria_nome']}")
                    continue
                
                # Verificar se agente já existe
                agente = AgenteJuridico.query.filter_by(classe=config_agente['classe']).first()
                
                if not agente:
                    # Criar novo agente
                    agente = AgenteJuridico(
                        nome=config_agente['nome'],
                        classe=config_agente['classe'],
                        descricao=config_agente['descricao'],
                        categoria_id=categoria.id,
                        icone=config_agente['icone'],
                        cor_destaque=config_agente['cor_destaque'],
                        template_prompt=config_agente['template_prompt'],
                        ativo=True,
                        nivel_especializacao=4,
                        modelo_ai='gpt-4',
                        temperatura=0.7,
                        top_p=0.9,
                        max_tokens=2000,
                        data_criacao=datetime.now(),
                        data_atualizacao=datetime.now()
                    )
                    db.session.add(agente)
                    adicionados += 1
                    print(f"➕ Agente adicionado: {config_agente['nome']}")
                else:
                    # Atualizar agente existente
                    agente.nome = config_agente['nome']
                    agente.descricao = config_agente['descricao']
                    agente.icone = config_agente['icone']
                    agente.cor_destaque = config_agente['cor_destaque']
                    agente.template_prompt = config_agente['template_prompt']
                    agente.data_atualizacao = datetime.now()
                    atualizados += 1
                    print(f"🔄 Agente atualizado: {config_agente['nome']}")
            
            db.session.commit()
            print(f"\n✅ Sincronização concluída!")
            print(f"➕ {adicionados} agentes adicionados")
            print(f"🔄 {atualizados} agentes atualizados")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro na sincronização: {str(e)}")
            raise e

if __name__ == '__main__':
    sincronizar_agentes()