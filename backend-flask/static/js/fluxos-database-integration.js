/**
 * Integração entre Editor de Fluxos e Banco de Dados
 * Carrega componentes compartilhados e permite configuração
 */

// Estado global da integração
let componentesCarregados = [];
let categoriasSistema = [];
let componenteConfigurandoId = null;

/**
 * Inicializa a integração com o banco de dados
 */
async function inicializarIntegracao() {
    console.log('🔄 Inicializando integração fluxos-database...');
    
    try {
        // Carregar componentes do banco
        await carregarComponentesShared();
        
        // Carregar categorias disponíveis
        await carregarCategorias();
        
        // Configurar eventos de configuração
        configurarEventosConfiguracao();
        
        console.log('✅ Integração inicializada com sucesso');
        return true;
        
    } catch (error) {
        console.error('❌ Erro na inicialização da integração:', error);
        return false;
    }
}

/**
 * Carrega componentes compartilhados do banco de dados
 */
async function carregarComponentesShared(categoria = null, termo = null) {
    try {
        const params = new URLSearchParams();
        if (categoria) params.append('categoria', categoria);
        if (termo) params.append('q', termo);
        
        const url = `/api/componentes/shared/listar${params.toString() ? '?' + params.toString() : ''}`;
        console.log(`🔍 Buscando componentes: ${url}`);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.componentes) {
            componentesCarregados = data.componentes;
            
            console.log(`✅ ${data.componentes.length} componentes carregados do banco`);
            
            // Atualizar sidebar com componentes reais
            atualizarSidebarComponentes(data.componentes);
            
            // Atualizar estatísticas
            atualizarEstatisticasComponentes(data.componentes);
            
            return data.componentes;
        } else {
            throw new Error(data.error || 'Falha ao carregar componentes');
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar componentes:', error);
        
        // Exibir mensagem de erro para o usuário
        exibirMensagemErro('Erro ao carregar componentes do banco de dados. Usando componentes padrão.');
        
        // Usar fallback se necessário
        return carregarComponentesFallback();
    }
}

/**
 * Atualiza a sidebar com componentes do banco de dados
 */
function atualizarSidebarComponentes(componentes) {
    const sidebar = document.querySelector('.sidebar-left .sidebar-section:last-child') || 
                   document.querySelector('.sidebar-left') || 
                   document.querySelector('.components-sidebar');
    if (!sidebar) {
        console.warn('⚠️ Sidebar de componentes não encontrada');
        return;
    }
    
    // Organizar por categoria
    const componentesPorCategoria = {};
    componentes.forEach(comp => {
        const categoria = comp.categoria || 'outros';
        if (!componentesPorCategoria[categoria]) {
            componentesPorCategoria[categoria] = [];
        }
        componentesPorCategoria[categoria].push(comp);
    });
    
    // Cores das categorias seguindo o padrão do sistema
    const coresCategoria = {
        'Extração': '#20597f',
        'Classificação': '#fec208',
        'Análise': '#17a2b7',
        'Especialização': '#c4414f',
        'Transformação': '#e98132',
        'Geração': '#36bf9c',
        'Agregação': '#1175e5',
        'Conexão': '#6d47b3'
    };
    
    // Divisão mais equilibrada entre as sidebars
    const categoriasEsquerda = ['Extração', 'Classificação', 'Análise', 'Especialização'];
    const categoriasDireita = ['Transformação', 'Geração', 'Agregação', 'Conexão', 'Validação'];
    
    // Filtrar componentes para cada sidebar
    const componentesEsquerda = componentes.filter(comp => 
        categoriasEsquerda.includes(comp.categoria)
    );
    
    const componentesDireita = componentes.filter(comp => 
        categoriasDireita.includes(comp.categoria)
    );
    
    // Adicionar componentes diretamente na sidebar existente
    componentesEsquerda.forEach(comp => {
        const componentHtml = `
            <div class="component-item" 
                 data-type="${comp.tipo}"
                 data-name="${comp.nome}"
                 data-id="${comp.id}"
                 data-color="${coresCategoria[comp.categoria] || '#6c757d'}"
                 data-icon="${comp.icone}"
                 draggable="true"
                 title="${comp.descricao}">
                <div class="component-name">${comp.nome}</div>
                <div class="component-desc">${comp.descricao}</div>
            </div>
        `;
        
        sidebar.insertAdjacentHTML('beforeend', componentHtml);
    });
    
    // Configurar eventos de drag and drop
    const componentItems = sidebar.querySelectorAll('.component-item[draggable="true"]');
    componentItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            const componentId = this.getAttribute('data-id');
            const componente = componentesCarregados.find(c => c.id == componentId);
            
            if (componente) {
                const dragData = {
                    id: componente.id,
                    type: componente.tipo,
                    name: componente.nome,
                    desc: componente.descricao,
                    icon: componente.icone,
                    color: coresCategoria[componente.categoria] || '#6c757d',
                    categoria: componente.categoria,
                    database_id: componente.id
                };
                
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('text/plain', JSON.stringify(dragData));
            }
        });
    });
    
    // Atualizar sidebar direita também
    atualizarSidebarDireita(componentesDireita, coresCategoria);
    
    console.log(`✅ ${componentesEsquerda.length} componentes adicionados à sidebar esquerda`);
    console.log(`✅ ${componentesDireita.length} componentes adicionados à sidebar direita`);
}

