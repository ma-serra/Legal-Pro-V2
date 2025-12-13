// ========================================================================================
// SISTEMA DE SALVAMENTO COM IDENTIFICADORES ÚNICOS - VALIDAÇÃO MULTI-AGENTE
// ========================================================================================

console.log("📋 Sistema de salvamento de análises carregado");

// Variável global para armazenar dados da última análise
let ultimaAnaliseCompleta = null;

// Função para salvar análise no banco de dados
async function salvarAnaliseNoBanco(dadosAnalise) {
    try {
        console.log("🔄 Iniciando salvamento da análise...");
        console.log("📊 Dados para salvamento:", dadosAnalise);
        
        const response = await fetch('/api/validacao-multi-agente/salvar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(dadosAnalise)
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            console.log("✅ Análise salva com sucesso!");
            console.log("🆔 Identificadores únicos:", resultado.data.numero_registro, resultado.data.uuid_analise);
            
            // Verificar se a análise já existia
            if (resultado.data.ja_existia) {
                // Mostrar notificação de que a análise já existia
                mostrarNotificacaoAviso(resultado);
            } else {
                // Mostrar notificação de sucesso
                mostrarNotificacaoSucesso(resultado);
            }
            
            // Atualizar interface com informações de salvamento
            adicionarInfoSalvamento(resultado.data);
            
            // Redirecionamento para histórico de análises após 2 segundos
            setTimeout(() => {
                console.log("🔄 Redirecionando para histórico de análises...");
                window.location.href = '/historico-analises-multiagente';
            }, 2000);
            
            return resultado;
        } else {
            console.error("❌ Erro ao salvar análise:", resultado.error);
            mostrarNotificacaoErro(resultado.error);
            return null;
        }
    } catch (error) {
        console.error("❌ Erro na requisição de salvamento:", error);
        mostrarNotificacaoErro("Erro de conexão com o servidor");
        return null;
    }
}

// Função para extrair dados da análise da página
function extrairDadosAnalise() {
    try {
        console.log("📊 DEBUG: Iniciando extração de dados da análise...");
        console.log("📊 DEBUG: ultimaAnaliseCompleta:", ultimaAnaliseCompleta);
        
        // Verificar se há dados da última análise
        if (!ultimaAnaliseCompleta) {
            console.warn("⚠️ DEBUG: Nenhum resultado de análise encontrado em ultimaAnaliseCompleta");
            return null;
        }
        
        // Extrair texto do documento (do campo de entrada)
        const textoDocumento = document.getElementById('texto_documento')?.value || 
                              document.querySelector('textarea[name="texto_documento"]')?.value || 
                              '';
        
        console.log("📊 DEBUG: Texto do documento extraído:", textoDocumento ? `${textoDocumento.length} caracteres` : 'não encontrado');
        
        if (!textoDocumento.trim()) {
            console.warn("⚠️ DEBUG: Texto do documento não encontrado, usando dados da análise");
            // Se não encontrar o texto original, usar uma mensagem padrão
        }
        
        // Preparar dados para salvamento
        const dadosAnalise = {
            titulo_analise: `Análise Multi-Agente - ${ultimaAnaliseCompleta.numero_registro || new Date().getTime()}`,
            descricao: "Análise realizada através da interface de validação multi-agente expandida",
            documento_original: textoDocumento || "Documento analisado via interface web",
            documento_nome: "documento_validacao.txt",
            documento_tipo: "text/plain",
            total_agentes_utilizados: (ultimaAnaliseCompleta.results?.analises || ultimaAnaliseCompleta.resultados || []).length,
            areas_juridicas_envolvidas: extrairAreasJuridicas(),
            resultados_agentes: ultimaAnaliseCompleta.results?.analises || ultimaAnaliseCompleta.resultados || [],
            recomendacoes_prioritarias: ultimaAnaliseCompleta.recomendacoes_consolidadas?.prioritarias || [],
            recomendacoes_importantes: ultimaAnaliseCompleta.recomendacoes_consolidadas?.importantes || [],
            recomendacoes_sugeridas: ultimaAnaliseCompleta.recomendacoes_consolidadas?.sugeridas || [],
            tempo_processamento_segundos: ultimaAnaliseCompleta.results?.tempo_total || ultimaAnaliseCompleta.tempo_processamento || 15,
            modelos_ia_utilizados: extrairModelosUtilizados(),
            tokens_consumidos: ultimaAnaliseCompleta.meta?.total_tokens || ultimaAnaliseCompleta.tokens_total || 0,
            custo_estimado: calcularCustoEstimado(ultimaAnaliseCompleta.meta?.total_tokens || ultimaAnaliseCompleta.tokens_total || 0),
            status: "concluida",
            fallback_mode: ultimaAnaliseCompleta.fallback_mode || false,
            debug_mode: ultimaAnaliseCompleta.debug_mode || false,
            numero_registro_original: ultimaAnaliseCompleta.numero_registro
        };
        
        console.log("📊 DEBUG: Dados preparados para salvamento:", dadosAnalise);
        
        console.log("📋 Dados extraídos para salvamento:", dadosAnalise);
        return dadosAnalise;
        
    } catch (error) {
        console.error("❌ Erro ao extrair dados da análise:", error);
        return null;
    }
}

