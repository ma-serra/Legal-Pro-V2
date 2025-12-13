/**
 * ARS Theme Manager
 * Gerencia a aplicação do novo padrão visual preservando elementos específicos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Identificar e marcar elementos para preservação
    markPreservationElements();
    
    // Aplicar tema ARS globalmente
    applyARSTheme();
    
    // Observar mudanças dinâmicas no DOM
    observeDOMChanges();
});

/**
 * Marca elementos específicos para preservação de estilos originais
 */
function markPreservationElements() {
    // Marcar cards de especialistas jurídicos
    const especialistasCards = document.querySelectorAll('a[href*="/juridico/especialistas"] .card, .especialista-card');
    especialistasCards.forEach(card => {
        card.classList.add('preserve-original', 'especialista-card');
        const parent = card.closest('a[href*="/juridico/especialistas"]');
        if (parent) parent.classList.add('preserve-original');
    });
    
    // Marcar cards do dashboard principal
    if (window.location.pathname === '/' || document.body.classList.contains('route-index')) {
        const dashboardCards = document.querySelectorAll('.card');
        dashboardCards.forEach(card => {
            card.classList.add('preserve-original', 'dashboard-card');
        });
    }
    
    // Marcar módulo completo de assistentes/area
    if (window.location.pathname.includes('/assistentes/area')) {
        document.body.classList.add('route-assistentes-area', 'assistentes-module');
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            element.classList.add('preserve-original', 'assistente-card');
        });
    }
    
    // Marcar por rota específica baseada na URL
    markByRoute();
}

/**
 * Marca elementos baseado na rota atual
 */
function markByRoute() {
    const path = window.location.pathname;
    
    // Rota de especialistas jurídicos
    if (path.includes('/juridico/especialistas')) {
        document.body.classList.add('route-juridico-especialistas');
        const container = document.querySelector('#especialistas-container') || document.body;
        container.classList.add('preserve-original');
    }
    
    // Rota do dashboard
    if (path === '/' || path === '/index') {
        document.body.classList.add('route-index', 'homepage-container');
        const mainContainer = document.querySelector('#dashboard-main') || document.querySelector('main');
        if (mainContainer) mainContainer.classList.add('preserve-original');
    }
    
    // Rota de assistentes por área
    if (path.includes('/assistentes/area/')) {
        document.body.classList.add('route-assistentes-area', 'assistentes-module');
        const container = document.querySelector('#assistentes-area-container') || document.body;
        container.classList.add('preserve-original');
    }
}

/**
 * Aplica o tema ARS globalmente
 */
function applyARSTheme() {
    // Adicionar classe principal do tema
    document.body.classList.add('ars-theme-active');
    
    // Aplicar variáveis CSS do tema ARS atualizado
    document.documentElement.style.setProperty('--color-primary', '#2CA7A4');
    document.documentElement.style.setProperty('--color-secondary', '#0B9197');
    document.documentElement.style.setProperty('--color-accent-1', '#547692');
    document.documentElement.style.setProperty('--color-accent-2', '#185684');
    document.documentElement.style.setProperty('--color-neutral', '#435464');
    document.documentElement.style.setProperty('--primary-shade-1', '#238683');
    document.documentElement.style.setProperty('--primary-shade-2', '#196664');
    document.documentElement.style.setProperty('--secondary-shade-1', '#09747A');
    document.documentElement.style.setProperty('--secondary-shade-2', '#06595E');
    document.documentElement.style.setProperty('--neutral-shade-2', '#262F3B');
    
    // Aplicar fontes ARS
    applyARSFonts();
    
    // Processar elementos existentes
    processExistingElements();
}

/**
 * Aplica as fontes do padrão ARS
 */
function applyARSFonts() {
    // Títulos (H1-H6)
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach(heading => {
        if (!heading.closest('.preserve-original')) {
            heading.style.fontFamily = "'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif";
            heading.style.fontWeight = '700';
        }
    });
    
    // Corpo de texto
    const textElements = document.querySelectorAll('p, span, div, label, .form-label');
    textElements.forEach(element => {
        if (!element.closest('.preserve-original')) {
            element.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
        }
    });
    
    // Números e KPIs
    const numberElements = document.querySelectorAll('.kpi-number, .stat-number, .metric-value, [data-type="number"]');
    numberElements.forEach(element => {
        if (!element.closest('.preserve-original')) {
            element.style.fontFamily = "'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif";
            element.style.fontWeight = '500';
        }
    });
}

