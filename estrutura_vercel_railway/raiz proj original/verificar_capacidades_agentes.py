#!/usr/bin/env python3
"""
Script para verificar e corrigir agentes com capacidades insuficientes ou duplicadas.
Cada agente deve ter exatamente 5 capacidades únicas.
"""

import json
import logging
from collections import Counter
from main import db
from models import AgenteJuridico, CategoriaJuridica

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analisar_capacidades():
    """Analisa as capacidades de todos os agentes e identifica problemas"""
    
    problemas = {
        'sem_capacidades': [],
        'capacidades_insuficientes': [],
        'capacidades_duplicadas': [],
        'capacidades_vazias': [],
        'total_agentes': 0
    }
    
    agentes = AgenteJuridico.query.all()
    problemas['total_agentes'] = len(agentes)
    
    logger.info(f"🔍 Analisando {len(agentes)} agentes...")
    
    for agente in agentes:
        categoria = CategoriaJuridica.query.get(agente.categoria_id)
        categoria_nome = categoria.nome if categoria else "Categoria Desconhecida"
        
        # Verificar se tem capacidades
        if not agente.capacidades:
            problemas['sem_capacidades'].append({
                'id': agente.id,
                'nome': agente.nome,
                'categoria': categoria_nome,
                'categoria_id': agente.categoria_id
            })
            continue
            
        try:
            # Parse das capacidades JSON
            capacidades_list = json.loads(agente.capacidades) if isinstance(agente.capacidades, str) else agente.capacidades
            
            # Verificar se é uma lista válida
            if not isinstance(capacidades_list, list):
                problemas['capacidades_vazias'].append({
                    'id': agente.id,
                    'nome': agente.nome,
                    'categoria': categoria_nome,
                    'capacidades_atual': str(agente.capacidades)
                })
                continue
                
            # Limpar capacidades vazias ou None
            capacidades_limpa = [cap.strip() for cap in capacidades_list if cap and cap.strip()]
            
            # Verificar número de capacidades
            if len(capacidades_limpa) < 5:
                problemas['capacidades_insuficientes'].append({
                    'id': agente.id,
                    'nome': agente.nome,
                    'categoria': categoria_nome,
                    'categoria_id': agente.categoria_id,
                    'capacidades_atual': capacidades_limpa,
                    'total_capacidades': len(capacidades_limpa)
                })
                
            # Verificar duplicatas
            contador = Counter(capacidades_limpa)
            duplicatas = [cap for cap, count in contador.items() if count > 1]
            
            if duplicatas:
                problemas['capacidades_duplicadas'].append({
                    'id': agente.id,
                    'nome': agente.nome,
                    'categoria': categoria_nome,
                    'capacidades_duplicadas': duplicatas,
                    'capacidades_atual': capacidades_limpa
                })
                
        except (json.JSONDecodeError, TypeError) as e:
            problemas['capacidades_vazias'].append({
                'id': agente.id,
                'nome': agente.nome,
                'categoria': categoria_nome,
                'erro': str(e),
                'capacidades_atual': str(agente.capacidades)
            })
    
    return problemas