// Função para extrair áreas jurídicas dos resultados da análise
function extrairAreasJuridicas() {
    const areas = new Set();
    
    // Tentar extrair de diferentes locais possíveis
    const resultados = ultimaAnaliseCompleta?.results?.analises || ultimaAnaliseCompleta?.resultados || [];
    
    // 1. Procurar nas respostas dos agentes
    resultados.forEach(resultado => {
        const resposta = resultado.resposta || resultado.response || '';
        
        // Lista de áreas jurídicas para detectar
        const areasJuridicas = [
            'Direito Agrário', 'Direito Ambiental', 'Direito Bancário',
            'Direito Civil', 'Direito do Consumidor', 'Direito Empresarial',
            'Direito Família', 'Direito Imobiliário', 'Direito Internacional',
            'Direito Penal', 'Direito Previdenciário', 'Direito Processual',
            'Direito Trabalhista', 'Direito Tributário', 'Direito Constitucional',
            'Direito Administrativo', 'Direito Digital', 'Direito da Saúde',
            'Direito Eleitoral', 'Direito Notarial', 'Direito Marítimo',
            'Direito Aeronáutico'
        ];
        
        areasJuridicas.forEach(area => {
            if (resposta.includes(area)) {
                areas.add(area);
            }
        });
        
        // 2. Verificar se há categoria/área no resultado
        if (resultado.area_juridica) {
            areas.add(resultado.area_juridica);
        }
        if (resultado.categoria) {
            areas.add(resultado.categoria);
        }
    });
    
    // 3. Verificar se há área no metadata
    if (ultimaAnaliseCompleta?.meta?.area_juridica) {
        areas.add(ultimaAnaliseCompleta.meta.area_juridica);
    }
    
    // 4. Verificar campo direto
    if (ultimaAnaliseCompleta?.area_juridica) {
        areas.add(ultimaAnaliseCompleta.area_juridica);
    }
    
    // Converter Set para Array
    const areasArray = Array.from(areas);
    
    console.log("📊 Áreas jurídicas detectadas:", areasArray);
    
    // Se não encontrou nenhuma área, usar "Não especificada"
    return areasArray.length > 0 ? areasArray : ["Não especificada"];
}

// Função para extrair modelos de IA utilizados
function extrairModelosUtilizados() {
    const modelos = [];
    
    const resultados = ultimaAnaliseCompleta?.results?.analises || ultimaAnaliseCompleta?.resultados || [];
    
    resultados.forEach(resultado => {
        if (resultado.modelo_usado && !modelos.includes(resultado.modelo_usado)) {
            modelos.push(resultado.modelo_usado);
        } else if (resultado.api_provider && !modelos.includes(resultado.api_provider)) {
            modelos.push(resultado.api_provider);
        }
    });
    
    // Se não encontrou modelos, adicionar padrões
    if (modelos.length === 0) {
        modelos.push("GPT-4", "Claude 3.5 Sonnet");
    }
    
    return modelos;
}

