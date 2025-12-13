"""
Sistema de Assistentes Jurídicos Especializados
Integração com pgvector e APIs de IA (OpenAI, Anthropic, Gemini, DeepSeek)
"""

# Configuração das áreas jurídicas
AREAS_JURIDICAS = {
    'direito_agrario': {
        'nome': 'Direito Agrário',
        'icone': 'fas fa-tractor',
        'cor': '#2D5A27',
        'descricao': 'Reforma agrária, propriedade rural e contratos agrários'
    },
    'direito_bancario': {
        'nome': 'Direito Bancário',
        'icone': 'fas fa-university',
        'cor': '#8B4513',
        'descricao': 'Consultivo e contencioso bancário, regulatório'
    },
    'direito_empresarial': {
        'nome': 'Direito Empresarial',
        'icone': 'fas fa-building',
        'cor': '#1E3A8A',
        'descricao': 'Contratos empresariais, cessão de crédito, sociedades'
    },
    'direito_consumidor': {
        'nome': 'Direito do Consumidor',
        'icone': 'fas fa-shield-alt',
        'cor': '#4A1E4C',
        'descricao': 'Proteção consumidor, relações consumo'
    },
    'direito_penal': {
        'nome': 'Direito Penal',
        'icone': 'fas fa-handcuffs',
        'cor': '#7F1D1D',
        'descricao': 'Crimes, processo penal e defesa criminal'
    },
    'direito_trabalhista': {
        'nome': 'Direito Trabalhista',
        'icone': 'fas fa-hard-hat',
        'cor': '#92400E',
        'descricao': 'Relações trabalhistas, processos CLT'
    },
    'recuperacao_credito': {
        'nome': 'Recuperação de Crédito',
        'icone': 'fas fa-search-dollar',
        'cor': '#064E3B',
        'descricao': 'Localização devedores, acordos, execuções'
    },
    'direito_digital': {
        'nome': 'Direito Digital',
        'icone': 'fas fa-globe',
        'cor': '#6366f1',
        'descricao': 'LGPD, proteção de dados e crimes cibernéticos'
    },
    'direito_previdenciario': {
        'nome': 'Direito Previdenciário',
        'icone': 'fas fa-user-clock',
        'cor': '#8b5cf6',
        'descricao': 'Benefícios INSS, aposentadorias e pensões'
    },
    'direito_tributario': {
        'nome': 'Direito Tributário',
        'icone': 'fas fa-receipt',
        'cor': '#f59e0b',
        'descricao': 'Impostos, tributos e planejamento fiscal'
    },
    'direito_imobiliario': {
        'nome': 'Direito Imobiliário',
        'icone': 'fas fa-home',
        'cor': '#10b981',
        'descricao': 'Compra e venda, locações e regularização imobiliária'
    },
    'direito_securitario': {
        'nome': 'Direito Securitário',
        'icone': 'fas fa-shield-alt',
        'cor': '#3b82f6',
        'descricao': 'Contratos de seguro, sinistros e SUSEP'
    },
    'negociacao_conflitos': {
        'nome': 'Negociação e Conflitos',
        'icone': 'fas fa-handshake',
        'cor': '#06b6d4',
        'descricao': 'Mediação, conciliação e resolução de conflitos'
    },
    'direito_ambiental': {
        'nome': 'Direito Ambiental',
        'icone': 'fas fa-leaf',
        'cor': '#059669',
        'descricao': 'Licenciamento ambiental, crimes ambientais e sustentabilidade'
    },

    'analise_riscos': {
        'nome': 'Análise de Riscos Jurídicos',
        'icone': 'fas fa-chart-line',
        'cor': '#dc2626',
        'descricao': 'Avaliação de riscos legais e compliance empresarial'
    }
}

# Estilos de personalização dos assistentes
ESTILOS_ASSISTENTE = {
    'juridico_tecnico': {
        'nome': 'Jurídico Técnico',
        'descricao': 'Linguagem formal e precisa, citações jurídicas'
    },
    'informal': {
        'nome': 'Informal',
        'descricao': 'Linguagem acessível e didática'
    },
    'estrategico': {
        'nome': 'Estratégico',
        'descricao': 'Foco em soluções práticas e táticas'
    },
    'pedagogico': {
        'nome': 'Pedagógico',
        'descricao': 'Ensina conceitos jurídicos de forma clara'
    }
}