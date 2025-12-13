# Inicialização do módulo agents
from multiagent.agents.extrator import ExtratorAgent
from multiagent.agents.classificador import ClassificadorAgent
from multiagent.agents.analisador import AnalisadorAgent
from multiagent.agents.sintetizador import SintetizadorAgent
from multiagent.agents.formatador import FormatadorAgent
from multiagent.agents.resumidor import ResumidorAgent
from multiagent.agents.sentimento import SentimentoAgent
from multiagent.agents.tradutor import TradutorAgent
from multiagent.agents.gerador_imagens import GeradorImagensAgent

# Importa agentes jurídicos especializados
from multiagent.agents.juridicos import (
    EspecialistaDireitoTrabalhistaAgent,
    ConsultorDireitoPrevidenciarioAgent,
    AnalistaRiscosJuridicosAgent,
    AGENTES_JURIDICOS
)

# Importa agentes revisores para segunda opinião
from multiagent.agents.revisores import (
    RevisorDireitoBancarioAgent,
    RevisorDireitoTrabalhistaAgent,
    RevisorDireitoEmpresarialAgent
)

# Mapeamento de tipos de agentes para suas classes
AGENT_TYPES = {
    # Agentes padrão
    'extrator': ExtratorAgent,
    'classificador': ClassificadorAgent,
    'analisador': AnalisadorAgent,
    'sintetizador': SintetizadorAgent,
    'formatador': FormatadorAgent,
    'resumidor': ResumidorAgent,
    'sentimento': SentimentoAgent,
    'tradutor': TradutorAgent,
    'gerador_imagens': GeradorImagensAgent,
    
    # Agentes jurídicos especializados principais
    'especialista_direito_trabalhista': EspecialistaDireitoTrabalhistaAgent,
    'especialista_direito_empresarial': RevisorDireitoEmpresarialAgent,
    'especialista_direito_bancario': RevisorDireitoBancarioAgent,
    'especialista_direito_criminal': "EspecialistaDireitoCriminalAgent",
    'especialista_direito_digital': RevisorDireitoEmpresarialAgent,
    'especialista_direito_imobiliario': RevisorDireitoEmpresarialAgent,
    'especialista_direito_securitario': RevisorDireitoEmpresarialAgent,
    'especialista_direito_tributario': RevisorDireitoEmpresarialAgent,
    'especialista_direito_consumidor': RevisorDireitoEmpresarialAgent,
    'especialista_direito_previdenciario': ConsultorDireitoPrevidenciarioAgent,
    'especialista_direito_agrario': RevisorDireitoEmpresarialAgent,
    'especialista_negociacao_conflitos': RevisorDireitoEmpresarialAgent,
    'especialista_recuperacao_credito': RevisorDireitoEmpresarialAgent,
    
    # Agentes criminais específicos
    'especialista_juri_criminal': "EspecialistaTribunalJuriAgent",
    'especialista_tribunal_juri': "EspecialistaTribunalJuriAgent",
    'analista_evidencias_criminais': "AnalistaEvidenciasCriminaisAgent",
    'especialista_execucao_penal': "EspecialistaDireitoCriminalAgent",
    'especialista_defesa_criminal': "EspecialistaDireitoCriminalAgent",
    'especialista_crimes_transito': "EspecialistaDireitoCriminalAgent",
    'especialista_crimes_drogas': "EspecialistaDireitoCriminalAgent",
    'especialista_violencia_domestica': "EspecialistaDireitoCriminalAgent",
    'assessor_sustentacao_juri': "EspecialistaTribunalJuriAgent",
    'revisor_direito_penal': "EspecialistaDireitoCriminalAgent",
    
    # Consultores especializados
    'consultor_direito_previdenciario': ConsultorDireitoPrevidenciarioAgent,
    'consultor_mercado_capitais': RevisorDireitoBancarioAgent,
    'consultor_prevencao_lavagem_dinheiro': RevisorDireitoBancarioAgent,
    'consultor_previdencia_complementar': ConsultorDireitoPrevidenciarioAgent,
    'consultor_recuperacao_judicial': RevisorDireitoEmpresarialAgent,
    'consultor_seguros_corporativos': RevisorDireitoEmpresarialAgent,
    'consultor_conflitos_agrarios': RevisorDireitoEmpresarialAgent,
    'consultor_credito_rural': RevisorDireitoEmpresarialAgent,
    'consultor_condominios_convencoes': RevisorDireitoEmpresarialAgent,
    
    # Analistas especializados
    'analista_riscos_juridicos': AnalistaRiscosJuridicosAgent,
    'analista_assedio_discriminacao': EspecialistaDireitoTrabalhistaAgent,
    'analista_beneficios_fiscais': RevisorDireitoEmpresarialAgent,
    'analista_beneficios_incapacidade': ConsultorDireitoPrevidenciarioAgent,
    'analista_fraudes_sinistros': RevisorDireitoEmpresarialAgent,
    'analista_revisao_contratual_bancaria': RevisorDireitoBancarioAgent,
    'analista_score_recuperacao': RevisorDireitoEmpresarialAgent,
    
    # Agentes revisores (segunda opinião)
    'revisor_direito_bancario': RevisorDireitoBancarioAgent,
    'revisor_direito_trabalhista': RevisorDireitoTrabalhistaAgent,
    'revisor_direito_empresarial': RevisorDireitoEmpresarialAgent,
    
    # Gestores especializados
    'gestor_compliance_bancario': 'GestorComplianceBancarioAgent',
    'gestor_contencioso_bancario': 'GestorContenciosoBancarioAgent',
    'gestor_sinistros_securitarios': 'GestorSinistrosSecuritarioAgent',
    'gestor_compliance_susep': 'GestorComplianceSusepAgent',
    'gestor_contencioso_securitario': 'GestorContenciosoSecuritarioAgent',
    'gestor_carteira_inadimplente': RevisorDireitoEmpresarialAgent,
    'gestor_indicadores_recuperacao': RevisorDireitoEmpresarialAgent,
    
    # Especialistas em áreas específicas
    'especialista_aposentadoria_rural': ConsultorDireitoPrevidenciarioAgent,
    'especialista_atividades_especiais': ConsultorDireitoPrevidenciarioAgent,
    'especialista_cobranca_internacional': RevisorDireitoEmpresarialAgent,
    'especialista_contratos_comerciais': RevisorDireitoEmpresarialAgent,
    'especialista_contratos_eletronicos': RevisorDireitoEmpresarialAgent,
    'especialista_contratos_rurais': RevisorDireitoEmpresarialAgent,
    'especialista_contratos_seguro_agricola': RevisorDireitoEmpresarialAgent,
    'especialista_crimes_ciberneticos': RevisorDireitoEmpresarialAgent,
    'especialista_estruturacao_societaria': RevisorDireitoEmpresarialAgent,
    'especialista_fiscalizacao_trabalhista': EspecialistaDireitoTrabalhistaAgent,
    'especialista_incorporacao_registro': RevisorDireitoEmpresarialAgent,
    'especialista_locacoes_comerciais': RevisorDireitoEmpresarialAgent,
    'especialista_planejamento_previdenciario': ConsultorDireitoPrevidenciarioAgent,
    'especialista_produtos_financeiros': RevisorDireitoBancarioAgent,
    'especialista_publicidade_enganosa': RevisorDireitoEmpresarialAgent,
    'especialista_recuperacao_credito': RevisorDireitoEmpresarialAgent,
    'especialista_seguros_rurais': RevisorDireitoEmpresarialAgent,
    'especialista_startups_vc': RevisorDireitoEmpresarialAgent,
    'especialista_teses_tributarias': RevisorDireitoEmpresarialAgent,
    'especialista_tributacao_municipal': RevisorDireitoEmpresarialAgent,
    'especialista_tributacao_economia_digital': RevisorDireitoEmpresarialAgent,
    
    # Auditores
    'auditor_conformidade_imobiliaria': RevisorDireitoEmpresarialAgent,
    'auditor_conformidade_sindical': EspecialistaDireitoTrabalhistaAgent,
    'auditor_contribuicoes_previdenciarias': ConsultorDireitoPrevidenciarioAgent,
    'auditor_passivos_ambientais': RevisorDireitoEmpresarialAgent,
    'auditor_planejamento_tributario': RevisorDireitoEmpresarialAgent,
    'auditor_politicas_credito': RevisorDireitoEmpresarialAgent,
    'auditor_protecao_dados': RevisorDireitoEmpresarialAgent,
    'auditor_praticas_comerciais': RevisorDireitoEmpresarialAgent,
    
    # Peritos
    'perito_contratos_compra_venda': RevisorDireitoEmpresarialAgent,
    'perito_provas_digitais': RevisorDireitoEmpresarialAgent,
    'perito_regulacao_seguros': RevisorDireitoEmpresarialAgent,
    'perito_revisao_aposentadorias': ConsultorDireitoPrevidenciarioAgent,
    
    # Agentes de compliance e governança
    'agente_compliance_governanca': RevisorDireitoEmpresarialAgent,
    'agente_governanca_digital': RevisorDireitoEmpresarialAgent,
    'agente_inteligencia_artificial': RevisorDireitoEmpresarialAgent,
    'agente_politicas_inclusao': EspecialistaDireitoTrabalhistaAgent,
    
    # Agentes de fiscalização e monitoramento
    'agente_fiscalizacao': RevisorDireitoEmpresarialAgent,
    'agente_monitoramento_reputacao': RevisorDireitoEmpresarialAgent,
    
    # Facilitadores e negociadores
    'facilitador_disputas_empresariais': RevisorDireitoEmpresarialAgent,
    'negociador_conflitos_tecnologia': RevisorDireitoEmpresarialAgent,
    'especialista_negociacao_internacional': RevisorDireitoEmpresarialAgent,
    'especialista_negociacao_sindical': EspecialistaDireitoTrabalhistaAgent,
}