/**
 * Processa elementos existentes aplicando tema ARS
 */
function processExistingElements() {
    // Processar cards (exceto os preservados)
    const cards = document.querySelectorAll('.card:not(.preserve-original):not(.especialista-card):not(.dashboard-card):not(.assistente-card)');
    cards.forEach(card => {
        applyARSCardStyle(card);
    });
    
    // Processar botões (exceto os preservados)
    const buttons = document.querySelectorAll('.btn:not(.preserve-original .btn)');
    buttons.forEach(button => {
        applyARSButtonStyle(button);
    });
    
    // Processar formulários (exceto os preservados)
    const formElements = document.querySelectorAll('.form-control:not(.preserve-original .form-control), .form-select:not(.preserve-original .form-select)');
    formElements.forEach(element => {
        applyARSFormStyle(element);
    });
}

/**
 * Aplica estilo ARS a um card
 */
function applyARSCardStyle(card) {
    card.style.background = 'rgba(248, 252, 253, 0.08)';
    card.style.border = '1px solid rgba(172, 189, 194, 0.2)';
    card.style.borderRadius = '12px';
    card.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.1)';
    card.style.backdropFilter = 'blur(10px)';
    card.style.transition = 'all 0.3s ease';
}

/**
 * Aplica estilo ARS a um botão
 */
function applyARSButtonStyle(button) {
    button.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    button.style.fontWeight = '500';
    button.style.borderRadius = '8px';
    button.style.padding = '0.75rem 1.5rem';
    button.style.transition = 'all 0.3s ease';
    button.style.border = 'none';
    
    if (button.classList.contains('btn-primary')) {
        button.style.background = '#2CA7A4';
        button.style.color = '#ffffff';
        button.style.boxShadow = '0 2px 8px rgba(44, 167, 164, 0.3)';
    } else if (button.classList.contains('btn-secondary')) {
        button.style.background = '#0B9197';
        button.style.color = '#ffffff';
        button.style.boxShadow = '0 2px 8px rgba(11, 145, 151, 0.3)';
    }
}

/**
 * Aplica estilo ARS a elementos de formulário
 */
function applyARSFormStyle(element) {
    element.style.backgroundColor = 'rgba(248, 252, 253, 0.1)';
    element.style.border = '1px solid #ACBDC2';
    element.style.borderRadius = '8px';
    element.style.color = '#ffffff';
    element.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    element.style.padding = '0.75rem 1rem';
    element.style.transition = 'all 0.3s ease';
}

/**
 * Observa mudanças no DOM para aplicar tema em elementos dinâmicos
 */
function observeDOMChanges() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Verificar se precisa preservar
                        if (shouldPreserveElement(node)) {
                            node.classList.add('preserve-original');
                        } else {
                            // Aplicar tema ARS
                            applyThemeToNewElement(node);
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

/**
 * Verifica se um elemento deve ser preservado
 */
function shouldPreserveElement(element) {
    const path = window.location.pathname;
    
    // Verificar por rota
    if (path.includes('/juridico/especialistas') || 
        path === '/' || 
        path.includes('/assistentes/area/')) {
        return true;
    }
    
    // Verificar por classe ou atributo
    if (element.classList.contains('especialista-card') ||
        element.classList.contains('dashboard-card') ||
        element.classList.contains('assistente-card') ||
        element.closest('.preserve-original')) {
        return true;
    }
    
    return false;
}

/**
 * Aplica tema ARS a novos elementos
 */
function applyThemeToNewElement(element) {
    if (element.classList.contains('card')) {
        applyARSCardStyle(element);
    }
    
    if (element.classList.contains('btn')) {
        applyARSButtonStyle(element);
    }
    
    if (element.classList.contains('form-control') || element.classList.contains('form-select')) {
        applyARSFormStyle(element);
    }
    
    // Aplicar fontes
    if (element.matches('h1, h2, h3, h4, h5, h6')) {
        element.style.fontFamily = "'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif";
        element.style.fontWeight = '700';
    }
    
    if (element.matches('p, span, div, label')) {
        element.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    }
}

/**
 * Função utilitária para debug
 */
function debugTheme() {
    console.log('ARS Theme Debug Info:');
    console.log('Current path:', window.location.pathname);
    console.log('Body classes:', document.body.className);
    console.log('Preserved elements:', document.querySelectorAll('.preserve-original').length);
    console.log('ARS themed elements:', document.querySelectorAll('.ars-theme-active *').length);
}

// Expor função de debug globalmente
window.arsThemeDebug = debugTheme;