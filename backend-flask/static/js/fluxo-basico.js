// Editor de Fluxos - Versão Básica
document.addEventListener('DOMContentLoaded', function() {
    // 1. Configurar componentes da paleta
    const componentes = document.querySelectorAll('.componente-item');
    componentes.forEach(comp => {
        comp.addEventListener('click', function() {
            // Ao clicar, adiciona o componente ao canvas
            const tipo = this.getAttribute('data-tipo');
            const nome = this.querySelector('.componente-nome').textContent;
            const desc = this.querySelector('.componente-desc').textContent;
            adicionarComponente(tipo, nome, desc);
        });
    });

    // 2. Configurar botão de salvar
    const btnSalvar = document.getElementById('btn-salvar');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', salvarFluxo);
    }

    // 3. Carregar fluxo existente se houver
    if (typeof fluxoData !== 'undefined' && fluxoData.componentes) {
        carregarFluxo(fluxoData);
    }
});

// Adicionar um novo componente ao canvas
function adicionarComponente(tipo, nome, descricao, posX = null, posY = null) {
    // Gerar um ID único para o componente
    const id = 'comp-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    
    // Posição aleatória se não for especificada
    if (posX === null) posX = 50 + Math.random() * 300;
    if (posY === null) posY = 50 + Math.random() * 300;
    
    // Criar o elemento HTML
    const comp = document.createElement('div');
    comp.id = id;
    comp.className = 'componente ' + tipo;
    comp.style.left = posX + 'px';
    comp.style.top = posY + 'px';
    
    // Conteúdo do componente
    comp.innerHTML = `
        <div class="componente-header">
            <span class="componente-titulo">${nome}</span>
            <button class="btn-fechar" onclick="removerComponente('${id}')">×</button>
        </div>
        <div class="componente-tipo">${tipo}</div>
        <div class="componente-corpo">${descricao}</div>
    `;
    
    // Adicionar ao canvas
    document.getElementById('canvas').appendChild(comp);
    
    // Tornar arrastável
    tornarArrastavel(id);
    
    // Atualizar contador
    atualizarContador();
    
    return id;
}

// Tornar um componente arrastável
function tornarArrastavel(id) {
    const elem = document.getElementById(id);
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    // Manipulador para iniciar arrasto
    elem.onmousedown = dragMouseDown;
    
    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        
        // Obter posição inicial do mouse
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        // Adicionar classe visual de arrasto
        elem.classList.add('arrastando');
        
        // Adicionar eventos temporários para movimento e finalização
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }
    
    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        
        // Calcular nova posição
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        // Definir nova posição do elemento
        elem.style.top = (elem.offsetTop - pos2) + "px";
        elem.style.left = (elem.offsetLeft - pos1) + "px";
    }
    
    function closeDragElement() {
        // Remover handlers de movimento
        document.onmouseup = null;
        document.onmousemove = null;
        
        // Remover classe visual de arrasto
        elem.classList.remove('arrastando');
    }
}

// Remover um componente
function removerComponente(id) {
    const elem = document.getElementById(id);
    if (elem) {
        elem.parentNode.removeChild(elem);
        atualizarContador();
    }
}

// Atualizar contador de componentes
function atualizarContador() {
    const contador = document.getElementById('contador-componentes');
    if (contador) {
        const total = document.querySelectorAll('.componente').length;
        contador.textContent = total;
    }
}

// Salvar o fluxo
function salvarFluxo() {
    // Coletar dados do formulário
    const nome = document.getElementById('fluxo-nome').value;
    const descricao = document.getElementById('fluxo-desc').value;
    
    // Coletar componentes
    const componentes = [];
    document.querySelectorAll('.componente').forEach(comp => {
        componentes.push({
            id: comp.id,
            tipo: comp.classList[1], // A segunda classe é o tipo
            nome: comp.querySelector('.componente-titulo').textContent,
            descricao: comp.querySelector('.componente-corpo').textContent,
            posX: parseInt(comp.style.left),
            posY: parseInt(comp.style.top)
        });
    });
    
    // Montar dados do fluxo
    const dados = {
        nome: nome,
        descricao: descricao,
        componentes: componentes
    };
    
    // Determinar URL (novo ou edição)
    const url = window.location.pathname.includes('/editar/') 
        ? window.location.pathname 
        : '/fluxos/criar';
    
    // Enviar dados
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Fluxo salvo com sucesso!');
            if (data.id && !window.location.pathname.includes('/editar/')) {
                window.location.href = '/fluxos/editar/' + data.id;
            }
        } else {
            alert('Erro ao salvar fluxo: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar fluxo.');
    });
}

// Carregar fluxo existente
function carregarFluxo(fluxo) {
    // Preencher formulário
    document.getElementById('fluxo-nome').value = fluxo.nome || '';
    document.getElementById('fluxo-desc').value = fluxo.descricao || '';
    
    // Carregar componentes
    if (fluxo.componentes && Array.isArray(fluxo.componentes)) {
        fluxo.componentes.forEach(comp => {
            adicionarComponente(
                comp.tipo, 
                comp.nome, 
                comp.descricao, 
                comp.posX || 50, 
                comp.posY || 50
            );
        });
    }
}