def get_agent_by_type(agent_type, config=None):
    """
    Obtém uma instância de agente com base no tipo.
    
    Args:
        agent_type: O tipo de agente desejado
        config: Configuração opcional para o agente
        
    Returns:
        Instância de agente do tipo solicitado
    
    Raises:
        ValueError: Se o tipo de agente não for reconhecido
    """
    agent_class = AGENT_TYPES.get(agent_type.lower())
    
    if not agent_class:
        # Tenta buscar pelo nome da classe
        for cls_name, cls in AGENT_TYPES.items():
            if isinstance(cls, str):
                continue  # Pula strings, elas são tratadas abaixo
            if agent_type.lower() in cls.__name__.lower():
                agent_class = cls
                break
    
    if not agent_class:
        raise ValueError(f"Tipo de agente não reconhecido: {agent_type}")
    
    # Se o agente_class for uma string (nome da classe), busca a classe real
    if isinstance(agent_class, str):
        # Importar dinamicamente
        from multiagent.utils.init_juridico_db import carregar_classes_juridicas
        
        classes_juridicas = carregar_classes_juridicas()
        for cls in classes_juridicas:
            if cls.__name__ == agent_class:
                agent_class = cls
                break
        
        if isinstance(agent_class, str):
            raise ValueError(f"Não foi possível carregar a classe {agent_class}")
        
    return agent_class(config or {})
