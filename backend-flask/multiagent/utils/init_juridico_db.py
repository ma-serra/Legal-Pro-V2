"""
Módulo para inicialização dos dados de agentes jurídicos no banco de dados.
"""
import json
import logging
import importlib
from typing import Dict, List, Any, Optional, Type
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

def carregar_classes_juridicas() -> List[Type]:
    """
    Carrega dinamicamente as classes de agentes jurídicos.
    
    Returns:
        List[Type]: Lista com as classes de agentes jurídicos
    """
    # Inicializa a lista de classes
    classes = []
    
    # Cria uma classe base para os agentes jurídicos
    from multiagent.agents.base_juridico import BaseJuridicoAgent
    
    # Importa a implementação própria do agente de Tribunal do Júri
    from multiagent.agents.tribunal_juri import EspecialistaTribunalJuriAgent
    
    # Importa a implementação própria do agente de Direito Criminal
    from multiagent.agents.direito_criminal import EspecialistaDireitoCriminalAgent
    
    class AnalistaEvidenciasCriminaisAgent(BaseJuridicoAgent):
        """Agente especializado em análise de evidências criminais"""
        def _processar(self, data):
            from multiagent.agents.juridicos import EspecialistaDireitoBancarioAgent
            # Reutiliza a lógica do especialista em direito bancário com ajustes
            # No futuro, implementar uma lógica específica para análise de evidências
            agent = EspecialistaDireitoBancarioAgent(self.config)
            result = agent._processar(data)
            if "tipo_documento" in result:
                result["tipo_documento"] = "evidencias_criminais"
            return result
    
    # Importa os novos agentes especializados
    try:
        from multiagent.agents.gestor_compliance_bancario import GestorComplianceBancarioAgent
        from multiagent.agents.gestor_contencioso_bancario import GestorContenciosoBancarioAgent
        from multiagent.agents.gestor_sinistros_securitario import GestorSinistrosSecuritarioAgent
        from multiagent.agents.gestor_compliance_susep import GestorComplianceSusepAgent
        from multiagent.agents.gestor_contencioso_securitario import GestorContenciosoSecuritarioAgent
        
        # Adiciona as classes à lista
        classes.extend([
            EspecialistaTribunalJuriAgent,
            EspecialistaDireitoCriminalAgent,
            AnalistaEvidenciasCriminaisAgent,
            GestorComplianceBancarioAgent,
            GestorContenciosoBancarioAgent,
            GestorSinistrosSecuritarioAgent,
            GestorComplianceSusepAgent,
            GestorContenciosoSecuritarioAgent
        ])
    except ImportError as e:
        logger.warning(f"Erro ao importar agentes especializados: {e}")
        # Adiciona apenas as classes básicas se não conseguir importar os novos agentes
        classes.extend([
            EspecialistaTribunalJuriAgent,
            EspecialistaDireitoCriminalAgent,
            AnalistaEvidenciasCriminaisAgent
        ])
    
    return classes

def initialize() -> None:
    """
    Inicializa os dados de agentes jurídicos no banco de dados.
    Cria as categorias e agentes jurídicos se ainda não existirem.
    """
    from main import db
    from models import CategoriaJuridica, AgenteJuridico
    
    logger.info("Inicializando dados de agentes jurídicos...")
    
    # Primeiro, inicializa as categorias jurídicas
    categorias = inicializar_categorias_juridicas(db, CategoriaJuridica)
    
    # Depois, inicializa os agentes jurídicos
    inicializar_agentes_juridicos(db, AgenteJuridico, categorias)
    
    # Por último, inicializa os agentes revisores
    inicializar_agentes_revisores(db, AgenteJuridico, categorias)
    
    logger.info("Inicialização de dados jurídicos concluída com sucesso")

