/**
 * Editor Visual de Fluxos - Versão melhorada
 * 
 * Este script implementa a funcionalidade de arrastar e conectar blocos
 * para criar fluxos de trabalho personalizados.
 */

// Contador para IDs únicos de novos nós
let nodeCounter = 0;

// Dados do fluxo atual
let fluxoAtual = {
    id: null,
    nome: "Novo Fluxo",
    descricao: "",
    agentes: [],
    conexoes: []
};

// Nó selecionado atualmente
let noSelecionado = null;

// Configurações
const tamanhoGrade = 20;
let nivelZoom = 1.0;

/**
 * Inicializa o editor de fluxos
 */
function inicializarEditor() {
    console.log("Inicializando editor de fluxos...");
    
    // Configurar eventos de drag-and-drop manualmente
    configurarPaleta();
    
    // Configurar o canvas para receber elementos
    configurarCanvas();
    
    // Configurar botões da interface
    configurarBotoes();
    
    // Carregar dados do fluxo se existirem
    if (typeof fluxoData !== 'undefined') {
        carregarFluxo(fluxoData);
    }
    
    console.log("Editor inicializado com sucesso");
}

/**
 * Configura os itens da paleta para serem arrastáveis
 */
function configurarPaleta() {
    // Selecionar todos os itens da paleta
    const itens = document.querySelectorAll('.agent-item');
    
    itens.forEach(item => {
        // Adicionar classe visual para indicar que é arrastável
        item.classList.add('draggable');
        
        // Adicionar evento mousedown para iniciar o arrastar
        item.addEventListener('mousedown', function(e) {
            // Criar clone do item para arrastar
            const clone = this.cloneNode(true);
            clone.id = 'drag-temp';
            clone.style.position = 'absolute';
            clone.style.zIndex = '1000';
            clone.style.width = this.offsetWidth + 'px';
            clone.style.opacity = '0.8';
            clone.classList.add('dragging');
            
            // Posicionar o clone
            clone.style.left = e.pageX - this.offsetWidth/2 + 'px';
            clone.style.top = e.pageY - 20 + 'px';
            
            // Adicionar o clone ao body
            document.body.appendChild(clone);
            
            // Armazenar dados do item original para usar quando soltar
            clone.dataset.agentType = this.dataset.agentType;
            clone.dataset.agentPath = this.dataset.agentPath;
            clone.dataset.agentId = this.dataset.agentId;
            clone.querySelector('h6') ? clone.dataset.agentName = this.querySelector('h6').textContent : '';
            clone.querySelector('small') ? clone.dataset.agentDesc = this.querySelector('small').textContent : '';
            
            // Adicionar eventos de movimento e soltar
            document.addEventListener('mousemove', moverElemento);
            document.addEventListener('mouseup', soltarElemento);
            
            // Prevenir comportamento padrão
            e.preventDefault();
        });
    });
}

/**
 * Função executada quando o usuário move o mouse arrastando um item
 */
function moverElemento(e) {
    const elemento = document.getElementById('drag-temp');
    if (elemento) {
        elemento.style.left = e.pageX - elemento.offsetWidth/2 + 'px';
        elemento.style.top = e.pageY - 20 + 'px';
        
        // Verificar se está sobre o canvas
        const canvas = document.getElementById('canvas');
        const canvasRect = canvas.getBoundingClientRect();
        
        if (e.clientX > canvasRect.left && e.clientX < canvasRect.right &&
            e.clientY > canvasRect.top && e.clientY < canvasRect.bottom) {
            // Destacar o canvas para indicar que é uma área de soltura válida
            canvas.classList.add('canvas-hover');
        } else {
            canvas.classList.remove('canvas-hover');
        }
    }
}

/**
 * Função executada quando o usuário solta o elemento arrastado
 */
