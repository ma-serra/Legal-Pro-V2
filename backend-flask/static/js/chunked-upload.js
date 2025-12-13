/**
 * Sistema de Upload em Chunks para contornar limite CloudFlare
 * Divide arquivos grandes em pedaços menores que 5MB
 */

class ChunkedUploader {
    constructor(options = {}) {
        this.chunkSize = options.chunkSize || 5 * 1024 * 1024; // 5MB chunks
        this.maxRetries = options.maxRetries || 3;
        this.onProgress = options.onProgress || (() => {});
        this.onComplete = options.onComplete || (() => {});
        this.onError = options.onError || (() => {});
    }

    async upload(file, uploadUrl) {
        const totalChunks = Math.ceil(file.size / this.chunkSize);
        const sessionId = this.generateSessionId();
        
        console.log(`Iniciando upload em chunks: ${totalChunks} chunks de ${this.chunkSize / 1024 / 1024}MB`);
        
        try {
            // Upload cada chunk sequencialmente
            for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
                const start = chunkIndex * this.chunkSize;
                const end = Math.min(start + this.chunkSize, file.size);
                const chunk = file.slice(start, end);
                
                console.log(`Enviando chunk ${chunkIndex + 1}/${totalChunks} (${start}-${end})`);
                
                await this.uploadChunk(chunk, chunkIndex, totalChunks, sessionId, file.name);
                
                // Atualizar progresso
                const progress = ((chunkIndex + 1) / totalChunks) * 100;
                this.onProgress(progress, chunkIndex + 1, totalChunks);
            }
            
            // Finalizar upload
            const result = await this.finalizeUpload(sessionId, file.name);
            this.onComplete(result);
            
            return result;
            
        } catch (error) {
            console.error('Erro no upload em chunks:', error);
            this.onError(error);
            throw error;
        }
    }
    
    async uploadChunk(chunk, chunkIndex, totalChunks, sessionId, filename) {
        const formData = new FormData();
        formData.append('chunk', chunk);
        formData.append('chunkIndex', chunkIndex);
        formData.append('totalChunks', totalChunks);
        formData.append('sessionId', sessionId);
        formData.append('filename', filename);
        
        let retries = 0;
        while (retries < this.maxRetries) {
            try {
                const response = await fetch('/transcricao-video/upload-chunk', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                if (result.success) {
                    return result;
                } else {
                    throw new Error(result.error || 'Erro no upload do chunk');
                }
                
            } catch (error) {
                retries++;
                console.warn(`Tentativa ${retries}/${this.maxRetries} falhou para chunk ${chunkIndex}:`, error);
                
                if (retries >= this.maxRetries) {
                    throw new Error(`Falha após ${this.maxRetries} tentativas no chunk ${chunkIndex}: ${error.message}`);
                }
                
                // Esperar antes de tentar novamente (backoff exponencial)
                await this.delay(Math.pow(2, retries) * 1000);
            }
        }
    }
    
    async finalizeUpload(sessionId, filename) {
        try {
            console.log(`🎯 Finalizando upload - Sessão: ${sessionId}, Arquivo: ${filename}`);
            
            const response = await fetch('/transcricao-video/finalize-upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    sessionId: sessionId,
                    filename: filename
                })
            });
            
            const responseData = await response.json();
            
            if (!response.ok) {
                const errorMsg = responseData.error || response.statusText;
                console.error(`❌ Erro HTTP ${response.status}:`, errorMsg);
                throw new Error(`Erro ao finalizar upload (${response.status}): ${errorMsg}`);
            }
            
            if (!responseData.success) {
                console.error('❌ Resposta de erro:', responseData);
                throw new Error(responseData.error || 'Erro desconhecido na finalização');
            }
            
            console.log('✅ Upload finalizado com sucesso:', responseData);
            return responseData;
            
        } catch (error) {
            console.error('❌ Erro na finalização do upload:', error);
            throw error;
        }
    }
    
    generateSessionId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Função global para inicializar upload em chunks
function initializeChunkedUpload() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('audio-upload');
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    
    if (!uploadArea || !fileInput) return;
    
    const uploader = new ChunkedUploader({
        chunkSize: 5 * 1024 * 1024, // 5MB chunks
        onProgress: (progress, currentChunk, totalChunks) => {
            if (progressContainer && progressBar && progressText) {
                progressContainer.style.display = 'block';
                progressBar.style.width = `${progress}%`;
                progressText.textContent = `Enviando chunk ${currentChunk}/${totalChunks} (${Math.round(progress)}%)`;
            }
        },
        onComplete: (result) => {
            console.log('Upload concluído:', result);
            if (result.success && result.transcript_id) {
                // Redirecionar para página de resultado
                window.location.href = `/transcricao-video/result/${result.transcript_id}`;
            }
        },
        onError: (error) => {
            console.error('Erro no upload:', error);
            alert(`Erro no upload: ${error.message}`);
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }
    });
    
    // Handler para upload via drag & drop
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0], uploader);
        }
    });
    
    // Handler para upload via input
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0], uploader);
        }
    });
    
    // Drag & drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
}

async function handleFileUpload(file, uploader) {
    // Validar arquivo
    const maxSize = 200 * 1024 * 1024; // 200MB
    if (file.size > maxSize) {
        alert(`Arquivo muito grande. Limite: ${maxSize / 1024 / 1024}MB`);
        return;
    }
    
    const allowedTypes = ['audio/', 'video/'];
    if (!allowedTypes.some(type => file.type.startsWith(type))) {
        alert('Apenas arquivos de áudio e vídeo são permitidos');
        return;
    }
    
    try {
        console.log(`Iniciando upload em chunks: ${file.name} (${file.size} bytes)`);
        await uploader.upload(file, '/transcricao-video/upload-chunk');
        
    } catch (error) {
        console.error('Erro no upload:', error);
        alert(`Erro no upload: ${error.message}`);
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initializeChunkedUpload);