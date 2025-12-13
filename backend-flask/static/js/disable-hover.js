/**
 * Script para remover todos os efeitos hover de botões no sistema
 * Este script é executado após o carregamento completo da página
 */
document.addEventListener('DOMContentLoaded', function() {
    // Identificar todos os botões no documento
    const botoes = document.querySelectorAll('.btn, button, a.btn, input[type="button"], input[type="submit"]');
    
    // Aplicar estilos fixos a cada botão
    botoes.forEach(function(botao) {
        // Salvar cor original
        const bgColor = getComputedStyle(botao).backgroundColor;
        const borderColor = getComputedStyle(botao).borderColor;
        const textColor = getComputedStyle(botao).color;
        
        // Sobrescrever estilos padrão
        botao.style.transition = 'none';
        botao.style.transform = 'none';
        botao.style.boxShadow = 'none';
        
        // Definir aparência para classe secundária (btn-secondary)
        if (botao.classList.contains('btn-secondary') || 
            botao.classList.contains('btn-outline-secondary')) {
            botao.style.backgroundColor = '#6c757d';
            botao.style.borderColor = '#6c757d';
            botao.style.color = 'white';
        }
        
        // Remover todos os listeners de hover que possam estar definidos via CSS
        botao.addEventListener('mouseenter', function(e) {
            if (botao.classList.contains('btn-secondary') || 
                botao.classList.contains('btn-outline-secondary')) {
                botao.style.backgroundColor = '#6c757d';
                botao.style.borderColor = '#6c757d';
                botao.style.color = 'white';
            } else {
                botao.style.backgroundColor = bgColor;
                botao.style.borderColor = borderColor;
                botao.style.color = textColor;
            }
            botao.style.transform = 'none';
            botao.style.boxShadow = 'none';
            e.stopPropagation();
        }, true);
        
        botao.addEventListener('mouseleave', function(e) {
            if (botao.classList.contains('btn-secondary') || 
                botao.classList.contains('btn-outline-secondary')) {
                botao.style.backgroundColor = '#6c757d';
                botao.style.borderColor = '#6c757d';
                botao.style.color = 'white';
            } else {
                botao.style.backgroundColor = bgColor;
                botao.style.borderColor = borderColor;
                botao.style.color = textColor;
            }
            botao.style.transform = 'none';
            botao.style.boxShadow = 'none';
            e.stopPropagation();
        }, true);
    });
    
    // Detectar dinamicamente novos botões adicionados ao DOM
    const observador = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.nodeType === 1) { // Elemento Node
                        // Verificar se o elemento adicionado é um botão
                        if (node.classList && (node.classList.contains('btn') || node.tagName === 'BUTTON')) {
                            aplicarEstiloBotao(node);
                        }
                        
                        // Verificar botões dentro do elemento adicionado
                        const botoesInternos = node.querySelectorAll('.btn, button, a.btn');
                        botoesInternos.forEach(aplicarEstiloBotao);
                    }
                }
            }
        });
    });
    
    function aplicarEstiloBotao(botao) {
        // Aplicar estilo fixo para btn-secondary
        if (botao.classList.contains('btn-secondary') || 
            botao.classList.contains('btn-outline-secondary')) {
            botao.style.backgroundColor = '#6c757d';
            botao.style.borderColor = '#6c757d';
            botao.style.color = 'white';
        }
        
        botao.style.transition = 'none';
        botao.style.transform = 'none';
        botao.style.boxShadow = 'none';
        
        // Adicionar os mesmos event listeners para mouseenter/mouseleave
        botao.addEventListener('mouseenter', function(e) {
            if (botao.classList.contains('btn-secondary') || 
                botao.classList.contains('btn-outline-secondary')) {
                botao.style.backgroundColor = '#6c757d';
                botao.style.borderColor = '#6c757d';
                botao.style.color = 'white';
            }
            botao.style.transform = 'none';
            botao.style.boxShadow = 'none';
            e.stopPropagation();
        }, true);
        
        botao.addEventListener('mouseleave', function(e) {
            if (botao.classList.contains('btn-secondary') || 
                botao.classList.contains('btn-outline-secondary')) {
                botao.style.backgroundColor = '#6c757d';
                botao.style.borderColor = '#6c757d';
                botao.style.color = 'white';
            }
            botao.style.transform = 'none';
            botao.style.boxShadow = 'none';
            e.stopPropagation();
        }, true);
    }
    
    // Observar todo o documento para detectar mudanças no DOM
    observador.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Aplicar estilos específicos para botões com texto "Cancelar"
    // Usando JavaScript puro para encontrar elementos que contêm o texto "Cancelar"
    const todosBotoes = document.querySelectorAll('a.btn, button, .btn');
    todosBotoes.forEach(function(botao) {
        if (botao.textContent.includes('Cancelar')) {
            botao.style.backgroundColor = '#6c757d';
            botao.style.borderColor = '#6c757d';
            botao.style.color = 'white';
            botao.style.transition = 'none';
            botao.style.transform = 'none';
            botao.style.boxShadow = 'none';
        }
    });
});