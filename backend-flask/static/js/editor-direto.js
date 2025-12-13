/**
 * Editor de Fluxos Direto - JavaScript Principal
 * Sistema completo de canvas com arrastar e soltar
 */

// Estado global do editor
let currentFluxo = null;
let selectedNode = null;
let draggedElement = null;
let canvas = null;
let canvasContainer = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let zoomLevel = 1.0;
let nodes = [];
let connections = [];
let nodeCounter = 0;

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando Editor de Fluxos...');
    
    // Elementos principais
    canvas = document.getElementById('canvas');
    canvasContainer = document.getElementById('canvas-container');
    
    if (!canvas || !canvasContainer) {
        console.error('Elementos canvas não encontrados!');
        return;
    }
    
    // Inicializar editor
    initializeEditor();
    setupDragAndDrop();
    setupCanvasControls();
    setupPropertyPanel();
    
    // Carregar dados do fluxo se existir
    if (typeof fluxoData !== 'undefined' && fluxoData) {
        currentFluxo = fluxoData;
        loadFluxoData(fluxoData);
    }
    
    console.log('Editor de Fluxos inicializado com sucesso!');
});

/**
 * Inicializa o editor básico
 */
function initializeEditor() {
    // Configurar canvas
    canvas.style.position = 'relative';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.minHeight = '600px';
    
    // Eventos do canvas
    canvas.addEventListener('click', function(e) {
        if (e.target === canvas) {
            deselectAllNodes();
        }
    });
    
    // Prevenir contexto menu no canvas
    canvas.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
}

/**
 * Configura o sistema de arrastar e soltar
 */
function setupDragAndDrop() {
    // Tornar itens da paleta arrastáveis
    const agentItems = document.querySelectorAll('.agent-item');
    
    agentItems.forEach(item => {
        item.draggable = true;
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('click', handleAgentClick);
    });
    
    // Configurar área de drop no canvas
    canvas.addEventListener('dragover', handleDragOver);
    canvas.addEventListener('drop', handleDrop);
}

/**
 * Manipula o início do arraste
 */
function handleDragStart(e) {
    draggedElement = {
        type: e.target.getAttribute('data-agent-type'),
        path: e.target.getAttribute('data-agent-path'),
        id: e.target.getAttribute('data-agent-id'),
        title: e.target.querySelector('h6').textContent,
        description: e.target.querySelector('small').textContent
    };
    
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', '');
}

/**
 * Manipula clique nos itens da paleta (alternativa ao arrastar)
 */
function handleAgentClick(e) {
    const agentData = {
        type: e.currentTarget.getAttribute('data-agent-type'),
        path: e.currentTarget.getAttribute('data-agent-path'),
        id: e.currentTarget.getAttribute('data-agent-id'),
        title: e.currentTarget.querySelector('h6').textContent,
        description: e.currentTarget.querySelector('small').textContent
    };
    
    // Posição aleatória no canvas
    const rect = canvas.getBoundingClientRect();
    const x = 50 + Math.random() * (rect.width - 250);
    const y = 50 + Math.random() * (rect.height - 150);
    
    createNode(agentData, x, y);
}

/**
 * Manipula arrastar sobre o canvas
 */
function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
}

/**
 * Manipula soltar no canvas
 */
function handleDrop(e) {
    e.preventDefault();
    
    if (!draggedElement) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    createNode(draggedElement, x, y);
    draggedElement = null;
}

/**
 * Cria um novo nó no canvas
 */
function createNode(agentData, x, y) {
    nodeCounter++;
    
    const node = {
        id: `node_${nodeCounter}`,
        type: agentData.type,
        path: agentData.path,
        agentId: agentData.id,
        title: agentData.title,
        description: agentData.description,
        x: x,
        y: y,
        properties: {}
    };
    
    nodes.push(node);
    renderNode(node);
    updateFluxoStats();
}

/**
 * Renderiza um nó no canvas
 */
