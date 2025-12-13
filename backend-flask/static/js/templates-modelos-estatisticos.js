/**
 * JavaScript Unificado para Templates de Edição de Modelos Estatísticos
 * Legal Design Pro V2 - Sistema de Análise Estatística e Preditiva
 */

// ==================== FUNÇÕES GERAIS ====================

// Função para atualizar parâmetros baseados na área jurídica selecionada
function atualizarParametrosRegressao() {
    const area = document.getElementById('areaJuridicaModeloRegressao')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    
    // Atualizar tipos de análise
    const tipoSelect = document.getElementById('tipoAnaliseRegressaoEdit');
    if (tipoSelect && dados?.regressao) {
        tipoSelect.innerHTML = '';
        dados.regressao.tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
    
    // Atualizar variáveis dependentes
    const variavelSelect = document.getElementById('variavelDependenteEdit');
    if (variavelSelect && dados?.regressao) {
        variavelSelect.innerHTML = '';
        dados.regressao.variaveis.forEach(variavel => {
            const option = document.createElement('option');
            option.value = variavel.value;
            option.textContent = variavel.text;
            variavelSelect.appendChild(option);
        });
    }
}

function atualizarParametrosArvore() {
    const area = document.getElementById('areaJuridicaModeloArvore')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    
    const tipoSelect = document.getElementById('tipoAcaoArvore');
    if (tipoSelect && dados?.arvores) {
        tipoSelect.innerHTML = '';
        dados.arvores.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
}

function atualizarParametrosNeurais() {
    const area = document.getElementById('areaJuridicaModeloNeurais')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    
    // Atualizar tipos de análise neural
    const tipoSelect = document.getElementById('tipoAnaliseNeuralEdit');
    if (tipoSelect && dados?.neurais) {
        tipoSelect.innerHTML = '';
        dados.neurais.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
    
    // Atualizar modelos neurais
    const modeloSelect = document.getElementById('modeloNeuralEdit');
    if (modeloSelect && dados?.modelos_neurais) {
        modeloSelect.innerHTML = '';
        dados.modelos_neurais.forEach(modelo => {
            const option = document.createElement('option');
            option.value = modelo.value;
            option.textContent = modelo.text;
            modeloSelect.appendChild(option);
        });
    }
}

function atualizarParametrosTemporais() {
    const area = document.getElementById('areaJuridicaModeloTemporais')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    
    const tipoSelect = document.getElementById('tipoAnaliseTemporaisEdit');
    if (tipoSelect && dados?.temporais) {
        tipoSelect.innerHTML = '';
        dados.temporais.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
}

function atualizarParametrosSobrevivencia() {
    const area = document.getElementById('areaJuridicaModeloSobrevivencia')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    
    const eventoSelect = document.getElementById('eventoInteresseEdit');
    if (eventoSelect && dados?.sobrevivencia) {
        eventoSelect.innerHTML = '';
        dados.sobrevivencia.forEach(evento => {
            const option = document.createElement('option');
            option.value = evento.value;
            option.textContent = evento.text;
            eventoSelect.appendChild(option);
        });
    }
}

// ==================== FUNÇÕES DE MANIPULAÇÃO DE VARIÁVEIS ====================

// Regressão - Variáveis Independentes
function adicionarVariavelIndependente() {
    const container = document.getElementById('variaveisIndependentesContainer');
    if (!container) return;
    
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
    container.appendChild(div);
}

function removerVariavelIndependente(button) {
    button.closest('.variavel-independente').remove();
}

// Árvores de Decisão - Atributos de Entrada
function adicionarAtributoEntrada() {
    const container = document.getElementById('atributosEntradaContainer');
    if (!container) return;
    
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
    container.appendChild(div);
}

function removerAtributoEntrada(button) {
    button.closest('.atributo-entrada').remove();
}

// Redes Neurais - Camadas
function adicionarCamada() {
    const container = document.getElementById('camadasContainer');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'camada mb-3';
    div.innerHTML = `
        <div class="row">
            <div class="col-4">
                <select class="form-select" name="tipoCamada[]">
                    <option value="dense">Dense</option>
                    <option value="conv1d">Conv1D</option>
                    <option value="conv2d">Conv2D</option>
                    <option value="lstm">LSTM</option>
                    <option value="gru">GRU</option>
                    <option value="dropout">Dropout</option>
                    <option value="batch_norm">Batch Norm</option>
                </select>
            </div>
            <div class="col-3">
                <input type="number" class="form-control" placeholder="Neurônios" name="numeroNeuronios[]" min="1" max="1024">
            </div>
            <div class="col-4">
                <select class="form-select" name="ativacao[]">
                    <option value="relu">ReLU</option>
                    <option value="sigmoid">Sigmoid</option>
                    <option value="tanh">Tanh</option>
                    <option value="softmax">Softmax</option>
                    <option value="linear">Linear</option>
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

function removerCamada(button) {
    button.closest('.camada').remove();
}

// Séries Temporais - Variáveis Externas
function adicionarVariavelExterna() {
    const container = document.getElementById('variaveisExternasContainer');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'variavel-externa mb-3';
    div.innerHTML = `
        <div class="row">
            <div class="col-8">
                <input type="text" class="form-control" placeholder="Nome da Variável Externa" name="nomeVariavelExterna[]">
            </div>
            <div class="col-3">
                <select class="form-select" name="tipoVariavelExterna[]">
                    <option value="economica">Econômica</option>
                    <option value="social">Social</option>
                    <option value="politica">Política</option>
                    <option value="juridica">Jurídica</option>
                    <option value="temporal">Temporal</option>
                </select>
            </div>
            <div class="col-1">
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removerVariavelExterna(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    container.appendChild(div);
}

function removerVariavelExterna(button) {
    button.closest('.variavel-externa').remove();
}

// Sobrevivência - Covariáveis
function adicionarCovariavel() {
    const container = document.getElementById('covariaveisContainer');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'covariavel mb-3';
    div.innerHTML = `
        <div class="row">
            <div class="col-4">
                <input type="text" class="form-control" placeholder="Nome da Covariável" name="nomeCovariavel[]">
            </div>
            <div class="col-3">
                <select class="form-select" name="tipoCovariavel[]">
                    <option value="categorica">Categórica</option>
                    <option value="continua">Contínua</option>
                    <option value="binaria">Binária</option>
                    <option value="ordinal">Ordinal</option>
                </select>
            </div>
            <div class="col-3">
                <select class="form-select" name="efeito[]">
                    <option value="fixo">Efeito Fixo</option>
                    <option value="tempo_dependente">Tempo-Dependente</option>
                    <option value="estratificado">Estratificado</option>
                </select>
            </div>
            <div class="col-1">
                <button type="button" class="btn btn-outline-success btn-sm" onclick="configurarCovariavel(this)" title="Configurar">
                    <i class="fas fa-cog"></i>
                </button>
            </div>
            <div class="col-1">
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removerCovariavel(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    container.appendChild(div);
}

function removerCovariavel(button) {
    button.closest('.covariavel').remove();
}

function configurarCovariavel(button) {
    // Implementar configuração específica da covariável
    console.log('Configurando covariável...');
}

// ==================== FUNÇÕES DE ATUALIZAÇÃO DE VALORES ====================

function atualizarValorProfundidade(valor) {
    const span = document.getElementById('valorProfundidadeVisualizacao');
    if (span) span.textContent = valor;
}

function atualizarValorDropout(valor) {
    const span = document.getElementById('valorDropout');
    if (span) span.textContent = valor;
}

// ==================== FUNÇÕES DE MODELO ESPECÍFICAS ====================

function atualizarParametrosModelo() {
    const modelo = document.getElementById('modeloPrincipal')?.value;
    const container = document.getElementById('parametrosModeloContainer');
    
    if (!container) return;
    
    // Limpar container
    container.innerHTML = '';
    
    switch (modelo) {
        case 'arima':
        case 'sarima':
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Parâmetros ARIMA/SARIMA configurados na seção específica abaixo.
                </div>
            `;
            break;
        case 'prophet':
            container.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <label class="form-label">Crescimento</label>
                        <select class="form-select">
                            <option value="linear">Linear</option>
                            <option value="logistic">Logístico</option>
                        </select>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Sazonalidade Anual</label>
                        <select class="form-select">
                            <option value="auto">Automática</option>
                            <option value="true">Habilitada</option>
                            <option value="false">Desabilitada</option>
                        </select>
                    </div>
                </div>
            `;
            break;
        case 'lstm':
            container.innerHTML = `
                <div class="row">
                    <div class="col-4">
                        <label class="form-label">Unidades LSTM</label>
                        <input type="number" class="form-control" value="50" min="10" max="500">
                    </div>
                    <div class="col-4">
                        <label class="form-label">Camadas</label>
                        <input type="number" class="form-control" value="2" min="1" max="10">
                    </div>
                    <div class="col-4">
                        <label class="form-label">Dropout</label>
                        <input type="range" class="form-range" min="0" max="0.8" step="0.1" value="0.2">
                    </div>
                </div>
            `;
            break;
    }
}

function atualizarParametrosModeloSobrevivencia() {
    const modelo = document.getElementById('modeloSobrevivencia')?.value;
    const container = document.getElementById('parametrosModeloSobrevivencia');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    switch (modelo) {
        case 'cox':
            container.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="proporcionalidade" checked>
                    <label class="form-check-label" for="proporcionalidade">
                        Verificar Proporcionalidade
                    </label>
                </div>
            `;
            break;
        case 'weibull':
        case 'exponencial':
        case 'log_normal':
            container.innerHTML = `
                <label class="form-label">Parâmetro de Forma</label>
                <input type="number" class="form-control" placeholder="Estimado automaticamente" readonly>
            `;
            break;
    }
}

// ==================== FUNÇÕES DE TESTE E SALVAMENTO ====================

async function testarModeloRegressao() {
    const formData = coletarDadosFormulario('formEditarRegressao');
    console.log('Testando modelo de regressão...', formData);
    
    try {
        const response = await fetch('/api/estatistica/testar-regressao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'regressao');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de regressão');
    }
}

async function testarModeloArvore() {
    const formData = coletarDadosFormulario('formEditarArvoreDecisao');
    console.log('Testando modelo de árvore...', formData);
    
    try {
        const response = await fetch('/api/estatistica/testar-arvore', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'arvore');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de árvore de decisão');
    }
}

async function testarModeloNeurais() {
    const formData = coletarDadosFormulario('formEditarRedesNeurais');
    console.log('Testando modelo neural...', formData);
    
    try {
        const response = await fetch('/api/estatistica/testar-neurais', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'neurais');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de redes neurais');
    }
}

async function testarModeloTemporais() {
    const formData = coletarDadosFormulario('formEditarSeriesTemporais');
    console.log('Testando modelo temporal...', formData);
    
    try {
        const response = await fetch('/api/estatistica/testar-temporais', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'temporais');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de séries temporais');
    }
}

async function testarModeloSobrevivencia() {
    const formData = coletarDadosFormulario('formEditarSobrevivencia');
    console.log('Testando modelo de sobrevivência...', formData);
    
    try {
        const response = await fetch('/api/estatistica/testar-sobrevivencia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'sobrevivencia');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de análise de sobrevivência');
    }
}

// Funções de salvamento
async function salvarModeloRegressao() {
    const formData = coletarDadosFormulario('formEditarRegressao');
    await salvarModelo(formData, 'regressao');
}

async function salvarModeloArvore() {
    const formData = coletarDadosFormulario('formEditarArvoreDecisao');
    await salvarModelo(formData, 'arvore');
}

async function salvarModeloNeurais() {
    const formData = coletarDadosFormulario('formEditarRedesNeurais');
    await salvarModelo(formData, 'neurais');
}

async function salvarModeloTemporais() {
    const formData = coletarDadosFormulario('formEditarSeriesTemporais');
    await salvarModelo(formData, 'temporais');
}

async function salvarModeloSobrevivencia() {
    const formData = coletarDadosFormulario('formEditarSobrevivencia');
    await salvarModelo(formData, 'sobrevivencia');
}

// ==================== FUNÇÕES AUXILIARES ====================

function coletarDadosFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    
    const formData = new FormData(form);
    const dados = {};
    
    // Campos simples
    for (let [key, value] of formData.entries()) {
        if (dados[key]) {
            // Se já existe, converter para array
            if (!Array.isArray(dados[key])) {
                dados[key] = [dados[key]];
            }
            dados[key].push(value);
        } else {
            dados[key] = value;
        }
    }
    
    // Campos específicos (select, checkbox, etc.)
    const selects = form.querySelectorAll('select');
    selects.forEach(select => {
        dados[select.id] = select.value;
    });
    
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        dados[checkbox.id] = checkbox.checked;
    });
    
    const ranges = form.querySelectorAll('input[type="range"]');
    ranges.forEach(range => {
        dados[range.id] = range.value;
    });
    
    return dados;
}

async function salvarModelo(dados, tipo) {
    try {
        const response = await fetch(`/api/estatistica/salvar-${tipo}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            mostrarSucesso(`Modelo de ${tipo} salvo com sucesso!`);
            // Fechar modal
            const modal = document.querySelector(`.modal.show`);
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
            }
        } else {
            mostrarErro(resultado.erro || 'Erro ao salvar modelo');
        }
    } catch (error) {
        console.error('Erro ao salvar modelo:', error);
        mostrarErro('Erro ao salvar modelo');
    }
}

function mostrarResultadoTeste(resultado, tipo) {
    const modalContent = `
        <div class="modal fade" id="modalResultadoTeste" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-check-circle me-2"></i>Resultado do Teste - ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <pre>${JSON.stringify(resultado, null, 2)}</pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente
    const existingModal = document.getElementById('modalResultadoTeste');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Adicionar novo modal
    document.body.insertAdjacentHTML('beforeend', modalContent);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalResultadoTeste'));
    modal.show();
}

function mostrarSucesso(mensagem) {
    // Implementar toast de sucesso
    console.log('Sucesso:', mensagem);
    // Aqui você pode usar sua biblioteca de toast preferida
}

function mostrarErro(mensagem) {
    // Implementar toast de erro
    console.error('Erro:', mensagem);
    // Aqui você pode usar sua biblioteca de toast preferida
}

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar dados das áreas jurídicas quando disponível
    if (typeof dadosPorArea !== 'undefined') {
        window.dadosPorArea = dadosPorArea;
    }
    
    // Configurar eventos dos modais
    const modals = [
        'modalEditarRegressao',
        'modalEditarArvoreDecisao', 
        'modalEditarRedesNeurais',
        'modalEditarSeriesTemporais',
        'modalEditarSobrevivencia'
    ];
    
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('shown.bs.modal', function() {
                // Atualizar parâmetros quando modal for mostrado
                const areaSelect = modal.querySelector('select[id*="areaJuridica"]');
                if (areaSelect) {
                    // Disparar evento de mudança para carregar dados iniciais
                    areaSelect.dispatchEvent(new Event('change'));
                }
            });
        }
    });
    
    console.log('Templates de edição de modelos estatísticos inicializados');
});