function soltarElemento(e) {
    const elemento = document.getElementById('drag-temp');
    if (elemento) {
        // Verificar se está sobre o canvas
        const canvas = document.getElementById('canvas');
        const canvasRect = canvas.getBoundingClientRect();
        
        if (e.clientX > canvasRect.left && e.clientX < canvasRect.right &&
            e.clientY > canvasRect.top && e.clientY < canvasRect.bottom) {
            // Calcular posição relativa ao canvas
            const posX = e.clientX - canvasRect.left;
            const posY = e.clientY - canvasRect.top;
            
            // Criar novo nó no canvas
            criarNo(
                elemento.dataset.agentType,
                elemento.dataset.agentName,
                elemento.dataset.agentDesc,
                posX,
                posY,
                elemento.dataset.agentPath,
                elemento.dataset.agentId
            );
        }
        
        // Remover elemento temporário
        elemento.remove();
        canvas.classList.remove('canvas-hover');
        
        // Remover os listeners
        document.removeEventListener('mousemove', moverElemento);
        document.removeEventListener('mouseup', soltarElemento);
    }
}

/**
 * Configura o canvas para receber os nós
 */
function configurarCanvas() {
    const canvas = document.getElementById('canvas');
    
    // Adicionar classe para indicar que aceita itens soltos
    canvas.classList.add('droppable');
    
    // Evento de clique no canvas para desselecionar nós
    canvas.addEventListener('click', function(e) {
        // Verificar se o clique foi diretamente no canvas e não em um nó
        if (e.target === canvas) {
            deselecionarTodos();
        }
    });
}

/**
 * Configura os botões da interface
 */
function configurarBotoes() {
    // Botão de salvar
    const btnSalvar = document.getElementById('btn-salvar-fluxo');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', salvarFluxo);
    }
    
    // Botão de zoom in
    const btnZoomIn = document.getElementById('btn-zoom-in');
    if (btnZoomIn) {
        btnZoomIn.addEventListener('click', function() {
            nivelZoom += 0.1;
            aplicarZoom();
        });
    }
    
    // Botão de zoom out
    const btnZoomOut = document.getElementById('btn-zoom-out');
    if (btnZoomOut) {
        btnZoomOut.addEventListener('click', function() {
            nivelZoom = Math.max(0.3, nivelZoom - 0.1);
            aplicarZoom();
        });
    }
    
    // Botão de resetar zoom
    const btnZoomReset = document.getElementById('btn-zoom-reset');
    if (btnZoomReset) {
        btnZoomReset.addEventListener('click', function() {
            nivelZoom = 1.0;
            aplicarZoom();
        });
    }
}

/**
 * Aplica o nível de zoom atual ao canvas
 */
function aplicarZoom() {
    const canvas = document.getElementById('canvas');
    const conteudo = document.querySelector('.canvas-content');
    
    if (conteudo) {
        conteudo.style.transform = `scale(${nivelZoom})`;
        conteudo.style.transformOrigin = 'top left';
    }
}

/**
 * Cria um novo nó no canvas
 */
function criarNo(tipo, nome, descricao, posX, posY, caminho, id) {
    // Gerar ID único para o nó
    const noId = `no-${Date.now()}-${nodeCounter++}`;
    
    // Configuração do nó para os dados
    const noConfig = {
        id: noId,
        tipo: tipo,
        nome: nome,
        descricao: descricao,
        posicao_x: posX,
        posicao_y: posY,
        configuracao: {},
        caminho: caminho,
        data_id: id
    };
    
    // Adicionar nó aos dados do fluxo
    fluxoAtual.agentes.push(noConfig);
    
    // Criar elemento HTML do nó
    const noElemento = document.createElement('div');
    noElemento.id = noId;
    noElemento.className = `no no-tipo-${tipo}`;
    noElemento.style.left = `${posX}px`;
    noElemento.style.top = `${posY}px`;
    
    // Conteúdo do nó
    noElemento.innerHTML = `
        <div class="no-cabecalho">
            <h5 class="no-titulo">${nome}</h5>
            <button type="button" class="btn-close btn-close-sm no-excluir" aria-label="Fechar"></button>
        </div>
        <div class="no-tipo">${tipo}</div>
        <div class="no-corpo">${descricao}</div>
        <div class="no-rodape">
            <small class="no-id">${noId}</small>
        </div>
        <div class="ponto-conexao ponto-conexao-saida"></div>
        <div class="ponto-conexao ponto-conexao-entrada"></div>
    `;
    
    // Adicionar o nó ao canvas
    document.getElementById('canvas').appendChild(noElemento);
    
    // Configurar nó para ser arrastável
    configurarNoArrastavel(noId);
    
    // Configurar eventos de conexão
    configurarConexoes(noId);
    
    // Atualizar estatísticas
    atualizarEstatisticas();
    
    return noId;
}

