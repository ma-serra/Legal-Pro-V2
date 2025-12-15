/**
 * Tipos TypeScript para Processos Dinâmicos
 * Fase 5 - Frontend React
 */

export interface Processo {
    id_processo: number;
    uuid: string;
    tenant_id?: number;

    // Dados básicos
    numero_cnj?: string;
    pasta: string;
    status_id: number;
    natureza_id: number;

    // Cliente
    cliente_id?: number;
    posicao_cliente_id?: number;

    // Classificação
    acao_id?: number;
    procedimento_id?: number;
    fase_id?: number;

    // Localização
    orgao_id?: number;
    comarca_id?: number;
    vara_turma_id?: number;

    // CNJ
    justica_cnj_id?: number;
    instancia_cnj_id?: number;
    classe_cnj_id?: number;

    // Datas
    data_distribuicao?: string;
    data_criacao: string;
    data_atualizacao: string;

    // Valores
    valor_causa?: number;
    valor_causa_atualizado?: number;
    valor_envolvido?: number;
    valor_envolvido_atualizado?: number;
    contingencia?: number;

    // Prognóstico
    tipo_probabilidade_id?: number;
    risco_id?: number;

    // Metadados
    titulo?: string;
    observacao_pasta?: string;
    ativo: boolean;
}

export interface ProcessoCreate {
    pasta: string;
    natureza_id: number;
    status_id: number;
    tenant_id?: number;
    numero_cnj?: string;
    cliente_id?: number;
    titulo?: string;
    valor_causa?: number;
    data_distribuicao?: string;
    campos_especificos?: Record<string, any>;
    dados_tributario?: DadosTributario;
    dados_trabalhista?: DadosTrabalhista;
    dados_civel?: DadosCivel;
}

export interface DadosTributario {
    tributo_id?: number;
    numero_aiim?: string;
    numero_cda?: string;
    valor_principal?: number;
    valor_multa?: number;
    valor_juros?: number;
    indice_juros?: string;
}

export interface DadosTrabalhista {
    tolerancia_acordo?: number;
    acordo_realizado?: number;
    data_acordo?: string;
    observacoes_acordo?: string;
}

export interface DadosCivel {
    tolerancia_acordo?: number;
    acordo_realizado?: number;
    data_acordo?: string;
    observacoes_acordo?: string;
}

export interface Tributo {
    id_tributo: number;
    codigo: string;
    nome: string;
    descricao?: string;
    esfera?: string;
    ativo: boolean;
}

export interface TeseTributaria {
    id_tese: number;
    codigo: string;
    titulo: string;
    descricao?: string;
    tributo_id?: number;
    tema_repercussao_geral?: string;
    tema_repetitivo?: string;
    tribunal_origem?: string;
    probabilidade_sucesso?: number;
    fundamentacao?: string;
    situacao: string;
    ativo: boolean;
}

export interface PrognosticoTributario {
    provavel: {
        tese?: TeseTributaria;
        valor?: number;
        percentual: number;
    };
    possivel: {
        tese?: TeseTributaria;
        valor?: number;
        percentual: number;
    };
    remoto: {
        tese?: TeseTributaria;
        valor?: number;
        percentual: number;
    };
    observacoes?: string;
    data_avaliacao?: string;
    avaliado_por?: string;
}

export interface IndiceMonetario {
    id_indice: number;
    nome: string;
    descricao?: string;
    fonte_oficial?: string;
    ativo: boolean;
    total_registros?: number;
    ultima_atualizacao?: string;
    ultimo_valor?: number;
}

export interface HistoricoIndice {
    data_referencia: string;
    valor: number;
}

export interface FiltroPesquisa {
    numero_cnj?: string;
    pasta?: string;
    natureza_id?: number;
    status_id?: number;
    cliente_id?: number;
    data_inicio?: string;
    data_fim?: string;
    busca?: string;
    page?: number;
    per_page?: number;
    ordenacao?: string;
    ordem?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    paginas: number;
    pagina_atual: number;
    por_pagina: number;
}

export interface ApiResponse<T> {
    data?: T;
    error?: string;
    details?: any;
}
