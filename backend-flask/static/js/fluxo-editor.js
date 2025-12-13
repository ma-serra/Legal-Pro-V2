/**
 * Editor Visual de Fluxos
 * 
 * Este script implementa a funcionalidade de arrastar e conectar blocos
 * para criar fluxos de trabalho personalizados.
 */

// Configuração do jsPlumb
let jsPlumbInstance;
// Nós e conexões do fluxo atual
let fluxoNodes = [];
let fluxoConnections = [];
// Nó atualmente selecionado
let selectedNode = null;
// Dados do fluxo atual
let currentFluxo = {
    id: null,
    nome: "Novo Fluxo",
    descricao: "",
    agentes: [],
    conexoes: [],
    configuracao: {
        tema: "light",
        auto_layout: true,
        mostrar_grid: true,
        snap_to_grid: true
    }
};

// Contador para IDs únicos de novos nós
let nodeCounter = 0;

// Configurações
const gridSize = 20;
let zoomLevel = 1.0;
let isDarkMode = false;
let showGrid = true;
let snapToGrid = true;

/**
 * Inicializa o editor visual
 */
function initFluxoEditor() {
    console.log("Inicializando editor de fluxos...");
    
    // Inicializar jsPlumb
    jsPlumbInstance = jsPlumb.getInstance({
        Endpoint: ["Dot", { radius: 4 }],
        Connector: ["Bezier", { curviness: 50 }],
        HoverPaintStyle: { stroke: "#1e90ff", strokeWidth: 2 },
        ConnectionOverlays: [
            ["Arrow", { 
                location: 1,
                id: "arrow",
                length: 10,
                foldback: 0.8
            }]
        ],
        Container: "canvas"
    });
    
    // Configurar drag-and-drop para os itens da paleta
    setupDragDrop();
    
    // Configurar manipuladores de eventos
    setupEventHandlers();
    
    // Verificar se há um fluxo para carregar
    loadFluxoFromPage();
    
    // Aplicar preferências de tema
    setupTheme();
    
    console.log("Editor inicializado com sucesso");
}

/**
 * Configura o drag-and-drop dos elementos da paleta para o canvas
 */
function setupDragDrop() {
    console.log("Configurando drag-and-drop...");
    
    // Garantir que o jQuery e jQuery UI estão carregados
    if (typeof $ === 'undefined' || typeof $.ui === 'undefined') {
        console.error("jQuery ou jQuery UI não está disponível!");
        return;
    }
    
    // Reinicializar draggable em todos os itens da paleta
    try {
        // Remover draggable existente para evitar duplicação
        $(".agent-item").draggable("destroy");
    } catch (e) {
        // Ignora se não estiverem inicializados
    }
    
    // Tornar os itens da paleta arrastáveis
    $(".agent-item").draggable({
        helper: "clone",
        cursor: "move",
        appendTo: "body",
        zIndex: 1000,
        containment: "document",
        start: function(event, ui) {
            console.log("Iniciou arrasto de componente");
            $(ui.helper).addClass("agent-dragging");
        }
    });
    
    // Configurar o canvas para receber elementos arrastados
    try {
        $("#canvas").droppable("destroy");
    } catch (e) {
        // Ignora se não estiver inicializado
    }
    
    $("#canvas").droppable({
        accept: ".agent-item",
        activeClass: "canvas-drop-active",
        hoverClass: "canvas-drop-hover",
        drop: function(event, ui) {
            console.log("Componente solto no canvas");
            const offset = $(this).offset();
            let posX = ui.offset.left - offset.left;
            let posY = ui.offset.top - offset.top;
            
            // Ajustar à grade se necessário
            if (snapToGrid) {
                posX = Math.round(posX / gridSize) * gridSize;
                posY = Math.round(posY / gridSize) * gridSize;
            }
            
            // Obter dados do elemento arrastado
            const agentType = $(ui.draggable).data("agent-type");
            const agentPath = $(ui.draggable).data("agent-path");
            const agentId = $(ui.draggable).data("agent-id");
            const agentName = $(ui.draggable).find("h6").text();
            const agentDesc = $(ui.draggable).find("small").text();
            
            console.log("Criando nó:", agentType, agentName);
            
            // Criar um novo nó no fluxo
            createNode(agentType, agentName, agentDesc, posX, posY, agentPath, agentId);
        }
    });
}

