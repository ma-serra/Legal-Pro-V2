/**
 * Legal Design Editor - Reconstruído do Zero
 * Sistema completamente novo para templates e ícones
 */

class LegalEditorRebuilt {
    constructor() {
        this.quill = null;
        this.templates = new Map();
        this.icons = new Map();
        this.isInitialized = false;
        
        console.log('🔧 Inicializando Legal Editor Rebuilt...');
        this.initialize();
    }

    async initialize() {
        try {
            // 1. Configurar editor Quill
            await this.setupQuillEditor();
            
            // 2. Carregar dados do servidor
            await this.loadTemplatesFromServer();
            await this.loadIconsFromServer();
            
            // 3. Configurar interface
            this.setupUI();
            this.bindEvents();
            
            this.isInitialized = true;
            console.log('✅ Legal Editor inicializado com sucesso');
            
        } catch (error) {
            console.error('❌ Erro na inicialização:', error);
        }
    }

    setupQuillEditor() {
        return new Promise((resolve) => {
            const editorElement = document.getElementById('richEditor');
            if (!editorElement) {
                console.error('Editor element not found');
                resolve();
                return;
            }

            this.quill = new Quill('#richEditor', {
                theme: 'snow',
                modules: {
                    toolbar: [
                        ['bold', 'italic', 'underline'],
                        [{ 'header': [1, 2, 3, false] }],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'align': [] }],
                        [{ 'color': [] }, { 'background': [] }],
                        ['clean']
                    ]
                }
            });

            this.quill.on('text-change', () => this.updateStats());
            console.log('✅ Quill editor configurado');
            resolve();
        });
    }

    async loadTemplatesFromServer() {
        try {
            console.log('📥 Carregando templates do servidor...');
            const response = await fetch('/legal-design-pro/api/templates-list');
            const data = await response.json();
            
            if (data.success && data.templates) {
                this.templates.clear();
                
                data.templates.forEach(template => {
                    this.templates.set(template.id, template);
                });
                
                console.log(`✅ ${this.templates.size} templates carregados`);
                this.renderTemplatesUI();
            } else {
                console.warn('Nenhum template encontrado');
            }
        } catch (error) {
            console.error('Erro ao carregar templates:', error);
        }
    }

    async loadIconsFromServer() {
        try {
            console.log('📥 Carregando ícones do servidor...');
            const response = await fetch('/api/icons/library');
            const data = await response.json();
            
            if (data.success && data.packs) {
                this.icons.clear();
                
                Object.entries(data.packs).forEach(([packName, packData]) => {
                    if (packData.icons) {
                        packData.icons.forEach(icon => {
                            this.icons.set(icon.name, icon);
                        });
                    }
                });
                
                console.log(`✅ ${this.icons.size} ícones carregados`);
                this.renderIconsUI();
            } else {
                console.warn('Nenhum ícone encontrado');
            }
        } catch (error) {
            console.error('Erro ao carregar ícones:', error);
        }
    }

    renderTemplatesUI() {
        const templatesContainer = document.getElementById('templates-tab');
        if (!templatesContainer) return;

        // Agrupar templates por área
        const templatesByArea = new Map();
        this.templates.forEach(template => {
            const area = template.area_juridica || 'geral';
            if (!templatesByArea.has(area)) {
                templatesByArea.set(area, []);
            }
            templatesByArea.get(area).push(template);
        });

        // Cores por área
        const areaColors = {
            'criminal': '#dc3545',
            'trabalhista': '#fd7e14',
            'empresarial': '#198754',
            'bancario': '#6f42c1',
            'consumidor': '#20c997',
            'agrario': '#ffc107',
            'securitario': '#e91e63'
        };

        let html = '';
        templatesByArea.forEach((templates, area) => {
            const color = areaColors[area] || '#007bff';
            
            html += `
                <div class="template-area mb-4">
                    <h6 style="color: ${color}; font-weight: bold; text-transform: uppercase; font-size: 0.8rem;">
                        ${area.replace('_', ' ')}
                    </h6>
                    <div class="row g-2">
            `;
            
            templates.forEach(template => {
                html += `
                    <div class="col-12 col-sm-6">
                        <button class="btn btn-outline-secondary btn-sm w-100 text-start template-btn-new"
                                style="border-color: ${color}; color: ${color};"
                                data-template-id="${template.id}"
                                data-area="${area}"
                                title="${template.descricao || template.nome}">
                            <small>${template.nome}</small>
                        </button>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });

        templatesContainer.innerHTML = html;
        console.log('✅ Interface de templates renderizada');
    }

    renderIconsUI() {
        const iconsContainer = document.getElementById('icons-tab');
        if (!iconsContainer) return;

        // Agrupar ícones por pack
        const iconsByPack = new Map();
        this.icons.forEach(icon => {
            const pack = icon.pack || 'pack1';
            if (!iconsByPack.has(pack)) {
                iconsByPack.set(pack, []);
            }
            iconsByPack.get(pack).push(icon);
        });

        let html = '';
        iconsByPack.forEach((icons, packName) => {
            html += `
                <div class="icon-pack mb-4">
                    <h6 style="color: #007bff; font-weight: bold; text-transform: uppercase; font-size: 0.8rem;">
                        ${packName.replace('pack', 'Pack ')}
                    </h6>
                    <div class="row g-2">
            `;
            
            icons.forEach(icon => {
                html += `
                    <div class="col-3">
                        <button class="btn btn-outline-secondary btn-sm w-100 p-2 icon-btn-new"
                                data-icon-path="${icon.path}"
                                title="${icon.name}">
                            <img src="${icon.path}" alt="${icon.name}" 
                                 style="width: 24px; height: 24px; object-fit: contain;">
                        </button>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });

        iconsContainer.innerHTML = html;
        console.log('✅ Interface de ícones renderizada');
    }

    setupUI() {
        // Configurar abas
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    bindEvents() {
        // Eventos para templates
        document.addEventListener('click', (e) => {
            if (e.target.closest('.template-btn-new')) {
                const btn = e.target.closest('.template-btn-new');
                const templateId = btn.dataset.templateId;
                const area = btn.dataset.area;
                this.insertTemplate(templateId, area);
            }
        });

        // Eventos para ícones
        document.addEventListener('click', (e) => {
            if (e.target.closest('.icon-btn-new')) {
                const btn = e.target.closest('.icon-btn-new');
                const iconPath = btn.dataset.iconPath;
                this.insertIcon(iconPath);
            }
        });

        console.log('✅ Eventos configurados');
    }

    async insertTemplate(templateId, area) {
        if (!this.quill) {
            console.error('Editor não inicializado');
            return;
        }

        try {
            console.log(`📝 Inserindo template ID: ${templateId}`);
            
            // Buscar template específico
            const template = this.templates.get(parseInt(templateId));
            if (!template) {
                console.error('Template não encontrado:', templateId);
                return;
            }

            // Buscar conteúdo HTML do template
            const response = await fetch(`/legal-design-pro/api/template-content/${template.nome.toLowerCase().replace(/\s+/g, '-')}?area=${area}`);
            const data = await response.json();
            
            if (data.success && data.template && data.template.conteudo_html) {
                // Inserir conteúdo real do banco
                const content = this.processTemplateContent(data.template.conteudo_html);
                this.insertContentIntoEditor(content);
                this.showSuccess(`Template "${template.nome}" inserido com sucesso!`);
            } else {
                // Fallback: template básico
                const fallbackContent = this.createFallbackTemplate(template, area);
                this.insertContentIntoEditor(fallbackContent);
                this.showSuccess(`Template "${template.nome}" inserido!`);
            }
            
        } catch (error) {
            console.error('Erro ao inserir template:', error);
            this.showError('Erro ao inserir template');
        }
    }

    processTemplateContent(htmlContent) {
        // Tornar campos editáveis
        let processedContent = htmlContent;
        
        // Destacar campos editáveis
        processedContent = processedContent.replace(/\[([^\]]+)\]/g, 
            '<span class="editable-field" style="background-color: #fff3cd; padding: 2px 4px; border: 1px solid #856404; border-radius: 3px; cursor: pointer;" title="Clique para editar">$1</span>'
        );
        
        processedContent = processedContent.replace(/___+/g, 
            '<span class="editable-field" style="background-color: #d1ecf1; padding: 2px 8px; border: 1px solid #0c5460; border-radius: 3px; cursor: pointer;" title="Clique para editar">CAMPO EDITÁVEL</span>'
        );
        
        return `<div class="template-container" style="border: 2px dashed #28a745; padding: 20px; margin: 15px 0; background-color: rgba(40, 167, 69, 0.05); border-radius: 8px;">${processedContent}</div>`;
    }

    createFallbackTemplate(template, area) {
        const areaColors = {
            'criminal': '#dc3545',
            'trabalhista': '#fd7e14',
            'empresarial': '#198754',
            'bancario': '#6f42c1',
            'consumidor': '#20c997',
            'agrario': '#ffc107',
            'securitario': '#e91e63'
        };
        
        const color = areaColors[area] || '#007bff';
        
        return `
            <div class="template-container" style="border: 2px dashed ${color}; padding: 20px; margin: 15px 0; background-color: rgba(0, 123, 255, 0.05); border-radius: 8px;">
                <h3 style="color: ${color}; margin-bottom: 15px;">${template.nome.toUpperCase()}</h3>
                <p style="margin-bottom: 10px;"><strong>Área:</strong> ${area}</p>
                <p style="margin-bottom: 15px;">${template.descricao || 'Template jurídico padrão'}</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <p>📝 <span class="editable-field" style="background-color: #fff3cd; padding: 2px 4px; border: 1px solid #856404; border-radius: 3px; cursor: pointer;">Conteúdo editável do template</span></p>
                    <p>📅 Data: <span class="editable-field" style="background-color: #d1ecf1; padding: 2px 8px; border: 1px solid #0c5460; border-radius: 3px; cursor: pointer;">__/__/____</span></p>
                    <p>👤 Responsável: <span class="editable-field" style="background-color: #fff3cd; padding: 2px 4px; border: 1px solid #856404; border-radius: 3px; cursor: pointer;">Nome do responsável</span></p>
                </div>
            </div>
        `;
    }

    insertIcon(iconPath) {
        if (!this.quill) {
            console.error('Editor não inicializado');
            return;
        }

        try {
            const iconHtml = `<img src="${iconPath}" style="width: 32px; height: 32px; margin: 0 4px; vertical-align: middle;" alt="Ícone jurídico">`;
            this.insertContentIntoEditor(iconHtml);
            this.showSuccess('Ícone inserido com sucesso!');
        } catch (error) {
            console.error('Erro ao inserir ícone:', error);
            this.showError('Erro ao inserir ícone');
        }
    }

    insertContentIntoEditor(content) {
        const selection = this.quill.getSelection();
        const index = selection ? selection.index : this.quill.getLength();
        this.quill.clipboard.dangerouslyPasteHTML(index, content);
        
        // Adicionar evento para campos editáveis
        setTimeout(() => {
            this.setupEditableFields();
        }, 100);
    }

    setupEditableFields() {
        document.querySelectorAll('.editable-field').forEach(field => {
            field.removeEventListener('click', this.handleFieldEdit);
            field.addEventListener('click', this.handleFieldEdit.bind(this));
        });
    }

    handleFieldEdit(e) {
        const field = e.target;
        const currentText = field.textContent;
        
        // Criar input inline
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentText;
        input.style.cssText = `
            background: white;
            border: 2px solid #007bff;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: inherit;
            font-family: inherit;
            min-width: 100px;
        `;
        
        // Substituir campo por input
        field.parentNode.insertBefore(input, field);
        field.style.display = 'none';
        input.focus();
        input.select();
        
        // Função para finalizar edição
        const finishEdit = () => {
            field.textContent = input.value || currentText;
            field.style.display = '';
            input.remove();
            this.showSuccess('Campo atualizado!');
        };
        
        // Eventos
        input.addEventListener('blur', finishEdit);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishEdit();
            }
            if (e.key === 'Escape') {
                field.style.display = '';
                input.remove();
            }
        });
    }

    switchTab(tabName) {
        // Atualizar abas
        document.querySelectorAll('.tools-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

        // Mostrar conteúdo
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`)?.classList.add('active');
    }

    updateStats() {
        if (!this.quill) return;
        
        const text = this.quill.getText();
        const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
        const charCount = text.length;
        const paragraphs = text.split('\n').filter(p => p.trim().length > 0).length;
        
        document.getElementById('statsWords').textContent = wordCount;
        document.getElementById('statsChars').textContent = charCount;
        document.getElementById('statsParagraphs').textContent = paragraphs;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Remover notificação anterior
        const existing = document.querySelector('.editor-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = 'editor-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            background-color: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando Legal Editor Rebuilt...');
    window.legalEditorRebuilt = new LegalEditorRebuilt();
});

// Backup: inicializar após um tempo se não foi carregado
setTimeout(() => {
    if (!window.legalEditorRebuilt) {
        console.log('🔄 Backup: Inicializando Legal Editor...');
        window.legalEditorRebuilt = new LegalEditorRebuilt();
    }
}, 2000);