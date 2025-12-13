/**
 * Integração Canvas-Database para Componentes
 * Conecta interface visual com lógica de persistência
 */

class CanvasDatabaseIntegration {
    constructor() {
        this.apiBase = '/componentes_editor';
        this.init();
    }

    init() {
        // Verificar se estamos na página certa
        if (!document.getElementById('editor-canvas')) {
            return;
        }

        this.setupSaveIntegration();
        this.setupComponentCreation();
        
        console.log('✅ Integração Canvas-Database inicializada');
    }

    /**
     * Integra salvamento do canvas com banco de dados
     */
    setupSaveIntegration() {
        // Override da função saveDesign global
        const originalSaveDesign = window.saveDesign;
        
        window.saveDesign = async () => {
            if (!window.canvasEditor) {
                console.error('Canvas Editor não encontrado');
                return;
            }

            const designData = window.canvasEditor.designData;
            
            try {
                // Salvar cada elemento como componente no banco
                for (const element of designData.elements) {
                    await this.saveElementAsComponent(element);
                }
                
                // Salvar design completo
                await this.saveDesignLayout(designData);
                
                this.showNotification('Design salvo e sincronizado com banco!', 'success');
            } catch (error) {
                console.error('Erro ao salvar design:', error);
                this.showNotification('Erro ao salvar design', 'error');
            }
        };
    }

    /**
     * Salva elemento do canvas como componente no banco
     */
    async saveElementAsComponent(element) {
        const componentData = {
            nome: this.extractComponentName(element),
            categoria: this.mapElementTypeToCategory(element.type),
            tipo: element.type,
            descricao: this.extractDescription(element),
            configuracao_visual: {
                width: element.width,
                height: element.height,
                position: { x: element.x, y: element.y },
                style: element.style || {}
            },
            codigo_html: this.generateHTMLFromElement(element),
            codigo_css: this.generateCSSFromElement(element),
            codigo_js: this.generateJSFromElement(element),
            ativo: true,
            canvas_generated: true
        };

        const response = await fetch(`${this.apiBase}/api/componentes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(componentData)
        });

        if (!response.ok) {
            throw new Error(`Erro ao salvar componente: ${response.statusText}`);
        }

        const result = await response.json();
        return result;
    }

    /**
     * Carrega componentes do banco para o canvas
     */
    async loadComponentsToCanvas() {
        try {
            const response = await fetch(`${this.apiBase}/api/componentes`);
            const components = await response.json();
            
            // Filtrar apenas componentes criados no canvas
            const canvasComponents = components.filter(c => c.canvas_generated);
            
            // Adicionar cada componente ao canvas
            for (const component of canvasComponents) {
                this.addComponentToCanvas(component);
            }
            
            this.showNotification(`${canvasComponents.length} componentes carregados!`, 'info');
        } catch (error) {
            console.error('Erro ao carregar componentes:', error);
            this.showNotification('Erro ao carregar componentes', 'error');
        }
    }

    /**
     * Adiciona componente do banco ao canvas
     */
    addComponentToCanvas(component) {
        if (!window.canvasEditor) return;
        
        const template = {
            type: component.tipo,
            name: component.nome,
            content: component.codigo_html || component.descricao,
            className: this.mapCategoryToClassName(component.categoria),
            icon: this.mapCategoryToIcon(component.categoria),
            width: component.configuracao_visual?.width || 300,
            height: component.configuracao_visual?.height || 80
        };
        
        const position = component.configuracao_visual?.position || { x: 50, y: 50 };
        window.canvasEditor.createElement(template, position.x, position.y);
    }

    /**
     * Configura criação de componentes via formulário
     */
    setupComponentCreation() {
        // Interceptar submissão do formulário de novo componente
        const form = document.querySelector('form[action*="criar_componente"]');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleFormSubmission(form);
            });
        }
    }

    /**
     * Processa submissão do formulário
     */
    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const componentData = Object.fromEntries(formData.entries());
        
        try {
            // Criar componente no banco
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Adicionar ao canvas se estiver aberto
                if (window.canvasEditor) {
                    const template = this.formDataToTemplate(componentData);
                    window.canvasEditor.createElement(template, 100, 100);
                }
                
                this.showNotification('Componente criado com sucesso!', 'success');
            }
        } catch (error) {
            console.error('Erro ao criar componente:', error);
            this.showNotification('Erro ao criar componente', 'error');
        }
    }

    /**
     * Salva layout do design completo
     */
    async saveDesignLayout(designData) {
        const layoutData = {
            name: `Design_${new Date().toISOString().split('T')[0]}`,
            elements: designData.elements,
            metadata: designData.metadata,
            created_at: new Date()
        };

        const response = await fetch(`${this.apiBase}/api/layouts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(layoutData)
        });