/**
 * Cria um novo nó no canvas
 */
function createNode(type, name, description, posX, posY, path = "", dataId = null) {
    // Gerar ID único para o nó
    const nodeId = `node-${Date.now()}-${nodeCounter++}`;
    
    // Configuração do nó
    const nodeConfig = {
        id: nodeId,
        tipo: type,
        nome: name,
        descricao: description,
        posicao_x: posX,
        posicao_y: posY,
        configuracao: {},
        caminho: path,
        data_id: dataId
    };
    
    // Adicionar nó à lista de nós do fluxo
    fluxoNodes.push(nodeConfig);
    
    // Criar o elemento HTML do nó
    const $node = $(`
        <div id="${nodeId}" class="node node-type-${type}" style="left: ${posX}px; top: ${posY}px;">
            <div class="node-header">
                <h5 class="node-title">${name}</h5>
                <button type="button" class="btn-close btn-close-sm node-delete" aria-label="Close"></button>
            </div>
            <div class="node-type">${type}</div>
            <div class="node-body">${description}</div>
            <div class="node-footer">
                <small class="node-id">${nodeId}</small>
            </div>
            <div class="connection-point connection-point-output"></div>
            <div class="connection-point connection-point-input"></div>
        </div>
    `);
    
    // Adicionar nó ao canvas
    $("#canvas").append($node);
    
    // Tornar o nó arrastável
    jsPlumbInstance.draggable(nodeId, {
        grid: snapToGrid ? [gridSize, gridSize] : null,
        stop: function(event) {
            // Atualizar a posição do nó no modelo de dados
            const nodeInfo = fluxoNodes.find(n => n.id === nodeId);
            if (nodeInfo) {
                const position = $(`#${nodeId}`).position();
                nodeInfo.posicao_x = position.left;
                nodeInfo.posicao_y = position.top;
            }
            updateFluxoState();
        }
    });
    
    // Adicionar endpoints para conectar os nós
    jsPlumbInstance.addEndpoint(nodeId, {
        anchor: "Right",
        uuid: `${nodeId}-output`,
        maxConnections: -1,
        isSource: true,
        cssClass: "endpoint-output",
        overlays: [
            ["Custom", {
                create: function() { 
                    return $("<div class='endpoint-overlay-out'></div>"); 
                }
            }]
        ]
    });
    
    jsPlumbInstance.addEndpoint(nodeId, {
        anchor: "Left",
        uuid: `${nodeId}-input`,
        maxConnections: -1,
        isTarget: true,
        cssClass: "endpoint-input",
        overlays: [
            ["Custom", {
                create: function() { 
                    return $("<div class='endpoint-overlay-in'></div>"); 
                }
            }]
        ]
    });
    
    // Adicionar evento de clique para selecionar o nó
    $node.on("click", function(e) {
        if (!$(e.target).hasClass("node-delete")) {
            selectNode(nodeId);
        }
        e.stopPropagation();
    });
    
    // Adicionar evento para deletar o nó
    $node.find(".node-delete").on("click", function(e) {
        deleteNode(nodeId);
        e.stopPropagation();
    });
    
    // Selecionar o nó recém-criado
    selectNode(nodeId);
    
    // Atualizar o estado do fluxo
    updateFluxoState();
    
    return nodeId;
}

/**
 * Seleciona um nó e exibe suas propriedades
 */
function selectNode(nodeId) {
    // Remover seleção anterior
    $(".node").removeClass("node-selected");
    
    // Aplicar seleção no nó
    $(`#${nodeId}`).addClass("node-selected");
    
    // Armazenar nó selecionado
    selectedNode = fluxoNodes.find(n => n.id === nodeId);
    
    // Mostrar painel de propriedades
    showNodeProperties(selectedNode);
}

/**
 * Exibe o painel de propriedades de um nó
 */