def inicializar_categorias_juridicas(db, CategoriaJuridica) -> Dict[str, int]:
    """
    Inicializa as categorias jurídicas no banco de dados.
    
    Args:
        db: Instância do SQLAlchemy
        CategoriaJuridica: Modelo de categoria jurídica
        
    Returns:
        Dict[str, int]: Dicionário com os IDs das categorias criadas (chave: código, valor: id)
    """
    categorias_data = [
        {
            "nome": "Direito Bancário",
            "descricao": "Análise de contratos bancários, financiamentos, investimentos e questões regulatórias bancárias.",
            "icone": "fas fa-university",
            "cor": "#3498db",
            "codigo": "bancario"
        },
        {
            "nome": "Direito Securitário",
            "descricao": "Análise de contratos de seguro, resseguro e questões regulatórias de seguros.",
            "icone": "fas fa-shield-alt",
            "cor": "#2ecc71",
            "codigo": "securitario"
        },
        {
            "nome": "Direito Trabalhista",
            "descricao": "Análise de contratos de trabalho, acordos coletivos e questões relacionadas a relações de trabalho.",
            "icone": "fas fa-briefcase",
            "cor": "#e74c3c",
            "codigo": "trabalhista"
        },
        {
            "nome": "Direito Previdenciário",
            "descricao": "Análise de questões relacionadas à previdência social e benefícios previdenciários.",
            "icone": "fas fa-hand-holding-usd",
            "cor": "#9b59b6",
            "codigo": "previdenciario"
        },
        {
            "nome": "Direito Tributário",
            "descricao": "Análise fiscal e tributária, planejamento tributário e contencioso fiscal.",
            "icone": "fas fa-file-invoice-dollar",
            "cor": "#f39c12",
            "codigo": "tributario"
        },
        {
            "nome": "Direito Imobiliário",
            "descricao": "Análise de contratos imobiliários, incorporações, locações e direito registral.",
            "icone": "fas fa-home",
            "cor": "#1abc9c",
            "codigo": "imobiliario"
        },
        {
            "nome": "Direito Digital",
            "descricao": "Análise de contratos digitais, LGPD, direitos autorais e propriedade intelectual.",
            "icone": "fas fa-laptop-code",
            "cor": "#3498db",
            "codigo": "digital"
        },
        {
            "nome": "Direito Empresarial",
            "descricao": "Análise de contratos societários, fusões e aquisições, governança corporativa.",
            "icone": "fas fa-building",
            "cor": "#34495e",
            "codigo": "empresarial"
        },
        {
            "nome": "Análise de Riscos Jurídicos",
            "descricao": "Identificação e avaliação de riscos jurídicos em operações empresariais.",
            "icone": "fas fa-exclamation-triangle",
            "cor": "#e74c3c",
            "codigo": "riscos"
        },
        {
            "nome": "Direito Penal",
            "descricao": "Análise de crimes econômicos, compliance criminal e defesa corporativa.",
            "icone": "fas fa-gavel",
            "cor": "#8e44ad",
            "codigo": "penal"
        },
        {
            "nome": "Direito Ambiental",
            "descricao": "Análise de licenciamento ambiental, responsabilidade ambiental e sustentabilidade.",
            "icone": "fas fa-leaf",
            "cor": "#27ae60",
            "codigo": "ambiental"
        },
        {
            "nome": "Direito do Consumidor",
            "descricao": "Análise de relações de consumo, práticas comerciais e direitos do consumidor.",
            "icone": "fas fa-shopping-cart",
            "cor": "#d35400",
            "codigo": "consumidor"
        },
    ]
    
    categorias_ids = {}
    
    for categoria_data in categorias_data:
        # Verifica se a categoria já existe
        categoria = CategoriaJuridica.query.filter_by(nome=categoria_data["nome"]).first()
        
        if not categoria:
            # Cria a categoria se não existir
            categoria = CategoriaJuridica(
                nome=categoria_data["nome"],
                descricao=categoria_data["descricao"],
                icone=categoria_data["icone"],
                cor=categoria_data["cor"],
                ativa=True
            )
            
            try:
                db.session.add(categoria)
                db.session.commit()
                logger.info(f"Categoria jurídica criada: {categoria.nome}")
            except IntegrityError:
                db.session.rollback()
                logger.warning(f"Categoria já existe: {categoria_data['nome']}")
        
        # Armazena o ID da categoria no dicionário
        categorias_ids[categoria_data["codigo"]] = categoria.id
    
    logger.info("Categorias jurídicas inicializadas com sucesso")
    return categorias_ids

