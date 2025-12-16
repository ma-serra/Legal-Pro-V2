// Interfaces para o sistema de Templates baseadas na estrutura original
/**
 * Categorias padrão de templates
 */
export const TEMPLATE_CATEGORIAS = [
    'peticoes',
    'contratos',
    'pareceres',
    'recursos',
    'outros'
];
/**
 * Tipos de assistentes/templates disponíveis
 */
export const ASSISTENTE_TIPOS = {
    juridico: { label: 'Jurídico', icon: 'gavel' },
    resumidor: { label: 'Resumidor', icon: 'file-text' },
    sentimento: { label: 'Análise de Sentimento', icon: 'heart' },
    extrator: { label: 'Extrator', icon: 'database' },
    tradutor: { label: 'Tradutor', icon: 'languages' },
    classificador: { label: 'Classificador', icon: 'tag' },
    gerador: { label: 'Gerador', icon: 'sparkles' },
    sintetizador: { label: 'Sintetizador', icon: 'layers' },
    formatador: { label: 'Formatador', icon: 'align-left' }
};
