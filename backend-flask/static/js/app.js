// Funções de utilidade
function initTooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Verifica automaticamente o tema do sistema operacional para texto
function initTextTheme() {
  // Verifica se o usuário prefere o tema escuro
  const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Encontra todos os elementos pre que estão em áreas de visualização de texto
  const textPreviewElements = document.querySelectorAll('.text-original-preview pre, .resultado-texto pre, .texto-original, pre.text-wrap, pre[style*="max-height"]');
  
  // Aplica o tema apropriado - fundo escuro para quem prefere tema escuro
  if (prefersDarkMode) {
    textPreviewElements.forEach(el => {
      el.classList.remove('bg-light');
      el.classList.add('pre-dark');
    });
  }
  
  // Procura por elementos pre em fundos escuros e aplica cor branca ao texto
  const darkBackgroundElements = document.querySelectorAll('.bg-dark, .bg-primary, .bg-secondary, .bg-navy, .dark-bg, [style*="background-color: #1d2733"]');
  darkBackgroundElements.forEach(darkElem => {
    const preElements = darkElem.querySelectorAll('pre');
    preElements.forEach(pre => {
      pre.style.color = '#ffffff';
    });
  });
  
  // Detecta especificamente elementos pre dentro de fundos escuros
  // como o da imagem compartilhada
  const allPreElements = document.querySelectorAll('pre');
  allPreElements.forEach(pre => {
    // Verifica se o elemento está em um fundo escuro
    const parentBgColor = getComputedStyle(pre.parentElement).backgroundColor;
    const preBgColor = getComputedStyle(pre).backgroundColor;
    
    // Cores escuras comuns em RGB
    const darkColors = [
      'rgb(29, 39, 51)', // #1d2733
      'rgb(30, 35, 48)', // #1e2330
      'rgb(18, 18, 18)', // #121212
      'rgb(45, 45, 45)', // #2d2d2d
      'rgb(33, 37, 41)', // #212529
      'rgb(52, 58, 64)', // #343a40
      'rgba(0, 0, 0,'     // qualquer rgba com preto
    ];
    
    // Verificar se a cor de fundo é escura
    const isDarkBg = darkColors.some(color => 
      parentBgColor.startsWith(color) || preBgColor.startsWith(color)
    );
    
    if (isDarkBg) {
      pre.style.color = '#ffffff';
      pre.setAttribute('data-color', 'dark');
    }
  });
  
  // Adiciona botão de alternância para cada área de texto quando possível
  const textAreas = document.querySelectorAll('.text-original-preview, .resultado-texto');
  textAreas.forEach(area => {
    // Apenas adiciona se encontrou um elemento pre filho
    const preElem = area.querySelector('pre');
    if (preElem) {
      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'btn btn-sm theme-toggle position-absolute top-0 end-0 m-2';
      toggleBtn.innerHTML = '<i class="fas fa-adjust"></i>';
      toggleBtn.title = 'Alternar tema claro/escuro';
      toggleBtn.onclick = function(e) {
        e.preventDefault();
        preElem.classList.toggle('bg-light');
        preElem.classList.toggle('pre-dark');
      };
      
      // Verifica se já tem posicionamento relativo para o botão posicionar corretamente
      if (getComputedStyle(area).position !== 'relative') {
        area.style.position = 'relative';
      }
      
      area.appendChild(toggleBtn);
    }
  });
}

// Inicializa todos os componentes quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
  // Inicializa tooltips
  initTooltips();
  
  // Inicializa a área de drag and drop
  initDragDropArea();
  
  // Inicializa temas de texto
  initTextTheme();
});

