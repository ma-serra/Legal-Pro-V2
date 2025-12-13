/**
 * Configuração de campos específicos para cada área jurídica
 * Sistema de formulários dinâmicos para cadastro de processos
 */

const CAMPOS_POR_AREA = {
    "Direito Agrário": {
        nome: "Direito Agrário",
        campos: [
            {
                id: "tipo_imovel_rural",
                label: "Tipo de Imóvel Rural",
                type: "select",
                options: ["Fazenda", "Sítio", "Chácara", "Área de Assentamento", "Terras Indígenas", "Quilombola", "Outro"],
                required: true
            },
            {
                id: "area_hectares",
                label: "Área (Hectares)",
                type: "number",
                placeholder: "Ex: 150.5",
                step: "0.01",
                required: true
            },
            {
                id: "matricula_imovel",
                label: "Matrícula do Imóvel",
                type: "text",
                placeholder: "Nº da matrícula no Registro de Imóveis",
                required: false
            },
            {
                id: "incra_envolvido",
                label: "INCRA Envolvido",
                type: "checkbox",
                required: false
            },
            {
                id: "conflito_posse",
                label: "Conflito de Posse",
                type: "checkbox",
                required: false
            },
            {
                id: "regularizacao_fundiaria",
                label: "Regularização Fundiária",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Civil": {
        nome: "Direito Civil",
        campos: [
            {
                id: "tipo_acao_civil",
                label: "Tipo de Ação Cível",
                type: "select",
                options: ["Indenização", "Cobrança", "Rescisão Contratual", "Divórcio", "Inventário", "Usucapião", "Outro"],
                required: true
            },
            {
                id: "dano_moral_pedido",
                label: "Dano Moral (Pedido)",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "dano_material_pedido",
                label: "Dano Material (Pedido)",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "prescricao_aplicavel",
                label: "Prazo Prescricional (anos)",
                type: "number",
                placeholder: "Ex: 3, 5, 10",
                required: false
            },
            {
                id: "testemunhas",
                label: "Número de Testemunhas",
                type: "number",
                placeholder: "Ex: 3",
                required: false
            }
        ]
    },
    
    "Direito Trabalhista": {
        nome: "Direito Trabalhista",
        campos: [
            {
                id: "pedido_verba",
                label: "Pedido de Verba",
                type: "multicheck",
                options: [
                    "Horas Extras",
                    "Adicional Noturno",
                    "Insalubridade",
                    "Periculosidade",
                    "FGTS",
                    "13º Salário",
                    "Férias + 1/3",
                    "Aviso Prévio",
                    "Multa 40% FGTS",
                    "Dano Moral",
                    "Equiparação Salarial",
                    "Diferenças Salariais"
                ],
                required: true
            },
            {
                id: "data_admissao",
                label: "Data de Admissão",
                type: "date",
                required: true
            },
            {
                id: "data_demissao",
                label: "Data de Demissão",
                type: "date",
                required: false
            },
            {
                id: "salario_mensal",
                label: "Salário Mensal",
                type: "money",
                placeholder: "R$ 0,00",
                required: true
            },
            {
                id: "funcao_exercida",
                label: "Função Exercida",
                type: "text",
                placeholder: "Ex: Analista, Operador, Vendedor",
                required: true
            }
        ]
    },
    
    "Direito Penal": {
        nome: "Direito Penal",
        campos: [
            {
                id: "tipo_crime",
                label: "Tipo de Crime",
                type: "select",
                options: ["Furto", "Roubo", "Estelionato", "Homicídio", "Lesão Corporal", "Tráfico de Drogas", "Porte Ilegal de Arma", "Corrupção", "Outro"],
                required: true
            },
            {
                id: "fase_penal",
                label: "Fase do Processo",
                type: "select",
                options: ["Inquérito Policial", "Denúncia", "Instrução", "Alegações Finais", "Sentença", "Recurso", "Trânsito em Julgado"],
                required: true
            },
            {
                id: "pena_maxima",
                label: "Pena Máxima (anos)",
                type: "number",
                placeholder: "Ex: 4, 8, 12",
                required: false
            },
            {
                id: "regime_prisional",
                label: "Regime Prisional",
                type: "select",
                options: ["Fechado", "Semi-Aberto", "Aberto", "Não Aplicável"],
                required: false
            },
            {
                id: "preso_provisorio",
                label: "Preso Provisório",
                type: "checkbox",
                required: false
            },
            {
                id: "medida_cautelar",
                label: "Medida Cautelar",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Administrativo": {
        nome: "Direito Administrativo",
        campos: [
            {
                id: "tipo_acao_administrativa",
                label: "Tipo de Ação",
                type: "select",
                options: ["Mandado de Segurança", "Ação Anulatória", "Ação de Improbidade", "Desapropriação", "Licitação", "Concurso Público", "Servidores Públicos", "Outro"],
                required: true
            },
            {
                id: "orgao_publico",
                label: "Órgão Público Envolvido",
                type: "text",
                placeholder: "Ex: Prefeitura, Estado, União",
                required: true
            },
            {
                id: "ato_administrativo",
                label: "Ato Administrativo Questionado",
                type: "text",
                placeholder: "Descreva o ato",
                required: false
            },
            {
                id: "prazo_decadencial",
                label: "Prazo Decadencial (dias)",
                type: "number",
                placeholder: "Ex: 120",
                required: false
            },
            {
                id: "liminar_concedida",
                label: "Liminar Concedida",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Tributário": {
        nome: "Direito Tributário",
        campos: [
            {
                id: "tipo_tributo",
                label: "Tipo de Tributo",
                type: "select",
                options: ["ICMS", "ISS", "PIS/COFINS", "IRPJ", "CSLL", "INSS", "FGTS", "IPTU", "IPVA", "ITR", "IPI", "II", "IE", "IOF", "Outro"],
                required: true
            },
            {
                id: "valor_autuacao",
                label: "Valor da Autuação",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "processo_administrativo",
                label: "Nº Processo Administrativo",
                type: "text",
                placeholder: "Número do PAF",
                required: false
            },
            {
                id: "parcelamento",
                label: "Parcelamento",
                type: "checkbox",
                required: false
            },
            {
                id: "discussao_constitucionalidade",
                label: "Discussão de Constitucionalidade",
                type: "checkbox",
                required: false
            },
            {
                id: "repercussao_geral",
                label: "Repercussão Geral STF",
                type: "text",
                placeholder: "Nº do Tema",
                required: false
            }
        ]
    },
    
    "Direito Empresarial": {
        nome: "Direito Empresarial",
        campos: [
            {
                id: "tipo_societario",
                label: "Tipo Societário",
                type: "select",
                options: ["LTDA", "S/A", "EIRELI", "SLU", "Sociedade Simples", "Cooperativa", "Outro"],
                required: true
            },
            {
                id: "objeto_social",
                label: "Objeto Social",
                type: "textarea",
                placeholder: "Descreva o objeto social da empresa",
                required: false
            },
            {
                id: "capital_social",
                label: "Capital Social",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "recuperacao_judicial",
                label: "Recuperação Judicial",
                type: "checkbox",
                required: false
            },
            {
                id: "falencia",
                label: "Falência",
                type: "checkbox",
                required: false
            },
            {
                id: "dissolucao_societaria",
                label: "Dissolução Societária",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito do Consumidor": {
        nome: "Direito do Consumidor",
        campos: [
            {
                id: "tipo_relacao_consumo",
                label: "Tipo de Relação",
                type: "select",
                options: ["Produto Defeituoso", "Serviço Defeituoso", "Cobrança Indevida", "Propaganda Enganosa", "Vício do Produto", "Vício do Serviço", "Outro"],
                required: true
            },
            {
                id: "fornecedor",
                label: "Fornecedor/Prestador",
                type: "text",
                placeholder: "Nome da empresa",
                required: true
            },
            {
                id: "valor_produto_servico",
                label: "Valor do Produto/Serviço",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "procon_acionado",
                label: "PROCON Acionado",
                type: "checkbox",
                required: false
            },
            {
                id: "inversao_onus_prova",
                label: "Inversão do Ônus da Prova",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Previdenciário": {
        nome: "Direito Previdenciário",
        campos: [
            {
                id: "tipo_beneficio",
                label: "Tipo de Benefício",
                type: "select",
                options: ["Aposentadoria por Idade", "Aposentadoria por Tempo de Contribuição", "Aposentadoria por Invalidez", "Pensão por Morte", "Auxílio-Doença", "Auxílio-Acidente", "BPC/LOAS", "Salário-Maternidade", "Outro"],
                required: true
            },
            {
                id: "numero_beneficio",
                label: "Número do Benefício (NB)",
                type: "text",
                placeholder: "Ex: 123.456.789-0",
                required: false
            },
            {
                id: "tempo_contribuicao",
                label: "Tempo de Contribuição (anos)",
                type: "number",
                placeholder: "Ex: 35",
                step: "0.5",
                required: false
            },
            {
                id: "data_der",
                label: "Data DER/DIB",
                type: "date",
                required: false
            },
            {
                id: "rmi_calculado",
                label: "RMI Calculado",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "revisao_beneficio",
                label: "Revisão de Benefício",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Imobiliário": {
        nome: "Direito Imobiliário",
        campos: [
            {
                id: "tipo_imovel",
                label: "Tipo de Imóvel",
                type: "select",
                options: ["Residencial", "Comercial", "Industrial", "Terreno", "Rural", "Misto", "Outro"],
                required: true
            },
            {
                id: "matricula_registro",
                label: "Matrícula no Registro de Imóveis",
                type: "text",
                placeholder: "Nº da matrícula",
                required: false
            },
            {
                id: "valor_imovel",
                label: "Valor do Imóvel",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "financiamento",
                label: "Financiamento",
                type: "checkbox",
                required: false
            },
            {
                id: "despejo",
                label: "Ação de Despejo",
                type: "checkbox",
                required: false
            },
            {
                id: "usucapiao",
                label: "Usucapião",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Ambiental": {
        nome: "Direito Ambiental",
        campos: [
            {
                id: "tipo_dano_ambiental",
                label: "Tipo de Dano Ambiental",
                type: "select",
                options: ["Poluição Hídrica", "Poluição Atmosférica", "Desmatamento", "Fauna", "Resíduos Sólidos", "Licenciamento", "APP", "Reserva Legal", "Outro"],
                required: true
            },
            {
                id: "orgao_fiscalizador",
                label: "Órgão Fiscalizador",
                type: "select",
                options: ["IBAMA", "ICMBio", "CETESB", "INEMA", "SEMAD", "IMA", "Outro"],
                required: false
            },
            {
                id: "auto_infracao",
                label: "Nº Auto de Infração",
                type: "text",
                placeholder: "Número do AI",
                required: false
            },
            {
                id: "valor_multa_ambiental",
                label: "Valor da Multa",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "tac_firmado",
                label: "TAC Firmado",
                type: "checkbox",
                required: false
            },
            {
                id: "area_protegida",
                label: "Área Protegida (Hectares)",
                type: "number",
                placeholder: "Ex: 50.5",
                step: "0.01",
                required: false
            }
        ]
    },
    
    "Direito Digital": {
        nome: "Direito Digital",
        campos: [
            {
                id: "tipo_caso_digital",
                label: "Tipo de Caso",
                type: "select",
                options: ["Vazamento de Dados", "LGPD", "Crimes Cibernéticos", "Direitos Autorais Digital", "E-commerce", "Contratos Digitais", "Fake News", "Difamação Online", "Outro"],
                required: true
            },
            {
                id: "plataforma_envolvida",
                label: "Plataforma Envolvida",
                type: "text",
                placeholder: "Ex: Facebook, Instagram, Site",
                required: false
            },
            {
                id: "dados_sensiveis",
                label: "Dados Sensíveis (LGPD)",
                type: "checkbox",
                required: false
            },
            {
                id: "anpd_notificada",
                label: "ANPD Notificada",
                type: "checkbox",
                required: false
            },
            {
                id: "titulares_afetados",
                label: "Número de Titulares Afetados",
                type: "number",
                placeholder: "Ex: 1000",
                required: false
            },
            {
                id: "valor_dano_digital",
                label: "Valor do Dano Estimado",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            }
        ]
    },
    
    "Direito Bancário": {
        nome: "Direito Bancário",
        campos: [
            {
                id: "tipo_operacao_bancaria",
                label: "Tipo de Operação",
                type: "select",
                options: ["Empréstimo", "Financiamento", "Cartão de Crédito", "Cheque Especial", "Conta Corrente", "Investimento", "CDC", "Leasing", "Outro"],
                required: true
            },
            {
                id: "instituicao_financeira",
                label: "Instituição Financeira",
                type: "text",
                placeholder: "Nome do banco",
                required: true
            },
            {
                id: "numero_contrato_bancario",
                label: "Número do Contrato",
                type: "text",
                placeholder: "Nº do contrato",
                required: false
            },
            {
                id: "taxa_juros_aplicada",
                label: "Taxa de Juros (% a.m.)",
                type: "number",
                placeholder: "Ex: 2.5",
                step: "0.01",
                required: false
            },
            {
                id: "saldo_devedor",
                label: "Saldo Devedor",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "revisao_contrato",
                label: "Revisão de Contrato",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Direito Securitário": {
        nome: "Direito Securitário",
        campos: [
            {
                id: "tipo_seguro",
                label: "Tipo de Seguro",
                type: "select",
                options: ["Vida", "Saúde", "Auto", "Residencial", "Empresarial", "Responsabilidade Civil", "Previdência Privada", "Outro"],
                required: true
            },
            {
                id: "seguradora",
                label: "Seguradora",
                type: "text",
                placeholder: "Nome da seguradora",
                required: true
            },
            {
                id: "numero_apolice",
                label: "Número da Apólice",
                type: "text",
                placeholder: "Nº da apólice",
                required: false
            },
            {
                id: "numero_sinistro",
                label: "Número do Sinistro",
                type: "text",
                placeholder: "Nº do sinistro",
                required: false
            },
            {
                id: "valor_indenizacao_pedido",
                label: "Valor da Indenização (Pedido)",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "negativa_cobertura",
                label: "Negativa de Cobertura",
                type: "checkbox",
                required: false
            }
        ]
    },
    
    "Negociação e Conflitos": {
        nome: "Negociação e Conflitos",
        campos: [
            {
                id: "metodo_resolucao",
                label: "Método de Resolução",
                type: "select",
                options: ["Mediação", "Conciliação", "Arbitragem", "Negociação Direta", "Outro"],
                required: true
            },
            {
                id: "valor_acordo_proposto",
                label: "Valor do Acordo Proposto",
                type: "money",
                placeholder: "R$ 0,00",
                required: false
            },
            {
                id: "prazo_negociacao",
                label: "Prazo para Negociação (dias)",
                type: "number",
                placeholder: "Ex: 30",
                required: false
            },
            {
                id: "camara_arbitragem",
                label: "Câmara de Arbitragem",
                type: "text",
                placeholder: "Nome da câmara",
                required: false
            },
            {
                id: "acordo_homologado",
                label: "Acordo Homologado",
                type: "checkbox",
                required: false
            }
        ]
    }
};

/**
 * Renderiza os campos específicos da área jurídica selecionada
 */
function renderizarCamposEspecificos(areaSelecionada) {
    const container = document.getElementById('campos-especificos-container');
    
    if (!container) {
        console.error('Container de campos específicos não encontrado');
        return;
    }
    
    // Limpar campos anteriores
    container.innerHTML = '';
    
    if (!areaSelecionada || !CAMPOS_POR_AREA[areaSelecionada]) {
        container.style.display = 'none';
        return;
    }
    
    const config = CAMPOS_POR_AREA[areaSelecionada];
    container.style.display = 'block';
    
    // Criar seção header
    const header = document.createElement('div');
    header.className = 'section-header';
    header.innerHTML = `<i class="fas fa-cogs me-2"></i>Campos Específicos - ${config.nome}`;
    container.appendChild(header);
    
    // Criar container dos campos
    const camposContainer = document.createElement('div');
    camposContainer.className = 'row form-row';
    
    config.campos.forEach(campo => {
        const colDiv = document.createElement('div');
        
        // Definir tamanho da coluna baseado no tipo
        if (campo.type === 'textarea' || campo.type === 'multicheck') {
            colDiv.className = 'col-md-12';
        } else {
            colDiv.className = 'col-md-6';
        }
        
        const fieldHtml = criarCampoHTML(campo);
        colDiv.innerHTML = fieldHtml;
        camposContainer.appendChild(colDiv);
    });
    
    container.appendChild(camposContainer);
}

/**
 * Cria o HTML de um campo específico
 */
function criarCampoHTML(campo) {
    const required = campo.required ? 'required' : '';
    const requiredMark = campo.required ? ' *' : '';
    
    let html = `<label for="${campo.id}" class="form-label">${campo.label}${requiredMark}</label>`;
    
    switch (campo.type) {
        case 'text':
            html += `<input type="text" class="form-control" id="${campo.id}" name="campos_especificos_${campo.id}" placeholder="${campo.placeholder || ''}" ${required}>`;
            break;
            
        case 'number':
            html += `<input type="number" class="form-control" id="${campo.id}" name="campos_especificos_${campo.id}" placeholder="${campo.placeholder || ''}" step="${campo.step || '1'}" ${required}>`;
            break;
            
        case 'money':
            html += `<input type="text" class="form-control money-mask" id="${campo.id}" name="campos_especificos_${campo.id}" placeholder="${campo.placeholder || 'R$ 0,00'}" ${required}>`;
            break;
            
        case 'date':
            html += `<input type="date" class="form-control" id="${campo.id}" name="campos_especificos_${campo.id}" ${required}>`;
            break;
            
        case 'select':
            html += `<select class="form-select" id="${campo.id}" name="campos_especificos_${campo.id}" ${required}>`;
            html += `<option value="">Selecione...</option>`;
            campo.options.forEach(option => {
                html += `<option value="${option}">${option}</option>`;
            });
            html += `</select>`;
            break;
            
        case 'checkbox':
            html += `<div class="form-check">`;
            html += `<input class="form-check-input" type="checkbox" id="${campo.id}" name="campos_especificos_${campo.id}" value="true">`;
            html += `<label class="form-check-label" for="${campo.id}">Sim</label>`;
            html += `</div>`;
            break;
            
        case 'textarea':
            html += `<textarea class="form-control" id="${campo.id}" name="campos_especificos_${campo.id}" rows="3" placeholder="${campo.placeholder || ''}" ${required}></textarea>`;
            break;
            
        case 'multicheck':
            html += `<div class="checkbox-grid">`;
            campo.options.forEach((option, index) => {
                html += `<div class="form-check">`;
                html += `<input class="form-check-input" type="checkbox" id="${campo.id}_${index}" name="campos_especificos_${campo.id}" value="${option}">`;
                html += `<label class="form-check-label" for="${campo.id}_${index}">${option}</label>`;
                html += `</div>`;
            });
            html += `</div>`;
            break;
    }
    
    return html;
}

/**
 * Aplica máscaras de dinheiro nos campos money
 */
function aplicarMascaras() {
    // Máscara de dinheiro
    const moneyInputs = document.querySelectorAll('.money-mask');
    moneyInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = (value / 100).toFixed(2);
            value = value.replace('.', ',');
            value = value.replace(/(\d)(?=(\d{3})+\,)/g, '$1.');
            e.target.value = 'R$ ' + value;
        });
    });
}

/**
 * Coleta os dados dos campos específicos para envio no formulário
 */
function coletarCamposEspecificos() {
    const areaSelecionada = document.getElementById('area_juridica').value;
    
    if (!areaSelecionada || !CAMPOS_POR_AREA[areaSelecionada]) {
        return {};
    }
    
    const config = CAMPOS_POR_AREA[areaSelecionada];
    const dados = {};
    
    config.campos.forEach(campo => {
        if (campo.type === 'multicheck') {
            // Coletar múltiplos checkboxes
            const checkboxes = document.querySelectorAll(`input[name="campos_especificos_${campo.id}"]:checked`);
            dados[campo.id] = Array.from(checkboxes).map(cb => cb.value);
        } else if (campo.type === 'checkbox') {
            const checkbox = document.getElementById(campo.id);
            dados[campo.id] = checkbox ? checkbox.checked : false;
        } else if (campo.type === 'money') {
            const input = document.getElementById(campo.id);
            if (input && input.value) {
                // Remover formatação e converter para número
                const valor = input.value.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
                dados[campo.id] = parseFloat(valor) || 0;
            }
        } else if (campo.type === 'number') {
            const input = document.getElementById(campo.id);
            dados[campo.id] = input && input.value ? parseFloat(input.value) : null;
        } else {
            const input = document.getElementById(campo.id);
            dados[campo.id] = input ? input.value : '';
        }
    });
    
    return dados;
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const areaSelect = document.getElementById('area_juridica');
    
    if (areaSelect) {
        // Renderizar campos quando área for selecionada
        areaSelect.addEventListener('change', function() {
            renderizarCamposEspecificos(this.value);
            // Aplicar máscaras após renderizar
            setTimeout(aplicarMascaras, 100);
        });
    }
    
    // Interceptar submit do formulário para adicionar campos específicos
    const form = document.querySelector('form[action*="cadastro"]');
    if (form) {
        form.addEventListener('submit', function(e) {
            const camposEspecificos = coletarCamposEspecificos();
            
            // Criar input hidden com JSON dos campos específicos
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'campos_especificos_json';
            hiddenInput.value = JSON.stringify(camposEspecificos);
            form.appendChild(hiddenInput);
        });
    }
});
