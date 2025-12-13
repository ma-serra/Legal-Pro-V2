// Fallback simples para Bootstrap caso CDN falhe
console.log('Bootstrap fallback carregado');

// Função básica para dropdown
function initFallbackDropdown() {
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            if (menu && menu.classList.contains('dropdown-menu')) {
                menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', initFallbackDropdown);