def inicializar_agentes_juridicos(db, AgenteJuridico, categorias_ids: Dict[str, int]) -> None:
    """
    Inicializa os agentes jurídicos no banco de dados.
    
    Args:
        db: Instância do SQLAlchemy
        AgenteJuridico: Modelo de agente jurídico
        categorias_ids: Dicionário com os IDs das categorias (chave: código, valor: id)
    """
    agentes_data = [
        {
            "nome": "Especialista em Direito Bancário",
            "classe": "EspecialistaDireitoBancarioAgent",
            "descricao": "Especializado na análise de contratos bancários, operações financeiras e conformidade regulatória bancária.",
            "categoria_codigo": "bancario",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
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
            }
        },
        {
            "nome": "Especialista em Direito Securitário",
            "classe": "EspecialistaDireitoSecuritarioAgent",
            "descricao": "Especializado na análise de contratos de seguro, resseguro e questões regulatórias do mercado de seguros.",
            "categoria_codigo": "securitario", 
            "nivel_especializacao": 4,
            "modelo_ai": "gpt-4o",
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
            }
        },
        {
            "nome": "Especialista em Direito Trabalhista",
            "classe": "EspecialistaDireitoTrabalhistaAgent",
            "descricao": "Especializado na análise de questões trabalhistas, contratos de trabalho e relações laborais.",
            "categoria_codigo": "trabalhista",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
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
            }
        },
        {
            "nome": "Consultor em Direito Previdenciário",
            "classe": "ConsultorDireitoPrevidenciarioAgent",
            "descricao": "Especializado em análise de benefícios previdenciários, tempo de contribuição e aposentadorias.",
            "categoria_codigo": "previdenciario",
            "nivel_especializacao": 4,
            "modelo_ai": "gpt-4o",
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
            }
        },
        {
            "nome": "Especialista em Direito Tributário",
            "classe": "EspecialistaDireitoTributarioAgent",
            "descricao": "Especializado em análise fiscal, planejamento tributário e contencioso administrativo fiscal.",
            "categoria_codigo": "tributario",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
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
            }
        },
        {
            "nome": "Especialista em Direito Imobiliário",
            "classe": "EspecialistaDireitoImobiliarioAgent",
            "descricao": "Especializado em contratos imobiliários, incorporações, registro de imóveis e locações.",
            "categoria_codigo": "imobiliario",
            "nivel_especializacao": 4,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de contratos de compra e venda",
                    "Verificação de documentação imobiliária",
                    "Assessoria em incorporações",
                    "Análise de contratos de locação",
                    "Orientação sobre regularização fundiária"
                ],
                "fontes_conhecimento": [
                    "Lei de Registros Públicos",
                    "Lei de Locações",
                    "Lei de Incorporações Imobiliárias",
                    "Jurisprudência imobiliária"
                ]
            }
        },
        {
            "nome": "Especialista em Direito Digital",
            "classe": "EspecialistaDireitoDigitalAgent",
            "descricao": "Especializado em análise de contratos digitais, LGPD, direitos autorais e propriedade intelectual.",
            "categoria_codigo": "digital",
            "nivel_especializacao": 4,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de compliance com LGPD",
                    "Avaliação de contratos de software",
                    "Orientação sobre propriedade intelectual",
                    "Verificação de termos de uso",
                    "Análise de riscos em operações digitais"
                ],
                "fontes_conhecimento": [
                    "Lei Geral de Proteção de Dados",
                    "Marco Civil da Internet",
                    "Lei de Direitos Autorais",
                    "Jurisprudência sobre direito digital"
                ]
            }
        },
        {
            "nome": "Especialista em Direito Empresarial",
            "classe": "EspecialistaDireitoEmpresarialAgent",
            "descricao": "Especializado em contratos societários, fusões e aquisições, governança corporativa e compliance.",
            "categoria_codigo": "empresarial",
            "nivel_especializacao": 5,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de contratos societários",
                    "Due diligence jurídica",
                    "Assessoria em operações de M&A",
                    "Verificação de estruturas societárias",
                    "Orientação sobre governança corporativa"
                ],
                "fontes_conhecimento": [
                    "Lei das S.A.",
                    "Código Civil - Direito Empresarial",
                    "Jurisprudência comercial",
                    "Regras da CVM"
                ]
            }
        },
        {
            "nome": "Analista de Riscos Jurídicos",
            "classe": "AnalistaRiscosJuridicosAgent",
            "descricao": "Especializado na identificação, avaliação e mitigação de riscos jurídicos em operações empresariais.",
            "categoria_codigo": "riscos",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Mapeamento de riscos jurídicos",
                    "Análise de impacto regulatório",
                    "Avaliação de contingências",
                    "Elaboração de planos de mitigação",
                    "Monitoramento de riscos legais"
                ],
                "fontes_conhecimento": [
                    "Legislação multidisciplinar",
                    "Precedentes judiciais relevantes",
                    "Normas regulatórias setoriais",
                    "Modelos de análise de risco"
                ]
            }
        },
        {
            "nome": "Especialista em Direito Criminal",
            "classe": "EspecialistaDireitoCriminalAgent",
            "descricao": "Analisa casos criminais, fornecendo análise técnica sobre tipos penais, procedimentos, jurisprudência e estratégias de defesa ou acusação.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de tipos penais e elementos do crime",
                    "Avaliação de procedimentos criminais",
                    "Identificação de estratégias de defesa e acusação",
                    "Análise de provas e evidências",
                    "Avaliação de riscos processuais"
                ],
                "fontes_conhecimento": [
                    "Código Penal",
                    "Código de Processo Penal",
                    "Jurisprudência criminal",
                    "Doutrina especializada"
                ]
            }
        },
        {
            "nome": "Especialista em Tribunal do Júri",
            "classe": "EspecialistaTribunalJuriAgent",
            "descricao": "Analisa casos de competência do Tribunal do Júri, oferecendo estratégias específicas para sustentação oral, argumentação persuasiva, e manejo do corpo de jurados.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Estratégias para argumentação perante jurados",
                    "Técnicas de oratória e persuasão",
                    "Análise de perfil de jurados",
                    "Preparação de testemunhas",
                    "Abordagens para réplica e tréplica"
                ],
                "fontes_conhecimento": [
                    "Código de Processo Penal - Capítulo do Júri",
                    "Jurisprudência específica de Tribunal do Júri",
                    "Técnicas de argumentação persuasiva",
                    "Psicologia do convencimento"
                ]
            }
        },
        {
            "nome": "Analista de Evidências Criminais",
            "classe": "AnalistaEvidenciasCriminaisAgent",
            "descricao": "Especializado na análise técnica de provas e evidências em processos criminais, avaliando laudos periciais, depoimentos e sua admissibilidade processual.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 4,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise técnica de laudos periciais",
                    "Avaliação da admissibilidade de provas",
                    "Identificação de inconsistências em depoimentos",
                    "Análise da cadeia de custódia de evidências",
                    "Sugestão de perícias complementares"
                ],
                "fontes_conhecimento": [
                    "Código de Processo Penal",
                    "Jurisprudência sobre provas",
                    "Princípios de criminalística",
                    "Manuais de técnicas periciais"
                ]
            }
        },
        {
            "nome": "Especialista em Execução Penal",
            "classe": "EspecialistaExecucaoPenalAgent",
            "descricao": "Analisa questões relacionadas à execução da pena, progressão de regime, benefícios, indultos e medidas alternativas.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 4,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Análise de cálculos de pena",
                    "Avaliação de requisitos para progressão de regime",
                    "Identificação de benefícios aplicáveis",
                    "Elaboração de estratégias para livramento condicional",
                    "Análise de incidentes na execução"
                ],
                "fontes_conhecimento": [
                    "Lei de Execução Penal",
                    "Jurisprudência em execução penal",
                    "Súmulas dos tribunais superiores",
                    "Decretos de indulto e comutação"
                ]
            }
        },
        {
            "nome": "Assessor de Sustentação Oral no Júri",
            "classe": "AssessorSustentacaoJuriAgent",
            "descricao": "Auxilia na preparação de sustentações orais para o Tribunal do Júri, com foco em técnicas persuasivas, organização de argumentos e estratégias retóricas.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Estruturação de argumentos persuasivos",
                    "Técnicas de oratória para júri",
                    "Preparação para réplica e tréplica",
                    "Uso estratégico de evidências",
                    "Abordagens psicológicas para convencimento"
                ],
                "fontes_conhecimento": [
                    "Técnicas de retórica forense",
                    "Psicologia do júri",
                    "Estudos de caso de julgamentos célebres",
                    "Manuais de persuasão para advogados criminalistas"
                ]
            }
        }
    ]
    
    for agente_data in agentes_data:
        # Verifica se o agente já existe
        agente = AgenteJuridico.query.filter_by(classe=agente_data["classe"]).first()
        
        if not agente:
            # Converte os detalhes técnicos para JSON
            detalhes_json = json.dumps(agente_data["detalhes_tecnicos"])
            
            # Cria o agente se não existir
            agente = AgenteJuridico(
                nome=agente_data["nome"],
                classe=agente_data["classe"],
                descricao=agente_data["descricao"],
                categoria_id=categorias_ids[agente_data["categoria_codigo"]],
                nivel_especializacao=agente_data["nivel_especializacao"],
                ativo=True,
                modelo_ai=agente_data["modelo_ai"],
                detalhes_tecnicos=detalhes_json
            )
            
            try:
                db.session.add(agente)
                db.session.commit()
                logger.info(f"Agente jurídico criado: {agente.nome}")
            except IntegrityError:
                db.session.rollback()
                logger.warning(f"Agente já existe: {agente_data['nome']}")
    
    logger.info("Agentes jurídicos inicializados com sucesso")

