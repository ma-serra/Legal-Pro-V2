/**
 * Sistema de Seleção de Especialistas para Análise Multi-Agente
 * Carrega dinamicamente os 309 especialistas das 18 áreas jurídicas
 */

class EspecialistasSelector {
    constructor() {
        this.especialistas = [];
        this.especialistasSelecionados = [];
        this.categorias = [];
        this.maxSelecao = 4; // Limite de 4 especialistas
        this.init();
    }

    async init() {
        await this.carregarCategorias();
        await this.carregarEspecialistas();
        this.configurarEventos();
        this.atualizarContador();
    }

    async carregarCategorias() {
        try {
            const response = await fetch('/api/especialistas/categorias');
            const data = await response.json();
            
            if (data.categorias) {
                this.categorias = data.categorias;
                this.popularSelectCategorias();
            }
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
        }
    }

    popularSelectCategorias() {
        const categoriaFilter = document.getElementById('categoriaFilter');
        if (!categoriaFilter) return;
        
        categoriaFilter.innerHTML = '<option value="">Todas as Áreas (309 especialistas)</option>';
        
        this.categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria.id;
            option.textContent = `${categoria.nome} (${categoria.total_agentes} especialistas)`;
            categoriaFilter.appendChild(option);
        });
    }

    async carregarEspecialistas(categoriaId = '', busca = '') {
        try {
            this.mostrarLoading(true);
            
            // Cache key para evitar requisições desnecessárias
            const cacheKey = `${categoriaId}-${busca}`;
            if (this.cache && this.cache[cacheKey]) {
                this.especialistas = this.cache[cacheKey];
                this.renderizarEspecialistas();
                this.mostrarLoading(false);
                return;
            }
            
            const params = new URLSearchParams();
            if (categoriaId) params.append('categoria_id', categoriaId);
            if (busca) params.append('busca', busca);
            params.append('limite', '100'); // Aumentar limite para reduzir requisições
            
            const response = await fetch(`/api/especialistas?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data && data.especialistas && Array.isArray(data.especialistas)) {
                // Armazenar no cache
                if (!this.cache) this.cache = {};
                this.cache[cacheKey] = data.especialistas;
                
                this.especialistas = data.especialistas;
                this.renderizarEspecialistas();
            } else {
                console.error('Dados inválidos recebidos:', data);
                this.mostrarEstadoVazio(true);
            }
            
            this.mostrarLoading(false);
        } catch (error) {
            console.error('Erro ao carregar especialistas:', error);
            this.mostrarLoading(false);
            this.mostrarEstadoVazio(true);
        }
    }

    renderizarEspecialistas() {
        const agentsList = document.getElementById('agentsList');
        if (!agentsList) return;
        
        if (this.especialistas.length === 0) {
            this.mostrarEstadoVazio(true);
            return;
        }
        
        this.mostrarEstadoVazio(false);
        this.atualizarContadorEspecialistas();
        
        // Renderização em lotes para melhor performance
        this.renderizarEmLotes(agentsList);
    }

    renderizarEmLotes(container) {
        container.innerHTML = '';
        
        // Configuração para renderização em lotes
        const batchSize = 20; // Renderizar 20 cards por vez
        const fragmento = document.createDocumentFragment();
        let currentBatch = 0;
        
        const renderBatch = () => {
            const start = currentBatch * batchSize;
            const end = Math.min(start + batchSize, this.especialistas.length);
            
            for (let i = start; i < end; i++) {
                const especialista = this.especialistas[i];
                const card = this.criarCardOtimizado(especialista);
                if (card) fragmento.appendChild(card);
            }
            
            container.appendChild(fragmento);
            currentBatch++;
            
            // Continuar renderizando se houver mais especialistas
            if (end < this.especialistas.length) {
                requestAnimationFrame(renderBatch);
            }
        };
        
        renderBatch();
    }

    criarCardOtimizado(especialista) {
        // Validar dados do especialista
        if (!especialista || !especialista.id || !especialista.nome) {
            return null;
        }

        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        
        const isSelected = this.especialistasSelecionados.includes(especialista.id);
        const disabled = !isSelected && this.especialistasSelecionados.length >= this.maxSelecao;
        
        // Valores seguros com defaults
        const corCategoria = especialista.cor_categoria || '#5a8fa3';
        const icone = especialista.icone || 'fas fa-user-tie';
        const descricao = especialista.descricao || 'Sem descrição disponível';
        const categoria = especialista.categoria || 'Categoria não informada';
        const nivelEspecializacao = especialista.nivel_especializacao || 'Especialista';
        
        // Template otimizado
        col.innerHTML = `
            <div class="agent-card ${disabled ? 'disabled' : ''}" 
                 style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; cursor: ${disabled ? 'not-allowed' : 'pointer'}; opacity: ${disabled ? '0.6' : '1'}; transition: all 0.2s; position: relative; border: 2px solid ${isSelected ? corCategoria : 'transparent'};">
                
                <div class="agent-preview">
                    <div class="d-flex align-items-center mb-2">
                        <i class="${icone} me-2" style="color: ${corCategoria}; font-size: 1.3rem;"></i>
                        <strong style="font-size: 1rem; line-height: 1.2; color: white;">${especialista.nome}</strong>
                    </div>
                    <small class="d-block mb-3" style="color: rgba(255,255,255,0.8); line-height: 1.4;">
                        ${descricao.length > 85 ? descricao.substring(0, 85) + '...' : descricao}
                    </small>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="badge" style="background: ${corCategoria}; font-size: 0.75rem; padding: 6px 10px; border-radius: 6px;">
                            ${categoria}
                        </span>
                        <span style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">
                            ${nivelEspecializacao}
                        </span>
                    </div>
                    
                    <!-- Checkbox na parte inferior -->
                    <div class="d-flex justify-content-center">
                        <label class="form-check-label d-flex align-items-center" for="agente${especialista.id}" 
                               style="color: white; cursor: ${disabled ? 'not-allowed' : 'pointer'};">
                            <input class="form-check-input me-2" type="checkbox" 
                                   value="${especialista.id}" 
                                   id="agente${especialista.id}" 
                                   ${isSelected ? 'checked' : ''}
                                   ${disabled ? 'disabled' : ''}
                                   style="width: 18px; height: 18px; background: rgba(255,255,255,0.9); border: 2px solid ${corCategoria};">
                            <span style="font-size: 0.9rem;">Selecionar especialista</span>
                        </label>
                    </div>
                </div>
            </div>
        `;
        
        // Event listeners otimizados
        const checkbox = col.querySelector(`#agente${especialista.id}`);
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                this.atualizarSelecao(especialista.id, e.target.checked);
            });
        }

        const agentCard = col.querySelector('.agent-card');
        if (agentCard && !disabled) {
            agentCard.addEventListener('mouseenter', () => {
                agentCard.style.background = 'rgba(255,255,255,0.15)';
            });
            agentCard.addEventListener('mouseleave', () => {
                agentCard.style.background = 'rgba(255,255,255,0.1)';
            });
        }
        
        return col;
    }

    // Atualizar estado visual dos cards após mudanças
    atualizarEstadoCards() {
        const cards = document.querySelectorAll('#agentsList .agent-card');
        cards.forEach(card => {
            const especialistaId = parseInt(card.getAttribute('data-especialista-id'));
            const checkbox = card.querySelector('input[type="checkbox"]');
            
            if (!checkbox || !especialistaId) return;
            
            const isSelected = this.especialistasSelecionados.includes(especialistaId);
            const shouldDisable = !isSelected && this.especialistasSelecionados.length >= this.maxSelecao;
            
            // Obter cor da categoria do especialista
            const especialista = this.especialistas.find(e => e.id === especialistaId);
            const corCategoria = especialista?.cor_categoria || '#5a8fa3';
            
            // Atualizar estado visual
            card.style.border = `2px solid ${isSelected ? corCategoria : 'transparent'}`;
            card.style.opacity = shouldDisable ? '0.6' : '1';
            card.style.cursor = shouldDisable ? 'not-allowed' : 'pointer';
            
            checkbox.disabled = shouldDisable;
            checkbox.checked = isSelected;
            
            // Atualizar classes
            if (shouldDisable) {
                card.classList.add('disabled');
            } else {
                card.classList.remove('disabled');
            }
        });
    }

    atualizarSelecao(especialistaId, selecionado) {
        console.log('Atualizando seleção:', especialistaId, selecionado);
        
        if (selecionado) {
            if (!this.especialistasSelecionados.includes(especialistaId) && this.especialistasSelecionados.length < this.maxSelecao) {
                this.especialistasSelecionados.push(especialistaId);
                console.log('Especialista adicionado:', especialistaId);
            } else if (this.especialistasSelecionados.length >= this.maxSelecao) {
                // Reverter checkbox se limite atingido
                const checkbox = document.getElementById(`agente${especialistaId}`);
                if (checkbox) checkbox.checked = false;
                alert(`Máximo de ${this.maxSelecao} especialistas permitidos.`);
                return;
            }
        } else {
            this.especialistasSelecionados = this.especialistasSelecionados.filter(id => id !== especialistaId);
            console.log('Especialista removido:', especialistaId);
        }
        
        console.log('Especialistas selecionados:', this.especialistasSelecionados);
        this.atualizarContador();
        this.atualizarEstadoCards();
    }

    atualizarContador() {
        const selectedCount = document.getElementById('selectedCount');
        if (selectedCount) {
            selectedCount.textContent = this.especialistasSelecionados.length;
        }
        
        // Atualizar botão de análise
        const btnAnalise = document.getElementById('btnAnaliseEstatistica');
        if (btnAnalise) {
            if (this.especialistasSelecionados.length > 0) {
                btnAnalise.disabled = false;
                btnAnalise.style.opacity = '1';
            } else {
                btnAnalise.disabled = true;
                btnAnalise.style.opacity = '0.6';
            }
        }
    }

    atualizarEstadoCards() {
        // Atualizar estado visual dos cards sem re-renderizar tudo
        this.especialistas.forEach(especialista => {
            const checkbox = document.getElementById(`agente${especialista.id}`);
            const card = checkbox?.closest('.agent-card');
            
            if (checkbox && card) {
                const isSelected = this.especialistasSelecionados.includes(especialista.id);
                const disabled = !isSelected && this.especialistasSelecionados.length >= this.maxSelecao;
                
                checkbox.checked = isSelected;
                checkbox.disabled = disabled;
                
                // Atualizar estilo do card
                card.style.opacity = disabled ? '0.6' : '1';
                card.style.cursor = disabled ? 'not-allowed' : 'pointer';
                card.style.border = `2px solid ${isSelected ? (especialista.cor_categoria || '#5a8fa3') : 'transparent'}`;
            }
        });
    }

    atualizarContadorEspecialistas() {
        const categoriaFilter = document.getElementById('categoriaFilter');
        const totalEspecialistas = this.especialistas.length;
        
        if (categoriaFilter && totalEspecialistas > 0) {
            const selectedOption = categoriaFilter.options[categoriaFilter.selectedIndex];
            if (selectedOption && selectedOption.value === '') {
                selectedOption.textContent = `Todas as Áreas (${totalEspecialistas} especialistas)`;
            }
        }
    }

    mostrarLoading(show) {
        const loadingAgents = document.getElementById('loadingAgents');
        const agentsList = document.getElementById('agentsList');
        
        if (loadingAgents) loadingAgents.style.display = show ? 'block' : 'none';
        if (agentsList) agentsList.style.display = show ? 'none' : 'block';
    }

    mostrarEstadoVazio(show) {
        const emptyState = document.getElementById('emptyState');
        const agentsList = document.getElementById('agentsList');
        
        if (emptyState) emptyState.style.display = show ? 'block' : 'none';
        if (agentsList) agentsList.style.display = show ? 'none' : 'block';
    }

    configurarEventos() {
        // Filtro por categoria
        const categoriaFilter = document.getElementById('categoriaFilter');
        if (categoriaFilter) {
            categoriaFilter.addEventListener('change', (e) => {
                const categoriaId = e.target.value;
                const busca = document.getElementById('buscaEspecialista')?.value || '';
                this.carregarEspecialistas(categoriaId, busca);
            });
        }

        // Busca por texto
        const buscaEspecialista = document.getElementById('buscaEspecialista');
        if (buscaEspecialista) {
            let timeoutBusca;
            buscaEspecialista.addEventListener('input', (e) => {
                clearTimeout(timeoutBusca);
                timeoutBusca = setTimeout(() => {
                    const categoriaId = document.getElementById('categoriaFilter')?.value || '';
                    const busca = e.target.value;
                    this.carregarEspecialistas(categoriaId, busca);
                }, 300);
            });
        }

        // Selecionar todos os especialistas visíveis (respeitando limite de 4)
        const btnSelecionarTodos = document.getElementById('btnSelecionarTodos');
        if (btnSelecionarTodos) {
            btnSelecionarTodos.addEventListener('click', () => {
                let adicionados = 0;
                for (const especialista of this.especialistas) {
                    if (!this.especialistasSelecionados.includes(especialista.id) && 
                        this.especialistasSelecionados.length < this.maxSelecao) {
                        this.especialistasSelecionados.push(especialista.id);
                        adicionados++;
                    }
                    if (this.especialistasSelecionados.length >= this.maxSelecao) break;
                }
                
                if (adicionados === 0 && this.especialistasSelecionados.length >= this.maxSelecao) {
                    alert(`Limite máximo de ${this.maxSelecao} especialistas já atingido.`);
                }
                
                this.atualizarContador();
                this.renderizarEspecialistas();
            });
        }

        // Limpar seleção
        const btnLimparSelecao = document.getElementById('btnLimparSelecao');
        if (btnLimparSelecao) {
            btnLimparSelecao.addEventListener('click', () => {
                this.especialistasSelecionados = [];
                this.atualizarContador();
                this.renderizarEspecialistas();
            });
        }
    }

    getEspecialistasSelecionados() {
        return this.especialistasSelecionados;
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Criar instância global do seletor de especialistas
    window.especialistasSelector = new EspecialistasSelector();
    
    // Configurar outros eventos da página
    configurarUploadArquivo();
    configurarAnalise();
});

