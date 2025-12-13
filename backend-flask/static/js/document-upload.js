// Debug log para verificar se o arquivo está carregando
console.log('Document upload script carregado com sucesso');

// Função para processar arquivo carregado - VERSÃO NOVA
function processarArquivo(input) {
    console.log('processarArquivo chamada', input);
    
    if (!input || !input.files || !input.files[0]) {
        console.log('Nenhum arquivo selecionado');
        return;
    }
    
    const arquivo = input.files[0];
    console.log('Arquivo selecionado:', arquivo.name, arquivo.type, arquivo.size);
    
    // Validação de tipo de arquivo
    const extensaoPermitida = /\.(txt|pdf|docx|doc|html|md|csv|xlsx|xls)$/i;
    if (!extensaoPermitida.test(arquivo.name)) {
        alert('Tipo de arquivo não suportado. Use: PDF, Word, TXT, HTML, MD, Excel ou CSV');
        input.value = '';
        return;
    }
    
    // Validação de tamanho (máximo 10MB)
    if (arquivo.size > 10 * 1024 * 1024) {
        alert('Arquivo muito grande. Tamanho máximo permitido: 10MB');
        input.value = '';
        return;
    }
    
    const textarea = document.getElementById('texto');
    if (!textarea) {
        console.error('Textarea não encontrada');
        return;
    }
    
    // Mostrar estado de carregamento
    const originalPlaceholder = textarea.placeholder;
    const originalValue = textarea.value;
    textarea.placeholder = 'Processando arquivo... Aguarde...';
    textarea.disabled = true;
    textarea.style.backgroundColor = '#f8f9fa';
    
    // Criar FormData
    const formData = new FormData();
    formData.append('documento', arquivo);
    
    console.log('Enviando arquivo para processamento...');
    
    // Fazer upload com fetch
    fetch('/processar-documento', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('Resposta recebida:', response.status);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados recebidos:', data);
        
        if (data.success && data.texto) {
            textarea.value = data.texto;
            mostrarNotificacao(`Arquivo "${arquivo.name}" carregado com sucesso!`, 'success');
        } else {
            throw new Error(data.error || 'Erro desconhecido ao processar arquivo');
        }
    })
    .catch(error => {
        console.error('Erro no upload:', error);
        textarea.value = originalValue;
        mostrarNotificacao(`Erro ao processar arquivo: ${error.message}`, 'error');
    })
    .finally(() => {
        // Restaurar estado original
        textarea.placeholder = originalPlaceholder;
        textarea.disabled = false;
        textarea.style.backgroundColor = '';
        input.value = ''; // Limpar input para permitir reenvio
    });
}

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo) {
    console.log('Mostrando notificação:', tipo, mensagem);
    
    // Remover notificações anteriores
    const notificacoesAnteriores = document.querySelectorAll('.alert-upload');
    notificacoesAnteriores.forEach(n => n.remove());
    
    const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
    const icone = tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
    
    const alerta = document.createElement('div');
    alerta.className = `alert ${alertClass} alert-dismissible fade show alert-upload`;
    alerta.style.position = 'fixed';
    alerta.style.top = '20px';
    alerta.style.right = '20px';
    alerta.style.zIndex = '9999';
    alerta.style.minWidth = '300px';
    alerta.innerHTML = `
        <i class="fas ${icone} me-2"></i>
        ${mensagem}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(alerta);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.remove();
        }
    }, 5000);
}

// Função para adicionar drag and drop
function adicionarDragAndDrop() {
    const uploadArea = document.querySelector('.upload-area');
    const textarea = document.getElementById('texto');
    
    if (!uploadArea && !textarea) return;
    
    console.log('Adicionando drag and drop');
    
    // Elementos que aceitam drag and drop
    const dropZones = [uploadArea, textarea].filter(Boolean);
    
    dropZones.forEach(zone => {
        // Prevenir comportamento padrão
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight durante drag
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, () => highlight(zone), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, () => unhighlight(zone), false);
        });
        
        // Handle drop
        zone.addEventListener('drop', handleDrop, false);
    });
    
    // Prevenir comportamento padrão no body
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(element) {
        if (element.classList.contains('upload-area')) {
            element.style.backgroundColor = '#e3f2fd';
            element.style.borderColor = '#2196F3';
            element.style.transform = 'scale(1.02)';
        } else if (element.id === 'texto') {
            element.style.backgroundColor = '#e3f2fd';
            element.style.border = '2px dashed #2196F3';
        }
    }
    
    function unhighlight(element) {
        if (element.classList.contains('upload-area')) {
            element.style.backgroundColor = '#f8f9fa';
            element.style.borderColor = '#dee2e6';
            element.style.transform = 'scale(1)';
        } else if (element.id === 'texto') {
            element.style.backgroundColor = '';
            element.style.border = '';
        }
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            console.log('Arquivo arrastado:', files[0].name);
            
            // Simular input file para reutilizar a função processarArquivo
            const fakeInput = {
                files: files,
                value: ''
            };
            
            processarArquivo(fakeInput);
        }
    }
    
    // Adicionar clique na área de upload
    if (uploadArea) {
        // Adicionar clique em toda a área de upload
        uploadArea.addEventListener('click', function(e) {
            // Verificar se não é o botão que foi clicado
            if (!e.target.classList.contains('btn') && !e.target.closest('.btn')) {
                console.log('Clique na área de upload detectado');
                const inputFile = document.getElementById('documento');
                if (inputFile) {
                    console.log('Abrindo seletor de arquivo');
                    inputFile.click();
                } else {
                    console.error('Input file não encontrado');
                }
            }
        });
        
        // Adicionar clique em elementos filhos também
        const uploadChildren = uploadArea.querySelectorAll('i, strong, div:not(.btn)');
        uploadChildren.forEach(child => {
            child.addEventListener('click', function(e) {
                if (!e.target.classList.contains('btn') && !e.target.closest('.btn')) {
                    console.log('Clique em elemento filho detectado');
                    e.stopPropagation();
                    const inputFile = document.getElementById('documento');
                    if (inputFile) {
                        inputFile.click();
                    }
                }
            });
        });
        
        uploadArea.style.cursor = 'pointer';
        uploadArea.style.transition = 'all 0.3s ease';
        console.log('Event listeners adicionados à área de upload');
    }
}

// Adicionar efeitos visuais de hover
function adicionarEfeitosVisuais() {
    const uploadArea = document.querySelector('.upload-area');
    const hoverIndicator = document.getElementById('hover-indicator');
    
    if (uploadArea && hoverIndicator) {
        uploadArea.addEventListener('mouseenter', function() {
            hoverIndicator.style.opacity = '1';
            uploadArea.style.transform = 'scale(1.02)';
            uploadArea.style.boxShadow = '0 8px 25px rgba(25, 118, 210, 0.15)';
        });
        
        uploadArea.addEventListener('mouseleave', function() {
            hoverIndicator.style.opacity = '0';
            uploadArea.style.transform = 'scale(1)';
            uploadArea.style.boxShadow = 'none';
        });
        
        uploadArea.addEventListener('mousedown', function() {
            uploadArea.style.transform = 'scale(0.98)';
        });
        
        uploadArea.addEventListener('mouseup', function() {
            uploadArea.style.transform = 'scale(1.02)';
        });
        
        console.log('Efeitos visuais adicionados à área de upload');
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando upload de documentos...');
    
    // Adicionar drag and drop
    adicionarDragAndDrop();
    
    // Adicionar efeitos visuais
    adicionarEfeitosVisuais();
    
    // Verificar se elementos existem
    const inputFile = document.getElementById('documento');
    const textarea = document.getElementById('texto');
    
    if (!inputFile) {
        console.error('Input file não encontrado');
    } else {
        console.log('Input file encontrado e configurado');
    }
    
    if (!textarea) {
        console.error('Textarea não encontrada');
    } else {
        console.log('Textarea encontrada e configurada para drag and drop');
    }
});