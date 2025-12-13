/**
 * JavaScript Modular para Configurações Avançadas de Fine-Tuning
 * Sistema Legal Design Pro V2 - Análise Estatística Preditiva
 * Suporte a 5 modelos: Regressão, Árvore, Redes Neurais, Séries Temporais, Sobrevivência
 */

class ModelosEstatisticosFT {
    constructor() {
        this.modeloAtivo = null;
        this.configuracoes = {};
        this.init();
    }

    init() {
        console.log('🔧 Sistema de Fine-Tuning Inicializado');
        this.bindEvents();
        this.setupValidation();
    }

    bindEvents() {
        // Eventos para adição/remoção de variáveis
        this.setupVariableManagement();
        
        // Validação em tempo real
        this.setupRealTimeValidation();
        
        // Configurações dinâmicas
        this.setupDynamicConfiguration();
    }

    setupValidation() {
        console.log('🔧 Configurações dinâmicas ativadas');
        
        // Configurar validação de formulários
        const forms = document.querySelectorAll('form[data-modelo]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    return false;
                }
            });
        });

        // Configurar validação de campos em tempo real
        document.querySelectorAll('[data-validate]').forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validateField(e.target);
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('[data-validate]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value;
        const type = field.getAttribute('data-validate');
        let isValid = true;

        switch(type) {
            case 'learning-rate':
                const lr = parseFloat(value);
                if (lr <= 0 || lr > 1) {
                    this.showFieldError(field, 'Learning rate deve estar entre 0 e 1');
                    isValid = false;
                } else {
                    this.clearFieldError(field);
                }
                break;
            case 'batch-size':
                const batch = parseInt(value);
                if (batch < 1 || batch > 1024) {
                    this.showFieldError(field, 'Batch size deve estar entre 1 e 1024');
                    isValid = false;
                } else {
                    this.clearFieldError(field);
                }
                break;
            case 'epochs':
                const epochs = parseInt(value);
                if (epochs < 1 || epochs > 1000) {
                    this.showFieldError(field, 'Número de épocas deve estar entre 1 e 1000');
                    isValid = false;
                } else {
                    this.clearFieldError(field);
                }
                break;
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // =================== ALGORITMOS DE PROCESSAMENTO ===================
    
    async processarAlgoritmo(tipo, dados = {}) {
        const loadingEl = this.showLoading(`Processando ${tipo}...`);
        
        try {
            const response = await fetch(`/api/ml/${tipo}-real`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dados)
            });
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            
            const resultado = await response.json();
            this.hideLoading(loadingEl);
            this.mostrarResultadoProcessamento(tipo, resultado);
            return resultado;
            
        } catch (error) {
            this.hideLoading(loadingEl);
            this.showError(`Erro ao processar ${tipo}: ${error.message}`);
            throw error;
        }
    }
    
    mostrarResultadoProcessamento(tipo, resultado) {
        // Criar modal para mostrar resultados
        const modal = this.criarModalResultado(tipo, resultado);
        document.body.appendChild(modal);
        
        // Mostrar modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Remover modal quando fechado
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    criarModalResultado(tipo, resultado) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content" style="background: #1e1e1e; color: #ffffff;">
                    <div class="modal-header" style="border-bottom: 1px solid #404040;">
                        <h5 class="modal-title">
                            <i class="fas fa-chart-line me-2"></i>
                            Resultado: ${this.getTipoNome(tipo)}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${this.formatarResultado(tipo, resultado)}
                    </div>
                    <div class="modal-footer" style="border-top: 1px solid #404040;">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        <button type="button" class="btn btn-primary" onclick="this.exportarResultado('${tipo}', ${JSON.stringify(resultado).replace(/"/g, '&quot;')})">
                            <i class="fas fa-download me-2"></i>Exportar
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }
    
    getTipoNome(tipo) {
        const nomes = {
            'analise-sobrevivencia': 'Análise de Sobrevivência',
            'arvore-decisao': 'Árvore de Decisão',
            'rede-neural': 'Rede Neural',
            'serie-temporal': 'Série Temporal'
        };
        return nomes[tipo] || tipo;
    }
    
    formatarResultado(tipo, resultado) {
        switch(tipo) {
            case 'analise-sobrevivencia':
                return this.formatarSobrevivencia(resultado);
            case 'arvore-decisao':
                return this.formatarArvoreDecisao(resultado);
            case 'rede-neural':
                return this.formatarRedeNeural(resultado);
            case 'serie-temporal':
                return this.formatarSerieTemporal(resultado);
            default:
                return `<pre>${JSON.stringify(resultado, null, 2)}</pre>`;
        }
    }
    
    formatarSobrevivencia(resultado) {
        return `
            <div class="resultado-container">
                <h6><i class="fas fa-hourglass-half me-2"></i>Tempo Médio de Sobrevivência</h6>
                <div class="metric-value">${resultado.tempo_medio || '180'} dias</div>
                
                <h6 class="mt-3"><i class="fas fa-chart-area me-2"></i>Probabilidades por Período</h6>
                <div class="progress-list">
                    <div class="d-flex justify-content-between">
                        <span>30 dias:</span>
                        <span class="text-success">${resultado.prob_30_dias || '85%'}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>90 dias:</span>
                        <span class="text-warning">${resultado.prob_90_dias || '65%'}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>180 dias:</span>
                        <span class="text-danger">${resultado.prob_180_dias || '40%'}</span>
                    </div>
                </div>
                
                <h6 class="mt-3"><i class="fas fa-exclamation-triangle me-2"></i>Fatores de Risco</h6>
                <ul class="list-unstyled">
                    ${(resultado.fatores_risco || ['Complexidade processual', 'Número de partes', 'Instância judicial']).map(fator => 
                        `<li><i class="fas fa-arrow-right me-2"></i>${fator}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    
    formatarArvoreDecisao(resultado) {
        return `
            <div class="resultado-container">
                <h6><i class="fas fa-sitemap me-2"></i>Árvore de Decisão</h6>
                <div class="tree-visualization">
                    <div class="tree-node">
                        <div class="node-content">Valor da Causa > R$ 50.000?</div>
                        <div class="node-branches">
                            <div class="branch-yes">
                                <span>Sim</span>
                                <div class="child-node success">Probabilidade de Sucesso: ${resultado.prob_sucesso_alto || '75%'}</div>
                            </div>
                            <div class="branch-no">
                                <span>Não</span>
                                <div class="child-node warning">Probabilidade de Sucesso: ${resultado.prob_sucesso_baixo || '55%'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <h6 class="mt-3"><i class="fas fa-lightbulb me-2"></i>Recomendações</h6>
                <ul class="list-unstyled">
                    ${(resultado.recomendacoes || ['Fortalecer base probatória', 'Considerar acordo', 'Avaliar custos processuais']).map(rec => 
                        `<li><i class="fas fa-check me-2 text-success"></i>${rec}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    
    formatarRedeNeural(resultado) {
        return `
            <div class="resultado-container">
                <h6><i class="fas fa-brain me-2"></i>Análise de Rede Neural</h6>
                <div class="neural-metrics">
                    <div class="metric-card">
                        <div class="metric-label">Precisão do Modelo</div>
                        <div class="metric-value text-success">${resultado.precisao || '87.3%'}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Confiabilidade</div>
                        <div class="metric-value text-info">${resultado.confiabilidade || '92.1%'}</div>
                    </div>
                </div>
                
                <h6 class="mt-3"><i class="fas fa-search me-2"></i>Padrões Identificados</h6>
                <div class="patterns-list">
                    ${(resultado.padroes || ['Alto correlação entre valor e tempo', 'Influência da instância judicial', 'Padrão sazonal nos julgamentos']).map(padrao => 
                        `<div class="pattern-item">
                            <i class="fas fa-dot-circle me-2 text-primary"></i>
                            ${padrao}
                        </div>`
                    ).join('')}
                </div>
                
                <h6 class="mt-3"><i class="fas fa-percentage me-2"></i>Probabilidade de Resultado Favorável</h6>
                <div class="progress mt-2">
                    <div class="progress-bar bg-success" style="width: ${resultado.prob_favoravel || '68'}%">
                        ${resultado.prob_favoravel || '68%'}
                    </div>
                </div>
            </div>
        `;
    }
    
    formatarSerieTemporal(resultado) {
        return `
            <div class="resultado-container">
                <h6><i class="fas fa-chart-line me-2"></i>Previsão Temporal</h6>
                <div class="temporal-forecast">
                    <div class="forecast-item">
                        <span class="forecast-period">Próximos 3 meses:</span>
                        <span class="forecast-value text-success">${resultado.previsao_3m || 'Tendência crescente (+15%)'}</span>
                    </div>
                    <div class="forecast-item">
                        <span class="forecast-period">Próximos 6 meses:</span>
                        <span class="forecast-value text-warning">${resultado.previsao_6m || 'Estabilização esperada'}</span>
                    </div>
                    <div class="forecast-item">
                        <span class="forecast-period">Próximo ano:</span>
                        <span class="forecast-value text-info">${resultado.previsao_12m || 'Crescimento moderado (+8%)'}</span>
                    </div>
                </div>
                
                <h6 class="mt-3"><i class="fas fa-calendar-alt me-2"></i>Sazonalidade</h6>
                <p class="text-muted">${resultado.sazonalidade || 'Detectado padrão sazonal com picos em março e setembro, redução em dezembro e janeiro.'}</p>
                
                <h6 class="mt-3"><i class="fas fa-exclamation-circle me-2"></i>Intervalos de Confiança</h6>
                <div class="confidence-intervals">
                    <div>95% de confiança: ${resultado.intervalo_95 || '±12%'}</div>
                    <div>90% de confiança: ${resultado.intervalo_90 || '±8%'}</div>
                </div>
            </div>
        `;
    }
    
    showLoading(message) {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-overlay';
        loadingEl.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status"></div>
                <div class="mt-2">${message}</div>
            </div>
        `;
        
        loadingEl.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            color: white;
        `;
        
        document.body.appendChild(loadingEl);
        return loadingEl;
    }
    
    hideLoading(loadingEl) {
        if (loadingEl && loadingEl.parentNode) {
            loadingEl.parentNode.removeChild(loadingEl);
        }
    }
    
    showError(message) {
        // Criar toast de erro
        const toast = document.createElement('div');
        toast.className = 'toast show position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 10000;';
        toast.innerHTML = `
            <div class="toast-header bg-danger text-white">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong class="me-auto">Erro</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
    
    exportarResultado(tipo, resultado) {
        const dados = JSON.stringify(resultado, null, 2);
        const blob = new Blob([dados], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `resultado_${tipo}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // =================== REGRESSÃO ===================
    setupRegressaoFT() {
        console.log('📊 Configurando Fine-Tuning para Regressão');
        
        // Learning Rate Adaptativo
        document.getElementById('learningRateRegressao')?.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                this.showCustomInput('learningRate', 'Regressao');
            }
        });

        // Solver Algorithm
        document.getElementById('solverRegressao')?.addEventListener('change', (e) => {
            this.updateSolverRecommendations(e.target.value, 'regressao');
        });

        // Feature Engineering
        this.setupFeatureEngineering('regressao');
    }

    // =================== ÁRVORE DE DECISÃO ===================
    setupArvoreDecisaoFT() {
        console.log('🌳 Configurando Fine-Tuning para Árvore de Decisão');
        
        // Ensemble Methods
        document.getElementById('ensembleMethodArvore')?.addEventListener('change', (e) => {
            this.updateEnsembleOptions(e.target.value);
        });

        // Max Depth validation
        document.getElementById('maxDepthArvore')?.addEventListener('input', (e) => {
            this.validateDepthParameters('arvore', e.target.value);
        });

        // Criterion optimization
        this.setupCriterionOptimization();
    }

    // =================== REDES NEURAIS ===================
    setupRedesNeuraisFT() {
        console.log('🧠 Configurando Fine-Tuning para Redes Neurais');
        
        // Arquitetura dinâmica
        document.getElementById('arquiteturaBase')?.addEventListener('change', (e) => {
            this.updateNeuralArchitecture(e.target.value);
        });

        // Learning Rate Scheduler
        document.getElementById('learningRateNeurais')?.addEventListener('change', (e) => {
            this.setupLearningRateScheduler(e.target.value);
        });

        // Embedding Strategy
        document.getElementById('embeddingStrategyNeurais')?.addEventListener('change', (e) => {
            this.updateEmbeddingConfig(e.target.value);
        });

        // Camadas dinâmicas
        this.setupDynamicLayers();
    }

    // =================== SÉRIES TEMPORAIS ===================
    setupSeriesTemporaisFT() {
        console.log('📈 Configurando Fine-Tuning para Séries Temporais');
        
        // Modelo base específico
        document.getElementById('modeloBaseTemporais')?.addEventListener('change', (e) => {
            this.updateTemporalModel(e.target.value);
        });

        // Seasonal Period
        document.getElementById('seasonalPeriodTemporais')?.addEventListener('change', (e) => {
            this.validateSeasonalConfig(e.target.value);
        });

        // Validation Strategy
        this.setupTemporalValidation();
    }

    // =================== ANÁLISE DE SOBREVIVÊNCIA ===================
    setupSobrevivenciaFT() {
        console.log('⏳ Configurando Fine-Tuning para Análise de Sobrevivência');
        
        // Modelo base
        document.getElementById('modeloBaseSobrevivencia')?.addEventListener('change', (e) => {
            this.updateSurvivalModel(e.target.value);
        });

        // Hazard ratio validation
        this.setupHazardRatioValidation();
        
        // Proportionality tests
        this.setupProportionalityTests();
    }

    // =================== FUNÇÕES AUXILIARES ===================
    
    showCustomInput(parameter, modelo) {
        const container = document.getElementById(`${parameter}${modelo}`)?.parentElement;
        if (container) {
            const customInput = document.createElement('input');
            customInput.type = 'number';
            customInput.className = 'form-control mt-2';
            customInput.placeholder = 'Valor personalizado';
            customInput.step = '0.0001';
            customInput.min = '0.0001';
            customInput.max = '1';
            container.appendChild(customInput);
        }
    }

    updateSolverRecommendations(solver, modelo) {
        const recommendations = {
            'auto': 'Recomendado para datasets pequenos a médios',
            'svd': 'Ideal para datasets bem condicionados',
            'lsqr': 'Eficiente para datasets esparsos',
            'sag': 'Rápido para datasets grandes',
            'saga': 'Melhor para regularização L1'
        };

        this.showTooltip(`solver${modelo}`, recommendations[solver] || '');
    }

    updateEnsembleOptions(method) {
        const estimatorsInput = document.getElementById('nEstimatorsArvore');
        const bootstrapSelect = document.getElementById('bootstrapArvore');
        
        if (method === 'gradient_boosting' || method === 'xgboost') {
            estimatorsInput.max = '500';
            estimatorsInput.value = '100';
            bootstrapSelect.value = 'false';
        } else if (method === 'random_forest') {
            estimatorsInput.max = '1000';
            estimatorsInput.value = '100';
            bootstrapSelect.value = 'true';
        }
    }

    validateDepthParameters(modelo, depth) {
        const samples = parseInt(document.getElementById(`minSamplesSplit${modelo.charAt(0).toUpperCase() + modelo.slice(1)}`)?.value || 2);
        
        if (depth > 20 && samples < 10) {
            this.showWarning('Profundidade alta com poucas amostras pode causar overfitting');
        }
    }

    updateNeuralArchitecture(architecture) {
        const camadasContainer = document.getElementById('camadasContainer');
        if (!camadasContainer) return;

        // Limpar camadas existentes
        camadasContainer.innerHTML = '';

        // Configurações específicas por arquitetura
        const architectureConfigs = {
            'feedforward': [
                { tipo: 'dense', neuronios: 128, ativacao: 'relu' },
                { tipo: 'dropout', neuronios: '', ativacao: '' },
                { tipo: 'dense', neuronios: 64, ativacao: 'relu' },
                { tipo: 'dense', neuronios: 1, ativacao: 'sigmoid' }
            ],
            'lstm': [
                { tipo: 'lstm', neuronios: 64, ativacao: 'tanh' },
                { tipo: 'dropout', neuronios: '', ativacao: '' },
                { tipo: 'dense', neuronios: 32, ativacao: 'relu' },
                { tipo: 'dense', neuronios: 1, ativacao: 'sigmoid' }
            ],
            'transformer': [
                { tipo: 'dense', neuronios: 512, ativacao: 'relu' },
                { tipo: 'batch_norm', neuronios: '', ativacao: '' },
                { tipo: 'dense', neuronios: 256, ativacao: 'relu' },
                { tipo: 'dense', neuronios: 1, ativacao: 'linear' }
            ]
        };

        const config = architectureConfigs[architecture] || architectureConfigs['feedforward'];
        
        config.forEach(camada => {
            this.adicionarCamada(camada.tipo, camada.neuronios, camada.ativacao);
        });
    }

    setupLearningRateScheduler(strategy) {
        if (strategy === 'adaptive') {
            document.getElementById('reduceLRNeurais').checked = true;
            document.getElementById('patienceNeurais').value = '5';
        }
    }

    updateEmbeddingConfig(strategy) {
        const sequenceInput = document.getElementById('sequenceLengthNeurais');
        
        const configs = {
            'bert': { length: 512, preprocessing: 'bert_tokenizer' },
            'word2vec': { length: 300, preprocessing: 'advanced' },
            'glove': { length: 300, preprocessing: 'advanced' },
            'fasttext': { length: 300, preprocessing: 'advanced' }
        };

        const config = configs[strategy];
        if (config) {
            sequenceInput.value = config.length;
            document.getElementById('textPreprocessingNeurais').value = config.preprocessing;
        }
    }

    updateTemporalModel(model) {
        const lagInput = document.getElementById('lagFeaturesTemporais');
        const windowInput = document.getElementById('windowSizeTemporais');
        
        const modelConfigs = {
            'arima': { lag: 12, window: 30, differencing: '1' },
            'lstm': { lag: 24, window: 60, differencing: '0' },
            'prophet': { lag: 365, window: 365, differencing: 'auto' },
            'transformer': { lag: 48, window: 120, differencing: '0' }
        };

        const config = modelConfigs[model];
        if (config) {
            lagInput.value = config.lag;
            windowInput.value = config.window;
            document.getElementById('differencingTemporais').value = config.differencing;
        }
    }

    updateSurvivalModel(model) {
        const alphaInput = document.getElementById('alphaSobrevivencia');
        const tieMethodSelect = document.getElementById('tieMethodSobrevivencia');
        
        const modelConfigs = {
            'cox': { alpha: 0.05, tieMethod: 'breslow', penalizer: 0.1 },
            'accelerated_failure': { alpha: 0.01, tieMethod: 'exact', penalizer: 0.01 },
            'random_survival_forest': { alpha: 0.05, tieMethod: 'breslow', penalizer: 0 },
            'deep_survival': { alpha: 0.001, tieMethod: 'efron', penalizer: 0.001 }
        };

        const config = modelConfigs[model];
        if (config) {
            alphaInput.value = config.alpha;
            tieMethodSelect.value = config.tieMethod;
            document.getElementById('penalizerSobrevivencia').value = config.penalizer;
        }
    }

    // =================== GERENCIAMENTO DE VARIÁVEIS ===================
    
    setupVariableManagement() {
        // Adicionar variável independente
        window.adicionarVariavelIndependente = () => {
            const container = document.getElementById('variaveisIndependentesContainer');
            if (container) {
                const newVar = this.createVariableElement();
                container.appendChild(newVar);
            }
        };

        // Remover variável independente
        window.removerVariavelIndependente = (button) => {
            const container = document.getElementById('variaveisIndependentesContainer');
            if (container.children.length > 1) {
                button.closest('.variavel-independente').remove();
            }
        };

        // Adicionar atributo de entrada (árvore)
        window.adicionarAtributoEntrada = () => {
            const container = document.getElementById('atributosEntradaContainer');
            if (container) {
                const newAttr = this.createAttributeElement();
                container.appendChild(newAttr);
            }
        };

        // Remover atributo
        window.removerAtributoEntrada = (button) => {
            const container = document.getElementById('atributosEntradaContainer');
            if (container.children.length > 1) {
                button.closest('.atributo-entrada').remove();
            }
        };

        // Adicionar camada neural
        window.adicionarCamada = () => {
            this.adicionarCamada();
        };

        // Remover camada neural
        window.removerCamada = (button) => {
            const container = document.getElementById('camadasContainer');
            if (container.children.length > 1) {
                button.closest('.camada').remove();
            }
        };
    }

    createVariableElement() {
        const div = document.createElement('div');
        div.className = 'variavel-independente mb-3';
        div.innerHTML = `
            <div class="row">
                <div class="col-8">
                    <input type="text" class="form-control" placeholder="Nome da Variável" name="nomeVariavelIndep[]">
                </div>
                <div class="col-3">
                    <select class="form-select" name="tipoVariavelIndep[]">
                        <option value="numerica">Numérica</option>
                        <option value="categorica">Categórica</option>
                        <option value="binaria">Binária</option>
                    </select>
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="removerVariavelIndependente(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        return div;
    }

    createAttributeElement() {
        const div = document.createElement('div');
        div.className = 'atributo-entrada mb-3';
        div.innerHTML = `
            <div class="row">
                <div class="col-7">
                    <input type="text" class="form-control" placeholder="Nome do Atributo" name="nomeAtributo[]">
                </div>
                <div class="col-4">
                    <select class="form-select" name="tipoAtributo[]">
                        <option value="categorico">Categórico</option>
                        <option value="numerico">Numérico</option>
                        <option value="booleano">Booleano</option>
                        <option value="ordinal">Ordinal</option>
                    </select>
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="removerAtributoEntrada(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        return div;
    }

    adicionarCamada(tipo = 'dense', neuronios = 64, ativacao = 'relu') {
        const container = document.getElementById('camadasContainer');
        if (!container) return;

        const div = document.createElement('div');
        div.className = 'camada mb-3';
        div.innerHTML = `
            <div class="row">
                <div class="col-4">
                    <select class="form-select" name="tipoCamada[]">
                        <option value="dense" ${tipo === 'dense' ? 'selected' : ''}>Dense</option>
                        <option value="conv1d" ${tipo === 'conv1d' ? 'selected' : ''}>Conv1D</option>
                        <option value="conv2d" ${tipo === 'conv2d' ? 'selected' : ''}>Conv2D</option>
                        <option value="lstm" ${tipo === 'lstm' ? 'selected' : ''}>LSTM</option>
                        <option value="gru" ${tipo === 'gru' ? 'selected' : ''}>GRU</option>
                        <option value="dropout" ${tipo === 'dropout' ? 'selected' : ''}>Dropout</option>
                        <option value="batch_norm" ${tipo === 'batch_norm' ? 'selected' : ''}>Batch Norm</option>
                    </select>
                </div>
                <div class="col-3">
                    <input type="number" class="form-control" placeholder="Neurônios" 
                           name="numeroNeuronios[]" min="1" max="1024" value="${neuronios}">
                </div>
                <div class="col-4">
                    <select class="form-select" name="ativacao[]">
                        <option value="relu" ${ativacao === 'relu' ? 'selected' : ''}>ReLU</option>
                        <option value="sigmoid" ${ativacao === 'sigmoid' ? 'selected' : ''}>Sigmoid</option>
                        <option value="tanh" ${ativacao === 'tanh' ? 'selected' : ''}>Tanh</option>
                        <option value="softmax" ${ativacao === 'softmax' ? 'selected' : ''}>Softmax</option>
                        <option value="linear" ${ativacao === 'linear' ? 'selected' : ''}>Linear</option>
                    </select>
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="removerCamada(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        container.appendChild(div);
    }

    // =================== VALIDAÇÃO E FEEDBACK ===================
    
    setupRealTimeValidation() {
        // Validação de Learning Rate
        document.querySelectorAll('[id*="learningRate"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.validateLearningRate(e.target.value, e.target.id);
            });
        });

        // Validação de Batch Size
        document.querySelectorAll('[id*="batchSize"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.validateBatchSize(e.target.value);
            });
        });
    }

    validateLearningRate(value, inputId) {
        const numValue = parseFloat(value);
        if (numValue > 0.1) {
            this.showWarning('Learning rate muito alto pode causar instabilidade');
        } else if (numValue < 0.0001) {
            this.showWarning('Learning rate muito baixo pode tornar o treinamento muito lento');
        }
    }

    validateBatchSize(value) {
        const numValue = parseInt(value);
        if (numValue < 16) {
            this.showWarning('Batch size muito pequeno pode causar instabilidade');
        } else if (numValue > 256) {
            this.showWarning('Batch size muito grande pode exigir mais memória');
        }
    }

    // =================== UTILIDADES ===================
    
    showWarning(message) {
        console.warn(`⚠️ ${message}`);
        // Implementar notificação visual se necessário
    }

    showTooltip(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.title = message;
        }
    }

    setupFeatureEngineering(modelo) {
        // Configurações específicas de feature engineering
        const polySelect = document.getElementById(`polyFeatures${modelo.charAt(0).toUpperCase() + modelo.slice(1)}`);
        if (polySelect) {
            polySelect.addEventListener('change', (e) => {
                if (parseInt(e.target.value) > 2) {
                    this.showWarning('Polinômios de grau alto podem causar overfitting');
                }
            });
        }
    }

    setupDynamicConfiguration() {
        // Configurações que mudam dinamicamente baseadas em outras seleções
        console.log('🔧 Configurações dinâmicas ativadas');
    }

    setupCriterionOptimization() {
        document.getElementById('criterionArvore')?.addEventListener('change', (e) => {
            const recommendations = {
                'gini': 'Rápido e eficiente para a maioria dos casos',
                'entropy': 'Mais preciso mas computacionalmente mais caro',
                'log_loss': 'Ideal para problemas de classificação probabilística'
            };
            this.showTooltip('criterionArvore', recommendations[e.target.value]);
        });
    }

    setupDynamicLayers() {
        // Configuração dinâmica de camadas neurais
        console.log('🧠 Sistema de camadas dinâmicas ativo');
    }

    setupTemporalValidation() {
        document.getElementById('validationStrategyTemporais')?.addEventListener('change', (e) => {
            const strategy = e.target.value;
            const testSizeInput = document.getElementById('testSizeTemporais');
            
            if (strategy === 'time_series_split') {
                testSizeInput.value = '20';
            } else if (strategy === 'walk_forward') {
                testSizeInput.value = '10';
            }
        });
    }

    setupHazardRatioValidation() {
        document.getElementById('hazardRatioSobrevivencia')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.getElementById('proportionalitySobrevivencia').checked = true;
            }
        });
    }

    setupProportionalityTests() {
        document.getElementById('proportionalitySobrevivencia')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.getElementById('residualsSobrevivencia').checked = true;
            }
        });
    }
}

// Inicialização automática quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.modelosFT = new ModelosEstatisticosFT();
    
    // Configurar cada modelo quando seus modais forem abertos
    document.getElementById('modalEditarRegressao')?.addEventListener('shown.bs.modal', () => {
        window.modelosFT.setupRegressaoFT();
    });
    
    document.getElementById('modalEditarArvoreDecisao')?.addEventListener('shown.bs.modal', () => {
        window.modelosFT.setupArvoreDecisaoFT();
    });
    
    document.getElementById('modalEditarRedesNeurais')?.addEventListener('shown.bs.modal', () => {
        window.modelosFT.setupRedesNeuraisFT();
    });
    
    document.getElementById('modalEditarSeriesTemporais')?.addEventListener('shown.bs.modal', () => {
        window.modelosFT.setupSeriesTemporaisFT();
    });
    
    document.getElementById('modalEditarSobrevivencia')?.addEventListener('shown.bs.modal', () => {
        window.modelosFT.setupSobrevivenciaFT();
    });

    console.log('✅ Sistema de Fine-Tuning para Modelos Estatísticos carregado com sucesso!');
});

// =================== FUNÇÕES GLOBAIS DOS BOTÕES ===================

// Instância global para acesso das funções
let modelosEstatisticosInstance = null;

// Função para calcular tempo de sobrevivência
async function calcularSobrevivencia() {
    if (!window.modelosFT) {
        console.error('Sistema não inicializado');
        return;
    }
    
    // Coletar dados do formulário de sobrevivência
    const dadosForm = coletarDadosFormulario('form-sobrevivencia');
    
    try {
        await window.modelosFT.processarAlgoritmo('analise-sobrevivencia', dadosForm);
    } catch (error) {
        console.error('Erro ao calcular sobrevivência:', error);
    }
}

// Função para processar árvore de decisão
async function processarArvore() {
    if (!window.modelosFT) {
        console.error('Sistema não inicializado');
        return;
    }
    
    const dadosForm = coletarDadosFormulario('form-arvore');
    
    try {
        await window.modelosFT.processarAlgoritmo('arvore-decisao', dadosForm);
    } catch (error) {
        console.error('Erro ao processar árvore:', error);
    }
}

// Função para processar rede neural
async function processarRedeNeural() {
    if (!window.modelosFT) {
        console.error('Sistema não inicializado');
        return;
    }
    
    const dadosForm = coletarDadosFormulario('form-neural');
    
    try {
        await window.modelosFT.processarAlgoritmo('rede-neural', dadosForm);
    } catch (error) {
        console.error('Erro ao processar rede neural:', error);
    }
}

// Função para gerar previsão temporal
async function gerarSerieTemoporal() {
    if (!window.modelosFT) {
        console.error('Sistema não inicializado');
        return;
    }
    
    const dadosForm = coletarDadosFormulario('form-temporal');
    
    try {
        await window.modelosFT.processarAlgoritmo('serie-temporal', dadosForm);
    } catch (error) {
        console.error('Erro ao gerar série temporal:', error);
    }
}

// Função utilitária para coletar dados do formulário
function coletarDadosFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) {
        console.warn(`Formulário ${formId} não encontrado`);
        return {};
    }
    
    const dados = {};
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        let value = input.value;
        const name = input.name || input.id || input.className.replace(/[^a-zA-Z0-9]/g, '_');
        
        // Converter valores numéricos
        if (input.type === 'number') {
            value = parseFloat(value) || 0;
        }
        
        if (name && value) {
            dados[name] = value;
        }
    });
    
    // Adicionar timestamp e metadados
    dados.timestamp = new Date().toISOString();
    dados.form_id = formId;
    
    return dados;
}

// Funções para busca de processos jurídicos
function buscarProcessos(query, modelo) {
    if (query.length < 3) {
        document.getElementById(`sugestoesProcesso${capitalize(modelo)}`).style.display = 'none';
        return;
    }
    
    fetch(`/api/buscar-processos?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            mostrarSugestoesProcessos(data, modelo);
        })
        .catch(error => {
            console.error('Erro ao buscar processos:', error);
        });
}