/**
 * Atualiza a sidebar direita com componentes do banco de dados
 */
function atualizarSidebarDireita(componentes, coresCategoria) {
    const sidebar = document.querySelector('.sidebar-right .sidebar-section:last-child') || 
                   document.querySelector('.sidebar-right') || 
                   document.querySelector('.components-sidebar-right');
    if (!sidebar) {
        console.warn('⚠️ Sidebar direita não encontrada');
        return;
    }
    
    // Adicionar componentes diretamente na sidebar direita
    componentes.forEach(comp => {
        const componentHtml = `
            <div class="component-item" 
                 data-type="${comp.tipo}"
                 data-name="${comp.nome}"
                 data-id="${comp.id}"
                 data-color="${coresCategoria[comp.categoria] || '#6c757d'}"
                 data-icon="${comp.icone}"
                 draggable="true"
                 title="${comp.descricao}">
                <div class="component-name">${comp.nome}</div>
                <div class="component-desc">${comp.descricao}</div>
            </div>
        `;
        
        sidebar.insertAdjacentHTML('beforeend', componentHtml);
    });
    
    // Configurar eventos de drag and drop para sidebar direita
    const componentItems = sidebar.querySelectorAll('.component-item[draggable="true"]');
    componentItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            const componentId = this.getAttribute('data-id');
            const componente = componentesCarregados.find(c => c.id == componentId);
            
            if (componente) {
                const dragData = {
                    id: componente.id,
                    type: componente.tipo,
                    name: componente.nome,
                    desc: componente.descricao,
                    icon: componente.icone,
                    color: coresCategoria[componente.categoria] || '#6c757d',
                    categoria: componente.categoria,
                    database_id: componente.id
                };
                
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('text/plain', JSON.stringify(dragData));
            }
        });
    });
}

/**
 * Obtém ícone apropriado para categoria
 */
function obterIconeCategoria(categoria) {
    const icones = {
        'extrator': 'fas fa-file-export',
        'classificador': 'fas fa-filter',
        'analisador': 'fas fa-search',
        'processador': 'fas fa-cogs',
        'especialista': 'fas fa-user-tie',
        'transformador': 'fas fa-exchange-alt',
        'gerador': 'fas fa-magic',
        'agregador': 'fas fa-layer-group',
        'conector': 'fas fa-plug',
        'validador': 'fas fa-check-circle',
        'otimizador': 'fas fa-rocket'
    };
    
    return icones[categoria] || 'fas fa-cog';
}

/**
 * Configura eventos de drag & drop dos componentes
 */
function configurarEventosDragDrop() {
    const componentItems = document.querySelectorAll('.component-item[draggable="true"]');
    
    componentItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            const componentId = this.getAttribute('data-component-id');
            const componente = componentesCarregados.find(c => c.id == componentId);
            
            if (componente) {
                draggedComponent = {
                    id: componente.id,
                    type: componente.tipo,
                    name: componente.nome,
                    desc: componente.descricao,
                    icon: componente.icone,
                    color: componente.cor,
                    categoria: componente.categoria,
                    database_id: componente.id
                };
                
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('text/plain', JSON.stringify(draggedComponent));
                
                console.log(`🔄 Iniciando drag: ${componente.nome}`);
            }
        });
        
        item.addEventListener('dragend', function(e) {
            draggedComponent = null;
        });
    });
}