function renderNode(node) {
    const nodeElement = document.createElement('div');
    nodeElement.className = `flow-node node-type-${node.type}`;
    nodeElement.id = node.id;
    nodeElement.style.left = node.x + 'px';
    nodeElement.style.top = node.y + 'px';
    
    nodeElement.innerHTML = `
        <div class="node-header">
            <div class="node-title">${node.title}</div>
            <button class="btn btn-sm btn-danger" onclick="removeNode('${node.id}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="node-type">${node.type}</div>
        <div class="node-body">${node.description}</div>
        <div class="node-footer">ID: ${node.id}</div>
    `;
    
    // Tornar o nó movível
    makeNodeDraggable(nodeElement, node);
    
    // Evento de clique para seleção
    nodeElement.addEventListener('click', function(e) {
        e.stopPropagation();
        selectNode(node.id);
    });
    
    canvas.appendChild(nodeElement);
}

/**
 * Torna um nó arrastável dentro do canvas
 */
function makeNodeDraggable(element, node) {
    let isDragging = false;
    let startX, startY, initialX, initialY;
    
    element.addEventListener('mousedown', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.parentElement.tagName === 'BUTTON') {
            return; // Não arrastar se clicou no botão
        }
        
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        initialX = node.x;
        initialY = node.y;
        
        element.style.cursor = 'grabbing';
        
        function handleMouseMove(e) {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            node.x = initialX + deltaX;
            node.y = initialY + deltaY;
            
            // Limitar aos bounds do canvas
            node.x = Math.max(0, Math.min(node.x, canvas.offsetWidth - element.offsetWidth));
            node.y = Math.max(0, Math.min(node.y, canvas.offsetHeight - element.offsetHeight));
            
            element.style.left = node.x + 'px';
            element.style.top = node.y + 'px';
        }
        
        function handleMouseUp() {
            isDragging = false;
            element.style.cursor = 'grab';
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        }
        
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    });
}

/**
 * Seleciona um nó
 */
function selectNode(nodeId) {
    deselectAllNodes();
    
    const nodeElement = document.getElementById(nodeId);
    const node = nodes.find(n => n.id === nodeId);
    
    if (nodeElement && node) {
        nodeElement.classList.add('selected');
        selectedNode = node;
        showNodeProperties(node);
    }
}

/**
 * Deseleciona todos os nós
 */
function deselectAllNodes() {
    document.querySelectorAll('.flow-node.selected').forEach(el => {
        el.classList.remove('selected');
    });
    selectedNode = null;
    showFluxoProperties();
}

/**
 * Remove um nó
 */
function removeNode(nodeId) {
    const nodeElement = document.getElementById(nodeId);
    if (nodeElement) {
        nodeElement.remove();
    }
    
    nodes = nodes.filter(n => n.id !== nodeId);
    
    if (selectedNode && selectedNode.id === nodeId) {
        selectedNode = null;
        showFluxoProperties();
    }
    
    updateFluxoStats();
}

/**
 * Configura controles do canvas
 */
function setupCanvasControls() {
    // Botão de zoom in
    const zoomInBtn = document.getElementById('btn-zoom-in');
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', function() {
            zoomLevel = Math.min(zoomLevel + 0.1, 2.0);
            updateZoom();
        });
    }
    
    // Botão de zoom out
    const zoomOutBtn = document.getElementById('btn-zoom-out');
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', function() {
            zoomLevel = Math.max(zoomLevel - 0.1, 0.5);
            updateZoom();
        });
    }
    
    // Botão de reset do zoom
    const zoomResetBtn = document.getElementById('btn-zoom-reset');
    if (zoomResetBtn) {
        zoomResetBtn.addEventListener('click', function() {
            zoomLevel = 1.0;
            updateZoom();
        });
    }
    
    // Botão limpar canvas
    const clearBtn = document.getElementById('btn-clear-canvas');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            if (confirm('Tem certeza que deseja limpar todo o canvas?')) {
                clearCanvas();
            }
        });
    }
    
    // Botão toggle grade
    const toggleGridBtn = document.getElementById('btn-toggle-grid');
    if (toggleGridBtn) {
        toggleGridBtn.addEventListener('click', toggleGrid);
    }
    
    // Botão salvar
    const saveBtn = document.getElementById('btn-salvar');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveFluxo);
    }
}

/**
 * Atualiza o zoom do canvas
 */
function updateZoom() {
    canvas.style.transform = `scale(${zoomLevel})`;
    document.getElementById('zoom-level').textContent = Math.round(zoomLevel * 100) + '%';
}

