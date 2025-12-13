/**
 * Sistema de Upload Simplificado - Debug
 * Implementação mínima para identificar problemas
 */

console.log('🔧 Upload Debug carregado');

// Aguardar DOM estar pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 DOM carregado, iniciando debug');
    
    // Encontrar elementos
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('documento');
    const textArea = document.getElementById('texto');
    
    console.log('🔧 Elementos encontrados:', {
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        textArea: !!textArea
    });
    
    if (!uploadArea) {
        console.error('❌ Área de upload não encontrada');
        return;
    }
    
    if (!fileInput) {
        console.error('❌ Input de arquivo não encontrado');
        return;
    }
    
    // Remover todos os event listeners existentes
    uploadArea.replaceWith(uploadArea.cloneNode(true));
    const newUploadArea = document.querySelector('.upload-area');
    
    console.log('🔧 Adicionando event listeners...');
    
    // CLIQUE SIMPLES
    newUploadArea.addEventListener('click', function(e) {
        console.log('🔧 CLIQUE DETECTADO!', e.target);
        e.preventDefault();
        e.stopPropagation();
        
        // Verificar se não é botão
        if (!e.target.matches('button') && !e.target.closest('button')) {
            console.log('🔧 Abrindo seletor de arquivo...');
            fileInput.click();
        }
    });
    
    // DRAG AND DROP BÁSICO
    newUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        console.log('🔧 Drag over detectado');
        newUploadArea.style.backgroundColor = 'rgba(0, 123, 255, 0.2)';
    });
    
    newUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        console.log('🔧 Drag leave detectado');
        newUploadArea.style.backgroundColor = '';
    });
    
    newUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        console.log('🔧 DROP DETECTADO!', e.dataTransfer.files);
        newUploadArea.style.backgroundColor = '';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            console.log('🔧 Processando arquivo:', files[0].name);
            processarArquivoDebug(files[0]);
        }
    });
    
    // INPUT FILE CHANGE
    fileInput.addEventListener('change', function(e) {
        console.log('🔧 Input file mudou:', e.target.files);
        if (e.target.files.length > 0) {
            processarArquivoDebug(e.target.files[0]);
        }
    });
    
    // Estilização visual
    newUploadArea.style.cursor = 'pointer';
    newUploadArea.style.transition = 'all 0.3s ease';
    
    console.log('🔧 Sistema de upload debug configurado!');
});

// Função de processamento simplificada
function processarArquivoDebug(file) {
    console.log('🔧 Processando arquivo:', file.name, file.type, file.size);
    
    const textArea = document.getElementById('texto');
    if (textArea) {
        textArea.value = 'Processando arquivo: ' + file.name + '...';
    }
    
    const formData = new FormData();
    formData.append('documento', file);
    
    console.log('🔧 Enviando para servidor...');
    
    fetch('/processar-documento', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('🔧 Resposta recebida:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('🔧 Dados processados:', data);
        if (data.success && textArea) {
            textArea.value = data.texto;
            console.log('✅ Arquivo processado com sucesso!');
            
            // Mostrar notificação simples
            alert('Arquivo processado com sucesso: ' + data.filename);
        } else {
            console.error('❌ Erro no processamento:', data.error);
            alert('Erro: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('❌ Erro na requisição:', error);
        alert('Erro de comunicação: ' + error.message);
        if (textArea) {
            textArea.value = '';
        }
    });
}

// Teste manual
window.testarUpload = function() {
    console.log('🔧 Teste manual iniciado');
    const fileInput = document.getElementById('documento');
    if (fileInput) {
        fileInput.click();
    } else {
        console.error('❌ Input não encontrado para teste');
    }
};

console.log('🔧 Upload Debug pronto. Use testarUpload() no console para teste manual.');