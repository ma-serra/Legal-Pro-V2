/**
 * Sistema de formatação monetária corrigido
 * Sem declarações duplicadas ou conflitos de escopo
 * @version 1.3.0 - Definitivamente corrigido
 */

(function() {
    'use strict';
    
    // Evitar redeclarações usando IIFE e verificação de existência
    if (window.currencyFormatterLoaded) {
        return;
    }
    window.currencyFormatterLoaded = true;

    // Constantes únicas
    const CURRENCY_CONFIG = {
        SYMBOL: 'R$',
        DECIMAL_PLACES: 2,
        THOUSANDS_SEPARATOR: '.',
        DECIMAL_SEPARATOR: ',',
        PATTERN: /^R?\$?\s?(\d{1,3}(\.\d{3})*),(\d{2})$/
    };

    // Classe principal
    class MoneyFormatter {
        static formatCurrency(value, includeSymbol = true, decimalPlaces = 2) {
            if (value === null || value === undefined || value === '') {
                return includeSymbol ? 'R$ 0,00' : '0,00';
            }

            try {
                let numericValue;

                if (typeof value === 'string') {
                    let cleanValue = value.replace(/[R$\s]/g, '');
                    
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

                    numericValue = parseFloat(cleanValue);
                } else {
                    numericValue = parseFloat(value);
                }

                if (isNaN(numericValue)) {
                    return includeSymbol ? 'R$ 0,00' : '0,00';
                }

                const rounded = Math.round(numericValue * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces);
                const isNegative = rounded < 0;
                const absoluteValue = Math.abs(rounded);
                const integerPart = Math.floor(absoluteValue);
                const decimalPart = (absoluteValue - integerPart).toFixed(decimalPlaces).substring(2);

                const formattedInteger = integerPart.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                let formattedValue = `${formattedInteger},${decimalPart}`;

                if (isNegative) {
                    formattedValue = `-${formattedValue}`;
                }

                return includeSymbol ? `R$ ${formattedValue}` : formattedValue;

            } catch (error) {
                console.warn('Erro na formatação monetária:', error);
                return includeSymbol ? 'R$ 0,00' : '0,00';
            }
        }

        static parseCurrency(formattedValue) {
            if (!formattedValue || typeof formattedValue !== 'string') {
                return 0;
            }

            try {
                let cleanValue = formattedValue.replace(/[R$\s]/g, '');

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

        static setupCurrencyInput(input) {
            if (!input || !input.addEventListener) {
                return;
            }

            input.addEventListener('input', function(e) {
                const cursorPosition = e.target.selectionStart;
                const value = e.target.value;
                const numericValue = MoneyFormatter.parseCurrency(value);
                const formattedValue = MoneyFormatter.formatCurrency(numericValue, false);
                
                e.target.value = formattedValue;
                
                const newCursorPosition = Math.min(cursorPosition, formattedValue.length);
                e.target.setSelectionRange(newCursorPosition, newCursorPosition);
            });

            input.addEventListener('blur', function(e) {
                const numericValue = MoneyFormatter.parseCurrency(e.target.value);
                e.target.value = MoneyFormatter.formatCurrency(numericValue, false);
            });
        }

        static initializeAllCurrencyInputs(className = 'currency-input') {
            const inputs = document.querySelectorAll(`.${className}`);
            inputs.forEach(input => {
                this.setupCurrencyInput(input);
            });
        }
    }

    // Registrar globalmente sem conflitos
    window.MoneyFormatter = MoneyFormatter;
    window.formatCurrency = (value, includeSymbol, decimalPlaces) => 
        MoneyFormatter.formatCurrency(value, includeSymbol, decimalPlaces);
    window.parseCurrency = (value) => MoneyFormatter.parseCurrency(value);
    window.formatMoeda = (value) => MoneyFormatter.formatCurrency(value);
    window.formatReal = (value) => MoneyFormatter.formatCurrency(value);

    // Inicialização automática
    document.addEventListener('DOMContentLoaded', function() {
        MoneyFormatter.initializeAllCurrencyInputs();
        console.log('✅ Sistema de formatação monetária inicializado (v1.3.0)');
    });

})();