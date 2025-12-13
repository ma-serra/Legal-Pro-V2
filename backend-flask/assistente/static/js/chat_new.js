// chat_new.js - Versão reescrita para interface com configurações visíveis
document.addEventListener('DOMContentLoaded', function() {
    // Elementos principais
    const chatForm = document.getElementById('chatForm');
    const mensagemInput = document.getElementById('mensagem');
    const chatMensagens = document.getElementById('chatMensagens');
    const btnLimpar = document.getElementById('btnLimpar');
    const configForm = document.getElementById('configForm');
    const btnEnviarArquivo = document.getElementById('btnEnviarArquivo');
    const arquivoInput = document.getElementById('arquivo');
    const uploadStatus = document.getElementById('uploadStatus');
    const tipoMensagemSelecao = document.getElementById('tipoMensagem');
    const useDb = document.getElementById('useDb');
    const useWeb = document.getElementById('useWeb');
    
    // Comportamento do formulário de chat
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const mensagem = mensagemInput.value.trim();
            if (!mensagem) return;
            
            // Adiciona mensagem do usuário ao chat
            adicionarMensagem('user', mensagem);
            mensagemInput.value = '';
            mensagemInput.style.height = 'auto';
            
            // Exibe indicador de digitação
            exibirIndicadorDigitacao();
            
            // Configuração para a consulta
            const tipoMensagem = tipoMensagemSelecao ? tipoMensagemSelecao.value : 'padrao';
            const useDbValue = useDb ? useDb.checked : true;
            const useWebValue = useWeb ? useWeb.checked : false;
            const conversaId = document.getElementById('conversaId').value;
            
            // Envia mensagem para o servidor via AJAX
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/assistente/enviar_mensagem');
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                // Remove indicador de digitação
                removerIndicadorDigitacao();
                
                if (xhr.status === 200) {
                    try {
                        const resposta = JSON.parse(xhr.responseText);
                        
                        if (resposta.erro) {
                            // Exibe mensagem de erro
                            adicionarMensagem('system', `Erro: ${resposta.erro}`, 'erro');
                        } else if (resposta.resposta) {
                            // Adiciona resposta do assistente
                            adicionarMensagem('assistant', resposta.resposta, null, resposta.fontes);
                            
                            // Atualiza título da conversa se necessário
                            if (resposta.titulo && resposta.titulo !== 'Nova Conversa') {
                                document.querySelector('.card-header h5').textContent = resposta.titulo;
                            }
                        }
                    } catch (error) {
                        console.error('Erro ao processar resposta:', error);
                        adicionarMensagem('system', 'Erro ao processar resposta do servidor.', 'erro');
                    }
                } else {
                    adicionarMensagem('system', 'Erro na comunicação com o servidor.', 'erro');
                }
            };
            
            xhr.onerror = function() {
                removerIndicadorDigitacao();
                adicionarMensagem('system', 'Falha na comunicação com o servidor.', 'erro');
            };
            
            xhr.send(JSON.stringify({
                mensagem: mensagem,
                tipo_mensagem: tipoMensagem,
                conversa_id: conversaId,
                use_db: useDbValue,
                use_web: useWebValue
            }));
        });
    }
    
    // Upload de arquivo
    if (btnEnviarArquivo && arquivoInput) {
        btnEnviarArquivo.addEventListener('click', function() {
            arquivoInput.click();
        });
        
        arquivoInput.addEventListener('change', function() {
            if (arquivoInput.files.length > 0) {
                const arquivo = arquivoInput.files[0];
                
                if (arquivo.size > 10 * 1024 * 1024) { // 10MB
                    alert('O arquivo é muito grande. Tamanho máximo: 10MB.');
                    arquivoInput.value = '';
                    return;
                }
                
                // Exibe status de upload
                if (uploadStatus) {
                    uploadStatus.textContent = 'Enviando arquivo...';
                    uploadStatus.style.display = 'block';
                }
                
                const formData = new FormData();
                formData.append('arquivo', arquivo);
                formData.append('conversa_id', document.getElementById('conversaId').value);
                
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/assistente/upload_arquivo');
                
                xhr.onload = function() {
                    if (uploadStatus) {
                        uploadStatus.style.display = 'none';
                    }
                    
                    if (xhr.status === 200) {
                        try {
                            const resposta = JSON.parse(xhr.responseText);
                            
                            if (resposta.erro) {
                                adicionarMensagem('system', `Erro: ${resposta.erro}`, 'erro');
                            } else {
                                adicionarMensagem('user', `Arquivo enviado: ${arquivo.name}`, 'arquivo');
                                adicionarMensagem('assistant', resposta.resposta);
                            }
                        } catch (error) {
                            console.error('Erro ao processar resposta:', error);
                            adicionarMensagem('system', 'Erro ao processar resposta do servidor.', 'erro');
                        }
                    } else {
                        adicionarMensagem('system', 'Erro ao enviar arquivo.', 'erro');
                    }
                    
                    arquivoInput.value = '';
                };
                
                xhr.onerror = function() {
                    if (uploadStatus) {
                        uploadStatus.style.display = 'none';
                    }
                    adicionarMensagem('system', 'Falha na comunicação com o servidor.', 'erro');
                    arquivoInput.value = '';
                };
                
                xhr.send(formData);
            }
        });
    }
    
    // Configuração do formulário de configurações
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const conversaId = document.getElementById('conversaId').value;
            const modeloLlm = document.getElementById('modeloLlm').value;
            const personalidade = document.getElementById('personalidade').value;
            const tomVoz = document.getElementById('tomVoz').value;
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/assistente/atualizar_config');
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    // Exibe mensagem de sucesso
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i> Configurações atualizadas com sucesso!';
                    chatMensagens.appendChild(alertDiv);
                    chatMensagens.scrollTop = chatMensagens.scrollHeight;
                    
                    // Remove alerta após alguns segundos
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 3000);
                    
                    // Atualiza informações no cabeçalho
                    if (conversaId) {
                        const infoHeader = document.querySelector('.card-header small.text-muted');
                        if (infoHeader) {
                            const modeloTexto = modeloLlm.split('/')[1];
                            const personalidadeTexto = personalidade.charAt(0).toUpperCase() + personalidade.slice(1);
                            const tomVozTexto = tomVoz.charAt(0).toUpperCase() + tomVoz.slice(1);
                            infoHeader.textContent = `${modeloTexto} | ${personalidadeTexto} | ${tomVozTexto}`;
                        }
                    }
                } else {
                    alert('Erro ao atualizar configurações.');
                }
            };
            
            xhr.onerror = function() {
                alert('Falha na comunicação com o servidor.');
            };
            
            xhr.send(JSON.stringify({
                conversa_id: conversaId,
                modelo_llm: modeloLlm,
                personalidade: personalidade,
                tom_voz: tomVoz
            }));
        });
    }
    
    // Botão de limpar conversa
    if (btnLimpar) {
        btnLimpar.addEventListener('click', function() {
            const conversaId = btnLimpar.getAttribute('data-conversa-id');
            if (!conversaId) return;
            
            if (confirm('Tem certeza que deseja limpar esta conversa? Todas as mensagens serão apagadas.')) {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/assistente/limpar_conversa');
                xhr.setRequestHeader('Content-Type', 'application/json');
                
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        // Limpa a área de mensagens
                        chatMensagens.innerHTML = '';
                        
                        // Adiciona mensagem de boas-vindas
                        adicionarMensagem('assistant', 'Conversa limpa. Como posso ajudar?');
                    } else {
                        alert('Erro ao limpar conversa.');
                    }
                };
                
                xhr.onerror = function() {
                    alert('Falha na comunicação com o servidor.');
                };
                
                xhr.send(JSON.stringify({
                    conversa_id: conversaId
                }));
            }
        });
    }
    
    // Autoajuste da altura do campo de texto
    if (mensagemInput) {
        mensagemInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Atalho Ctrl+Enter para enviar
        mensagemInput.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    // Exibe as mensagens iniciais se existirem
    if (chatMensagens) {
        chatMensagens.scrollTop = chatMensagens.scrollHeight;
    }
});

