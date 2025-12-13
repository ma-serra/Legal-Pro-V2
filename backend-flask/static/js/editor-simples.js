/**
 * Editor de Fluxos - Versão Simplificada
 */

// Variáveis globais
let componentesSelecionados = [];
let canvas = null;

// Inicializar quando a página estiver carregada
document.addEventListener('DOMContentLoaded', () => {
    inicializarEditor();
});

/**
 * Inicializa o editor com funcionalidades básicas
 */
function inicializarEditor() {
    console.log('Inicializando editor simples...');
    
    // Obter referência ao canvas
    canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error('Canvas não encontrado!');
        return;
    }
    
    // Configurar os componentes da paleta
    configurarComponentes();
    
    // Configurar botões de ação
    configurarBotoes();
    
    console.log('Editor inicializado com sucesso');
}

/**
 * Configura os componentes da paleta para serem adicionados ao canvas
 */
function configurarComponentes() {
    // Selecionar todos os componentes da paleta
    const componentes = document.querySelectorAll('.agent-item');
    
    componentes.forEach(componente => {
        // Adicionar evento de clique para cada componente
        componente.addEventListener('click', (e) => {
            // Criar um componente no canvas baseado no item clicado
            const tipo = componente.getAttribute('data-agent-type');
            const caminho = componente.getAttribute('data-agent-path');
            const id = componente.getAttribute('data-agent-id');
            const nome = componente.querySelector('h6')?.textContent || 'Componente';
            const descricao = componente.querySelector('small')?.textContent || '';
            
            // Adicionar ao canvas em uma posição aleatória
            const posX = 50 + Math.random() * 200;
            const posY = 50 + Math.random() * 200;
            
            adicionarComponenteAoCanvas(tipo, nome, descricao, posX, posY, caminho, id);
        });
        
        // Alterar cursor para indicar que é clicável
        componente.style.cursor = 'pointer';
    });
}

/**
 * Adiciona um componente ao canvas
 */
