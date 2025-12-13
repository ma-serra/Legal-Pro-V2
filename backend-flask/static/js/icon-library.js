/**
 * Sistema de Biblioteca de Ícones Legais
 * Integra os ícones extraídos dos 5 packs ao editor
 */

class IconLibrary {
    constructor() {
        this.currentPack = 'all';
        this.searchQuery = '';
        this.icons = [];
        this.loading = false;
        this.init();
    }

    init() {
        this.loadIconLibrary();
        this.setupEventListeners();
    }

    async loadIconLibrary() {
        try {
            this.loading = true;
            this.showLoadingSpinner();
            
            const response = await fetch('/api/icons/library');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.icons = data;
            this.renderIconLibrary();
            this.updateStats();
            
        } catch (error) {
            console.error('Erro ao carregar biblioteca de ícones:', error);
            this.showError('Erro ao carregar biblioteca de ícones');
        } finally {
            this.loading = false;
            this.hideLoadingSpinner();
        }
    }

    setupEventListeners() {
        // Busca de ícones
        const searchInput = document.getElementById('icon-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.searchIcons();
            });
        }

        // Filtro por pack
        const packFilter = document.getElementById('pack-filter');
        if (packFilter) {
            packFilter.addEventListener('change', (e) => {
                this.currentPack = e.target.value;
                this.filterByPack();
            });
        }

        // Delegação de eventos para cliques em ícones
        const iconContainer = document.getElementById('icon-container');
        if (iconContainer) {
            iconContainer.addEventListener('click', (e) => {
                const iconItem = e.target.closest('.icon-item');
                if (iconItem) {
                    this.selectIcon(iconItem);
                }
            });
        }
    }

    async searchIcons() {
        if (this.loading) return;

        try {
            this.loading = true;
            this.showLoadingSpinner();

            const params = new URLSearchParams({
                q: this.searchQuery,
                category: this.currentPack !== 'all' ? this.getPackCategory(this.currentPack) : ''
            });

            const response = await fetch(`/api/icons/search?${params}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.renderSearchResults(data);

        } catch (error) {
            console.error('Erro na busca de ícones:', error);
            this.showError('Erro na busca de ícones');
        } finally {
            this.loading = false;
            this.hideLoadingSpinner();
        }
    }

    async filterByPack() {
        if (this.currentPack === 'all') {
            this.renderIconLibrary();
            return;
        }

        try {
            this.loading = true;
            this.showLoadingSpinner();

            const response = await fetch(`/api/icons/pack/${this.currentPack}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.renderPackIcons(data);

        } catch (error) {
            console.error('Erro ao filtrar por pack:', error);
            this.showError('Erro ao filtrar ícones');
        } finally {
            this.loading = false;
            this.hideLoadingSpinner();
        }
    }

    renderIconLibrary() {
        const container = document.getElementById('icon-container');
        if (!container || !this.icons.packs) return;

        let html = '';
        
        Object.entries(this.icons.packs).forEach(([packName, packData]) => {
            html += `
                <div class="pack-section mb-4">
                    <h5 class="pack-title">${packData.name}</h5>
                    <div class="pack-stats text-muted mb-2">
                        ${packData.total} ícones disponíveis
                    </div>
                    <div class="icon-grid">
                        ${packData.icons.map(icon => this.renderIcon(icon)).join('')}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    renderSearchResults(data) {
        const container = document.getElementById('icon-container');
        if (!container) return;

        const resultsHeader = `
            <div class="search-results-header mb-3">
                <h5>Resultados da Busca</h5>
                <p class="text-muted">
                    ${data.total} ícones encontrados
                    ${data.query ? `para "${data.query}"` : ''}
                    ${data.category ? `na categoria "${data.category}"` : ''}
                </p>
            </div>
        `;

        const iconsHtml = data.icons.map(icon => this.renderIcon(icon)).join('');

        container.innerHTML = `
            ${resultsHeader}
            <div class="icon-grid">
                ${iconsHtml}
            </div>
        `;
    }

    renderPackIcons(data) {
        const container = document.getElementById('icon-container');
        if (!container) return;

        const packHeader = `
            <div class="pack-header mb-3">
                <h5>${data.name}</h5>
                <p class="text-muted">${data.total} ícones disponíveis</p>
            </div>
        `;

        const iconsHtml = data.icons.map(icon => this.renderIcon(icon)).join('');

        container.innerHTML = `
            ${packHeader}
            <div class="icon-grid">
                ${iconsHtml}
            </div>
        `;
    }

    renderIcon(icon) {
        return `
            <div class="icon-item" data-icon-id="${icon.id}" data-icon-url="${icon.url}">
                <img src="${icon.url}" alt="${icon.name}" class="icon-image">
                <div class="icon-info">
                    <div class="icon-name">${icon.name}</div>
                    <div class="icon-category">${icon.category}</div>
                </div>
            </div>
        `;
    }

    selectIcon(iconItem) {
        // Remover seleção anterior
        document.querySelectorAll('.icon-item.selected').forEach(item => {
            item.classList.remove('selected');
        });

        // Adicionar seleção atual
        iconItem.classList.add('selected');

        const iconUrl = iconItem.dataset.iconUrl;
        const iconId = iconItem.dataset.iconId;

        // Inserir ícone no editor
        this.insertIconIntoEditor(iconUrl, iconId);
    }

    insertIconIntoEditor(iconUrl, iconId) {
        const editor = document.getElementById('editor-content');
        if (!editor) return;

        // Criar elemento de imagem
        const img = document.createElement('img');
        img.src = iconUrl;
        img.alt = `Ícone Legal ${iconId}`;
        img.className = 'legal-icon';
        img.style.cssText = 'max-width: 100px; height: auto; margin: 10px; cursor: pointer;';

        // Inserir no editor
        if (editor.contentEditable === 'true') {
            // Editor de texto rico
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            range.insertNode(img);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);
        } else {
            // Fallback: adicionar no final
            editor.appendChild(img);
        }

        // Fechar modal se estiver aberto
        const modal = document.getElementById('iconLibraryModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        }

        // Trigger change event para salvar automaticamente
        editor.dispatchEvent(new Event('input', { bubbles: true }));
    }

    updateStats() {
        const statsContainer = document.getElementById('icon-stats');
        if (!statsContainer || !this.icons) return;

        statsContainer.innerHTML = `
            <div class="stats-item">
                <strong>${this.icons.total_icons}</strong>
                <span>Ícones Totais</span>
            </div>
            <div class="stats-item">
                <strong>${Object.keys(this.icons.packs).length}</strong>
                <span>Packs Disponíveis</span>
            </div>
            <div class="stats-item">
                <strong>${this.icons.categories.length}</strong>
                <span>Categorias</span>
            </div>
        `;
    }

    getPackCategory(packName) {
        const categories = {
            'pack1': 'Direito Criminal',
            'pack2': 'Direito Empresarial',
            'pack3': 'Direito Bancário',
            'pack4': 'Direito Trabalhista',
            'pack5': 'Direito do Consumidor'
        };
        return categories[packName] || '';
    }

    showLoadingSpinner() {
        const container = document.getElementById('icon-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <p class="mt-2 text-muted">Carregando ícones...</p>
                </div>
            `;
        }
    }

    hideLoadingSpinner() {
        // Spinner será removido quando o conteúdo for renderizado
    }

    showError(message) {
        const container = document.getElementById('icon-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </div>
            `;
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('icon-container')) {
        window.iconLibrary = new IconLibrary();
    }
});

// Função global para abrir modal de ícones
function openIconLibrary() {
    const modal = new bootstrap.Modal(document.getElementById('iconLibraryModal'));
    modal.show();
    
    // Inicializar biblioteca se ainda não foi feito
    if (!window.iconLibrary) {
        window.iconLibrary = new IconLibrary();
    }
}