// Função para calcular custo estimado baseado nos tokens e modelos usados
function calcularCustoEstimado(tokens) {
    // Preços reais atualizados por 1M tokens (em USD) - Base: Outubro 2024
    const precosPorModelo = {
        // OpenAI
        'gpt-4o': { input: 5.00, output: 15.00 },
        'gpt-4o-mini': { input: 0.15, output: 0.60 },
        'gpt-4': { input: 30.00, output: 60.00 },
        'gpt-3.5-turbo': { input: 0.50, output: 1.50 },
        
        // Anthropic
        'claude-3-5-sonnet': { input: 3.00, output: 15.00 },
        'claude-3-opus': { input: 15.00, output: 75.00 },
        'claude-3-haiku': { input: 0.25, output: 1.25 },
        'claude-sonnet': { input: 3.00, output: 15.00 },
        'claude-opus': { input: 15.00, output: 75.00 },
        
        // Google
        'gemini-1.5-pro': { input: 3.50, output: 10.50 },
        'gemini-2.5-pro': { input: 3.50, output: 10.50 },
        'gemini-1.5-flash': { input: 0.15, output: 0.60 },
        'gemini-2.5-flash': { input: 0.15, output: 0.60 },
        'gemini-pro': { input: 0.50, output: 1.50 },
        
        // DeepSeek
        'deepseek-chat': { input: 0.14, output: 0.28 },
        'deepseek-coder': { input: 0.14, output: 0.28 },
        'deepseek-reasoner': { input: 0.14, output: 0.28 }
    };
    
    // Taxa de câmbio USD para BRL (atualizada)
    const taxaCambio = 5.25;
    
    // Extrair modelos utilizados
    const modelosUtilizados = extrairModelosUtilizados();
    
    // Se não temos informação dos modelos, usar média ponderada
    if (!modelosUtilizados || modelosUtilizados.length === 0) {
        // Média ponderada: GPT-4o e Claude 3.5 Sonnet (modelos principais)
        const mediaInput = (5.00 + 3.00) / 2;  // $4.00/1M
        const mediaOutput = (15.00 + 15.00) / 2; // $15.00/1M
        
        // Assumir 40% input, 60% output
        const tokensInput = tokens * 0.4;
        const tokensOutput = tokens * 0.6;
        
        const custoUSD = (tokensInput / 1000000 * mediaInput) + (tokensOutput / 1000000 * mediaOutput);
        return custoUSD * taxaCambio;
    }
    
    // Calcular custo baseado nos modelos realmente utilizados
    let custoTotalUSD = 0;
    let modelosEncontrados = 0;
    
    modelosUtilizados.forEach(modelo => {
        const modeloLower = modelo.toLowerCase();
        
        // Procurar modelo na tabela de preços
        for (const [key, preco] of Object.entries(precosPorModelo)) {
            if (modeloLower.includes(key) || key.includes(modeloLower)) {
                // Assumir 40% input, 60% output (proporção típica em análises)
                const tokensInput = tokens * 0.4;
                const tokensOutput = tokens * 0.6;
                
                const custoModelo = (tokensInput / 1000000 * preco.input) + 
                                   (tokensOutput / 1000000 * preco.output);
                
                custoTotalUSD += custoModelo;
                modelosEncontrados++;
                break;
            }
        }
    });
    
    // Se encontrou modelos, usar média dos custos
    if (modelosEncontrados > 0) {
        const custoMedioUSD = custoTotalUSD / modelosEncontrados;
        return custoMedioUSD * taxaCambio;
    }
    
    // Fallback: usar modelo GPT-4o como referência
    const tokensInput = tokens * 0.4;
    const tokensOutput = tokens * 0.6;
    const custoUSD = (tokensInput / 1000000 * 5.00) + (tokensOutput / 1000000 * 15.00);
    
    return custoUSD * taxaCambio;
}