/**
 * Configura um nó para ser arrastável
 */
function configurarNoArrastavel(noId) {
    const no = document.getElementById(noId);
    if (!no) return;
    
    no.addEventListener('mousedown', function(e) {
        // Ignorar se o clique foi no botão de fechar
        if (e.target.classList.contains('no-excluir')) {
            return;
        }
        
        // Selecionar este nó
        selecionarNo(noId);
        
        // Posição inicial do mouse
        const initialX = e.clientX;
        const initialY = e.clientY;
        
        // Posição inicial do nó
        const noRect = no.getBoundingClientRect();
        const initialNoX = noRect.left;
        const initialNoY = noRect.top;
        
        // Função para mover o nó
        function moverNo(e) {
            // Calcular deslocamento
            const dx = e.clientX - initialX;
            const dy = e.clientY - initialY;
            
            // Calcular nova posição
            let newX = initialNoX + dx;
            let newY = initialNoY + dy;
            
            // Converter para posição relativa ao canvas
            const canvas = document.getElementById('canvas');
            const canvasRect = canvas.getBoundingClientRect();
            newX = newX - canvasRect.left + canvas.scrollLeft;
            newY = newY - canvasRect.top + canvas.scrollTop;
            
            // Ajustar à grade se necessário
            newX = Math.round(newX / tamanhoGrade) * tamanhoGrade;
            newY = Math.round(newY / tamanhoGrade) * tamanhoGrade;
            
            // Atualizar posição do nó
            no.style.left = `${newX}px`;
            no.style.top = `${newY}px`;
            
            // Atualizar posição nos dados
            const noData = fluxoAtual.agentes.find(n => n.id === noId);
            if (noData) {
                noData.posicao_x = newX;
                noData.posicao_y = newY;
            }
            
            // Atualizar conexões
            atualizarConexoes();
        }
        
        // Função para parar de mover
        function pararMover() {
            document.removeEventListener('mousemove', moverNo);
            document.removeEventListener('mouseup', pararMover);
        }
        
        // Adicionar eventos temporários
        document.addEventListener('mousemove', moverNo);
        document.addEventListener('mouseup', pararMover);
        
        // Prevenir comportamento padrão
        e.preventDefault();
    });
    
    // Evento de clique no botão de excluir
    no.querySelector('.no-excluir').addEventListener('click', function() {
        excluirNo(noId);
    });
}

/**
 * Seleciona um nó
 */
function selecionarNo(noId) {
    // Desselecionar outros nós
    deselecionarTodos();
    
    // Selecionar este nó
    const no = document.getElementById(noId);
    if (no) {
        no.classList.add('no-selecionado');
        noSelecionado = noId;
        
        // Mostrar propriedades do nó no painel lateral
        mostrarPropriedadesNo(noId);
    }
}

/**
 * Desseleciona todos os nós
 */
function deselecionarTodos() {
    document.querySelectorAll('.no').forEach(no => {
        no.classList.remove('no-selecionado');
    });
    
    noSelecionado = null;
    
    // Ocultar painel de propriedades
    document.getElementById('node-properties').classList.add('hidden');
    document.getElementById('flow-properties').classList.remove('hidden');
}

/**
 * Mostra as propriedades do nó selecionado no painel lateral
 */
