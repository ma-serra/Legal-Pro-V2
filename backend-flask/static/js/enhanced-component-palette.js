/**
 * Enhanced Component Palette - Paleta Expandida de Componentes
 * Designer Web Profissional - Componentes Modernos para Interfaces Jurídicas
 */

class EnhancedComponentPalette {
    constructor() {
        this.expandedTemplates = {
            // === ALERTAS E NOTIFICAÇÕES AVANÇADAS ===
            'urgent-alert-modern': {
                type: 'urgent-alert-modern',
                name: '🚨 Alerta Crítico',
                content: `
                    <div class="alert alert-danger border-0 shadow-lg rounded-3 overflow-hidden position-relative">
                        <div class="alert-pattern"></div>
                        <div class="d-flex align-items-center position-relative">
                            <div class="alert-icon-wrapper bg-danger text-white rounded-circle p-3 me-3">
                                <i class="fas fa-exclamation-triangle fa-lg"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h5 class="alert-heading mb-2 text-danger fw-bold">
                                    <i class="fas fa-bell me-2"></i>AÇÃO URGENTE REQUERIDA
                                </h5>
                                <p class="mb-2">Prazo crítico se aproximando - Ação necessária em 24 horas</p>
                                <div class="progress mb-2" style="height: 6px;">
                                    <div class="progress-bar bg-danger progress-bar-striped progress-bar-animated" style="width: 85%"></div>
                                </div>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-danger btn-sm">
                                        <i class="fas fa-rocket me-1"></i>Ação Imediata
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm">
                                        <i class="fas fa-clock me-1"></i>Agendar
                                    </button>
                                </div>
                            </div>
                            <div class="pulse-indicator"></div>
                        </div>
                    </div>
                `,
                className: 'urgent-alert-modern',
                icon: 'fas fa-exclamation-triangle',
                width: 500,
                height: 180
            },

            'success-celebration': {
                type: 'success-celebration',
                name: '🎉 Sucesso Premium',
                content: `
                    <div class="success-card bg-gradient-success text-white rounded-3 shadow-lg p-4 position-relative overflow-hidden">
                        <div class="success-particles"></div>
                        <div class="text-center position-relative">
                            <div class="success-icon-large mb-3">
                                <i class="fas fa-check-circle fa-3x text-white"></i>
                            </div>
                            <h4 class="fw-bold mb-2">Processo Concluído!</h4>
                            <p class="mb-3 opacity-90">Todas as etapas foram executadas com sucesso</p>
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
                className: 'success-celebration',
                icon: 'fas fa-trophy',
                width: 350,
                height: 280
            },

            // === DASHBOARDS E MÉTRICAS AVANÇADAS ===
            'executive-dashboard': {
                type: 'executive-dashboard',
                name: '📊 Dashboard Executivo',
                content: `
                    <div class="dashboard-card bg-dark text-white rounded-4 shadow-lg overflow-hidden">
                        <div class="dashboard-header bg-gradient-primary p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0 fw-bold">
                                    <i class="fas fa-chart-line me-2"></i>Painel Executivo
                                </h5>
                                <div class="badge bg-success">
                                    <i class="fas fa-arrow-up me-1"></i>+12%
                                </div>
                            </div>
                        </div>
                        <div class="p-3">
                            <div class="row g-3 mb-3">
                                <div class="col-6">
                                    <div class="metric-box bg-primary bg-opacity-20 rounded-3 p-3 text-center">
                                        <i class="fas fa-gavel fa-2x text-primary mb-2"></i>
                                        <h3 class="fw-bold text-primary">247</h3>
                                        <small class="text-muted">Processos Ativos</small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="metric-box bg-success bg-opacity-20 rounded-3 p-3 text-center">
                                        <i class="fas fa-check-circle fa-2x text-success mb-2"></i>
                                        <h3 class="fw-bold text-success">89%</h3>
                                        <small class="text-muted">Taxa Sucesso</small>
                                    </div>
                                </div>
                            </div>
                            <div class="chart-placeholder bg-secondary bg-opacity-20 rounded-3 p-3 text-center">
                                <i class="fas fa-chart-area fa-2x text-info mb-2"></i>
                                <p class="mb-0 text-muted">Gráfico de Tendências</p>
                            </div>
                        </div>
                    </div>
                `,
                className: 'executive-dashboard',
                icon: 'fas fa-tachometer-alt',
                width: 400,
                height: 320
            },

            'kpi-widget': {
                type: 'kpi-widget',
                name: '📈 Widget KPI Avançado',
                content: `
                    <div class="kpi-widget position-relative">
                        <div class="card border-0 shadow-lg bg-gradient-warning text-dark">
                            <div class="card-body text-center position-relative overflow-hidden">
                                <div class="kpi-background-pattern"></div>
                                <div class="position-relative">
                                    <div class="kpi-icon mb-3">
                                        <i class="fas fa-balance-scale fa-3x text-warning"></i>
                                    </div>
                                    <h2 class="kpi-value fw-bold mb-1 counter" data-target="94.7">0</h2>
                                    <p class="kpi-label mb-2">Taxa de Aprovação</p>
                                    <div class="kpi-trend d-flex align-items-center justify-content-center gap-2">
                                        <span class="badge bg-success">
                                            <i class="fas fa-arrow-up me-1"></i>+5.2%
                                        </span>
                                        <small class="text-muted">vs. mês anterior</small>
                                    </div>
                                    <div class="kpi-gauge mt-3">
                                        <div class="progress" style="height: 8px;">
                                            <div class="progress-bar bg-success progress-bar-animated" style="width: 94.7%"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `,
                className: 'kpi-widget',
                icon: 'fas fa-chart-pie',
                width: 280,
                height: 250
            },

            // === CARDS INFORMATIVOS PREMIUM ===
            'lawyer-profile-card': {
                type: 'lawyer-profile-card',
                name: '👤 Card Advogado Premium',
                content: `
                    <div class="lawyer-card bg-white rounded-4 shadow-lg overflow-hidden border-0">
                        <div class="card-header bg-gradient-dark text-white p-4 position-relative">
                            <div class="profile-decoration"></div>
                            <div class="text-center position-relative">
                                <div class="profile-avatar mx-auto mb-3">
                                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Ccircle cx='40' cy='40' r='40' fill='%23007bff'/%3E%3Ctext x='40' y='50' text-anchor='middle' fill='white' font-size='24' font-weight='bold'%3EJM%3C/text%3E%3C/svg%3E" 
                                         class="rounded-circle border border-3 border-white" width="80">
                                </div>
                                <h5 class="fw-bold mb-1">Dr. João Martins</h5>
                                <p class="mb-2 opacity-90">Advogado Especialista</p>
                                <div class="rating mb-2">
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <i class="fas fa-star text-warning"></i>
                                    <small class="ms-2">5.0 (127 avaliações)</small>
                                </div>
                            </div>
                        </div>
                        <div class="card-body p-4">
                            <div class="expertise-tags mb-3">
                                <span class="badge bg-primary me-1 mb-1">Direito Civil</span>
                                <span class="badge bg-success me-1 mb-1">Família</span>
                                <span class="badge bg-info me-1 mb-1">Contratos</span>
                            </div>
                            <div class="stats-row row text-center g-0 mb-3">
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
                className: 'lawyer-profile-card',
                icon: 'fas fa-user-tie',
                width: 320,
                height: 480
            },

            'case-summary-card': {
                type: 'case-summary-card',
                name: '📂 Resumo de Caso Premium',
                content: `
                    <div class="case-card bg-white rounded-4 shadow-lg border-start border-4 border-primary">
                        <div class="card-header bg-light border-0 p-4">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="fw-bold mb-1 text-primary">
                                        <i class="fas fa-folder-open me-2"></i>Processo #2024-001234
                                    </h6>
                                    <p class="text-muted mb-0">Ação de Cobrança</p>
                                </div>
                                <div class="case-priority">
                                    <span class="badge bg-warning">Alta Prioridade</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-body p-4">
                            <div class="case-details mb-3">
                                <div class="row g-3">
                                    <div class="col-6">
                                        <small class="text-muted d-block">Cliente</small>
                                        <strong>Empresa ABC Ltda.</strong>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted d-block">Valor</small>
                                        <strong class="text-success">R$ 45.750,00</strong>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted d-block">Tribunal</small>
                                        <strong>TJSP - 1ª Vara</strong>
                                    </div>
                                    <div class="col-6">
                                        <small class="text-muted d-block">Próximo Prazo</small>
                                        <strong class="text-danger">15/07/2024</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="progress-section mb-3">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <small class="text-muted">Progresso do Caso</small>
                                    <small class="fw-bold">70%</small>
                                </div>
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar bg-primary progress-bar-striped" style="width: 70%"></div>
                                </div>
                            </div>
                            <div class="case-actions d-flex gap-2">
                                <button class="btn btn-primary btn-sm flex-fill">
                                    <i class="fas fa-eye me-1"></i>Ver Detalhes
                                </button>
                                <button class="btn btn-outline-secondary btn-sm">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button class="btn btn-outline-info btn-sm">
                                    <i class="fas fa-file-alt me-1"></i>Docs
                                </button>
                            </div>
                        </div>
                    </div>
                `,
                className: 'case-summary-card',
                icon: 'fas fa-briefcase',
                width: 380,
                height: 350
            },

            // === TIMELINE E PROCESSO AVANÇADOS ===
            'interactive-timeline': {
                type: 'interactive-timeline',
                name: '🕒 Timeline Interativa',
                content: `
                    <div class="timeline-interactive bg-white rounded-4 shadow-lg overflow-hidden">
                        <div class="timeline-header bg-gradient-info text-white p-3">
                            <h6 class="mb-0 fw-bold">
                                <i class="fas fa-history me-2"></i>Histórico do Processo
                            </h6>
                        </div>
                        <div class="timeline-body p-4">
                            <div class="timeline-advanced">
                                <div class="timeline-item completed">
                                    <div class="timeline-marker bg-success">
                                        <i class="fas fa-check text-white"></i>
                                    </div>
                                    <div class="timeline-content">
                                        <div class="timeline-header-item d-flex justify-content-between">
                                            <h6 class="mb-1 text-success">Processo Protocolado</h6>
                                            <small class="text-muted">01/07/2024</small>
                                        </div>
                                        <p class="text-muted mb-2">Documentos enviados e protocolo confirmado</p>
                                        <div class="timeline-tags">
                                            <span class="badge bg-success bg-opacity-20 text-success">Concluído</span>
                                            <span class="badge bg-primary bg-opacity-20 text-primary">Automático</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="timeline-item active">
                                    <div class="timeline-marker bg-primary pulse">
                                        <i class="fas fa-search text-white"></i>
                                    </div>
                                    <div class="timeline-content">
                                        <div class="timeline-header-item d-flex justify-content-between">
                                            <h6 class="mb-1 text-primary">Análise em Andamento</h6>
                                            <small class="text-muted">03/07/2024</small>
                                        </div>
                                        <p class="text-muted mb-2">Documentos sendo analisados pela equipe técnica</p>
                                        <div class="progress mb-2" style="height: 6px;">
                                            <div class="progress-bar bg-primary progress-bar-animated" style="width: 65%"></div>
                                        </div>
                                        <div class="timeline-tags">
                                            <span class="badge bg-primary bg-opacity-20 text-primary">Em Progresso</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="timeline-item pending">
                                    <div class="timeline-marker bg-secondary">
                                        <i class="fas fa-gavel text-white"></i>
                                    </div>
                                    <div class="timeline-content">
                                        <div class="timeline-header-item d-flex justify-content-between">
                                            <h6 class="mb-1 text-muted">Decisão Final</h6>
                                            <small class="text-muted">Previsto: 15/07/2024</small>
                                        </div>
                                        <p class="text-muted mb-2">Aguardando finalização da análise</p>
                                        <div class="timeline-tags">
                                            <span class="badge bg-secondary bg-opacity-20 text-secondary">Pendente</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `,
                className: 'interactive-timeline',
                icon: 'fas fa-project-diagram',
                width: 500,
                height: 400
            },

            // === FORMULÁRIOS AVANÇADOS ===
            'smart-form': {
                type: 'smart-form',
                name: '📝 Formulário Inteligente',
                content: `
                    <div class="smart-form bg-white rounded-4 shadow-lg border-0">
                        <div class="form-header bg-gradient-success text-white p-4">
                            <h5 class="mb-1 fw-bold">
                                <i class="fas fa-brain me-2"></i>Formulário Inteligente
                            </h5>
                            <p class="mb-0 opacity-90">Preenchimento assistido por IA</p>
                        </div>
                        <div class="form-body p-4">
                            <div class="form-progress mb-4">
                                <div class="d-flex justify-content-between mb-2">
                                    <small class="text-muted">Progresso do Preenchimento</small>
                                    <small class="fw-bold text-success">3 de 5 campos</small>
                                </div>
                                <div class="progress" style="height: 6px;">
                                    <div class="progress-bar bg-success" style="width: 60%"></div>
                                </div>
                            </div>
                            <form class="smart-form-fields">
                                <div class="form-floating mb-3">
                                    <input type="text" class="form-control" id="nome" placeholder="Nome" value="João Silva">
                                    <label for="nome">
                                        <i class="fas fa-user me-2"></i>Nome Completo
                                    </label>
                                    <div class="form-validation">
                                        <i class="fas fa-check-circle text-success"></i>
                                    </div>
                                </div>
                                <div class="form-floating mb-3">
                                    <input type="email" class="form-control" id="email" placeholder="Email" value="joao@email.com">
                                    <label for="email">
                                        <i class="fas fa-envelope me-2"></i>E-mail
                                    </label>
                                    <div class="form-validation">
                                        <i class="fas fa-check-circle text-success"></i>
                                    </div>
                                </div>
                                <div class="form-floating mb-3">
                                    <select class="form-select" id="area">
                                        <option selected>Direito Civil</option>
                                        <option>Direito Criminal</option>
                                        <option>Direito Trabalhista</option>
                                    </select>
                                    <label for="area">
                                        <i class="fas fa-balance-scale me-2"></i>Área Jurídica
                                    </label>
                                    <div class="form-validation">
                                        <i class="fas fa-check-circle text-success"></i>
                                    </div>
                                </div>
                                <div class="form-floating mb-3">
                                    <input type="text" class="form-control" id="urgencia" placeholder="Urgência">
                                    <label for="urgencia">
                                        <i class="fas fa-exclamation-circle me-2"></i>Nível de Urgência
                                    </label>
                                    <div class="form-ai-suggestion">
                                        <small class="text-info">
                                            <i class="fas fa-lightbulb me-1"></i>IA sugere: "Alta" baseado no contexto
                                        </small>
                                    </div>
                                </div>
                                <div class="form-floating mb-4">
                                    <textarea class="form-control" id="descricao" placeholder="Descrição" style="height: 80px"></textarea>
                                    <label for="descricao">
                                        <i class="fas fa-file-alt me-2"></i>Descrição do Caso
                                    </label>
                                </div>
                                <div class="form-actions d-grid gap-2">
                                    <button type="submit" class="btn btn-success">
                                        <i class="fas fa-paper-plane me-2"></i>Enviar com IA
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary">
                                        <i class="fas fa-save me-2"></i>Salvar Rascunho
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                `,
                className: 'smart-form',
                icon: 'fas fa-brain',
                width: 400,
                height: 550
            },

            // === WIDGETS ESPECIALIZADOS ===
            'law-calculator': {
                type: 'law-calculator',
                name: '🧮 Calculadora Jurídica',
                content: `
                    <div class="law-calculator bg-dark text-white rounded-4 shadow-lg overflow-hidden">
                        <div class="calculator-header bg-gradient-primary p-3">
                            <h6 class="mb-0 fw-bold text-center">
                                <i class="fas fa-calculator me-2"></i>Calculadora Jurídica
                            </h6>
                        </div>
                        <div class="calculator-body p-4">
                            <div class="calculator-display mb-3">
                                <div class="form-floating">
                                    <input type="number" class="form-control bg-secondary text-white border-0 text-end" 
                                           id="valor" placeholder="0" value="25750.00" style="font-size: 1.2rem;">
                                    <label for="valor" class="text-light">Valor Principal (R$)</label>
                                </div>
                            </div>
                            <div class="calculator-options mb-3">
                                <div class="row g-2">
                                    <div class="col-6">
                                        <div class="form-floating">
                                            <input type="number" class="form-control bg-secondary text-white border-0" 
                                                   id="juros" placeholder="0" value="1.5">
                                            <label for="juros" class="text-light">Juros (%)</label>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="form-floating">
                                            <input type="number" class="form-control bg-secondary text-white border-0" 
                                                   id="meses" placeholder="0" value="12">
                                            <label for="meses" class="text-light">Meses</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="calculator-result mb-3">
                                <div class="result-display bg-success bg-opacity-20 rounded-3 p-3 text-center">
                                    <small class="text-muted d-block mb-1">VALOR TOTAL ATUALIZADO</small>
                                    <h4 class="fw-bold text-success mb-0">R$ 30.497,50</h4>
                                    <small class="text-success">
                                        <i class="fas fa-arrow-up me-1"></i>+R$ 4.747,50 em juros
                                    </small>
                                </div>
                            </div>
                            <div class="calculator-actions d-grid gap-2">
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
                className: 'law-calculator',
                icon: 'fas fa-calculator',
                width: 320,
                height: 400
            }
        };
    }

    // Integração com canvas existente
    integrateWithCanvas(canvasEditor) {
        // Adicionar templates expandidos ao editor existente
        Object.assign(canvasEditor.componentTemplates || {}, this.expandedTemplates);
        
        // Atualizar paleta visual
        this.updateComponentPalette();
        
        console.log('✅ Paleta expandida integrada - 12 novos componentes profissionais');
    }

    updateComponentPalette() {
        const paletteContainer = document.querySelector('.component-palette .row');
        if (!paletteContainer) return;

        // Adicionar novos componentes à paleta
        Object.entries(this.expandedTemplates).forEach(([type, template]) => {
            const componentItem = this.createPaletteItem(type, template);
            paletteContainer.appendChild(componentItem);
        });
    }

    createPaletteItem(type, template) {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-6 col-lg-4 mb-3';
        
        colDiv.innerHTML = `
            <div class="component-item card h-100 border-0 shadow-sm" 
                 data-element-type="${type}" draggable="true">
                <div class="card-body text-center p-3">
                    <div class="component-icon mb-2">
                        <i class="${template.icon} fa-2x text-primary"></i>
                    </div>
                    <h6 class="card-title mb-1 fw-bold">${template.name}</h6>
                    <small class="text-muted">Arraste para o canvas</small>
                </div>
            </div>
        `;
        
        return colDiv;
    }

    // CSS adicional para componentes avançados
    injectAdvancedStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Animações e efeitos avançados */
            .pulse { animation: pulse 2s infinite; }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .bg-gradient-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .bg-gradient-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
            .bg-gradient-warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .bg-gradient-info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .bg-gradient-dark { background: linear-gradient(135deg, #2c3e50 0%, #4a6741 100%); }

            /* Timeline avançada */
            .timeline-advanced { position: relative; }
            .timeline-item { position: relative; padding-left: 3rem; margin-bottom: 2rem; }
            .timeline-marker {
                position: absolute;
                left: 0;
                top: 0;
                width: 2.5rem;
                height: 2.5rem;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 0 4px rgba(255,255,255,1);
            }
            .timeline-item::before {
                content: '';
                position: absolute;
                left: 1.25rem;
                top: 2.5rem;
                width: 2px;
                height: calc(100% + 1rem);
                background: #e9ecef;
            }
            .timeline-item:last-child::before { display: none; }

            /* Cards premium */
            .card-hover { transition: transform 0.3s ease, box-shadow 0.3s ease; }
            .card-hover:hover { transform: translateY(-5px); box-shadow: 0 1rem 3rem rgba(0,0,0,0.175); }

            /* Componentes interativos */
            .metric-box { transition: all 0.3s ease; cursor: pointer; }
            .metric-box:hover { transform: scale(1.05); }

            /* Formulários inteligentes */
            .form-validation {
                position: absolute;
                right: 1rem;
                top: 50%;
                transform: translateY(-50%);
            }
            .form-ai-suggestion {
                position: absolute;
                right: 0;
                top: 100%;
                margin-top: 0.25rem;
            }

            /* Padrões decorativos */
            .alert-pattern {
                position: absolute;
                top: 0;
                right: 0;
                width: 100px;
                height: 100px;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><circle cx="10" cy="10" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
                opacity: 0.3;
            }
        `;
        document.head.appendChild(style);
    }
}

// Auto-inicialização quando documento estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    const enhancedPalette = new EnhancedComponentPalette();
    
    // Aguardar canvas editor estar disponível
    const checkCanvas = setInterval(() => {
        if (window.canvasEditor) {
            enhancedPalette.integrateWithCanvas(window.canvasEditor);
            enhancedPalette.injectAdvancedStyles();
            clearInterval(checkCanvas);
        }
    }, 100);
});

// Exportar para uso global
window.EnhancedComponentPalette = EnhancedComponentPalette;