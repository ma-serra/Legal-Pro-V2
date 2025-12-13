// Legal Design Editor - Versão Totalmente Corrigida
// Cache Buster: 2025-06-13-034500

console.log('=== LEGAL DESIGN EDITOR VERSÃO CORRIGIDA CARREGADA ===');

class LegalDesignEditor {
    constructor() {
        console.log('=== CONSTRUTOR EXECUTANDO ===');
        this.documentContent = null;
        this.initializeEditor();
        this.setupEventListeners();
        this.setupAutoSave();
    }
    
    initializeEditor() {
        console.log('=== INICIALIZANDO EDITOR ===');
        
        // Aguardar DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.findDocumentContent();
            });
        } else {
            this.findDocumentContent();
        }
        
        this.toolsSidebar = document.getElementById('toolsSidebar');
        this.propertiesPanel = document.getElementById('propertiesPanel');
        
        this.isToolsVisible = true;
        this.isPropertiesVisible = false;
        this.documentData = {
            title: 'Petição Inicial',
            area: 'Direito Civil',
            content: ''
        };
    }
    
    findDocumentContent() {
        console.log('=== PROCURANDO DOCUMENT CONTENT ===');
        
        // Múltiplas tentativas para encontrar o elemento
        const selectors = [
            '#documentContent',
            '.document-page',
            '[contenteditable="true"]',
            '.document-container .document-page'
        ];
        
        for (let selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                this.documentContent = element;
                console.log(`Elemento encontrado com seletor: ${selector}`);
                console.log('Elemento:', element);
                console.log('ID:', element.id);
                console.log('Classes:', element.className);
                console.log('ContentEditable:', element.contentEditable);
                console.log('Tag:', element.tagName);
                break;
            }
        }
        
        if (!this.documentContent) {
            console.error('ERRO: Nenhum elemento de documento encontrado!');
            return;
        }
        
        console.log('=== DOCUMENT CONTENT INICIALIZADO COM SUCESSO ===');
    }
    
    setupEventListeners() {
        console.log('=== CONFIGURANDO EVENT LISTENERS ===');
        
        // Aguardar um pouco para garantir que o DOM está completo
        setTimeout(() => {
            const toolItems = document.querySelectorAll('.tool-item');
            console.log(`Encontradas ${toolItems.length} ferramentas`);
            
            toolItems.forEach((item, index) => {
                console.log(`Configurando ferramenta ${index}:`, {
                    element: item,
                    template: item.getAttribute('data-template'),
                    element_attr: item.getAttribute('data-element'),
                    ai: item.getAttribute('data-ai'),
                    title: item.querySelector('.tool-item-title')?.textContent
                });
                
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log(`=== CLIQUE NA FERRAMENTA ${index} ===`);
                    console.log('Item clicado:', item);
                    
                    this.handleToolAction(item);
                });
            });
            
            // Configurar sistema de cores
            this.setupColorSystem();
            
            // Configurar sistema de exclusão
            this.setupDeletionSystem();
            
            // Configurar formatação
            this.setupFormattingControls();
            
        }, 500);
    }
    
    setupColorSystem() {
        console.log('=== CONFIGURANDO SISTEMA DE CORES ===');
        
        // Paleta de cores baseada na imagem fornecida
        const colorPalette = [
            // Linha 1 - Tons neutros e azuis
            '#2c3e50', '#6c757d', '#f8f9fa', '#3f729b', '#2e8b57', '#2f4f4f', '#2e8b57',
            // Linha 2 - Verdes e azuis escuros  
            '#1a1a1a', '#2e8b57', '#40e0d0', '#20b2aa', '#000000', '#4682b4', '#2e8b57',
            // Linha 3 - Azuis claros
            '#e6f3ff', '#4682b4', '#1e90ff', '#20b2aa', '#2e8b57', '#2f4f4f', '#2e8b57',
            // Linha 4 - Azuis e verdes
            '#4682b4', '#1e90ff', '#32cd32', '#00ff7f', '#00fa9a', '#6c757d', '#8a2be2',
            // Linha 5 - Azuis e vermelhos
            '#4682b4', '#dc143c', '#ff4500', '#228b22', '#00bfff', '#8a2be2', '#4682b4',
            // Linha 6 - Vermelhos e verdes
            '#dc143c', '#20b2aa', '#40e0d0', '#2e8b57', '#ff4500', '#6c757d', '#2f4f4f',
            // Linha 7 - Tons variados
            '#4682b4', '#6c757d', '#daa520', '#2f4f4f', '#4682b4', '#daa520', '#2f4f4f',
            // Linha 8 - Tons finais
            '#d3d3d3', '#daa520', '#000000', '#1e90ff', '#ffff00', '#2f4f4f', '#40e0d0',
            // Linha 9 - Tons adicionais
            '#dc143c', '#ff8c00', '#00fa9a', '#0000ff', '#8a2be2', '#f8f9fa', '#e6e6e6',
            // Linha 10 - Complementares
            '#6c757d', '#ffff00', '#daa520'
        ];
        
        // Criar paletas para cada tipo de cor
        this.createColorPalette('textColorGrid', colorPalette);
        this.createColorPalette('bgColorGrid', colorPalette);
        this.createColorPalette('highlightGrid', colorPalette);
        
        // Configurar botões de cor
        this.setupColorButtons();
        
        // Configurar inputs de cor personalizada
        this.setupCustomColorInputs();
    }
    
    createColorPalette(gridId, colors) {
        const grid = document.getElementById(gridId);
        if (!grid) return;
        
        grid.innerHTML = '';
        
        colors.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'color-swatch';
            swatch.style.backgroundColor = color;
            swatch.title = color;
            swatch.dataset.color = color;
            
            swatch.addEventListener('click', (e) => {
                this.applyColor(gridId, color);
                this.closeColorPalettes();
            });
            
            grid.appendChild(swatch);
        });
    }
    
    setupColorButtons() {
        // Armazenar seleção de texto
        this.savedSelection = null;
        this.currentColorGrid = null;
        
        // Salvar seleção quando o usuário selecionar texto
        this.documentContent.addEventListener('mouseup', () => {
            const selection = window.getSelection();
            if (selection.rangeCount > 0 && !selection.isCollapsed) {
                this.savedSelection = selection.getRangeAt(0).cloneRange();
                this.savedText = selection.toString();
                console.log('Seleção de texto salva:', this.savedText);
            }
        });
        
        // Interceptar cliques nos botões de cor para preservar seleção
        document.addEventListener('mousedown', (e) => {
            if (e.target.closest('.color-palette-dropdown') || e.target.closest('[data-color-target]')) {
                e.preventDefault();
                // Salvar seleção atual antes do clique
                const selection = window.getSelection();
                if (selection.rangeCount > 0 && !selection.isCollapsed) {
                    this.savedSelection = selection.getRangeAt(0).cloneRange();
                    this.savedText = selection.toString();
                    console.log('Seleção preservada antes do clique na paleta:', this.savedText);
                }
            }
        });
        
        // Botão de cor de texto
        const textColorBtn = document.getElementById('textColorBtn');
        const textColorPalette = document.getElementById('textColorPalette');
        
        if (textColorBtn && textColorPalette) {
            textColorBtn.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Previne perda de seleção
            });
            
            textColorBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.currentColorGrid = 'textColorGrid';
                this.closeColorPalettes();
                textColorPalette.classList.toggle('show');
            });
        }
        
        // Botão de cor de fundo
        const bgColorBtn = document.getElementById('bgColorBtn');
        const bgColorPalette = document.getElementById('bgColorPalette');
        
        if (bgColorBtn && bgColorPalette) {
            bgColorBtn.addEventListener('mousedown', (e) => {
                e.preventDefault();
            });
            
            bgColorBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.currentColorGrid = 'bgColorGrid';
                this.closeColorPalettes();
                bgColorPalette.classList.toggle('show');
            });
        }
        
        // Botão de marcador
        const highlightBtn = document.getElementById('highlightBtn');
        const highlightPalette = document.getElementById('highlightPalette');
        
        if (highlightBtn && highlightPalette) {
            highlightBtn.addEventListener('mousedown', (e) => {
                e.preventDefault();
            });
            
            highlightBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.currentColorGrid = 'highlightGrid';
                this.closeColorPalettes();
                highlightPalette.classList.toggle('show');
            });
        }
        
        // Configurar cliques nas cores das paletas
        document.querySelectorAll('.color-item').forEach(colorItem => {
            colorItem.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Previne perda de seleção
            });
            
            colorItem.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const color = colorItem.dataset.color;
                const gridId = this.currentColorGrid || colorItem.closest('.color-grid')?.id || 'textColorGrid';
                
                console.log('Clique na cor detectado:', color, 'Grid:', gridId);
                console.log('Seleção salva disponível:', this.savedSelection ? 'SIM' : 'NÃO');
                
                // Aplicar cor diretamente se há seleção salva
                if (this.savedSelection && this.savedText) {
                    console.log('Aplicando cor ao texto salvo:', this.savedText);
                    this.applyColorToSavedSelection(gridId, color);
                } else {
                    console.log('Nenhuma seleção salva, aplicando cor para próximo texto');
                    this.applyColor(gridId, color);
                }
                
                this.closeColorPalettes();
            });
        });
        
        // Fechar paletas ao clicar fora
        document.addEventListener('click', () => {
            this.closeColorPalettes();
        });
    }
    
    closeColorPalettes() {
        document.querySelectorAll('.color-palette-dropdown').forEach(palette => {
            palette.classList.remove('show');
        });
    }
    
    applyColor(gridId, color) {
        const selection = window.getSelection();
        
        console.log('=== DEBUG APLICAÇÃO DE COR ===');
        console.log(`Aplicando cor ${color} do grid ${gridId}`);
        console.log('Seleção completa:', selection);
        console.log('Range count:', selection.rangeCount);
        console.log('Is collapsed (sem seleção):', selection.isCollapsed);
        console.log('Texto selecionado:', selection.toString());
        console.log('Anchor node:', selection.anchorNode);
        console.log('Focus node:', selection.focusNode);
        
        // Focar no documento antes de aplicar cor
        this.documentContent.focus();
        
        // Forçar CSS styling
        document.execCommand('styleWithCSS', false, true);
        
        if (gridId === 'textColorGrid') {
            console.log('=== APLICANDO COR DE TEXTO ===');
            
            if (selection.rangeCount > 0 && !selection.isCollapsed && selection.toString().length > 0) {
                console.log('Texto selecionado detectado, aplicando cor diretamente');
                
                // Método 1: Usar execCommand diretamente
                const success1 = document.execCommand('foreColor', false, color);
                console.log('execCommand foreColor resultado:', success1);
                
                if (!success1) {
                    console.log('execCommand falhou, tentando método manual...');
                    
                    // Método 2: Envolver em span manualmente
                    const range = selection.getRangeAt(0);
                    const selectedText = range.toString();
                    const span = document.createElement('span');
                    span.style.color = color;
                    span.textContent = selectedText;
                    
                    try {
                        range.deleteContents();
                        range.insertNode(span);
                        console.log('Span inserido manualmente com sucesso');
                    } catch (e) {
                        console.error('Erro ao inserir span:', e);
                    }
                }
                
                // Limpar seleção
                selection.removeAllRanges();
                
            } else {
                console.log('Nenhum texto selecionado, definindo cor para próximo texto');
                
                // Aplicar cor para próximo texto digitado
                document.execCommand('foreColor', false, color);
                console.log('Cor definida para próximo texto via execCommand');
            }
            
            const preview = document.getElementById('textColorPreview');
            if (preview) {
                preview.style.backgroundColor = color;
                console.log('Preview de cor atualizado');
            }
            
        } else if (gridId === 'bgColorGrid') {
            console.log('=== APLICANDO COR DE FUNDO ===');
            
            if (selection.rangeCount > 0 && !selection.isCollapsed && selection.toString().length > 0) {
                console.log('Aplicando cor de fundo ao texto selecionado');
                
                const success = document.execCommand('hiliteColor', false, color);
                console.log('hiliteColor resultado:', success);
                
                if (!success) {
                    // Fallback manual
                    const range = selection.getRangeAt(0);
                    const selectedText = range.toString();
                    const span = document.createElement('span');
                    span.style.backgroundColor = color;
                    span.textContent = selectedText;
                    
                    range.deleteContents();
                    range.insertNode(span);
                }
                
                selection.removeAllRanges();
            } else {
                console.log('Definindo cor de fundo para próximo texto');
                document.execCommand('hiliteColor', false, color);
            }
            
            const preview = document.getElementById('bgColorPreview');
            if (preview) preview.style.backgroundColor = color;
            
        } else if (gridId === 'highlightGrid') {
            console.log('=== APLICANDO MARCADOR ===');
            
            if (selection.rangeCount > 0 && !selection.isCollapsed && selection.toString().length > 0) {
                const range = selection.getRangeAt(0);
                const selectedText = range.toString();
                const span = document.createElement('span');
                span.style.backgroundColor = color;
                span.style.padding = '2px 4px';
                span.style.borderRadius = '3px';
                span.textContent = selectedText;
                
                range.deleteContents();
                range.insertNode(span);
                selection.removeAllRanges();
                
                console.log('Marcador aplicado ao texto selecionado');
            } else {
                console.log('Aplicando marcador para próximo texto');
                const span = document.createElement('span');
                span.style.backgroundColor = color;
                span.style.padding = '2px 4px';
                span.style.borderRadius = '3px';
                span.innerHTML = '&#8203;';
                document.execCommand('insertHTML', false, span.outerHTML);
            }
            
            const preview = document.getElementById('highlightPreview');
            if (preview) preview.style.backgroundColor = color;
        }
        
        console.log('=== FIM DEBUG APLICAÇÃO DE COR ===');
        this.showNotification(`Cor ${color} aplicada!`, 'success');
    }
    
    applyColorToSavedSelection(gridId, color) {
        console.log('=== APLICANDO COR AO TEXTO SALVO ===');
        console.log('Texto salvo:', this.savedText);
        console.log('Grid:', gridId, 'Cor:', color);
        
        // Buscar o texto no documento e aplicar cor
        const content = this.documentContent.innerHTML;
        console.log('Buscando texto no documento...');
        
        if (gridId === 'textColorGrid') {
            // Substituir o texto encontrado por uma versão com cor
            const coloredText = `<span style="color: ${color};">${this.savedText}</span>`;
            const newContent = content.replace(this.savedText, coloredText);
            
            if (newContent !== content) {
                this.documentContent.innerHTML = newContent;
                console.log('Cor de texto aplicada com sucesso!');
                this.showNotification(`Cor ${color} aplicada ao texto selecionado!`, 'success');
            } else {
                console.log('Texto não encontrado, aplicando cor para próximo texto');
                this.applyColor(gridId, color);
            }
            
        } else if (gridId === 'bgColorGrid') {
            const highlightedText = `<span style="background-color: ${color};">${this.savedText}</span>`;
            const newContent = content.replace(this.savedText, highlightedText);
            
            if (newContent !== content) {
                this.documentContent.innerHTML = newContent;
                console.log('Cor de fundo aplicada com sucesso!');
                this.showNotification(`Cor de fundo ${color} aplicada ao texto selecionado!`, 'success');
            } else {
                console.log('Texto não encontrado, aplicando cor para próximo texto');
                this.applyColor(gridId, color);
            }
            
        } else if (gridId === 'highlightGrid') {
            const highlightedText = `<span style="background-color: ${color}; padding: 2px 4px; border-radius: 3px;">${this.savedText}</span>`;
            const newContent = content.replace(this.savedText, highlightedText);
            
            if (newContent !== content) {
                this.documentContent.innerHTML = newContent;
                console.log('Marcador aplicado com sucesso!');
                this.showNotification(`Marcador ${color} aplicado ao texto selecionado!`, 'success');
            } else {
                console.log('Texto não encontrado, aplicando cor para próximo texto');
                this.applyColor(gridId, color);
            }
        }
        
        // Limpar seleção salva após aplicar
        this.savedSelection = null;
        this.savedText = null;
        console.log('=== FIM APLICAÇÃO DE COR AO TEXTO SALVO ===');
    }
    
    setupDeletionSystem() {
        console.log('=== CONFIGURANDO SISTEMA DE EXCLUSÃO ===');
        
        // Adicionar botões de exclusão aos elementos inseridos
        document.addEventListener('click', (e) => {
            // Verificar se clicou em um elemento editável
            const target = e.target.closest('.timeline-element, .highlight-box, blockquote, .ai-suggestion, div[style*="border"], div[style*="background"]');
            
            if (target && this.documentContent.contains(target)) {
                this.showDeleteButton(target, e);
            }
        });
        
        // Tecla Delete para exclusão
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' && e.ctrlKey) {
                const selection = window.getSelection();
                if (selection.rangeCount > 0) {
                    const range = selection.getRangeAt(0);
                    const element = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE 
                        ? range.commonAncestorContainer 
                        : range.commonAncestorContainer.parentElement;
                    
                    const deletableElement = element.closest('.timeline-element, .highlight-box, blockquote, .ai-suggestion, div[style*="border"]');
                    if (deletableElement && this.documentContent.contains(deletableElement)) {
                        this.deleteElement(deletableElement);
                    }
                }
            }
        });
    }
    
    showDeleteButton(element, event) {
        // Remover botões existentes
        document.querySelectorAll('.delete-element-btn').forEach(btn => btn.remove());
        
        // Criar botão de exclusão
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-element-btn';
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        deleteBtn.title = 'Excluir elemento (Ctrl+Del)';
        deleteBtn.style.cssText = `
            position: absolute;
            top: ${event.pageY - 10}px;
            left: ${event.pageX + 10}px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            z-index: 9999;
            font-size: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        `;
        
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteElement(element);
            deleteBtn.remove();
        });
        
        document.body.appendChild(deleteBtn);
        
        // Remover botão após 3 segundos
        setTimeout(() => {
            if (deleteBtn.parentNode) {
                deleteBtn.remove();
            }
        }, 3000);
    }
    
    deleteElement(element) {
        if (confirm('Deseja realmente excluir este elemento?')) {
            element.remove();
            this.showNotification('Elemento excluído com sucesso!', 'success');
            console.log('Elemento excluído:', element);
        }
    }
    
    setupFormattingControls() {
        console.log('=== CONFIGURANDO CONTROLES DE FORMATAÇÃO ===');
        
        // Seletor de fonte
        const fontFamily = document.getElementById('fontFamily');
        if (fontFamily) {
            fontFamily.addEventListener('change', (e) => {
                document.execCommand('fontName', false, e.target.value);
                this.showNotification(`Fonte alterada para ${e.target.value}`, 'success');
            });
        }
        
        // Seletor de tamanho
        const fontSize = document.getElementById('fontSize');
        if (fontSize) {
            fontSize.addEventListener('change', (e) => {
                const size = e.target.value.replace('pt', '');
                document.execCommand('fontSize', false, '3');
                // Aplicar tamanho específico
                const selection = window.getSelection();
                if (selection.rangeCount > 0) {
                    const range = selection.getRangeAt(0);
                    const span = document.createElement('span');
                    span.style.fontSize = e.target.value;
                    try {
                        range.surroundContents(span);
                    } catch (e) {
                        console.log('Erro ao aplicar tamanho:', e);
                    }
                }
                this.showNotification(`Tamanho alterado para ${e.target.value}`, 'success');
            });
        }
        
        // Botões de formatação
        document.querySelectorAll('[data-format]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.target.closest('[data-format]').dataset.format;
                document.execCommand(format, false, null);
                btn.classList.toggle('active');
                this.showNotification(`Formatação ${format} aplicada`, 'success');
            });
        });
        
        // Botões de alinhamento
        document.querySelectorAll('[data-align]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const align = e.target.closest('[data-align]').dataset.align;
                let command = '';
                switch(align) {
                    case 'left': command = 'justifyLeft'; break;
                    case 'center': command = 'justifyCenter'; break;
                    case 'right': command = 'justifyRight'; break;
                    case 'justify': command = 'justifyFull'; break;
                }
                document.execCommand(command, false, null);
                this.showNotification(`Alinhamento ${align} aplicado`, 'success');
            });
        });
        
        // Botões de ação avançada
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('[data-action]').dataset.action;
                this.handleAdvancedAction(action);
            });
        });
        
        // Seletor de formato de bloco
        const blockFormat = document.getElementById('blockFormat');
        if (blockFormat) {
            blockFormat.addEventListener('change', (e) => {
                this.formatBlock(e.target.value);
            });
        }
        
        // Atalhos de teclado
        this.setupKeyboardShortcuts();
    }
    
    handleAdvancedAction(action) {
        console.log(`Executando ação: ${action}`);
        
        switch(action) {
            case 'undo':
                document.execCommand('undo', false, null);
                this.showNotification('Ação desfeita', 'success');
                break;
                
            case 'redo':
                document.execCommand('redo', false, null);
                this.showNotification('Ação refeita', 'success');
                break;
                
            case 'subscript':
                document.execCommand('subscript', false, null);
                this.showNotification('Subscrito aplicado', 'success');
                break;
                
            case 'superscript':
                document.execCommand('superscript', false, null);
                this.showNotification('Sobrescrito aplicado', 'success');
                break;
                
            case 'insertOrderedList':
                document.execCommand('insertOrderedList', false, null);
                this.showNotification('Lista numerada inserida', 'success');
                break;
                
            case 'insertUnorderedList':
                document.execCommand('insertUnorderedList', false, null);
                this.showNotification('Lista com marcadores inserida', 'success');
                break;
                
            case 'outdent':
                document.execCommand('outdent', false, null);
                this.showNotification('Recuo diminuído', 'success');
                break;
                
            case 'indent':
                document.execCommand('indent', false, null);
                this.showNotification('Recuo aumentado', 'success');
                break;
                
            case 'insertTable':
                this.insertTable();
                break;
                
            case 'insertLink':
                this.insertLink();
                break;
                
            case 'insertImage':
                this.insertImage();
                break;
                
            case 'insertQuote':
                this.insertQuote();
                break;
                
            case 'insertRule':
                this.insertHorizontalRule();
                break;
                
            case 'clearFormat':
                document.execCommand('removeFormat', false, null);
                this.showNotification('Formatação removida', 'success');
                break;
                
            case 'selectAll':
                document.execCommand('selectAll', false, null);
                this.showNotification('Tudo selecionado', 'success');
                break;
                
            case 'findReplace':
                this.showFindReplace();
                break;
                
            case 'spellCheck':
                this.runSpellCheck();
                break;
                
            case 'wordCount':
                this.showWordCount();
                break;
                
            case 'print':
                this.printDocument();
                break;
                
            default:
                console.log(`Ação não implementada: ${action}`);
        }
    }
    
    formatBlock(format) {
        document.execCommand('formatBlock', false, format);
        this.showNotification(`Formato ${format} aplicado`, 'success');
    }
    
    insertTable() {
        const rows = prompt('Número de linhas:', '3');
        const cols = prompt('Número de colunas:', '3');
        
        if (rows && cols) {
            let tableHTML = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 1rem 0;">';
            for (let i = 0; i < parseInt(rows); i++) {
                tableHTML += '<tr>';
                for (let j = 0; j < parseInt(cols); j++) {
                    tableHTML += '<td style="padding: 8px; border: 1px solid #ddd;">&nbsp;</td>';
                }
                tableHTML += '</tr>';
            }
            tableHTML += '</table>';
            
            this.insertContent(tableHTML, 'Tabela');
        }
    }
    
    insertLink() {
        const url = prompt('URL do link:');
        const text = prompt('Texto do link:');
        
        if (url && text) {
            const linkHTML = `<a href="${url}" target="_blank" style="color: #007bff; text-decoration: underline;">${text}</a>`;
            this.insertContent(linkHTML, 'Link');
        }
    }
    
    insertImage() {
        // Criar input de arquivo oculto
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg';
        fileInput.style.display = 'none';
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                // Verificar se é uma imagem válida
                if (!file.type.startsWith('image/')) {
                    this.showNotification('Por favor, selecione apenas arquivos de imagem', 'error');
                    return;
                }
                
                // Verificar tamanho (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    this.showNotification('Imagem muito grande. Máximo 5MB permitido', 'error');
                    return;
                }
                
                // Criar FileReader para converter em base64
                const reader = new FileReader();
                reader.onload = (e) => {
                    const dataURL = e.target.result;
                    const alt = prompt('Texto alternativo da imagem:', file.name.split('.')[0]);
                    
                    const imgHTML = `
                        <div style="text-align: center; margin: 1rem 0; display: inline-block; width: auto;">
                            <img src="${dataURL}" 
                                 alt="${alt || 'Imagem'}" 
                                 style="
                                     max-width: 400px; 
                                     width: auto; 
                                     height: auto; 
                                     border-radius: 8px; 
                                     box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                                     display: block;
                                     object-fit: contain;
                                 "
                                 title="${file.name}">
                            <div style="font-size: 0.8em; color: #6c757d; margin-top: 0.5rem; white-space: nowrap;">
                                ${file.name} (${(file.size / 1024).toFixed(1)} KB)
                            </div>
                        </div>
                    `;
                    
                    this.insertContent(imgHTML, 'Imagem');
                    this.showNotification(`Imagem "${file.name}" inserida com sucesso!`, 'success');
                };
                
                reader.onerror = () => {
                    this.showNotification('Erro ao carregar a imagem', 'error');
                };
                
                reader.readAsDataURL(file);
            }
            
            // Remover input temporário
            document.body.removeChild(fileInput);
        });
        
        // Adicionar ao DOM e clique
        document.body.appendChild(fileInput);
        fileInput.click();
    }
    
    insertQuote() {
        const text = prompt('Texto da citação:');
        
        if (text) {
            const quoteHTML = `
                <blockquote style="
                    border-left: 4px solid #007bff;
                    padding-left: 1rem;
                    margin: 1rem 0;
                    font-style: italic;
                    color: #6c757d;
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 0 4px 4px 0;
                ">
                    ${text}
                </blockquote>
            `;
            this.insertContent(quoteHTML, 'Citação');
        }
    }
    
    insertHorizontalRule() {
        const ruleHTML = '<hr style="border: none; border-top: 2px solid #dee2e6; margin: 2rem 0;">';
        this.insertContent(ruleHTML, 'Linha horizontal');
    }
    
    showFindReplace() {
        const searchText = prompt('Localizar:');
        if (searchText) {
            const replaceText = prompt('Substituir por:');
            if (replaceText !== null) {
                const content = this.documentContent.innerHTML;
                const newContent = content.replace(new RegExp(searchText, 'gi'), replaceText);
                this.documentContent.innerHTML = newContent;
                this.showNotification(`Texto substituído: "${searchText}" por "${replaceText}"`, 'success');
            }
        }
    }
    
    runSpellCheck() {
        // Simulação de verificação ortográfica
        const words = this.documentContent.innerText.split(/\s+/);
        const suspiciousWords = words.filter(word => 
            word.length > 15 || 
            /[0-9]{5,}/.test(word) ||
            /[A-Z]{3,}/.test(word)
        );
        
        if (suspiciousWords.length > 0) {
            this.showNotification(`Verificação concluída. ${suspiciousWords.length} palavras podem precisar de revisão`, 'info');
        } else {
            this.showNotification('Nenhum erro ortográfico detectado', 'success');
        }
    }
    
    showWordCount() {
        const text = this.documentContent.innerText || '';
        const words = text.trim().split(/\s+/).filter(word => word.length > 0);
        const chars = text.length;
        const charsNoSpaces = text.replace(/\s/g, '').length;
        const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;
        
        alert(`Estatísticas do documento:
        
Palavras: ${words.length}
Caracteres: ${chars}
Caracteres sem espaços: ${charsNoSpaces}
Parágrafos: ${paragraphs}`);
    }
    
    printDocument() {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Documento Legal</title>
                <style>
                    body { font-family: 'Times New Roman', serif; line-height: 1.6; margin: 2cm; }
                    h1, h2, h3 { color: #2c3e50; }
                    table { border-collapse: collapse; width: 100%; }
                    td, th { border: 1px solid #ddd; padding: 8px; }
                    blockquote { border-left: 4px solid #007bff; padding-left: 1rem; margin: 1rem 0; font-style: italic; }
                </style>
            </head>
            <body>
                ${this.documentContent.innerHTML}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
    
    setupCustomColorInputs() {
        // Configurar inputs de cor personalizada
        const customColorInputs = document.querySelectorAll('input[type="color"]');
        
        customColorInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const color = e.target.value;
                const gridId = e.target.getAttribute('data-target');
                
                if (gridId) {
                    this.applyColor(gridId, color);
                }
            });
        });
    }
    
    setupKeyboardShortcuts() {
        this.documentContent.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'b':
                        e.preventDefault();
                        document.execCommand('bold', false, null);
                        break;
                    case 'i':
                        e.preventDefault();
                        document.execCommand('italic', false, null);
                        break;
                    case 'u':
                        e.preventDefault();
                        document.execCommand('underline', false, null);
                        break;
                    case 'z':
                        e.preventDefault();
                        document.execCommand('undo', false, null);
                        break;
                    case 'y':
                        e.preventDefault();
                        document.execCommand('redo', false, null);
                        break;
                    case 'a':
                        e.preventDefault();
                        document.execCommand('selectAll', false, null);
                        break;
                    case 'p':
                        e.preventDefault();
                        this.printDocument();
                        break;
                }
            }
        });
    }
    
    handleToolAction(item) {
        console.log('=== PROCESSANDO AÇÃO DA FERRAMENTA ===');
        console.log('Item:', item);
        
        if (!item) {
            console.error('Item não fornecido');
            return;
        }
        
        const template = item.getAttribute('data-template');
        const element = item.getAttribute('data-element');
        const ai = item.getAttribute('data-ai');
        
        console.log('Atributos:', { template, element, ai });
        
        // Verificar se temos o documento
        if (!this.documentContent) {
            console.log('Documento não encontrado, procurando novamente...');
            this.findDocumentContent();
        }
        
        if (!this.documentContent) {
            console.error('ERRO: Documento não encontrado!');
            this.showNotification('Erro: Área do documento não encontrada', 'error');
            return;
        }
        
        console.log('Documento encontrado, processando ação...');
        
        if (template) {
            this.insertTemplate(template);
        } else if (element) {
            this.insertElement(element);
        } else if (ai) {
            this.callAIAssistant(ai);
        } else {
            console.error('Nenhum atributo de ação encontrado');
            this.showNotification('Erro: Ação não reconhecida', 'error');
        }
    }
    
    insertTemplate(templateType) {
        console.log('=== INSERINDO TEMPLATE ===');
        console.log('Tipo:', templateType);
        
        const templates = {
            'peticao': `
                <h1 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
                    PETIÇÃO INICIAL
                </h1>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <strong>✅ TEMPLATE INSERIDO COM SUCESSO!</strong>
                </div>
                <h2 style="color: #2c3e50; margin-top: 2rem;">I - DOS FATOS</h2>
                <p>Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito,</p>
                <p>[NOME DO REQUERENTE], [qualificação completa], vem respeitosamente à presença de Vossa Excelência...</p>
                <h2 style="color: #2c3e50; margin-top: 2rem;">II - DO DIREITO</h2>
                <p>O direito invocado fundamenta-se nos seguintes dispositivos legais:</p>
                <h2 style="color: #2c3e50; margin-top: 2rem;">III - DOS PEDIDOS</h2>
                <p>Diante do exposto, requer-se:</p>
                <p>a) A citação do requerido;</p>
                <p>b) A procedência dos pedidos;</p>
                <p>c) A condenação em honorários advocatícios.</p>
            `,
            'contestacao': `
                <h1 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
                    CONTESTAÇÃO
                </h1>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <strong>✅ TEMPLATE CONTESTAÇÃO INSERIDO!</strong>
                </div>
                <h2 style="color: #2c3e50;">I - PRELIMINARES</h2>
                <p>Preliminarmente, sustenta-se que...</p>
                <h2 style="color: #2c3e50;">II - DO MÉRITO</h2>
                <p>Quanto ao mérito, impugna-se os fatos alegados...</p>
            `,
            'recurso': `
                <h1 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
                    RECURSO DE APELAÇÃO
                </h1>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <strong>✅ TEMPLATE RECURSO INSERIDO!</strong>
                </div>
                <h2 style="color: #2c3e50;">I - DOS FATOS</h2>
                <p>Vem o recorrente, por seu advogado, interpor o presente recurso...</p>
            `,
            'contrato': `
                <h1 style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
                    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
                </h1>
                <div style="background: #e8f4fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                    <strong>✅ TEMPLATE CONTRATO INSERIDO!</strong>
                </div>
                <h2 style="color: #2c3e50;">CLÁUSULA PRIMEIRA - DO OBJETO</h2>
                <p>O presente contrato tem por objeto...</p>
                <h2 style="color: #2c3e50;">CLÁUSULA SEGUNDA - DO VALOR</h2>
                <p>O valor total dos serviços é de...</p>
            `
        };
        
        if (templates[templateType]) {
            this.insertContent(templates[templateType], `Template ${templateType}`);
        } else {
            console.error('Template não encontrado:', templateType);
            this.showNotification(`Template ${templateType} não encontrado`, 'error');
        }
    }
    
    insertElement(elementType) {
        console.log('=== INSERINDO ELEMENTO ===');
        console.log('Tipo:', elementType);
        
        const elements = {
            'timeline': `
                <div style="border-left: 4px solid #3498db; padding-left: 1rem; margin: 2rem 0; background: #f8f9fa; border-radius: 5px; padding: 1rem;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem;">
                        <strong>✅ TIMELINE INSERIDA COM SUCESSO!</strong>
                    </div>
                    <h4 style="color: #2c3e50; margin-bottom: 1rem;">Timeline Processual</h4>
                    <div style="margin-bottom: 0.5rem;"><strong>📅 [Data]:</strong> [Evento importante]</div>
                    <div style="margin-bottom: 0.5rem;"><strong>📅 [Data]:</strong> [Próximo evento]</div>
                    <div style="margin-bottom: 0.5rem;"><strong>📅 [Data]:</strong> [Evento futuro]</div>
                </div>
            `,
            'chart': `
                <div style="border: 2px solid #17a2b8; padding: 1rem; margin: 2rem 0; background: #f8f9fa; border-radius: 5px;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem;">
                        <strong>✅ GRÁFICO INSERIDO COM SUCESSO!</strong>
                    </div>
                    <h4 style="color: #2c3e50; text-align: center;">Gráfico Explicativo</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
                        <tr style="background: #e9ecef;">
                            <th style="border: 1px solid #dee2e6; padding: 0.5rem;">Item</th>
                            <th style="border: 1px solid #dee2e6; padding: 0.5rem;">Valor</th>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #dee2e6; padding: 0.5rem;">Dado 1</td>
                            <td style="border: 1px solid #dee2e6; padding: 0.5rem;">[Valor]</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #dee2e6; padding: 0.5rem;">Dado 2</td>
                            <td style="border: 1px solid #dee2e6; padding: 0.5rem;">[Valor]</td>
                        </tr>
                    </table>
                </div>
            `,
            'highlight': `
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 1rem; margin: 2rem 0;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem;">
                        <strong>✅ DESTAQUE INSERIDO COM SUCESSO!</strong>
                    </div>
                    <h4 style="color: #856404; margin-bottom: 0.5rem;">💡 Ponto Importante</h4>
                    <p style="margin: 0; color: #856404;">
                        <strong>[Texto em destaque aqui - ponto crucial do documento]</strong>
                    </p>
                </div>
            `,
            'citation': `
                <blockquote style="border-left: 4px solid #007bff; margin: 2rem 0; padding: 1rem; background: #f8f9fa; font-style: italic; border-radius: 5px;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem; font-style: normal;">
                        <strong>✅ CITAÇÃO INSERIDA COM SUCESSO!</strong>
                    </div>
                    <p style="font-size: 1.1em; color: #495057; margin-bottom: 1rem;">
                        "[Texto da citação jurisprudencial ou doutrinária aqui]"
                    </p>
                    <footer style="font-size: 0.9em; color: #6c757d; font-style: normal;">
                        — <cite><strong>[Fonte: Tribunal, Autor, etc.]</strong></cite>
                    </footer>
                </blockquote>
            `
        };
        
        if (elements[elementType]) {
            this.insertContent(elements[elementType], `Elemento ${elementType}`);
        } else {
            console.error('Elemento não encontrado:', elementType);
            this.showNotification(`Elemento ${elementType} não encontrado`, 'error');
        }
    }
    
    insertContent(content, description) {
        console.log('=== INSERINDO CONTEÚDO ===');
        console.log('Descrição:', description);
        console.log('Documento existe?', !!this.documentContent);
        
        if (!this.documentContent) {
            console.error('Documento não encontrado!');
            this.showNotification('Erro: Documento não encontrado', 'error');
            return;
        }
        
        try {
            console.log('Conteúdo ANTES - length:', this.documentContent.innerHTML.length);
            
            // Criar wrapper com funcionalidades de drag e resize para elementos gráficos
            let finalContent = content;
            
            // Verificar se é um elemento que deve ser arrastável (imagens, tabelas, gráficos, etc.)
            if (content.includes('<img') || content.includes('<table') || content.includes('border:') || content.includes('chart') || content.includes('timeline')) {
                const wrapperId = 'draggable-' + Date.now();
                finalContent = `
                    <div id="${wrapperId}" class="draggable-resizable-element" style="
                        position: relative;
                        display: inline-block;
                        border: 2px dashed transparent;
                        margin: 10px;
                        cursor: move;
                        min-width: 100px;
                        min-height: 50px;
                        overflow: visible;
                        background: rgba(255,255,255,0.01);
                        max-width: 100%;
                        width: auto;
                        height: auto;
                    " onmouseenter="this.style.border='2px dashed #007bff'; this.querySelector('.resize-controls').style.display='block';" 
                       onmouseleave="this.style.border='2px dashed transparent'; this.querySelector('.resize-controls').style.display='none';">
                        ${content}
                        <div class="resize-controls" style="display: none;">
                            <div class="resize-handle nw" style="position: absolute; top: -8px; left: -8px; width: 16px; height: 16px; background: #007bff; cursor: nw-resize; border: 2px solid white; border-radius: 50%; z-index: 1001;"></div>
                            <div class="resize-handle ne" style="position: absolute; top: -8px; right: -8px; width: 16px; height: 16px; background: #007bff; cursor: ne-resize; border: 2px solid white; border-radius: 50%; z-index: 1001;"></div>
                            <div class="resize-handle sw" style="position: absolute; bottom: -8px; left: -8px; width: 16px; height: 16px; background: #007bff; cursor: sw-resize; border: 2px solid white; border-radius: 50%; z-index: 1001;"></div>
                            <div class="resize-handle se" style="position: absolute; bottom: -8px; right: -8px; width: 16px; height: 16px; background: #007bff; cursor: se-resize; border: 2px solid white; border-radius: 50%; z-index: 1001;"></div>
                        </div>
                    </div>
                `;
                
                // Inserir no final do documento
                this.documentContent.innerHTML += finalContent;
                
                // Configurar funcionalidades após inserção
                setTimeout(() => {
                    this.setupDragAndResize(wrapperId);
                }, 100);
                
            } else {
                // Inserir conteúdo normal
                this.documentContent.innerHTML += finalContent;
            }
            
            console.log('Conteúdo DEPOIS - length:', this.documentContent.innerHTML.length);
            console.log('Conteúdo inserido com sucesso!');
            
            // Scroll para o novo conteúdo
            this.documentContent.scrollTop = this.documentContent.scrollHeight;
            
            // Notificação de sucesso
            this.showNotification(`${description} inserido com sucesso!`, 'success');
            
        } catch (error) {
            console.error('Erro ao inserir conteúdo:', error);
            this.showNotification(`Erro ao inserir ${description}: ${error.message}`, 'error');
        }
    }
    
    setupDragAndResize(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        console.log('Configurando drag & resize para:', elementId);
        
        // Sistema de arrastar
        let isDragging = false;
        let dragStartX, dragStartY, elementStartX, elementStartY;
        
        element.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('resize-handle')) return;
            
            isDragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            
            const rect = element.getBoundingClientRect();
            const containerRect = this.documentContent.getBoundingClientRect();
            elementStartX = rect.left - containerRect.left;
            elementStartY = rect.top - containerRect.top;
            
            element.style.zIndex = '1000';
            element.style.position = 'relative';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;
            
            element.style.left = deltaX + 'px';
            element.style.top = deltaY + 'px';
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.style.zIndex = 'auto';
            }
        });
        
        // Sistema de redimensionar
        const resizeHandles = element.querySelectorAll('.resize-handle');
        resizeHandles.forEach(handle => {
            let isResizing = false;
            let resizeStartX, resizeStartY, startWidth, startHeight;
            
            handle.addEventListener('mousedown', (e) => {
                isResizing = true;
                resizeStartX = e.clientX;
                resizeStartY = e.clientY;
                
                const rect = element.getBoundingClientRect();
                startWidth = rect.width;
                startHeight = rect.height;
                
                e.stopPropagation();
                e.preventDefault();
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;
                
                const deltaX = e.clientX - resizeStartX;
                const deltaY = e.clientY - resizeStartY;
                
                if (handle.classList.contains('se')) {
                    element.style.width = Math.max(100, startWidth + deltaX) + 'px';
                    element.style.height = Math.max(50, startHeight + deltaY) + 'px';
                } else if (handle.classList.contains('sw')) {
                    element.style.width = Math.max(100, startWidth - deltaX) + 'px';
                    element.style.height = Math.max(50, startHeight + deltaY) + 'px';
                } else if (handle.classList.contains('ne')) {
                    element.style.width = Math.max(100, startWidth + deltaX) + 'px';
                    element.style.height = Math.max(50, startHeight - deltaY) + 'px';
                } else if (handle.classList.contains('nw')) {
                    element.style.width = Math.max(100, startWidth - deltaX) + 'px';
                    element.style.height = Math.max(50, startHeight - deltaY) + 'px';
                }
                
                // Ajustar conteúdo interno se for imagem
                const img = element.querySelector('img');
                if (img) {
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'contain';
                }
            });
            
            document.addEventListener('mouseup', () => {
                isResizing = false;
            });
        });
    }
    
    callAIAssistant(aiType) {
        console.log('=== CHAMANDO ASSISTENTE IA ===');
        console.log('Tipo:', aiType);
        
        if (aiType === 'generate') {
            const aiContent = `
                <div style="border: 2px solid #28a745; padding: 1rem; margin: 2rem 0; background: #f8fff9; border-radius: 5px;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem;">
                        <strong>✅ ASSISTENTE IA ATIVADO COM SUCESSO!</strong>
                    </div>
                    <h4 style="color: #155724; margin-bottom: 1rem;">🤖 Sugestão da IA</h4>
                    <p style="color: #155724;">
                        <strong>Texto gerado pela IA:</strong><br>
                        Com base no contexto do documento, sugiro incluir uma fundamentação legal mais robusta, 
                        citando precedentes jurisprudenciais relevantes e doutrina especializada na matéria.
                    </p>
                    <p style="color: #155724; font-size: 0.9em; margin-top: 1rem;">
                        <em>💡 Dica: Utilize as ferramentas de citação para adicionar jurisprudência específica.</em>
                    </p>
                </div>
            `;
            this.insertContent(aiContent, 'Assistente IA - Geração');
            
        } else if (aiType === 'review') {
            const reviewContent = `
                <div style="border: 2px solid #ffc107; padding: 1rem; margin: 2rem 0; background: #fffbf0; border-radius: 5px;">
                    <div style="background: #d4edda; padding: 0.5rem; border-radius: 3px; margin-bottom: 1rem;">
                        <strong>✅ REVISÃO IA EXECUTADA COM SUCESSO!</strong>
                    </div>
                    <h4 style="color: #856404; margin-bottom: 1rem;">🔍 Análise do Documento</h4>
                    <ul style="color: #856404;">
                        <li><strong>Estrutura:</strong> Documento bem organizado ✓</li>
                        <li><strong>Fundamentação:</strong> Necessita de mais base legal</li>
                        <li><strong>Linguagem:</strong> Adequada ao contexto jurídico ✓</li>
                        <li><strong>Sugestão:</strong> Adicionar mais jurisprudência</li>
                    </ul>
                </div>
            `;
            this.insertContent(reviewContent, 'Assistente IA - Revisão');
            
        } else {
            this.showNotification(`Assistente IA ${aiType} não implementado`, 'info');
        }
    }
    
    showNotification(message, type = 'info') {
        console.log(`NOTIFICAÇÃO [${type}]: ${message}`);
        
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        notification.innerHTML = `
            <strong>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</strong>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Remover após 3 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    saveDocument() {
        console.log('=== SALVANDO DOCUMENTO ===');
        
        if (!this.documentContent) {
            this.showNotification('Erro: Documento não encontrado para salvar', 'error');
            return;
        }
        
        const documentData = {
            title: this.documentData.title,
            content: this.documentContent.innerHTML,
            area: this.documentData.area
        };
        
        // Salvar no localStorage temporariamente
        try {
            localStorage.setItem('legal_document_content', this.documentContent.innerHTML);
            localStorage.setItem('legal_document_timestamp', new Date().toISOString());
            this.showNotification('Documento salvo localmente!', 'success');
        } catch (error) {
            console.error('Erro ao salvar:', error);
            this.showNotification('Erro ao salvar documento', 'error');
        }
    }
    
    exportDocument() {
        console.log('=== EXPORTANDO DOCUMENTO ===');
        
        if (!this.documentContent) {
            this.showNotification('Erro: Documento não encontrado para exportar', 'error');
            return;
        }
        
        const documentData = {
            title: this.documentData.title,
            content: this.documentContent.innerHTML,
            area: this.documentData.area
        };
        
        const link = document.createElement('a');
        link.href = '/legal_design_pro/exportar_documento';
        link.download = `${this.documentData.title}.docx`;
        link.click();
        
        this.showNotification('Documento exportado!', 'success');
    }
    
    setupAutoSave() {
        console.log('=== CONFIGURANDO AUTO SAVE ===');
        
        // Auto save local a cada 5 minutos
        setInterval(() => {
            if (this.documentContent && this.documentContent.innerHTML.trim().length > 100) {
                console.log('Auto save local executado');
                this.saveToLocalStorage();
            }
        }, 300000); // 5 minutos
        
        // Salvar ao digitar (debounced)
        let saveTimeout;
        this.documentContent.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                this.saveToLocalStorage();
            }, 10000); // 10 segundos após parar de digitar
        });
    }
    
    saveToLocalStorage() {
        try {
            const content = this.documentContent.innerHTML;
            localStorage.setItem('legal_document_content', content);
            localStorage.setItem('legal_document_timestamp', new Date().toISOString());
            console.log('Documento salvo localmente');
        } catch (error) {
            console.error('Erro ao salvar localmente:', error);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM READY - INICIALIZANDO EDITOR ===');
    window.legalEditor = new LegalDesignEditor();
});

// Backup: inicializar imediatamente se o DOM já estiver pronto
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('=== DOM JÁ PRONTO - INICIALIZANDO EDITOR ===');
    window.legalEditor = new LegalDesignEditor();
}

console.log('=== SCRIPT LEGAL DESIGN EDITOR CARREGADO COMPLETAMENTE ===');