function showNodeProperties(node) {
    if (!node) return;
    
    // Esconder todos os painéis de propriedades
    $("#node-properties").removeClass("hidden");
    $("#fluxo-properties").addClass("hidden");
    
    // Preencher campos básicos
    $("#node-name").val(node.nome);
    $("#node-description").val(node.descricao);
    
    // Exibir propriedades específicas do tipo de nó
    const $customProps = $("#node-custom-properties");
    $customProps.empty();
    
    switch (node.tipo) {
        case "extrator":
            $customProps.append(`
                <div class="mb-3">
                    <label class="form-label">Formato de Saída</label>
                    <select class="form-select" id="prop-formato-saida">
                        <option value="texto" ${node.configuracao.formato_saida === "texto" ? "selected" : ""}>Texto</option>
                        <option value="json" ${node.configuracao.formato_saida === "json" ? "selected" : ""}>JSON</option>
                        <option value="estruturado" ${node.configuracao.formato_saida === "estruturado" ? "selected" : ""}>Estruturado</option>
                    </select>
                </div>
            `);
            break;
            
        case "classificador":
            let categorias = node.configuracao.categorias || [];
            $customProps.append(`
                <div class="mb-3">
                    <label class="form-label">Categorias</label>
                    <input type="text" class="form-control" id="prop-categorias" value="${categorias.join(", ")}">
                    <small class="form-text text-muted">Separadas por vírgula</small>
                </div>
            `);
            break;
            
        case "analisador":
            $customProps.append(`
                <div class="mb-3">
                    <label class="form-label">Modelo</label>
                    <select class="form-select" id="prop-modelo">
                        <option value="gpt-4o" ${node.configuracao.modelo === "gpt-4o" ? "selected" : ""}>OpenAI GPT-4o</option>
                        <option value="anthropic" ${node.configuracao.modelo === "anthropic" ? "selected" : ""}>Anthropic Claude</option>
                        <option value="deepseek" ${node.configuracao.modelo === "deepseek" ? "selected" : ""}>DeepSeek</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Nível de Detalhe</label>
                    <select class="form-select" id="prop-nivel-detalhe">
                        <option value="baixo" ${node.configuracao.nivel_detalhe === "baixo" ? "selected" : ""}>Baixo</option>
                        <option value="medio" ${node.configuracao.nivel_detalhe === "medio" ? "selected" : ""}>Médio</option>
                        <option value="alto" ${node.configuracao.nivel_detalhe === "alto" ? "selected" : ""}>Alto</option>
                    </select>
                </div>
            `);
            break;
            
        // Adicionar mais tipos conforme necessário
    }
    
    // Configurar eventos para salvar propriedades
    $customProps.find("select, input").on("change", function() {
        saveNodeProperties();
    });
    
    // Configurar eventos para campos básicos
    $("#node-name, #node-description").off("change").on("change", function() {
        saveNodeProperties();
    });
}

/**
 * Salva as propriedades do nó selecionado
 */
function saveNodeProperties() {
    if (!selectedNode) return;
    
    // Atualizar nome e descrição
    selectedNode.nome = $("#node-name").val();
    selectedNode.descricao = $("#node-description").val();
    
    // Atualizar no modelo de dados
    const nodeIndex = fluxoNodes.findIndex(n => n.id === selectedNode.id);
    if (nodeIndex !== -1) {
        fluxoNodes[nodeIndex] = selectedNode;
    }
    
    // Atualizar na interface
    const $node = $(`#${selectedNode.id}`);
    $node.find(".node-title").text(selectedNode.nome);
    $node.find(".node-body").text(selectedNode.descricao);
    
    // Atualizar propriedades específicas
    switch (selectedNode.tipo) {
        case "extrator":
            selectedNode.configuracao.formato_saida = $("#prop-formato-saida").val();
            break;
            
        case "classificador":
            const categorias = $("#prop-categorias").val().split(",").map(c => c.trim()).filter(c => c);
            selectedNode.configuracao.categorias = categorias;
            break;
            
        case "analisador":
            selectedNode.configuracao.modelo = $("#prop-modelo").val();
            selectedNode.configuracao.nivel_detalhe = $("#prop-nivel-detalhe").val();
            break;
    }
    
    // Atualizar estado do fluxo
    updateFluxoState();
}

/**
 * Deleta um nó e suas conexões
 */