// Função para mostrar notificação de sucesso
function mostrarNotificacaoSucesso(dadosSalvamento) {
    // Criar elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notificacao.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 400px; max-width: 500px;';
    
    notificacao.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-check-circle me-2" style="font-size: 1.5rem; color: #198754;"></i>
            <div>
                <strong>✅ Análise Salva com Sucesso!</strong><br>
                <small>
                    <strong>ID:</strong> ${dadosSalvamento.data.numero_registro}<br>
                    <strong>UUID:</strong> ${dadosSalvamento.data.uuid_analise}<br>
                    <div class="mt-2 p-2 bg-light rounded">
                        <i class="fas fa-arrow-right text-primary"></i> 
                        <strong>Redirecionando para o histórico em 2 segundos...</strong>
                    </div>
                </small>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notificacao);
    
    // Remover após 10 segundos (mais tempo para ler a mensagem de redirecionamento)
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, 10000);
}

// Função para mostrar notificação de aviso (análise já existia)
function mostrarNotificacaoAviso(dadosSalvamento) {
    // Criar elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    notificacao.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 400px; max-width: 500px;';
    
    notificacao.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-info-circle me-2" style="font-size: 1.5rem; color: #ffc107;"></i>
            <div>
                <strong>ℹ️ ${dadosSalvamento.message}</strong><br>
                <small>
                    <strong>ID:</strong> ${dadosSalvamento.data.numero_registro}<br>
                    <strong>UUID:</strong> ${dadosSalvamento.data.uuid_analise}<br>
                    <div class="mt-2 p-2 bg-light rounded">
                        <i class="fas fa-arrow-right text-primary"></i> 
                        <strong>Redirecionando para o histórico em 2 segundos...</strong>
                    </div>
                </small>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notificacao);
    
    // Remover após 10 segundos
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, 10000);
}

// Função para mostrar notificação de erro
function mostrarNotificacaoErro(mensagem) {
    const notificacao = document.createElement('div');
    notificacao.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    notificacao.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 350px;';
    
    notificacao.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <div>
                <strong>Erro ao Salvar Análise</strong><br>
                <small>${mensagem}</small>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notificacao);
    
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, 10000);
}

// Função para adicionar informações de salvamento na interface
function adicionarInfoSalvamento(dadosSalvamento) {
    // Procurar container de resultados
    const resultadosContainer = document.getElementById('analysis-results');
    if (!resultadosContainer) return;
    
    // Criar card de informações de salvamento
    const cardSalvamento = document.createElement('div');
    cardSalvamento.className = 'card mt-3 border-success';
    cardSalvamento.innerHTML = `
        <div class="card-header bg-success text-white">
            <h6 class="mb-0">
                <i class="fas fa-database me-2"></i>
                Análise Salva no Sistema
            </h6>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-1"><strong>Número de Registro:</strong></p>
                    <code class="text-success">${dadosSalvamento.numero_registro}</code>
                </div>
                <div class="col-md-6">
                    <p class="mb-1"><strong>Identificador Único:</strong></p>
                    <code class="text-muted small">${dadosSalvamento.uuid_analise}</code>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-12">
                    <p class="mb-1"><strong>Hash SHA-256:</strong></p>
                    <code class="text-muted small">${dadosSalvamento.hash_sha256}</code>
                </div>
            </div>
            <div class="mt-3">
                <button type="button" class="btn btn-sm btn-outline-success" onclick="buscarAnalise('${dadosSalvamento.numero_registro}')">
                    <i class="fas fa-search me-1"></i>
                    Buscar Análise
                </button>
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="exportarAnalise('${dadosSalvamento.numero_registro}')">
                    <i class="fas fa-download me-1"></i>
                    Exportar
                </button>
            </div>
        </div>
    `;
    
    resultadosContainer.appendChild(cardSalvamento);
}