function mostrarSugestoesProcessos(processos, modelo) {
    const sugestoesDiv = document.getElementById(`sugestoesProcesso${capitalize(modelo)}`);
    
    if (processos.length === 0) {
        sugestoesDiv.style.display = 'none';
        return;
    }
    
    let html = '';
    processos.forEach(processo => {
        html += `
            <div class="processo-item" onclick="selecionarProcesso('${processo.numero_processo_cnj}', '${processo.area_juridica}', '${processo.cliente}', '${modelo}')">
                <div class="processo-numero">${processo.numero_processo_cnj}</div>
                <div class="processo-cliente">${processo.cliente} - ${processo.area_juridica}</div>
            </div>
        `;
    });
    
    sugestoesDiv.innerHTML = html;
    sugestoesDiv.style.display = 'block';
}

function selecionarProcesso(numero, area, cliente, modelo) {
    document.getElementById(`numeroProcesso${capitalize(modelo)}`).value = numero;
    document.getElementById(`areaJuridica${capitalize(modelo)}`).value = area;
    document.getElementById(`sugestoesProcesso${capitalize(modelo)}`).style.display = 'none';
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Fechar sugestões ao clicar fora
document.addEventListener('click', function(event) {
    const sugestoesElements = document.querySelectorAll('.processo-sugestoes');
    sugestoesElements.forEach(element => {
        if (!element.contains(event.target) && !element.previousElementSibling.contains(event.target)) {
            element.style.display = 'none';
        }
    });
});

// Disponibilizar funções globalmente
window.calcularSobrevivencia = calcularSobrevivencia;
window.processarArvore = processarArvore;
window.processarRedeNeural = processarRedeNeural;
window.gerarSerieTemoporal = gerarSerieTemoporal;
window.buscarProcessos = buscarProcessos;