// Função para inicializar a área de drag and drop
function initDragDropArea() {
  const dropzone = document.getElementById('dropzone');
  const textArea = document.getElementById('texto');
  
  if (!dropzone || !textArea) return;
  
  // Impede o comportamento padrão de arrastar e soltar
  const preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  // Define as funções de arrastar
  const highlight = () => dropzone.classList.add('drag-over');
  const unhighlight = () => dropzone.classList.remove('drag-over');
  
  // Adiciona listeners para os eventos de drag and drop
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });
  
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, unhighlight, false);
  });
  
  // Função para lidar com a queda do arquivo
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      processFile(files[0]);
    }
  });
  
  // Adiciona um listener para o clique na área de drag and drop
  dropzone.addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.txt,.pdf,.docx,.html,.csv,.xlsx,.xls,.md';
    
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        processFile(e.target.files[0]);
      }
    });
    
    fileInput.click();
  });
  
  // Processa o arquivo selecionado
  function processFile(file) {
    // Cria a visualização do arquivo na área de drop
    createFilePreview(file);
    
    // Determina o tipo de arquivo
    const fileType = file.type || 'text/plain';
    const extension = file.name.split('.').pop().toLowerCase();
    
    // Verifica se é um arquivo de texto que podemos ler diretamente
    if (fileType === 'text/plain' || fileType === 'text/html' || 
        fileType === 'text/markdown' || extension === 'md' || extension === 'txt') {
      const reader = new FileReader();
      reader.addEventListener('load', (e) => {
        textArea.value = e.target.result;
        // Atualiza o status de processamento
        updateProcessingStatus('success', 'Texto extraído com sucesso');
      });
      reader.readAsText(file);
    } else {
      // Para outros formatos, extrai texto via API
      extractTextFromFile(file);
    }
  }
  
  // Cria a visualização do arquivo
  function createFilePreview(file) {
    // Limpa a área de drop
    dropzone.innerHTML = '';
    
    // Cria o elemento de preview
    const preview = document.createElement('div');
    preview.className = 'dz-preview';
    
    // Obtém o ícone baseado no tipo e extensão do arquivo
    const fileIcon = getFileIcon(file);
    
    // Cria o HTML do preview
    preview.innerHTML = `
      <div class="dz-image">
        <i class="${fileIcon} fa-3x text-primary"></i>
      </div>
      <div class="dz-details">
        <div class="dz-filename">${file.name}</div>
        <div class="dz-size">${formatFileSize(file.size)}</div>
      </div>
      <div class="dz-progress">
        <div class="dz-upload progress">
          <div class="progress-bar bg-primary" role="progressbar" style="width: 0%"></div>
        </div>
      </div>
      <div class="dz-success-mark">
        <i class="fas fa-check-circle text-success"></i>
      </div>
    `;
    
    dropzone.appendChild(preview);
    
    // Simula o progresso do upload
    simulateProgress(preview);
  }
  
  // Simula o progresso do processamento do arquivo
  function simulateProgress(preview) {
    const progressBar = preview.querySelector('.progress-bar');
    let progress = 0;
    
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        preview.classList.add('dz-success');
        setTimeout(() => {
          preview.querySelector('.dz-progress').style.display = 'none';
          preview.querySelector('.dz-success-mark').style.display = 'block';
        }, 300);
      }
      progressBar.style.width = progress + '%';
    }, 200);
  }
  
  // Retorna o ícone apropriado para o tipo de arquivo
  function getFileIcon(file) {
    const extension = file.name.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return 'fas fa-file-pdf';
      case 'doc':
      case 'docx':
        return 'fas fa-file-word';
      case 'txt':
        return 'fas fa-file-alt';
      case 'html':
      case 'htm':
        return 'fas fa-file-code';
      case 'csv':
        return 'fas fa-file-csv';
      case 'xlsx':
      case 'xls':
        return 'fas fa-file-excel';
      case 'md':
        return 'fab fa-markdown';
      default:
        return 'fas fa-file';
    }
  }
  
  // Formata o tamanho do arquivo
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // Extrai texto do arquivo via API
  function extractTextFromFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/extrair_texto', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        textArea.value = data.texto;
        updateProcessingStatus('success', 'Texto extraído com sucesso');
      } else {
        updateProcessingStatus('error', data.error || 'Erro ao extrair texto');
      }
    })
    .catch(error => {
      console.error('Erro ao extrair texto:', error);
      updateProcessingStatus('error', 'Erro ao processar arquivo');
    });
  }
  
  // Atualiza o status de processamento
  function updateProcessingStatus(type, message) {
    // Remove qualquer status anterior
    const existingStatus = document.querySelector('.processing-status');
    if (existingStatus) {
      existingStatus.remove();
    }
    
    // Cria novo elemento de status
    const statusElement = document.createElement('div');
    statusElement.className = `alert processing-status alert-${type === 'success' ? 'success' : 'danger'} mt-2`;
    statusElement.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
      ${message}
    `;
    
    // Adiciona após a área de drop
    dropzone.parentNode.insertBefore(statusElement, dropzone.nextSibling);
    
    // Remove o status após alguns segundos
    setTimeout(() => {
      if (statusElement.parentNode) {
        statusElement.remove();
      }
    }, 5000);
  }
}