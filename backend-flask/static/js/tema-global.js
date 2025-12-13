/**
 * Sistema Global de Temas - Aplica temas personalizados em todas as páginas
 */

(function() {
    'use strict';
    
    // Função para aplicar tema do localStorage
    function aplicarTemaGlobal() {
        try {
            const temaSalvo = localStorage.getItem('tema_sistema');
            if (!temaSalvo) return;
            
            const cores = JSON.parse(temaSalvo);
            
            // Aplicar variáveis CSS globais
            const root = document.documentElement;
            root.style.setProperty('--header-bg', cores.header_bg || '#1a1a1a');
            root.style.setProperty('--primary-color', cores.primary_color || '#007bff');
            root.style.setProperty('--text-color', cores.text_color || '#ffffff');
            root.style.setProperty('--accent-color', cores.accent_color || '#4dabf7');
            root.style.setProperty('--bg-color', cores.bg_color || '#2c2c2c');
            
            // Aplicar ao navbar
            aplicarTemaNavbar(cores);
            
        } catch (error) {
            console.warn('Erro ao aplicar tema global:', error);
        }
    }
    
    // Função para aplicar tema ao navbar
    function aplicarTemaNavbar(cores) {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // Aplicar cor de fundo do header
        navbar.style.backgroundColor = cores.header_bg || '#1a1a1a';
        
        // Aplicar cor do texto
        navbar.querySelectorAll('.navbar-brand, .nav-link').forEach(el => {
            el.style.color = cores.text_color || '#ffffff';
        });
        
        // Aplicar cores dos ícones
        navbar.querySelectorAll('i').forEach(icon => {
            if (icon.classList.contains('fa-balance-scale') || 
                icon.classList.contains('fa-user') ||
                icon.classList.contains('fas')) {
                icon.style.color = cores.primary_color || '#007bff';
            }
            if (icon.classList.contains('bi-palette-fill') ||
                icon.classList.contains('bi')) {
                icon.style.color = cores.accent_color || '#4dabf7';
            }
        });
        
        // Aplicar ao header se existir
        const header = document.querySelector('header');
        if (header) {
            header.style.backgroundColor = cores.header_bg || '#1a1a1a';
            header.style.color = cores.text_color || '#ffffff';
        }
    }
    
    // Função para observar mudanças no DOM e aplicar tema
    function observarMudancasDOM() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches('.navbar') || node.querySelector('.navbar')) {
                                setTimeout(aplicarTemaGlobal, 100);
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
    
    // Aplicar tema quando o DOM estiver carregado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            aplicarTemaGlobal();
            observarMudancasDOM();
        });
    } else {
        aplicarTemaGlobal();
        observarMudancasDOM();
    }
    
    // Aplicar tema quando a página estiver completamente carregada
    window.addEventListener('load', aplicarTemaGlobal);
    
    // Escutar eventos personalizados para aplicar tema
    window.addEventListener('tema-atualizado', function(event) {
        if (event.detail && event.detail.cores) {
            localStorage.setItem('tema_sistema', JSON.stringify(event.detail.cores));
            aplicarTemaGlobal();
        }
    });
    
    // Expor funções globalmente para uso em outros scripts
    window.TemaGlobal = {
        aplicar: aplicarTemaGlobal,
        salvar: function(cores) {
            localStorage.setItem('tema_sistema', JSON.stringify(cores));
            aplicarTemaGlobal();
            
            // Disparar evento personalizado
            window.dispatchEvent(new CustomEvent('tema-atualizado', {
                detail: { cores: cores }
            }));
        },
        obter: function() {
            try {
                const tema = localStorage.getItem('tema_sistema');
                return tema ? JSON.parse(tema) : null;
            } catch (error) {
                console.warn('Erro ao obter tema:', error);
                return null;
            }
        },
        resetar: function() {
            localStorage.removeItem('tema_sistema');
            location.reload();
        }
    };
    
})();