// Interfaces para o sistema de Templates baseadas na estrutura original

import type { AssistenteConfig, AssistenteTipo } from './assistente'

/**
 * Interface completa de um template
 * Baseada em agentes_preconfigurados.json e resseguro.json
 */
export interface Template {
    id: string
    nome: string
    tipo: AssistenteTipo
    categoria: string
    area_juridica: string
    descricao: string
    prompt_template: string
    campos_variaveis: string[]
    customizado: boolean
    configuracoes: AssistenteConfig
    created_at?: string
    updated_at?: string
    created_by?: string
}

/**
 * Formulário de criação/edição de template
 */
export interface TemplateForm {
    nome: string
    tipo: AssistenteTipo
    categoria: string
    area_juridica: string
    descricao: string
    prompt_template: string
    campos_variaveis: string[]
    configuracoes: AssistenteConfig
}

/**
 * Categoria de template
 */
export interface TemplateCategoria {
    id: number
    nome: string
    descricao: string
    parent_id: number | null
    total_templates: number
}

/**
 * Categorias padrão de templates
 */
export const TEMPLATE_CATEGORIAS = [
    'peticoes',
    'contratos',
    'pareceres',
    'recursos',
    'outros'
] as const

/**
 * Tipos de assistentes/templates disponíveis
 */
export const ASSISTENTE_TIPOS: Record<AssistenteTipo, { label: string; icon: string }> = {
    juridico: { label: 'Jurídico', icon: 'gavel' },
    resumidor: { label: 'Resumidor', icon: 'file-text' },
    sentimento: { label: 'Análise de Sentimento', icon: 'heart' },
    extrator: { label: 'Extrator', icon: 'database' },
    tradutor: { label: 'Tradutor', icon: 'languages' },
    classificador: { label: 'Classificador', icon: 'tag' },
    gerador: { label: 'Gerador', icon: 'sparkles' },
    sintetizador: { label: 'Sintetizador', icon: 'layers' },
    formatador: { label: 'Formatador', icon: 'align-left' }
}