// Função para buscar análise salva
async function buscarAnalise(identificador) {
    try {
        const response = await fetch(`/api/validacao-multi-agente/buscar/${identificador}`);
        const resultado = await response.json();
        
        if (resultado.success) {
            console.log("✅ Análise encontrada:", resultado.data);
            
            // Exibir resultados da análise carregada
            if (typeof displayAnalysisResults === 'function') {
                displayAnalysisResults({
                    numero_registro: resultado.data.numero_registro,
                    resultados_agentes: resultado.data.resultados_agentes,
                    results: resultado.data.resultados_agentes,
                    meta: {
                        numero_registro: resultado.data.numero_registro,
                        total_tokens: resultado.data.tokens_consumidos,
                        tempo_total: resultado.data.tempo_processamento_segundos
                    }
                });
            } else {
                mostrarModalAnalise(resultado.data);
            }
        } else {
            console.error("❌ Análise não encontrada:", resultado.error);
            mostrarNotificacaoErro("Análise não encontrada");
        }
    } catch (error) {
        console.error("❌ Erro ao buscar análise:", error);
        mostrarNotificacaoErro("Erro ao buscar análise");
    }
}

// Função para exportar análise
async function exportarAnalise(identificador, formato = 'pdf') {
    try {
        console.log(`📄 Iniciando exportação ${formato.toUpperCase()} para análise: ${identificador}`);
        
        const response = await fetch(`/api/validacao-multi-agente/exportar/${identificador}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ formato: formato })
        });
        
        if (response.ok) {
            // Se retornou arquivo, fazer download
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/')) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `relatorio_analise_${identificador}.${formato}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                console.log(`✅ Arquivo ${formato.toUpperCase()} baixado com sucesso`);
                mostrarNotificacaoSucesso({ numero_registro: `Arquivo ${formato.toUpperCase()} exportado` });
            } else {
                const data = await response.json();
                console.log("📄 Resposta da exportação:", data);
            }
        } else {
            const errorData = await response.json();
            console.error("❌ Erro na exportação:", errorData);
            mostrarNotificacaoErro(`Erro na exportação: ${errorData.error}`);
        }
    } catch (error) {
        console.error("❌ Erro ao exportar análise:", error);
        mostrarNotificacaoErro("Erro ao exportar análise");
    }
}