function configurarUploadArquivo() {
    const documentFile = document.getElementById('documentFile');
    const uploadArea = document.getElementById('uploadArea');
    const fileInfo = document.getElementById('fileInfo');

    if (!documentFile || !uploadArea) return;

    // Configurar drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.style.background = 'rgba(255,255,255,0.15)';
    }

    function unhighlight(e) {
        uploadArea.style.background = 'rgba(255,255,255,0.1)';
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        documentFile.files = files;
        handleFiles(files);
    }

    documentFile.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            showFileInfo(file);
        }
    }

    function showFileInfo(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        if (fileName && fileSize && fileInfo) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

function configurarAnalise() {
    const btnAnalise = document.getElementById('btnAnaliseMultiagente');
    if (!btnAnalise) return;

    btnAnalise.addEventListener('click', function() {
        const documentFile = document.getElementById('documentFile');
        const file = documentFile?.files[0];
        const especialistasSelecionados = window.especialistasSelector?.getEspecialistasSelecionados() || [];

        if (!file) {
            alert('Por favor, selecione um arquivo para análise.');
            return;
        }

        if (especialistasSelecionados.length === 0) {
            alert('Por favor, selecione pelo menos um especialista (máximo 4).');
            return;
        }

        // Mostrar área de progresso
        const progressCard = document.getElementById('progressCard');
        if (progressCard) {
            progressCard.style.display = 'block';
        }
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iniciando Análise...';

        // Simular progresso
        simulateAnalysis();
    });
}

function simulateAnalysis() {
    const progressBar = document.getElementById('analysisProgress');
    const progressText = document.getElementById('progressText');
    let progress = 0;

    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;

        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        if (progressText) {
            progressText.textContent = `Analisando documento... ${Math.round(progress)}%`;
        }

        if (progress >= 100) {
            clearInterval(interval);
            showResults();
        }
    }, 500);
}

function showResults() {
    const resultsCard = document.getElementById('resultsCard');
    const analysisResults = document.getElementById('analysisResults');
    const especialistasSelecionados = window.especialistasSelector?.getEspecialistasSelecionados() || [];
    
    if (resultsCard) {
        resultsCard.style.display = 'block';
    }
    
    if (analysisResults) {
        analysisResults.innerHTML = `
            <div class="alert alert-success" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: white; border-radius: 8px;">
                <h6><i class="fas fa-check-circle me-2"></i>Análise Concluída com Sucesso</h6>
                <p>A análise multi-agente foi concluída com ${especialistasSelecionados.length} especialistas selecionados. Os resultados detalhados estarão disponíveis em breve.</p>
            </div>
            <div class="mt-3">
                <h6 style="color: white;">Próximos Passos:</h6>
                <ul style="color: rgba(255,255,255,0.9);">
                    <li>Revisar as recomendações dos especialistas</li>
                    <li>Baixar o relatório completo</li>
                    <li>Agendar consultoria jurídica se necessário</li>
                </ul>
            </div>
        `;
    }

    const btn = document.getElementById('btnAnaliseMultiagente');
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-brain me-2"></i>Nova Análise';
    }
}