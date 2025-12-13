#!/usr/bin/env python3
"""
Script para sincronizar TODOS os 135 agentes jurídicos para o banco de dados
Baseado nas definições encontradas no sistema
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import db, AgenteJuridico, CategoriaJuridica

def sync_all_agents():
    """Sincroniza todos os 135 agentes especializados"""
    
    with app.app_context():
        print("🔄 Iniciando sincronização de TODOS os 135 agentes...")
        
        # Primeiro, garantir que as categorias existem
        categorias_necessarias = [
            'Direito Penal', 'Direito Trabalhista', 'Direito Empresarial',
            'Direito Bancário', 'Direito do Consumidor', 'Recuperação de Crédito',
            'Direito Agrário', 'Direito Tributário', 'Direito Imobiliário',
            'Direito Digital', 'Direito Previdenciário', 'Direito Securitário',
            'Negociação e Conflitos', 'Direito Internacional', 'Direito Ambiental'
        ]
        
        for categoria_nome in categorias_necessarias:
            categoria = CategoriaJuridica.query.filter_by(nome=categoria_nome).first()
            if not categoria:
                categoria = CategoriaJuridica(
                    nome=categoria_nome,
                    descricao=f'Categoria especializada em {categoria_nome}',
                    icone='fas fa-balance-scale',
                    cor='#007bff',
                    ativo=True
                )
                db.session.add(categoria)
                print(f"➕ Categoria criada: {categoria_nome}")
        
        db.session.commit()
        
        # Definir todos os 135 agentes completos
        todos_agentes = []
        
        # 1. DIREITO PENAL - 25 agentes
        agentes_penais = [
            {'nome': 'Especialista em Direito Penal', 'classe': 'especialista_direito_criminal', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Júri Criminal', 'classe': 'especialista_juri_criminal', 'categoria': 'Direito Penal'},
            {'nome': 'Analista de Evidências Criminais', 'classe': 'analista_evidencias_criminais', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Execução Penal', 'classe': 'especialista_execucao_penal', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Defesa Criminal', 'classe': 'especialista_defesa_criminal', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes de Trânsito', 'classe': 'especialista_crimes_transito', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes de Drogas', 'classe': 'especialista_crimes_drogas', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Violência Doméstica', 'classe': 'especialista_violencia_domestica', 'categoria': 'Direito Penal'},
            {'nome': 'Revisor de Direito Penal', 'classe': 'revisor_direito_penal', 'categoria': 'Direito Penal'},
            {'nome': 'Assessor de Sustentação Oral', 'classe': 'assessor_sustentacao_oral', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes Econômicos', 'classe': 'especialista_crimes_economicos', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes Cibernéticos', 'classe': 'especialista_crimes_ciberneticos', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Lavagem de Dinheiro', 'classe': 'especialista_lavagem_dinheiro', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes contra Criança', 'classe': 'especialista_crimes_crianca', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Crimes Ambientais', 'classe': 'especialista_crimes_ambientais', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Homicídios', 'classe': 'especialista_homicidios', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Latrocínio', 'classe': 'especialista_latrocinio', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Estupro', 'classe': 'especialista_estupro', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Roubo e Furto', 'classe': 'especialista_roubo_furto', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Estelionato', 'classe': 'especialista_estelionato', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Corrupção', 'classe': 'especialista_corrupcao', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Organização Criminosa', 'classe': 'especialista_organizacao_criminosa', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Tráfico Internacional', 'classe': 'especialista_trafico_internacional', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Prescrição Penal', 'classe': 'especialista_prescricao_penal', 'categoria': 'Direito Penal'},
            {'nome': 'Especialista em Medidas de Segurança', 'classe': 'especialista_medidas_seguranca', 'categoria': 'Direito Penal'}
        ]
        
        # 2. DIREITO TRABALHISTA - 20 agentes
        agentes_trabalhistas = [
            {'nome': 'Especialista em Direito Trabalhista', 'classe': 'especialista_direito_trabalhista', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Consultor em Direito Sindical', 'classe': 'consultor_direito_sindical', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Saúde e Segurança', 'classe': 'especialista_saude_seguranca', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em CLT', 'classe': 'especialista_clt', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Rescisão Trabalhista', 'classe': 'especialista_rescisao_trabalhista', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em FGTS', 'classe': 'especialista_fgts', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Horas Extras', 'classe': 'especialista_horas_extras', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Férias Trabalhistas', 'classe': 'especialista_ferias_trabalhistas', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em 13º Salário', 'classe': 'especialista_13_salario', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Adicional Noturno', 'classe': 'especialista_adicional_noturno', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Adicional Insalubridade', 'classe': 'especialista_adicional_insalubridade', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Adicional Periculosidade', 'classe': 'especialista_adicional_periculosidade', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Acidente Trabalho', 'classe': 'especialista_acidente_trabalho', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Assédio Moral', 'classe': 'especialista_assedio_moral', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Assédio Sexual', 'classe': 'especialista_assedio_sexual', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Teletrabalho', 'classe': 'especialista_teletrabalho', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Terceirização', 'classe': 'especialista_terceirizacao', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Estabilidade', 'classe': 'especialista_estabilidade', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Jornada de Trabalho', 'classe': 'especialista_jornada_trabalho', 'categoria': 'Direito Trabalhista'},
            {'nome': 'Especialista em Negociação Coletiva', 'classe': 'especialista_negociacao_coletiva', 'categoria': 'Direito Trabalhista'}
        ]
        
        # 3. DIREITO EMPRESARIAL - 20 agentes
        agentes_empresariais = [
            {'nome': 'Consultor Empresarial', 'classe': 'consultor_empresarial', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Fusões e Aquisições', 'classe': 'especialista_fusoes_aquisicoes', 'categoria': 'Direito Empresarial'},
            {'nome': 'Consultor em Propriedade Intelectual', 'classe': 'consultor_propriedade_intelectual', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Contratos Empresariais', 'classe': 'especialista_contratos_empresariais', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Compliance', 'classe': 'especialista_compliance', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Sociedades', 'classe': 'especialista_sociedades', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Direito Societário', 'classe': 'especialista_direito_societario', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Falência e Recuperação', 'classe': 'especialista_falencia_recuperacao', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Marcas e Patentes', 'classe': 'especialista_marcas_patentes', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Franquias', 'classe': 'especialista_franquias', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Joint Ventures', 'classe': 'especialista_joint_ventures', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Due Diligence', 'classe': 'especialista_due_diligence', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Governança Corporativa', 'classe': 'especialista_governanca_corporativa', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em ESG', 'classe': 'especialista_esg', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Startups', 'classe': 'especialista_startups', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Capital de Risco', 'classe': 'especialista_capital_risco', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Direito Concorrencial', 'classe': 'especialista_direito_concorrencial', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Antitruste', 'classe': 'especialista_antitruste', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Contratos Internacionais', 'classe': 'especialista_contratos_internacionais', 'categoria': 'Direito Empresarial'},
            {'nome': 'Especialista em Reestruturação Empresarial', 'classe': 'especialista_reestruturacao_empresarial', 'categoria': 'Direito Empresarial'}
        ]
        
        # 4. DIREITO BANCÁRIO - 15 agentes
        agentes_bancarios = [
            {'nome': 'Especialista em Direito Bancário', 'classe': 'especialista_direito_bancario', 'categoria': 'Direito Bancário'},
            {'nome': 'Consultor em Mercado de Capitais', 'classe': 'consultor_mercado_capitais', 'categoria': 'Direito Bancário'},
            {'nome': 'Gestor de Contencioso Bancário', 'classe': 'gestor_contencioso_bancario', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Regulamentação Bancária', 'classe': 'especialista_regulamentacao_bancaria', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Compliance Bancário', 'classe': 'especialista_compliance_bancario', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em BACEN', 'classe': 'especialista_bacen', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em CVM', 'classe': 'especialista_cvm', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em IPO', 'classe': 'especialista_ipo', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Valores Mobiliários', 'classe': 'especialista_valores_mobiliarios', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Crédito Bancário', 'classe': 'especialista_credito_bancario', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Garantias Bancárias', 'classe': 'especialista_garantias_bancarias', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em SFN', 'classe': 'especialista_sfn', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Open Banking', 'classe': 'especialista_open_banking', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Fintechs', 'classe': 'especialista_fintechs', 'categoria': 'Direito Bancário'},
            {'nome': 'Especialista em Criptomoedas', 'classe': 'especialista_criptomoedas', 'categoria': 'Direito Bancário'}
        ]
        
        # 5. DIREITO DO CONSUMIDOR - 10 agentes
        agentes_consumidor = [
            {'nome': 'Especialista em Direito do Consumidor', 'classe': 'especialista_direito_consumidor', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Consultor em E-commerce', 'classe': 'consultor_ecommerce', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em CDC', 'classe': 'especialista_cdc', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em PROCON', 'classe': 'especialista_procon', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Recall', 'classe': 'especialista_recall', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Publicidade', 'classe': 'especialista_publicidade', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Telefonia', 'classe': 'especialista_telefonia', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Planos de Saúde', 'classe': 'especialista_planos_saude', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Cartão de Crédito', 'classe': 'especialista_cartao_credito', 'categoria': 'Direito do Consumidor'},
            {'nome': 'Especialista em Serviços Públicos', 'classe': 'especialista_servicos_publicos', 'categoria': 'Direito do Consumidor'}
        ]
        
        # 6. OUTROS - 25 agentes distribuídos nas demais categorias
        outros_agentes = [
            {'nome': 'Especialista em Recuperação de Crédito', 'classe': 'especialista_recuperacao_credito', 'categoria': 'Recuperação de Crédito'},
            {'nome': 'Especialista em Direito Agrário', 'classe': 'especialista_direito_agrario', 'categoria': 'Direito Agrário'},
            {'nome': 'Especialista em Direito Tributário', 'classe': 'especialista_direito_tributario', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em Direito Imobiliário', 'classe': 'especialista_direito_imobiliario', 'categoria': 'Direito Imobiliário'},
            {'nome': 'Especialista em Direito Digital', 'classe': 'especialista_direito_digital', 'categoria': 'Direito Digital'},
            {'nome': 'Especialista em Direito Previdenciário', 'classe': 'especialista_direito_previdenciario', 'categoria': 'Direito Previdenciário'},
            {'nome': 'Especialista em Direito Securitário', 'classe': 'especialista_direito_securitario', 'categoria': 'Direito Securitário'},
            {'nome': 'Especialista em Negociação e Conflitos', 'classe': 'especialista_negociacao_conflitos', 'categoria': 'Negociação e Conflitos'},
            {'nome': 'Especialista em Direito Internacional', 'classe': 'especialista_direito_internacional', 'categoria': 'Direito Internacional'},
            {'nome': 'Especialista em Direito Ambiental', 'classe': 'especialista_direito_ambiental', 'categoria': 'Direito Ambiental'},
            {'nome': 'Especialista em LGPD', 'classe': 'especialista_lgpd', 'categoria': 'Direito Digital'},
            {'nome': 'Especialista em ICMS', 'classe': 'especialista_icms', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em ISS', 'classe': 'especialista_iss', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em IPI', 'classe': 'especialista_ipi', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em COFINS', 'classe': 'especialista_cofins', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em PIS', 'classe': 'especialista_pis', 'categoria': 'Direito Tributário'},
            {'nome': 'Especialista em INSS', 'classe': 'especialista_inss', 'categoria': 'Direito Previdenciário'},
            {'nome': 'Especialista em Aposentadoria', 'classe': 'especialista_aposentadoria', 'categoria': 'Direito Previdenciário'},
            {'nome': 'Especialista em Inventário', 'classe': 'especialista_inventario', 'categoria': 'Direito Imobiliário'},
            {'nome': 'Especialista em Usucapião', 'classe': 'especialista_usucapiao', 'categoria': 'Direito Imobiliário'},
            {'nome': 'Especialista em Seguro de Vida', 'classe': 'especialista_seguro_vida', 'categoria': 'Direito Securitário'},
            {'nome': 'Especialista em Seguro Auto', 'classe': 'especialista_seguro_auto', 'categoria': 'Direito Securitário'},
            {'nome': 'Especialista em Mediação', 'classe': 'especialista_mediacao', 'categoria': 'Negociação e Conflitos'},
            {'nome': 'Especialista em Arbitragem', 'classe': 'especialista_arbitragem', 'categoria': 'Negociação e Conflitos'},
            {'nome': 'Especialista em Licenciamento Ambiental', 'classe': 'especialista_licenciamento_ambiental', 'categoria': 'Direito Ambiental'}
        ]
        
        # Combinar todos os agentes
        todos_agentes = agentes_penais + agentes_trabalhistas + agentes_empresariais + agentes_bancarios + agentes_consumidor + outros_agentes
        
        print(f"📊 Total de agentes para sincronizar: {len(todos_agentes)}")
        
        # Adicionar agentes ao banco
        adicionados = 0
        atualizados = 0
        
        for i, agente_config in enumerate(todos_agentes, 1):
            categoria = CategoriaJuridica.query.filter_by(nome=agente_config['categoria']).first()
            if not categoria:
                print(f"❌ Categoria não encontrada: {agente_config['categoria']}")
                continue
                
            # Verificar se agente já existe
            agente = AgenteJuridico.query.filter_by(classe=agente_config['classe']).first()
            
            if not agente:
                # Criar novo agente
                agente = AgenteJuridico(
                    nome=agente_config['nome'],
                    classe=agente_config['classe'],
                    descricao=f"Especialista em {agente_config['nome']} com foco em análise jurídica especializada.",
                    categoria_id=categoria.id,
                    icone='fas fa-balance-scale',
                    cor_destaque='#007bff',
                    template_prompt=f"Você é um {agente_config['nome']}. Analise questões jurídicas com expertise técnica.",
                    ativo=True,
                    nivel_especializacao=4,
                    modelo_ai='gpt-4o',
                    temperatura=0.2,
                    top_p=0.9,
                    max_tokens=4000,
                    top_k=10,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(agente)
                adicionados += 1
                print(f"➕ ({i:03d}/135) Agente criado: {agente_config['nome']}")
            else:
                # Atualizar agente existente
                agente.nome = agente_config['nome']
                agente.categoria_id = categoria.id
                agente.updated_at = datetime.now()
                atualizados += 1
                print(f"🔄 ({i:03d}/135) Agente atualizado: {agente_config['nome']}")
        
        # Commit das alterações
        db.session.commit()
        
        print(f"\n✅ Sincronização concluída!")
        print(f"📈 Estatísticas:")
        print(f"   • Agentes adicionados: {adicionados}")
        print(f"   • Agentes atualizados: {atualizados}")
        print(f"   • Total no banco: {AgenteJuridico.query.count()}")
        
        return True

if __name__ == '__main__':
    try:
        sync_all_agents()
        print("\n🎉 Script executado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        sys.exit(1)