/**
 * Configura busca de componentes
 */
function configurarBuscaComponentes() {
    const searchInput = document.getElementById('search-components');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const termo = this.value.toLowerCase().trim();
        
        // Filtrar componentes visualmente
        const componentItems = document.querySelectorAll('.component-item');
        
        componentItems.forEach(item => {
            const nome = item.querySelector('.component-name').textContent.toLowerCase();
            const desc = item.querySelector('.component-desc').textContent.toLowerCase();
            
            const matches = nome.includes(termo) || desc.includes(termo);
            
            item.style.display = matches ? 'flex' : 'none';
        });
        
        // Ocultar categorias vazias
        document.querySelectorAll('.category-section').forEach(categoryDiv => {
            const visibleItems = categoryDiv.querySelectorAll('.component-item[style="display: flex;"], .component-item:not([style])');
            categoryDiv.style.display = visibleItems.length > 0 ? 'block' : 'none';
        });
    });
}

/**
 * Adiciona componente diretamente ao canvas
 */
async function adicionarComponenteCanvas(componenteId) {
    try {
        const componente = componentesCarregados.find(c => c.id == componenteId);
        if (!componente) {
            throw new Error('Componente não encontrado');
        }
        
        // Posição aleatória no canvas
        const canvas = document.getElementById('canvas');
        const rect = canvas.getBoundingClientRect();
        const x = 50 + Math.random() * (rect.width - 200);
        const y = 50 + Math.random() * (rect.height - 100);
        
        const componentData = {
            id: componentIdCounter++,
            type: componente.tipo,
            name: componente.nome,
            desc: componente.descricao,
            x: x,
            y: y,
            color: componente.cor,
            icon: componente.icone,
            database_id: componente.id
        };
        
        // Adicionar ao array global (se existir no contexto)
        if (typeof components !== 'undefined') {
            components.push(componentData);
        }
        
        // Renderizar no canvas (usando função do editor se existir)
        if (typeof renderComponent === 'function') {
            renderComponent(componentData);
        } else if (typeof addComponent === 'function') {
            addComponent(componentData);
        } else {
            console.warn('⚠️ Função de renderização não encontrada');
        }
        
        // Atualizar estatísticas (se função existir)
        if (typeof updateStats === 'function') {
            updateStats();
        }
        
        console.log(`✅ Componente ${componente.nome} adicionado ao canvas`);
        
    } catch (error) {
        console.error('❌ Erro ao adicionar componente:', error);
        exibirMensagemErro('Erro ao adicionar componente ao canvas');
    }
}

/**
 * Abre configuração de componente
 */