        if (!response.ok) {
            throw new Error(`Erro ao salvar layout: ${response.statusText}`);
        }

        return await response.json();
    }

    // Métodos auxiliares
    extractComponentName(element) {
        return element.content?.match(/<h[1-6][^>]*>([^<]+)</)?.[1] || 
               element.name || 
               `Componente_${Date.now()}`;
    }

    mapElementTypeToCategory(type) {
        const typeMap = {
            'urgent-box': 'alertas',
            'warning-box': 'alertas', 
            'info-box': 'informacao',
            'legal-table': 'tabelas',
            'legal-timeline': 'timelines'
        };
        return typeMap[type] || 'geral';
    }

    mapCategoryToClassName(category) {
        const classMap = {
            'alertas': 'alert alert-warning',
            'informacao': 'alert alert-info',
            'tabelas': 'table-container',
            'timelines': 'timeline-container'
        };
        return classMap[category] || 'component-container';
    }

    mapCategoryToIcon(category) {
        const iconMap = {
            'alertas': 'fas fa-exclamation-triangle',
            'informacao': 'fas fa-info-circle',
            'tabelas': 'fas fa-table',
            'timelines': 'fas fa-stream'
        };
        return iconMap[category] || 'fas fa-cube';
    }

    extractDescription(element) {
        // Extrair descrição do conteúdo HTML
        const textContent = element.content?.replace(/<[^>]*>/g, '') || '';
        return textContent.substring(0, 200) + (textContent.length > 200 ? '...' : '');
    }

    generateHTMLFromElement(element) {
        // Gerar HTML baseado no elemento do canvas
        const elementDOM = document.getElementById(element.id);
        return elementDOM ? elementDOM.outerHTML : element.content;
    }

    generateCSSFromElement(element) {
        // Gerar CSS baseado nas propriedades do elemento
        return `
.${element.type} {
    width: ${element.width}px;
    height: ${element.height}px;
    position: relative;
}
        `.trim();
    }

    generateJSFromElement(element) {
        // Gerar JavaScript básico para interatividade
        return `
// Funcionalidade para ${element.type}
document.addEventListener('DOMContentLoaded', function() {
    const element = document.querySelector('.${element.type}');
    if (element) {
        element.addEventListener('click', function() {
            console.log('${element.type} clicked');
        });
    }
});
        `.trim();
    }

    formDataToTemplate(formData) {
        return {
            type: formData.tipo || 'custom',
            name: formData.nome,
            content: formData.descricao,
            className: this.mapCategoryToClassName(formData.categoria),
            icon: this.mapCategoryToIcon(formData.categoria),
            width: 300,
            height: 100
        };
    }

    showNotification(message, type = 'info') {
        // Reutilizar sistema de notificação do canvas
        if (window.canvasEditor) {
            window.canvasEditor.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Função global para integração com fluxos
window.exportToFluxo = function() {
    if (!window.canvasEditor) {
        alert('Canvas Editor não encontrado');
        return;
    }

    const designData = window.canvasEditor.designData;
    const fluxoData = {
        nome: `Fluxo_${new Date().toISOString().split('T')[0]}`,
        descricao: 'Fluxo gerado a partir do Canvas Editor',
        componentes: designData.elements.map(element => ({
            tipo: element.type,
            nome: element.name,
            posicao: { x: element.x, y: element.y },
            configuracao: element
        }))
    };

    // Salvar no localStorage para uso no editor de fluxos
    localStorage.setItem('fluxo_from_canvas', JSON.stringify(fluxoData));
    
    // Redirecionar para editor de fluxos
    window.location.href = '/fluxos/editor';
};

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.canvasIntegration = new CanvasDatabaseIntegration();
});