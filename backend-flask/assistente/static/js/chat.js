/**
 * JavaScript para o módulo Assistente
 * Gerencia a interação do chat, conexão SSE, upload de arquivos e configurações
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos da página
    const chatMensagens = document.getElementById('messages');
    const formMensagem = document.getElementById('chatForm');
    const mensagemTexto = document.getElementById('userInput');
    const btnEnviar = formMensagem ? formMensagem.querySelector('button[type="submit"]') : null;
    const btnUpload = document.getElementById('btnUpload');
    const uploadArea = document.getElementById('uploadArea');
    const dropZone = document.getElementById('dropZone');
    const fileUpload = document.getElementById('fileUpload');
    const btnLimpar = document.getElementById('btnLimpar');
    const formConfiguracoes = document.getElementById('formConfiguracoes');
    const toggleUseDb = document.getElementById('useDb');
    const toggleUseWeb = document.getElementById('useWeb');
    
    // Campos ocultos
    const conversaId = document.getElementById('conversaId');
    const modeloLlm = document.getElementById('modeloLlm');
    const personalidade = document.getElementById('personalidade');
    const tomVoz = document.getElementById('tomVoz');
    
    // Variáveis para controle do chat
    let isWaitingResponse = false;
    let currentResponseText = '';
    let currentResponseElement = null;
    
    // SSE foi removido para simplificar a implementação
    let eventSourceConnected = false;
    
    // Substituímos o SSE por requisições AJAX padrão
    console.log('Usando comunicação AJAX para respostas');
    
                location.reload(); // Recarrega a página para restabelecer a conexão
            }
        }, 5000);
    };
    
    // Escuta eventos do tipo 'assistente_update'
    eventSource.addEventListener('assistente_update', function(e) {
        if (!isWaitingResponse) return;
        
        try {
            const data = JSON.parse(e.data);
            
            switch (data.event) {
                case 'start':
                    // Inicializa container para a resposta
                    startResponseContainer();
                    break;
                    
                case 'token':
                    // Adiciona um token à resposta atual
                    appendResponseToken(data.data);
                    break;
                    
                case 'end':
                    // Finaliza a resposta e formata o resultado
                    finishResponseContainer();
                    break;
                    
                case 'error':
                    // Mostra erro na resposta
                    showErrorInResponse(data.data);
                    break;
            }
        } catch (error) {
            console.error('Erro ao processar evento SSE:', error);
        }
    });
    
    // Função para inicializar o container para a resposta
    function startResponseContainer() {
        // Cria elemento de resposta do assistente
        const messageElement = document.createElement('div');
        messageElement.className = 'message message-assistant';
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        
        const infoElement = document.createElement('div');
        infoElement.className = 'message-info';
        infoElement.innerHTML = '<small class="text-muted">' + getCurrentTimeFormatted() + '</small>';
        
        messageElement.appendChild(contentElement);
        messageElement.appendChild(infoElement);
        
        // Adiciona ao chat e scroll para o final
        chatMensagens.appendChild(messageElement);
        scrollToBottom();
        
        // Armazena referências
        currentResponseElement = contentElement;
        currentResponseText = '';
    }
    
    // Função para adicionar um token à resposta
    function appendResponseToken(token) {
        if (!currentResponseElement) return;
        
        currentResponseText += token;
        // Converte Markdown para HTML
        currentResponseElement.innerHTML = marked.parse(currentResponseText);
        scrollToBottom();
    }
    
    // Função para finalizar a resposta
    function finishResponseContainer() {
        if (!currentResponseElement) return;
        
        // Remove indicador de digitação
        const typingIndicator = currentResponseElement.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        // Formata a resposta final
        currentResponseElement.innerHTML = marked.parse(currentResponseText);
        
        // Destaca blocos de código, se existirem
        highlightCodeBlocks();
        
        // Scroll para o final e reset
        scrollToBottom();
        isWaitingResponse = false;
        btnEnviar.disabled = false;
        mensagemTexto.disabled = false;
        mensagemTexto.focus();
        
        currentResponseElement = null;
        currentResponseText = '';
    }
    
    // Função para mostrar erro na resposta
    function showErrorInResponse(errorMessage) {
        if (!currentResponseElement) {
            startResponseContainer();
        }
        
        currentResponseElement.innerHTML = `<div class="alert alert-danger">Erro: ${errorMessage}</div>`;
        isWaitingResponse = false;
        btnEnviar.disabled = false;
        mensagemTexto.disabled = false;
        currentResponseElement = null;
    }
    
    // Função para destacar blocos de código
    function highlightCodeBlocks() {
        // Se você estiver usando uma biblioteca de syntax highlighting como Prism.js ou highlight.js
        // Coloque a lógica de highlight aqui
    }
    
    // Função para obter o horário atual formatado
    function getCurrentTimeFormatted() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Função para rolar o chat para o final
    function scrollToBottom() {
        chatMensagens.scrollTop = chatMensagens.scrollHeight;
    }
    
    // Handler do envio de mensagem
    if (formMensagem) {
        formMensagem.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const mensagem = mensagemTexto.value.trim();
            if (!mensagem || isWaitingResponse) return;
            
            // Adiciona a mensagem do usuário ao chat
            const messageElement = document.createElement('div');
            messageElement.className = 'message message-user';
            
            const contentElement = document.createElement('div');
            contentElement.className = 'message-content';
            contentElement.textContent = mensagem;
            
            const infoElement = document.createElement('div');
            infoElement.className = 'message-info';
            infoElement.innerHTML = '<small class="text-muted">' + getCurrentTimeFormatted() + '</small>';
            
            messageElement.appendChild(contentElement);
            messageElement.appendChild(infoElement);
            
            chatMensagens.appendChild(messageElement);
            scrollToBottom();
            
            // Limpa o campo de texto e desabilita para esperar resposta
            mensagemTexto.value = '';
            mensagemTexto.disabled = true;
            if (btnEnviar) btnEnviar.disabled = true;
            isWaitingResponse = true;
        
        // Obtém opções de consulta (RAG e Web)
        const useDb = toggleUseDb.checked;
        const useWeb = toggleUseWeb.checked;
        
        // Prepara dados para envio
        const formData = new FormData();
        formData.append('conversa_id', conversaId.value);
        formData.append('mensagem', mensagem);
        formData.append('modelo_llm', modeloLlm.value);
        formData.append('personalidade', personalidade.value);
        formData.append('tom_voz', tomVoz.value);
        formData.append('use_db', useDb);
        formData.append('use_web', useWeb);
        
        // Envia a mensagem para o servidor
        fetch('/assistente/chat/enviar', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                showErrorInResponse(data.error || 'Erro ao processar mensagem');
                isWaitingResponse = false;
                btnEnviar.disabled = false;
                mensagemTexto.disabled = false;
            }
        })
        .catch(error => {
            console.error('Erro ao enviar mensagem:', error);
            showErrorInResponse('Erro de conexão');
            isWaitingResponse = false;
            btnEnviar.disabled = false;
            mensagemTexto.disabled = false;
        });
    });
    
    // Manipulação de upload de arquivos
    if (btnUpload && uploadArea && dropZone && fileUpload) {
        // Toggle da área de upload
        btnUpload.addEventListener('click', function() {
            uploadArea.style.display = uploadArea.style.display === 'none' ? 'block' : 'none';
        });
        
        // Seleção de arquivo via clique
        dropZone.addEventListener('click', function() {
            fileUpload.click();
        });
        
        // Quando um arquivo é selecionado
        fileUpload.addEventListener('change', function() {
            if (this.files.length > 0) {
                uploadFile(this.files[0]);
            }
        });
        
        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.add('active');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.remove('active');
            }, false);
        });
        
        dropZone.addEventListener('drop', function(e) {
            const file = e.dataTransfer.files[0];
            if (file) {
                uploadFile(file);
            }
        }, false);
        
        // Função para upload de arquivo
        function uploadFile(file) {
            if (!conversaId.value) {
                alert('Erro: ID da conversa não encontrado');
                return;
            }
            
            const allowedTypes = [
                'text/plain', 'application/pdf', 'image/png', 'image/jpeg',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ];
            
            if (!allowedTypes.includes(file.type)) {
                alert('Tipo de arquivo não suportado. Por favor, envie arquivos .txt, .pdf, .docx, .png ou .jpg');
                return;
            }
            
            // Prepara dados para upload
            const formData = new FormData();
            formData.append('file', file);
            formData.append('conversa_id', conversaId.value);
            
            // Atualiza a interface para mostrar progresso
            dropZone.innerHTML = '<p>Enviando arquivo...</p><div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div></div>';
            
            // Envia o arquivo
            fetch('/assistente/chat/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Oculta a área de upload e restaura
                    uploadArea.style.display = 'none';
                    dropZone.innerHTML = '<p>Arraste arquivos aqui ou clique para selecionar</p><small class="text-muted">Formatos suportados: TXT, PDF, DOCX, PNG, JPG</small>';
                    
                    // Adiciona mensagem sobre o upload
                    const messageElement = document.createElement('div');
                    messageElement.className = 'message message-user';
                    
                    const contentElement = document.createElement('div');
                    contentElement.className = 'message-content';
                    contentElement.innerHTML = `<p>Arquivo enviado: <strong>${data.filename}</strong></p>`;
                    
                    const infoElement = document.createElement('div');
                    infoElement.className = 'message-info';
                    infoElement.innerHTML = '<small class="text-muted">' + getCurrentTimeFormatted() + '</small>';
                    
                    messageElement.appendChild(contentElement);
                    messageElement.appendChild(infoElement);
                    
                    chatMensagens.appendChild(messageElement);
                    scrollToBottom();
                } else {
                    alert('Erro ao enviar arquivo: ' + data.error);
                    dropZone.innerHTML = '<p>Arraste arquivos aqui ou clique para selecionar</p><small class="text-muted">Formatos suportados: TXT, PDF, DOCX, PNG, JPG</small>';
                }
            })
            .catch(error => {
                console.error('Erro ao fazer upload:', error);
                alert('Erro de conexão ao enviar arquivo');
                dropZone.innerHTML = '<p>Arraste arquivos aqui ou clique para selecionar</p><small class="text-muted">Formatos suportados: TXT, PDF, DOCX, PNG, JPG</small>';
            });
        }
    }
    
    // Botão Limpar Conversa
    if (btnLimpar) {
        btnLimpar.addEventListener('click', function() {
            const conversaId = this.getAttribute('data-conversa-id');
            if (!conversaId) return;
            
            if (confirm('Tem certeza que deseja limpar esta conversa?')) {
                fetch('/assistente/chat/limpar/' + conversaId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Recarrega a página após limpar
                        window.location.reload();
                    } else {
                        alert('Erro ao limpar conversa: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Ocorreu um erro ao processar sua solicitação.');
                });
            }
        });
    }
    
    // Formulário de configurações
    if (formConfiguracoes) {
        formConfiguracoes.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!conversaId.value) {
                alert('Erro: ID da conversa não encontrado');
                return;
            }
            
            // Obtém valores do formulário
            const configModeloLlm = document.getElementById('configModeloLlm').value;
            const configPersonalidade = document.getElementById('configPersonalidade').value;
            const configTomVoz = document.getElementById('configTomVoz').value;
            
            // Atualiza os campos ocultos
            modeloLlm.value = configModeloLlm;
            personalidade.value = configPersonalidade;
            tomVoz.value = configTomVoz;
            
            // Prepara dados para envio
            const formData = new FormData();
            formData.append('conversa_id', conversaId.value);
            formData.append('modelo_llm', configModeloLlm);
            formData.append('personalidade', configPersonalidade);
            formData.append('tom_voz', configTomVoz);
            
            // Envia a atualização para o servidor
            fetch('/assistente/chat/atualizar_config', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Fecha o modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('configuracoesModal'));
                    modal.hide();
                    
                    // Adiciona mensagem de sistema
                    const messageElement = document.createElement('div');
                    messageElement.className = 'alert alert-info text-center my-3';
                    messageElement.innerHTML = 'Configurações atualizadas';
                    
                    chatMensagens.appendChild(messageElement);
                    scrollToBottom();
                    
                    // Remove a mensagem após alguns segundos
                    setTimeout(() => {
                        messageElement.remove();
                    }, 3000);
                } else {
                    alert('Erro ao atualizar configurações: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Ocorreu um erro ao processar sua solicitação.');
            });
        });
    }
    
    // Inicialização
    scrollToBottom();
    if (mensagemTexto) {
        // Auto-resize do textarea
        mensagemTexto.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Submit com Enter (mas não com Shift+Enter)
        mensagemTexto.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                formMensagem.dispatchEvent(new Event('submit'));
            }
        });
    }
});