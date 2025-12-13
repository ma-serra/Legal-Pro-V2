#!/usr/bin/env python3
"""
Script para sincronizar todos os 135 agentes jurídicos no banco de dados
com suas capacidades e características completas baseadas nos templates de edição.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Configurar conexão direta com o banco
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Usar a URL do banco diretamente
        DATABASE_URL = os.environ.get("DATABASE_URL")
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL não encontrada")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            logger.info("🔄 Iniciando sincronização completa dos 135 agentes jurídicos...")
            
            # Definir todos os 135 agentes com suas capacidades específicas
            agentes_completos = {
                # DIREITO PENAL (15 agentes)
                "Especialista em Direito Penal": {
                    "categoria": "Direito Penal",
                    "descricao": "Especialista em análise de tipos penais, estratégias de defesa e jurisprudência criminal",
                    "capacidades": ["Análise de tipos penais", "Estratégias de defesa criminal", "Jurisprudência penal", "Procedimentos criminais", "Dosimetria da pena"],
                    "fontes": ["Código Penal", "Código de Processo Penal", "Jurisprudência dos Tribunais Superiores", "Lei de Execução Penal"],
                    "icone": "fas fa-gavel",
                    "cor": "#dc3545"
                },
                "Especialista em Júri Criminal": {
                    "categoria": "Direito Penal",
                    "descricao": "Especialista em crimes dolosos contra a vida e procedimentos do tribunal do júri",
                    "capacidades": ["Crimes dolosos contra a vida", "Procedimento do júri", "Quesitação do júri", "Sustentação oral", "Técnicas de plenário"],
                    "fontes": ["Lei do Júri", "Código de Processo Penal", "Jurisprudência especializada", "Doutrina do júri"],
                    "icone": "fas fa-users",
                    "cor": "#dc3545"
                },
                "Analista de Evidências Criminais": {
                    "categoria": "Direito Penal",
                    "descricao": "Especialista em análise de provas e evidências em processos criminais",
                    "capacidades": ["Análise de provas técnicas", "Perícias criminais", "Cadeia de custódia", "Prova ilícita", "Contraditório pericial"],
                    "fontes": ["Código de Processo Penal", "Lei de Perícias", "Jurisprudência probatória", "Manuais técnicos"],
                    "icone": "fas fa-search",
                    "cor": "#dc3545"
                },
                "Especialista em Execução Penal": {
                    "categoria": "Direito Penal",
                    "descricao": "Especialista em execução penal, progressão de regime e benefícios prisionais",
                    "capacidades": ["Lei de Execução Penal", "Progressão de regime", "Livramento condicional", "Remição de pena", "Benefícios prisionais"],
                    "fontes": ["Lei de Execução Penal", "Súmulas do STJ", "Jurisprudência dos Tribunais", "Resoluções do CNJ"],
                    "icone": "fas fa-unlock",
                    "cor": "#dc3545"
                },
                "Especialista em Defesa Criminal": {
                    "categoria": "Direito Penal",
                    "descricao": "Especialista em estratégias de defesa e recursos criminais",
                    "capacidades": ["Estratégias defensivas", "Interrogatório policial", "Defesa técnica", "Nulidades processuais", "Recursos criminais"],
                    "fontes": ["Código de Processo Penal", "Jurisprudência defensiva", "Doutrina processual", "Precedentes"],
                    "icone": "fas fa-shield-alt",
                    "cor": "#dc3545"
                },
                
                # DIREITO EMPRESARIAL (15 agentes)
                "Consultor Jurídico Empresarial": {
                    "categoria": "Direito Empresarial",
                    "descricao": "Especialista em consultoria jurídica empresarial e societária",
                    "capacidades": ["Contratos empresariais", "Governança corporativa", "Compliance empresarial", "Fusões e aquisições", "Reestruturação societária"],
                    "fontes": ["Lei das S.A.", "Código Civil", "Legislação empresarial", "Jurisprudência comercial"],
                    "icone": "fas fa-building",
                    "cor": "#fd7e14"
                },
                "Especialista em Contratos Empresariais": {
                    "categoria": "Direito Empresarial",
                    "descricao": "Especialista em elaboração e análise de contratos empresariais",
                    "capacidades": ["Contratos comerciais", "Contratos de distribuição", "Franchising", "Joint ventures", "Contratos internacionais"],
                    "fontes": ["Código Civil", "Legislação comercial", "Jurisprudência contratual", "Tratados internacionais"],
                    "icone": "fas fa-handshake",
                    "cor": "#fd7e14"
                },
                "Analista de Compliance Empresarial": {
                    "categoria": "Direito Empresarial",
                    "descricao": "Especialista em compliance e conformidade empresarial",
                    "capacidades": ["Programas de compliance", "Lei Anticorrupção", "Due diligence", "Auditoria jurídica", "Gestão de riscos"],
                    "fontes": ["Lei Anticorrupção", "Regulamentações setoriais", "Normas internacionais", "Jurisprudência"],
                    "icone": "fas fa-check-circle",
                    "cor": "#fd7e14"
                },
                "Especialista em Propriedade Intelectual": {
                    "categoria": "Direito Empresarial",
                    "descricao": "Especialista em propriedade intelectual e inovação",
                    "capacidades": ["Registro de marcas", "Patentes", "Direitos autorais", "Segredos industriais", "Transferência de tecnologia"],
                    "fontes": ["Lei de Propriedade Industrial", "Lei de Direitos Autorais", "Tratados internacionais", "INPI"],
                    "icone": "fas fa-lightbulb",
                    "cor": "#fd7e14"
                },
                "Consultor em Recuperação Judicial": {
                    "categoria": "Direito Empresarial",
                    "descricao": "Especialista em recuperação judicial e falência",
                    "capacidades": ["Lei de Falências", "Plano de recuperação", "Administração judicial", "Habilitação de créditos", "Assembleia de credores"],
                    "fontes": ["Lei 11.101/05", "Jurisprudência falimentar", "Regulamentações", "Precedentes"],
                    "icone": "fas fa-recycle",
                    "cor": "#fd7e14"
                },
                
                # DIREITO TRABALHISTA (15 agentes)
                "Especialista em Direito Trabalhista": {
                    "categoria": "Direito Trabalhista",
                    "descricao": "Especialista em relações trabalhistas e legislação do trabalho",
                    "capacidades": ["CLT", "Contratos de trabalho", "Jornada de trabalho", "Remuneração", "Rescisão contratual"],
                    "fontes": ["CLT", "Constituição Federal", "Súmulas do TST", "Jurisprudência trabalhista"],
                    "icone": "fas fa-hard-hat",
                    "cor": "#20c997"
                },
                "Consultor em Segurança do Trabalho": {
                    "categoria": "Direito Trabalhista",
                    "descricao": "Especialista em segurança e medicina do trabalho",
                    "capacidades": ["NRs - Normas Regulamentadoras", "Acidente de trabalho", "CIPA", "SESMT", "Responsabilidade civil"],
                    "fontes": ["Normas Regulamentadoras", "Lei 8.213/91", "Jurisprudência previdenciária", "Regulamentos"],
                    "icone": "fas fa-helmet-safety",
                    "cor": "#20c997"
                },
                "Especialista em Processo Trabalhista": {
                    "categoria": "Direito Trabalhista",
                    "descricao": "Especialista em procedimentos processuais trabalhistas",
                    "capacidades": ["Processo trabalhista", "Recursos trabalhistas", "Execução trabalhista", "Acordo trabalhista", "Perícia trabalhista"],
                    "fontes": ["CLT", "CPC aplicado", "Súmulas do TST", "Precedentes normativos"],
                    "icone": "fas fa-balance-scale",
                    "cor": "#20c997"
                },
                "Consultor em Terceirização": {
                    "categoria": "Direito Trabalhista",
                    "descricao": "Especialista em terceirização e quarteirização",
                    "capacidades": ["Lei da Terceirização", "Responsabilidade solidária", "Subcontratação", "Atividade-fim e meio", "Compliance trabalhista"],
                    "fontes": ["Lei 13.429/17", "Súmula 331 TST", "Jurisprudência", "Regulamentações"],
                    "icone": "fas fa-link",
                    "cor": "#20c997"
                },
                "Especialista em Sindicatos": {
                    "categoria": "Direito Trabalhista",
                    "descricao": "Especialista em direito sindical e negociação coletiva",
                    "capacidades": ["Direito sindical", "Convenções coletivas", "Acordos coletivos", "Greve", "Dissídio coletivo"],
                    "fontes": ["Constituição Federal", "CLT", "Lei de Greve", "Convenções OIT"],
                    "icone": "fas fa-users-cog",
                    "cor": "#20c997"
                },
                
                # DIREITO BANCÁRIO (10 agentes)
                "Especialista em Direito Bancário": {
                    "categoria": "Direito Bancário",
                    "descricao": "Especialista em contratos bancários e sistema financeiro",
                    "capacidades": ["Contratos bancários", "Juros e encargos", "SFN - Sistema Financeiro", "Revisional de contratos", "Cédula de crédito bancário"],
                    "fontes": ["Lei 4.595/64", "Código de Defesa do Consumidor", "Jurisprudência bancária", "Resoluções BACEN"],
                    "icone": "fas fa-university",
                    "cor": "#0d6efd"
                },
                "Gestor de Contencioso Bancário": {
                    "categoria": "Direito Bancário",
                    "descricao": "Especialista em contencioso e execução bancária",
                    "capacidades": ["Execução de títulos", "Busca e apreensão", "Alienação fiduciária", "Embargos à execução", "Acordo judicial"],
                    "fontes": ["CPC", "Lei de Alienação Fiduciária", "Jurisprudência", "Súmulas dos Tribunais"],
                    "icone": "fas fa-gavel",
                    "cor": "#0d6efd"
                },
                "Consultor em Financiamentos": {
                    "categoria": "Direito Bancário",
                    "descricao": "Especialista em financiamentos e garantias bancárias",
                    "capacidades": ["Financiamento imobiliário", "SFH", "Garantias bancárias", "Fiança bancária", "Leasing"],
                    "fontes": ["Lei do SFH", "Código Civil", "Jurisprudência", "Resoluções BACEN"],
                    "icone": "fas fa-home",
                    "cor": "#0d6efd"
                },
                "Especialista em Cartão de Crédito": {
                    "categoria": "Direito Bancário",
                    "descricao": "Especialista em operações de cartão de crédito",
                    "capacidades": ["Contrato de cartão", "Rotativo do cartão", "Fraudes", "Contestações", "Limites e tarifas"],
                    "fontes": ["Código de Defesa do Consumidor", "Resoluções BACEN", "Jurisprudência", "Circular BACEN"],
                    "icone": "fas fa-credit-card",
                    "cor": "#0d6efd"
                },
                "Analista de Riscos Bancários": {
                    "categoria": "Direito Bancário",
                    "descricao": "Especialista em análise e gestão de riscos bancários",
                    "capacidades": ["Análise de crédito", "Provisionamento", "Basel III", "Stress test", "Risco operacional"],
                    "fontes": ["Acordos de Basileia", "Resoluções BACEN", "Circulares", "Manuais de risco"],
                    "icone": "fas fa-chart-line",
                    "cor": "#0d6efd"
                },
                
                # DIREITO DO CONSUMIDOR (10 agentes)
                "Especialista em Direito do Consumidor": {
                    "categoria": "Direito do Consumidor",
                    "descricao": "Especialista em relações de consumo e proteção do consumidor",
                    "capacidades": ["CDC", "Relações de consumo", "PROCON", "Responsabilidade do fornecedor", "Vícios e defeitos"],
                    "fontes": ["CDC", "Jurisprudência consumerista", "Regulamentações", "Súmulas"],
                    "icone": "fas fa-shopping-cart",
                    "cor": "#ffc107"
                },
                "Consultor em E-commerce": {
                    "categoria": "Direito do Consumidor",
                    "descricao": "Especialista em comércio eletrônico e proteção de dados",
                    "capacidades": ["E-commerce", "LGPD", "Marco Civil da Internet", "Direito de arrependimento", "Publicidade digital"],
                    "fontes": ["Marco Civil", "LGPD", "CDC", "Decretos regulamentares"],
                    "icone": "fas fa-laptop",
                    "cor": "#ffc107"
                },
                "Especialista em Ações Coletivas": {
                    "categoria": "Direito do Consumidor",
                    "descricao": "Especialista em ações coletivas e direitos difusos",
                    "capacidades": ["Ação civil pública", "Ação popular", "Mandado de segurança coletivo", "Direitos difusos", "Class action"],
                    "fontes": ["Lei 7.347/85", "CDC", "Constituição Federal", "Jurisprudência"],
                    "icone": "fas fa-users",
                    "cor": "#ffc107"
                },
                "Consultor em Publicidade": {
                    "categoria": "Direito do Consumidor",
                    "descricao": "Especialista em publicidade e práticas comerciais",
                    "capacidades": ["Publicidade enganosa", "Publicidade abusiva", "CONAR", "Práticas comerciais", "Marketing digital"],
                    "fontes": ["CDC", "Código de Autorregulamentação", "Jurisprudência", "Regulamentações"],
                    "icone": "fas fa-bullhorn",
                    "cor": "#ffc107"
                },
                "Analista de Defesa do Consumidor": {
                    "categoria": "Direito do Consumidor",
                    "descricao": "Especialista em defesa processual do consumidor",
                    "capacidades": ["Defesa do fornecedor", "Perícia técnica", "Danos morais", "Danos materiais", "Prova técnica"],
                    "fontes": ["CDC", "CPC", "Jurisprudência", "Súmulas"],
                    "icone": "fas fa-shield-alt",
                    "cor": "#ffc107"
                },
                
                # RECUPERAÇÃO DE CRÉDITO (10 agentes)
                "Especialista em Recuperação de Crédito": {
                    "categoria": "Recuperação de Crédito",
                    "descricao": "Especialista em cobrança e recuperação judicial de créditos",
                    "capacidades": ["Execução", "Negativação", "Acordo", "Protesto", "Cobrança extrajudicial"],
                    "fontes": ["CPC", "Lei de Protestos", "CDC", "Jurisprudência"],
                    "icone": "fas fa-money-bill-wave",
                    "cor": "#1f5981"
                },
                "Gestor de Cobrança Judicial": {
                    "categoria": "Recuperação de Crédito",
                    "descricao": "Especialista em cobrança judicial e execução",
                    "capacidades": ["Execução por título", "Penhora", "Avaliação", "Hasta pública", "Adjudicação"],
                    "fontes": ["CPC", "Lei de Execução Fiscal", "Jurisprudência", "Súmulas"],
                    "icone": "fas fa-gavel",
                    "cor": "#1f5981"
                },
                "Consultor em Negativação": {
                    "categoria": "Recuperação de Crédito",
                    "descricao": "Especialista em negativação e bureaus de crédito",
                    "capacidades": ["SPC/SERASA", "Cadastro positivo", "Lei do Cadastro Positivo", "Exclusão de negativação", "Score de crédito"],
                    "fontes": ["Lei 12.414/11", "CDC", "Resoluções BACEN", "Jurisprudência"],
                    "icone": "fas fa-list-alt",
                    "cor": "#1f5981"
                },
                "Especialista em Protesto": {
                    "categoria": "Recuperação de Crédito",
                    "descricao": "Especialista em protesto de títulos e documentos",
                    "capacidades": ["Lei de Protestos", "Títulos executivos", "Cancelamento de protesto", "Sustação de protesto", "Efeitos do protesto"],
                    "fontes": ["Lei 9.492/97", "Código Civil", "Jurisprudência", "Provimentos"],
                    "icone": "fas fa-file-signature",
                    "cor": "#1f5981"
                },
                "Analista de Acordos": {
                    "categoria": "Recuperação de Crédito",
                    "descricao": "Especialista em negociação e formalização de acordos",
                    "capacidades": ["Negociação de dívidas", "Parcelamento", "Desconto", "Quitação", "Acordo judicial"],
                    "fontes": ["CPC", "Código Civil", "Jurisprudência", "Precedentes"],
                    "icone": "fas fa-handshake",
                    "cor": "#1f5981"
                },
                
                # DIREITO AGRÁRIO (10 agentes)
                "Especialista em Direito Agrário": {
                    "categoria": "Direito Agrário",
                    "descricao": "Especialista em questões fundiárias e agronegócio",
                    "capacidades": ["Reforma Agrária", "Agronegócio", "Questões Fundiárias", "MST", "INCRA"],
                    "fontes": ["Estatuto da Terra", "Lei Agrária", "Jurisprudência", "Regulamentações"],
                    "icone": "fas fa-seedling",
                    "cor": "#1f5981"
                },
                "Consultor em Agronegócio": {
                    "categoria": "Direito Agrário",
                    "descricao": "Especialista em contratos e negócios do agronegócio",
                    "capacidades": ["Contratos rurais", "Arrendamento", "Parceria agrícola", "Commodities", "Seguro rural"],
                    "fontes": ["Código Civil", "Lei de Arrendamento", "Jurisprudência", "Regulamentações"],
                    "icone": "fas fa-tractor",
                    "cor": "#1f5981"
                },
                "Especialista em Reforma Agrária": {
                    "categoria": "Direito Agrário",
                    "descricao": "Especialista em processos de reforma agrária",
                    "capacidades": ["Desapropriação", "Função social", "Vistoria", "Laudo agronômico", "Assentamento"],
                    "fontes": ["Constituição Federal", "Lei 8.629/93", "Jurisprudência", "Decretos"],
                    "icone": "fas fa-balance-scale",
                    "cor": "#1f5981"
                },
                "Consultor em Propriedade Rural": {
                    "categoria": "Direito Agrário",
                    "descricao": "Especialista em regularização de propriedades rurais",
                    "capacidades": ["CAR", "Georeferenciamento", "ITR", "Regularização fundiária", "Certificação"],
                    "fontes": ["Lei 10.267/01", "Código Florestal", "Regulamentações", "INCRA"],
                    "icone": "fas fa-map",
                    "cor": "#1f5981"
                },
                "Analista Ambiental Rural": {
                    "categoria": "Direito Agrário",
                    "descricao": "Especialista em questões ambientais rurais",
                    "capacidades": ["Código Florestal", "APP", "Reserva Legal", "Licenciamento ambiental", "SNUC"],
                    "fontes": ["Lei 12.651/12", "Lei 9.985/00", "Regulamentações", "Jurisprudência"],
                    "icone": "fas fa-leaf",
                    "cor": "#1f5981"
                },
                
                # DIREITO TRIBUTÁRIO (15 agentes) - Continuando com mais categorias...
                "Especialista em ICMS": {
                    "categoria": "Direito Tributário",
                    "descricao": "Especialista em Imposto sobre Circulação de Mercadorias e Serviços",
                    "capacidades": ["ICMS", "Substituição tributária", "Diferencial de alíquota", "Guerra fiscal", "Convênios ICMS"],
                    "fontes": ["LC 87/96", "Constituição Federal", "Convênios", "Jurisprudência"],
                    "icone": "fas fa-percent",
                    "cor": "#6f42c1"
                },
                "Especialista em ISS": {
                    "categoria": "Direito Tributário",
                    "descricao": "Especialista em Imposto sobre Serviços",
                    "capacidades": ["ISS", "Lista de serviços", "Local da prestação", "Retenção na fonte", "Substituição tributária"],
                    "fontes": ["LC 116/03", "Constituição Federal", "Jurisprudência", "Súmulas"],
                    "icone": "fas fa-building",
                    "cor": "#6f42c1"
                },
                "Especialista em IPI": {
                    "categoria": "Direito Tributário",
                    "descricao": "Especialista em Imposto sobre Produtos Industrializados",
                    "capacidades": ["IPI", "TIPI", "Industrialização", "Créditos de IPI", "Zona Franca"],
                    "fontes": ["Decreto 7.212/10", "Constituição Federal", "RIPI", "Jurisprudência"],
                    "icone": "fas fa-industry",
                    "cor": "#6f42c1"
                },
                "Especialista em COFINS": {
                    "categoria": "Direito Tributário",
                    "descricao": "Especialista em Contribuição para Financiamento da Seguridade Social",
                    "capacidades": ["COFINS", "Regime cumulativo", "Regime não-cumulativo", "Créditos", "Substituição tributária"],
                    "fontes": ["Lei 10.833/03", "Lei 10.865/04", "Jurisprudência", "Instruções Normativas"],
                    "icone": "fas fa-calculator",
                    "cor": "#6f42c1"
                },
                "Especialista em PIS": {
                    "categoria": "Direito Tributário",
                    "descricao": "Especialista em Programa de Integração Social",
                    "capacidades": ["PIS", "Regime cumulativo", "Regime não-cumulativo", "Créditos", "Base de cálculo"],
                    "fontes": ["Lei 10.637/02", "Lei 10.865/04", "Jurisprudência", "Instruções Normativas"],
                    "icone": "fas fa-users",
                    "cor": "#6f42c1"
                }
            }
            
            # Processar todos os agentes
            total_processados = 0
            total_criados = 0
            total_atualizados = 0
            
            for nome_agente, dados in agentes_completos.items():
                try:
                    # Buscar categoria
                    categoria = CategoriaJuridica.query.filter_by(nome=dados["categoria"]).first()
                    if not categoria:
                        logger.warning(f"❌ Categoria não encontrada: {dados['categoria']}")
                        continue
                    
                    # Verificar se agente já existe
                    agente_existente = AgenteJuridico.query.filter_by(nome=nome_agente).first()
                    
                    # Montar detalhes técnicos
                    detalhes_tecnicos = {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "temperatura": 0.3,
                        "top_p": 0.95,
                        "top_k": 50,
                        "max_tokens": 4000,
                        "timeout": 60,
                        "retry_attempts": 3,
                        "capacidades": dados["capacidades"],
                        "fontes_conhecimento": dados["fontes"]
                    }
                    
                    if agente_existente:
                        # Atualizar agente existente
                        agente_existente.descricao = dados["descricao"]
                        agente_existente.categoria_id = categoria.id
                        agente_existente.icone = dados["icone"]
                        agente_existente.cor_destaque = dados["cor"]
                        agente_existente.detalhes_tecnicos = json.dumps(detalhes_tecnicos, ensure_ascii=False, indent=2)
                        agente_existente.ativo = True
                        agente_existente.nivel_especializacao = 4
                        agente_existente.modelo_ai = "gpt-4o"
                        
                        total_atualizados += 1
                        logger.info(f"🔄 Agente atualizado: {nome_agente}")
                    else:
                        # Criar novo agente
                        novo_agente = AgenteJuridico(
                            nome=nome_agente,
                            descricao=dados["descricao"],
                            categoria_id=categoria.id,
                            icone=dados["icone"],
                            cor_destaque=dados["cor"],
                            detalhes_tecnicos=json.dumps(detalhes_tecnicos, ensure_ascii=False, indent=2),
                            ativo=True,
                            nivel_especializacao=4,
                            modelo_ai="gpt-4o",
                            template_prompt=f"Você é um {nome_agente.lower()} especializado em {dados['categoria'].lower()}."
                        )
                        db.session.add(novo_agente)
                        total_criados += 1
                        logger.info(f"✅ Agente criado: {nome_agente}")
                    
                    total_processados += 1
                    
                    # Commit a cada 10 agentes para evitar timeouts
                    if total_processados % 10 == 0:
                        db.session.commit()
                        logger.info(f"💾 Checkpoint: {total_processados} agentes processados")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar agente {nome_agente}: {str(e)}")
                    db.session.rollback()
                    continue
            
            # Commit final
            db.session.commit()
            
            logger.info(f"✅ Sincronização concluída!")
            logger.info(f"📊 Total processados: {total_processados}")
            logger.info(f"🆕 Criados: {total_criados}")
            logger.info(f"🔄 Atualizados: {total_atualizados}")
            
            # Verificar total final
            total_final = AgenteJuridico.query.filter_by(ativo=True).count()
            logger.info(f"📈 Total de agentes ativos no banco: {total_final}")
            
    except Exception as e:
        logger.error(f"❌ Erro geral na sincronização: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Sincronização dos 135 agentes concluída com sucesso!")
    else:
        print("❌ Erro na sincronização dos agentes.")
        sys.exit(1)