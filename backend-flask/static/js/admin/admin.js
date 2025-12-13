/**
 * Scripts para a área administrativa
 */
document.addEventListener('DOMContentLoaded', function() {
  // Toggle do modo de debug
  const debugSwitch = document.getElementById('debugSwitch');
  if (debugSwitch) {
    debugSwitch.addEventListener('change', function() {
      toggleDebugMode(debugSwitch.checked);
    });
  }

  // Inicialização de tooltips do Bootstrap
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

/**
 * Ativa ou desativa o modo de debug
 * @param {boolean} enabled - Se true, ativa o modo de debug
 */
function toggleDebugMode(enabled) {
  fetch('/admin/debug', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `enabled=${enabled}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Atualiza a UI
      document.querySelector('label[for="debugSwitch"]').textContent = 
        enabled ? 'Ativado' : 'Desativado';
      
      // Atualiza a cor do card de debug
      const debugCard = document.querySelector('.card-header:has(i.fa-bug)');
      if (debugCard) {
        if (enabled) {
          debugCard.classList.remove('bg-secondary');
          debugCard.classList.add('bg-warning');
          debugCard.classList.remove('text-white');
          debugCard.classList.add('text-dark');
        } else {
          debugCard.classList.remove('bg-warning');
          debugCard.classList.add('bg-secondary');
          debugCard.classList.remove('text-dark');
          debugCard.classList.add('text-white');
        }
      }
      
      // Exibe mensagem de sucesso
      showToast('Modo de Debug', data.message, 'success');
    } else {
      // Reverte o switch em caso de erro
      document.getElementById('debugSwitch').checked = !enabled;
      
      // Exibe mensagem de erro
      showToast('Erro', data.error || 'Erro ao alterar modo de debug', 'danger');
    }
  })
  .catch(error => {
    console.error('Erro ao alternar modo de debug:', error);
    
    // Reverte o switch em caso de erro
    document.getElementById('debugSwitch').checked = !enabled;
    
    // Exibe mensagem de erro
    showToast('Erro', 'Erro de comunicação com o servidor', 'danger');
  });
}

/**
 * Cria e exibe um toast de notificação
 * @param {string} title - Título do toast
 * @param {string} message - Mensagem do toast
 * @param {string} type - Tipo do toast (success, danger, warning, info)
 */
function showToast(title, message, type = 'info') {
  // Verifica se o container de toasts existe, se não, cria
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Cria o toast
  const toastId = 'toast-' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header bg-${type} text-white">
        <strong class="me-auto">${title}</strong>
        <small>${new Date().toLocaleTimeString()}</small>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Fechar"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;
  
  // Adiciona o toast ao container
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  // Inicializa e exibe o toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, {
    autohide: true,
    delay: 5000
  });
  toast.show();
  
  // Remove o toast do DOM após ser ocultado
  toastElement.addEventListener('hidden.bs.toast', function() {
    toastElement.remove();
  });
}