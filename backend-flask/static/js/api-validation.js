/**
 * Script para validação de chaves de API no painel administrativo
 */

// Definição dos formatos esperados para cada provedor
// Usando IIFE (Immediately Invoked Function Expression) para evitar poluição do escopo global
var API_KEY_FORMATS = (window.API_KEY_FORMATS || {
    'openai': {
        prefix: 'sk-',
        minLength: 30,
        message: 'As chaves da OpenAI geralmente começam com "sk-" e têm pelo menos 30 caracteres.'
    },
    'anthropic': {
        prefix: 'sk-ant-',
        minLength: 30,
        message: 'As chaves da Anthropic geralmente começam com "sk-ant-" e têm pelo menos 30 caracteres.'
    },
    'google': {
        prefix: 'AIza',
        minLength: 20,
        message: 'As chaves da Google geralmente começam com "AIza" e têm pelo menos 20 caracteres.'
    },
    'perplexity': {
        prefix: 'pplx-',
        minLength: 25,
        message: 'As chaves da Perplexity geralmente começam com "pplx-" e têm pelo menos 25 caracteres.'
    },
    'deepseek': {
        prefix: 'sk-',
        minLength: 30,
        message: 'As chaves da Deepseek geralmente começam com "sk-" e têm pelo menos 30 caracteres.'
    }
};

/**
 * Valida o formato de uma chave de API
 * @param {string} provider - O nome do provedor (openai, anthropic, etc.)
 * @param {string} key - A chave de API a ser validada
 * @returns {Object} - Objeto com o resultado da validação
 */
function validateApiKeyFormat(provider, key) {
    // Se o usuário não inseriu uma nova chave (manteve a máscara ou em branco)
    if (key === '************' || key.trim() === '') {
        return {
            valid: false,
            message: 'Por favor, insira uma chave de API válida.',
            isMasked: (key === '************')
        };
    }
    
    // Se não temos regras de validação para este provedor
    if (!API_KEY_FORMATS[provider]) {
        return { valid: true, message: 'Formato não verificado para este provedor.' };
    }
    
    const format = API_KEY_FORMATS[provider];
    const isValid = key.startsWith(format.prefix) && key.length >= format.minLength;
    
    return {
        valid: isValid,
        message: isValid ? 'Formato válido.' : format.message,
        hasCorrectPrefix: key.startsWith(format.prefix),
        hasCorrectLength: key.length >= format.minLength
    };
}

/**
 * Adiciona validação em tempo real para campos de chave de API
 */
function setupApiKeyValidation() {
    document.querySelectorAll('[id$="_api_key"]').forEach(input => {
        const provider = input.id.replace('_api_key', '');
        
        // Criar elemento de feedback se não existir
        let feedbackElement = document.getElementById(`${provider}_key_feedback`);
        if (!feedbackElement) {
            feedbackElement = document.createElement('div');
            feedbackElement.id = `${provider}_key_feedback`;
            feedbackElement.className = 'form-text mt-1 d-none';
            input.parentNode.insertBefore(feedbackElement, input.nextSibling);
        }
        
        // Evento de validação durante digitação
        input.addEventListener('input', function() {
            const key = this.value;
            
            // Não validar se for a versão mascarada
            if (key === '************') {
                feedbackElement.className = 'form-text mt-1 d-none';
                return;
            }
            
            const result = validateApiKeyFormat(provider, key);
            
            if (result.valid) {
                feedbackElement.className = 'form-text text-success mt-1';
                feedbackElement.innerHTML = '<i class="fas fa-check-circle me-1"></i>' + result.message;
            } else {
                feedbackElement.className = 'form-text text-warning mt-1';
                feedbackElement.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>' + result.message;
            }
        });
        
        // Validação ao tentar testar a chave
        const testButton = document.querySelector(`.test-api[data-provider="${provider}"]`);
        if (testButton) {
            testButton.addEventListener('click', function(e) {
                const key = input.value;
                const result = validateApiKeyFormat(provider, key);
                
                // Se for a versão mascarada, pedir ao usuário que insira a chave completa
                if (result.isMasked) {
                    e.preventDefault();
                    alert('Por favor, insira a chave de API completa antes de testar.');
                    return false;
                }
                
                // Se o formato não for válido, pedir confirmação
                if (!result.valid) {
                    if (!confirm(`Aviso: ${result.message}\n\nDeseja continuar mesmo assim?`)) {
                        e.preventDefault();
                        return false;
                    }
                }
            }, true);
        }
    });
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    setupApiKeyValidation();
});