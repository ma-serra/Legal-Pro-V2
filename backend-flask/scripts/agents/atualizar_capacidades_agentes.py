#!/usr/bin/env python3
"""
Script para atualizar todos os agentes especialistas com 5 capacidades específicas
baseadas em suas áreas de especialização jurídica.
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configurar conexão com banco
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Mapeamento de capacidades por área de especialização
CAPACIDADES_POR_AREA = {
    "Direito Penal": [
        "Análise de tipificação penal e elementos do crime",
        "Elaboração de defesas técnicas em processos criminais",
        "Interpretação de jurisprudência dos tribunais superiores",
        "Cálculo de penas e benefícios processuais",
        "Estratégias de alegações preliminares e nulidades"
    ],
    
    "Direito Civil": [
        "Análise de contratos e responsabilidade civil",
        "Interpretação do Código Civil e legislação especial",
        "Elaboração de pareceres sobre direitos reais",
        "Cálculo de danos materiais e morais",
        "Estratégias em ações de cobrança e execução"
    ],
    
    "Direito Trabalhista": [
        "Análise de relações de emprego e CLT",
        "Cálculo de verbas rescisórias e indenizações",
        "Interpretação de convenções coletivas",
        "Estratégias em processos trabalhistas",
        "Análise de acidentes de trabalho e doenças ocupacionais"
    ],
    
    "Direito Empresarial": [
        "Análise de contratos empresariais e societários",
        "Interpretação da Lei das S.A. e Código Civil",
        "Elaboração de pareceres sobre governança corporativa",
        "Estratégias em fusões, aquisições e reestruturações",
        "Análise de compliance e responsabilidade empresarial"
    ],
    
    "Direito Tributário": [
        "Análise do CTN e legislação tributária específica",
        "Cálculo de tributos e planejamento tributário",
        "Interpretação de jurisprudência fiscal",
        "Estratégias em execuções fiscais e parcelamentos",
        "Elaboração de defesas em processos administrativos"
    ],
    
    "Direito do Consumidor": [
        "Análise do CDC e direitos do consumidor",
        "Interpretação de práticas abusivas e publicidade",
        "Cálculo de danos e restituições em dobro",
        "Estratégias em ações coletivas e individuais",
        "Análise de contratos de adesão e cláusulas abusivas"
    ],
    
    "Direito Imobiliário": [
        "Análise de contratos imobiliários e escrituras",
        "Interpretação da Lei de Registros Públicos",
        "Elaboração de pareceres sobre usucapião",
        "Estratégias em ações possessórias",
        "Análise de incorporações e condomínios"
    ],
    
    "Direito Bancário": [
        "Análise de contratos bancários e financeiros",
        "Interpretação de regulamentação do SFN",
        "Cálculo de juros e encargos financeiros",
        "Estratégias em revisões contratuais",
        "Análise de operações de crédito e garantias"
    ],
    
    "Direito Securitário": [
        "Análise de contratos de seguros e resseguros",
        "Interpretação da regulamentação SUSEP",
        "Cálculo de indenizações e coberturas",
        "Estratégias em regulação de sinistros",
        "Análise de responsabilidade civil de corretores"
    ],
    
    "Direito Agrário": [
        "Análise de contratos agrários e fundiários",
        "Interpretação da Lei Agrária e Estatuto da Terra",
        "Elaboração de pareceres sobre reforma agrária",
        "Estratégias em ações de desapropriação",
        "Análise de regularização fundiária"
    ],
    
    "Recuperação de Crédito": [
        "Análise de títulos executivos e garantias",
        "Estratégias em execuções judiciais e extrajudiciais",
        "Interpretação de falências e recuperações",
        "Cálculo de juros, multas e correção monetária",
        "Elaboração de acordos e parcelamentos"
    ],
    
    "Compliance Bancário": [
        "Análise de normas regulamentares do BACEN",
        "Interpretação de políticas de prevenção à lavagem",
        "Elaboração de procedimentos de compliance",
        "Estratégias em auditorias e fiscalizações",
        "Análise de responsabilidade de administradores"
    ],
    
    "Crimes Financeiros": [
        "Análise de crimes contra o sistema financeiro",
        "Interpretação da Lei de Lavagem de Dinheiro",
        "Elaboração de defesas em crimes econômicos",
        "Estratégias em investigações financeiras",
        "Análise de colaboração premiada e delação"
    ],
    
    "Crimes de Drogas": [
        "Análise da Lei 11.343/06 e tipificação",
        "Interpretação de jurisprudência sobre drogas",
        "Elaboração de defesas técnicas especializadas",
        "Estratégias de desclassificação de condutas",
        "Análise de medidas cautelares alternativas"
    ],
    
    "Litígios Coletivos": [
        "Análise de ações civis públicas e coletivas",
        "Interpretação do Código de Defesa do Consumidor",
        "Elaboração de termos de ajustamento de conduta",
        "Estratégias em class actions e ações populares",
        "Análise de legitimidade e representatividade"
    ],
    
    "Conciliação e Mediação": [
        "Técnicas de mediação e conciliação judicial",
        "Análise de viabilidade de acordos",
        "Elaboração de propostas de transação",
        "Estratégias de negociação colaborativa",
        "Interpretação de marcos legais da mediação"
    ],
    
    # Capacidades para especialistas em análise e processamento
    "Análise Documental": [
        "Extração e análise de informações jurídicas relevantes",
        "Identificação de pontos controvertidos em documentos",
        "Classificação de documentos por área jurídica",
        "Síntese de peças processuais e contratos",
        "Detecção de inconsistências e irregularidades"
    ],
    
    "Revisão Legal": [
        "Revisão técnica de pareceres e petições",
        "Verificação de fundamentação jurídica",
        "Análise de precedentes e jurisprudência aplicável",
        "Controle de qualidade em documentos jurídicos",
        "Validação de citações e referências legais"
    ],
    
    "Análise de Riscos": [
        "Identificação de riscos jurídicos em operações",
        "Avaliação de probabilidade de sucesso processual",
        "Análise de impacto financeiro de decisões",
        "Mapeamento de passivos contingentes",
        "Elaboração de matriz de riscos jurídicos"
    ]
}

def conectar_database():
    """Conecta ao banco PostgreSQL"""
    try:
        session = Session()
        print("✅ Conectado ao banco de dados")
        return session
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {e}")
        return None

def obter_todos_agentes(session):
    """Obtém todos os agentes ativos do banco"""
    try:
        query = text("""
            SELECT aj.id, aj.nome, aj.descricao, aj.ativo, cj.nome as categoria_nome
            FROM agente_juridico aj
            LEFT JOIN categoria_juridica cj ON aj.categoria_id = cj.id
            WHERE aj.ativo = true
            ORDER BY aj.id
        """)
        
        result = session.execute(query)
        agentes = result.fetchall()
        print(f"✅ Encontrados {len(agentes)} agentes ativos")
        return agentes
    except Exception as e:
        print(f"❌ Erro ao obter agentes: {e}")
        return []

def determinar_area_agente(nome, descricao, categoria):
    """Determina a área de especialização do agente baseado em nome, descrição e categoria"""
    nome_lower = nome.lower() if nome else ""
    descricao_lower = descricao.lower() if descricao else ""
    categoria_lower = categoria.lower() if categoria else ""
    
    # Mapeamento por palavras-chave
    mapeamentos = {
        "Direito Penal": ["penal", "criminal", "crime", "defesa criminal"],
        "Direito Civil": ["civil", "contratos", "responsabilidade civil"],
        "Direito Trabalhista": ["trabalhista", "clt", "trabalho", "emprego"],
        "Direito Empresarial": ["empresarial", "societário", "empresa", "corporativo"],
        "Direito Tributário": ["tributário", "fiscal", "tributo", "imposto"],
        "Direito do Consumidor": ["consumidor", "cdc", "relação de consumo"],
        "Direito Imobiliário": ["imobiliário", "imóvel", "posse", "propriedade"],
        "Direito Bancário": ["bancário", "financeiro", "banco", "crédito"],
        "Direito Securitário": ["securitário", "seguro", "resseguro", "susep"],
        "Direito Agrário": ["agrário", "rural", "terra", "agronegócio"],
        "Recuperação de Crédito": ["recuperação", "crédito", "cobrança", "execução"],
        "Compliance Bancário": ["compliance", "regulamentação", "bacen"],
        "Crimes Financeiros": ["financeiro", "lavagem", "econômico"],
        "Crimes de Drogas": ["droga", "entorpecente", "11.343"],
        "Litígios Coletivos": ["coletivo", "civil pública", "class action"],
        "Conciliação e Mediação": ["conciliação", "mediação", "acordo"],
        "Análise Documental": ["análise", "documento", "extração"],
        "Revisão Legal": ["revisão", "controle", "qualidade"],
        "Análise de Riscos": ["risco", "contingente", "probabilidade"]
    }
    
    texto_completo = f"{nome_lower} {descricao_lower} {categoria_lower}"
    
    for area, palavras_chave in mapeamentos.items():
        if any(palavra in texto_completo for palavra in palavras_chave):
            return area
    
    # Fallback baseado na categoria
    if categoria:
        if "penal" in categoria_lower or "criminal" in categoria_lower:
            return "Direito Penal"
        elif "civil" in categoria_lower:
            return "Direito Civil"
        elif "trabalhista" in categoria_lower:
            return "Direito Trabalhista"
        elif "empresarial" in categoria_lower:
            return "Direito Empresarial"
        elif "tributário" in categoria_lower:
            return "Direito Tributário"
    
    # Fallback padrão
    return "Análise Documental"

def atualizar_capacidades_agente(session, agente_id, capacidades):
    """Atualiza as capacidades de um agente específico"""
    try:
        capacidades_json = json.dumps(capacidades, ensure_ascii=False)
        
        query = text("""
            UPDATE agente_juridico 
            SET capacidades = :capacidades,
                data_atualizacao = :data_atualizacao
            WHERE id = :agente_id
        """)
        
        session.execute(query, {
            'capacidades': capacidades_json,
            'agente_id': agente_id,
            'data_atualizacao': datetime.now()
        })
        
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar agente {agente_id}: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando atualização de capacidades dos agentes especialistas...")
    
    session = conectar_database()
    if not session:
        return
    
    try:
        agentes = obter_todos_agentes(session)
        if not agentes:
            print("❌ Nenhum agente encontrado")
            return
        
        sucessos = 0
        falhas = 0
        
        for agente in agentes:
            agente_id, nome, descricao, ativo, categoria_nome = agente
            
            print(f"\n📋 Processando agente: {nome} (ID: {agente_id})")
            
            # Determinar área de especialização
            area_especializada = determinar_area_agente(nome, descricao, categoria_nome)
            print(f"   Área identificada: {area_especializada}")
            
            # Obter capacidades para a área
            capacidades = CAPACIDADES_POR_AREA.get(area_especializada, CAPACIDADES_POR_AREA["Análise Documental"])
            
            # Atualizar no banco
            if atualizar_capacidades_agente(session, agente_id, capacidades):
                print(f"   ✅ Capacidades atualizadas com sucesso")
                print(f"   📝 Capacidades: {', '.join(capacidades[:2])}...")
                sucessos += 1
            else:
                print(f"   ❌ Falha ao atualizar capacidades")
                falhas += 1
        
        # Commit das alterações
        session.commit()
        
        print(f"\n📊 Resumo da atualização:")
        print(f"   ✅ Sucessos: {sucessos}")
        print(f"   ❌ Falhas: {falhas}")
        print(f"   📁 Total processado: {len(agentes)}")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()