/**
 * JavaScript corrigido para o módulo Assistente
 * Mantém o campo de mensagem visível após o envio
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos da página
    const messages = document.getElementById('messages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const fileUpload = document.getElementById('fileUpload');
    
    // Configurações do chat
    const conversaId = document.querySelector('input[name="conversa_id"]') 
        ? document.querySelector('input[name="conversa_id"]').value 
        : null;
    
    // Variáveis para controle do chat
    let isWaitingResponse = false;
    
    // Função para obter o horário atual formatado
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Função para rolar para o final do chat
    function scrollToBottom() {
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    }
    
    // Adicionar mensagem do usuário ao chat
    function addUserMessage(text) {
        if (!messages) return;
        
        // Remove a mensagem de boas vindas se existir
        const emptyChat = messages.querySelector('.empty-chat-message');
        if (emptyChat) {
            emptyChat.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-user';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'message-info';
        infoDiv.innerHTML = `<small class="text-muted">${getCurrentTime()}</small>`;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(infoDiv);
        messages.appendChild(messageDiv);
        
        scrollToBottom();
    }
    
    // Adicionar mensagem do assistente ao chat
    function addAssistantMessage(text) {
        if (!messages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Se o texto for vazio, mostrar indicador de digitação
        if (!text) {
            contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        } else {
            contentDiv.textContent = text;
        }
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'message-info';
        infoDiv.innerHTML = `<small class="text-muted">${getCurrentTime()}</small>`;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(infoDiv);
        messages.appendChild(messageDiv);
        
        scrollToBottom();
        
        return contentDiv; // Retorna o div de conteúdo para atualização posterior
    }
    
    // Manipular envio do formulário
    if (chatForm && userInput) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = userInput.value.trim();
            if (!message || isWaitingResponse) return;
            
            // Adicionar mensagem do usuário ao chat
            addUserMessage(message);
            
            // Preparar área para resposta do assistente
            const responseContent = addAssistantMessage('');
            
            // Coletar dados do formulário
            const formData = new FormData();
            formData.append('conversa_id', conversaId);
            formData.append('mensagem', message);
            
            // Obter configurações do assistente, se disponíveis
            const modeloLlm = document.getElementById('modelo_llm');
            const personalidade = document.getElementById('personalidade');
            const tomVoz = document.getElementById('tom_voz');
            const useWeb = document.getElementById('usar_pesquisa_web');
            const useDocs = document.getElementById('usar_documentos');
            
            if (modeloLlm) formData.append('modelo_llm', modeloLlm.value);
            if (personalidade) formData.append('personalidade', personalidade.value);
            if (tomVoz) formData.append('tom_voz', tomVoz.value);
            if (useWeb) formData.append('use_web', useWeb.checked);
            if (useDocs) formData.append('use_db', useDocs.checked);
            
            // Limpar campo de entrada
            userInput.value = '';
            
            // IMPORTANTE: NÃO vamos desabilitar o campo de mensagem
            // Apenas definir o estado de espera
            isWaitingResponse = true;
            
            // Enviar a mensagem via AJAX
            fetch('/assistente/chat/enviar', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Remover indicador de digitação
                if (responseContent.querySelector('.typing-indicator')) {
                    responseContent.querySelector('.typing-indicator').remove();
                }
                
                if (data.success) {
                    // Mostrar a resposta
                    responseContent.textContent = data.response || 'Não foi possível obter uma resposta.';
                } else {
                    // Mostrar erro
                    responseContent.innerHTML = `<div class="alert alert-danger">${data.error || 'Erro ao processar mensagem'}</div>`;
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                if (responseContent) {
                    responseContent.innerHTML = '<div class="alert alert-danger">Erro de conexão. Por favor, tente novamente.</div>';
                }
            })
            .finally(() => {
                // Finalizar estado de espera
                isWaitingResponse = false;
                scrollToBottom();
            });
        });
    }
    
    // Manipular o upload de arquivos
    if (fileUpload) {
        fileUpload.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                
                // Adicionar mensagem sobre o arquivo
                addUserMessage(`Arquivo enviado: ${file.name}`);
                
                // Preparar para upload
                const formData = new FormData();
                formData.append('file', file);
                formData.append('conversa_id', conversaId);
                
                // Enviar arquivo para o servidor
                fetch('/assistente/chat/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Mostrar confirmação
                        addAssistantMessage(`Arquivo "${data.filename}" recebido. Você pode fazer perguntas sobre o conteúdo deste documento.`);
                    } else {
                        // Mostrar erro
                        addAssistantMessage(`Erro ao processar arquivo: ${data.error || 'Formato não suportado.'}`);
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    addAssistantMessage('Erro ao enviar arquivo. Por favor, tente novamente.');
                });
            }
        });
    }
});