// Função para mostrar modal de análise (fallback)
function mostrarModalAnalise(dadosAnalise) {
    console.log("📊 Exibindo detalhes da análise:", dadosAnalise);
    
    // Criar modal simples
    const modalHtml = `
        <div class="modal fade" id="modalAnalise" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content bg-dark text-light">
                    <div class="modal-header">
                        <h5 class="modal-title">Detalhes da Análise</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>Número de Registro:</h6>
                        <p class="text-info">${dadosAnalise.numero_registro}</p>
                        
                        <h6>Status:</h6>
                        <p class="text-success">${dadosAnalise.status}</p>
                        
                        <h6>Documento:</h6>
                        <p>${dadosAnalise.documento_nome} (${dadosAnalise.documento_tamanho} bytes)</p>
                        
                        <div class="mt-3">
                            <button class="btn btn-primary me-2" onclick="exportarAnalise('${dadosAnalise.numero_registro}', 'pdf')">
                                <i class="fas fa-file-pdf me-1"></i>Exportar PDF
                            </button>
                            <button class="btn btn-success" onclick="exportarAnalise('${dadosAnalise.numero_registro}', 'docx')">
                                <i class="fas fa-file-word me-1"></i>Exportar DOCX
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar modal ao documento
    const existingModal = document.getElementById('modalAnalise');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalAnalise'));
    modal.show();
}



// Função para intercept resultados da análise
function interceptarResultadosAnalise() {
    console.log("🔧 DEBUG: Iniciando interceptação de resultados...");
    
    // Aguardar que a função displayAnalysisResults seja definida
    const intervalId = setInterval(() => {
        if (typeof window.displayAnalysisResults === 'function') {
            console.log("✅ DEBUG: Função displayAnalysisResults encontrada, interceptando...");
            
            const originalDisplayResults = window.displayAnalysisResults;
            
            window.displayAnalysisResults = function(data) {
                console.log("🎯 DEBUG: displayAnalysisResults interceptada! Dados recebidos:", data);
                
                // Armazenar dados para salvamento
                ultimaAnaliseCompleta = data;
                console.log("💾 DEBUG: Dados armazenados em ultimaAnaliseCompleta");
                
                // Chamar função original
                const resultado = originalDisplayResults.call(this, data);
                
                // Adicionar botão de salvamento após 3 segundos
                setTimeout(() => {
                    console.log("⏰ DEBUG: Timeout executado, adicionando botão de salvamento...");
                    adicionarBotaoSalvamento();
                }, 3000);
                
                return resultado;
            };
            
            clearInterval(intervalId);
            console.log("✅ DEBUG: Interceptação configurada com sucesso");
        } else {
            console.log("⏳ DEBUG: Aguardando função displayAnalysisResults...");
        }
    }, 500);
    
    // Timeout de segurança para não ficar em loop infinito
    setTimeout(() => {
        clearInterval(intervalId);
        console.warn("⚠️ DEBUG: Timeout de interceptação atingido");
    }, 30000);
}

// Função para adicionar botão de salvamento
function adicionarBotaoSalvamento() {
    console.log("🔧 DEBUG: Tentando adicionar botão de salvamento...");
    
    // Verificar se já existe botão
    if (document.getElementById('btn-salvar-analise')) {
        console.log("ℹ️ DEBUG: Botão de salvamento já existe");
        return;
    }
    
    // Procurar container de resultados
    let resultadosContainer = document.getElementById('analysis-results') || 
                             document.getElementById('resultadosAnalise') ||
                             document.querySelector('.container-fluid');
    
    console.log("📊 DEBUG: Container de resultados:", resultadosContainer ? 'encontrado' : 'não encontrado');
    
    if (!resultadosContainer) {
        console.warn("⚠️ DEBUG: Container de resultados não encontrado, tentando adicionar ao body");
        resultadosContainer = document.body;
    }
    
    // Criar botão de salvamento
    const btnContainer = document.createElement('div');
    btnContainer.className = 'text-center mt-4 mb-4';
    btnContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999;';
    btnContainer.innerHTML = `
        <button id="btn-salvar-analise" type="button" class="btn btn-success btn-lg shadow-lg">
            <i class="fas fa-save me-2"></i>
            Salvar Análise no Sistema
            <small class="d-block mt-1">Com identificadores únicos</small>
        </button>
    `;
    
    // Adicionar ao final do body para garantir visibilidade
    document.body.appendChild(btnContainer);
    console.log("✅ DEBUG: Botão de salvamento adicionado");
    
    // Adicionar evento de clique
    document.getElementById('btn-salvar-analise').addEventListener('click', async function() {
        console.log("🖱️ DEBUG: Botão de salvamento clicado!");
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
        
        const dados = extrairDadosAnalise();
        console.log("📊 DEBUG: Dados extraídos:", dados);
        
        if (dados) {
            const resultado = await salvarAnaliseNoBanco(dados);
            if (resultado) {
                this.innerHTML = '<i class="fas fa-check me-2"></i>Salvo com Sucesso!';
                this.className = 'btn btn-outline-success btn-lg shadow-lg';
                
                // Remover botão após 5 segundos
                setTimeout(() => {
                    this.parentElement.remove();
                }, 5000);
            } else {
                this.innerHTML = '<i class="fas fa-save me-2"></i>Tentar Novamente';
                this.disabled = false;
                this.className = 'btn btn-warning btn-lg shadow-lg';
            }
        } else {
            this.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Análise no Sistema';
            this.disabled = false;
            this.className = 'btn btn-danger btn-lg shadow-lg';
            mostrarNotificacaoErro("Dados da análise não encontrados - verifique se a análise foi concluída");
        }
    });
    
    console.log("✅ DEBUG: Event listener adicionado ao botão");
}

// Inicializar sistema quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log("🔄 Inicializando sistema de salvamento de análises...");
    
    // Interceptar resultados
    interceptarResultadosAnalise();
    
    console.log("✅ Sistema de salvamento inicializado");
});

// ========================================================================================
// FIM DO SISTEMA DE SALVAMENTO
// ========================================================================================