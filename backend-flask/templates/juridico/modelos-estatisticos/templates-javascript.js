/**
 * JavaScript Unificado para Templates de Edição de Modelos Estatísticos
 * Legal Design Pro V2 - Sistema de Análise Estatística e Preditiva
 */

// ==================== FUNÇÕES GERAIS ====================

// ==================== SIMULAÇÃO DE BASE DE PROCESSOS ====================
// Base simulada de processos com CNPJs/CPFs associados
const BASE_PROCESSOS_SIMULADA = {
    '1234567-89.2024.8.26.0100': {
        cliente: 'Maria Silva Santos',
        cnpj_cpf: '123.456.789-10',
        tipo_pessoa: 'fisica'
    },
    '2345678-90.2024.8.26.0200': {
        cliente: 'Empresa Tech Solutions Ltda',
        cnpj_cpf: '12.345.678/0001-90',
        tipo_pessoa: 'juridica'
    },
    '3456789-01.2024.8.26.0300': {
        cliente: 'João Roberto da Costa',
        cnpj_cpf: '987.654.321-00',
        tipo_pessoa: 'fisica'
    },
    '4567890-12.2024.8.26.0400': {
        cliente: 'Comercial São Paulo S/A',
        cnpj_cpf: '98.765.432/0001-10',
        tipo_pessoa: 'juridica'
    },
    '5678901-23.2024.8.26.0500': {
        cliente: 'Ana Paula Ferreira',
        cnpj_cpf: '456.789.123-45',
        tipo_pessoa: 'fisica'
    }
};

// Função para buscar dados do processo na base simulada
function buscarDadosProcesso(numeroProcesso) {
    return BASE_PROCESSOS_SIMULADA[numeroProcesso] || null;
}

// Função para aplicar máscara de CNPJ/CPF
function aplicarMascaraCnpjCpf(campo) {
    let valor = campo.value.replace(/\D/g, '');
    
    if (valor.length <= 11) {
        // CPF: 123.456.789-10
        valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
        valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
        valor = valor.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    } else {
        // CNPJ: 12.345.678/0001-90
        valor = valor.replace(/^(\d{2})(\d)/, '$1.$2');
        valor = valor.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
        valor = valor.replace(/\.(\d{3})(\d)/, '.$1/$2');
        valor = valor.replace(/(\d{4})(\d)/, '$1-$2');
    }
    
    campo.value = valor;
    
    // Determinar automaticamente o tipo de pessoa
    const tipoPessoaField = campo.id.replace('cnpjCpfCliente', 'tipoPessoa');
    const tipoPessoaSelect = document.getElementById(tipoPessoaField);
    
    if (tipoPessoaSelect && valor.length >= 14) {
        if (valor.replace(/\D/g, '').length === 11) {
            tipoPessoaSelect.value = 'fisica';
        } else if (valor.replace(/\D/g, '').length === 14) {
            tipoPessoaSelect.value = 'juridica';
        }
    }
}

// Função para preenchimento automático baseado no processo CNJ
function preencherAutomaticoCnpjCpf(campoCnj, sufixo = '') {
    const numeroProcesso = campoCnj.value.trim();
    const dadosProcesso = buscarDadosProcesso(numeroProcesso);
    
    if (dadosProcesso) {
        // Campos específicos baseados no sufixo do template
        const cnpjCpfField = document.getElementById(`cnpjCpfCliente${sufixo}`);
        const clienteField = document.getElementById(`clienteAutor${sufixo}`);
        const tipoPessoaField = document.getElementById(`tipoPessoa${sufixo}`);
        
        if (cnpjCpfField) {
            cnpjCpfField.value = dadosProcesso.cnpj_cpf;
            cnpjCpfField.style.backgroundColor = '#e8f5e8';
            
            // Feedback visual temporário
            setTimeout(() => {
                cnpjCpfField.style.backgroundColor = '';
            }, 2000);
        }
        
        if (clienteField && !clienteField.value) {
            clienteField.value = dadosProcesso.cliente;
            clienteField.style.backgroundColor = '#e8f5e8';
            
            setTimeout(() => {
                clienteField.style.backgroundColor = '';
            }, 2000);
        }
        
        if (tipoPessoaField) {
            tipoPessoaField.value = dadosProcesso.tipo_pessoa;
        }
        
        // Mostrar notificação de sucesso
        mostrarNotificacaoPreenchimento('Dados preenchidos automaticamente com base no processo!');
    }
}

// Função para mostrar notificação de preenchimento
function mostrarNotificacaoPreenchimento(mensagem) {
    // Criar elemento de notificação
    const notificacao = document.createElement('div');
    notificacao.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notificacao.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
    notificacao.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notificacao);
    
    // Remover automaticamente após 3 segundos
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, 3000);
}

// Função para atualizar parâmetros baseados na área jurídica selecionada
// ============= CONFIGURAÇÕES DA MATRIZ UNIVERSAL =============
const MATRIZ_AREAS_JURIDICAS = {
    'trabalhista': {
        nome: 'Direito Trabalhista',
        volume_minimo: 2000,
        precisao_esperada: '88-95%',
        precisao_media: 91.5,
        campos_especificos: [
            'horas_extras_e_reflexos', 'indenizacao_por_danos_morais',
            'fgts_e_a_multa_de_40_porcento', 'verbas_rescisoria',
            'adicional_noturno_e_reflexos', 'ferias_em_dobro',
            'adicional_de_periculosidade', 'adicional_de_insalubridade',
            'estabilidade_provisoria', 'multa_do_artigo_477'
        ],
        caracteristicas: 'Alta padronização CLT'
    },
    'civil': {
        nome: 'Direito Civil',
        volume_minimo: 3000,
        precisao_esperada: '85-92%',
        precisao_media: 88.5,
        campos_especificos: [
            'danos_morais', 'danos_materiais', 'lucros_cessantes',
            'restituicao_valores', 'rescisao_contratual', 'cumprimento_obrigacao',
            'indenizacao_por_inadimplemento', 'juros_e_correcao',
            'responsabilidade_civil', 'direitos_da_personalidade'
        ],
        caracteristicas: 'Grande diversidade de casos'
    },
    'tributario': {
        nome: 'Direito Tributário',
        volume_minimo: 1500,
        precisao_esperada: '90-96%',
        precisao_media: 93,
        campos_especificos: [
            'restituicao_tributos', 'anulacao_debito_fiscal',
            'compensacao_tributaria', 'multa_fiscal',
            'juros_sobre_tributos', 'parcelamento_debitos',
            'exclusao_do_simples', 'credito_presumido',
            'nulidade_auto_infracao', 'repetitividade_indevido'
        ],
        caracteristicas: 'Legislação específica'
    },
    'consumidor': {
        nome: 'Direito do Consumidor',
        volume_minimo: 2500,
        precisao_esperada: '87-94%',
        precisao_media: 90.5,
        campos_especificos: [
            'danos_morais_consumidor', 'restituicao_em_dobro',
            'vicio_do_produto', 'propaganda_enganosa',
            'cobranca_indevida', 'negativacao_indevida',
            'defeito_do_produto', 'praticas_abusivas',
            'rescisao_contratual_cdc', 'inversao_onus_prova'
        ],
        caracteristicas: 'CDC bem estruturado'
    },
    'familia': {
        nome: 'Direito de Família',
        volume_minimo: 1000,
        precisao_esperada: '83-90%',
        precisao_media: 86.5,
        campos_especificos: [
            'pensao_alimenticia', 'divisao_bens',
            'guarda_dos_filhos', 'visitas',
            'reconhecimento_paternidade', 'divorcio_consensual',
            'uniao_estavel', 'regime_bens_matrimonial',
            'adocao', 'violencia_domestica'
        ],
        caracteristicas: 'Alto componente emocional'
    },
    'imobiliario': {
        nome: 'Direito Imobiliário',
        volume_minimo: 1200,
        precisao_esperada: '86-93%',
        precisao_media: 89.5,
        campos_especificos: [
            'reintegracao_posse', 'usucapiao',
            'rescisao_contrato_compra_venda', 'cobranca_condominio',
            'indenizacao_benfeitorias', 'danos_por_vazamento',
            'distrato_imobiliario', 'entrega_chaves',
            'registro_imovel', 'financiamento_habitacional'
        ],
        caracteristicas: 'Valores bem definidos'
    },
    'empresarial': {
        nome: 'Direito Empresarial',
        volume_minimo: 1800,
        precisao_esperada: '84-91%',
        precisao_media: 87.5,
        campos_especificos: [
            'dissolucao_sociedade', 'cobranca_titulo_credito',
            'recuperacao_judicial', 'falencia',
            'responsabilidade_socios', 'apuracao_haveres',
            'concorrencia_desleal', 'propriedade_industrial',
            'contratos_empresariais', 'joint_venture'
        ],
        caracteristicas: 'Complexidade societária'
    },
    'penal': {
        nome: 'Direito Penal',
        volume_minimo: 2200,
        precisao_esperada: '89-95%',
        precisao_media: 92,
        campos_especificos: [
            'habeas_corpus', 'reparacao_dano_moral_penal',
            'relaxamento_prisao', 'sursis_pena',
            'liberdade_provisoria', 'progressao_regime',
            'revisao_criminal', 'execucao_penal',
            'medidas_cautelares', 'detencao_preventiva'
        ],
        caracteristicas: 'Alta complexidade processual'
    },
    'administrativo': {
        nome: 'Direito Administrativo',
        volume_minimo: 1600,
        precisao_esperada: '85-92%',
        precisao_media: 88.5,
        campos_especificos: [
            'mandado_seguranca', 'anulacao_ato_administrativo',
            'ressarcimento_errario', 'licitacao_publica',
            'concurso_publico', 'servidor_publico',
            'desapropriacao', 'improbidade_administrativa',
            'contratos_administrativos', 'processo_administrativo'
        ],
        caracteristicas: 'Atos da administração pública'
    },
    'constitucional': {
        nome: 'Direito Constitucional',
        volume_minimo: 800,
        precisao_esperada: '82-89%',
        precisao_media: 85.5,
        campos_especificos: [
            'arguicao_descumprimento', 'acao_inconstitucionalidade',
            'habeas_data', 'mandado_injuncao',
            'direitos_fundamentais', 'controle_constitucionalidade',
            'recurso_extraordinario', 'repercussao_geral',
            'acao_direta_constitucionalidade', 'subsidiariedade'
        ],
        caracteristicas: 'Direitos fundamentais'
    },
    'ambiental': {
        nome: 'Direito Ambiental',
        volume_minimo: 1400,
        precisao_esperada: '86-93%',
        precisao_media: 89.5,
        campos_especificos: [
            'acao_civil_publica_ambiental', 'recuperacao_dano_ambiental',
            'licenciamento_ambiental', 'multa_ambiental',
            'termo_ajustamento_conduta', 'compensacao_ambiental',
            'area_preservacao_permanente', 'reserva_legal',
            'estudo_impacto_ambiental', 'crimes_ambientais'
        ],
        caracteristicas: 'Proteção do meio ambiente'
    },
    'previdenciario': {
        nome: 'Direito Previdenciário',
        volume_minimo: 3500,
        precisao_esperada: '91-97%',
        precisao_media: 94,
        campos_especificos: [
            'aposentadoria_invalidez', 'auxilio_doenca',
            'pensao_morte', 'revisao_beneficio',
            'restabelecimento_beneficio', 'aposentadoria_tempo_contribuicao',
            'auxilio_acidente', 'salario_maternidade',
            'aposentadoria_especial', 'beneficio_loas'
        ],
        caracteristicas: 'Alta padronização INSS'
    },
    'internacional': {
        nome: 'Direito Internacional',
        volume_minimo: 600,
        precisao_esperada: '80-87%',
        precisao_media: 83.5,
        campos_especificos: [
            'extradicao', 'homologacao_sentenca_estrangeira',
            'arbitragem_internacional', 'carta_rogatoria',
            'cooperacao_juridica_internacional', 'tratados_internacionais',
            'direitos_humanos', 'refugio_e_asilo',
            'nacionalidade', 'imunidade_diplomatica'
        ],
        caracteristicas: 'Complexidade de jurisdições'
    }
};

function atualizarParametrosRegressao() {
    const area = document.getElementById('areaJuridicaModeloRegressao')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    // Atualizar campos específicos da área
    atualizarCamposEspecificosArea(area);
    
    // Atualizar validação de volume mínimo
    atualizarVolumeMinimoArea(area);
    
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
    
    // Atualizar barra de precisão esperada
    if (areaConfig) {
        const precisaoBar = document.getElementById('precisaoEsperada');
        const classificacaoTexto = document.getElementById('classificacaoPrecisao');
        
        if (precisaoBar) {
            precisaoBar.style.width = areaConfig.precisao_media + '%';
            precisaoBar.textContent = areaConfig.precisao_media + '% - ' + 
                (areaConfig.precisao_media >= 88 ? 'Alta Precisão' :
                 areaConfig.precisao_media >= 75 ? 'Precisão Moderada' : 'Baixa Precisão');
            
            // Atualizar cor da barra
            precisaoBar.className = 'progress-bar bg-primary';
        }
        
        if (classificacaoTexto) {
            classificacaoTexto.innerHTML = `<i class="fas fa-info-circle"></i> ${areaConfig.nome} - ${areaConfig.caracteristicas}`;
        }
    }
}