function deleteNode(nodeId) {
    // Remover todas as conexões do nó
    jsPlumbInstance.remove(nodeId);
    
    // Remover do modelo de dados
    fluxoNodes = fluxoNodes.filter(n => n.id !== nodeId);
    
    // Atualizar conexões
    updateFluxoConnections();
    
    // Limpar seleção se for o nó selecionado
    if (selectedNode && selectedNode.id === nodeId) {
        selectedNode = null;
        $("#node-properties").addClass("hidden");
    }
    
    // Atualizar estado do fluxo
    updateFluxoState();
}

/**
 * Atualiza as conexões no modelo de dados
 */
function updateFluxoConnections() {
    // Limpar conexões atuais
    fluxoConnections = [];
    
    // Obter todas as conexões do jsPlumb
    const connections = jsPlumbInstance.getConnections();
    
    // Mapear para o formato do modelo de dados
    connections.forEach(conn => {
        const sourceId = conn.sourceId;
        const targetId = conn.targetId;
        
        fluxoConnections.push({
            origem: sourceId,
            destino: targetId,
            tipo: "default"
        });
    });
    
    // Atualizar o estado do fluxo
    updateFluxoState();
}

/**
 * Atualiza o estado geral do fluxo
 */
function updateFluxoState() {
    // Atualizar o modelo de dados do fluxo
    currentFluxo.agentes = fluxoNodes;
    currentFluxo.conexoes = fluxoConnections;
    
    // Atualizar exibição do JSON (para debug)
    if ($("#fluxo-json").length) {
        $("#fluxo-json").val(JSON.stringify(currentFluxo, null, 2));
    }
}

/**
 * Configura manipuladores de eventos
 */
function setupEventHandlers() {
    // Configurar eventos de conexão do jsPlumb
    jsPlumbInstance.bind("connection", function(info) {
        console.log("Nova conexão:", info);
        updateFluxoConnections();
    });
    
    jsPlumbInstance.bind("connectionDetached", function(info) {
        console.log("Conexão removida:", info);
        updateFluxoConnections();
    });
    
    // Clicar no canvas deseleciona o nó
    $("#canvas").on("click", function(e) {
        if ($(e.target).attr("id") === "canvas") {
            $(".node").removeClass("node-selected");
            selectedNode = null;
            $("#node-properties").addClass("hidden");
            $("#fluxo-properties").removeClass("hidden");
        }
    });
    
    // Botão para alternar modo escuro
    $("#btn-toggle-dark-mode").on("click", function() {
        isDarkMode = !isDarkMode;
        applyTheme();
    });
    
    // Botão para alternar grade
    $("#btn-toggle-grid").on("click", function() {
        showGrid = !showGrid;
        applyGridVisibility();
    });
    
    // Botão para alternar snap à grade
    $("#btn-toggle-snap").on("click", function() {
        snapToGrid = !snapToGrid;
        $(this).find("i").toggleClass("fa-magnet fa-minus");
        
        // Atualizar opção de grade para todos os nós
        fluxoNodes.forEach(node => {
            jsPlumbInstance.draggable(node.id, {
                grid: snapToGrid ? [gridSize, gridSize] : null
            });
        });
    });
    
    // Controles de zoom
    $("#btn-zoom-in").on("click", function() {
        zoomLevel = Math.min(zoomLevel + 0.1, 2.0);
        applyZoom();
    });
    
    $("#btn-zoom-out").on("click", function() {
        zoomLevel = Math.max(zoomLevel - 0.1, 0.5);
        applyZoom();
    });
    
    $("#btn-zoom-reset").on("click", function() {
        zoomLevel = 1.0;
        applyZoom();
    });
    
    // Botão para limpar canvas
    $("#btn-clear-canvas").on("click", function() {
        if (confirm("Tem certeza que deseja limpar todo o canvas? Esta ação não pode ser desfeita.")) {
            clearCanvas();
        }
    });
    
    // Botão para salvar fluxo
    $("#btn-salvar").on("click", function() {
        saveFluxo();
    });
    
    // Botão para propriedades do fluxo
    $("#btn-propriedades-fluxo").on("click", function() {
        showFluxoProperties();
    });
    
    // Filtro de busca para a paleta de agentes
    $("#busca-agentes").on("input", function() {
        const term = $(this).val().toLowerCase();
        $(".agent-item").each(function() {
            const text = $(this).text().toLowerCase();
            $(this).toggle(text.includes(term));
        });
    });
}