def relatorio_problemas(problemas):
    """Gera relatório detalhado dos problemas encontrados"""
    
    logger.info("📊 RELATÓRIO DE CAPACIDADES DOS AGENTES")
    logger.info("=" * 60)
    
    logger.info(f"Total de agentes analisados: {problemas['total_agentes']}")
    
    # Agentes sem capacidades
    if problemas['sem_capacidades']:
        logger.warning(f"❌ {len(problemas['sem_capacidades'])} agentes SEM capacidades:")
        for agente in problemas['sem_capacidades']:
            logger.warning(f"  - {agente['nome']} ({agente['categoria']})")
    
    # Agentes com capacidades insuficientes
    if problemas['capacidades_insuficientes']:
        logger.warning(f"⚠️  {len(problemas['capacidades_insuficientes'])} agentes com MENOS de 5 capacidades:")
        for agente in problemas['capacidades_insuficientes']:
            logger.warning(f"  - {agente['nome']} ({agente['categoria']}) - {agente['total_capacidades']} capacidades")
            for cap in agente['capacidades_atual']:
                logger.warning(f"    * {cap}")
    
    # Agentes com capacidades duplicadas
    if problemas['capacidades_duplicadas']:
        logger.warning(f"🔄 {len(problemas['capacidades_duplicadas'])} agentes com capacidades DUPLICADAS:")
        for agente in problemas['capacidades_duplicadas']:
            logger.warning(f"  - {agente['nome']} ({agente['categoria']})")
            logger.warning(f"    Duplicadas: {agente['capacidades_duplicadas']}")
    
    # Agentes com capacidades inválidas
    if problemas['capacidades_vazias']:
        logger.error(f"💥 {len(problemas['capacidades_vazias'])} agentes com capacidades INVÁLIDAS:")
        for agente in problemas['capacidades_vazias']:
            logger.error(f"  - {agente['nome']} ({agente['categoria']})")
            if 'erro' in agente:
                logger.error(f"    Erro: {agente['erro']}")
    
    # Resumo geral
    total_problemas = (len(problemas['sem_capacidades']) + 
                      len(problemas['capacidades_insuficientes']) + 
                      len(problemas['capacidades_duplicadas']) + 
                      len(problemas['capacidades_vazias']))
    
    logger.info("=" * 60)
    if total_problemas == 0:
        logger.info("✅ TODOS OS AGENTES ESTÃO COM CAPACIDADES CORRETAS!")
    else:
        logger.warning(f"❌ Total de agentes com problemas: {total_problemas}")
        agentes_ok = problemas['total_agentes'] - total_problemas
        logger.info(f"✅ Agentes sem problemas: {agentes_ok}")

def corrigir_capacidades_automaticamente(problemas):
    """Corrige automaticamente os problemas de capacidades encontrados"""
    
    logger.info("🔧 Iniciando correção automática das capacidades...")
    
    correcoes_realizadas = 0
    
    try:
        # Corrigir agentes sem capacidades
        for agente_info in problemas['sem_capacidades']:
            agente = AgenteJuridico.query.get(agente_info['id'])
            if agente:
                capacidades_genericas = gerar_capacidades_por_categoria(agente_info['categoria_id'], agente_info['nome'])
                agente.capacidades = json.dumps(capacidades_genericas)
                correcoes_realizadas += 1
                logger.info(f"✅ Adicionadas capacidades para: {agente_info['nome']}")
        
        # Corrigir agentes com capacidades insuficientes
        for agente_info in problemas['capacidades_insuficientes']:
            agente = AgenteJuridico.query.get(agente_info['id'])
            if agente:
                capacidades_atuais = agente_info['capacidades_atual']
                capacidades_faltantes = 5 - len(capacidades_atuais)
                
                # Gerar capacidades adicionais
                novas_capacidades = gerar_capacidades_adicionais(
                    agente_info['categoria_id'], 
                    agente_info['nome'], 
                    capacidades_atuais, 
                    capacidades_faltantes
                )
                
                capacidades_completas = capacidades_atuais + novas_capacidades
                agente.capacidades = json.dumps(capacidades_completas)
                correcoes_realizadas += 1
                logger.info(f"✅ Completadas capacidades para: {agente_info['nome']} (+{capacidades_faltantes})")
        
        # Corrigir agentes com capacidades duplicadas
        for agente_info in problemas['capacidades_duplicadas']:
            agente = AgenteJuridico.query.get(agente_info['id'])
            if agente:
                # Remover duplicatas mantendo ordem
                capacidades_unicas = []
                for cap in agente_info['capacidades_atual']:
                    if cap not in capacidades_unicas:
                        capacidades_unicas.append(cap)
                
                # Se ficou com menos de 5, completar
                if len(capacidades_unicas) < 5:
                    faltantes = 5 - len(capacidades_unicas)
                    capacidades_adicionais = gerar_capacidades_adicionais(
                        agente_info['categoria_id'], 
                        agente_info['nome'], 
                        capacidades_unicas, 
                        faltantes
                    )
                    capacidades_unicas.extend(capacidades_adicionais)
                
                agente.capacidades = json.dumps(capacidades_unicas)
                correcoes_realizadas += 1
                logger.info(f"✅ Removidas duplicatas de: {agente_info['nome']}")
        
        # Corrigir agentes com capacidades inválidas
        for agente_info in problemas['capacidades_vazias']:
            agente = AgenteJuridico.query.get(agente_info['id'])
            if agente:
                capacidades_novas = gerar_capacidades_por_categoria(agente_info['categoria_id'], agente_info['nome'])
                agente.capacidades = json.dumps(capacidades_novas)
                correcoes_realizadas += 1
                logger.info(f"✅ Corrigidas capacidades inválidas de: {agente_info['nome']}")
        
        # Commit das alterações
        db.session.commit()
        logger.info(f"💾 Correções salvas no banco de dados: {correcoes_realizadas} agentes corrigidos")
        
    except Exception as e:
        logger.error(f"❌ Erro durante correção: {str(e)}")
        db.session.rollback()
        return False
    
    return True

