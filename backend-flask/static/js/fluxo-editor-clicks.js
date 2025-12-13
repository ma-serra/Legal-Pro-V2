// Script para selecionar o card ao clicar na criação de fluxos
document.addEventListener('DOMContentLoaded', function() {
    // Selecionar todos os cards de templates de fluxo
    const cards = document.querySelectorAll('.flow-template-card');
    
    // Adicionar evento de clique para cada card
    cards.forEach(card => {
        card.addEventListener('click', function() {
            // Encontrar o input radio dentro deste card
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                // Marcar o radio button
                radio.checked = true;
            }
        });
    });
});