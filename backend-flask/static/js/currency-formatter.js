/**
 * Utilitário universal para formatação monetária no frontend
 * Padrão brasileiro com símbolo R$ e separadores corretos
 * OTIMIZADO: Lazy loading e performance melhorada
 * 
 * @fileoverview Sistema universal de formatação monetária JavaScript
 * @version 1.2.0 - Corrigido (sem duplicações)
 */

// Constantes para uso em toda aplicação
if (typeof window.CURRENCY_CONSTANTS === 'undefined') {
    window.CURRENCY_CONSTANTS = {
        SYMBOL: 'R$',
        DECIMAL_PLACES: 2,
        THOUSANDS_SEPARATOR: '.',
        DECIMAL_SEPARATOR: ',',
        PATTERN: /^R?\$?\s?(\d{1,3}(\.\d{3})*),(\d{2})$/
    };
}

// Verificar se a classe já foi declarada para evitar erro de redeclaração
if (typeof window.CurrencyFormatter === 'undefined') {
    class CurrencyFormatter {
    
    /**
     * Formatar valor para moeda brasileira
     * @param {number|string|null} value - Valor a ser formatado
     * @param {boolean} includeSymbol - Se deve incluir o símbolo R$ (padrão: true)
     * @param {number} decimalPlaces - Número de casas decimais (padrão: 2)
     * @returns {string} Valor formatado no padrão brasileiro
     */
    static formatCurrency(value, includeSymbol = true, decimalPlaces = 2) {
        // Tratar valores null, undefined ou vazios
        if (value === null || value === undefined || value === '') {
            return includeSymbol ? 'R$ 0,00' : '0,00';
        }

        try {
            let numericValue;

            // Converter string para número se necessário
            if (typeof value === 'string') {
                // Remove caracteres não numéricos exceto ponto e vírgula
                let cleanValue = value.replace(/[R$\s]/g, '');
                
                // Lidar com formato brasileiro (1.234,56)
                if (cleanValue.includes(',') && cleanValue.includes('.')) {
                    const parts = cleanValue.split(',');
                    if (parts.length === 2) {
                        const integerPart = parts[0].replace(/\./g, '');
                        const decimalPart = parts[1];
                        cleanValue = `${integerPart}.${decimalPart}`;
                    }
                } else if (cleanValue.includes(',')) {
                    // Apenas vírgula, substituir por ponto
                    cleanValue = cleanValue.replace(',', '.');
                }

                numericValue = parseFloat(cleanValue);
            } else {
                numericValue = parseFloat(value);
            }

            // Verificar se é um número válido
            if (isNaN(numericValue)) {
                return includeSymbol ? 'R$ 0,00' : '0,00';
            }

            // Arredondar para o número de casas decimais especificado
            const rounded = Math.round(numericValue * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces);

            // Separar parte inteira e decimal
            const isNegative = rounded < 0;
            const absoluteValue = Math.abs(rounded);
            const integerPart = Math.floor(absoluteValue);
            const decimalPart = (absoluteValue - integerPart).toFixed(decimalPlaces).substring(2);

            // Formatar parte inteira com pontos como separadores de milhares
            const formattedInteger = integerPart.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

            // Combinar partes
            let formattedValue = `${formattedInteger},${decimalPart}`;

            // Adicionar sinal negativo se necessário
            if (isNegative) {
                formattedValue = `-${formattedValue}`;
            }

            // Adicionar símbolo R$ se solicitado
            return includeSymbol ? `R$ ${formattedValue}` : formattedValue;

        } catch (error) {
            console.warn('Erro na formatação monetária:', error);
            return includeSymbol ? 'R$ 0,00' : '0,00';
        }
    }

    /**
     * Converter string formatada em moeda para número
     * @param {string} formattedValue - String no formato "R$ 1.234,56"
     * @returns {number} Valor numérico correspondente
     */
    static parseCurrency(formattedValue) {
        if (!formattedValue || typeof formattedValue !== 'string') {
            return 0;
        }

        try {
            // Remove R$ e espaços
            let cleanValue = formattedValue.replace(/[R$\s]/g, '');

            // Lidar com formato brasileiro
            if (cleanValue.includes(',') && cleanValue.includes('.')) {
                const parts = cleanValue.split(',');
                if (parts.length === 2) {
                    const integerPart = parts[0].replace(/\./g, '');
                    const decimalPart = parts[1];
                    cleanValue = `${integerPart}.${decimalPart}`;
                }
            } else if (cleanValue.includes(',')) {
                cleanValue = cleanValue.replace(',', '.');
            }

            return parseFloat(cleanValue) || 0;

        } catch (error) {
            console.warn('Erro no parsing monetário:', error);
            return 0;
        }
    }

    /**
     * Validar entrada de valor monetário
     * @param {string} value - Valor a ser validado
     * @returns {object} {isValid: boolean, parsedValue: number}
     */
    static validateCurrencyInput(value) {
        try {
            const parsed = this.parseCurrency(value);
            return {
                isValid: !isNaN(parsed) && isFinite(parsed),
                parsedValue: parsed
            };
        } catch (error) {
            return {
                isValid: false,
                parsedValue: 0
            };
        }
    }

    /**
     * Formatar automaticamente input de moeda durante digitação
     * @param {HTMLInputElement} input - Elemento input
     */
    static setupCurrencyInput(input) {
        if (!input || !input.addEventListener) {
            console.warn('Elemento input inválido para formatação monetária');
            return;
        }

        // Evento de input para formatação em tempo real
        input.addEventListener('input', function(e) {
            const cursorPosition = e.target.selectionStart;
            const value = e.target.value;
            const numericValue = window.CurrencyFormatter.parseCurrency(value);
            const formattedValue = window.CurrencyFormatter.formatCurrency(numericValue, false);
            
            e.target.value = formattedValue;
            
            // Manter posição do cursor aproximada
            const newCursorPosition = Math.min(cursorPosition, formattedValue.length);
            e.target.setSelectionRange(newCursorPosition, newCursorPosition);
        });

        // Evento de blur para garantir formatação final
        input.addEventListener('blur', function(e) {
            const numericValue = window.CurrencyFormatter.parseCurrency(e.target.value);
            e.target.value = window.CurrencyFormatter.formatCurrency(numericValue, false);
        });

        // Permitir apenas números, vírgula, ponto e teclas de controle
        input.addEventListener('keypress', function(e) {
            const char = String.fromCharCode(e.which);
            if (!/[\d,.]/.test(char) && 
                !['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    /**
     * Aplicar formatação monetária a todos os elementos com classe específica
     * @param {string} className - Nome da classe CSS (padrão: 'currency-input')
     */
    static initializeAllCurrencyInputs(className = 'currency-input') {
        const inputs = document.querySelectorAll(`.${className}`);
        inputs.forEach(input => {
            this.setupCurrencyInput(input);
        });
    }

    /**
     * Formatar todos os elementos de texto com valores monetários
     * @param {string} selector - Seletor CSS (padrão: '.currency-display')
     */
    static formatAllCurrencyDisplays(selector = '.currency-display') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            const value = element.textContent || element.innerText;
            const formatted = this.formatCurrency(value);
            element.textContent = formatted;
            element.setAttribute('data-original-value', value);
        });
    }
}

    // Registrar na janela global
    window.CurrencyFormatter = CurrencyFormatter;
}

// Funções globais para compatibilidade e facilidade de uso
if (typeof window.formatCurrency === 'undefined') {
    window.formatCurrency = (value, includeSymbol, decimalPlaces) => 
        window.CurrencyFormatter.formatCurrency(value, includeSymbol, decimalPlaces);

    window.parseCurrency = (value) => 
        window.CurrencyFormatter.parseCurrency(value);

    window.formatMoeda = (value) => 
        window.CurrencyFormatter.formatCurrency(value);

    window.formatReal = (value) => 
        window.CurrencyFormatter.formatCurrency(value);
}

// Inicialização automática quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.CurrencyFormatter !== 'undefined') {
        // Inicializar inputs de moeda automaticamente
        window.CurrencyFormatter.initializeAllCurrencyInputs();
        
        // Formatar displays de moeda automaticamente
        window.CurrencyFormatter.formatAllCurrencyDisplays();
        
        console.log('✅ Sistema de formatação monetária inicializado');
    }
});

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CurrencyFormatter: window.CurrencyFormatter,
        formatCurrency: window.CurrencyFormatter.formatCurrency,
        parseCurrency: window.CurrencyFormatter.parseCurrency,
        CURRENCY_CONSTANTS: window.CURRENCY_CONSTANTS
    };
}