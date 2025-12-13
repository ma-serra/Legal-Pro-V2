/**
 * Sistema de Pesquisa Jurídica Inteligente
 * Integra com a API do Legal Design Pro para realizar pesquisas jurídicas
 */

class LegalResearchSystem {
    constructor() {
        this.apiEndpoint = '/legal-design-pro/pesquisa-juridica';
        this.currentResults = null;
        this.searchHistory = this.loadSearchHistory();
        
        this.init();
    }

    init() {
        this.setupResearchModal();
        this.bindEvents();
    }

    setupResearchModal() {
        // Criar modal de pesquisa jurídica se não existir
        if (!document.getElementById('researchModal')) {
            const modalHTML = `
                <div class="modal fade" id="researchModal" tabindex="-1" aria-labelledby="researchModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content bg-dark text-white">
                            <div class="modal-header border-secondary">
                                <h5 class="modal-title" id="researchModalLabel">
                                    <i class="bi bi-search"></i> Pesquisa Jurídica Inteligente
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <!-- Formulário de Pesquisa -->
                                <div class="row mb-4">
                                    <div class="col-md-8">
                                        <label for="researchQuery" class="form-label">Termo de Pesquisa</label>
                                        <input type="text" class="form-control bg-secondary text-white border-secondary" 
                                               id="researchQuery" placeholder="Ex: Responsabilidade civil por danos morais">
                                    </div>
                                    <div class="col-md-4">
                                        <label for="researchArea" class="form-label">Área Jurídica</label>
                                        <select class="form-select bg-secondary text-white border-secondary" id="researchArea">
                                            <option value="Geral">Geral</option>
                                            <option value="Direito Civil">Direito Civil</option>
                                            <option value="Direito Penal">Direito Penal</option>
                                            <option value="Direito Trabalhista">Direito Trabalhista</option>
                                            <option value="Direito Empresarial">Direito Empresarial</option>
                                            <option value="Direito Bancário">Direito Bancário</option>
                                            <option value="Direito do Consumidor">Direito do Consumidor</option>
                                            <option value="Direito Tributário">Direito Tributário</option>
                                            <option value="Direito Administrativo">Direito Administrativo</option>
                                        </select>
                                    </div>
                                </div>

                                <div class="row mb-3">
                                    <div class="col-12">
                                        <button type="button" class="btn btn-primary me-2" id="executeResearch">
                                            <i class="bi bi-search"></i> Pesquisar
                                        </button>
                                        <button type="button" class="btn btn-outline-secondary me-2" id="clearResearch">
                                            <i class="bi bi-trash"></i> Limpar
                                        </button>
                                        <button type="button" class="btn btn-outline-info" id="showHistory">
                                            <i class="bi bi-clock-history"></i> Histórico
                                        </button>
                                    </div>
                                </div>

                                <!-- Loading State -->
                                <div id="researchLoading" class="text-center d-none">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Pesquisando...</span>
                                    </div>
                                    <p class="mt-2">Realizando pesquisa jurídica...</p>
                                </div>

                                <!-- Resultados da Pesquisa -->
                                <div id="researchResults" class="d-none">
                                    <div class="card bg-secondary border-secondary">
                                        <div class="card-header">
                                            <h6 class="mb-0">
                                                <i class="bi bi-file-earmark-text"></i> Resultados da Pesquisa
                                            </h6>
                                        </div>
                                        <div class="card-body">
                                            <div id="researchContent" class="research-content"></div>
                                            <div class="mt-3">
                                                <button type="button" class="btn btn-success btn-sm" id="insertResearchResult">
                                                    <i class="bi bi-plus-circle"></i> Inserir no Documento
                                                </button>
                                                <button type="button" class="btn btn-info btn-sm" id="saveResearch">
                                                    <i class="bi bi-bookmark"></i> Salvar Pesquisa
                                                </button>
                                                <button type="button" class="btn btn-warning btn-sm" id="exportResearch">
                                                    <i class="bi bi-download"></i> Exportar
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Histórico de Pesquisas -->
                                <div id="researchHistoryPanel" class="d-none">
                                    <div class="card bg-secondary border-secondary">
                                        <div class="card-header">
                                            <h6 class="mb-0">
                                                <i class="bi bi-clock-history"></i> Histórico de Pesquisas
                                            </h6>
                                        </div>
                                        <div class="card-body">
                                            <div id="historyList"></div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Sugestões de Pesquisa -->
                                <div class="mt-3">
                                    <h6>Sugestões de Pesquisa:</h6>
                                    <div class="d-flex flex-wrap gap-2">
                                        <span class="badge bg-primary suggestion-badge" data-query="responsabilidade civil por danos morais">
                                            Responsabilidade Civil
                                        </span>
                                        <span class="badge bg-primary suggestion-badge" data-query="prescrição e decadência">
                                            Prescrição e Decadência
                                        </span>
                                        <span class="badge bg-primary suggestion-badge" data-query="contratos de adesão">
                                            Contratos de Adesão
                                        </span>
                                        <span class="badge bg-primary suggestion-badge" data-query="direitos do consumidor">
                                            Direitos do Consumidor
                                        </span>
                                        <span class="badge bg-primary suggestion-badge" data-query="rescisão trabalhista">
                                            Rescisão Trabalhista
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
    }

    bindEvents() {
        // Evento para abrir modal de pesquisa
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-ai="research"]')) {
                e.preventDefault();
                this.openResearchModal();
            }
        });

        // Eventos do modal
        document.getElementById('executeResearch')?.addEventListener('click', () => this.executeSearch());
        document.getElementById('clearResearch')?.addEventListener('click', () => this.clearForm());
        document.getElementById('showHistory')?.addEventListener('click', () => this.showHistory());
        document.getElementById('insertResearchResult')?.addEventListener('click', () => this.insertResult());
        document.getElementById('saveResearch')?.addEventListener('click', () => this.saveCurrentResearch());
        document.getElementById('exportResearch')?.addEventListener('click', () => this.exportResults());

        // Sugestões
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-badge')) {
                const query = e.target.dataset.query;
                document.getElementById('researchQuery').value = query;
                this.executeSearch();
            }
        });

        // Enter para pesquisar
        document.getElementById('researchQuery')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeSearch();
            }
        });
    }

    openResearchModal() {
        const modal = new bootstrap.Modal(document.getElementById('researchModal'));
        modal.show();
        
        // Focus no campo de pesquisa
        setTimeout(() => {
            document.getElementById('researchQuery').focus();
        }, 500);
    }

    async executeSearch() {
        const query = document.getElementById('researchQuery').value.trim();
        const area = document.getElementById('researchArea').value;

        if (!query) {
            this.showNotification('Por favor, insira um termo de pesquisa.', 'warning');
            return;
        }

        this.showLoading(true);
        this.hideResults();

        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    area: area,
                    provider: 'openai'
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentResults = data;
                this.displayResults(data);
                this.addToHistory(query, area, data.timestamp);
                this.showNotification('Pesquisa realizada com sucesso!', 'success');
            } else {
                this.showNotification('Erro na pesquisa: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Erro na pesquisa:', error);
            this.showNotification('Erro de conexão. Verifique sua internet.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        const content = document.getElementById('researchContent');
        
        // Formatar resultado
        const formattedResult = this.formatResearchResult(data.result);
        
        content.innerHTML = `
            <div class="research-metadata mb-3">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Consulta:</strong> ${data.query}
                    </div>
                    <div class="col-md-3">
                        <strong>Área:</strong> ${data.area}
                    </div>
                    <div class="col-md-3">
                        <strong>Data:</strong> ${new Date(data.timestamp).toLocaleString('pt-BR')}
                    </div>
                </div>
            </div>
            <div class="research-result">
                ${formattedResult}
            </div>
        `;

        this.showResults();
    }

    formatResearchResult(result) {
        // Converter markdown básico para HTML
        return result
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/(\d+\.)/g, '<br><strong>$1</strong>')
            .replace(/([A-Z][^:]*:)/g, '<br><strong>$1</strong>');
    }

    insertResult() {
        if (!this.currentResults) return;

        // Encontrar o editor de documento
        const documentContent = document.getElementById('documentContent') || 
                              document.querySelector('.document-page') ||
                              document.querySelector('[contenteditable="true"]');

        if (documentContent) {
            const researchSection = `
                <div class="research-section" style="border-left: 4px solid #007bff; padding-left: 15px; margin: 20px 0; background: rgba(0,123,255,0.1);">
                    <h4 style="color: #007bff; margin-bottom: 10px;">📚 Pesquisa Jurídica</h4>
                    <p><strong>Consulta:</strong> ${this.currentResults.query}</p>
                    <p><strong>Área:</strong> ${this.currentResults.area}</p>
                    <div style="margin-top: 15px;">
                        ${this.formatResearchResult(this.currentResults.result)}
                    </div>
                    <p style="font-size: 0.8em; color: #666; margin-top: 15px;">
                        <em>Pesquisa realizada em ${new Date(this.currentResults.timestamp).toLocaleString('pt-BR')}</em>
                    </p>
                </div>
            `;

            // Inserir no final do documento
            documentContent.insertAdjacentHTML('beforeend', researchSection);
            
            this.showNotification('Resultado inserido no documento!', 'success');
            
            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('researchModal'));
            if (modal) modal.hide();
        } else {
            this.showNotification('Não foi possível encontrar o documento para inserir o resultado.', 'warning');
        }
    }

    saveCurrentResearch() {
        if (!this.currentResults) return;

        const savedResearches = JSON.parse(localStorage.getItem('savedResearches') || '[]');
        savedResearches.push({
            ...this.currentResults,
            savedAt: new Date().toISOString(),
            id: Date.now()
        });

        localStorage.setItem('savedResearches', JSON.stringify(savedResearches));
        this.showNotification('Pesquisa salva com sucesso!', 'success');
    }

    exportResults() {
        if (!this.currentResults) return;

        const exportData = {
            query: this.currentResults.query,
            area: this.currentResults.area,
            result: this.currentResults.result,
            timestamp: this.currentResults.timestamp,
            exportedAt: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `pesquisa-juridica-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Pesquisa exportada!', 'success');
    }

    showHistory() {
        const historyPanel = document.getElementById('researchHistoryPanel');
        const historyList = document.getElementById('historyList');
        
        if (this.searchHistory.length === 0) {
            historyList.innerHTML = '<p class="text-muted">Nenhuma pesquisa realizada ainda.</p>';
        } else {
            historyList.innerHTML = this.searchHistory.map(item => `
                <div class="card bg-dark border-secondary mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${item.query}</strong>
                                <small class="text-muted d-block">${item.area} - ${new Date(item.timestamp).toLocaleString('pt-BR')}</small>
                            </div>
                            <button class="btn btn-sm btn-outline-primary" onclick="legalResearch.repeatSearch('${item.query}', '${item.area}')">
                                <i class="bi bi-arrow-repeat"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        historyPanel.classList.toggle('d-none');
    }

    repeatSearch(query, area) {
        document.getElementById('researchQuery').value = query;
        document.getElementById('researchArea').value = area;
        document.getElementById('researchHistoryPanel').classList.add('d-none');
        this.executeSearch();
    }

    addToHistory(query, area, timestamp) {
        this.searchHistory.unshift({ query, area, timestamp });
        
        // Manter apenas os últimos 20 itens
        if (this.searchHistory.length > 20) {
            this.searchHistory = this.searchHistory.slice(0, 20);
        }
        
        this.saveSearchHistory();
    }

    loadSearchHistory() {
        try {
            return JSON.parse(localStorage.getItem('researchHistory') || '[]');
        } catch {
            return [];
        }
    }

    saveSearchHistory() {
        localStorage.setItem('researchHistory', JSON.stringify(this.searchHistory));
    }

    clearForm() {
        document.getElementById('researchQuery').value = '';
        document.getElementById('researchArea').value = 'Geral';
        this.hideResults();
        document.getElementById('researchHistoryPanel').classList.add('d-none');
    }

    showLoading(show) {
        const loading = document.getElementById('researchLoading');
        if (show) {
            loading.classList.remove('d-none');
        } else {
            loading.classList.add('d-none');
        }
    }

    showResults() {
        document.getElementById('researchResults').classList.remove('d-none');
    }

    hideResults() {
        document.getElementById('researchResults').classList.add('d-none');
    }

    showNotification(message, type = 'info') {
        // Criar toast notification
        const toastHTML = `
            <div class="toast-container position-fixed top-0 end-0 p-3">
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} text-white">
                        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                        <strong class="me-auto">Pesquisa Jurídica</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', toastHTML);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            const toastElements = document.querySelectorAll('.toast-container');
            toastElements.forEach(toast => toast.remove());
        }, 3000);
    }
}

// Inicializar sistema quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.legalResearch = new LegalResearchSystem();
});