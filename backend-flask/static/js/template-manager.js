/**
 * Sistema de Gerenciamento de Templates Jurídicos
 * Funcionalidades: Visualizar, Editar, Usar e Excluir templates
 */

// Dados globais dos templates
let templatesData = {};
let areaAtual = '';

// Inicialização
function initTemplateManager(area, templates) {
    areaAtual = area;
    templatesData = templates;
    
    console.log(`Template Manager inicializado para área: ${area}`);
    console.log(`Templates carregados: ${templates.length}`);
}

// ============ VISUALIZAR TEMPLATE ============
function visualizarTemplate(templateId) {
    const template = getTemplateById(templateId);
    if (!template) {
        mostrarMensagem('error', 'Template não encontrado');
        return;
    }
    
    mostrarModalVisualizacao(template);
}

function mostrarModalVisualizacao(template) {
    const modalHtml = `
        <div class="modal fade" id="modalVisualizarTemplate" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        <h5 class="modal-title text-white">
                            <i class="${template.icon || 'fas fa-file-alt'} me-2"></i>
                            ${template.nome}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <div class="row">
                            <div class="col-md-8">
                                <div class="mb-4">
                                    <h6 class="fw-bold text-primary mb-2">
                                        <i class="fas fa-info-circle me-1"></i>Descrição
                                    </h6>
                                    <p class="text-muted mb-0">${template.desc || template.descricao}</p>
                                </div>
                                
                                <div class="mb-4">
                                    <h6 class="fw-bold text-primary mb-3">
                                        <i class="fas fa-list-check me-1"></i>Campos Disponíveis
                                    </h6>
                                    <div class="row g-2">
                                        ${(template.campos || []).map(campo => `
                                            <div class="col-md-6">
                                                <div class="border rounded p-2 bg-light">
                                                    <small class="d-flex align-items-center">
                                                        <i class="fas fa-check-circle text-success me-2"></i>
                                                        <span class="fw-medium">${campo}</span>
                                                    </small>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                
                                ${template.conteudo ? `
                                    <div class="mb-4">
                                        <h6 class="fw-bold text-primary mb-2">
                                            <i class="fas fa-file-text me-1"></i>Exemplo de Uso
                                        </h6>
                                        <div class="bg-light border rounded p-3">
                                            <p class="mb-0 small">${template.conteudo}</p>
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                            
                            <div class="col-md-4">
                                <div class="card border-0 bg-light h-100">
                                    <div class="card-body text-center">
                                        <div class="mb-3">
                                            <i class="${template.icon || 'fas fa-file-alt'}" style="font-size: 3rem; color: #c29e74;"></i>
                                        </div>
                                        
                                        <div class="small text-muted">
                                            <div class="d-flex justify-content-between border-bottom py-1">
                                                <span>ID:</span>
                                                <span class="fw-medium">${template.id}</span>
                                            </div>
                                            <div class="d-flex justify-content-between border-bottom py-1">
                                                <span>Área:</span>
                                                <span class="fw-medium">${areaAtual.charAt(0).toUpperCase() + areaAtual.slice(1)}</span>
                                            </div>
                                            <div class="d-flex justify-content-between border-bottom py-1">
                                                <span>Campos:</span>
                                                <span class="fw-medium">${(template.campos || []).length}</span>
                                            </div>
                                            <div class="d-flex justify-content-between py-1">
                                                <span>Status:</span>
                                                <span class="badge bg-success">Ativo</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer bg-light">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Fechar
                        </button>
                        <button type="button" class="btn btn-warning" onclick="editarTemplate(${template.id})">
                            <i class="fas fa-edit me-1"></i>Editar
                        </button>
                        <button type="button" class="btn btn-success" onclick="usarTemplate(${template.id})">
                            <i class="fas fa-play me-1"></i>Usar Template
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente e adicionar novo
    const existingModal = document.getElementById('modalVisualizarTemplate');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalVisualizarTemplate'));
    modal.show();
}

// ============ EDITAR TEMPLATE ============
// ============ EDITAR TEMPLATE ============
function editarTemplate(templateId) {
    const template = getTemplateById(templateId);
    if (!template) {
        mostrarMensagem('error', 'Template não encontrado');
        return;
    }
    
    mostrarModalEdicao(template);
}

function mostrarModalEdicao(template) {
    const modalHtml = `
        <div class="modal fade" id="modalEditarTemplate" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>
                            Editar Template: ${template.nome}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="formEditarTemplate" onsubmit="salvarEdicaoTemplate(event, ${template.id})">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-12 mb-4">
                                    <div class="form-floating">
                                        <input type="text" class="form-control" id="editNome" 
                                               value="${template.nome}" placeholder="Nome do Template" required>
                                        <label for="editNome">
                                            <i class="fas fa-file-alt me-1"></i>Nome do Template
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="col-12 mb-4">
                                    <div class="form-floating">
                                        <textarea class="form-control" id="editDescricao" 
                                                  style="height: 100px" placeholder="Descrição" required>${template.desc || template.descricao}</textarea>
                                        <label for="editDescricao">
                                            <i class="fas fa-align-left me-1"></i>Descrição do Template
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="col-12 mb-4">
                                    <label class="form-label fw-bold">
                                        <i class="fas fa-list me-1"></i>Campos do Template
                                    </label>
                                    <div class="form-floating">
                                        <textarea class="form-control" id="editCampos" 
                                                  style="height: 120px" placeholder="Digite os campos separados por vírgula" required>${(template.campos || []).join(', ')}</textarea>
                                        <label for="editCampos">Digite os campos separados por vírgula</label>
                                    </div>
                                    <div class="form-text">
                                        <i class="fas fa-info-circle me-1"></i>
                                        Exemplo: Nome completo, CPF, Endereço, Telefone
                                    </div>
                                </div>
                                
                                <div class="col-md-6 mb-4">
                                    <div class="form-floating">
                                        <input type="text" class="form-control" id="editIcone" 
                                               value="${template.icon || 'fas fa-file-alt'}" placeholder="Ícone">
                                        <label for="editIcone">
                                            <i class="fas fa-icons me-1"></i>Ícone (Font Awesome)
                                        </label>
                                    </div>
                                    <div class="form-text">
                                        <i class="fas fa-lightbulb me-1"></i>
                                        Ex: fas fa-file-alt, fas fa-gavel, fas fa-balance-scale
                                    </div>
                                </div>
                                
                                <div class="col-md-6 mb-4">
                                    <div class="card bg-light">
                                        <div class="card-body text-center">
                                            <h6 class="card-title">Pré-visualização</h6>
                                            <i id="previewIcone" class="${template.icon || 'fas fa-file-alt'}" style="font-size: 2rem; color: #007bff;"></i>
                                            <p class="card-text mt-2" id="previewNome">${template.nome}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save me-1"></i>Salvar Alterações
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Fechar modal de visualização se aberto
    const visualModal = document.getElementById('modalVisualizarTemplate');
    if (visualModal) {
        bootstrap.Modal.getInstance(visualModal)?.hide();
    }
    
    // Remover modal existente e adicionar novo
    const existingModal = document.getElementById('modalEditarTemplate');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalEditarTemplate'));
    modal.show();
    
    // Adicionar event listeners para pré-visualização em tempo real
    document.getElementById('editNome').addEventListener('input', function() {
        document.getElementById('previewNome').textContent = this.value || 'Nome do Template';
    });
    
    document.getElementById('editIcone').addEventListener('input', function() {
        const icone = this.value || 'fas fa-file-alt';
        document.getElementById('previewIcone').className = icone;
    });
}

function salvarEdicaoTemplate(event, templateId) {
    event.preventDefault();
    
    const dados = {
        nome: document.getElementById('editNome').value.trim(),
        descricao: document.getElementById('editDescricao').value.trim(),
        campos: document.getElementById('editCampos').value.split(',').map(c => c.trim()).filter(c => c),
        icone: document.getElementById('editIcone').value.trim()
    };
    
    if (!dados.nome || !dados.descricao) {
        mostrarMensagem('error', 'Nome e descrição são obrigatórios');
        return;
    }
    
    // Enviar dados para API
    fetch(`/modulos/${areaAtual}/templates/${templateId}/editar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarMensagem('success', data.mensagem);
            
            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalEditarTemplate'));
            modal.hide();
            
            // Atualizar template na página
            atualizarTemplateNaPagina(templateId, data.template);
        } else {
            mostrarMensagem('error', data.erro || 'Erro ao salvar alterações');
        }
    })
    .catch(error => {
        console.error('Erro ao editar template:', error);
        mostrarMensagem('error', 'Erro de conexão');
    });
}

// ============ USAR TEMPLATE ============
function usarTemplate(templateId) {
    const template = getTemplateById(templateId);
    if (!template) {
        mostrarMensagem('error', 'Template não encontrado');
        return;
    }
    
    mostrarModalUso(template);
}

// ============ EXCLUIR TEMPLATE ============
function excluirTemplate(templateId) {
    const template = getTemplateById(templateId);
    if (!template) {
        mostrarMensagem('error', 'Template não encontrado');
        return;
    }
    
    // Confirmar exclusão
    if (confirm(`Tem certeza que deseja excluir o template "${template.nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        // Simular exclusão
        mostrarMensagem('success', `Template "${template.nome}" excluído com sucesso!`);
        
        // Remover da lista visual
        const templateElement = document.querySelector(`[data-template-id="${templateId}"]`);
        if (templateElement) {
            templateElement.remove();
        }
    }
}

function mostrarModalUso(template) {
    const modalHtml = `
        <div class="modal fade" id="modalUsarTemplate" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-play me-2"></i>
                            Usar Template: ${template.nome}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="formUsarTemplate" onsubmit="gerarDocumento(event, ${template.id})">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="alert alert-info d-flex align-items-center mb-4">
                                        <i class="fas fa-info-circle me-2"></i>
                                        <div>
                                            <strong>Sobre este template:</strong> ${template.desc || template.descricao}
                                        </div>
                                    </div>
                                    
                                    <h6 class="fw-bold mb-3">
                                        <i class="fas fa-edit me-1"></i>
                                        Preencha os campos necessários:
                                    </h6>
                                    
                                    ${(template.campos || []).map((campo, index) => `
                                        <div class="mb-4">
                                            <div class="form-floating">
                                                <textarea class="form-control" name="campo_${index}" 
                                                          style="height: 80px" placeholder="${campo}" required></textarea>
                                                <label>
                                                    <i class="fas fa-pen me-1"></i>${campo}
                                                </label>
                                            </div>
                                        </div>
                                    `).join('')}
                                    
                                    <div class="row">
                                        <div class="col-md-6 mb-4">
                                            <div class="form-floating">
                                                <select class="form-select" name="formato" required>
                                                    <option value="pdf">PDF - Documento portátil</option>
                                                    <option value="docx">Word (DOCX) - Editável</option>
                                                </select>
                                                <label>
                                                    <i class="fas fa-file me-1"></i>Formato do documento
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div class="col-md-6 mb-4">
                                            <div class="form-floating">
                                                <input type="text" class="form-control" name="nome_arquivo" 
                                                       value="${template.nome.replace(/\s+/g, '_')}_documento" required>
                                                <label>
                                                    <i class="fas fa-tag me-1"></i>Nome do arquivo
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-4">
                                    <div class="card bg-light h-100">
                                        <div class="card-header bg-primary text-white">
                                            <h6 class="mb-0">
                                                <i class="fas fa-eye me-1"></i>
                                                Pré-visualização
                                            </h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="text-center mb-3">
                                                <i class="${template.icon || 'fas fa-file-alt'}" style="font-size: 3rem; color: #007bff;"></i>
                                                <h6 class="mt-2">${template.nome}</h6>
                                            </div>
                                            
                                            <div class="small">
                                                <div class="mb-2">
                                                    <strong>Campos:</strong>
                                                    <ul class="list-unstyled mt-1">
                                                        ${(template.campos || []).map(campo => 
                                                            `<li><i class="fas fa-check text-success me-1"></i>${campo}</li>`
                                                        ).join('')}
                                                    </ul>
                                                </div>
                                                
                                                <div class="mb-2">
                                                    <strong>Área:</strong> ${areaAtual.charAt(0).toUpperCase() + areaAtual.slice(1)}
                                                </div>
                                                
                                                <div class="mb-2">
                                                    <strong>Tipo:</strong> Documento jurídico especializado
                                                </div>
                                            </div>
                                            
                                            <div class="mt-3 p-2 bg-warning bg-opacity-10 rounded">
                                                <small class="text-muted">
                                                    <i class="fas fa-lightbulb me-1"></i>
                                                    O documento será gerado automaticamente com base nos dados fornecidos.
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Cancelar
                            </button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-file-download me-1"></i>Gerar Documento
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Fechar modal de visualização se aberto
    const visualModal = document.getElementById('modalVisualizarTemplate');
    if (visualModal) {
        bootstrap.Modal.getInstance(visualModal)?.hide();
    }
    
    // Remover modal existente e adicionar novo
    const existingModal = document.getElementById('modalUsarTemplate');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalUsarTemplate'));
    modal.show();
}

function gerarDocumento(event, templateId) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const campos = {};
    
    // Coletar dados dos campos
    for (let [key, value] of formData.entries()) {
        campos[key] = value;
    }
    
    const dados = {
        campos: campos,
        formato: formData.get('formato') || 'pdf'
    };
    
    // Enviar dados para API
    fetch(`/modulos/${areaAtual}/templates/${templateId}/usar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarMensagem('success', data.mensagem);
            
            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalUsarTemplate'));
            modal.hide();
            
            // Simular download (em produção seria um link real)
            if (data.download_url) {
                console.log('Download simulado:', data.download_url);
                mostrarMensagem('info', 'Documento gerado! Verificar downloads.');
            }
        } else {
            mostrarMensagem('error', data.erro || 'Erro ao gerar documento');
        }
    })
    .catch(error => {
        console.error('Erro ao usar template:', error);
        mostrarMensagem('error', 'Erro de conexão');
    });
}