// Funções auxiliares

// Adiciona uma mensagem no chat
function adicionarMensagem(remetente, texto, tipo, fontes) {
    const chatMensagens = document.getElementById('chatMensagens');
    if (!chatMensagens) return;
    
    const mensagemDiv = document.createElement('div');
    mensagemDiv.className = `mensagem ${remetente}`;
    
    // Adiciona ícone apropriado
    let icone = '';
    if (remetente === 'user') {
        icone = '<i class="fas fa-user"></i>';
    } else if (remetente === 'assistant') {
        icone = '<i class="fas fa-robot"></i>';
    } else if (remetente === 'system') {
        icone = '<i class="fas fa-exclamation-circle"></i>';
    }
    
    // Formatação do conteúdo
    let conteudo = '';
    
    if (tipo === 'erro') {
        conteudo = `<div class="alert alert-danger">${texto}</div>`;
    } else if (tipo === 'arquivo') {
        conteudo = `<div class="arquivo"><i class="fas fa-file me-2"></i>${texto}</div>`;
    } else {
        // Formata o texto com Markdown se for do assistente
        if (remetente === 'assistant' && window.marked) {
            conteudo = marked.parse(texto);
            
            // Aplica highlight em blocos de código se disponível
            if (window.hljs) {
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            }
        } else {
            conteudo = `<p>${texto}</p>`;
        }
    }
    
    // Adiciona fontes se fornecidas
    let fontesHtml = '';
    if (fontes && fontes.length > 0) {
        fontesHtml = '<div class="fontes mt-2"><h6>Fontes:</h6><ul>';
        fontes.forEach(fonte => {
            fontesHtml += `<li><a href="${fonte.url}" target="_blank">${fonte.titulo || fonte.url}</a></li>`;
        });
        fontesHtml += '</ul></div>';
    }
    
    mensagemDiv.innerHTML = `
        <div class="mensagem-header">
            ${icone} <span class="remetente">${remetente === 'user' ? 'Você' : remetente === 'assistant' ? 'Assistente' : 'Sistema'}</span>
        </div>
        <div class="mensagem-conteudo">
            ${conteudo}
            ${fontesHtml}
        </div>
    `;
    
    chatMensagens.appendChild(mensagemDiv);
    chatMensagens.scrollTop = chatMensagens.scrollHeight;
}

// Exibe indicador de digitação
function exibirIndicadorDigitacao() {
    const chatMensagens = document.getElementById('chatMensagens');
    if (!chatMensagens) return;
    
    // Remove qualquer indicador existente
    removerIndicadorDigitacao();
    
    // Cria novo indicador
    const indicador = document.createElement('div');
    indicador.id = 'typingIndicator';
    indicador.className = 'mensagem assistant';
    indicador.innerHTML = `
        <div class="mensagem-header">
            <i class="fas fa-robot"></i> <span class="remetente">Assistente</span>
        </div>
        <div class="mensagem-conteudo">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMensagens.appendChild(indicador);
    chatMensagens.scrollTop = chatMensagens.scrollHeight;
}

// Remove indicador de digitação
function removerIndicadorDigitacao() {
    const indicador = document.getElementById('typingIndicator');
    if (indicador) {
        indicador.remove();
    }
}