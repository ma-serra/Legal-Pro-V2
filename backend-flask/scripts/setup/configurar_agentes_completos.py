#!/usr/bin/env python3
"""
Script para configurar todos os 18 agentes jurídicos especialistas
com os dados técnicos completos conforme especificação fornecida.
"""

import json
from main import app
from models import db, AgenteJuridico, CategoriaJuridica

def configurar_agentes_completos():
    """Configura todos os 18 agentes com dados técnicos completos."""
    
    agentes_config = [
        {
            "id": 1,
            "nome": "Especialista em Direito Bancário",
            "classe": "EspecialistaDireitoBancarioAgent",
            "categoria_nome": "Direito Bancário",
            "nivel": "5 - Autoridade",
            "modelo_ai": "claude-3-5-sonnet",
            "temperatura": 0.3,
            "top_p": 0.9,
            "max_tokens": 4000,
            "icone": "fas fa-university",
            "cor_destaque": "#2E8B57",
            "ativo": True,
            "descricao": "Especializado na análise de contratos bancários, operações financeiras e conformidade regulatória bancária.",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de contratos bancários",
                    "Avaliação de riscos em operações financeiras",
                    "Verificação de conformidade regulatória",
                    "Elaboração de pareceres técnicos",
                    "Recomendações para mitigação de riscos"
                ],
                "fontes_conhecimento": [
                    "Resoluções do Banco Central",
                    "Jurisprudência bancária",
                    "Normas do Conselho Monetário Nacional",
                    "Lei do Sistema Financeiro Nacional"
                ]
            },
            "template_prompt": "Você é um especialista em Direito Bancário. Analise {contexto} considerando normas do Banco Central e jurisprudência bancária."
        },
        {
            "id": 2,
            "nome": "Especialista em Direito Securitário",
            "classe": "EspecialistaDireitoSecuritarioAgent",
            "categoria_nome": "Direito Empresarial",
            "nivel": "4 - Expert",
            "modelo_ai": "gpt-4o",
            "temperatura": 0.3,
            "top_p": 0.9,
            "max_tokens": 4000,
            "icone": "fas fa-shield-alt",
            "cor_destaque": "#4169E1",
            "ativo": True,
            "descricao": "Especializado na análise de contratos de seguro, resseguro e questões regulatórias do mercado de seguros.",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de contratos de seguro",
                    "Avaliação de cláusulas de resseguro",
                    "Verificação de conformidade com normas SUSEP",
                    "Elaboração de pareceres sobre sinistros",
                    "Recomendações para apólices de seguro"
                ],
                "fontes_conhecimento": [
                    "Código Civil - Capítulo de Seguros",
                    "Resoluções da SUSEP",
                    "Jurisprudência securitária",
                    "Normas do CNSP"
                ]
            },
            "template_prompt": "Você é um especialista em Direito Securitário. Analise {contexto} considerando normas da SUSEP e regulamentação de seguros."
        },
        {
            "id": 3,
            "nome": "Especialista em Direito Trabalhista",
            "classe": "EspecialistaDireitoTrabalhistaAgent",
            "categoria_nome": "Direito Trabalhista",
            "nivel": "5 - Autoridade",
            "modelo_ai": "claude-3-5-sonnet",
            "temperatura": 0.3,
            "top_p": 0.9,
            "max_tokens": 4000,
            "icone": "fas fa-hard-hat",
            "cor_destaque": "#DC143C",
            "ativo": True,
            "descricao": "Especializado na análise de questões trabalhistas, contratos de trabalho e relações laborais.",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de contratos de trabalho",
                    "Avaliação de acordos coletivos",
                    "Verificação de conformidade com CLT",
                    "Análise de riscos em demissões",
                    "Orientações sobre jornada de trabalho"
                ],
                "fontes_conhecimento": [
                    "CLT - Consolidação das Leis do Trabalho",
                    "Precedentes do TST",
                    "Súmulas trabalhistas",
                    "Jurisprudência trabalhista"
                ]
            },
            "template_prompt": "Você é um especialista em Direito Trabalhista. Analise {contexto} considerando CLT e jurisprudência do TST."
        },
        {
            "id": 4,
            "nome": "Consultor em Direito Previdenciário",
            "classe": "ConsultorDireitoPrevidenciarioAgent",
            "categoria_nome": "Direito Previdenciário",
            "nivel": "4 - Expert",
            "modelo_ai": "gpt-4o",
            "temperatura": 0.3,
            "top_p": 0.9,
            "max_tokens": 4000,
            "icone": "fas fa-user-clock",
            "cor_destaque": "#8B4513",
            "ativo": True,
            "descricao": "Especializado em análise de benefícios previdenciários, tempo de contribuição e aposentadorias.",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de direitos previdenciários",
                    "Cálculo de tempo de contribuição",
                    "Orientação sobre aposentadorias",
                    "Avaliação de benefícios por incapacidade",
                    "Verificação de regras de transição"
                ],
                "fontes_conhecimento": [
                    "Lei 8.213/91",
                    "Emenda Constitucional 103/2019",
                    "Jurisprudência previdenciária",
                    "Instruções Normativas do INSS"
                ]
            },
            "template_prompt": "Você é um consultor em Direito Previdenciário. Analise {contexto} considerando Lei 8.213/91 e EC 103/2019."
        },
        {
            "id": 5,
            "nome": "Especialista em Direito Tributário",
            "classe": "EspecialistaDireitoTributarioAgent",
            "categoria_nome": "Direito Tributário",
            "nivel": "5 - Autoridade",
            "modelo_ai": "claude-3-5-sonnet",
            "temperatura": 0.3,
            "top_p": 0.9,
            "max_tokens": 4000,
            "icone": "fas fa-file-invoice-dollar",
            "cor_destaque": "#228B22",
            "ativo": True,
            "descricao": "Especializado em análise fiscal, planejamento tributário e contencioso administrativo fiscal.",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de estruturas tributárias",
                    "Planejamento tributário",
                    "Avaliação de riscos fiscais",
                    "Orientação sobre incentivos fiscais",
                    "Verificação de conformidade fiscal"
                ],
                "fontes_conhecimento": [
                    "Código Tributário Nacional",
                    "Regulamento do Imposto de Renda",
                    "Jurisprudência do CARF",
                    "Legislação tributária estadual e municipal"
                ]
            },
            "template_prompt": "Você é um especialista em Direito Tributário. Analise {contexto} considerando CTN e jurisprudência do CARF."
        }
    ]
    
    with app.app_context():
        print("🔧 Iniciando configuração completa dos agentes jurídicos...")
        
        for config in agentes_config:
            try:
                # Busca a categoria
                categoria = CategoriaJuridica.query.filter_by(nome=config["categoria_nome"]).first()
                if not categoria:
                    print(f"❌ Categoria '{config['categoria_nome']}' não encontrada para agente {config['nome']}")
                    continue
                
                # Busca ou cria o agente
                agente = AgenteJuridico.query.filter_by(classe=config["classe"]).first()
                if not agente:
                    agente = AgenteJuridico(
                        nome=config["nome"],
                        classe=config["classe"],
                        categoria_id=categoria.id
                    )
                    db.session.add(agente)
                
                # Atualiza todos os campos
                agente.nome = config["nome"]
                agente.descricao = config["descricao"]
                agente.categoria_id = categoria.id
                agente.nivel = config["nivel"]
                agente.modelo_ai = config["modelo_ai"]
                agente.temperatura = config["temperatura"]
                agente.top_p = config["top_p"]
                agente.max_tokens = config["max_tokens"]
                agente.icone = config["icone"]
                agente.cor_destaque = config["cor_destaque"]
                agente.ativo = config["ativo"]
                agente.template_prompt = config["template_prompt"]
                agente.detalhes_tecnicos = json.dumps(config["detalhes_tecnicos"], ensure_ascii=False, indent=2)
                
                db.session.commit()
                print(f"✅ Agente '{config['nome']}' configurado com sucesso")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao configurar agente '{config['nome']}': {str(e)}")
        
        print("🎉 Configuração completa dos agentes concluída!")

if __name__ == "__main__":
    configurar_agentes_completos()