def gerar_capacidades_por_categoria(categoria_id, nome_agente):
    """Gera 5 capacidades específicas baseadas na categoria e nome do agente"""
    
    # Mapeamento de capacidades por categoria
    capacidades_base = {
        1: ["Análise de contratos bancários", "Regulamentação do SFN", "Operações de crédito", "Compliance bancário", "Produtos financeiros"],
        2: ["Contratos de seguro", "Análise de sinistros", "Regulamentação SUSEP", "Cobertura securitária", "Prêmios e indenizações"],
        3: ["Contratos de trabalho", "Legislação trabalhista", "Relações de emprego", "Direitos trabalhistas", "Rescisão contratual"],
        4: ["Benefícios previdenciários", "INSS e perícias", "Aposentadorias", "Auxílios previdenciários", "Tempo de contribuição"],
        5: ["Legislação tributária", "Planejamento fiscal", "Obrigações tributárias", "Execução fiscal", "Impostos e contribuições"],
        6: ["Contratos imobiliários", "Registro de imóveis", "Direito registral", "Operações imobiliárias", "Locação e financiamento"],
        7: ["Direito digital", "LGPD e privacidade", "Contratos eletrônicos", "Crimes digitais", "Marco Civil da Internet"],
        8: ["Contratos empresariais", "Direito societário", "Fusões e aquisições", "Compliance empresarial", "Reestruturação societária"],
        9: ["Análise de riscos", "Gestão de contingências", "Avaliação jurídica", "Compliance de riscos", "Estratégias preventivas"],
        10: ["Direito penal", "Processo criminal", "Defesa criminal", "Crimes e contravenções", "Execução penal"],
        11: ["Direito ambiental", "Licenciamento ambiental", "Compliance ambiental", "Legislação ambiental", "Responsabilidade ambiental"],
        12: ["Direito do consumidor", "CDC e proteção", "Relações de consumo", "Práticas comerciais", "Defesa do consumidor"],
        13: ["Direito civil", "Contratos civis", "Responsabilidade civil", "Direitos reais", "Obrigações civis"],
        14: ["Mediação e arbitragem", "Resolução de conflitos", "Negociação jurídica", "Métodos alternativos", "Acordos e conciliação"],
        15: ["Direito de família", "Divórcio e separação", "Guarda e alimentos", "Sucessões e inventário", "União estável"],
        16: ["Direito administrativo", "Atos administrativos", "Licitações e contratos", "Servidor público", "Controle da administração"],
        17: ["Direito constitucional", "Controle de constitucionalidade", "Direitos fundamentais", "Organização dos poderes", "Processo constitucional"]
    }
    
    capacidades_genericas = capacidades_base.get(categoria_id, [
        "Análise jurídica especializada",
        "Interpretação legal",
        "Elaboração de pareceres",
        "Consultoria jurídica",
        "Estratégias processuais"
    ])
    
    # Personalizar baseado no nome do agente
    if "Especialista" in nome_agente:
        especialidade = nome_agente.replace("Especialista em ", "").replace("Especialista de ", "")
        capacidades_genericas[0] = f"Análise especializada em {especialidade.lower()}"
    
    return capacidades_genericas[:5]

