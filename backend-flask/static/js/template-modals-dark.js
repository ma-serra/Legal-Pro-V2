/**
 * Sistema de Modais Dark Theme para Templates Jurídicos
 * UX Exclusiva e Experiência Visual Única
 */

class TemplateModalManager {
    constructor() {
        this.currentTemplate = null;
        this.previewTimer = null;
        this.formData = {};
        this.isGenerating = false;
        
        this.init();
    }
    
    init() {
        // Garantir que o CSS dark theme esteja carregado
        this.loadDarkThemeCSS();
        
        // Configurar eventos globais
        this.setupGlobalEvents();
    }
    
    loadDarkThemeCSS() {
        if (!document.querySelector('link[href*="modals-dark-theme.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/modals-dark-theme.css';
            document.head.appendChild(link);
        }
    }
    
    setupGlobalEvents() {
        // Limpar modais ao fechar
        document.addEventListener('hidden.bs.modal', (e) => {
            if (e.target.classList.contains('modal-dark')) {
                this.cleanupModal(e.target);
            }
        });
        
        // Prevenir fechamento acidental durante geração
        document.addEventListener('hide.bs.modal', (e) => {
            if (this.isGenerating && e.target.classList.contains('modal-dark')) {
                e.preventDefault();
                this.showWarning('Aguarde a conclusão da geração do documento...');
            }
        });
    }
    
    /**
     * Mostra modal para utilizar template
     */
    showTemplateModal(template) {
        this.currentTemplate = template;
        this.createModalHTML(template);
        
        const modal = new bootstrap.Modal(document.getElementById('modalUtilizarTemplate'));
        modal.show();
        
        // Configurar eventos do modal
        this.setupModalEvents();
        
        // Carregar tema da pré-visualização
        setTimeout(() => {
            this.loadPreviewTheme();
        }, 100);
        
        // Gerar preview inicial
        this.generatePreview();
    }
    
    createModalHTML(template) {
        const modalId = 'modalUtilizarTemplate';
        
        // Remover modal existente
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
            existingModal.remove();
        }
        
        const modalHTML = `
            <div class="modal fade modal-dark" id="${modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-fullscreen-lg-down">
                    <div class="modal-content">
                        ${this.createModalHeader(template)}
                        ${this.createModalBody(template)}
                        ${this.createModalFooter()}
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    createModalHeader(template) {
        return `
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="fas fa-magic"></i>
                    Utilizar Template: ${template.nome || template.title}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
    
    createModalBody(template) {
        return `
            <div class="modal-body">
                <div class="row g-4">
                    <div class="col-lg-6">
                        ${this.createTemplateInfo(template)}
                        ${this.createFormSection(template)}
                    </div>
                    <div class="col-lg-6">
                        ${this.createPreviewSection()}
                    </div>
                </div>
            </div>
        `;
    }
    
    createTemplateInfo(template) {
        return `
            <div class="template-info-card">
                <h6>
                    <i class="fas fa-info-circle"></i>
                    Informações do Template
                </h6>
                <p><strong>Nome:</strong> ${template.nome || template.title}</p>
                <p><strong>Descrição:</strong> ${template.descricao || template.description || 'Template jurídico especializado'}</p>
                <p><strong>Categoria:</strong> ${template.categoria || template.category || 'Geral'}</p>
                <p><strong>Módulo:</strong> ${template.modulo_nome || template.module || 'Sistema Jurídico'}</p>
            </div>
        `;
    }
    
    createFormSection(template) {
        const campos = template.campos || this.getDefaultFields(template);
        
        return `
            <div class="form-section">
                <div class="form-section-title">
                    <i class="fas fa-edit"></i>
                    Dados do Documento
                </div>
                <form id="templateForm" class="form-dark">
                    ${campos.map(campo => this.createFieldHTML(campo)).join('')}
                    
                    <div class="form-section" style="margin-top: 2rem;">
                        <div class="form-section-title">
                            <i class="fas fa-cog"></i>
                            Configurações de Geração
                        </div>
                        
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">
                                    <i class="fas fa-file-alt"></i>
                                    Formato de Saída
                                </label>
                                <select class="form-select" id="formatoSaida" name="formato">
                                    <option value="docx">Documento Word (.docx)</option>
                                    <option value="pdf">Documento PDF (.pdf)</option>
                                    <option value="html">Página Web (.html)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">
                                    <i class="fas fa-font"></i>
                                    Estilo do Documento
                                </label>
                                <select class="form-select" id="estiloDocumento" name="estilo">
                                    <option value="formal">Formal - Jurídico</option>
                                    <option value="moderno">Moderno - Corporativo</option>
                                    <option value="minimalista">Minimalista - Clean</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        `;
    }
    
    createFieldHTML(campo) {
        const fieldId = `field_${campo.nome || campo.name || Math.random().toString(36).substr(2, 9)}`;
        const fieldName = campo.nome || campo.name || fieldId;
        const fieldLabel = campo.label || this.formatFieldLabel(fieldName);
        const fieldType = campo.tipo || campo.type || 'text';
        const isRequired = campo.obrigatorio || campo.required || false;
        const placeholder = campo.placeholder || `Digite ${fieldLabel.toLowerCase()}...`;
        
        let fieldHTML = '';
        
        switch (fieldType) {
            case 'textarea':
                fieldHTML = `
                    <div class="mb-3">
                        <label for="${fieldId}" class="form-label">
                            <i class="fas fa-align-left"></i>
                            ${fieldLabel} ${isRequired ? '<span class="text-danger">*</span>' : ''}
                        </label>
                        <textarea 
                            class="form-control" 
                            id="${fieldId}" 
                            name="${fieldName}" 
                            rows="4" 
                            placeholder="${placeholder}"
                            ${isRequired ? 'required' : ''}
                        ></textarea>
                    </div>
                `;
                break;
                
            case 'select':
                const options = campo.opcoes || campo.options || ['Opção 1', 'Opção 2', 'Opção 3'];
                fieldHTML = `
                    <div class="mb-3">
                        <label for="${fieldId}" class="form-label">
                            <i class="fas fa-list"></i>
                            ${fieldLabel} ${isRequired ? '<span class="text-danger">*</span>' : ''}
                        </label>
                        <select class="form-select" id="${fieldId}" name="${fieldName}" ${isRequired ? 'required' : ''}>
                            <option value="">Selecione uma opção...</option>
                            ${options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                        </select>
                    </div>
                `;
                break;
                
            case 'number':
                fieldHTML = `
                    <div class="mb-3">
                        <label for="${fieldId}" class="form-label">
                            <i class="fas fa-hashtag"></i>
                            ${fieldLabel} ${isRequired ? '<span class="text-danger">*</span>' : ''}
                        </label>
                        <input 
                            type="number" 
                            class="form-control" 
                            id="${fieldId}" 
                            name="${fieldName}" 
                            placeholder="${placeholder}"
                            ${isRequired ? 'required' : ''}
                        >
                    </div>
                `;
                break;
                
            case 'date':
                fieldHTML = `
                    <div class="mb-3">
                        <label for="${fieldId}" class="form-label">
                            <i class="fas fa-calendar"></i>
                            ${fieldLabel} ${isRequired ? '<span class="text-danger">*</span>' : ''}
                        </label>
                        <input 
                            type="date" 
                            class="form-control" 
                            id="${fieldId}" 
                            name="${fieldName}"
                            ${isRequired ? 'required' : ''}
                        >
                    </div>
                `;
                break;
                
            default: // text
                fieldHTML = `
                    <div class="mb-3">
                        <label for="${fieldId}" class="form-label">
                            <i class="fas fa-keyboard"></i>
                            ${fieldLabel} ${isRequired ? '<span class="text-danger">*</span>' : ''}
                        </label>
                        <input 
                            type="text" 
                            class="form-control" 
                            id="${fieldId}" 
                            name="${fieldName}" 
                            placeholder="${placeholder}"
                            ${isRequired ? 'required' : ''}
                        >
                    </div>
                `;
        }
        
        return fieldHTML;
    }
    
    createPreviewSection() {
        return `
            <div class="preview-area" id="previewArea">
                <div class="preview-header">
                    <h6>
                        <i class="fas fa-eye"></i>
                        Pré-visualização do Documento
                    </h6>
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="templateModalManager.refreshPreview()">
                        <i class="fas fa-sync-alt"></i>
                        Atualizar
                    </button>
                </div>
                <div class="preview-theme-controls" style="background: rgba(0,0,0,0.2); padding: 0.75rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 1rem;">
                    <span style="color: #e2e8f0; font-size: 0.85rem; font-weight: 500;">Tema:</span>
                    <label style="position: relative; display: inline-block; width: 50px; height: 24px;">
                        <input type="checkbox" id="previewThemeToggle" onchange="templateModalManager.togglePreviewTheme()" style="opacity: 0; width: 0; height: 0;">
                        <span style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #374151; transition: 0.3s; border-radius: 24px; border: 1px solid rgba(255,255,255,0.2);"></span>
                        <span style="position: absolute; content: ''; height: 18px; width: 18px; left: 2px; bottom: 2px; background: white; transition: 0.3s; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></span>
                    </label>
                    <span style="color: #94a3b8; font-size: 0.8rem;">Escuro/Claro</span>
                </div>
                <div id="previewContent" class="preview-content">
                    <div class="preview-placeholder">
                        <i class="fas fa-file-alt" style="font-size: 3rem;"></i>
                        <p>Preencha os campos ao lado para visualizar o documento...</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    createModalFooter() {
        return `
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary-dark" data-bs-dismiss="modal">
                    <i class="fas fa-times"></i>
                    Cancelar
                </button>
                <button type="button" class="btn btn-warning-dark" onclick="templateModalManager.saveAsDraft()">
                    <i class="fas fa-save"></i>
                    Salvar Rascunho
                </button>
                <button type="button" class="btn btn-primary-dark" onclick="templateModalManager.generatePreview()">
                    <i class="fas fa-eye"></i>
                    Atualizar Preview
                </button>
                <button type="button" class="btn btn-success-dark" onclick="templateModalManager.generateDocument()">
                    <i class="fas fa-download"></i>
                    Gerar Documento
                </button>
            </div>
        `;
    }
    
    setupModalEvents() {
        const form = document.getElementById('templateForm');
        if (!form) return;
        
        // Auto-preview ao digitar
        form.addEventListener('input', (e) => {
            clearTimeout(this.previewTimer);
            this.previewTimer = setTimeout(() => {
                this.generatePreview();
            }, 1000);
        });
        
        // Validação em tempo real
        form.addEventListener('input', (e) => {
            this.validateField(e.target);
        });
        
        // Salvar dados no sessionStorage
        form.addEventListener('input', (e) => {
            this.saveFormData();
        });
    }
    
    generatePreview() {
        const formData = this.getFormData();
        const previewContent = document.getElementById('previewContent');
        
        if (!previewContent) return;
        
        if (Object.keys(formData).length === 0) {
            previewContent.innerHTML = `
                <div class="preview-placeholder">
                    <i class="fas fa-file-alt" style="font-size: 3rem;"></i>
                    <p>Preencha os campos ao lado para visualizar o documento...</p>
                </div>
            `;
            return;
        }
        
        // Simular geração de preview
        const template = this.currentTemplate;
        const previewHTML = this.generatePreviewHTML(template, formData);
        
        previewContent.innerHTML = previewHTML;
    }
    
    generatePreviewHTML(template, formData) {
        const currentDate = new Date().toLocaleDateString('pt-BR');
        
        return `
            <div class="document-preview">
                <div style="text-align: center; margin-bottom: 2rem; border-bottom: 2px solid var(--modal-border); padding-bottom: 1rem;">
                    <h4 style="color: var(--modal-text); margin-bottom: 0.5rem;">${template.nome || template.title}</h4>
                    <p style="color: var(--modal-text-muted); margin: 0;">Documento gerado em ${currentDate}</p>
                </div>
                
                <div style="line-height: 1.8; color: var(--modal-text);">
                    ${this.buildDocumentContent(template, formData)}
                </div>
                
                <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--modal-border); text-align: center;">
                    <p style="color: var(--modal-text-muted); font-size: 0.9rem; margin: 0;">
                        <i class="fas fa-info-circle"></i>
                        Esta é uma pré-visualização. O documento final pode ter formatação adicional.
                    </p>
                </div>
            </div>
        `;
    }
    
    buildDocumentContent(template, formData) {
        // Construir conteúdo baseado no tipo de template
        let content = `<p><strong>Documento:</strong> ${template.nome || template.title}</p>`;
        
        if (template.categoria) {
            content += `<p><strong>Categoria:</strong> ${template.categoria}</p>`;
        }
        
        content += '<div style="margin: 1.5rem 0;"><strong>Dados Informados:</strong></div>';
        content += '<div style="background: rgba(45, 55, 72, 0.3); padding: 1rem; border-radius: 8px; margin: 1rem 0;">';
        
        Object.entries(formData).forEach(([key, value]) => {
            if (value && value.trim()) {
                const label = this.formatFieldLabel(key);
                content += `<p><strong>${label}:</strong> ${value}</p>`;
            }
        });
        
        content += '</div>';
        
        // Adicionar conteúdo padrão baseado no template
        content += this.getTemplateSpecificContent(template, formData);
        
        return content;
    }
    
    getTemplateSpecificContent(template, formData) {
        const templateType = template.categoria?.toLowerCase() || '';
        
        switch (templateType) {
            case 'contrato':
                return this.generateContractContent(formData);
            case 'petição':
            case 'peticao':
                return this.generatePetitionContent(formData);
            case 'parecer':
                return this.generateOpinionContent(formData);
            default:
                return this.generateGenericContent(formData);
        }
    }
    
    generateContractContent(formData) {
        return `
            <div style="margin: 1.5rem 0;">
                <h5 style="color: var(--modal-text);">CLÁUSULAS CONTRATUAIS</h5>
                <p>As partes acordam com os termos especificados e se comprometem ao cumprimento integral das obrigações assumidas neste instrumento.</p>
                
                <div style="margin: 1rem 0;">
                    <p><strong>CLÁUSULA PRIMEIRA:</strong> Do objeto e finalidade do presente contrato.</p>
                    <p><strong>CLÁUSULA SEGUNDA:</strong> Das obrigações das partes contratantes.</p>
                    <p><strong>CLÁUSULA TERCEIRA:</strong> Das condições de pagamento e valores.</p>
                </div>
            </div>
        `;
    }
    
    generatePetitionContent(formData) {
        return `
            <div style="margin: 1.5rem 0;">
                <h5 style="color: var(--modal-text);">PETIÇÃO INICIAL</h5>
                <p>Vem respeitosamente à presença de Vossa Excelência expor e requerer o que segue:</p>
                
                <div style="margin: 1rem 0;">
                    <p><strong>DOS FATOS:</strong></p>
                    <p>Exposição dos fatos relevantes para o caso em questão.</p>
                    
                    <p><strong>DO DIREITO:</strong></p>
                    <p>Fundamentação jurídica aplicável à situação apresentada.</p>
                    
                    <p><strong>DOS PEDIDOS:</strong></p>
                    <p>Requerimentos específicos solicitados ao juízo.</p>
                </div>
            </div>
        `;
    }
    
    generateOpinionContent(formData) {
        return `
            <div style="margin: 1.5rem 0;">
                <h5 style="color: var(--modal-text);">PARECER JURÍDICO</h5>
                <p>Análise técnica sobre a questão jurídica apresentada.</p>
                
                <div style="margin: 1rem 0;">
                    <p><strong>1. CONSIDERAÇÕES INICIAIS</strong></p>
                    <p>Contextualização da questão jurídica.</p>
                    
                    <p><strong>2. ANÁLISE JURÍDICA</strong></p>
                    <p>Exame detalhado dos aspectos legais envolvidos.</p>
                    
                    <p><strong>3. CONCLUSÃO</strong></p>
                    <p>Opinião técnica fundamentada sobre o caso.</p>
                </div>
            </div>
        `;
    }
    
    generateGenericContent(formData) {
        return `
            <div style="margin: 1.5rem 0;">
                <h5 style="color: var(--modal-text);">CONTEÚDO DO DOCUMENTO</h5>
                <p>Documento elaborado conforme as especificações fornecidas e padrões jurídicos aplicáveis.</p>
                
                <div style="margin: 1rem 0;">
                    <p>O presente documento foi gerado automaticamente com base nas informações fornecidas e serve como base para elaboração do documento final.</p>
                </div>
            </div>
        `;
    }
    
    async generateDocument() {
        if (this.isGenerating) return;
        
        const formData = this.getFormData();
        const formato = formData.formato || 'docx';
        
        if (!this.validateForm()) {
            this.showError('Por favor, preencha todos os campos obrigatórios.');
            return;
        }
        
        this.isGenerating = true;
        this.showLoadingState();
        
        try {
            const response = await fetch('/api/templates/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    template_id: this.currentTemplate.id,
                    data: formData,
                    format: formato
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadDocument(blob, formato);
                this.showSuccess('Documento gerado com sucesso!');
                
                // Fechar modal após sucesso
                setTimeout(() => {
                    bootstrap.Modal.getInstance(document.getElementById('modalUtilizarTemplate')).hide();
                }, 2000);
            } else {
                throw new Error('Erro ao gerar documento');
            }
        } catch (error) {
            console.error('Erro ao gerar documento:', error);
            this.showError('Erro ao gerar documento. Tente novamente.');
        } finally {
            this.isGenerating = false;
            this.hideLoadingState();
        }
    }
    
    downloadDocument(blob, format) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentTemplate.nome || 'documento'}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    saveAsDraft() {
        const formData = this.getFormData();
        const draftData = {
            template_id: this.currentTemplate.id,
            template_name: this.currentTemplate.nome || this.currentTemplate.title,
            data: formData,
            saved_at: new Date().toISOString()
        };
        
        localStorage.setItem(`draft_${this.currentTemplate.id}`, JSON.stringify(draftData));
        this.showSuccess('Rascunho salvo com sucesso!');
    }
    
    validateForm() {
        const form = document.getElementById('templateForm');
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.markFieldInvalid(field);
                isValid = false;
            } else {
                this.markFieldValid(field);
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        if (field.hasAttribute('required') && !field.value.trim()) {
            this.markFieldInvalid(field);
        } else {
            this.markFieldValid(field);
        }
    }
    
    markFieldInvalid(field) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
    }
    
    markFieldValid(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
    }
    
    getFormData() {
        const form = document.getElementById('templateForm');
        if (!form) return {};
        
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    saveFormData() {
        this.formData = this.getFormData();
        sessionStorage.setItem('templateFormData', JSON.stringify(this.formData));
    }
    
    loadFormData() {
        const saved = sessionStorage.getItem('templateFormData');
        if (saved) {
            this.formData = JSON.parse(saved);
            this.populateForm(this.formData);
        }
    }
    
    populateForm(data) {
        Object.entries(data).forEach(([key, value]) => {
            const field = document.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = value;
            }
        });
    }
    
    getDefaultFields(template) {
        return [
            { nome: 'titulo', tipo: 'text', obrigatorio: true, label: 'Título do Documento' },
            { nome: 'parte1', tipo: 'text', obrigatorio: true, label: 'Primeira Parte' },
            { nome: 'parte2', tipo: 'text', obrigatorio: false, label: 'Segunda Parte' },
            { nome: 'objeto', tipo: 'textarea', obrigatorio: true, label: 'Objeto/Finalidade' },
            { nome: 'observacoes', tipo: 'textarea', obrigatorio: false, label: 'Observações Adicionais' }
        ];
    }
    
    formatFieldLabel(fieldName) {
        return fieldName
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    refreshPreview() {
        this.generatePreview();
        this.showInfo('Pré-visualização atualizada!');
    }
    
    togglePreviewTheme() {
        const previewContent = document.getElementById('previewContent');
        const toggle = document.getElementById('previewThemeToggle');
        const slider = toggle ? toggle.nextElementSibling : null;
        const ball = slider ? slider.nextElementSibling : null;
        
        if (!previewContent || !toggle || !slider || !ball) return;
        
        if (toggle.checked) {
            // Tema claro
            previewContent.style.background = '#f7fafc';
            previewContent.style.color = '#2d3748';
            slider.style.background = '#10b981';
            ball.style.transform = 'translateX(26px)';
            this.showInfo('Tema claro ativado');
        } else {
            // Tema escuro
            previewContent.style.background = '#2d3748';
            previewContent.style.color = '#e2e8f0';
            slider.style.background = '#374151';
            ball.style.transform = 'translateX(0px)';
            this.showInfo('Tema escuro ativado');
        }
        
        // Salvar preferência
        localStorage.setItem('previewTheme', toggle.checked ? 'light' : 'dark');
    }
    
    loadPreviewTheme() {
        const savedTheme = localStorage.getItem('previewTheme');
        const toggle = document.getElementById('previewThemeToggle');
        const previewArea = document.getElementById('previewArea');
        
        if (toggle && previewArea) {
            if (savedTheme === 'light') {
                toggle.checked = true;
                previewArea.classList.add('light-theme');
            } else {
                toggle.checked = false;
                previewArea.classList.remove('light-theme');
            }
        }
    }
    
    showLoadingState() {
        const modal = document.getElementById('modalUtilizarTemplate');
        if (!modal) return;
        
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="loading-spinner"></div>
                <p style="color: var(--modal-text); margin-top: 1rem;">Gerando documento...</p>
            </div>
        `;
        
        modal.querySelector('.modal-content').appendChild(loadingOverlay);
    }
    
