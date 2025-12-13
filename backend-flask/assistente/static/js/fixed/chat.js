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
    
    // Elementos de configuração
    const useWebToggle = document.getElementById('usar_pesquisa_web');
    const useDocsToggle = document.getElementById('usar_documentos');
    const modeloSelect = document.getElementById('modelo_llm');
    const personalidadeSelect = document.getElementById('personalidade');
    const tomVozSelect = document.getElementById('tom_voz');
    
    // Estado do chat
    let isWaitingResponse = false;
    
    // Obter hora atual formatada
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
            // Aqui poderia usar uma biblioteca como marked.js para renderizar markdown
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
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = userInput.value.trim();
            if (!message || isWaitingResponse) return;
            
            // Adicionar mensagem do usuário ao chat
            addUserMessage(message);
            
            // Limpar campo de entrada e mostrar estado de espera
            userInput.value = '';
            isWaitingResponse = true;
            
            // Preparar área para resposta do assistente
            const responseContent = addAssistantMessage('');
            
            // Coletar dados do formulário
            const formData = new FormData();
            formData.append('content', message);
            formData.append('modelo_llm', modeloSelect ? modeloSelect.value : 'gpt-4o');
            formData.append('personalidade', personalidadeSelect ? personalidadeSelect.value : 'advogado');
            formData.append('tom_voz', tomVozSelect ? tomVozSelect.value : 'formal');
            formData.append('usar_pesquisa_web', useWebToggle ? useWebToggle.checked : false);
            formData.append('usar_documentos', useDocsToggle ? useDocsToggle.checked : false);
            
            // Simular uma resposta do assistente
            // Em produção, isso seria substituído pela chamada real à API
            
            // Enviar requisição para o servidor
            fetch('/assistente/chat/enviar', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualizar o conteúdo da resposta
                    if (responseContent) {
                        responseContent.textContent = data.response || "Entendi sua mensagem. Como posso ajudar?";
                    }
                } else {
                    // Mostrar erro
                    if (responseContent) {
                        responseContent.innerHTML = `<div class="alert alert-danger">Erro: ${data.error || 'Ocorreu um erro ao processar sua mensagem.'}</div>`;
                    }
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                if (responseContent) {
                    responseContent.innerHTML = '<div class="alert alert-danger">Erro de conexão. Por favor, tente novamente.</div>';
                }
            })
            .finally(() => {
                // Independentemente do resultado, habilitar o formulário novamente
                isWaitingResponse = false;
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
                
                // Enviar arquivo para o servidor
                fetch('/assistente/chat/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Mostrar confirmação
                        addAssistantMessage(`Arquivo "${file.name}" recebido. Você pode fazer perguntas sobre o conteúdo deste documento.`);
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