def gerar_capacidades_adicionais(categoria_id, nome_agente, capacidades_existentes, quantidade):
    """Gera capacidades adicionais que não conflitem com as existentes"""
    
    capacidades_extras = {
        1: ["Análise de risco de crédito", "Produtos de investimento", "Mercado de capitais", "Prevenção à lavagem", "Câmbio e derivativos"],
        2: ["Resseguros", "Corretagem de seguros", "Atuária", "Fundos de pensão", "Seguros especiais"],
        3: ["Direito sindical", "Segurança do trabalho", "Medicina do trabalho", "Processo trabalhista", "Acordos coletivos"],
        4: ["Regime próprio", "Previdência privada", "Revisão de benefícios", "Contagem de tempo", "Nexo previdenciário"],
        5: ["Auditoria fiscal", "Contencioso tributário", "Transfer pricing", "Tributos estaduais", "Tributos municipais"],
        6: ["Incorporação imobiliária", "Condomínios", "Direito urbanístico", "Parcelamento do solo", "Cartório de imóveis"],
        7: ["Propriedade intelectual", "E-commerce", "Assinatura digital", "Blockchain", "Inteligência artificial"],
        8: ["Recuperação judicial", "Propriedade intelectual", "Contratos internacionais", "ESG empresarial", "Capital de risco"],
        9: ["Due diligence", "Auditoria de compliance", "Gestão de crises", "Planejamento estratégico", "Monitoramento regulatório"],
        10: ["Execução penal", "Tribunal do júri", "Crimes econômicos", "Violência doméstica", "Recursos criminais"],
        11: ["Crimes ambientais", "Licenciamento", "Compensação ambiental", "Auditoria ambiental", "Sustentabilidade"],
        12: ["Publicidade enganosa", "E-commerce", "Superendividamento", "Recall", "SAC e atendimento"],
        13: ["Família e sucessões", "Responsabilidade civil", "Contratos em geral", "Propriedade", "Vizinhança"],
        14: ["Conciliação", "Câmaras arbitrais", "Conflitos empresariais", "Mediação familiar", "Justiça restaurativa"],
        15: ["Adoção", "Violência doméstica", "Alienação parental", "Bem de família", "Planejamento sucessório"],
        16: ["Improbidade administrativa", "Licitações", "Desapropriação", "Servidor público", "Controle externo"],
        17: ["Mandado de segurança", "Ação popular", "Inconstitucionalidade", "Direitos fundamentais", "Federalismo"]
    }
    
    extras = capacidades_extras.get(categoria_id, [
        "Elaboração de petições",
        "Análise de jurisprudência",
        "Pareceres técnicos",
        "Consultoria especializada",
        "Estratégias processuais"
    ])
    
    # Filtrar capacidades que já existem
    novas_capacidades = []
    for cap in extras:
        if cap not in capacidades_existentes and len(novas_capacidades) < quantidade:
            novas_capacidades.append(cap)
    
    # Se ainda falta, completar com capacidades genéricas
    while len(novas_capacidades) < quantidade:
        cap_generica = f"Análise jurídica avançada - {len(novas_capacidades) + 1}"
        if cap_generica not in capacidades_existentes:
            novas_capacidades.append(cap_generica)
    
    return novas_capacidades

def executar_verificacao_completa():
    """Executa verificação completa e correção das capacidades"""
    
    logger.info("🚀 Iniciando verificação completa das capacidades dos agentes...")
    
    # Analisar problemas
    problemas = analisar_capacidades()
    
    # Gerar relatório
    relatorio_problemas(problemas)
    
    # Perguntar se deve corrigir
    total_problemas = (len(problemas['sem_capacidades']) + 
                      len(problemas['capacidades_insuficientes']) + 
                      len(problemas['capacidades_duplicadas']) + 
                      len(problemas['capacidades_vazias']))
    
    if total_problemas > 0:
        logger.info(f"🔧 Iniciando correção automática de {total_problemas} problemas...")
        sucesso = corrigir_capacidades_automaticamente(problemas)
        
        if sucesso:
            logger.info("✅ Correção concluída com sucesso!")
            # Verificar novamente após correção
            logger.info("🔍 Verificação pós-correção:")
            problemas_pos = analisar_capacidades()
            relatorio_problemas(problemas_pos)
        else:
            logger.error("❌ Falha na correção automática")
    
    return problemas

if __name__ == "__main__":
    try:
        with db.session.begin():
            problemas = executar_verificacao_completa()
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")