    hideLoadingState() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        // Criar notificação toast de forma segura
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        
        // Criar estrutura DOM segura sem innerHTML
        const flexDiv = document.createElement('div');
        flexDiv.className = 'd-flex';
        
        const toastBody = document.createElement('div');
        toastBody.className = 'toast-body';
        
        const icon = document.createElement('i');
        icon.className = `fas fa-${this.getIconForType(type)} me-2`;
        
        const messageText = document.createTextNode(message);
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close btn-close-white me-2 m-auto';
        closeButton.setAttribute('data-bs-dismiss', 'toast');
        
        // Montar estrutura
        toastBody.appendChild(icon);
        toastBody.appendChild(messageText);
        flexDiv.appendChild(toastBody);
        flexDiv.appendChild(closeButton);
        toast.appendChild(flexDiv);
        
        // Container de toasts
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Mostrar toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover após esconder
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    cleanupModal(modal) {
        // Limpar timers
        if (this.previewTimer) {
            clearTimeout(this.previewTimer);
        }
        
        // Limpar dados
        this.currentTemplate = null;
        this.formData = {};
        this.isGenerating = false;
        
        // Remover dados da sessão
        sessionStorage.removeItem('templateFormData');
    }
}

// Instância global
window.templateModalManager = new TemplateModalManager();

// Função para usar template (compatibilidade)
function utilizarTemplate(template) {
    window.templateModalManager.showTemplateModal(template);
}

// Função para usar template por ID
function utilizarTemplatePorId(templateId) {
    // Buscar template nos dados globais se disponível
    if (window.todosTemplates) {
        const template = window.todosTemplates.find(t => t.id == templateId);
        if (template) {
            utilizarTemplate(template);
            return;
        }
    }
    
    // Buscar template via API
    fetch(`/api/templates/${templateId}`)
        .then(response => response.json())
        .then(template => {
            if (template) {
                utilizarTemplate(template);
            } else {
                templateModalManager.showError('Template não encontrado');
            }
        })
        .catch(error => {
            console.error('Erro ao buscar template:', error);
            templateModalManager.showError('Erro ao carregar template');
        });
}