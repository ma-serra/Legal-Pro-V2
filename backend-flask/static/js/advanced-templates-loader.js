/**
 * Advanced Templates Loader - Carregador Dinâmico de Templates Avançados
 * Expande o Canvas Editor Pro com componentes profissionais
 */

class AdvancedTemplatesLoader {
    constructor() {
        this.templates = this.getAdvancedTemplates();
        this.init();
    }

    init() {
        // Aguardar canvas editor estar disponível
        const loadTemplates = setInterval(() => {
            if (window.canvasEditor) {
                this.integratewithCanvasEditor();
                clearInterval(loadTemplates);
                console.log('✅ Templates avançados carregados - 20 novos componentes profissionais');
            }
        }, 100);
    }

    integratewithCanvasEditor() {
        // Adicionar métodos de template ao canvas editor
        Object.assign(window.canvasEditor, this.getTemplateMethods());
        
        // Estender função getComponentTemplate
        const originalGetTemplate = window.canvasEditor.getComponentTemplate;
        window.canvasEditor.getComponentTemplate = (type) => {
            return this.templates[type] || originalGetTemplate.call(window.canvasEditor, type);
        };
    }

    getAdvancedTemplates() {
        return {
            // === COMPONENTES PREMIUM ===
            'deadline-alert': {
                type: 'deadline-alert',
                name: 'Alerta de Prazo',
                content: this.getDeadlineAlertTemplate(),
                className: 'deadline-alert-container',
                icon: 'fas fa-clock',
                width: 350,
                height: 150
            },
            'success-celebration': {
                type: 'success-celebration',
                name: 'Sucesso Premium',
                content: this.getSuccessCelebrationTemplate(),
                className: 'success-celebration-container',
                icon: 'fas fa-trophy',
                width: 350,
                height: 280
            },
            'kpi-widget': {
                type: 'kpi-widget',
                name: 'Widget KPI',
                content: this.getKPIWidgetTemplate(),
                className: 'kpi-widget-container',
                icon: 'fas fa-chart-pie',
                width: 280,
                height: 250
            },
            'lawyer-profile-card': {
                type: 'lawyer-profile-card',
                name: 'Card Advogado',
                content: this.getLawyerProfileTemplate(),
                className: 'lawyer-profile-container',
                icon: 'fas fa-user-tie',
                width: 320,
                height: 480
            },

            // === DASHBOARDS & MÉTRICAS ===
            'executive-dashboard': {
                type: 'executive-dashboard',
                name: 'Dashboard Executivo',
                content: this.getExecutiveDashboardTemplate(),
                className: 'executive-dashboard-container',
                icon: 'fas fa-tachometer-alt',
                width: 400,
                height: 320
            },
            'case-summary-card': {
                type: 'case-summary-card',
                name: 'Resumo de Caso',
                content: this.getCaseSummaryTemplate(),
                className: 'case-summary-container',
                icon: 'fas fa-briefcase',
                width: 380,
                height: 350
            },
            'progress-tracker': {
                type: 'progress-tracker',
                name: 'Rastreador de Progresso',
                content: this.getProgressTrackerTemplate(),
                className: 'progress-tracker-container',
                icon: 'fas fa-tasks',
                width: 350,
                height: 200
            },
            'metric-card': {
                type: 'metric-card',
                name: 'Card de Métrica',
                content: this.getMetricCardTemplate(),
                className: 'metric-card-container',
                icon: 'fas fa-chart-line',
                width: 200,
                height: 160
            },

            // === FORMULÁRIOS INTELIGENTES ===
            'smart-form': {
                type: 'smart-form',
                name: 'Formulário Inteligente',
                content: this.getSmartFormTemplate(),
                className: 'smart-form-container',
                icon: 'fas fa-brain',
                width: 400,
                height: 550
            },
            'filter-panel': {
                type: 'filter-panel',
                name: 'Painel de Filtros',
                content: this.getFilterPanelTemplate(),
                className: 'filter-panel-container',
                icon: 'fas fa-filter',
                width: 250,
                height: 300
            },
            'search-widget': {
                type: 'search-widget',
                name: 'Widget de Busca',
                content: this.getSearchWidgetTemplate(),
                className: 'search-widget-container',
                icon: 'fas fa-search',
                width: 350,
                height: 140
            },
            'quick-form': {
                type: 'quick-form',
                name: 'Formulário Rápido',
                content: this.getQuickFormTemplate(),
                className: 'quick-form-container',
                icon: 'fas fa-edit',
                width: 300,
                height: 280
            },

            // === WIDGETS ESPECIALIZADOS ===
            'law-calculator': {
                type: 'law-calculator',
                name: 'Calculadora Jurídica',
                content: this.getLawCalculatorTemplate(),
                className: 'law-calculator-container',
                icon: 'fas fa-calculator',
                width: 320,
                height: 400
            },
            'document-preview': {
                type: 'document-preview',
                name: 'Preview de Documento',
                content: this.getDocumentPreviewTemplate(),
                className: 'document-preview-container',
                icon: 'fas fa-file-alt',
                width: 300,
                height: 220
            },
            'interactive-timeline': {
                type: 'interactive-timeline',
                name: 'Timeline Interativa',
                content: this.getInteractiveTimelineTemplate(),
                className: 'interactive-timeline-container',
                icon: 'fas fa-project-diagram',
                width: 500,
                height: 400
            },
            'contact-list': {
                type: 'contact-list',
                name: 'Lista de Contatos',
                content: this.getContactListTemplate(),
                className: 'contact-list-container',
                icon: 'fas fa-address-book',
                width: 300,
                height: 180
            },

            // === NAVEGAÇÃO & INTERFACE ===
            'tab-navigation': {
                type: 'tab-navigation',
                name: 'Navegação por Abas',
                content: this.getTabNavigationTemplate(),
                className: 'tab-navigation-container',
                icon: 'fas fa-folder-open',
                width: 400,
                height: 150
            },
            'breadcrumb-nav': {
                type: 'breadcrumb-nav',
                name: 'Breadcrumb',
                content: this.getBreadcrumbTemplate(),
                className: 'breadcrumb-container',
                icon: 'fas fa-sitemap',
                width: 500,
                height: 60
            },
            'action-buttons': {
                type: 'action-buttons',
                name: 'Botões de Ação',
                content: this.getActionButtonsTemplate(),
                className: 'action-buttons-container',
                icon: 'fas fa-mouse-pointer',
                width: 200,
                height: 250
            },
            'process-flow': {
                type: 'process-flow',
                name: 'Fluxo de Processo',
                content: this.getProcessFlowTemplate(),
                className: 'process-flow-container',
                icon: 'fas fa-sitemap',
                width: 500,
                height: 180
            }
        };
    }

