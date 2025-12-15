// Interfaces principais do sistema de Assistentes baseadas na estrutura original

/**
 * Configurações de LLM para assistentes e templates
 */
export interface AssistenteConfig {
    llm_provider: 'openai' | 'anthropic' | 'google'
    llm_model: string
    temperatura: number
    parametros: Record<string, any>
    modo_debug: boolean
    sempre_executar: boolean
    timeout: number
    max_tokens: number
}

/**
 * Tipos de assistentes disponíveis no sistema
 */
export type AssistenteTipo =
    | 'juridico'
    | 'resumidor'
    | 'sentimento'
    | 'extrator'
    | 'tradutor'
    | 'classificador'
    | 'gerador'
    | 'sintetizador'
    | 'formatador'

/**
 * Interface completa de um assistente
 * Baseada em agentes_preconfigurados.json
 */
export interface Assistente {
    id: string
    nome: string
    tipo: AssistenteTipo
    descricao: string
    prompt_template: string
    configuracoes: AssistenteConfig
    area_juridica?: string
    customizado?: boolean
    created_at?: string
    updated_at?: string
}

/**
 * Configurações de chat do assistente
 */
export interface ChatConfig {
    modelo_llm: string
    personalidade: 'advogado' | 'juiz' | 'promotor'
    tom_voz: 'formal' | 'natural' | 'simples'
    usar_pesquisa_web: boolean
    usar_documentos: boolean
}

/**
 * Mensagem de chat
 */
export interface ChatMessage {
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: Date
    config_usada?: ChatConfig
}

/**
 * Conversa/Histórico
 */
export interface Conversa {
    id: string
    assistente_id: string
    titulo: string
    mensagens: ChatMessage[]
    created_at: Date
    updated_at: Date
}

/**
 * Modelos LLM disponíveis por provider
 */
export const LLM_MODELS = {
    openai: [
        { value: 'gpt-4o', label: 'GPT-4o' },
        { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
        { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' }
    ],
    anthropic: [
        { value: 'claude-3-opus', label: 'Claude 3 Opus' },
        { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet' },
        { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' }
    ],
    google: [
        { value: 'gemini-pro', label: 'Gemini Pro' },
        { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' }
    ]
} as const

/**
 * Configurações default para novos assistentes
 */
export const DEFAULT_ASSISTENTE_CONFIG: AssistenteConfig = {
    llm_provider: 'openai',
    llm_model: 'gpt-4o',
    temperatura: 0.3,
    parametros: {},
    modo_debug: false,
    sempre_executar: true,
    timeout: 120,
    max_tokens: 8000
}

/**
 * Configurações default de chat
 */
export const DEFAULT_CHAT_CONFIG: ChatConfig = {
    modelo_llm: 'openai/gpt-4o',
    personalidade: 'advogado',
    tom_voz: 'formal',
    usar_pesquisa_web: false,
    usar_documentos: false
}
