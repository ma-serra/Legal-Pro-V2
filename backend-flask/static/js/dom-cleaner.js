/**
 * Script de limpeza automática do DOM
 * Remove avisos de innerHTML de todos os elementos da página
 */

function limparAvisosDom() {
    const elementos = document.querySelectorAll('*');
    let limpezas = 0;
    
    // Padrões de texto para remover
    const padroes = [
        /AVISO:\s*Validar\/sanitizar\s*dados\s*antes\s*de\s*usar\s*innerHTML/gi,
        /Validar\/sanitizar\s*dados\s*antes\s*de\s*usar\s*innerHTML/gi,
        /AVISO:\s*Validar\/sanitizar/gi,
        /Validar\/sanitizar/gi
    ];
    
    elementos.forEach(elemento => {
        // Verificar textContent apenas em elementos visuais específicos (evita interferir com scripts)
        if (elemento.textContent && !elemento.tagName || 
            ['DIV', 'SPAN', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'BUTTON', 'A', 'LABEL', 'TD', 'TH'].includes(elemento.tagName)) {
            let textoOriginal = elemento.textContent;
            let textoLimpo = textoOriginal;
            
            // Só limpar se contém exatamente o padrão de aviso
            if (textoOriginal.includes('AVISO:') || textoOriginal.includes('Validar/sanitizar')) {
                padroes.forEach(padrao => {
                    textoLimpo = textoLimpo.replace(padrao, '');
                });
                
                if (textoLimpo !== textoOriginal) {
                    elemento.textContent = textoLimpo.trim();
                    limpezas++;
                }
            }
        }
        
        // Verificar innerHTML
        if (elemento.innerHTML) {
            let htmlOriginal = elemento.innerHTML;
            let htmlLimpo = htmlOriginal;
            
            padroes.forEach(padrao => {
                htmlLimpo = htmlLimpo.replace(padrao, '');
            });
            
            if (htmlLimpo !== htmlOriginal) {
                elemento.innerHTML = htmlLimpo;
                limpezas++;
            }
        }
        
        // Verificar atributos específicos
        ['title', 'alt', 'placeholder', 'data-original-title', 'aria-label'].forEach(attr => {
            const valor = elemento.getAttribute(attr);
            if (valor) {
                let valorLimpo = valor;
                padroes.forEach(padrao => {
                    valorLimpo = valorLimpo.replace(padrao, '');
                });
                
                if (valorLimpo !== valor) {
                    elemento.setAttribute(attr, valorLimpo.trim());
                    limpezas++;
                }
            }
        });
    });
    
    // Limpar especificamente cards de fluxo
    const cardsFluxo = document.querySelectorAll('.card, .flow-element, .agent-item, .node');
    cardsFluxo.forEach(card => {
        const textoCard = card.textContent || '';
        if (textoCard.includes('AVISO') || textoCard.includes('Validar') || textoCard.includes('sanitizar')) {
            const elementosTexto = card.querySelectorAll('*');
            elementosTexto.forEach(el => {
                if (el.textContent) {
                    padroes.forEach(padrao => {
                        el.textContent = el.textContent.replace(padrao, '').trim();
                    });
                }
            });
        }
    });
    
    if (limpezas > 0) {
        console.log(`🧹 Limpados ${limpezas} avisos do DOM`);
    }
}

// Executar limpeza quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(limparAvisosDom, 500);
});

// Executar limpeza apenas se necessário
setInterval(function() {
    const hasWarnings = document.body.textContent.includes('AVISO:') || document.body.textContent.includes('Validar/sanitizar');
    if (hasWarnings) {
        limparAvisosDom();
    }
}, 3000);

// Executar limpeza quando houver mudanças no DOM
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        let needsCleaning = false;
        mutations.forEach(mutation => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                needsCleaning = true;
            }
        });
        if (needsCleaning) {
            setTimeout(limparAvisosDom, 100);
        }
    });
    
    if (document.body) {
        observer.observe(document.body, { 
            childList: true, 
            subtree: true, 
            characterData: true 
        });
    }
}