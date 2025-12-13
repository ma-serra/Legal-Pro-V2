/**
 * Sistema de Upload de Documentos - Versão Robusta
 * Funcionalidades: clique, drag-and-drop, validação e processamento
 */

class UploadManager {
    constructor() {
        this.uploadArea = null;
        this.fileInput = null;
        this.textArea = null;
        this.init();
    }

    init() {
        // Aguardar DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        console.log('Iniciando sistema de upload...');
        
        // Encontrar elementos
        this.uploadArea = document.querySelector('.upload-area');
        this.fileInput = document.getElementById('documento');
        this.textArea = document.getElementById('texto');

        if (!this.uploadArea) {
            console.error('Área de upload não encontrada');
            return;
        }

        if (!this.fileInput) {
            console.error('Input de arquivo não encontrado');
            return;
        }

        console.log('Elementos encontrados:', {
            uploadArea: !!this.uploadArea,
            fileInput: !!this.fileInput,
            textArea: !!this.textArea
        });

        this.setupClickHandler();
        this.setupDragAndDrop();
        this.setupFileInputHandler();
        
        console.log('Sistema de upload configurado com sucesso');
    }

    setupClickHandler() {
        console.log('Configurando handler de clique...');
        
        // Adicionar cursor pointer
        this.uploadArea.style.cursor = 'pointer';
        
        // Handler de clique principal
        this.uploadArea.addEventListener('click', (e) => {
            console.log('Clique detectado na área de upload');
            console.log('Target:', e.target.tagName, e.target.className);
            
            // Não interferir com botões
            if (e.target.matches('button') || e.target.closest('button')) {
                console.log('Clique em botão, ignorando...');
                return;
            }
            
            // Abrir seletor de arquivo
            this.openFileSelector();
        });

        console.log('Handler de clique configurado');
    }

    setupDragAndDrop() {
        console.log('Configurando drag and drop...');
        
        let dragCounter = 0;

        // Eventos de drag
        this.uploadArea.addEventListener('dragenter', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dragCounter++;
            this.highlightDropZone();
            console.log('Drag enter');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dragCounter--;
            if (dragCounter === 0) {
                this.unhighlightDropZone();
                console.log('Drag leave');
            }
        });

        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dragCounter = 0;
            this.unhighlightDropZone();
            
            const files = e.dataTransfer.files;
            console.log('Arquivo(s) solto(s):', files.length);
            
            if (files.length > 0) {
                this.processFile(files[0]);
            }
        });

        // Prevenir comportamento padrão no documento
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        console.log('Drag and drop configurado');
    }

    setupFileInputHandler() {
        this.fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files.length > 0) {
                console.log('Arquivo selecionado via input:', files[0].name);
                this.processFile(files[0]);
            }
        });
    }

    openFileSelector() {
        console.log('Abrindo seletor de arquivo...');
        this.fileInput.click();
    }

    highlightDropZone() {
        this.uploadArea.style.borderColor = '#007bff';
        this.uploadArea.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
        this.uploadArea.style.transform = 'scale(1.02)';
    }

    unhighlightDropZone() {
        this.uploadArea.style.borderColor = '#007bff';
        this.uploadArea.style.backgroundColor = '';
        this.uploadArea.style.transform = 'scale(1)';
    }

    validateFile(file) {
        const allowedTypes = [
            'text/plain',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/html',
            'text/markdown',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv'
        ];

        const allowedExtensions = ['.txt', '.pdf', '.docx', '.doc', '.html', '.md', '.xlsx', '.xls', '.csv'];
        
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (file.size > maxSize) {
            this.showNotification('Arquivo muito grande. Máximo: 10MB', 'error');
            return false;
        }

        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!hasValidExtension && !allowedTypes.includes(file.type)) {
            this.showNotification('Tipo de arquivo não suportado', 'error');
            return false;
        }

        return true;
    }

    async processFile(file) {
        console.log('Processando arquivo:', file.name);

        if (!this.validateFile(file)) {
            return;
        }

        // Mostrar loading
        if (this.textArea) {
            this.textArea.value = 'Processando arquivo...';
        }

        try {
            const formData = new FormData();
            formData.append('documento', file);

            const response = await fetch('/processar-documento', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            console.log('Resposta do servidor:', data);

            if (data.success && this.textArea) {
                this.textArea.value = data.texto;
                this.showNotification(`Arquivo "${data.filename}" processado com sucesso!`, 'success');
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }

        } catch (error) {
            console.error('Erro ao processar arquivo:', error);
            this.showNotification('Erro ao processar arquivo: ' + error.message, 'error');
            if (this.textArea) {
                this.textArea.value = '';
            }
        }
    }

    showNotification(message, type) {
        console.log(`Notificação ${type}:`, message);
        
        // Criar notificação visual
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        document.body.appendChild(notification);

        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Inicializar sistema de upload
const uploadManager = new UploadManager();

// Função global para compatibilidade
function processarArquivo(input) {
    if (input.files && input.files.length > 0) {
        uploadManager.processFile(input.files[0]);
    }
}

// CSS para animação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

console.log('Upload sistema carregado e pronto');