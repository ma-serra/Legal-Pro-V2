// Sistema de Upload e Análise Multi-Agente
document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando sistema...');
    
    // Elementos principais
    const uploadArea = document.getElementById('areaUpload');
    const fileInput = document.getElementById('documento');
    const textArea = document.getElementById('texto');
    const form = document.getElementById('formAnaliseExpandida');
    const btnExecutar = document.getElementById('btnExecutar');
    const resumoSelecao = document.getElementById('resumoSelecao');
    
    // Sistema de Upload
    if (uploadArea && fileInput) {
        console.log('Configurando sistema de upload...');
        
        // Clique na área
        uploadArea.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Clique detectado');
            fileInput.click();
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            uploadArea.style.background = 'linear-gradient(135deg, #c3e9ff 0%, #90cdf4 100%)';
            uploadArea.style.borderColor = '#0056b3';
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.style.background = 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)';
            uploadArea.style.borderColor = '#007bff';
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.background = 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)';
            uploadArea.style.borderColor = '#007bff';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                console.log('Arquivo arrastado:', files[0].name);
                processarArquivo(files[0]);
            }
        });
        
        // Input change
        fileInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files.length > 0) {
                console.log('Arquivo selecionado:', e.target.files[0].name);
                processarArquivo(e.target.files[0]);
            }
        });
    }
    
    function processarArquivo(file) {
        console.log('Processando arquivo:', file.name);
        
        if (textArea) {
            textArea.value = 'Processando arquivo: ' + file.name + '...';
        }
        
        const formData = new FormData();
        formData.append('documento', file);
        
        fetch('/processar-documento', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Resposta recebida:', data);
            if (data.success && textArea) {
                textArea.value = data.texto_extraido || 'Texto extraído com sucesso';
                verificarFormulario();
            } else {
                if (textArea) {
                    textArea.value = 'Erro: ' + (data.error || 'Erro desconhecido');
                }
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            if (textArea) {
                textArea.value = 'Erro de conexão ao processar arquivo.';
            }
        });
    }
    
    // Sistema de seleção de agentes
    const checkboxes = document.querySelectorAll('input[name="agentes_selecionados"], input[name="agentes_revisores"]');
    
    function atualizarResumo() {
        const selecionados = document.querySelectorAll('input[name="agentes_selecionados"]:checked, input[name="agentes_revisores"]:checked');
        
        if (resumoSelecao) {
            if (selecionados.length > 0) {
                resumoSelecao.innerHTML = selecionados.length + ' agente(s) selecionado(s)';
            } else {
                resumoSelecao.innerHTML = 'Nenhum agente selecionado';
            }
        }
        
        verificarFormulario();
    }
    
    function verificarFormulario() {
        const temTexto = textArea && textArea.value.trim().length > 0 && !textArea.value.includes('Processando');
        const temAgentes = document.querySelectorAll('input[name="agentes_selecionados"]:checked, input[name="agentes_revisores"]:checked').length > 0;
        
        if (btnExecutar) {
            btnExecutar.disabled = !(temTexto && temAgentes);
            console.log('Formulário válido:', temTexto && temAgentes);
        }
    }
    
    // Event listeners para checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', atualizarResumo);
    });
    
    // Botões de controle
    const selecionarTodos = document.getElementById('selecionarTodos');
    const limparSelecao = document.getElementById('limparSelecao');
    
    if (selecionarTodos) {
        selecionarTodos.addEventListener('click', function() {
            const activeTab = document.querySelector('.tab-pane.active');
            if (activeTab) {
                const checkboxesTab = activeTab.querySelectorAll('input[type="checkbox"]');
                checkboxesTab.forEach(cb => cb.checked = true);
                atualizarResumo();
            }
        });
    }
    
    if (limparSelecao) {
        limparSelecao.addEventListener('click', function() {
            checkboxes.forEach(cb => cb.checked = false);
            atualizarResumo();
        });
    }
    
    // Submissão do formulário
    if (form) {
        form.addEventListener('submit', function(e) {
            const temTexto = textArea && textArea.value.trim().length > 0 && !textArea.value.includes('Processando');
            const temAgentes = document.querySelectorAll('input[name="agentes_selecionados"]:checked, input[name="agentes_revisores"]:checked').length > 0;
            
            if (!temTexto) {
                e.preventDefault();
                alert('Por favor, carregue um documento primeiro.');
                return false;
            }
            
            if (!temAgentes) {
                e.preventDefault();
                alert('Por favor, selecione pelo menos um agente.');
                return false;
            }
            
            console.log('Enviando formulário...');
            return true;
        });
    }
    
    // Inicializar
    atualizarResumo();
    console.log('Sistema configurado com sucesso');
});