function atualizarCamposEspecificosArea(area, modelType = 'regressao') {
    // Ocultar todos os campos específicos primeiro
    const allAreaFields = ['trabalhista', 'civil', 'tributario', 'consumidor', 'familia', 'imobiliario', 'empresarial'];
    const modelSuffixes = {
        'regressao': '',
        'arvore': 'Arvore', 
        'neurais': 'Neurais',
        'temporais': 'Temporais',
        'sobrevivencia': 'Sobrevivencia'
    };
    
    const suffix = modelSuffixes[modelType] || '';
    
    allAreaFields.forEach(areaField => {
        const element = document.getElementById(`campos${areaField.charAt(0).toUpperCase() + areaField.slice(1)}${suffix}`);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Mapear áreas para IDs dos campos
    const areaToId = {
        'trabalhista': 'Trabalhista',
        'civil': 'Civel',
        'tributario': 'Tributario',
        'consumidor': 'Consumidor',
        'familia': 'Familia',
        'imobiliario': 'Imobiliario', 
        'empresarial': 'Empresarial'
    };
    
    // Mostrar campos da área selecionada
    const areaId = areaToId[area];
    if (areaId) {
        const element = document.getElementById(`campos${areaId}${suffix}`);
        if (element) {
            element.style.display = 'block';
        }
    }
    
    // Atualizar texto de ajuda se disponível
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let html = `
        <div class="row">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="fas fa-gavel me-2"></i>
                    Campos Específicos - ${areaConfig.nome}
                    <small class="text-muted">(${areaConfig.campos_especificos.length} campos)</small>
                </h6>
            </div>
        </div>
        <div class="row">
    `;
    
    // Criar checkboxes para cada campo específico
    areaConfig.campos_especificos.forEach((campo, index) => {
        const nomeFormatado = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="campo_${campo}" name="campos_especificos[]" value="${campo}">
                    <label class="form-check-label" for="campo_${campo}">
                        ${nomeFormatado}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-info mb-0">
                    <i class="fas fa-lightbulb me-2"></i>
                    <strong>Dica:</strong> ${areaConfig.caracteristicas}. 
                    Volume mínimo recomendado: <strong>${areaConfig.volume_minimo.toLocaleString()}</strong> casos 
                    para precisão de <strong>${areaConfig.precisao_esperada}</strong>.
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function atualizarVolumeMinimoArea(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return;
    
    const volumeMinimoElement = document.getElementById('volumeMinimo');
    if (volumeMinimoElement) {
        volumeMinimoElement.textContent = areaConfig.volume_minimo.toLocaleString();
    }
    
    // Simular volume atual (em produção, isso viria de uma API)
    const volumeAtualSimulado = Math.floor(Math.random() * 5000) + 500;
    validarVolumeMinimo(volumeAtualSimulado);
}

function validarVolumeMinimo(volumeAtual = null) {
    const area = document.getElementById('areaJuridicaModeloRegressao')?.value || 'civil';
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!areaConfig) return;
    
    // Se não foi passado volume atual, pegar do input
    if (volumeAtual === null) {
        const inputTamanho = document.getElementById('tamanhoAmostraRegressao');
        volumeAtual = parseInt(inputTamanho?.value) || 0;
    }
    
    const volumeMinimo = areaConfig.volume_minimo;
    const percentual = Math.min((volumeAtual / volumeMinimo) * 100, 100);
    
    // Atualizar elementos da interface
    const volumeAtualElement = document.getElementById('volumeAtual');
    const statusVolumeElement = document.getElementById('statusVolume');
    const progressoVolumeElement = document.getElementById('progressoVolume');
    const alertStatusVolume = document.getElementById('alertStatusVolume');
    const impactoPrecisaoElement = document.getElementById('impactoPrecisao');
    const precisaoTextoElement = document.getElementById('precisaoEsperadaTexto');
    
    if (volumeAtualElement) {
        volumeAtualElement.textContent = volumeAtual.toLocaleString();
    }
    
    if (progressoVolumeElement) {
        progressoVolumeElement.style.width = percentual + '%';
        progressoVolumeElement.textContent = Math.round(percentual) + '%';
        progressoVolumeElement.setAttribute('aria-valuenow', percentual);
        
        // Atualizar cor da barra de progresso
        progressoVolumeElement.className = 'progress-bar progress-bar-striped ' +
            'bg-primary';
    }
    
    // Calcular precisão estimada baseada no volume
    let precisaoEstimada = areaConfig.precisao_media;
    let statusTexto = '';
    let alertClass = 'alert-success';
    
    if (volumeAtual >= volumeMinimo) {
        statusTexto = 'Volume Adequado';
        alertClass = 'alert-success';
        precisaoEstimada = areaConfig.precisao_media;
    } else if (volumeAtual >= volumeMinimo * 0.5) {
        statusTexto = 'Volume Insuficiente';
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.85; // Redução de 15%
    } else {
        statusTexto = 'Volume Crítico';
        alertClass = 'alert-danger';
        precisaoEstimada = areaConfig.precisao_media * 0.7; // Redução de 30%
    }
    
    if (statusVolumeElement) {
        statusVolumeElement.textContent = statusTexto;
    }
    
    if (alertStatusVolume) {
        alertStatusVolume.className = `alert mb-0 ${alertClass}`;
    }
    
    if (precisaoTextoElement) {
        precisaoTextoElement.textContent = `Precisão estimada: ${Math.round(precisaoEstimada)}%`;
    }
    
    if (impactoPrecisaoElement) {
        if (volumeAtual >= volumeMinimo) {
            impactoPrecisaoElement.textContent = 'Volume adequado garantirá a precisão máxima do modelo';
        } else {
            const reducao = Math.round((areaConfig.precisao_media - precisaoEstimada) * 10) / 10;
            impactoPrecisaoElement.textContent = `Volume insuficiente pode reduzir a precisão em até ${reducao} pontos percentuais`;
        }
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

// ============= FUNÇÕES ESPECÍFICAS ÁRVORES DE DECISÃO =============

function atualizarParametrosArvore() {
    const area = document.getElementById('areaJuridicaModeloArvore')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    // Atualizar campos específicos da área
    atualizarCamposEspecificosAreaArvore(area);
    
    // Atualizar validação de volume mínimo
    atualizarVolumeMinimoAreaArvore(area);
    
    // Atualizar tipos de ação
    const tipoSelect = document.getElementById('tipoAcaoArvore');
    if (tipoSelect && dados?.arvoreDecisao) {
        tipoSelect.innerHTML = '';
        dados.arvoreDecisao.tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
    
    // Atualizar barra de precisão esperada
    if (areaConfig) {
        const precisaoBar = document.getElementById('precisaoEsperadaArvore');
        const classificacaoTexto = document.getElementById('classificacaoPrecisaoArvore');
        
        // Árvores de decisão têm precisão ligeiramente superior à regressão
        const precisaoArvore = Math.min(areaConfig.precisao_media + 1.5, 95);
        
        if (precisaoBar) {
            precisaoBar.style.width = precisaoArvore + '%';
            precisaoBar.textContent = Math.round(precisaoArvore) + '% - ' + 
                (precisaoArvore >= 88 ? 'Alta Precisão' :
                 precisaoArvore >= 75 ? 'Precisão Moderada' : 'Baixa Precisão');
            
            // Atualizar cor da barra
            precisaoBar.className = 'progress-bar ' +
                'bg-primary';
        }
        
        if (classificacaoTexto) {
            classificacaoTexto.innerHTML = `<i class="fas fa-info-circle"></i> ${areaConfig.nome} - Árvores interpretáveis`;
        }
    }
}

function atualizarCamposEspecificosAreaArvore(area) {
    const container = document.getElementById('camposEspecificosAreaArvore');
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!container || !areaConfig) return;
    
    let html = `
        <div class="row">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="fas fa-sitemap me-2"></i>
                    Campos Específicos - ${areaConfig.nome}
                    <small class="text-muted">(${areaConfig.campos_especificos.length} campos)</small>
                </h6>
            </div>
        </div>
        <div class="row">
    `;
    
    // Criar checkboxes para cada campo específico
    areaConfig.campos_especificos.forEach((campo, index) => {
        const nomeFormatado = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="campo_arvore_${campo}" name="campos_especificos_arvore[]" value="${campo}">
                    <label class="form-check-label" for="campo_arvore_${campo}">
                        ${nomeFormatado}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-success mb-0">
                    <i class="fas fa-tree me-2"></i>
                    <strong>Vantagem das Árvores:</strong> ${areaConfig.caracteristicas}. 
                    Árvores de decisão são altamente interpretáveis e adequadas para explicar decisões jurídicas.
                    Volume mínimo: <strong>${areaConfig.volume_minimo.toLocaleString()}</strong> casos.
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function atualizarVolumeMinimoAreaArvore(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return;
    
    // Árvores de decisão precisam de 10% menos dados que regressão
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 0.9);
    
    const volumeMinimoElement = document.getElementById('volumeMinimoArvore');
    if (volumeMinimoElement) {
        volumeMinimoElement.textContent = volumeMinimo.toLocaleString();
    }
    
    // Simular volume atual (em produção, isso viria de uma API)
    const volumeAtualSimulado = Math.floor(Math.random() * 5000) + 600;
    validarVolumeMinimoArvore(volumeAtualSimulado);
}

function validarVolumeMinimoArvore(volumeAtual = null) {
    const area = document.getElementById('areaJuridicaModeloArvore')?.value || 'civil';
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!areaConfig) return;
    
    // Se não foi passado volume atual, pegar do input
    if (volumeAtual === null) {
        const inputTamanho = document.getElementById('tamanhoAmostraArvore');
        volumeAtual = parseInt(inputTamanho?.value) || 0;
    }
    
    // Árvores precisam de 10% menos dados
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 0.9);
    const percentual = Math.min((volumeAtual / volumeMinimo) * 100, 100);
    
    // Atualizar elementos da interface
    const volumeAtualElement = document.getElementById('volumeAtualArvore');
    const statusVolumeElement = document.getElementById('statusVolumeArvore');
    const progressoVolumeElement = document.getElementById('progressoVolumeArvore');
    const alertStatusVolume = document.getElementById('alertStatusVolumeArvore');
    const impactoPrecisaoElement = document.getElementById('impactoPrecisaoArvore');
    const precisaoTextoElement = document.getElementById('precisaoEsperadaTextoArvore');
    
    if (volumeAtualElement) {
        volumeAtualElement.textContent = volumeAtual.toLocaleString();
    }
    
    if (progressoVolumeElement) {
        progressoVolumeElement.style.width = percentual + '%';
        progressoVolumeElement.textContent = Math.round(percentual) + '%';
        progressoVolumeElement.setAttribute('aria-valuenow', percentual);
        
        // Atualizar cor da barra de progresso
        progressoVolumeElement.className = 'progress-bar progress-bar-striped ' +
            'bg-primary';
    }
    
    // Calcular precisão estimada baseada no volume (árvores são mais tolerantes)
    let precisaoEstimada = areaConfig.precisao_media + 1.5; // Bonus para árvores
    let statusTexto = '';
    let alertClass = 'alert-success';
    
    if (volumeAtual >= volumeMinimo) {
        statusTexto = 'Volume Adequado';
        alertClass = 'alert-success';
        precisaoEstimada = Math.min(areaConfig.precisao_media + 1.5, 95);
    } else if (volumeAtual >= volumeMinimo * 0.5) {
        statusTexto = 'Volume Insuficiente';
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.9; // Menor penalidade que regressão
    } else {
        statusTexto = 'Volume Crítico';
        alertClass = 'alert-danger';
        precisaoEstimada = areaConfig.precisao_media * 0.75; // Menor penalidade que regressão
    }
    
    if (statusVolumeElement) {
        statusVolumeElement.textContent = statusTexto;
    }
    
    if (alertStatusVolume) {
        alertStatusVolume.className = `alert mb-0 ${alertClass}`;
    }
    
    if (precisaoTextoElement) {
        precisaoTextoElement.textContent = `Precisão estimada: ${Math.round(precisaoEstimada)}%`;
    }
    
    if (impactoPrecisaoElement) {
        if (volumeAtual >= volumeMinimo) {
            impactoPrecisaoElement.textContent = 'Volume adequado permitirá árvore com alta interpretabilidade';
        } else {
            const reducao = Math.round((areaConfig.precisao_media + 1.5 - precisaoEstimada) * 10) / 10;
            impactoPrecisaoElement.textContent = `Volume insuficiente pode reduzir precisão, mas árvores são mais tolerantes (redução: ${reducao}pp)`;
        }
    }
}

function validarModeloArvoreDecisao() {
    const area = document.getElementById('areaJuridicaModeloArvore')?.value;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let validacoes = {
        camposObrigatorios: validarCamposObrigatoriosArvore(),
        volumeDados: validarVolumeDadosArvore(areaConfig),
        camposEspecificos: validarCamposEspecificosSelecionadosArvore(area),
        consistenciaDados: validarConsistenciaDadosArvore(),
        parametrosArvore: validarParametrosArvore()
    };
    
    let erros = [];
    let avisos = [];
    let score = 0;
    let maxScore = 100;
    
    // Validar campos obrigatórios (25 pontos)
    if (validacoes.camposObrigatorios.valido) {
        score += 25;
    } else {
        erros.push(...validacoes.camposObrigatorios.erros);
    }
    
    // Validar volume de dados (20 pontos)
    if (validacoes.volumeDados.valido) {
        score += 20;
    } else {
        if (validacoes.volumeDados.critico) {
            erros.push(...validacoes.volumeDados.erros);
        } else {
            avisos.push(...validacoes.volumeDados.avisos);
            score += 12; // Árvores são mais tolerantes a volume menor
        }
    }
    
    // Validar campos específicos (20 pontos)
    if (validacoes.camposEspecificos.valido) {
        score += 20;
    } else {
        avisos.push(...validacoes.camposEspecificos.avisos);
        score += Math.round(validacoes.camposEspecificos.percentualPreenchido * 0.2);
    }
    
    // Validar consistência (20 pontos)
    if (validacoes.consistenciaDados.valido) {
        score += 20;
    } else {
        erros.push(...validacoes.consistenciaDados.erros);
    }
    
    // Validar parâmetros da árvore (15 pontos)
    if (validacoes.parametrosArvore.valido) {
        score += 15;
    } else {
        avisos.push(...validacoes.parametrosArvore.avisos);
        score += 10; // Pontuação parcial para avisos
    }
    
    return {
        score: score,
        maxScore: maxScore,
        percentual: Math.round((score / maxScore) * 100),
        erros: erros,
        avisos: avisos,
        podeExecutar: erros.length === 0,
        qualidade: score >= 80 ? 'Alta' : score >= 60 ? 'Média' : 'Baixa',
        validacoes: validacoes
    };
}

function validarCamposObrigatoriosArvore() {
    const camposObrigatorios = [
        { id: 'numeroProcessoCnjArvore', nome: 'Número do Processo CNJ' },
        { id: 'clienteAutorArvore', nome: 'Cliente/Autor' },
        { id: 'cnpjCpfClienteArvore', nome: 'CNPJ/CPF' },
        { id: 'estadoProcessoArvore', nome: 'Estado' },
        { id: 'comarcaProcessoArvore', nome: 'Comarca' },
        { id: 'juizoProcessoArvore', nome: 'Juízo' },
        { id: 'instanciaProcessoArvore', nome: 'Instância' },
        { id: 'valorDaCausaArvore', nome: 'Valor da Causa' },
        { id: 'dataDistribuicaoArvore', nome: 'Data de Distribuição' },
        { id: 'statusResultadoArvore', nome: 'Status/Resultado' },
        { id: 'nomeModeloArvore', nome: 'Nome do Modelo' },
        { id: 'areaJuridicaModeloArvore', nome: 'Área Jurídica' }
    ];
    
    let erros = [];
    
    camposObrigatorios.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (!elemento || !elemento.value.trim()) {
            erros.push(`Campo obrigatório não preenchido: ${campo.nome}`);
        }
    });
    
    // Validar formato CNJ
    const cnj = document.getElementById('numeroProcessoCnjArvore')?.value;
    if (cnj && !validarFormatoCNJ(cnj)) {
        erros.push('Número CNJ deve seguir o formato: 1234567-89.2024.8.26.0100');
    }
    
    // Validar valor da causa
    const valor = document.getElementById('valorDaCausaArvore')?.value;
    if (valor && !validarValorMonetario(valor)) {
        erros.push('Valor da causa deve ser um valor monetário válido');
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarVolumeDadosArvore(areaConfig) {
    if (!areaConfig) return { valido: false, critico: true, erros: ['Área jurídica não reconhecida'] };
    
    const volumeAtual = parseInt(document.getElementById('tamanhoAmostraArvore')?.value) || 0;
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 0.9); // 10% menos para árvores
    
    if (volumeAtual === 0) {
        return {
            valido: false,
            critico: true,
            erros: ['Tamanho da amostra não foi definido']
        };
    }
    
    if (volumeAtual < volumeMinimo * 0.4) { // Mais tolerante que regressão
        return {
            valido: false,
            critico: true,
            erros: [`Volume crítico: ${volumeAtual} casos (mínimo absoluto: ${Math.round(volumeMinimo * 0.4)})`]
        };
    }
    
    if (volumeAtual < volumeMinimo) {
        return {
            valido: false,
            critico: false,
            avisos: [`Volume abaixo do recomendado: ${volumeAtual}/${volumeMinimo} casos. Árvores são mais tolerantes a volumes menores.`]
        };
    }
    
    return { valido: true };
}

function validarCamposEspecificosSelecionadosArvore(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return { valido: false, avisos: ['Área não configurada'] };
    
    const checkboxes = document.querySelectorAll('input[name="campos_especificos_arvore[]"]:checked');
    const selecionados = checkboxes.length;
    const disponiveis = areaConfig.campos_especificos.length;
    const percentual = (selecionados / disponiveis) * 100;
    
    if (selecionados === 0) {
        return {
            valido: false,
            percentualPreenchido: 0,
            avisos: ['Nenhum campo específico da área foi selecionado. Árvores de decisão se beneficiam de features interpretáveis.']
        };
    }
    
    if (percentual < 40) { // Mais tolerante que regressão (40% vs 50%)
        return {
            valido: false,
            percentualPreenchido: percentual / 100,
            avisos: [`Poucos campos específicos selecionados: ${selecionados}/${disponiveis} (${Math.round(percentual)}%). Recomendado para árvores: pelo menos 60%.`]
        };
    }
    
    return {
        valido: true,
        percentualPreenchido: 1,
        selecionados: selecionados,
        percentual: percentual
    };
}

function validarConsistenciaDadosArvore() {
    let erros = [];
    
    // Validar consistência temporal
    const dataDistribuicao = new Date(document.getElementById('dataDistribuicaoArvore')?.value);
    if (dataDistribuicao > new Date()) {
        erros.push('Data de distribuição não pode ser futura');
    }
    
    if (dataDistribuicao < new Date('2000-01-01')) {
        erros.push('Data de distribuição muito antiga (anterior a 2000)');
    }
    
    // Validar valor da causa vs área
    const area = document.getElementById('areaJuridicaModeloArvore')?.value;
    const valorTexto = document.getElementById('valorDaCausaArvore')?.value;
    const valor = parsearValorMonetario(valorTexto);
    
    if (valor > 0) {
        const limitesArea = {
            'familia': { min: 0, max: 1000000 },
            'consumidor': { min: 100, max: 500000 },
            'trabalhista': { min: 1000, max: 2000000 },
            'civil': { min: 0, max: 10000000 },
            'empresarial': { min: 5000, max: 50000000 }
        };
        
        const limite = limitesArea[area];
        if (limite && (valor < limite.min || valor > limite.max)) {
            erros.push(`Valor da causa (R$ ${valor.toLocaleString()}) incompatível com ${MATRIZ_AREAS_JURIDICAS[area]?.nome}`);
        }
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarParametrosArvore() {
    let avisos = [];
    
    // Validar configurações específicas de árvore (max_depth, min_samples_split, etc.)
    const maxDepth = parseInt(document.getElementById('maxDepthArvore')?.value);
    if (maxDepth && (maxDepth < 2 || maxDepth > 20)) {
        avisos.push('Profundidade máxima recomendada: 3 a 15 níveis');
    }
    
    // Validar min_samples_split
    const minSamplesSplit = parseInt(document.getElementById('minSamplesSplit')?.value);
    if (minSamplesSplit && minSamplesSplit < 2) {
        avisos.push('Mínimo de amostras para divisão deve ser pelo menos 2');
    }
    
    // Validar objetivo de classificação
    const objetivo = document.getElementById('objetivoClassificacao')?.value;
    if (!objetivo) {
        avisos.push('Selecione um objetivo de classificação específico');
    }
    
    return {
        valido: avisos.length === 0,
        avisos: avisos
    };
}

async function testarModeloArvoreDecisao() {
    console.log('🌳 Iniciando validação avançada do modelo de árvore de decisão...');
    
    // Executar validação completa
    const validacao = validarModeloArvoreDecisao();
    
    // Mostrar resultado da validação
    mostrarResultadoValidacaoArvore(validacao);
    
    // Se há erros críticos, não prosseguir
    if (!validacao.podeExecutar) {
        console.log('❌ Validação falhou. Corrigir erros antes de continuar.');
        return;
    }
    
    // Se passou na validação, executar teste do modelo
    console.log('✅ Validação passou. Executando teste da árvore de decisão...');
    
    const formData = coletarDadosFormulario('formEditarArvoreDecisao');
    
    // Adicionar dados de validação ao formData
    formData.validacao = validacao;
    
    try {
        const response = await fetch('/api/estatistica/testar-arvore-decisao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'arvore-decisao');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de árvore de decisão');
    }
}

function mostrarResultadoValidacaoArvore(validacao) {
    // Criar modal de resultado da validação
    const modalHtml = `
        <div class="modal fade" id="modalValidacaoArvore" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-${validacao.podeExecutar ? 'success' : 'danger'} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${validacao.podeExecutar ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                            Validação Árvore de Decisão - Score: ${validacao.percentual}%
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-12">
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${validacao.qualidade === 'Alta' ? 'success' : validacao.qualidade === 'Média' ? 'warning' : 'danger'}" 
                                         style="width: ${validacao.percentual}%">
                                        ${validacao.percentual}% - Qualidade ${validacao.qualidade}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${validacao.erros.length > 0 ? `
                        <div class="alert alert-danger">
                            <h6><i class="fas fa-times-circle me-2"></i>Erros Encontrados (${validacao.erros.length})</h6>
                            <ul class="mb-0">
                                ${validacao.erros.map(erro => `<li>${erro}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.avisos.length > 0 ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Avisos (${validacao.avisos.length})</h6>
                            <ul class="mb-0">
                                ${validacao.avisos.map(aviso => `<li>${aviso}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.podeExecutar ? `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-tree me-2"></i>Árvore de Decisão Aprovada</h6>
                            <p class="mb-0">O modelo passou em todas as validações críticas e está pronto para criar uma árvore interpretável.</p>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        ${validacao.podeExecutar ? '<button type="button" class="btn btn-success" onclick="executarArvoreValidada()" data-bs-dismiss="modal">Executar Árvore</button>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modalValidacaoArvore');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalValidacaoArvore'));
    modal.show();
}

function executarArvoreValidada() {
    console.log('🌳 Executando árvore de decisão validada...');
    // Aqui seria a execução real do modelo
    mostrarSucesso('Árvore de decisão executada com sucesso! Modelo interpretável gerado.');
}

// ============= FUNÇÕES ESPECÍFICAS REDES NEURAIS =============

function atualizarParametrosNeurais() {
    const area = document.getElementById('areaJuridicaModeloNeurais')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    // Atualizar campos específicos da área
    atualizarCamposEspecificosAreaNeurais(area);
    
    // Atualizar validação de volume mínimo (3x mais dados que outros modelos)
    atualizarVolumeMinimoAreaNeurais(area);
    
    // Atualizar tipos de modelo neural
    const modeloSelect = document.getElementById('modeloNeuralEdit');
    if (modeloSelect && dados?.redesNeurais) {
        modeloSelect.innerHTML = '';
        dados.redesNeurais.tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            modeloSelect.appendChild(option);
        });
    }
    
    // Atualizar barra de precisão esperada (redes neurais têm maior potencial)
    if (areaConfig) {
        const precisaoBar = document.getElementById('precisaoEsperadaNeurais');
        const classificacaoTexto = document.getElementById('classificacaoPrecisaoNeurais');
        
        // Redes neurais têm o maior potencial de precisão (+3%)
        const precisaoNeurais = Math.min(areaConfig.precisao_media + 3, 95);
        
        if (precisaoBar) {
            precisaoBar.style.width = precisaoNeurais + '%';
            precisaoBar.textContent = Math.round(precisaoNeurais) + '% - ' + 
                (precisaoNeurais >= 88 ? 'Precisão Máxima' :
                 precisaoNeurais >= 75 ? 'Precisão Moderada' : 'Baixa Precisão');
            
            // Atualizar cor da barra (redes neurais sempre verde quando adequadas)
            precisaoBar.className = 'progress-bar ' +
                'bg-primary';
        }
        
        if (classificacaoTexto) {
            classificacaoTexto.innerHTML = `<i class="fas fa-brain"></i> ${areaConfig.nome} - Máxima capacidade preditiva com dados suficientes`;
        }
    }
}

function atualizarCamposEspecificosAreaNeurais(area) {
    const container = document.getElementById('camposEspecificosAreaNeurais');
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!container || !areaConfig) return;
    
    let html = `
        <div class="row">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="fas fa-brain me-2"></i>
                    Campos Específicos - ${areaConfig.nome}
                    <small class="text-muted">(${areaConfig.campos_especificos.length} campos)</small>
                </h6>
            </div>
        </div>
        <div class="row">
    `;
    
    // Criar checkboxes para cada campo específico
    areaConfig.campos_especificos.forEach((campo, index) => {
        const nomeFormatado = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="campo_neurais_${campo}" name="campos_especificos_neurais[]" value="${campo}">
                    <label class="form-check-label" for="campo_neurais_${campo}">
                        ${nomeFormatado}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-info mb-0">
                    <i class="fas fa-network-wired me-2"></i>
                    <strong>Vantagem das Redes Neurais:</strong> ${areaConfig.caracteristicas}. 
                    Redes neurais capturam padrões complexos e não-lineares, oferecendo a maior precisão quando bem treinadas.
                    Volume mínimo: <strong>${(areaConfig.volume_minimo * 3).toLocaleString()}</strong> casos (3x mais que outros modelos).
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function atualizarVolumeMinimoAreaNeurais(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return;
    
    // Redes neurais precisam de 3x mais dados que outros modelos
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 3);
    
    const volumeMinimoElement = document.getElementById('volumeMinimoNeurais');
    if (volumeMinimoElement) {
        volumeMinimoElement.textContent = volumeMinimo.toLocaleString();
    }
    
    // Simular volume atual (em produção, isso viria de uma API)
    const volumeAtualSimulado = Math.floor(Math.random() * 8000) + 1000;
    validarVolumeMinimoNeurais(volumeAtualSimulado);
}

function validarVolumeMinimoNeurais(volumeAtual = null) {
    const area = document.getElementById('areaJuridicaModeloNeurais')?.value || 'civil';
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!areaConfig) return;
    
    // Se não foi passado volume atual, pegar do input
    if (volumeAtual === null) {
        const inputTamanho = document.getElementById('tamanhoAmostraNeurais');
        volumeAtual = parseInt(inputTamanho?.value) || 0;
    }
    
    // Redes neurais precisam de 3x mais dados
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 3);
    const percentual = Math.min((volumeAtual / volumeMinimo) * 100, 100);
    
    // Atualizar elementos da interface
    const volumeAtualElement = document.getElementById('volumeAtualNeurais');
    const statusVolumeElement = document.getElementById('statusVolumeNeurais');
    const progressoVolumeElement = document.getElementById('progressoVolumeNeurais');
    const alertStatusVolume = document.getElementById('alertStatusVolumeNeurais');
    const riscoOverfittingElement = document.getElementById('riscoOverfittingNeurais');
    const precisaoTextoElement = document.getElementById('precisaoEsperadaTextoNeurais');
    
    if (volumeAtualElement) {
        volumeAtualElement.textContent = volumeAtual.toLocaleString();
    }
    
    if (progressoVolumeElement) {
        progressoVolumeElement.style.width = percentual + '%';
        progressoVolumeElement.textContent = Math.round(percentual) + '%';
        progressoVolumeElement.setAttribute('aria-valuenow', percentual);
        
        // Atualizar cor da barra de progresso
        progressoVolumeElement.className = 'progress-bar progress-bar-striped ' +
            'bg-primary';
    }
    
    // Calcular precisão estimada e risco de overfitting
    let precisaoEstimada = areaConfig.precisao_media + 3; // Bonus para redes neurais
    let statusTexto = '';
    let alertClass = 'alert-success';
    let riscoTexto = '';
    
    if (volumeAtual >= volumeMinimo) {
        statusTexto = 'Volume Adequado';
        alertClass = 'alert-success';
        precisaoEstimada = Math.min(areaConfig.precisao_media + 3, 95);
        riscoTexto = 'Risco baixo de overfitting - Rede bem generalizada';
    } else if (volumeAtual >= volumeMinimo * 0.7) {
        statusTexto = 'Volume Insuficiente';
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.85; // Penalidade maior que outros modelos
        riscoTexto = 'Risco moderado de overfitting - Considere regularização';
    } else {
        statusTexto = 'Volume Crítico';
        alertClass = 'alert-danger';
        precisaoEstimada = areaConfig.precisao_media * 0.6; // Penalidade severa
        riscoTexto = 'RISCO ALTO de overfitting severo - Volume inadequado para redes neurais';
    }
    
    if (statusVolumeElement) {
        statusVolumeElement.textContent = statusTexto;
    }
    
    if (alertStatusVolume) {
        alertStatusVolume.className = `alert mb-0 ${alertClass}`;
    }
    
    if (precisaoTextoElement) {
        precisaoTextoElement.textContent = `Precisão estimada: ${Math.round(precisaoEstimada)}%`;
    }
    
    if (riscoOverfittingElement) {
        riscoOverfittingElement.textContent = riscoTexto;
    }
}

function validarModeloRedesNeurais() {
    const area = document.getElementById('areaJuridicaModeloNeurais')?.value;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let validacoes = {
        camposObrigatorios: validarCamposObrigatoriosNeurais(),
        volumeDados: validarVolumeDadosNeurais(areaConfig),
        camposEspecificos: validarCamposEspecificosSelecionadosNeurais(area),
        consistenciaDados: validarConsistenciaDadosNeurais(),
        arquiteturaRede: validarArquiteturaRede()
    };
    
    let erros = [];
    let avisos = [];
    let score = 0;
    let maxScore = 100;
    
    // Validar campos obrigatórios (25 pontos)
    if (validacoes.camposObrigatorios.valido) {
        score += 25;
    } else {
        erros.push(...validacoes.camposObrigatorios.erros);
    }
    
    // Validar volume de dados (30 pontos - mais crítico para redes neurais)
    if (validacoes.volumeDados.valido) {
        score += 30;
    } else {
        if (validacoes.volumeDados.critico) {
            erros.push(...validacoes.volumeDados.erros);
        } else {
            avisos.push(...validacoes.volumeDados.avisos);
            score += 10; // Penalidade severa para redes neurais
        }
    }
    
    // Validar campos específicos (20 pontos)
    if (validacoes.camposEspecificos.valido) {
        score += 20;
    } else {
        avisos.push(...validacoes.camposEspecificos.avisos);
        score += Math.round(validacoes.camposEspecificos.percentualPreenchido * 0.2);
    }
    
    // Validar consistência (15 pontos)
    if (validacoes.consistenciaDados.valido) {
        score += 15;
    } else {
        erros.push(...validacoes.consistenciaDados.erros);
    }
    
    // Validar arquitetura da rede (10 pontos)
    if (validacoes.arquiteturaRede.valido) {
        score += 10;
    } else {
        avisos.push(...validacoes.arquiteturaRede.avisos);
        score += 5; // Pontuação parcial para avisos
    }
    
    return {
        score: score,
        maxScore: maxScore,
        percentual: Math.round((score / maxScore) * 100),
        erros: erros,
        avisos: avisos,
        podeExecutar: erros.length === 0,
        qualidade: score >= 80 ? 'Alta' : score >= 60 ? 'Média' : 'Baixa',
        validacoes: validacoes
    };
}

function validarCamposObrigatoriosNeurais() {
    const camposObrigatorios = [
        { id: 'numeroProcessoCnjNeurais', nome: 'Número do Processo CNJ' },
        { id: 'clienteAutorNeurais', nome: 'Cliente/Autor' },
        { id: 'cnpjCpfClienteNeurais', nome: 'CNPJ/CPF' },
        { id: 'estadoProcessoNeurais', nome: 'Estado' },
        { id: 'comarcaProcessoNeurais', nome: 'Comarca' },
        { id: 'juizoProcessoNeurais', nome: 'Juízo' },
        { id: 'instanciaProcessoNeurais', nome: 'Instância' },
        { id: 'valorDaCausaNeurais', nome: 'Valor da Causa' },
        { id: 'dataDistribuicaoNeurais', nome: 'Data de Distribuição' },
        { id: 'statusResultadoNeurais', nome: 'Status/Resultado' },
        { id: 'nomeModeloNeurais', nome: 'Nome do Modelo' },
        { id: 'areaJuridicaModeloNeurais', nome: 'Área Jurídica' }
    ];
    
    let erros = [];
    
    camposObrigatorios.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (!elemento || !elemento.value.trim()) {
            erros.push(`Campo obrigatório não preenchido: ${campo.nome}`);
        }
    });
    
    // Validar formato CNJ
    const cnj = document.getElementById('numeroProcessoCnjNeurais')?.value;
    if (cnj && !validarFormatoCNJ(cnj)) {
        erros.push('Número CNJ deve seguir o formato: 1234567-89.2024.8.26.0100');
    }
    
    // Validar valor da causa
    const valor = document.getElementById('valorDaCausaNeurais')?.value;
    if (valor && !validarValorMonetario(valor)) {
        erros.push('Valor da causa deve ser um valor monetário válido');
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarVolumeDadosNeurais(areaConfig) {
    if (!areaConfig) return { valido: false, critico: true, erros: ['Área jurídica não reconhecida'] };
    
    const volumeAtual = parseInt(document.getElementById('tamanhoAmostraNeurais')?.value) || 0;
    const volumeMinimo = Math.round(areaConfig.volume_minimo * 3); // 3x mais para redes neurais
    
    if (volumeAtual === 0) {
        return {
            valido: false,
            critico: true,
            erros: ['Tamanho da amostra não foi definido para a rede neural']
        };
    }
    
    if (volumeAtual < volumeMinimo * 0.6) { // Redes neurais são muito sensíveis
        return {
            valido: false,
            critico: true,
            erros: [`Volume crítico para rede neural: ${volumeAtual} casos (mínimo absoluto: ${Math.round(volumeMinimo * 0.6)}). Risco alto de overfitting.`]
        };
    }
    
    if (volumeAtual < volumeMinimo) {
        return {
            valido: false,
            critico: false,
            avisos: [`Volume abaixo do recomendado para rede neural: ${volumeAtual}/${volumeMinimo} casos. Considere técnicas de regularização.`]
        };
    }
    
    return { valido: true };
}

function validarCamposEspecificosSelecionadosNeurais(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return { valido: false, avisos: ['Área não configurada'] };
    
    const checkboxes = document.querySelectorAll('input[name="campos_especificos_neurais[]"]:checked');
    const selecionados = checkboxes.length;
    const disponiveis = areaConfig.campos_especificos.length;
    const percentual = (selecionados / disponiveis) * 100;
    
    if (selecionados === 0) {
        return {
            valido: false,
            percentualPreenchido: 0,
            avisos: ['Nenhum campo específico da área foi selecionado. Redes neurais se beneficiam de muitas features.']
        };
    }
    
    if (percentual < 60) { // Redes neurais precisam de mais features
        return {
            valido: false,
            percentualPreenchido: percentual / 100,
            avisos: [`Poucos campos específicos selecionados: ${selecionados}/${disponiveis} (${Math.round(percentual)}%). Recomendado para redes neurais: pelo menos 80%.`]
        };
    }
    
    return {
        valido: true,
        percentualPreenchido: 1,
        selecionados: selecionados,
        percentual: percentual
    };
}

function validarConsistenciaDadosNeurais() {
    let erros = [];
    
    // Validar consistência temporal
    const dataDistribuicao = new Date(document.getElementById('dataDistribuicaoNeurais')?.value);
    if (dataDistribuicao > new Date()) {
        erros.push('Data de distribuição não pode ser futura');
    }
    
    if (dataDistribuicao < new Date('2000-01-01')) {
        erros.push('Data de distribuição muito antiga (anterior a 2000)');
    }
    
    // Validar valor da causa vs área
    const area = document.getElementById('areaJuridicaModeloNeurais')?.value;
    const valorTexto = document.getElementById('valorDaCausaNeurais')?.value;
    const valor = parsearValorMonetario(valorTexto);
    
    if (valor > 0) {
        const limitesArea = {
            'familia': { min: 0, max: 1000000 },
            'consumidor': { min: 100, max: 500000 },
            'trabalhista': { min: 1000, max: 2000000 },
            'civil': { min: 0, max: 10000000 },
            'empresarial': { min: 5000, max: 50000000 }
        };
        
        const limite = limitesArea[area];
        if (limite && (valor < limite.min || valor > limite.max)) {
            erros.push(`Valor da causa (R$ ${valor.toLocaleString()}) incompatível com ${MATRIZ_AREAS_JURIDICAS[area]?.nome}`);
        }
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarArquiteturaRede() {
    let avisos = [];
    
    // Validar arquitetura base selecionada
    const arquitetura = document.getElementById('arquiteturaBase')?.value;
    if (!arquitetura) {
        avisos.push('Selecione uma arquitetura base para a rede neural');
    }
    
    // Validar número de camadas
    const camadas = document.querySelectorAll('select[name="tipoCamada[]"]').length;
    if (camadas < 2) {
        avisos.push('Rede neural deve ter pelo menos 2 camadas (entrada + saída)');
    }
    
    if (camadas > 20) {
        avisos.push('Muitas camadas podem causar problemas de vanishing gradient');
    }
    
    // Verificar se há camadas de regularização
    const hasDropout = Array.from(document.querySelectorAll('select[name="tipoCamada[]"]')).some(select => select.value === 'dropout');
    const hasBatchNorm = Array.from(document.querySelectorAll('select[name="tipoCamada[]"]')).some(select => select.value === 'batch_norm');
    
    if (!hasDropout && !hasBatchNorm) {
        avisos.push('Considere adicionar camadas de regularização (Dropout ou Batch Normalization)');
    }
    
    return {
        valido: avisos.length === 0,
        avisos: avisos
    };
}

async function testarModeloRedesNeurais() {
    console.log('🧠 Iniciando validação avançada do modelo de redes neurais...');
    
    // Executar validação completa
    const validacao = validarModeloRedesNeurais();
    
    // Mostrar resultado da validação
    mostrarResultadoValidacaoNeurais(validacao);
    
    // Se há erros críticos, não prosseguir
    if (!validacao.podeExecutar) {
        console.log('❌ Validação falhou. Corrigir erros antes de continuar.');
        return;
    }
    
    // Se passou na validação, executar teste do modelo
    console.log('✅ Validação passou. Executando teste da rede neural...');
    
    const formData = coletarDadosFormulario('formEditarRedesNeurais');
    
    // Adicionar dados de validação ao formData
    formData.validacao = validacao;
    
    try {
        const response = await fetch('/api/estatistica/testar-redes-neurais', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'redes-neurais');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de redes neurais');
    }
}

function mostrarResultadoValidacaoNeurais(validacao) {
    // Criar modal de resultado da validação
    const modalHtml = `
        <div class="modal fade" id="modalValidacaoNeurais" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-${validacao.podeExecutar ? 'success' : 'danger'} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${validacao.podeExecutar ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                            Validação Redes Neurais - Score: ${validacao.percentual}%
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-12">
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${validacao.qualidade === 'Alta' ? 'success' : validacao.qualidade === 'Média' ? 'warning' : 'danger'}" 
                                         style="width: ${validacao.percentual}%">
                                        ${validacao.percentual}% - Qualidade ${validacao.qualidade}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${validacao.erros.length > 0 ? `
                        <div class="alert alert-danger">
                            <h6><i class="fas fa-times-circle me-2"></i>Erros Encontrados (${validacao.erros.length})</h6>
                            <ul class="mb-0">
                                ${validacao.erros.map(erro => `<li>${erro}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.avisos.length > 0 ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Avisos (${validacao.avisos.length})</h6>
                            <ul class="mb-0">
                                ${validacao.avisos.map(aviso => `<li>${aviso}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.podeExecutar ? `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-brain me-2"></i>Rede Neural Aprovada</h6>
                            <p class="mb-0">O modelo passou em todas as validações críticas e está pronto para treinamento com máxima precisão.</p>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        ${validacao.podeExecutar ? '<button type="button" class="btn btn-success" onclick="executarRedeValidada()" data-bs-dismiss="modal">Treinar Rede Neural</button>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modalValidacaoNeurais');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalValidacaoNeurais'));
    modal.show();
}

function executarRedeValidada() {
    console.log('🧠 Iniciando treinamento da rede neural validada...');
    // Aqui seria o treinamento real do modelo
    mostrarSucesso('Rede neural iniciou treinamento! Máxima precisão esperada.');
}

// ============= FUNÇÕES ESPECÍFICAS SÉRIES TEMPORAIS =============

function atualizarParametrosTemporais() {
    const area = document.getElementById('areaJuridicaModeloTemporais')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    // Atualizar campos específicos da área
    atualizarCamposEspecificosAreaTemporais(area);
    
    // Atualizar validação de período histórico
    atualizarPeriodoMinimoAreaTemporais(area);
    
    // Atualizar tipos de análise temporal
    const tipoSelect = document.getElementById('tipoAnaliseTemporaisEdit');
    if (tipoSelect && dados?.seriesTemporais) {
        tipoSelect.innerHTML = '';
        dados.seriesTemporais.tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.value;
            option.textContent = tipo.text;
            tipoSelect.appendChild(option);
        });
    }
}

function atualizarCamposEspecificosAreaTemporais(area) {
    const container = document.getElementById('camposEspecificosAreaTemporais');
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!container || !areaConfig) return;
    
    let html = `
        <div class="row">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="fas fa-chart-area me-2"></i>
                    Campos Específicos - ${areaConfig.nome}
                    <small class="text-muted">(${areaConfig.campos_especificos.length} campos)</small>
                </h6>
            </div>
        </div>
        <div class="row">
    `;
    
    // Criar checkboxes para cada campo específico
    areaConfig.campos_especificos.forEach((campo, index) => {
        const nomeFormatado = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="campo_temporais_${campo}" name="campos_especificos_temporais[]" value="${campo}">
                    <label class="form-check-label" for="campo_temporais_${campo}">
                        ${nomeFormatado}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-primary mb-0">
                    <i class="fas fa-clock me-2"></i>
                    <strong>Vantagem das Séries Temporais:</strong> ${areaConfig.caracteristicas}. 
                    Séries temporais identificam padrões sazonais, tendências e ciclos jurídicos ao longo do tempo.
                    Período mínimo: <strong>24 meses</strong> de dados históricos.
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function atualizarPeriodoMinimoAreaTemporais(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return;
    
    // Período mínimo fixo de 24 meses para séries temporais
    const periodoMinimo = 24;
    
    const periodoMinimoElement = document.getElementById('periodoMinimoTemporais');
    if (periodoMinimoElement) {
        periodoMinimoElement.textContent = periodoMinimo.toString();
    }
    
    // Simular período atual (em produção, isso viria de uma API)
    const periodoAtualSimulado = Math.floor(Math.random() * 48) + 6;
    validarPeriodoMinimoTemporais(periodoAtualSimulado);
}

function validarPeriodoMinimoTemporais(periodoAtual = null) {
    const area = document.getElementById('areaJuridicaModeloTemporais')?.value || 'civil';
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!areaConfig) return;
    
    // Se não foi passado período atual, pegar do input
    if (periodoAtual === null) {
        const inputPeriodo = document.getElementById('periodoHistoricoMeses');
        periodoAtual = parseInt(inputPeriodo?.value) || 0;
    }
    
    // Período mínimo de 24 meses para séries temporais
    const periodoMinimo = 24;
    const percentual = Math.min((periodoAtual / periodoMinimo) * 100, 100);
    
    // Atualizar elementos da interface
    const periodoAtualElement = document.getElementById('periodoAtualTemporais');
    const statusPeriodoElement = document.getElementById('statusPeriodoTemporais');
    const progressoPeriodoElement = document.getElementById('progressoPeriodoTemporais');
    const alertStatusPeriodo = document.getElementById('alertStatusPeriodoTemporais');
    const impactoTemporalElement = document.getElementById('impactoTemporalTemporais');
    const precisaoTextoElement = document.getElementById('precisaoEsperadaTextoTemporais');
    
    if (periodoAtualElement) {
        periodoAtualElement.textContent = periodoAtual.toString();
    }
    
    if (progressoPeriodoElement) {
        progressoPeriodoElement.style.width = percentual + '%';
        progressoPeriodoElement.textContent = Math.round(percentual) + '%';
        progressoPeriodoElement.setAttribute('aria-valuenow', percentual);
        
        // Atualizar cor da barra de progresso
        progressoPeriodoElement.className = 'progress-bar progress-bar-striped ' +
            'bg-primary';
    }
    
    // Calcular precisão estimada baseada no período histórico
    let precisaoEstimada = areaConfig.precisao_media + 2; // Bonus para séries temporais bem configuradas
    let statusTexto = '';
    let alertClass = 'alert-success';
    let impactoTexto = '';
    
    if (periodoAtual >= periodoMinimo) {
        statusTexto = 'Período Adequado';
        alertClass = 'alert-success';
        precisaoEstimada = Math.min(areaConfig.precisao_media + 2, 94);
        impactoTexto = 'Período suficiente para identificar sazonalidades e tendências';
    } else if (periodoAtual >= periodoMinimo * 0.75) { // 18+ meses
        statusTexto = 'Período Limitado';
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.92;
        impactoTexto = 'Período pode ser insuficiente para capturar todos os padrões sazonais';
    } else if (periodoAtual >= 12) { // 12+ meses
        statusTexto = 'Período Insuficiente';
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.85;
        impactoTexto = 'Período muito curto - pode perder sazonalidades anuais importantes';
    } else {
        statusTexto = 'Período Crítico';
        alertClass = 'alert-danger';
        precisaoEstimada = areaConfig.precisao_media * 0.70;
        impactoTexto = 'PERÍODO INADEQUADO - Dados insuficientes para análise temporal confiável';
    }
    
    if (statusPeriodoElement) {
        statusPeriodoElement.textContent = statusTexto;
    }
    
    if (alertStatusPeriodo) {
        alertStatusPeriodo.className = `alert mb-0 ${alertClass}`;
    }
    
    if (precisaoTextoElement) {
        precisaoTextoElement.textContent = `Precisão estimada: ${Math.round(precisaoEstimada)}%`;
    }
    
    if (impactoTemporalElement) {
        impactoTemporalElement.textContent = impactoTexto;
    }
}

function validarModeloSeriesTemporais() {
    const area = document.getElementById('areaJuridicaModeloTemporais')?.value;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let validacoes = {
        camposObrigatorios: validarCamposObrigatoriosTemporais(),
        periodoHistorico: validarPeriodoHistoricoTemporais(),
        camposEspecificos: validarCamposEspecificosSelecionadosTemporais(area),
        consistenciaDados: validarConsistenciaDadosTemporais(),
        configuracaoTemporal: validarConfiguracaoTemporal()
    };
    
    let erros = [];
    let avisos = [];
    let score = 0;
    let maxScore = 100;
    
    // Validar campos obrigatórios (25 pontos)
    if (validacoes.camposObrigatorios.valido) {
        score += 25;
    } else {
        erros.push(...validacoes.camposObrigatorios.erros);
    }
    
    // Validar período histórico (35 pontos - mais crítico para séries temporais)
    if (validacoes.periodoHistorico.valido) {
        score += 35;
    } else {
        if (validacoes.periodoHistorico.critico) {
            erros.push(...validacoes.periodoHistorico.erros);
        } else {
            avisos.push(...validacoes.periodoHistorico.avisos);
            score += Math.round(validacoes.periodoHistorico.pontuacaoParcial);
        }
    }
    
    // Validar campos específicos (15 pontos)
    if (validacoes.camposEspecificos.valido) {
        score += 15;
    } else {
        avisos.push(...validacoes.camposEspecificos.avisos);
        score += Math.round(validacoes.camposEspecificos.percentualPreenchido * 0.15);
    }
    
    // Validar consistência (15 pontos)
    if (validacoes.consistenciaDados.valido) {
        score += 15;
    } else {
        erros.push(...validacoes.consistenciaDados.erros);
    }
    
    // Validar configuração temporal (10 pontos)
    if (validacoes.configuracaoTemporal.valido) {
        score += 10;
    } else {
        avisos.push(...validacoes.configuracaoTemporal.avisos);
        score += 5;
    }
    
    return {
        score: score,
        maxScore: maxScore,
        percentual: Math.round((score / maxScore) * 100),
        erros: erros,
        avisos: avisos,
        podeExecutar: erros.length === 0,
        qualidade: score >= 80 ? 'Alta' : score >= 60 ? 'Média' : 'Baixa',
        validacoes: validacoes
    };
}

function validarCamposObrigatoriosTemporais() {
    const camposObrigatorios = [
        { id: 'numeroProcessoCnjTemporais', nome: 'Número do Processo CNJ' },
        { id: 'clienteAutorTemporais', nome: 'Cliente/Autor' },
        { id: 'cnpjCpfClienteTemporais', nome: 'CNPJ/CPF' },
        { id: 'estadoProcessoTemporais', nome: 'Estado' },
        { id: 'comarcaProcessoTemporais', nome: 'Comarca' },
        { id: 'juizoProcessoTemporais', nome: 'Juízo' },
        { id: 'instanciaProcessoTemporais', nome: 'Instância' },
        { id: 'valorDaCausaTemporais', nome: 'Valor da Causa' },
        { id: 'dataDistribuicaoTemporais', nome: 'Data de Distribuição' },
        { id: 'statusResultadoTemporais', nome: 'Status/Resultado' },
        { id: 'nomeModeloTemporais', nome: 'Nome do Modelo' },
        { id: 'areaJuridicaModeloTemporais', nome: 'Área Jurídica' }
    ];
    
    let erros = [];
    
    camposObrigatorios.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (!elemento || !elemento.value.trim()) {
            erros.push(`Campo obrigatório não preenchido: ${campo.nome}`);
        }
    });
    
    // Validar formato CNJ
    const cnj = document.getElementById('numeroProcessoCnjTemporais')?.value;
    if (cnj && !validarFormatoCNJ(cnj)) {
        erros.push('Número CNJ deve seguir o formato: 1234567-89.2024.8.26.0100');
    }
    
    // Validar valor da causa
    const valor = document.getElementById('valorDaCausaTemporais')?.value;
    if (valor && !validarValorMonetario(valor)) {
        erros.push('Valor da causa deve ser um valor monetário válido');
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarPeriodoHistoricoTemporais() {
    const periodoAtual = parseInt(document.getElementById('periodoHistoricoMeses')?.value) || 0;
    const periodoMinimo = 24;
    
    if (periodoAtual === 0) {
        return {
            valido: false,
            critico: true,
            erros: ['Período histórico não foi definido']
        };
    }
    
    if (periodoAtual < 12) {
        return {
            valido: false,
            critico: true,
            erros: [`Período crítico: ${periodoAtual} meses (mínimo absoluto: 12 meses)`]
        };
    }
    
    if (periodoAtual < periodoMinimo) {
        const pontuacaoParcial = Math.round(35 * (periodoAtual / periodoMinimo));
        return {
            valido: false,
            critico: false,
            pontuacaoParcial: pontuacaoParcial,
            avisos: [`Período abaixo do recomendado: ${periodoAtual}/${periodoMinimo} meses. Pode comprometer a identificação de sazonalidades.`]
        };
    }
    
    return { valido: true };
}

function validarCamposEspecificosSelecionadosTemporais(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return { valido: false, avisos: ['Área não configurada'] };
    
    const checkboxes = document.querySelectorAll('input[name="campos_especificos_temporais[]"]:checked');
    const selecionados = checkboxes.length;
    const disponiveis = areaConfig.campos_especificos.length;
    const percentual = (selecionados / disponiveis) * 100;
    
    if (selecionados === 0) {
        return {
            valido: false,
            percentualPreenchido: 0,
            avisos: ['Nenhum campo específico da área foi selecionado. Séries temporais se beneficiam de variáveis explicativas.']
        };
    }
    
    if (percentual < 30) { // Séries temporais são mais tolerantes a menos campos
        return {
            valido: false,
            percentualPreenchido: percentual / 100,
            avisos: [`Poucos campos específicos selecionados: ${selecionados}/${disponiveis} (${Math.round(percentual)}%). Recomendado para séries temporais: pelo menos 40%.`]
        };
    }
    
    return {
        valido: true,
        percentualPreenchido: 1,
        selecionados: selecionados,
        percentual: percentual
    };
}

function validarConsistenciaDadosTemporais() {
    let erros = [];
    
    // Validar consistência temporal
    const dataDistribuicao = new Date(document.getElementById('dataDistribuicaoTemporais')?.value);
    if (dataDistribuicao > new Date()) {
        erros.push('Data de distribuição não pode ser futura');
    }
    
    if (dataDistribuicao < new Date('2000-01-01')) {
        erros.push('Data de distribuição muito antiga (anterior a 2000)');
    }
    
    // Validar granularidade vs período
    const granularidade = document.getElementById('granularidadeTemporal')?.value;
    const periodoMeses = parseInt(document.getElementById('periodoHistoricoMeses')?.value) || 0;
    
    const pontosMinimosPorGranularidade = {
        'diaria': 730,    // 2 anos * 365 dias
        'semanal': 104,   // 2 anos * 52 semanas
        'mensal': 24,     // 2 anos * 12 meses
        'trimestral': 8,  // 2 anos * 4 trimestres
        'semestral': 4,   // 2 anos * 2 semestres
        'anual': 5        // 5 anos mínimo
    };
    
    const pontosMinimos = pontosMinimosPorGranularidade[granularidade] || 24;
    const pontosDisponiveis = granularidade === 'mensal' ? periodoMeses : Math.floor(periodoMeses / 3);
    
    if (pontosDisponiveis < pontosMinimos * 0.5) {
        erros.push(`Período insuficiente para granularidade ${granularidade}: ${pontosDisponiveis} pontos (mínimo: ${Math.floor(pontosMinimos * 0.5)})`);
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarConfiguracaoTemporal() {
    let avisos = [];
    
    // Validar se há configuração de sazonalidade
    const temSazonalidade = document.getElementById('detectarSazonalidade')?.checked;
    if (!temSazonalidade) {
        avisos.push('Considere habilitar detecção de sazonalidade para séries temporais jurídicas');
    }
    
    // Validar método de decomposição
    const metodo = document.getElementById('metodoDecomposicao')?.value;
    if (!metodo) {
        avisos.push('Selecione um método de decomposição temporal');
    }
    
    // Validar janela de previsão
    const janela = parseInt(document.getElementById('janelaPrevisao')?.value);
    if (!janela || janela < 1) {
        avisos.push('Defina uma janela de previsão adequada');
    }
    
    return {
        valido: avisos.length === 0,
        avisos: avisos
    };
}

async function testarModeloSeriesTemporais() {
    console.log('📈 Iniciando validação avançada do modelo de séries temporais...');
    
    // Executar validação completa
    const validacao = validarModeloSeriesTemporais();
    
    // Mostrar resultado da validação
    mostrarResultadoValidacaoTemporais(validacao);
    
    // Se há erros críticos, não prosseguir
    if (!validacao.podeExecutar) {
        console.log('❌ Validação falhou. Corrigir erros antes de continuar.');
        return;
    }
    
    // Se passou na validação, executar teste do modelo
    console.log('✅ Validação passou. Executando teste de série temporal...');
    
    const formData = coletarDadosFormulario('formEditarSeriesTemporais');
    
    // Adicionar dados de validação ao formData
    formData.validacao = validacao;
    
    try {
        const response = await fetch('/api/estatistica/testar-series-temporais', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'series-temporais');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de séries temporais');
    }
}

function mostrarResultadoValidacaoTemporais(validacao) {
    // Criar modal de resultado da validação
    const modalHtml = `
        <div class="modal fade" id="modalValidacaoTemporais" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-${validacao.podeExecutar ? 'success' : 'danger'} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${validacao.podeExecutar ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                            Validação Séries Temporais - Score: ${validacao.percentual}%
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-12">
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${validacao.qualidade === 'Alta' ? 'success' : validacao.qualidade === 'Média' ? 'warning' : 'danger'}" 
                                         style="width: ${validacao.percentual}%">
                                        ${validacao.percentual}% - Qualidade ${validacao.qualidade}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${validacao.erros.length > 0 ? `
                        <div class="alert alert-danger">
                            <h6><i class="fas fa-times-circle me-2"></i>Erros Encontrados (${validacao.erros.length})</h6>
                            <ul class="mb-0">
                                ${validacao.erros.map(erro => `<li>${erro}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.avisos.length > 0 ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Avisos (${validacao.avisos.length})</h6>
                            <ul class="mb-0">
                                ${validacao.avisos.map(aviso => `<li>${aviso}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.podeExecutar ? `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-chart-area me-2"></i>Série Temporal Aprovada</h6>
                            <p class="mb-0">O modelo passou em todas as validações críticas e está pronto para análise temporal com identificação de padrões sazonais.</p>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        ${validacao.podeExecutar ? '<button type="button" class="btn btn-success" onclick="executarSerieValidada()" data-bs-dismiss="modal">Analisar Série Temporal</button>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modalValidacaoTemporais');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalValidacaoTemporais'));
    modal.show();
}

function executarSerieValidada() {
    console.log('📈 Executando análise de série temporal validada...');
    // Aqui seria a análise real da série temporal
    mostrarSucesso('Série temporal iniciou análise! Identificando padrões sazonais e tendências.');
}

// ============= FUNÇÕES ESPECÍFICAS ANÁLISE DE SOBREVIVÊNCIA =============

function atualizarParametrosSobrevivencia() {
    const area = document.getElementById('areaJuridicaModeloSobrevivencia')?.value || 'civil';
    const dados = window.dadosPorArea?.[area] || window.dadosPorArea?.civil;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    // Atualizar campos específicos da área
    atualizarCamposEspecificosAreaSobrevivencia(area);
    
    // Atualizar validação de eventos observados
    atualizarEventosObservadosArea(area);
    
    // Atualizar tipos de eventos de interesse
    const eventoSelect = document.getElementById('eventoInteresseEdit');
    if (eventoSelect && dados?.analiseSobrevivencia) {
        eventoSelect.innerHTML = '';
        dados.analiseSobrevivencia.eventos.forEach(evento => {
            const option = document.createElement('option');
            option.value = evento.value;
            option.textContent = evento.text;
            eventoSelect.appendChild(option);
        });
    }
}

function atualizarCamposEspecificosAreaSobrevivencia(area) {
    const container = document.getElementById('camposEspecificosAreaSobrevivencia');
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!container || !areaConfig) return;
    
    let html = `
        <div class="row">
            <div class="col-12">
                <h6 class="mb-3">
                    <i class="fas fa-hourglass-half me-2"></i>
                    Campos Específicos - ${areaConfig.nome}
                    <small class="text-muted">(${areaConfig.campos_especificos.length} campos)</small>
                </h6>
            </div>
        </div>
        <div class="row">
    `;
    
    // Criar checkboxes para cada campo específico
    areaConfig.campos_especificos.forEach((campo, index) => {
        const nomeFormatado = campo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" 
                           id="campo_sobrevivencia_${campo}" name="campos_especificos_sobrevivencia[]" value="${campo}">
                    <label class="form-check-label" for="campo_sobrevivencia_${campo}">
                        ${nomeFormatado}
                    </label>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-danger mb-0">
                    <i class="fas fa-hourglass-half me-2"></i>
                    <strong>Vantagem da Análise de Sobrevivência:</strong> ${areaConfig.caracteristicas}. 
                    Análise de sobrevivência estima tempo até eventos jurídicos (sentença, recurso, acordo) e identifica fatores de risco.
                    Requer <strong>eventos observados</strong> e tratamento adequado de censura.
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function atualizarEventosObservadosArea(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return;
    
    // Simular dados de eventos (em produção, isso viria de uma API)
    const totalCasos = Math.floor(Math.random() * 1000) + 500;
    const eventosObservados = Math.floor(totalCasos * (Math.random() * 0.4 + 0.3)); // 30-70%
    const eventosCensurados = totalCasos - eventosObservados;
    
    validarEventosObservados(eventosObservados, eventosCensurados);
}

function validarEventosObservados(eventosObservados, eventosCensurados) {
    const area = document.getElementById('areaJuridicaModeloSobrevivencia')?.value || 'civil';
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    if (!areaConfig) return;
    
    const totalEventos = eventosObservados + eventosCensurados;
    const taxaEventos = totalEventos > 0 ? (eventosObservados / totalEventos) * 100 : 0;
    
    // Atualizar elementos da interface
    const eventosObservadosElement = document.getElementById('eventosObservadosSobrevivencia');
    const eventosCensuradosElement = document.getElementById('eventosCensuradosSobrevivencia');
    const taxaEventosElement = document.getElementById('taxaEventosSobrevivencia');
    const alertStatusEventos = document.getElementById('alertStatusEventosSobrevivencia');
    const impactoConfiabilidadeElement = document.getElementById('impactoConfiabilidadeSobrevivencia');
    const precisaoTextoElement = document.getElementById('precisaoEsperadaTextoSobrevivencia');
    
    if (eventosObservadosElement) {
        eventosObservadosElement.textContent = eventosObservados.toLocaleString();
    }
    
    if (eventosCensuradosElement) {
        eventosCensuradosElement.textContent = eventosCensurados.toLocaleString();
    }
    
    if (taxaEventosElement) {
        taxaEventosElement.textContent = Math.round(taxaEventos) + '%';
    }
    
    // Atualizar barras de progresso
    const progressoObservados = document.getElementById('progressoEventosObservadosSobrevivencia');
    const progressoCensurados = document.getElementById('progressoEventosCensuradosSobrevivencia');
    
    if (progressoObservados) {
        progressoObservados.style.width = taxaEventos + '%';
        progressoObservados.textContent = Math.round(taxaEventos) + '% Observados';
    }
    
    if (progressoCensurados) {
        const taxaCensura = 100 - taxaEventos;
        progressoCensurados.style.width = taxaCensura + '%';
        progressoCensurados.textContent = Math.round(taxaCensura) + '% Censurados';
    }
    
    // Calcular precisão estimada e impacto baseado na taxa de eventos
    let precisaoEstimada = areaConfig.precisao_media;
    let alertClass = 'alert-success';
    let impactoTexto = '';
    
    if (taxaEventos >= 50) { // Taxa ideal de eventos
        alertClass = 'alert-success';
        precisaoEstimada = Math.min(areaConfig.precisao_media + 1, 93); // Bonus menor que outros modelos
        impactoTexto = 'Taxa adequada de eventos - Estimativas de sobrevivência confiáveis';
    } else if (taxaEventos >= 30) { // Taxa moderada
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.95;
        impactoTexto = 'Taxa moderada - Poder estatístico limitado, intervalos de confiança mais amplos';
    } else if (taxaEventos >= 15) { // Taxa baixa
        alertClass = 'alert-warning';
        precisaoEstimada = areaConfig.precisao_media * 0.85;
        impactoTexto = 'Taxa baixa de eventos - Estimativas menos precisas, considerar mais dados';
    } else { // Taxa crítica
        alertClass = 'alert-danger';
        precisaoEstimada = areaConfig.precisao_media * 0.70;
        impactoTexto = 'TAXA CRÍTICA - Poucos eventos observados, análise pode ser inadequada';
    }
    
    if (alertStatusEventos) {
        alertStatusEventos.className = `alert mb-0 ${alertClass}`;
    }
    
    if (precisaoTextoElement) {
        precisaoTextoElement.textContent = `Precisão estimada: ${Math.round(precisaoEstimada)}%`;
    }
    
    if (impactoConfiabilidadeElement) {
        impactoConfiabilidadeElement.textContent = impactoTexto;
    }
}

function validarModeloAnaliseSobrevivencia() {
    const area = document.getElementById('areaJuridicaModeloSobrevivencia')?.value;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let validacoes = {
        camposObrigatorios: validarCamposObrigatoriosSobrevivencia(),
        eventosObservados: validarEventosObservadosAdequados(),
        camposEspecificos: validarCamposEspecificosSelecionadosSobrevivencia(area),
        consistenciaDados: validarConsistenciaDadosSobrevivencia(),
        configuracaoSobrevivencia: validarConfiguracaoSobrevivencia()
    };
    
    let erros = [];
    let avisos = [];
    let score = 0;
    let maxScore = 100;
    
    // Validar campos obrigatórios (25 pontos)
    if (validacoes.camposObrigatorios.valido) {
        score += 25;
    } else {
        erros.push(...validacoes.camposObrigatorios.erros);
    }
    
    // Validar eventos observados (35 pontos - mais crítico para sobrevivência)
    if (validacoes.eventosObservados.valido) {
        score += 35;
    } else {
        if (validacoes.eventosObservados.critico) {
            erros.push(...validacoes.eventosObservados.erros);
        } else {
            avisos.push(...validacoes.eventosObservados.avisos);
            score += Math.round(validacoes.eventosObservados.pontuacaoParcial);
        }
    }
    
    // Validar campos específicos (15 pontos)
    if (validacoes.camposEspecificos.valido) {
        score += 15;
    } else {
        avisos.push(...validacoes.camposEspecificos.avisos);
        score += Math.round(validacoes.camposEspecificos.percentualPreenchido * 0.15);
    }
    
    // Validar consistência (15 pontos)
    if (validacoes.consistenciaDados.valido) {
        score += 15;
    } else {
        erros.push(...validacoes.consistenciaDados.erros);
    }
    
    // Validar configuração de sobrevivência (10 pontos)
    if (validacoes.configuracaoSobrevivencia.valido) {
        score += 10;
    } else {
        avisos.push(...validacoes.configuracaoSobrevivencia.avisos);
        score += 5;
    }
    
    return {
        score: score,
        maxScore: maxScore,
        percentual: Math.round((score / maxScore) * 100),
        erros: erros,
        avisos: avisos,
        podeExecutar: erros.length === 0,
        qualidade: score >= 80 ? 'Alta' : score >= 60 ? 'Média' : 'Baixa',
        validacoes: validacoes
    };
}

function validarCamposObrigatoriosSobrevivencia() {
    const camposObrigatorios = [
        { id: 'numeroProcessoCnjSobrevivencia', nome: 'Número do Processo CNJ' },
        { id: 'clienteAutorSobrevivencia', nome: 'Cliente/Autor' },
        { id: 'cnpjCpfClienteSobrevivencia', nome: 'CNPJ/CPF' },
        { id: 'estadoProcessoSobrevivencia', nome: 'Estado' },
        { id: 'comarcaProcessoSobrevivencia', nome: 'Comarca' },
        { id: 'juizoProcessoSobrevivencia', nome: 'Juízo' },
        { id: 'instanciaProcessoSobrevivencia', nome: 'Instância' },
        { id: 'valorDaCausaSobrevivencia', nome: 'Valor da Causa' },
        { id: 'dataDistribuicaoSobrevivencia', nome: 'Data de Distribuição' },
        { id: 'statusResultadoSobrevivencia', nome: 'Status/Resultado' },
        { id: 'nomeModeloSobrevivencia', nome: 'Nome do Modelo' },
        { id: 'areaJuridicaModeloSobrevivencia', nome: 'Área Jurídica' }
    ];
    
    let erros = [];
    
    camposObrigatorios.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (!elemento || !elemento.value.trim()) {
            erros.push(`Campo obrigatório não preenchido: ${campo.nome}`);
        }
    });
    
    // Validar formato CNJ
    const cnj = document.getElementById('numeroProcessoCnjSobrevivencia')?.value;
    if (cnj && !validarFormatoCNJ(cnj)) {
        erros.push('Número CNJ deve seguir o formato: 1234567-89.2024.8.26.0100');
    }
    
    // Validar valor da causa
    const valor = document.getElementById('valorDaCausaSobrevivencia')?.value;
    if (valor && !validarValorMonetario(valor)) {
        erros.push('Valor da causa deve ser um valor monetário válido');
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarEventosObservadosAdequados() {
    // Simular dados (em produção, isso viria da interface)
    const eventosObservados = parseInt(document.getElementById('eventosObservadosSobrevivencia')?.textContent?.replace(/[,\.]/g, '')) || 0;
    const eventosCensurados = parseInt(document.getElementById('eventosCensuradosSobrevivencia')?.textContent?.replace(/[,\.]/g, '')) || 0;
    const totalEventos = eventosObservados + eventosCensurados;
    
    if (totalEventos === 0) {
        return {
            valido: false,
            critico: true,
            erros: ['Nenhum evento foi definido para análise de sobrevivência']
        };
    }
    
    const taxaEventos = (eventosObservados / totalEventos) * 100;
    
    if (taxaEventos < 10) { // Taxa muito baixa de eventos
        return {
            valido: false,
            critico: true,
            erros: [`Taxa crítica de eventos observados: ${Math.round(taxaEventos)}% (mínimo: 15%)`]
        };
    }
    
    if (taxaEventos < 30) { // Taxa baixa mas não crítica
        const pontuacaoParcial = Math.round(35 * (taxaEventos / 50)); // Pontuação baseada na taxa
        return {
            valido: false,
            critico: false,
            pontuacaoParcial: pontuacaoParcial,
            avisos: [`Taxa baixa de eventos observados: ${Math.round(taxaEventos)}%. Análise pode ter poder estatístico limitado.`]
        };
    }
    
    return { valido: true };
}

function validarCamposEspecificosSelecionadosSobrevivencia(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return { valido: false, avisos: ['Área não configurada'] };
    
    const checkboxes = document.querySelectorAll('input[name="campos_especificos_sobrevivencia[]"]:checked');
    const selecionados = checkboxes.length;
    const disponiveis = areaConfig.campos_especificos.length;
    const percentual = (selecionados / disponiveis) * 100;
    
    if (selecionados === 0) {
        return {
            valido: false,
            percentualPreenchido: 0,
            avisos: ['Nenhum campo específico selecionado. Análise de sobrevivência se beneficia de covariáveis.']
        };
    }
    
    if (percentual < 25) { // Sobrevivência é mais tolerante a menos campos
        return {
            valido: false,
            percentualPreenchido: percentual / 100,
            avisos: [`Poucos campos específicos: ${selecionados}/${disponiveis} (${Math.round(percentual)}%). Recomendado: pelo menos 35%.`]
        };
    }
    
    return {
        valido: true,
        percentualPreenchido: 1,
        selecionados: selecionados,
        percentual: percentual
    };
}

function validarConsistenciaDadosSobrevivencia() {
    let erros = [];
    
    // Validar consistência temporal
    const dataDistribuicao = new Date(document.getElementById('dataDistribuicaoSobrevivencia')?.value);
    if (dataDistribuicao > new Date()) {
        erros.push('Data de distribuição não pode ser futura');
    }
    
    if (dataDistribuicao < new Date('2000-01-01')) {
        erros.push('Data de distribuição muito antiga (anterior a 2000)');
    }
    
    // Validar definição do evento
    const definicaoEvento = document.getElementById('definicaoEvento')?.value;
    if (!definicaoEvento || definicaoEvento.trim().length < 20) {
        erros.push('Definição do evento deve ser clara e detalhada (mínimo 20 caracteres)');
    }
    
    // Validar tipo de censura vs evento
    const tipoCensura = document.getElementById('tipoCensura')?.value;
    const eventoInteresse = document.getElementById('eventoInteresseEdit')?.value;
    
    if (tipoCensura === 'nenhuma' && eventoInteresse) {
        // Aviso: sem censura pode não ser realista
        // Não é erro, apenas menos comum em dados jurídicos
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarConfiguracaoSobrevivencia() {
    let avisos = [];
    
    // Validar unidade de tempo
    const unidadeTempo = document.getElementById('unidadeTempo')?.value;
    if (!unidadeTempo) {
        avisos.push('Selecione a unidade de tempo para análise');
    }
    
    // Validar método de estimação
    const metodoEstimacao = document.getElementById('metodoEstimacao')?.value;
    if (!metodoEstimacao) {
        avisos.push('Selecione um método de estimação (Kaplan-Meier, Cox, etc.)');
    }
    
    // Validar configuração de risco
    const calcularRisco = document.getElementById('calcularRisco')?.checked;
    if (!calcularRisco) {
        avisos.push('Considere habilitar cálculo de razão de risco (hazard ratio)');
    }
    
    return {
        valido: avisos.length === 0,
        avisos: avisos
    };
}

async function testarModeloAnaliseSobrevivencia() {
    console.log('⏳ Iniciando validação avançada do modelo de análise de sobrevivência...');
    
    // Executar validação completa
    const validacao = validarModeloAnaliseSobrevivencia();
    
    // Mostrar resultado da validação
    mostrarResultadoValidacaoSobrevivencia(validacao);
    
    // Se há erros críticos, não prosseguir
    if (!validacao.podeExecutar) {
        console.log('❌ Validação falhou. Corrigir erros antes de continuar.');
        return;
    }
    
    // Se passou na validação, executar teste do modelo
    console.log('✅ Validação passou. Executando teste de análise de sobrevivência...');
    
    const formData = coletarDadosFormulario('formEditarSobrevivencia');
    
    // Adicionar dados de validação ao formData
    formData.validacao = validacao;
    
    try {
        const response = await fetch('/api/estatistica/testar-analise-sobrevivencia', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const resultado = await response.json();
        mostrarResultadoTeste(resultado, 'analise-sobrevivencia');
    } catch (error) {
        console.error('Erro ao testar modelo:', error);
        mostrarErro('Erro ao testar modelo de análise de sobrevivência');
    }
}

function mostrarResultadoValidacaoSobrevivencia(validacao) {
    // Criar modal de resultado da validação
    const modalHtml = `
        <div class="modal fade" id="modalValidacaoSobrevivencia" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-${validacao.podeExecutar ? 'success' : 'danger'} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${validacao.podeExecutar ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                            Validação Análise de Sobrevivência - Score: ${validacao.percentual}%
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-12">
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${validacao.qualidade === 'Alta' ? 'success' : validacao.qualidade === 'Média' ? 'warning' : 'danger'}" 
                                         style="width: ${validacao.percentual}%">
                                        ${validacao.percentual}% - Qualidade ${validacao.qualidade}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${validacao.erros.length > 0 ? `
                        <div class="alert alert-danger">
                            <h6><i class="fas fa-times-circle me-2"></i>Erros Encontrados (${validacao.erros.length})</h6>
                            <ul class="mb-0">
                                ${validacao.erros.map(erro => `<li>${erro}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.avisos.length > 0 ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Avisos (${validacao.avisos.length})</h6>
                            <ul class="mb-0">
                                ${validacao.avisos.map(aviso => `<li>${aviso}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.podeExecutar ? `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-hourglass-half me-2"></i>Análise de Sobrevivência Aprovada</h6>
                            <p class="mb-0">O modelo passou em todas as validações críticas e está pronto para estimar tempo até eventos com curvas de sobrevivência.</p>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        ${validacao.podeExecutar ? '<button type="button" class="btn btn-success" onclick="executarSobrevivenciaValidada()" data-bs-dismiss="modal">Executar Análise de Sobrevivência</button>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modalValidacaoSobrevivencia');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalValidacaoSobrevivencia'));
    modal.show();
}

function executarSobrevivenciaValidada() {
    console.log('⏳ Executando análise de sobrevivência validada...');
    // Aqui seria a análise real de sobrevivência
    mostrarSucesso('Análise de sobrevivência iniciou! Estimando tempo até eventos e curvas de sobrevivência.');
}

// ==================== FUNÇÕES DE TESTE E SALVAMENTO ====================

// ============= SISTEMA DE VALIDAÇÃO AVANÇADA =============
function validarModeloRegressao() {
    const area = document.getElementById('areaJuridicaModeloRegressao')?.value;
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    
    let validacoes = {
        camposObrigatorios: validarCamposObrigatorios(),
        volumeDados: validarVolumeDados(areaConfig),
        camposEspecificos: validarCamposEspecificosSelecionados(area),
        consistenciaDados: validarConsistenciaDados(),
        parametrosEstatisticos: validarParametrosEstatisticos()
    };
    
    let erros = [];
    let avisos = [];
    let score = 0;
    let maxScore = 100;
    
    // Validar campos obrigatórios (25 pontos)
    if (validacoes.camposObrigatorios.valido) {
        score += 25;
    } else {
        erros.push(...validacoes.camposObrigatorios.erros);
    }
    
    // Validar volume de dados (20 pontos)
    if (validacoes.volumeDados.valido) {
        score += 20;
    } else {
        if (validacoes.volumeDados.critico) {
            erros.push(...validacoes.volumeDados.erros);
        } else {
            avisos.push(...validacoes.volumeDados.avisos);
            score += 10; // Pontuação parcial
        }
    }
    
    // Validar campos específicos (20 pontos)
    if (validacoes.camposEspecificos.valido) {
        score += 20;
    } else {
        avisos.push(...validacoes.camposEspecificos.avisos);
        score += Math.round(validacoes.camposEspecificos.percentualPreenchido * 0.2);
    }
    
    // Validar consistência (20 pontos)
    if (validacoes.consistenciaDados.valido) {
        score += 20;
    } else {
        erros.push(...validacoes.consistenciaDados.erros);
    }
    
    // Validar parâmetros estatísticos (15 pontos)
    if (validacoes.parametrosEstatisticos.valido) {
        score += 15;
    } else {
        avisos.push(...validacoes.parametrosEstatisticos.avisos);
    }
    
    return {
        score: score,
        maxScore: maxScore,
        percentual: Math.round((score / maxScore) * 100),
        erros: erros,
        avisos: avisos,
        podeExecutar: erros.length === 0,
        qualidade: score >= 80 ? 'Alta' : score >= 60 ? 'Média' : 'Baixa',
        validacoes: validacoes
    };
}

function validarCamposObrigatorios() {
    const camposObrigatorios = [
        { id: 'numeroProcessoCnj', nome: 'Número do Processo CNJ' },
        { id: 'clienteAutor', nome: 'Cliente/Autor' },
        { id: 'cnpjCpfCliente', nome: 'CNPJ/CPF' },
        { id: 'estadoProcesso', nome: 'Estado' },
        { id: 'comarcaProcesso', nome: 'Comarca' },
        { id: 'juizoProcesso', nome: 'Juízo' },
        { id: 'instanciaProcesso', nome: 'Instância' },
        { id: 'valorDaCausa', nome: 'Valor da Causa' },
        { id: 'dataDistribuicao', nome: 'Data de Distribuição' },
        { id: 'statusResultado', nome: 'Status/Resultado' },
        { id: 'nomeModeloRegressao', nome: 'Nome do Modelo' },
        { id: 'areaJuridicaModeloRegressao', nome: 'Área Jurídica' }
    ];
    
    let erros = [];
    
    camposObrigatorios.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (!elemento || !elemento.value.trim()) {
            erros.push(`Campo obrigatório não preenchido: ${campo.nome}`);
        }
    });
    
    // Validar formato CNJ
    const cnj = document.getElementById('numeroProcessoCnj')?.value;
    if (cnj && !validarFormatoCNJ(cnj)) {
        erros.push('Número CNJ deve seguir o formato: 1234567-89.2024.8.26.0100');
    }
    
    // Validar valor da causa
    const valor = document.getElementById('valorDaCausa')?.value;
    if (valor && !validarValorMonetario(valor)) {
        erros.push('Valor da causa deve ser um valor monetário válido');
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarVolumeDados(areaConfig) {
    if (!areaConfig) return { valido: false, critico: true, erros: ['Área jurídica não reconhecida'] };
    
    const volumeAtual = parseInt(document.getElementById('tamanhoAmostraRegressao')?.value) || 0;
    const volumeMinimo = areaConfig.volume_minimo;
    
    if (volumeAtual === 0) {
        return {
            valido: false,
            critico: true,
            erros: ['Tamanho da amostra não foi definido']
        };
    }
    
    if (volumeAtual < volumeMinimo * 0.3) {
        return {
            valido: false,
            critico: true,
            erros: [`Volume crítico: ${volumeAtual} casos (mínimo absoluto: ${Math.round(volumeMinimo * 0.3)})`]
        };
    }
    
    if (volumeAtual < volumeMinimo) {
        return {
            valido: false,
            critico: false,
            avisos: [`Volume abaixo do recomendado: ${volumeAtual}/${volumeMinimo} casos. Precisão pode ser reduzida.`]
        };
    }
    
    return { valido: true };
}

function validarCamposEspecificosSelecionados(area) {
    const areaConfig = MATRIZ_AREAS_JURIDICAS[area];
    if (!areaConfig) return { valido: false, avisos: ['Área não configurada'] };
    
    const checkboxes = document.querySelectorAll('input[name="campos_especificos[]"]:checked');
    const selecionados = checkboxes.length;
    const disponiveis = areaConfig.campos_especificos.length;
    const percentual = (selecionados / disponiveis) * 100;
    
    if (selecionados === 0) {
        return {
            valido: false,
            percentualPreenchido: 0,
            avisos: ['Nenhum campo específico da área foi selecionado. Isso pode impactar a precisão do modelo.']
        };
    }
    
    if (percentual < 50) {
        return {
            valido: false,
            percentualPreenchido: percentual / 100,
            avisos: [`Poucos campos específicos selecionados: ${selecionados}/${disponiveis} (${Math.round(percentual)}%). Recomendado: pelo menos 70%.`]
        };
    }
    
    return {
        valido: true,
        percentualPreenchido: 1,
        selecionados: selecionados,
        percentual: percentual
    };
}

function validarConsistenciaDados() {
    let erros = [];
    
    // Validar consistência temporal
    const dataDistribuicao = new Date(document.getElementById('dataDistribuicao')?.value);
    if (dataDistribuicao > new Date()) {
        erros.push('Data de distribuição não pode ser futura');
    }
    
    if (dataDistribuicao < new Date('2000-01-01')) {
        erros.push('Data de distribuição muito antiga (anterior a 2000)');
    }
    
    // Validar valor da causa vs área
    const area = document.getElementById('areaJuridicaModeloRegressao')?.value;
    const valorTexto = document.getElementById('valorDaCausa')?.value;
    const valor = parsearValorMonetario(valorTexto);
    
    if (valor > 0) {
        const limitesArea = {
            'familia': { min: 0, max: 1000000 },
            'consumidor': { min: 100, max: 500000 },
            'trabalhista': { min: 1000, max: 2000000 },
            'civil': { min: 0, max: 10000000 },
            'empresarial': { min: 5000, max: 50000000 }
        };
        
        const limite = limitesArea[area];
        if (limite && (valor < limite.min || valor > limite.max)) {
            erros.push(`Valor da causa (R$ ${valor.toLocaleString()}) incompatível com ${MATRIZ_AREAS_JURIDICAS[area]?.nome}`);
        }
    }
    
    return {
        valido: erros.length === 0,
        erros: erros
    };
}

function validarParametrosEstatisticos() {
    let avisos = [];
    
    // Validar configurações de regularização
    const regularizacao = document.getElementById('regularizacaoRegressao')?.value;
    const alpha = parseFloat(document.getElementById('alphaRegressao')?.value);
    
    if (regularizacao !== 'none' && (alpha < 0.001 || alpha > 100)) {
        avisos.push('Valor de Alpha para regularização pode não ser adequado (recomendado: 0.1 a 10)');
    }
    
    // Validar número de iterações
    const maxIter = parseInt(document.getElementById('maxIterRegressao')?.value);
    if (maxIter < 100) {
        avisos.push('Número de iterações muito baixo pode não convergir');
    } else if (maxIter > 5000) {
        avisos.push('Número de iterações muito alto pode causar overfitting');
    }
    
    // Validar cross-validation
    const cvFolds = parseInt(document.getElementById('cvFoldsRegressao')?.value);
    if (cvFolds < 3 || cvFolds > 20) {
        avisos.push('Número de folds para validação cruzada recomendado: 3 a 10');
    }
    
    return {
        valido: avisos.length === 0,
        avisos: avisos
    };
}

// Funções auxiliares de validação
function validarFormatoCNJ(cnj) {
    const regexCNJ = /^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$/;
    return regexCNJ.test(cnj);
}

function validarValorMonetario(valor) {
    if (!valor) return false;
    const valorLimpo = valor.replace(/[R$\s.,]/g, '');
    return !isNaN(valorLimpo) && parseFloat(valorLimpo) >= 0;
}

function parsearValorMonetario(valor) {
    if (!valor) return 0;
    return parseFloat(valor.replace(/[R$\s.]/g, '').replace(',', '.')) || 0;
}

async function testarModeloRegressao() {
    console.log('🔍 Iniciando validação avançada do modelo de regressão...');
    
    // Executar validação completa
    const validacao = validarModeloRegressao();
    
    // Mostrar resultado da validação
    mostrarResultadoValidacao(validacao);
    
    // Se há erros críticos, não prosseguir
    if (!validacao.podeExecutar) {
        console.log('❌ Validação falhou. Corrigir erros antes de continuar.');
        return;
    }
    
    // Se passou na validação, executar teste do modelo
    console.log('✅ Validação passou. Executando teste do modelo...');
    
    const formData = coletarDadosFormulario('formEditarRegressao');
    
    // Adicionar dados de validação ao formData
    formData.validacao = validacao;
    
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

function mostrarResultadoValidacao(validacao) {
    // Criar modal de resultado da validação
    const modalHtml = `
        <div class="modal fade" id="modalValidacaoRegressao" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-${validacao.podeExecutar ? 'success' : 'danger'} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${validacao.podeExecutar ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                            Resultado da Validação - Score: ${validacao.percentual}%
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-12">
                                <div class="progress" style="height: 25px;">
                                    <div class="progress-bar bg-${validacao.qualidade === 'Alta' ? 'success' : validacao.qualidade === 'Média' ? 'warning' : 'danger'}" 
                                         style="width: ${validacao.percentual}%">
                                        ${validacao.percentual}% - Qualidade ${validacao.qualidade}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${validacao.erros.length > 0 ? `
                        <div class="alert alert-danger">
                            <h6><i class="fas fa-times-circle me-2"></i>Erros Encontrados (${validacao.erros.length})</h6>
                            <ul class="mb-0">
                                ${validacao.erros.map(erro => `<li>${erro}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.avisos.length > 0 ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Avisos (${validacao.avisos.length})</h6>
                            <ul class="mb-0">
                                ${validacao.avisos.map(aviso => `<li>${aviso}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${validacao.podeExecutar ? `
                        <div class="alert alert-success">
                            <h6><i class="fas fa-check-circle me-2"></i>Modelo Aprovado</h6>
                            <p class="mb-0">O modelo passou em todas as validações críticas e está pronto para execução.</p>
                        </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        ${validacao.podeExecutar ? '<button type="button" class="btn btn-success" onclick="executarModeloValidado()" data-bs-dismiss="modal">Executar Modelo</button>' : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modalValidacaoRegressao');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar modal ao DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalValidacaoRegressao'));
    modal.show();
}

function executarModeloValidado() {
    console.log('▶️ Executando modelo validado...');
    // Aqui seria a execução real do modelo
    mostrarSucesso('Modelo de regressão executado com sucesso!');
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
        // Criar modal para solicitar nome do modelo
        const modalHtml = `
            <div class="modal fade" id="modalSalvarModelo" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content" style="background: rgba(46, 93, 133, 0.9); color: white; border: 1px solid rgba(78, 205, 196, 0.3);">
                        <div class="modal-header" style="background: #3b576f; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                            <h5 class="modal-title">
                                <i class="fas fa-save me-2"></i>Salvar Modelo ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="nomeModelo" class="form-label">Nome do Modelo:</label>
                                <input type="text" class="form-control" id="nomeModelo" 
                                       placeholder="Ex: Modelo Trabalhista - Análise Verbas" 
                                       style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); color: white;">
                            </div>
                            <div class="mb-3">
                                <label for="descricaoModelo" class="form-label">Descrição (opcional):</label>
                                <textarea class="form-control" id="descricaoModelo" rows="3" 
                                          placeholder="Descrição detalhada do modelo..."
                                          style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); color: white;"></textarea>
                            </div>
                        </div>
                        <div class="modal-footer" style="border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="confirmarSalvarModelo('${tipo}')">
                                <i class="fas fa-save me-1"></i>Salvar Modelo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente se houver
        const existingModal = document.getElementById('modalSalvarModelo');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Adicionar modal ao DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Armazenar dados temporariamente
        window.dadosModeloTemporario = dados;
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('modalSalvarModelo'));
        modal.show();
        
        // Focar no campo nome
        document.getElementById('nomeModelo').focus();
        
    } catch (error) {
        console.error('Erro ao criar modal de salvamento:', error);
        mostrarErro('Erro ao preparar salvamento do modelo');
    }
}

async function confirmarSalvarModelo(tipo) {
    try {
        const nome = document.getElementById('nomeModelo').value.trim();
        const descricao = document.getElementById('descricaoModelo').value.trim();
        
        if (!nome) {
            mostrarErro('Por favor, informe um nome para o modelo');
            return;
        }
        
        // Adicionar nome e descrição aos dados
        const dadosCompletos = {
            ...window.dadosModeloTemporario,
            nome: nome,
            descricao: descricao || `Modelo de ${tipo} criado em ${new Date().toLocaleString('pt-BR')}`
        };
        
        const response = await fetch(`/api/estatistica/salvar-${tipo}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosCompletos)
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            mostrarSucesso(`Modelo "${nome}" salvo com sucesso!`);
            
            // Fechar modal de salvamento
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalSalvarModelo'));
            modal.hide();
            
            // Limpar dados temporários
            delete window.dadosModeloTemporario;
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
                    <div class="modal-header bg-primary text-white">
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
    // Criar toast de sucesso
    const toastHtml = `
        <div class="toast align-items-center text-bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();
    
    // Remover do DOM após esconder
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function mostrarErro(mensagem) {
    // Criar toast de erro
    const toastHtml = `
        <div class="toast align-items-center text-bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i>${mensagem}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    
    // Remover do DOM após esconder
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// ==================== INICIALIZAÇÃO DE EVENT LISTENERS ====================
function inicializarEventListenersCnpjCpf() {
    // Event listeners para preenchimento automático baseado no CNJ
    const camposCnj = [
        'numeroProcessoCnj',           // Template Regressão
        'numeroProcessoCnjArvore',     // Template Árvore Decisão
        'numeroProcessoCnjNeurais',    // Template Redes Neurais
        'numeroProcessoCnjTemporais',  // Template Séries Temporais
        'numeroProcessoCnjSobrevivencia' // Template Sobrevivência
    ];
    
    camposCnj.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) {
            campo.addEventListener('blur', function() {
                const sufixo = id.replace('numeroProcessoCnj', '');
                preencherAutomaticoCnpjCpf(this, sufixo);
            });
        }
    });
    
    // Event listeners para máscara de CNPJ/CPF
    const camposCnpjCpf = [
        'cnpjCpfCliente',              // Template Regressão
        'cnpjCpfClienteArvore',        // Template Árvore Decisão
        'cnpjCpfClienteNeurais',       // Template Redes Neurais
        'cnpjCpfClienteTemporais',     // Template Séries Temporais
        'cnpjCpfClienteSobrevivencia'  // Template Sobrevivência
    ];
    
    camposCnpjCpf.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) {
            campo.addEventListener('input', function() {
                aplicarMascaraCnpjCpf(this);
            });
        }
    });
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
    
    // Inicializar event listeners para CNPJ/CPF
    inicializarEventListenersCnpjCpf();
    
    // ==================== FUNÇÕES ESPECÍFICAS PARA CADA MODELO ====================

    // Funções de atualização para cada modelo estatístico
    window.atualizarParametrosArvoreDecisao = function() {
        const area = document.getElementById('areaJuridicaModeloArvore')?.value || 'civil';
        atualizarCamposEspecificosArea(area, 'arvore');
    };

    window.atualizarParametrosRedesNeurais = function() {
        const area = document.getElementById('areaJuridicaModeloNeurais')?.value || 'civil';
        atualizarCamposEspecificosArea(area, 'neurais');
    };

    window.atualizarParametrosSeriesTemporais = function() {
        const area = document.getElementById('areaJuridicaModeloTemporais')?.value || 'trabalhista';
        // Séries temporais: apenas Trabalhista e Família
        if (!['trabalhista', 'familia'].includes(area)) {
            const selectElement = document.getElementById('areaJuridicaModeloTemporais');
            if (selectElement) {
                selectElement.value = 'trabalhista';
            }
            atualizarCamposEspecificosArea('trabalhista', 'temporais');
        } else {
            atualizarCamposEspecificosArea(area, 'temporais');
        }
    };

    window.atualizarParametrosSobrevivencia = function() {
        const area = document.getElementById('areaJuridicaModeloSobrevivencia')?.value || 'trabalhista';
        // Análise de sobrevivência: apenas Trabalhista e Família
        if (!['trabalhista', 'familia'].includes(area)) {
            const selectElement = document.getElementById('areaJuridicaModeloSobrevivencia');
            if (selectElement) {
                selectElement.value = 'trabalhista';
            }
            atualizarCamposEspecificosArea('trabalhista', 'sobrevivencia');
        } else {
            atualizarCamposEspecificosArea(area, 'sobrevivencia');
        }
    };
    
    // Event listeners adicionais para cada modelo
    
    // Árvore de Decisão
    const areaSelectArvore = document.getElementById('areaJuridicaModeloArvore');
    if (areaSelectArvore) {
        areaSelectArvore.addEventListener('change', window.atualizarParametrosArvoreDecisao);
        setTimeout(() => window.atualizarParametrosArvoreDecisao(), 100);
    }
    
    // Redes Neurais
    const areaSelectNeurais = document.getElementById('areaJuridicaModeloNeurais');
    if (areaSelectNeurais) {
        areaSelectNeurais.addEventListener('change', window.atualizarParametrosRedesNeurais);
        setTimeout(() => window.atualizarParametrosRedesNeurais(), 100);
    }
    
    // Séries Temporais
    const areaSelectTemporais = document.getElementById('areaJuridicaModeloTemporais');
    if (areaSelectTemporais) {
        areaSelectTemporais.addEventListener('change', window.atualizarParametrosSeriesTemporais);
        setTimeout(() => window.atualizarParametrosSeriesTemporais(), 100);
    }
    
    // Análise de Sobrevivência
    const areaSelectSobrevivencia = document.getElementById('areaJuridicaModeloSobrevivencia');
    if (areaSelectSobrevivencia) {
        areaSelectSobrevivencia.addEventListener('change', window.atualizarParametrosSobrevivencia);
        setTimeout(() => window.atualizarParametrosSobrevivencia(), 100);
    }
    
    console.log('✓ Matriz universal implementada em todos os 5 modelos estatísticos!');
});