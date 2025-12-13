/**
 * Canvas Editor Pro - Sistema Avançado de Edição Visual
 * Integração completa com paleta de componentes e funcionalidades profissionais
 */

class CanvasEditorPro {
    constructor() {
        this.canvas = null;
        this.selectedElement = null;
        this.draggedElement = null;
        this.designData = {
            elements: [],
            metadata: {
                created: new Date(),
                modified: new Date(),
                version: '1.0'
            }
        };
        this.history = [];
        this.historyIndex = -1;
        this.gridSize = 20;
        this.snapToGrid = true;
        this.zoom = 1;
        
        this.init();
    }

    init() {
        this.canvas = document.getElementById('editor-canvas');
        if (!this.canvas) {
            console.error('Canvas não encontrado!');
            return;
        }

        this.setupCanvas();
        this.setupPalette();
        this.setupKeyboardShortcuts();
        this.setupContextMenu();
        this.addHistory();
        
        console.log('✅ Canvas Editor Pro inicializado');
    }

    setupCanvas() {
        // Remover placeholder
        const placeholder = this.canvas.querySelector('.canvas-placeholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }

        // Configurar eventos do canvas
        this.canvas.addEventListener('dragover', this.handleDragOver.bind(this));
        this.canvas.addEventListener('drop', this.handleDrop.bind(this));
        this.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
        
        // Adicionar grade visual
        this.addGrid();
    }

    setupPalette() {
        const paletteItems = document.querySelectorAll('.component-item');
        
        paletteItems.forEach(item => {
            item.addEventListener('dragstart', this.handleDragStart.bind(this));
            item.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
    }

    addGrid() {
        const grid = document.createElement('div');
        grid.className = 'canvas-grid';
        grid.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
            background-size: ${this.gridSize}px ${this.gridSize}px;
            pointer-events: none;
            opacity: 0.3;
        `;
        this.canvas.appendChild(grid);
    }

    handleDragStart(e) {
        const elementType = e.target.closest('.component-item').dataset.elementType;
        const elementData = this.getComponentTemplate(elementType);
        
        e.dataTransfer.setData('application/json', JSON.stringify(elementData));
        e.dataTransfer.effectAllowed = 'copy';
        
        // Visual feedback
        e.target.style.opacity = '0.5';
    }

    handleDragEnd(e) {
        e.target.style.opacity = '1';
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(e) {
        e.preventDefault();
        
        try {
            const elementData = JSON.parse(e.dataTransfer.getData('application/json'));
            const rect = this.canvas.getBoundingClientRect();
            
            let x = e.clientX - rect.left;
            let y = e.clientY - rect.top;
            
            // Snap to grid
            if (this.snapToGrid) {
                x = Math.round(x / this.gridSize) * this.gridSize;
                y = Math.round(y / this.gridSize) * this.gridSize;
            }
            
            this.createElement(elementData, x, y);
        } catch (error) {
            console.error('Erro ao processar drop:', error);
        }
    }

    getComponentTemplate(type) {
        const templates = {
            'urgent-box': {
                type: 'urgent-box',
                name: 'Caixa Urgente',
                content: 'URGENTE: Conteúdo importante',
                className: 'alert alert-danger',
                icon: 'fas fa-exclamation-triangle',
                width: 300,
                height: 80
            },
            'warning-box': {
                type: 'warning-box',
                name: 'Caixa de Aviso',
                content: 'ATENÇÃO: Informação importante',
                className: 'alert alert-warning',
                icon: 'fas fa-exclamation-circle',
                width: 300,
                height: 80
            },
            'info-box': {
                type: 'info-box',
                name: 'Caixa de Informação',
                content: 'INFORMAÇÃO: Detalhes relevantes',
                className: 'alert alert-info',
                icon: 'fas fa-info-circle',
                width: 300,
                height: 80
            },
            'legal-table': {
                type: 'legal-table',
                name: 'Tabela Jurídica',
                content: this.getTableTemplate(),
                className: 'table-container',
                icon: 'fas fa-table',
                width: 400,
                height: 200
            },
            'legal-timeline': {
                type: 'legal-timeline',
                name: 'Linha do Tempo',
                content: this.getTimelineTemplate(),
                className: 'timeline-container',
                icon: 'fas fa-stream',
                width: 350,
                height: 250
            }
        };
        
        return templates[type] || templates['info-box'];
    }

    getTableTemplate() {
        return `
            <table class="table table-striped table-sm">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Descrição</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Item 1</td>
                        <td>Descrição do item</td>
                        <td><span class="badge bg-success">Ativo</span></td>
                    </tr>
                    <tr>
                        <td>Item 2</td>
                        <td>Descrição do item</td>
                        <td><span class="badge bg-warning">Pendente</span></td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    getTimelineTemplate() {
        return `
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-marker bg-primary"></div>
                    <div class="timeline-content">
                        <h6>Evento 1</h6>
                        <p>Descrição do primeiro evento</p>
                        <small class="text-muted">Data: 01/01/2025</small>
                    </div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-marker bg-success"></div>
                    <div class="timeline-content">
                        <h6>Evento 2</h6>
                        <p>Descrição do segundo evento</p>
                        <small class="text-muted">Data: 15/01/2025</small>
                    </div>
                </div>
            </div>
        `;
    }

    createElement(template, x, y) {
        const elementId = `element-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        const element = document.createElement('div');
        element.id = elementId;
        element.className = `canvas-element ${template.className}`;
        element.style.cssText = `
            position: absolute;
            left: ${x}px;
            top: ${y}px;
            width: ${template.width}px;
            min-height: ${template.height}px;
            border: 2px solid transparent;
            cursor: move;
            z-index: 10;
        `;
        
        element.innerHTML = `
            <div class="element-header">
                <span class="element-title">
                    <i class="${template.icon} me-2"></i>${template.name}
                </span>
                <div class="element-controls">
                    <button class="btn btn-sm btn-outline-primary edit-btn" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-btn" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="element-content" contenteditable="true">
                ${template.content}
            </div>
        `;
        
        // Adicionar eventos
        this.addElementEvents(element);
        
        // Adicionar ao canvas
        this.canvas.appendChild(element);
        
        // Salvar no histórico
        this.designData.elements.push({
            id: elementId,
            type: template.type,
            x: x,
            y: y,
            width: template.width,
            height: template.height,
            content: template.content
        });
        
        this.addHistory();
        this.selectElement(element);
        
        return element;
    }

    addElementEvents(element) {
        // Drag & Drop
        let isDragging = false;
        let startX, startY, startLeft, startTop;
        
        element.addEventListener('mousedown', (e) => {
            if (e.target.closest('.element-controls') || e.target.contentEditable === 'true') {
                return;
            }
            
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = parseInt(element.style.left);
            startTop = parseInt(element.style.top);
            
            document.addEventListener('mousemove', handleDrag);
            document.addEventListener('mouseup', handleDragEnd);
            
            e.preventDefault();
        });
        
        const handleDrag = (e) => {
            if (!isDragging) return;
            
            let newX = startLeft + (e.clientX - startX);
            let newY = startTop + (e.clientY - startY);
            
            // Snap to grid
            if (this.snapToGrid) {
                newX = Math.round(newX / this.gridSize) * this.gridSize;
                newY = Math.round(newY / this.gridSize) * this.gridSize;
            }
            
            element.style.left = newX + 'px';
            element.style.top = newY + 'px';
        };
        
        const handleDragEnd = () => {
            isDragging = false;
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('mouseup', handleDragEnd);
            this.addHistory();
        };
        
        // Seleção
        element.addEventListener('click', (e) => {
            if (!e.target.closest('.element-controls')) {
                this.selectElement(element);
            }
        });
        
        // Controles
        const editBtn = element.querySelector('.edit-btn');
        const deleteBtn = element.querySelector('.delete-btn');
        
        editBtn.addEventListener('click', () => this.editElement(element));
        deleteBtn.addEventListener('click', () => this.deleteElement(element));
    }

    selectElement(element) {
        // Remover seleção anterior
        if (this.selectedElement) {
            this.selectedElement.style.border = '2px solid transparent';
        }
        
        // Selecionar novo elemento
        this.selectedElement = element;
        element.style.border = '2px solid #007bff';
        
        // Mostrar propriedades
        this.showElementProperties(element);
    }

    showElementProperties(element) {
        // Implementar painel de propriedades
        console.log('Propriedades do elemento:', element.id);
    }

    editElement(element) {
        const content = element.querySelector('.element-content');
        content.focus();
    }

    deleteElement(element) {
        if (confirm('Deseja excluir este elemento?')) {
            // Remover do array de dados
            this.designData.elements = this.designData.elements.filter(
                el => el.id !== element.id
            );
            
            // Remover do DOM
            element.remove();
            
            // Limpar seleção
            if (this.selectedElement === element) {
                this.selectedElement = null;
            }
            
            this.addHistory();
        }
    }

    handleCanvasClick(e) {
        if (e.target === this.canvas) {
            this.clearSelection();
        }
    }

    clearSelection() {
        if (this.selectedElement) {
            this.selectedElement.style.border = '2px solid transparent';
            this.selectedElement = null;
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'z':
                        e.preventDefault();
                        this.undo();
                        break;
                    case 'y':
                        e.preventDefault();
                        this.redo();
                        break;
                    case 's':
                        e.preventDefault();
                        this.saveDesign();
                        break;
                }
            }
            
            if (e.key === 'Delete' && this.selectedElement) {
                this.deleteElement(this.selectedElement);
            }
        });
    }

    setupContextMenu() {
        this.canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            // Implementar menu de contexto
        });
    }

    addHistory() {
        const state = JSON.parse(JSON.stringify(this.designData));
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex++;
        
        // Limitar histórico a 50 estados
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.restoreState(this.history[this.historyIndex]);
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.restoreState(this.history[this.historyIndex]);
        }
    }

    restoreState(state) {
        this.designData = JSON.parse(JSON.stringify(state));
        this.renderCanvas();
    }

    renderCanvas() {
        // Limpar canvas (manter grid)
        const elements = this.canvas.querySelectorAll('.canvas-element');
        elements.forEach(el => el.remove());
        
        // Renderizar elementos
        this.designData.elements.forEach(elementData => {
            const template = this.getComponentTemplate(elementData.type);
            template.content = elementData.content;
            this.createElement(template, elementData.x, elementData.y);
        });
    }

    saveDesign() {
        try {
            this.designData.metadata.modified = new Date();
            
            // Atualizar dados dos elementos
            const elements = this.canvas.querySelectorAll('.canvas-element');
            this.designData.elements = Array.from(elements).map(el => ({
                id: el.id,
                type: el.dataset.elementType || 'unknown',
                x: parseInt(el.style.left),
                y: parseInt(el.style.top),
                width: parseInt(el.style.width),
                height: el.offsetHeight,
                content: el.querySelector('.element-content').innerHTML
            }));
            
            // Salvar no localStorage
            localStorage.setItem('canvas-design', JSON.stringify(this.designData));
            
            // Notificar sucesso
            this.showNotification('Design salvo com sucesso!', 'success');
            
            console.log('✅ Design salvo:', this.designData);
        } catch (error) {
            console.error('Erro ao salvar design:', error);
            this.showNotification('Erro ao salvar design', 'error');
        }
    }

    loadDesign() {
        try {
            const saved = localStorage.getItem('canvas-design');
            if (saved) {
                this.designData = JSON.parse(saved);
                this.renderCanvas();
                this.showNotification('Design carregado com sucesso!', 'success');
            }
        } catch (error) {
            console.error('Erro ao carregar design:', error);
            this.showNotification('Erro ao carregar design', 'error');
        }
    }

    clearCanvas() {
        if (confirm('Deseja limpar todo o canvas? Esta ação não pode ser desfeita.')) {
            // Limpar elementos
            const elements = this.canvas.querySelectorAll('.canvas-element');
            elements.forEach(el => el.remove());
            
            // Resetar dados
            this.designData.elements = [];
            this.selectedElement = null;
            
            // Mostrar placeholder
            const placeholder = this.canvas.querySelector('.canvas-placeholder');
            if (placeholder) {
                placeholder.style.display = 'block';
            }
            
            this.addHistory();
            this.showNotification('Canvas limpo', 'info');
        }
    }

    exportDesign() {
        try {
            // Preparar dados para export
            const exportData = {
                ...this.designData,
                exported: new Date(),
                elements: this.designData.elements.map(el => ({
                    ...el,
                    // Capturar HTML atual
                    html: document.getElementById(el.id)?.outerHTML || ''
                }))
            };
            
            // Criar blob e download
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `canvas-design-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            
            this.showNotification('Design exportado com sucesso!', 'success');
        } catch (error) {
            console.error('Erro ao exportar design:', error);
            this.showNotification('Erro ao exportar design', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Funções globais para os botões
function saveDesign() {
    if (window.canvasEditor) {
        window.canvasEditor.saveDesign();
    }
}

function clearCanvas() {
    if (window.canvasEditor) {
        window.canvasEditor.clearCanvas();
    }
}

function exportDesign() {
    if (window.canvasEditor) {
        window.canvasEditor.exportDesign();
    }
}

function loadDesign() {
    if (window.canvasEditor) {
        window.canvasEditor.loadDesign();
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.canvasEditor = new CanvasEditorPro();
});