    getTemplateMethods() {
        return {
            getDeadlineAlertTemplate: () => `
                <div class="card border-danger shadow-sm">
                    <div class="card-header bg-danger text-white d-flex align-items-center">
                        <i class="fas fa-clock me-2"></i>
                        <strong>PRAZO VENCENDO</strong>
                    </div>
                    <div class="card-body">
                        <h6 class="card-title text-danger">15 dias restantes</h6>
                        <p class="card-text">Prazo para contestação expira em 15 dias úteis</p>
                        <div class="progress mb-2" style="height: 6px;">
                            <div class="progress-bar bg-danger" style="width: 25%"></div>
                        </div>
                        <a href="#" class="btn btn-danger btn-sm">Ver Detalhes</a>
                    </div>
                </div>
            `,

            getSuccessCelebrationTemplate: () => `
                <div class="card bg-success text-white shadow-lg">
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-trophy fa-3x"></i>
                        </div>
                        <h4 class="card-title fw-bold">Processo Concluído!</h4>
                        <p class="card-text opacity-90">Todas as etapas foram executadas com sucesso</p>
                        <div class="row text-center mb-3">
                            <div class="col-4">
                                <h5 class="fw-bold">100%</h5>
                                <small>Concluído</small>
                            </div>
                            <div class="col-4">
                                <h5 class="fw-bold">0</h5>
                                <small>Pendências</small>
                            </div>
                            <div class="col-4">
                                <h5 class="fw-bold">15min</h5>
                                <small>Economizados</small>
                            </div>
                        </div>
                        <button class="btn btn-light btn-sm">
                            <i class="fas fa-download me-1"></i>Baixar Relatório
                        </button>
                    </div>
                </div>
            `,

            getKPIWidgetTemplate: () => `
                <div class="card border-0 shadow-lg bg-warning text-dark">
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-balance-scale fa-3x text-warning"></i>
                        </div>
                        <h2 class="fw-bold mb-1">94.7%</h2>
                        <p class="mb-2">Taxa de Aprovação</p>
                        <div class="d-flex align-items-center justify-content-center gap-2 mb-3">
                            <span class="badge bg-success">
                                <i class="fas fa-arrow-up me-1"></i>+5.2%
                            </span>
                            <small class="text-muted">vs. mês anterior</small>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar bg-success" style="width: 94.7%"></div>
                        </div>
                    </div>
                </div>
            `,

            getLawyerProfileTemplate: () => `
                <div class="card shadow-lg border-0">
                    <div class="card-header bg-dark text-white text-center p-4">
                        <div class="mb-3">
                            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Ccircle cx='40' cy='40' r='40' fill='%23007bff'/%3E%3Ctext x='40' y='50' text-anchor='middle' fill='white' font-size='24' font-weight='bold'%3EJM%3C/text%3E%3C/svg%3E" 
                                 class="rounded-circle border border-3 border-white" width="80">
                        </div>
                        <h5 class="fw-bold mb-1">Dr. João Martins</h5>
                        <p class="mb-2 opacity-90">Advogado Especialista</p>
                        <div class="rating">
                            <i class="fas fa-star text-warning"></i>
                            <i class="fas fa-star text-warning"></i>
                            <i class="fas fa-star text-warning"></i>
                            <i class="fas fa-star text-warning"></i>
                            <i class="fas fa-star text-warning"></i>
                            <small class="ms-2">5.0 (127 avaliações)</small>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <span class="badge bg-primary me-1">Direito Civil</span>
                            <span class="badge bg-success me-1">Família</span>
                            <span class="badge bg-info">Contratos</span>
                        </div>
                        <div class="row text-center mb-3">
                            <div class="col-4">
                                <strong class="d-block text-primary">156</strong>
                                <small class="text-muted">Casos</small>
                            </div>
                            <div class="col-4 border-start border-end">
                                <strong class="d-block text-success">12+</strong>
                                <small class="text-muted">Anos</small>
                            </div>
                            <div class="col-4">
                                <strong class="d-block text-warning">OAB</strong>
                                <small class="text-muted">SP 123456</small>
                            </div>
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary">
                                <i class="fas fa-comments me-2"></i>Consultar
                            </button>
                            <button class="btn btn-outline-secondary">
                                <i class="fas fa-user-plus me-2"></i>Seguir
                            </button>
                        </div>
                    </div>
                </div>
            `,

            getExecutiveDashboardTemplate: () => `
                <div class="card bg-dark text-white shadow-lg">
                    <div class="card-header bg-primary p-3">
                        <h5 class="mb-0 fw-bold">
                            <i class="fas fa-chart-line me-2"></i>Painel Executivo
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3 mb-3">
                            <div class="col-6">
                                <div class="bg-primary bg-opacity-20 rounded p-3 text-center">
                                    <i class="fas fa-gavel fa-2x text-primary mb-2"></i>
                                    <h3 class="fw-bold text-primary">247</h3>
                                    <small>Processos Ativos</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="bg-success bg-opacity-20 rounded p-3 text-center">
                                    <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
                                    <h3 class="fw-bold text-success">89%</h3>
                                    <small>Taxa Sucesso</small>
                                </div>
                            </div>
                        </div>
                        <div class="bg-secondary bg-opacity-20 rounded p-3 text-center">
                            <i class="fas fa-chart-area fa-2x text-info mb-2"></i>
                            <p class="mb-0 text-muted">Gráfico de Tendências</p>
                        </div>
                    </div>
                </div>
            `,

            getCaseSummaryTemplate: () => `
                <div class="card shadow-lg border-start border-4 border-primary">
                    <div class="card-header bg-light">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="fw-bold mb-1 text-primary">
                                    <i class="fas fa-folder-open me-2"></i>Processo #2024-001234
                                </h6>
                                <p class="text-muted mb-0">Ação de Cobrança</p>
                            </div>
                            <span class="badge bg-warning">Alta Prioridade</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row g-3 mb-3">
                            <div class="col-6">
                                <small class="text-muted d-block">Cliente</small>
                                <strong>Empresa ABC Ltda.</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted d-block">Valor</small>
                                <strong class="text-success">R$ 45.750,00</strong>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-2">
                                <small class="text-muted">Progresso</small>
                                <small class="fw-bold">70%</small>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-primary" style="width: 70%"></div>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-primary btn-sm flex-fill">
                                <i class="fas fa-eye me-1"></i>Ver Detalhes
                            </button>
                            <button class="btn btn-outline-secondary btn-sm">
                                <i class="fas fa-edit me-1"></i>Editar
                            </button>
                        </div>
                    </div>
                </div>
            `,

            getProgressTrackerTemplate: () => `
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-tasks me-2"></i>Progresso do Processo
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="progress mb-3" style="height: 8px;">
                            <div class="progress-bar bg-success" style="width: 65%"></div>
                        </div>
                        <div class="d-flex justify-content-between small text-muted mb-3">
                            <span>Início</span>
                            <span class="fw-bold text-success">65% Concluído</span>
                            <span>Finalização</span>
                        </div>
                        <div>
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-check-circle text-success me-2"></i>
                                <span>Protocolo realizado</span>
                            </div>
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-spinner fa-spin text-primary me-2"></i>
                                <span>Em análise</span>
                            </div>
                            <div class="d-flex align-items-center text-muted">
                                <i class="far fa-circle me-2"></i>
                                <span>Aguardando decisão</span>
                            </div>
                        </div>
                    </div>
                </div>
            `,

            getMetricCardTemplate: () => `
                <div class="card text-center border-0 shadow-sm">
                    <div class="card-body">
                        <div class="mb-3">
                            <i class="fas fa-chart-line fa-2x text-primary"></i>
                        </div>
                        <h2 class="text-primary mb-1">89.5%</h2>
                        <p class="text-muted mb-2">Taxa de Sucesso</p>
                        <small class="badge bg-success">
                            <i class="fas fa-arrow-up me-1"></i>+5.2%
                        </small>
                    </div>
                </div>
            `,

            getSmartFormTemplate: () => `
                <div class="card shadow-lg border-0">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-1 fw-bold">
                            <i class="fas fa-brain me-2"></i>Formulário Inteligente
                        </h6>
                        <small class="opacity-90">Preenchimento assistido por IA</small>
                    </div>
                    <div class="card-body">
                        <div class="progress mb-3" style="height: 6px;">
                            <div class="progress-bar bg-success" style="width: 60%"></div>
                        </div>
                        <form>
                            <div class="form-floating mb-3">
                                <input type="text" class="form-control" value="João Silva">
                                <label><i class="fas fa-user me-2"></i>Nome Completo</label>
                            </div>
                            <div class="form-floating mb-3">
                                <input type="email" class="form-control" value="joao@email.com">
                                <label><i class="fas fa-envelope me-2"></i>E-mail</label>
                            </div>
                            <div class="form-floating mb-3">
                                <select class="form-select">
                                    <option selected>Direito Civil</option>
                                    <option>Direito Criminal</option>
                                </select>
                                <label><i class="fas fa-balance-scale me-2"></i>Área Jurídica</label>
                            </div>
                            <button type="submit" class="btn btn-success w-100">
                                <i class="fas fa-paper-plane me-2"></i>Enviar com IA
                            </button>
                        </form>
                    </div>
                </div>
            `,

            getFilterPanelTemplate: () => `
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-filter me-2"></i>Filtros Avançados
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Período</label>
                            <div class="row g-2">
                                <div class="col">
                                    <input type="date" class="form-control form-control-sm">
                                </div>
                                <div class="col">
                                    <input type="date" class="form-control form-control-sm">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Status</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" checked>
                                <label class="form-check-label">Ativo</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox">
                                <label class="form-check-label">Pendente</label>
                            </div>
                        </div>
                        <button class="btn btn-info btn-sm w-100">Aplicar Filtros</button>
                    </div>
                </div>
            `,

            getSearchWidgetTemplate: () => `
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-search me-2"></i>Busca Inteligente
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" placeholder="Digite sua consulta...">
                            <button class="btn btn-primary">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                        <div class="d-flex gap-1 flex-wrap">
                            <span class="badge bg-light text-dark">Processo</span>
                            <span class="badge bg-light text-dark">Jurisprudência</span>
                            <span class="badge bg-light text-dark">Legislação</span>
                        </div>
                    </div>
                </div>
            `,

            getQuickFormTemplate: () => `
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-edit me-2"></i>Cadastro Rápido
                        </h6>
                    </div>
                    <div class="card-body">
                        <form>
                            <div class="mb-3">
                                <input type="text" class="form-control" placeholder="Nome completo">
                            </div>
                            <div class="mb-3">
                                <input type="email" class="form-control" placeholder="E-mail">
                            </div>
                            <div class="mb-3">
                                <select class="form-select">
                                    <option>Área Jurídica</option>
                                    <option>Civil</option>
                                    <option>Criminal</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Cadastrar</button>
                        </form>
                    </div>
                </div>
            `,

            getLawCalculatorTemplate: () => `
                <div class="card bg-dark text-white shadow-lg">
                    <div class="card-header bg-primary">
                        <h6 class="mb-0 text-center fw-bold">
                            <i class="fas fa-calculator me-2"></i>Calculadora Jurídica
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="form-floating mb-3">
                            <input type="number" class="form-control bg-secondary text-white border-0" 
                                   value="25750.00" style="font-size: 1.2rem;">
                            <label class="text-light">Valor Principal (R$)</label>
                        </div>
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <div class="form-floating">
                                    <input type="number" class="form-control bg-secondary text-white border-0" 
                                           value="1.5">
                                    <label class="text-light">Juros (%)</label>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="form-floating">
                                    <input type="number" class="form-control bg-secondary text-white border-0" 
                                           value="12">
                                    <label class="text-light">Meses</label>
                                </div>
                            </div>
                        </div>
                        <div class="bg-success bg-opacity-20 rounded p-3 text-center mb-3">
                            <small class="text-muted d-block mb-1">VALOR TOTAL ATUALIZADO</small>
                            <h4 class="fw-bold text-success mb-0">R$ 30.497,50</h4>
                            <small class="text-success">
                                <i class="fas fa-arrow-up me-1"></i>+R$ 4.747,50 em juros
                            </small>
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary">
                                <i class="fas fa-sync me-2"></i>Recalcular
                            </button>
                            <button class="btn btn-outline-light">
                                <i class="fas fa-file-pdf me-2"></i>Gerar Relatório
                            </button>
                        </div>
                    </div>
                </div>
            `,

            getDocumentPreviewTemplate: () => `
                <div class="card border-secondary">
                    <div class="card-header bg-light d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-file-alt me-2"></i>
                            <strong>Documento.pdf</strong>
                        </div>
                        <div class="badge bg-secondary">2.3 MB</div>
                    </div>
                    <div class="card-body text-center py-4">
                        <i class="fas fa-file-pdf fa-3x text-danger mb-3"></i>
                        <h6>Documento Legal</h6>
                        <p class="text-muted mb-3">Visualização disponível</p>
                        <div class="btn-group">
                            <button class="btn btn-outline-primary btn-sm">Visualizar</button>
                            <button class="btn btn-outline-success btn-sm">Download</button>
                        </div>
                    </div>
                </div>
            `,

            getInteractiveTimelineTemplate: () => `
                <div class="card shadow-lg">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0 fw-bold">
                            <i class="fas fa-history me-2"></i>Histórico do Processo
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="timeline-item d-flex mb-3">
                            <div class="timeline-marker bg-success rounded-circle p-2 me-3">
                                <i class="fas fa-check text-white"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1 text-success">Processo Protocolado</h6>
                                <small class="text-muted">01/07/2024 - 09:30</small>
                                <p class="mt-2 mb-0">Documentos submetidos com sucesso</p>
                            </div>
                        </div>
                        <div class="timeline-item d-flex mb-3">
                            <div class="timeline-marker bg-primary rounded-circle p-2 me-3">
                                <i class="fas fa-eye text-white"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1 text-primary">Em Análise</h6>
                                <small class="text-muted">03/07/2024 - 14:20</small>
                                <p class="mt-2 mb-0">Processo em fase de análise técnica</p>
                                <div class="progress mt-2" style="height: 6px;">
                                    <div class="progress-bar bg-primary" style="width: 65%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="timeline-item d-flex">
                            <div class="timeline-marker bg-secondary rounded-circle p-2 me-3">
                                <i class="fas fa-clock text-white"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1 text-muted">Aguardando Decisão</h6>
                                <small class="text-muted">Previsão: 15/07/2024</small>
                                <p class="mt-2 mb-0">Próxima etapa do processo</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,

            getContactListTemplate: () => `
                <div class="card">
                    <div class="card-header bg-dark text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-address-book me-2"></i>Contatos Jurídicos
                        </h6>
                    </div>
                    <div class="card-body p-0">
                        <div class="list-group list-group-flush">
                            <div class="list-group-item d-flex align-items-center">
                                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' fill='%23007bff'/%3E%3Ctext x='20' y='25' text-anchor='middle' fill='white' font-size='16' font-weight='bold'%3EJM%3C/text%3E%3C/svg%3E" 
                                     class="rounded-circle me-3" width="40">
                                <div>
                                    <h6 class="mb-1">João Martins</h6>
                                    <small class="text-muted">Advogado Sênior</small>
                                </div>
                            </div>
                            <div class="list-group-item d-flex align-items-center">
                                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' fill='%23dc3545'/%3E%3Ctext x='20' y='25' text-anchor='middle' fill='white' font-size='16' font-weight='bold'%3EAS%3C/text%3E%3C/svg%3E" 
                                     class="rounded-circle me-3" width="40">
                                <div>
                                    <h6 class="mb-1">Ana Silva</h6>
                                    <small class="text-muted">Consultora</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `,

            getTabNavigationTemplate: () => `
                <div class="card">
                    <ul class="nav nav-tabs card-header-tabs">
                        <li class="nav-item">
                            <a class="nav-link active" href="#">
                                <i class="fas fa-info-circle me-1"></i>Geral
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="fas fa-file-alt me-1"></i>Documentos
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#">
                                <i class="fas fa-history me-1"></i>Histórico
                            </a>
                        </li>
                    </ul>
                    <div class="card-body">
                        <h6>Informações Gerais</h6>
                        <p class="text-muted mb-0">Conteúdo da aba selecionada será exibido aqui.</p>
                    </div>
                </div>
            `,

            getBreadcrumbTemplate: () => `
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb bg-light p-3 rounded shadow-sm mb-0">
                        <li class="breadcrumb-item">
                            <a href="#" class="text-primary">
                                <i class="fas fa-home me-1"></i>Início
                            </a>
                        </li>
                        <li class="breadcrumb-item">
                            <a href="#" class="text-primary">Processos</a>
                        </li>
                        <li class="breadcrumb-item">
                            <a href="#" class="text-primary">Civil</a>
                        </li>
                        <li class="breadcrumb-item active" aria-current="page">
                            Processo #12345
                        </li>
                    </ol>
                </nav>
            `,

            getActionButtonsTemplate: () => `
                <div class="card">
                    <div class="card-body text-center">
                        <h6 class="card-title mb-3">Ações Disponíveis</h6>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary">
                                <i class="fas fa-plus me-2"></i>Novo Processo
                            </button>
                            <button class="btn btn-success">
                                <i class="fas fa-check me-2"></i>Aprovar
                            </button>
                            <button class="btn btn-warning">
                                <i class="fas fa-edit me-2"></i>Editar
                            </button>
                            <button class="btn btn-danger">
                                <i class="fas fa-trash me-2"></i>Excluir
                            </button>
                        </div>
                    </div>
                </div>
            `,

            getProcessFlowTemplate: () => `
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-sitemap me-2"></i>Fluxo do Processo
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="text-center">
                                <div class="bg-success rounded-circle p-3 mb-2 mx-auto" style="width: 60px; height: 60px;">
                                    <i class="fas fa-file-alt text-white"></i>
                                </div>
                                <small class="fw-bold">Protocolo</small>
                            </div>
                            <div class="text-success">→</div>
                            <div class="text-center">
                                <div class="bg-primary rounded-circle p-3 mb-2 mx-auto" style="width: 60px; height: 60px;">
                                    <i class="fas fa-search text-white"></i>
                                </div>
                                <small class="fw-bold">Análise</small>
                            </div>
                            <div class="text-muted">→</div>
                            <div class="text-center">
                                <div class="bg-secondary rounded-circle p-3 mb-2 mx-auto" style="width: 60px; height: 60px;">
                                    <i class="fas fa-gavel text-white"></i>
                                </div>
                                <small class="fw-bold">Decisão</small>
                            </div>
                        </div>
                    </div>
                </div>
            `
        };
    }
}

// Auto-inicialização
document.addEventListener('DOMContentLoaded', () => {
    new AdvancedTemplatesLoader();
});

// Exportar para uso global
window.AdvancedTemplatesLoader = AdvancedTemplatesLoader;