/**
 * Alterna a grade do canvas
 */
function toggleGrid() {
    canvas.classList.toggle('show-grid');
    const btn = document.getElementById('btn-toggle-grid');
    const icon = btn.querySelector('i');
    
    if (canvas.classList.contains('show-grid')) {
        icon.className = 'fas fa-th';
        btn.title = 'Ocultar Grade';
    } else {
        icon.className = 'fas fa-th-large';
        btn.title = 'Mostrar Grade';
    }
}

/**
 * Limpa o canvas
 */
function clearCanvas() {
    nodes = [];
    connections = [];
    selectedNode = null;
    
    // Remove todos os nós do DOM
    document.querySelectorAll('.flow-node').forEach(el => el.remove());
    
    showFluxoProperties();
    updateFluxoStats();
}

/**
 * Configura o painel de propriedades
 */
function setupPropertyPanel() {
    showFluxoProperties();
    
    // Inputs do fluxo
    const nomeInput = document.getElementById('fluxo-nome');
    const descricaoInput = document.getElementById('fluxo-descricao');
    
    if (nomeInput) {
        nomeInput.addEventListener('input', function() {
            document.getElementById('fluxo-titulo').textContent = this.value || 'Novo Fluxo';
        });
    }
    
    if (descricaoInput) {
        descricaoInput.addEventListener('input', function() {
            document.getElementById('fluxo-descricao').textContent = this.value || '';
        });
    }
}

/**
 * Mostra propriedades do fluxo
 */
function showFluxoProperties() {
    document.getElementById('fluxo-properties').style.display = 'block';
    document.getElementById('node-properties').style.display = 'none';
}

/**
 * Mostra propriedades do nó selecionado
 */
function showNodeProperties(node) {
    document.getElementById('fluxo-properties').style.display = 'none';
    document.getElementById('node-properties').style.display = 'block';
    
    // Preencher campos
    document.getElementById('node-name').value = node.title;
    document.getElementById('node-description').value = node.description;
}

/**
 * Atualiza estatísticas do fluxo
 */
function updateFluxoStats() {
    document.getElementById('fluxo-stats-nodes').textContent = nodes.length;
    document.getElementById('fluxo-stats-connections').textContent = connections.length;
}

/**
 * Salva o fluxo
 */
function saveFluxo() {
    const nome = document.getElementById('fluxo-nome').value || 'Novo Fluxo';
    const descricao = document.getElementById('fluxo-descricao').value || '';
    
    const fluxoData = {
        nome: nome,
        descricao: descricao,
        agentes: nodes.map(node => ({
            id: node.id,
            tipo: node.type,
            nome: node.title,
            posicao_x: node.x,
            posicao_y: node.y,
            propriedades: node.properties
        })),
        conexoes: connections
    };
    
    // Fazer requisição para salvar
    fetch('/fluxos/salvar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(fluxoData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Fluxo salvo com sucesso!');
            if (data.fluxo_id) {
                currentFluxo = fluxoData;
                currentFluxo.id = data.fluxo_id;
            }
        } else {
            alert('Erro ao salvar fluxo: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar fluxo');
    });
}

/**
 * Carrega dados de um fluxo existente
 */
function loadFluxoData(fluxo) {
    if (fluxo.agentes) {
        fluxo.agentes.forEach(agente => {
            const node = {
                id: agente.id || `node_${nodeCounter++}`,
                type: agente.tipo,
                title: agente.nome,
                description: agente.descricao || '',
                x: agente.posicao_x || 50,
                y: agente.posicao_y || 50,
                properties: agente.propriedades || {}
            };
            
            nodes.push(node);
            renderNode(node);
        });
    }
    
    updateFluxoStats();
}

/**
 * Obtém o token CSRF
 */
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

/**
 * Busca componentes na paleta
 */
function setupSearch() {
    const searchInput = document.getElementById('busca-agentes');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const agentItems = document.querySelectorAll('.agent-item');
            
            agentItems.forEach(item => {
                const title = item.querySelector('h6').textContent.toLowerCase();
                const desc = item.querySelector('small').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || desc.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

// Inicializar busca quando o DOM carregar
document.addEventListener('DOMContentLoaded', setupSearch);