// ============ EXCLUIR TEMPLATE ============
function excluirTemplate(templateId) {
    const template = getTemplateById(templateId);
    if (!template) {
        mostrarMensagem('error', 'Template não encontrado');
        return;
    }
    
    // Confirmar exclusão
    if (confirm(`Tem certeza que deseja excluir o template "${template.nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        executarExclusao(templateId);
    }
}

function executarExclusao(templateId) {
    fetch(`/modulos/${areaAtual}/templates/${templateId}/excluir`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarMensagem('success', data.mensagem);
            
            // Remover template da página
            const templateElement = document.querySelector(`[data-template-id="${templateId}"]`);
            if (templateElement) {
                templateElement.style.transition = 'all 0.3s ease';
                templateElement.style.opacity = '0';
                templateElement.style.transform = 'translateX(-100px)';
                
                setTimeout(() => {
                    templateElement.remove();
                }, 300);
            }
        } else {
            mostrarMensagem('error', data.erro || 'Erro ao excluir template');
        }
    })
    .catch(error => {
        console.error('Erro ao excluir template:', error);
        mostrarMensagem('error', 'Erro de conexão');
    });
}

// ============ FUNÇÕES AUXILIARES ============
function getTemplateById(id) {
    return templatesData.find(template => template.id == id);
}

function atualizarTemplateNaPagina(templateId, novosDados) {
    // Atualizar dados na memória
    const index = templatesData.findIndex(t => t.id == templateId);
    if (index !== -1) {
        templatesData[index] = { ...templatesData[index], ...novosDados };
    }
    
    // Atualizar visual na página
    const templateElement = document.querySelector(`[data-template-id="${templateId}"]`);
    if (templateElement) {
        const nomeElement = templateElement.querySelector('.template-nome');
        const descElement = templateElement.querySelector('.template-desc');
        
        if (nomeElement) nomeElement.textContent = novosDados.nome;
        if (descElement) descElement.textContent = novosDados.descricao;
    }
}

function mostrarMensagem(tipo, mensagem) {
    // Criar elemento de mensagem
    const alertClass = tipo === 'success' ? 'alert-success' : 
                      tipo === 'error' ? 'alert-danger' : 
                      tipo === 'info' ? 'alert-info' : 'alert-warning';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : 
                              tipo === 'error' ? 'exclamation-circle' : 
                              tipo === 'info' ? 'info-circle' : 'exclamation-triangle'} me-2"></i>
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Função para ver todos os templates (compatibilidade)
function verTodosTemplates() {
    window.location.href = '/templates-juridicos';
}

// Função para abrir template (compatibilidade)
function verTodosTemplates() {
    // Redirecionar para página de todos os templates da área atual
    window.location.href = `/templates/juridicos?area=${areaAtual}`;
}

function abrirTemplate(templateId) {
    visualizarTemplate(templateId);
}

// Controle de visualização de templates (cards vs lista)
document.addEventListener('DOMContentLoaded', function() {
    // Alternar entre visualização de cards e lista
    const btnViewCards = document.getElementById('btn-view-cards');
    const btnViewList = document.getElementById('btn-view-list');
    const cardsView = document.getElementById('templates-cards-view');
    const listView = document.getElementById('templates-list-view');
    
    if (btnViewCards && btnViewList && cardsView && listView) {
        btnViewCards.addEventListener('click', function() {
            this.classList.add('active');
            btnViewList.classList.remove('active');
            cardsView.classList.remove('d-none');
            listView.classList.add('d-none');
        });
        
        btnViewList.addEventListener('click', function() {
            this.classList.add('active');
            btnViewCards.classList.remove('active');
            cardsView.classList.add('d-none');
            listView.classList.remove('d-none');
        });
    }
});

// Função para criar novo template
function criarNovoTemplate() {
    const modalHtml = `
        <div class="modal fade" id="modalCriarTemplate" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-plus me-2"></i>
                            Criar Novo Template
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="formCriarTemplate" onsubmit="salvarNovoTemplate(event)">
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="mb-4">
                                        <div class="form-floating">
                                            <input type="text" class="form-control" id="novoNome" name="nome" required>
                                            <label><i class="fas fa-file-text me-1"></i>Nome do Template</label>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <div class="form-floating">
                                            <textarea class="form-control" id="novaDescricao" name="descricao" style="height: 80px" required></textarea>
                                            <label><i class="fas fa-info-circle me-1"></i>Descrição</label>
                                        </div>
                                    </div>
                                    
                                    <div class="row">
                                        <div class="col-md-6 mb-4">
                                            <div class="form-floating">
                                                <input type="text" class="form-control" id="novaCategoria" name="categoria" value="Geral">
                                                <label><i class="fas fa-tag me-1"></i>Categoria</label>
                                            </div>
                                        </div>
                                        
                                        <div class="col-md-6 mb-4">
                                            <div class="form-floating">
                                                <input type="text" class="form-control" id="novoIcone" name="icon" value="fas fa-file-alt">
                                                <label><i class="fas fa-icons me-1"></i>Ícone</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-4">
                                    <div class="card bg-light h-100">
                                        <div class="card-header bg-primary text-white">
                                            <h6 class="mb-0">
                                                <i class="fas fa-eye me-1"></i>
                                                Pré-visualização
                                            </h6>
                                        </div>
                                        <div class="card-body text-center">
                                            <div class="mb-3">
                                                <i id="previewNovoIcone" class="fas fa-file-alt" style="font-size: 3rem; color: #007bff;"></i>
                                                <h6 class="mt-2" id="previewNovoNome">Novo Template</h6>
                                            </div>
                                            
                                            <div class="small text-muted">
                                                <p id="previewNovaDescricao">Digite a descrição do template...</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-1"></i>Cancelar
                            </button>
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save me-1"></i>Criar Template
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente e adicionar novo
    const existingModal = document.getElementById('modalCriarTemplate');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('modalCriarTemplate'));
    modal.show();
    
    // Adicionar event listeners para pré-visualização em tempo real
    document.getElementById('novoNome').addEventListener('input', function() {
        document.getElementById('previewNovoNome').textContent = this.value || 'Novo Template';
    });
    
    document.getElementById('novaDescricao').addEventListener('input', function() {
        document.getElementById('previewNovaDescricao').textContent = this.value || 'Digite a descrição do template...';
    });
    
    document.getElementById('novoIcone').addEventListener('input', function() {
        const icone = this.value || 'fas fa-file-alt';
        document.getElementById('previewNovoIcone').className = icone;
    });
}

// Função para salvar novo template
function salvarNovoTemplate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const dados = Object.fromEntries(formData);
    
    // Adicionar campos padrão
    dados.campos = ['Conteúdo Principal', 'Observações'];
    dados.area = areaAtual;
    
    fetch(`/api/templates/${areaAtual}/criar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarMensagem('success', 'Template criado com sucesso!');
            bootstrap.Modal.getInstance(document.getElementById('modalCriarTemplate')).hide();
            // Recarregar página para mostrar novo template
            setTimeout(() => location.reload(), 1000);
        } else {
            mostrarMensagem('error', data.erro || 'Erro ao criar template');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarMensagem('error', 'Erro de conexão');
    });
}

// Exportar funções globalmente
window.initTemplateManager = initTemplateManager;
window.visualizarTemplate = visualizarTemplate;
window.editarTemplate = editarTemplate;
window.usarTemplate = usarTemplate;
window.excluirTemplate = excluirTemplate;
window.verTodosTemplates = verTodosTemplates;
window.abrirTemplate = abrirTemplate;
window.criarNovoTemplate = criarNovoTemplate;
window.salvarNovoTemplate = salvarNovoTemplate;

console.log('Template Manager carregado com sucesso!');