/**
 * Carrega um fluxo a partir dos dados da página
 */
function loadFluxoFromPage() {
    // Verificar se existe um objeto fluxo global
    if (typeof fluxoData !== 'undefined' && fluxoData) {
        // Usar os dados do fluxo existente
        currentFluxo = fluxoData;
        
        // Atualizar o título e descrição
        $("#fluxo-titulo").text(currentFluxo.nome);
        $("#fluxo-descricao").text(currentFluxo.descricao);
        
        // Renderizar os nós
        if (currentFluxo.agentes && currentFluxo.agentes.length) {
            currentFluxo.agentes.forEach(agente => {
                createNode(
                    agente.tipo,
                    agente.nome,
                    agente.descricao,
                    agente.posicao_x,
                    agente.posicao_y,
                    agente.caminho,
                    agente.data_id
                );
            });
        }
        
        // Renderizar as conexões após um breve delay para garantir que os endpoints foram criados
        setTimeout(() => {
            if (currentFluxo.conexoes && currentFluxo.conexoes.length) {
                currentFluxo.conexoes.forEach(conexao => {
                    jsPlumbInstance.connect({
                        source: `${conexao.origem}-output`,
                        target: `${conexao.destino}-input`
                    });
                });
            }
        }, 100);
    }
}

/**
 * Exibe o painel de propriedades do fluxo
 */
function showFluxoProperties() {
    $("#node-properties").addClass("hidden");
    $("#fluxo-properties").removeClass("hidden");
    
    // Preencher campos
    $("#fluxo-nome").val(currentFluxo.nome);
    $("#fluxo-descricao").val(currentFluxo.descricao);
    
    // Configurar evento para salvar propriedades
    $("#fluxo-nome, #fluxo-descricao").off("change").on("change", function() {
        // Atualizar modelo de dados
        currentFluxo.nome = $("#fluxo-nome").val();
        currentFluxo.descricao = $("#fluxo-descricao").val();
        
        // Atualizar interface
        $("#fluxo-titulo").text(currentFluxo.nome);
        $("#fluxo-descricao").text(currentFluxo.descricao);
        
        updateFluxoState();
    });
}

/**
 * Limpa o canvas e reinicia o fluxo
 */
function clearCanvas() {
    // Remover todos os nós
    jsPlumbInstance.empty("canvas");
    
    // Limpar modelos de dados
    fluxoNodes = [];
    fluxoConnections = [];
    selectedNode = null;
    
    // Ocultar painel de propriedades de nó
    $("#node-properties").addClass("hidden");
    $("#fluxo-properties").removeClass("hidden");
    
    // Atualizar estado do fluxo
    updateFluxoState();
}

/**
 * Salva o fluxo no servidor
 */
