#!/usr/bin/env python3
"""
Script para completar os 135 agentes especializados no sistema
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import db

def complete_all_135_agents():
    """Completa todos os 135 agentes especializados"""
    
    with app.app_context():
        print("Completando sistema com todos os 135 agentes...")
        
        # Verificar agentes atuais
        current_count = db.session.execute("SELECT COUNT(*) FROM agente_juridico").scalar()
        print(f"Agentes atuais: {current_count}")
        
        # Lista completa dos 135 agentes por área
        agentes_completos = [
            # DIREITO EMPRESARIAL (40 agentes)
            {'nome': 'Especialista em Contratos Empresariais', 'classe': 'especialista_contratos_empresariais', 'categoria_id': 8},
            {'nome': 'Especialista em Compliance', 'classe': 'especialista_compliance', 'categoria_id': 8},
            {'nome': 'Especialista em Sociedades', 'classe': 'especialista_sociedades', 'categoria_id': 8},
            {'nome': 'Especialista em Falência e Recuperação', 'classe': 'especialista_falencia_recuperacao', 'categoria_id': 8},
            {'nome': 'Especialista em Marcas e Patentes', 'classe': 'especialista_marcas_patentes', 'categoria_id': 8},
            {'nome': 'Especialista em Franquias', 'classe': 'especialista_franquias', 'categoria_id': 8},
            {'nome': 'Especialista em Joint Ventures', 'classe': 'especialista_joint_ventures', 'categoria_id': 8},
            {'nome': 'Especialista em Due Diligence', 'classe': 'especialista_due_diligence', 'categoria_id': 8},
            {'nome': 'Especialista em Governança Corporativa', 'classe': 'especialista_governanca_corporativa', 'categoria_id': 8},
            {'nome': 'Especialista em ESG', 'classe': 'especialista_esg', 'categoria_id': 8},
            {'nome': 'Especialista em Capital de Risco', 'classe': 'especialista_capital_risco', 'categoria_id': 8},
            {'nome': 'Especialista em Antitruste', 'classe': 'especialista_antitruste', 'categoria_id': 8},
            {'nome': 'Especialista em Contratos Internacionais', 'classe': 'especialista_contratos_internacionais', 'categoria_id': 8},
            {'nome': 'Especialista em Reestruturação Empresarial', 'classe': 'especialista_reestruturacao_empresarial', 'categoria_id': 8},
            {'nome': 'Especialista em Fusões e Aquisições', 'classe': 'especialista_fusoes_aquisicoes', 'categoria_id': 8},
            {'nome': 'Consultor em Propriedade Intelectual', 'classe': 'consultor_propriedade_intelectual', 'categoria_id': 8},
            {'nome': 'Especialista em Direito Concorrencial', 'classe': 'especialista_direito_concorrencial', 'categoria_id': 8},
            {'nome': 'Especialista em Licenciamento de Software', 'classe': 'especialista_licenciamento_software', 'categoria_id': 8},
            {'nome': 'Especialista em Contratos de Distribuição', 'classe': 'especialista_contratos_distribuicao', 'categoria_id': 8},
            {'nome': 'Especialista em Direito Societário Internacional', 'classe': 'especialista_direito_societario_internacional', 'categoria_id': 8},
            
            # DIREITO DO CONSUMIDOR (25 agentes)
            {'nome': 'Especialista em CDC', 'classe': 'especialista_cdc', 'categoria_id': 13},
            {'nome': 'Consultor em E-commerce', 'classe': 'consultor_ecommerce', 'categoria_id': 13},
            {'nome': 'Especialista em PROCON', 'classe': 'especialista_procon', 'categoria_id': 13},
            {'nome': 'Especialista em Recall', 'classe': 'especialista_recall', 'categoria_id': 13},
            {'nome': 'Especialista em Publicidade', 'classe': 'especialista_publicidade', 'categoria_id': 13},
            {'nome': 'Especialista em Telefonia', 'classe': 'especialista_telefonia', 'categoria_id': 13},
            {'nome': 'Especialista em Planos de Saúde', 'classe': 'especialista_planos_saude', 'categoria_id': 13},
            {'nome': 'Especialista em Cartão de Crédito', 'classe': 'especialista_cartao_credito', 'categoria_id': 13},
            {'nome': 'Especialista em Serviços Públicos', 'classe': 'especialista_servicos_publicos', 'categoria_id': 13},
            {'nome': 'Especialista em Produtos Defeituosos', 'classe': 'especialista_produtos_defeituosos', 'categoria_id': 13},
            {'nome': 'Especialista em Contratos de Adesão', 'classe': 'especialista_contratos_adesao', 'categoria_id': 13},
            {'nome': 'Especialista em Cláusulas Abusivas', 'classe': 'especialista_clausulas_abusivas', 'categoria_id': 13},
            {'nome': 'Especialista em Direito do Turismo', 'classe': 'especialista_direito_turismo', 'categoria_id': 13},
            {'nome': 'Especialista em Transporte Aéreo', 'classe': 'especialista_transporte_aereo', 'categoria_id': 13},
            {'nome': 'Especialista em Bancos e Financeiras', 'classe': 'especialista_bancos_financeiras', 'categoria_id': 13},
            {'nome': 'Especialista em Seguros de Vida', 'classe': 'especialista_seguros_vida_consumidor', 'categoria_id': 13},
            {'nome': 'Especialista em Educação Privada', 'classe': 'especialista_educacao_privada', 'categoria_id': 13},
            {'nome': 'Especialista em Medicina Privada', 'classe': 'especialista_medicina_privada', 'categoria_id': 13},
            {'nome': 'Especialista em Supermercados', 'classe': 'especialista_supermercados', 'categoria_id': 13},
            {'nome': 'Especialista em Concessionárias', 'classe': 'especialista_concessionarias', 'categoria_id': 13},
            {'nome': 'Especialista em Shopping Centers', 'classe': 'especialista_shopping_centers', 'categoria_id': 13},
            {'nome': 'Especialista em Delivery', 'classe': 'especialista_delivery', 'categoria_id': 13},
            {'nome': 'Especialista em Assinatura Digital', 'classe': 'especialista_assinatura_digital', 'categoria_id': 13},
            {'nome': 'Especialista em Streaming', 'classe': 'especialista_streaming', 'categoria_id': 13},
            {'nome': 'Especialista em Games e Apps', 'classe': 'especialista_games_apps', 'categoria_id': 13},
            
            # DIREITO TRIBUTÁRIO (20 agentes)
            {'nome': 'Especialista em ICMS', 'classe': 'especialista_icms', 'categoria_id': 5},
            {'nome': 'Especialista em ISS', 'classe': 'especialista_iss', 'categoria_id': 5},
            {'nome': 'Especialista em IPI', 'classe': 'especialista_ipi', 'categoria_id': 5},
            {'nome': 'Especialista em COFINS', 'classe': 'especialista_cofins', 'categoria_id': 5},
            {'nome': 'Especialista em PIS', 'classe': 'especialista_pis', 'categoria_id': 5},
            {'nome': 'Especialista em Imposto de Renda', 'classe': 'especialista_imposto_renda', 'categoria_id': 5},
            {'nome': 'Especialista em CSLL', 'classe': 'especialista_csll', 'categoria_id': 5},
            {'nome': 'Especialista em IPTU', 'classe': 'especialista_iptu', 'categoria_id': 5},
            {'nome': 'Especialista em ITBI', 'classe': 'especialista_itbi', 'categoria_id': 5},
            {'nome': 'Especialista em IPVA', 'classe': 'especialista_ipva', 'categoria_id': 5},
            {'nome': 'Especialista em ITR', 'classe': 'especialista_itr', 'categoria_id': 5},
            {'nome': 'Especialista em Simples Nacional', 'classe': 'especialista_simples_nacional', 'categoria_id': 5},
            {'nome': 'Especialista em Lucro Presumido', 'classe': 'especialista_lucro_presumido', 'categoria_id': 5},
            {'nome': 'Especialista em Lucro Real', 'classe': 'especialista_lucro_real', 'categoria_id': 5},
            {'nome': 'Especialista em Planejamento Tributário', 'classe': 'especialista_planejamento_tributario', 'categoria_id': 5},
            {'nome': 'Especialista em Elisão Fiscal', 'classe': 'especialista_elisao_fiscal', 'categoria_id': 5},
            {'nome': 'Especialista em Processo Administrativo Fiscal', 'classe': 'especialista_processo_administrativo_fiscal', 'categoria_id': 5},
            {'nome': 'Especialista em Execução Fiscal', 'classe': 'especialista_execucao_fiscal', 'categoria_id': 5},
            {'nome': 'Especialista em Parcelamento Tributário', 'classe': 'especialista_parcelamento_tributario', 'categoria_id': 5},
            {'nome': 'Especialista em Consultoria Tributária', 'classe': 'especialista_consultoria_tributaria', 'categoria_id': 5},
            
            # DIREITO IMOBILIÁRIO (15 agentes)
            {'nome': 'Especialista em Inventário', 'classe': 'especialista_inventario', 'categoria_id': 6},
            {'nome': 'Especialista em Usucapião', 'classe': 'especialista_usucapiao', 'categoria_id': 6},
            {'nome': 'Especialista em Registro de Imóveis', 'classe': 'especialista_registro_imoveis', 'categoria_id': 6},
            {'nome': 'Especialista em Locação Residencial', 'classe': 'especialista_locacao_residencial', 'categoria_id': 6},
            {'nome': 'Especialista em Locação Comercial', 'classe': 'especialista_locacao_comercial', 'categoria_id': 6},
            {'nome': 'Especialista em Compra e Venda', 'classe': 'especialista_compra_venda', 'categoria_id': 6},
            {'nome': 'Especialista em Financiamento Imobiliário', 'classe': 'especialista_financiamento_imobiliario', 'categoria_id': 6},
            {'nome': 'Especialista em Incorporação Imobiliária', 'classe': 'especialista_incorporacao_imobiliaria', 'categoria_id': 6},
            {'nome': 'Especialista em Condomínios', 'classe': 'especialista_condominios', 'categoria_id': 6},
            {'nome': 'Especialista em Direito de Vizinhança', 'classe': 'especialista_direito_vizinhanca', 'categoria_id': 6},
            {'nome': 'Especialista em Loteamentos', 'classe': 'especialista_loteamentos', 'categoria_id': 6},
            {'nome': 'Especialista em Desapropriação', 'classe': 'especialista_desapropriacao', 'categoria_id': 6},
            {'nome': 'Especialista em Regularização Fundiária', 'classe': 'especialista_regularizacao_fundiaria_imobiliario', 'categoria_id': 6},
            {'nome': 'Especialista em ITBI Imobiliário', 'classe': 'especialista_itbi_imobiliario', 'categoria_id': 6},
            {'nome': 'Especialista em Contratos Imobiliários', 'classe': 'especialista_contratos_imobiliarios', 'categoria_id': 6},
            
            # RECUPERAÇÃO DE CRÉDITO (15 agentes)
            {'nome': 'Especialista em Execução de Título', 'classe': 'especialista_execucao_titulo', 'categoria_id': 15},
            {'nome': 'Especialista em Negativação', 'classe': 'especialista_negativacao', 'categoria_id': 15},
            {'nome': 'Especialista em Acordos Judiciais', 'classe': 'especialista_acordos_judiciais', 'categoria_id': 15},
            {'nome': 'Especialista em Protesto de Títulos', 'classe': 'especialista_protesto_titulos', 'categoria_id': 15},
            {'nome': 'Especialista em Cobrança Extrajudicial', 'classe': 'especialista_cobranca_extrajudicial', 'categoria_id': 15},
            {'nome': 'Especialista em Insolvência Civil', 'classe': 'especialista_insolvencia_civil', 'categoria_id': 15},
            {'nome': 'Especialista em Penhora de Bens', 'classe': 'especialista_penhora_bens', 'categoria_id': 15},
            {'nome': 'Especialista em Leilão Judicial', 'classe': 'especialista_leilao_judicial', 'categoria_id': 15},
            {'nome': 'Especialista em Bloqueio de Contas', 'classe': 'especialista_bloqueio_contas', 'categoria_id': 15},
            {'nome': 'Especialista em Precatórios', 'classe': 'especialista_precatorios', 'categoria_id': 15},
            {'nome': 'Especialista em RPV', 'classe': 'especialista_rpv', 'categoria_id': 15},
            {'nome': 'Especialista em Execução Contra a Fazenda', 'classe': 'especialista_execucao_fazenda', 'categoria_id': 15},
            {'nome': 'Especialista em Cessão de Crédito', 'classe': 'especialista_cessao_credito', 'categoria_id': 15},
            {'nome': 'Especialista em Factoring', 'classe': 'especialista_factoring', 'categoria_id': 15},
            {'nome': 'Especialista em Securitização', 'classe': 'especialista_securitizacao', 'categoria_id': 15}
        ]
        
        agentes_adicionados = 0
        for agente_data in agentes_completos:
            # Verificar se já existe
            existe = db.session.execute(
                "SELECT COUNT(*) FROM agente_juridico WHERE classe = %s",
                (agente_data['classe'],)
            ).scalar()
            
            if existe == 0:
                # Adicionar agente
                db.session.execute("""
                    INSERT INTO agente_juridico 
                    (nome, classe, descricao, categoria_id, icone, ativo, template_prompt, 
                     nivel_especializacao, modelo_ai, temperatura, top_p, max_tokens, top_k, 
                     created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    agente_data['nome'],
                    agente_data['classe'],
                    f"Especialista em {agente_data['nome']} com análise jurídica especializada.",
                    agente_data['categoria_id'],
                    'fas fa-balance-scale',
                    True,
                    f"Você é um {agente_data['nome']}. Analise questões jurídicas com expertise técnica.",
                    4,
                    'gpt-4o',
                    0.2,
                    0.9,
                    4000,
                    10,
                    datetime.now(),
                    datetime.now()
                ))
                agentes_adicionados += 1
                print(f"+ {agente_data['nome']}")
        
        db.session.commit()
        
        final_count = db.session.execute("SELECT COUNT(*) FROM agente_juridico").scalar()
        print(f"\nConcluído!")
        print(f"Agentes adicionados: {agentes_adicionados}")
        print(f"Total final: {final_count}")
        
        return True

if __name__ == '__main__':
    complete_all_135_agents()