function mostrarPropriedadesNo(noId) {
    const no = fluxoAtual.agentes.find(n => n.id === noId);
    if (!no) return;
    
    // Ocultar propriedades do fluxo e mostrar propriedades do nó
    document.getElementById('flow-properties').classList.add('hidden');
    const propsPanel = document.getElementById('node-properties');
    propsPanel.classList.remove('hidden');
    
    // Preencher formulário
    document.getElementById('node-name').value = no.nome;
    document.getElementById('node-description').value = no.descricao;
    
    // Configurar eventos de atualização
    document.getElementById('node-name').onchange = function() {
        no.nome = this.value;
        document.querySelector(`#${noId} .no-titulo`).textContent = this.value;
    };
    
    document.getElementById('node-description').onchange = function() {
        no.descricao = this.value;
        document.querySelector(`#${noId} .no-corpo`).textContent = this.value;
    };
}

/**
 * Exclui um nó
 */
function excluirNo(noId) {
    // Remover nó dos dados
    fluxoAtual.agentes = fluxoAtual.agentes.filter(n => n.id !== noId);
    
    // Remover conexões relacionadas
    fluxoAtual.conexoes = fluxoAtual.conexoes.filter(
        c => c.origem !== noId && c.destino !== noId
    );
    
    // Remover nó do DOM
    const no = document.getElementById(noId);
    if (no) {
        no.remove();
    }
    
    // Atualizar estatísticas
    atualizarEstatisticas();
}

/**
 * Configura as conexões para um nó
 */
function configurarConexoes(noId) {
    // A implementar na próxima versão
}

/**
 * Atualiza as conexões visuais
 */
function atualizarConexoes() {
    // A implementar na próxima versão
}

/**
 * Atualiza as estatísticas do fluxo
 */
function atualizarEstatisticas() {
    const numNos = document.getElementById('fluxo-stats-nodes');
    const numConexoes = document.getElementById('fluxo-stats-connections');
    
    if (numNos) {
        numNos.textContent = fluxoAtual.agentes.length;
    }
    
    if (numConexoes) {
        numConexoes.textContent = fluxoAtual.conexoes.length;
    }
}

/**
 * Carrega um fluxo existente
 */
function carregarFluxo(fluxo) {
    // Limpar canvas
    const canvas = document.getElementById('canvas');
    canvas.innerHTML = '';
    
    // Atualizar dados do fluxo
    fluxoAtual = Object.assign({}, fluxo);
    
    // Atualizar formulário
    if (document.getElementById('fluxo-nome')) {
        document.getElementById('fluxo-nome').value = fluxo.nome || '';
    }
    
    if (document.getElementById('fluxo-descricao-input')) {
        document.getElementById('fluxo-descricao-input').value = fluxo.descricao || '';
    }
    
    // Criar nós
    if (fluxo.agentes && Array.isArray(fluxo.agentes)) {
        fluxo.agentes.forEach(agente => {
            criarNo(
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
    
    // Criar conexões
    // A implementar na próxima versão
    
    // Atualizar estatísticas
    atualizarEstatisticas();
}

/**
 * Salva o fluxo atual
 */
function salvarFluxo() {
    // Coletar dados do formulário
    if (document.getElementById('fluxo-nome')) {
        fluxoAtual.nome = document.getElementById('fluxo-nome').value;
    }
    
    if (document.getElementById('fluxo-descricao-input')) {
        fluxoAtual.descricao = document.getElementById('fluxo-descricao-input').value;
    }
    
    // Dados adicionais do fluxo
    fluxoAtual.ultima_atualizacao = new Date().toISOString();
    
    // Enviar dados para o servidor
    const url = fluxoAtual.id ? `/fluxos/editar/${fluxoAtual.id}` : '/api/fluxos/salvar';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(fluxoAtual)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Atualizar ID se for um fluxo novo
            if (data.fluxo_id && !fluxoAtual.id) {
                fluxoAtual.id = data.fluxo_id;
                
                // Atualizar URL para refletir o ID do fluxo
                history.replaceState(null, null, `/fluxos/editar/${fluxoAtual.id}`);
            }
            
            // Mostrar mensagem de sucesso
            alert('Fluxo salvo com sucesso!');
        } else {
            alert('Erro ao salvar fluxo: ' + (data.message || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro ao salvar fluxo:', error);
        alert('Erro ao salvar fluxo. Veja o console para mais detalhes.');
    });
}

// Inicializar quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado, inicializando editor...");
    setTimeout(inicializarEditor, 100);
});