function saveFluxo() {
    // Salvar alterações no nome e descrição antes de enviar
    if ($("#fluxo-nome").length && $("#fluxo-descricao").length) {
        currentFluxo.nome = $("#fluxo-nome").val();
        currentFluxo.descricao = $("#fluxo-descricao").val();
    }
    
    // Preparar os dados para envio
    const fluxoData = {
        id: currentFluxo.id,
        nome: currentFluxo.nome,
        descricao: currentFluxo.descricao,
        agentes: currentFluxo.agentes,
        conexoes: currentFluxo.conexoes,
        configuracao: currentFluxo.configuracao
    };
    
    // Mostrar feedback visual
    const $btnSalvar = $("#btn-salvar");
    const originalText = $btnSalvar.html();
    $btnSalvar.html('<i class="fas fa-spinner fa-spin me-1"></i> Salvando...');
    $btnSalvar.prop('disabled', true);
    
    // Determinar URL baseada em se é um fluxo existente ou novo
    const url = currentFluxo.id ? 
        `/fluxos/editor/${currentFluxo.id}` : 
        `/fluxos/criar`;
    
    // Adicionar CSRF token para evitar erros de segurança
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    
    // Enviar para o servidor
    $.ajax({
        url: url,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(fluxoData),
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(response) {
            if (response.success) {
                // Atualizar ID se for um novo fluxo
                if (response.fluxo_id) {
                    currentFluxo.id = response.fluxo_id;
                    
                    // Atualizar também a variável global fluxoData para o botão Testar
                    if (typeof fluxoData !== 'undefined') {
                        fluxoData.id = response.fluxo_id;
                    }
                }
                
                console.log("Fluxo salvo com ID:", currentFluxo.id);
                
                // Mostrar mensagem de sucesso
                Toast.show('Fluxo salvo com sucesso!', 'success');
                
                // Atualizar título da página para mostrar que foi salvo
                document.title = `${currentFluxo.nome} - Editor de Fluxos`;
                
                // Atualizar URL para refletir o ID (para fluxos novos)
                if (window.location.pathname.includes('/editor') && !window.location.pathname.includes(`/${currentFluxo.id}`)) {
                    history.replaceState(null, document.title, `/fluxos/editor/${currentFluxo.id}`);
                }
            } else {
                console.error("Erro ao salvar fluxo:", response);
                Toast.show(`Erro ao salvar: ${response.message || 'Erro desconhecido'}`, 'error');
            }
        },
        error: function(xhr, status, error) {
            let errorMsg = 'Erro ao salvar o fluxo';
            try {
                const response = JSON.parse(xhr.responseText);
                errorMsg = response.message || errorMsg;
            } catch (e) {
                console.error('Erro ao analisar resposta:', e);
            }
            Toast.show(errorMsg, 'error');
        },
        complete: function() {
            // Restaurar botão
            $btnSalvar.html(originalText);
            $btnSalvar.prop('disabled', false);
        }
    });
}

/**
 * Configura o tema inicial do editor
 */
function setupTheme() {
    // Verificar preferência do usuário
    isDarkMode = localStorage.getItem('darkMode') === 'true' || 
                 (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    // Aplicar tema inicial
    applyTheme();
    
    // Aplicar visibilidade da grade
    applyGridVisibility();
}

/**
 * Aplica o tema atual (claro/escuro)
 */
function applyTheme() {
    if (isDarkMode) {
        $("body").addClass("dark-mode");
        $("#btn-toggle-dark-mode").html('<i class="fas fa-sun"></i> <span class="theme-text">Modo Claro</span>');
    } else {
        $("body").removeClass("dark-mode");
        $("#btn-toggle-dark-mode").html('<i class="fas fa-moon"></i> <span class="theme-text">Modo Escuro</span>');
    }
    
    // Salvar preferência
    localStorage.setItem('darkMode', isDarkMode);
    
    // Atualizar configuração do fluxo
    currentFluxo.configuracao.tema = isDarkMode ? 'dark' : 'light';
}

/**
 * Aplica a visibilidade da grade
 */
function applyGridVisibility() {
    if (showGrid) {
        $("#canvas").addClass("show-grid");
        $("#btn-toggle-grid").html('<i class="fas fa-th"></i> Ocultar Grade');
    } else {
        $("#canvas").removeClass("show-grid");
        $("#btn-toggle-grid").html('<i class="fas fa-th"></i> Mostrar Grade');
    }
    
    // Atualizar configuração do fluxo
    currentFluxo.configuracao.mostrar_grid = showGrid;
}

/**
 * Aplica o nível de zoom
 */
function applyZoom() {
    $("#canvas").css('transform', `scale(${zoomLevel})`);
    $("#zoom-level").text(`${Math.round(zoomLevel * 100)}%`);
}

/**
 * Sistema de Toast para feedback
 */
const Toast = {
    show: function(message, type = 'info') {
        // Criar elemento toast se não existir
        let $toast = $("#toast-notification");
        if (!$toast.length) {
            $("body").append(`
                <div id="toast-notification" class="toast-notification">
                    <div class="toast-content"></div>
                </div>
            `);
            $toast = $("#toast-notification");
        }
        
        // Definir classe e conteúdo
        $toast.removeClass("info success error warning").addClass(type);
        $toast.find(".toast-content").text(message);
        
        // Mostrar toast
        $toast.addClass("show");
        
        // Esconder após 3 segundos
        setTimeout(() => {
            $toast.removeClass("show");
        }, 3000);
    }
};

// Inicializar quando o documento estiver pronto
$(document).ready(function() {
    initFluxoEditor();
    // Configurar drag-and-drop para os componentes
    setupDragDrop();
});