def inicializar_agentes_revisores(db, AgenteJuridico, categorias_ids: Dict[str, int]) -> None:
    """
    Inicializa os agentes revisores jurídicos no banco de dados.
    
    Args:
        db: Instância do SQLAlchemy
        AgenteJuridico: Modelo de agente jurídico
        categorias_ids: Dicionário com os IDs das categorias (chave: código, valor: id)
    """
    # Importamos o Revisor de Direito Penal
    from multiagent.agents.revisor_direito_penal import RevisorDireitoPenalAgent
    
    agentes_revisores_data = [
        {
            "nome": "Revisor de Direito Penal",
            "classe": "RevisorDireitoPenalAgent",
            "descricao": "Especializado em revisar análises de direito penal, crimes, procedimentos criminais e jurisprudência penal, fornecendo uma segunda opinião técnica e fundamentada.",
            "categoria_codigo": "penal",
            "nivel_especializacao": 5,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Revisão crítica de análises penais",
                    "Identificação de pontos controversos em matéria criminal",
                    "Complementação com jurisprudência penal relevante",
                    "Análise técnica de enquadramentos penais",
                    "Avaliação de estratégias processuais penais"
                ],
                "metodologia": [
                    "Análise técnica do texto original",
                    "Identificação de pontos de concordância",
                    "Mapeamento de divergências analíticas na esfera penal",
                    "Complementação com perspectivas adicionais e precedentes criminais",
                    "Avaliação geral de qualidade técnica"
                ]
            }
        },
        {
            "nome": "Revisor de Direito Bancário",
            "classe": "RevisorDireitoBancarioAgent",
            "descricao": "Especializado em revisar análises de contratos bancários e operações financeiras, fornecendo uma segunda opinião.",
            "categoria_codigo": "bancario",
            "nivel_especializacao": 5,
            "modelo_ai": "gpt-4o",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Revisão crítica de análises bancárias",
                    "Identificação de pontos controversos",
                    "Avaliação de riscos não identificados",
                    "Complementação de análises incompletas",
                    "Confirmação de conclusões corretas"
                ],
                "metodologia": [
                    "Análise completa do texto original",
                    "Identificação de pontos de concordância",
                    "Mapeamento de divergências analíticas",
                    "Complementação com perspectivas adicionais",
                    "Avaliação geral de qualidade técnica"
                ]
            }
        },
        {
            "nome": "Revisor de Direito Trabalhista",
            "classe": "RevisorDireitoTrabalhistaAgent",
            "descricao": "Especializado em revisar análises trabalhistas, contratos de trabalho e questões de relações laborais.",
            "categoria_codigo": "trabalhista",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Revisão crítica de análises trabalhistas",
                    "Identificação de vulnerabilidades legais",
                    "Avaliação de riscos não identificados",
                    "Complementação com jurisprudência recente",
                    "Verificação de conformidade com a CLT"
                ],
                "metodologia": [
                    "Análise completa do texto original",
                    "Identificação de pontos de concordância",
                    "Mapeamento de divergências analíticas",
                    "Complementação com perspectivas adicionais",
                    "Avaliação geral de qualidade técnica"
                ]
            }
        },
        {
            "nome": "Revisor de Direito Empresarial",
            "classe": "RevisorDireitoEmpresarialAgent",
            "descricao": "Especializado em revisar análises de contratos societários, operações corporativas e estruturas empresariais.",
            "categoria_codigo": "empresarial",
            "nivel_especializacao": 5,
            "modelo_ai": "claude-3-5-sonnet",
            "detalhes_tecnicos": {
                "capacidades": [
                    "Revisão crítica de análises societárias",
                    "Identificação de vulnerabilidades contratuais",
                    "Avaliação de riscos estratégicos",
                    "Complementação com perspectivas de governança",
                    "Verificação de conformidade regulatória"
                ],
                "metodologia": [
                    "Análise completa do texto original",
                    "Identificação de pontos de concordância",
                    "Mapeamento de divergências analíticas",
                    "Complementação com perspectivas adicionais",
                    "Avaliação geral de qualidade técnica"
                ]
            }
        }
    ]
    
    for agente_data in agentes_revisores_data:
        # Verifica se o agente já existe
        agente = AgenteJuridico.query.filter_by(classe=agente_data["classe"]).first()
        
        if not agente:
            # Converte os detalhes técnicos para JSON
            detalhes_json = json.dumps(agente_data["detalhes_tecnicos"])
            
            # Cria o agente se não existir
            agente = AgenteJuridico(
                nome=agente_data["nome"],
                classe=agente_data["classe"],
                descricao=agente_data["descricao"],
                categoria_id=categorias_ids[agente_data["categoria_codigo"]],
                nivel_especializacao=agente_data["nivel_especializacao"],
                ativo=True,
                modelo_ai=agente_data["modelo_ai"],
                detalhes_tecnicos=detalhes_json
            )
            
            try:
                db.session.add(agente)
                db.session.commit()
                logger.info(f"Agente revisor jurídico criado: {agente.nome}")
            except IntegrityError:
                db.session.rollback()
                logger.warning(f"Agente revisor já existe: {agente_data['nome']}")
    
    logger.info("Agentes revisores jurídicos inicializados com sucesso")