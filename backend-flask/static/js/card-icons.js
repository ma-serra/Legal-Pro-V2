/**
 * Adiciona ícones aos cards de especialistas criminais
 * Este script insere ícones Font Awesome antes dos títulos dos especialistas
 */
document.addEventListener('DOMContentLoaded', function() {
  // Abordagem 1: Para os cards no index.html
  function adicionarIconesCards() {
    // Encontra todos os cards na página
    const cards = document.querySelectorAll('.card');
    
    // Para cada card, verifica o título e adiciona o ícone apropriado
    cards.forEach(function(card) {
      // Encontra o título do card
      const title = card.querySelector('h5');
      
      // Se não encontrou título, pula para o próximo card
      if (!title) return;
      
      const text = title.textContent.trim();
      
      // Não adicionar ícones aos títulos dos cards criminais
      // Os ícones foram removidos conforme solicitado
    });
  }
  
  // Abordagem 2: Para a página de dashboard e cards criados dinamicamente
  function adicionarIconesCardsDinamicos() {
    // Busca cards mais genéricos na página que possam ter sido gerados dinamicamente
    const cardTitles = document.querySelectorAll('.card-title, h4, h5, h3');
    
    cardTitles.forEach(function(title) {
      const text = title.textContent.trim();
      
      // Primeiro verifica se o título já tem um ícone
      if (title.querySelector('i') || title.parentElement && title.parentElement.querySelector('i')) {
        return; // Já tem ícone, não precisa adicionar
      }
      
      let icon = null;
      
      // Determina qual ícone usar baseado no texto
      if (text.includes('Execução Penal')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-gavel text-danger me-2';
      } 
      else if (text.includes('Crimes de Trânsito')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-car-crash text-danger me-2';
      }
      else if (text.includes('Tribunal do Júri') || text.includes('Júri')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-users text-danger me-2';
      }
      else if (text.includes('Evidências') || text.includes('Prova')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-search text-danger me-2';
      }
      else if (text.includes('Oral') || text.includes('Sustentação')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-microphone text-danger me-2';
      }
      else if (text.includes('Revisor') || text.includes('Revisão')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-check-double text-danger me-2';
      }
      else if (text.includes('Criminal') || text.includes('Penal')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-balance-scale-right text-danger me-2';
      }
      else if (text.includes('Drogas')) {
        icon = document.createElement('i');
        icon.className = 'fas fa-pills text-danger me-2';
      }
      
      // Se encontrou um ícone correspondente, adiciona ao início do título
      if (icon) {
        title.insertBefore(icon, title.firstChild);
      }
    });
  }
  
  // Executa ambas as abordagens
  adicionarIconesCards();
  adicionarIconesCardsDinamicos();
  
  // Em alguns casos, os cards podem ser carregados dinamicamente
  // Então executamos a função novamente após um curto atraso
  setTimeout(function() {
    adicionarIconesCards();
    adicionarIconesCardsDinamicos();
  }, 500);
});