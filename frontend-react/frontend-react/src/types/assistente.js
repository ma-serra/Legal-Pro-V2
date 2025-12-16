// Interfaces principais do sistema de Assistentes baseadas na estrutura original
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
};
/**
 * Configurações default para novos assistentes
 */
export const DEFAULT_ASSISTENTE_CONFIG = {
    llm_provider: 'openai',
    llm_model: 'gpt-4o',
    temperatura: 0.3,
    parametros: {},
    modo_debug: false,
    sempre_executar: true,
    timeout: 120,
    max_tokens: 8000
};
/**
 * Configurações default de chat
 */
export const DEFAULT_CHAT_CONFIG = {
    modelo_llm: 'openai/gpt-4o',
    personalidade: 'advogado',
    tom_voz: 'formal',
    usar_pesquisa_web: false,
    usar_documentos: false
};