async function configurarComponente(componenteId) {
    try {
        componenteConfigurandoId = componenteId;
        const componente = componentesCarregados.find(c => c.id == componenteId);
        
        if (!componente) {
            throw new Error('Componente não encontrado');
        }
        
        console.log(`⚙️ Configurando componente: ${componente.nome}`);
        
        // Abrir modal/página de configuração
        const url = `/componentes-editor/${componenteId}/configurar`;
        
        // Opção 1: Abrir em modal (se tiver suporte)
        if (typeof abrirModalConfiguracao === 'function') {
            abrirModalConfiguracao(url, componente);
        } 
        // Opção 2: Abrir em nova janela
        else {
            const configWindow = window.open(url, 'configComponente', 'width=800,height=600,scrollbars=yes');
            
            // Escutar mensagens da janela de configuração
            window.addEventListener('message', function(event) {
                if (event.data.type === 'componente_configurado') {
                    console.log('✅ Componente configurado:', event.data.componente);
                    configWindow.close();
                    
                    // Recarregar componentes para pegar mudanças
                    carregarComponentesShared();
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Erro ao configurar componente:', error);
        exibirMensagemErro('Erro ao abrir configuração do componente');
    }
}

/**
 * Carrega categorias do sistema
 */
async function carregarCategorias() {
    try {
        const response = await fetch('/api/componentes/shared/categorias');
        const data = await response.json();
        
        if (data.success && data.categorias) {
            categoriasSistema = data.categorias;
            console.log(`✅ ${data.categorias.length} categorias carregadas`);
            return data.categorias;
        } else {
            throw new Error(data.error || 'Falha ao carregar categorias');
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar categorias:', error);
        return [];
    }
}

/**
 * Configura eventos de configuração
 */
function configurarEventosConfiguracao() {
    // Escutar mensagens de componentes configurados
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'componente_configurado') {
            console.log('📢 Componente configurado via mensagem:', event.data);
            
            // Atualizar lista local se necessário
            const componenteAtualizado = event.data.componente;
            const index = componentesCarregados.findIndex(c => c.id === componenteAtualizado.id);
            
            if (index !== -1) {
                componentesCarregados[index] = { ...componentesCarregados[index], ...componenteAtualizado };
                console.log('🔄 Componente local atualizado');
            }
        }
    });
}

/**
 * Atualiza estatísticas dos componentes
 */
function atualizarEstatisticasComponentes(componentes) {
    // Contar por categoria
    const estatisticas = {};
    componentes.forEach(comp => {
        const categoria = comp.categoria || 'outros';
        estatisticas[categoria] = (estatisticas[categoria] || 0) + 1;
    });
    
    // Calcular distribuição por sidebar
    const categoriasEsquerda = ['Extração', 'Classificação', 'Análise', 'Especialização'];
    const categoriasDireita = ['Transformação', 'Geração', 'Agregação', 'Conexão', 'Validação'];
    
    const componentesEsquerda = componentes.filter(comp => categoriasEsquerda.includes(comp.categoria)).length;
    const componentesDireita = componentes.filter(comp => categoriasDireita.includes(comp.categoria)).length;
    
    // Exibir no console para debug
    console.log('📊 Estatísticas de componentes:', {
        total: componentes.length,
        por_categoria: estatisticas,
        ativo: componentes.filter(c => c.ativo).length,
        distribuicao: {
            sidebar_esquerda: componentesEsquerda,
            sidebar_direita: componentesDireita
        }
    });
}

/**
 * Componentes de fallback para casos de erro
 */
function carregarComponentesFallback() {
    console.log('🔄 Carregando componentes de fallback...');
    
    const fallbackComponents = [
        {
            id: 'fallback_1',
            nome: 'Extrator de Texto',
            categoria: 'extrator',
            tipo: 'extrator_texto',
            descricao: 'Extrai texto de documentos',
            icone: 'fas fa-file-text',
            cor: '#20597f',
            ativo: true
        },
        {
            id: 'fallback_2',
            nome: 'Analisador de Sentimento',
            categoria: 'analisador',
            tipo: 'analisador_sentimento',
            descricao: 'Analisa sentimentos do texto',
            icone: 'fas fa-heart',
            cor: '#17a2b7',
            ativo: true
        }
    ];
    
    atualizarSidebarComponentes(fallbackComponents);
    return fallbackComponents;
}

/**
 * Exibe mensagem de erro para o usuário
 */
function exibirMensagemErro(mensagem) {
    // Tentar usar sistema de notificação se existir
    if (typeof showNotification === 'function') {
        showNotification('error', mensagem);
    } 
    // Fallback para alert
    else {
        console.error('❌', mensagem);
        
        // Mostrar toast se Bootstrap estiver disponível
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastHtml = `
                <div class="toast align-items-center text-white bg-danger border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">${mensagem}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            // Adicionar toast ao corpo
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                toastContainer.style.zIndex = '9999';
                document.body.appendChild(toastContainer);
            }
            
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        }
    }
}

// Inicialização automática quando DOM carregado
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que outros scripts carregaram
    setTimeout(() => {
        inicializarIntegracao();
    }, 1000);
});

// Exportar funções globalmente
window.fluxosDatabaseIntegration = {
    inicializarIntegracao,
    carregarComponentesShared,
    configurarComponente,
    adicionarComponenteCanvas,
    componentesCarregados: () => componentesCarregados,
    categoriasSistema: () => categoriasSistema
};