function adicionarComponenteAoCanvas(tipo, nome, descricao, posX, posY, caminho, id) {
    // Criar um ID único para o componente
    const componenteId = `comp-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // Criar o elemento HTML
    const novoComponente = document.createElement('div');
    novoComponente.id = componenteId;
    novoComponente.className = `node node-type-${tipo}`;
    novoComponente.style.left = `${posX}px`;
    novoComponente.style.top = `${posY}px`;
    
    // Conteúdo do componente
    novoComponente.innerHTML = `
        <div class="node-header">
            <h5 class="node-title">${nome}</h5>
            <button type="button" class="btn-close btn-close-sm node-delete" aria-label="Fechar"></button>
        </div>
        <div class="node-type">${tipo}</div>
        <div class="node-body">${descricao}</div>
        <div class="node-footer">
            <small class="node-id">${componenteId}</small>
        </div>
    `;
    
    // Adicionar ao canvas
    canvas.appendChild(novoComponente);
    
    // Tornar o componente arrastável manualmente
    tornarArrastavel(componenteId);
    
    // Adicionar evento de clique para seleção
    novoComponente.addEventListener('click', (e) => {
        // Evitar propagação se clicou no botão fechar
        if (e.target.classList.contains('node-delete')) {
            excluirComponente(componenteId);
            e.stopPropagation();
            return;
        }
        
        selecionarComponente(componenteId);
    });
    
    // Configurar o botão de fechar para excluir o componente
    const btnFechar = novoComponente.querySelector('.node-delete');
    if (btnFechar) {
        btnFechar.addEventListener('click', () => {
            excluirComponente(componenteId);
        });
    }
    
    // Adicionar o componente à lista de componentes selecionados
    const dadosComponente = {
        id: componenteId,
        tipo: tipo,
        nome: nome,
        descricao: descricao,
        posicao_x: posX,
        posicao_y: posY,
        caminho: caminho,
        id_dados: id
    };
    
    componentesSelecionados.push(dadosComponente);
    
    // Atualizar contador de componentes
    atualizarContadores();
    
    return componenteId;
}

/**
 * Torna um elemento arrastável
 */
function tornarArrastavel(elementoId) {
    const elemento = document.getElementById(elementoId);
    if (!elemento) return;

    let offsetX, offsetY, isDragging = false;

    // Mouse Down - Iniciar arrasto
    elemento.addEventListener('mousedown', function(e) {
        // Ignorar se clicou no botão fechar
        if (e.target.classList.contains('node-delete')) return;
        
        // Posição inicial do mouse
        offsetX = e.clientX - elemento.getBoundingClientRect().left;
        offsetY = e.clientY - elemento.getBoundingClientRect().top;
        isDragging = true;
        
        // Selecionar o elemento
        selecionarComponente(elementoId);
        
        // Evitar comportamento padrão
        e.preventDefault();
    });
    
    // Mouse Move - Mover elemento
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        // Calcular nova posição
        const canvasRect = canvas.getBoundingClientRect();
        const x = e.clientX - canvasRect.left - offsetX;
        const y = e.clientY - canvasRect.top - offsetY;
        
        // Atualizar posição do elemento
        elemento.style.left = `${x}px`;
        elemento.style.top = `${y}px`;
        
        // Atualizar dados do componente
        const componente = componentesSelecionados.find(c => c.id === elementoId);
        if (componente) {
            componente.posicao_x = x;
            componente.posicao_y = y;
        }
    });
    
    // Mouse Up - Finalizar arrasto
    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
}

/**
 * Seleciona um componente
 */
function selecionarComponente(componenteId) {
    // Desselecionar todos os componentes
    document.querySelectorAll('.node').forEach(node => {
        node.classList.remove('node-selected');
    });
    
    // Selecionar o componente atual
    const componenteAtual = document.getElementById(componenteId);
    if (componenteAtual) {
        componenteAtual.classList.add('node-selected');
    }
}

/**
 * Exclui um componente
 */
function excluirComponente(componenteId) {
    // Remover do DOM
    const componente = document.getElementById(componenteId);
    if (componente) {
        componente.remove();
    }
    
    // Remover da lista de componentes
    componentesSelecionados = componentesSelecionados.filter(c => c.id !== componenteId);
    
    // Atualizar contadores
    atualizarContadores();
}

/**
 * Atualiza os contadores de componentes e conexões
 */
function atualizarContadores() {
    // Atualizar contador de componentes
    const contadorNos = document.getElementById('fluxo-stats-nodes');
    if (contadorNos) {
        contadorNos.textContent = componentesSelecionados.length;
    }
    
    // Atualizar contador de conexões (simulado)
    const contadorConexoes = document.getElementById('fluxo-stats-connections');
    if (contadorConexoes) {
        contadorConexoes.textContent = '0';
    }
}

/**
 * Configura os botões de ação
 */
function configurarBotoes() {
    // Botão salvar
    const btnSalvar = document.getElementById('btn-salvar-fluxo');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', salvarFluxo);
    }
    
    // Eventos para formulário
    const campoNome = document.getElementById('fluxo-nome');
    const campoDesc = document.getElementById('fluxo-descricao-input');
    
    if (campoNome) {
        campoNome.addEventListener('input', function() {
            const tituloFluxo = document.getElementById('fluxo-titulo');
            if (tituloFluxo) {
                tituloFluxo.textContent = this.value;
            }
        });
    }
    
    if (campoDesc) {
        campoDesc.addEventListener('input', function() {
            const descFluxo = document.getElementById('fluxo-descricao');
            if (descFluxo) {
                descFluxo.textContent = this.value;
            }
        });
    }
}

/**
 * Salva o fluxo atual
 */
function salvarFluxo() {
    // Obter dados do formulário
    const nome = document.getElementById('fluxo-nome')?.value || 'Novo Fluxo';
    const descricao = document.getElementById('fluxo-descricao-input')?.value || '';
    
    // Estruturar dados do fluxo
    const dadosFluxo = {
        nome: nome,
        descricao: descricao,
        agentes: componentesSelecionados.map(c => ({
            id: c.id,
            tipo: c.tipo,
            nome: c.nome,
            descricao: c.descricao,
            posicao_x: c.posicao_x,
            posicao_y: c.posicao_y,
            caminho: c.caminho,
            data_id: c.id_dados,
            configuracao: {}
        })),
        conexoes: [],
        configuracao: {
            tema: 'light',
            auto_layout: true,
            mostrar_grid: true
        }
    };
    
    // Verificar se estamos editando um fluxo existente ou criando um novo
    const pathParts = window.location.pathname.split('/');
    const isEditando = pathParts.includes('editor');
    const fluxoId = isEditando ? pathParts[pathParts.length - 1] : null;
    
    // URL para requisição - a rota de edição é /fluxos/editor/<id>
    const url = isEditando ? 
        `/fluxos/editor/${fluxoId}` : 
        '/api/fluxos/salvar';
    
    // Debug: mostrar informações sobre a requisição
    console.log('Dados do fluxo a serem salvos:', dadosFluxo);
    console.log('URL de salvamento:', url);
    console.log('Está editando:', isEditando);
    console.log('ID do fluxo:', fluxoId);
    
    // Enviar dados
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosFluxo)
    })
    .then(response => {
        console.log('Resposta recebida:', response.status, response.statusText);
        return response.json();
    })
    .then(data => {
        console.log('Dados da resposta:', data);
        if (data.success) {
            alert('Fluxo salvo com sucesso!');
            
            // Redirecionar para a página de edição se for um novo fluxo
            if (!isEditando && data.fluxo_id) {
                window.location.href = `/fluxos/editor/${data.fluxo_id}`;
            }
        } else {
            alert('Erro ao salvar fluxo: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro ao salvar fluxo:', error);
        alert('Erro ao salvar fluxo. Veja o console para mais detalhes.');
    });
}