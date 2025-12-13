/**
 * Database Manager - Gerenciador de Banco de Dados
 * Fornece interface para administração de bancos Legal Pro
 */

const DatabaseManager = {
    currentJobId: null,
    eventSource: null,
    statusRefreshInterval: null,

    /**
     * Inicializa o gerenciador
     */
    init() {
        console.log('DatabaseManager: Inicializando...');
        this.loadStatus();
        this.loadHistory();
        
        // Auto-refresh a cada 30 segundos
        this.statusRefreshInterval = setInterval(() => {
            if (!this.currentJobId) {
                this.loadStatus();
            }
        }, 30000);
    },

    /**
     * Carrega status de todos os bancos
     */
    async loadStatus() {
        try {
            const response = await fetch('/admin/database/api/status');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar status');
            }
            
            // Atualizar estatísticas
            this.updateStats(data.stats);
            
            // Atualizar informações dos bancos
            this.updateDatabaseCards(data.active_db, data.databases);
            
            // Atualizar jobs ativos
            this.updateActiveJobs(data.recent_jobs);
            
        } catch (error) {
            console.error('Erro ao carregar status:', error);
            this.showToast('Erro ao carregar status dos bancos', 'error');
        }
    },

    /**
     * Atualiza estatísticas no dashboard
     */
    updateStats(stats) {
        if (!stats) return;
        
        document.getElementById('stat-tables').textContent = 
            stats.total_tables || '-';
        
        document.getElementById('stat-records').textContent = 
            (stats.total_records || 0).toLocaleString('pt-BR');
        
        document.getElementById('stat-size').textContent = 
            stats.size_mb ? `${stats.size_mb} MB` : '-';
        
        // Jobs ativos (contar jobs com status "running")
        document.getElementById('stat-jobs').textContent = '-';
    },

    /**
     * Atualiza cards dos bancos de dados
     */
    updateDatabaseCards(activeDb, databases) {
        // Neon
        if (databases.neon && databases.neon.configured) {
            const status = databases.neon.status;
            const badge = document.getElementById('badge-neon');
            const info = document.getElementById('info-neon');
            const card = document.getElementById('card-neon');
            
            badge.className = 'badge db-status-badge ' + 
                (status === 'online' ? 'bg-success' : 'bg-danger');
            badge.textContent = status === 'online' ? 'Online' : 'Offline';
            
            info.textContent = databases.neon.host || 'Neon PostgreSQL Cloud';
            
            if (activeDb.type === 'neon') {
                card.classList.add('active');
            }
        }
        
        // PostgreSQL Local
        if (databases.local && databases.local.configured && databases.local.type === 'postgres') {
            const status = databases.local.status;
            const badge = document.getElementById('badge-postgres');
            const info = document.getElementById('info-postgres');
            const card = document.getElementById('card-postgres');
            
            badge.className = 'badge db-status-badge ' + 
                (status === 'online' ? 'bg-success' : 'bg-danger');
            badge.textContent = status === 'online' ? 'Online' : 'Offline';
            
            info.textContent = databases.local.host || 'PostgreSQL Docker Local';
            
            if (activeDb.type === 'postgres_local') {
                card.classList.add('active');
            }
        } else {
            document.getElementById('badge-postgres').className = 'badge db-status-badge bg-secondary';
            document.getElementById('badge-postgres').textContent = 'Não Configurado';
            document.getElementById('info-postgres').textContent = 'PostgreSQL local não está configurado';
        }
        
        // SQLite Local
        if (databases.local && databases.local.configured && databases.local.type === 'sqlite') {
            const status = databases.local.status;
            const badge = document.getElementById('badge-sqlite');
            const info = document.getElementById('info-sqlite');
            const card = document.getElementById('card-sqlite');
            
            badge.className = 'badge db-status-badge ' + 
                (status === 'exists' ? 'bg-success' : 'bg-warning');
            badge.textContent = status === 'exists' ? 'Existe' : 'Não Existe';
            
            info.textContent = databases.local.path || 'local_legal_pro.db';
            
            if (activeDb.type === 'sqlite_local') {
                card.classList.add('active');
            }
        } else {
            document.getElementById('badge-sqlite').className = 'badge db-status-badge bg-secondary';
            document.getElementById('badge-sqlite').textContent = 'Não Configurado';
            document.getElementById('info-sqlite').textContent = 'SQLite local não está configurado';
        }
    },

    /**
     * Atualiza informações de jobs ativos
     */
    updateActiveJobs(recentJobs) {
        if (!recentJobs) return;
        
        const activeCount = recentJobs.filter(j => j.status === 'running').length;
        document.getElementById('stat-jobs').textContent = activeCount;
    },

    /**
     * Carrega histórico de operações
     */
    async loadHistory(page = 1) {
        try {
            const response = await fetch(`/admin/database/api/history?page=${page}&per_page=10`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar histórico');
            }
            
            this.renderHistory(data.jobs);
            
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            document.getElementById('history-body').innerHTML = 
                '<tr><td colspan="7" class="text-center text-danger">Erro ao carregar histórico</td></tr>';
        }
    },

    /**
     * Renderiza histórico na tabela
     */
    renderHistory(jobs) {
        const tbody = document.getElementById('history-body');
        
        if (!jobs || jobs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhuma operação registrada</td></tr>';
            return;
        }
        
        tbody.innerHTML = jobs.map(job => {
            const statusBadge = this.getStatusBadge(job.status);
            const typeIcon = this.getTypeIcon(job.type);
            const duration = this.calculateDuration(job.started_at, job.finished_at);
            
            return `
                <tr>
                    <td>${typeIcon} ${job.type}</td>
                    <td>${statusBadge}</td>
                    <td>${job.source_db || '-'} → ${job.target_db || '-'}</td>
                    <td>${job.created_by_username || 'Sistema'}</td>
                    <td>${this.formatDateTime(job.started_at)}</td>
                    <td>${duration}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-info" onclick="DatabaseManager.viewJobDetails(${job.id})">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    },

    /**
     * Retorna badge HTML para status
     */
    getStatusBadge(status) {
        const badges = {
            'pending': '<span class="badge bg-secondary">Pendente</span>',
            'running': '<span class="badge bg-primary">Em execução</span>',
            'success': '<span class="badge bg-success">Sucesso</span>',
            'failed': '<span class="badge bg-danger">Falhou</span>',
            'cancelled': '<span class="badge bg-warning">Cancelado</span>'
        };
        
        return badges[status] || '<span class="badge bg-secondary">-</span>';
    },

    /**
     * Retorna ícone para tipo de job
     */
    getTypeIcon(type) {
        const icons = {
            'sync': '<i class="fas fa-sync"></i>',
            'backup': '<i class="fas fa-download"></i>',
            'restore': '<i class="fas fa-upload"></i>',
            'init': '<i class="fas fa-plus-circle"></i>',
            'test': '<i class="fas fa-heartbeat"></i>'
        };
        
        return icons[type] || '<i class="fas fa-cog"></i>';
    },

    /**
     * Calcula duração entre duas datas
     */
    calculateDuration(start, end) {
        if (!start) return '-';
        if (!end) return 'Em andamento';
        
        const startDate = new Date(start);
        const endDate = new Date(end);
        const diff = endDate - startDate;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    },

    /**
     * Formata data e hora
     */
    formatDateTime(datetime) {
        if (!datetime) return '-';
        
        const date = new Date(datetime);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Sincroniza banco (Neon → Local)
     */
    async syncDatabase() {
        if (!confirm('Sincronizar Neon → Local? Isso pode demorar vários minutos.')) {
            return;
        }
        
        try {
            const response = await fetch('/admin/database/api/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao iniciar sincronização');
            }
            
            this.showToast('Sincronização iniciada', 'success');
            this.startJobMonitoring(data.job_id, 'Sincronizando Neon → Local');
            
        } catch (error) {
            console.error('Erro ao sincronizar:', error);
            this.showToast('Erro ao iniciar sincronização: ' + error.message, 'error');
        }
    },

    /**
     * Inicializa banco local
     */
    async initDatabase() {
        const dbType = prompt('Qual tipo de banco inicializar?\n\nDigite:\n- "sqlite" para SQLite\n- "postgres" para PostgreSQL', 'sqlite');
        
        if (!dbType || !['sqlite', 'postgres'].includes(dbType)) {
            return;
        }
        
        try {
            const response = await fetch('/admin/database/api/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ db_type: dbType })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao inicializar banco');
            }
            
            this.showToast('Inicialização iniciada', 'success');
            this.startJobMonitoring(data.job_id, `Inicializando ${dbType}`);
            
        } catch (error) {
            console.error('Erro ao inicializar:', error);
            this.showToast('Erro ao inicializar: ' + error.message, 'error');
        }
    },

    /**
     * Cria backup do banco
     */
    async backupDatabase() {
        if (!confirm('Criar backup do banco de dados ativo?')) {
            return;
        }
        
        try {
            const response = await fetch('/admin/database/api/backup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao criar backup');
            }
            
            this.showToast('Backup iniciado', 'success');
            this.startJobMonitoring(data.job_id, 'Criando Backup');
            
        } catch (error) {
            console.error('Erro ao criar backup:', error);
            this.showToast('Erro ao criar backup: ' + error.message, 'error');
        }
    },

    /**
     * Testa conexão
     */
    async testConnection() {
        const dbUrl = prompt('URL do banco de dados para testar:');
        if (!dbUrl) return;
        
        try {
            const response = await fetch('/admin/database/api/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    db_url: dbUrl,
                    db_type: 'test'
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao testar conexão');
            }
            
            this.showToast('Teste de conexão iniciado', 'success');
            this.startJobMonitoring(data.job_id, 'Testando Conexão');
            
        } catch (error) {
            console.error('Erro ao testar conexão:', error);
            this.showToast('Erro ao testar: ' + error.message, 'error');
        }
    },

    /**
     * Inicia monitoramento de job via SSE
     */
    startJobMonitoring(jobId, title) {
        this.currentJobId = jobId;
        
        // Mostrar área de progresso
        const container = document.getElementById('progress-container');
        container.classList.add('active');
        
        // Atualizar título
        document.getElementById('progress-title').textContent = title;
        
        // Resetar progresso
        this.updateProgress(0);
        document.getElementById('progress-logs').innerHTML = '';
        
        // Fechar EventSource anterior se existir
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Criar novo EventSource
        this.eventSource = new EventSource(`/admin/database/api/events/${jobId}`);
        
        // Listener para progresso
        this.eventSource.addEventListener('progress', (e) => {
            const job = JSON.parse(e.data);
            this.updateJobProgress(job);
        });
        
        // Listener para conclusão
        this.eventSource.addEventListener('completed', (e) => {
            const job = JSON.parse(e.data);
            this.updateJobProgress(job);
            this.finishJobMonitoring(job);
        });
        
        // Listener para erros
        this.eventSource.addEventListener('error', (e) => {
            console.error('SSE Error:', e);
            this.showToast('Erro na conexão de monitoramento', 'error');
            this.eventSource.close();
        });
        
        // Listener para timeout
        this.eventSource.addEventListener('timeout', (e) => {
            this.showToast('Timeout ao aguardar conclusão', 'warning');
            this.finishJobMonitoring(null);
        });
    },

    /**
     * Atualiza progresso do job
     */
    updateJobProgress(job) {
        // Atualizar barra de progresso
        this.updateProgress(job.progress || 0);
        
        // Adicionar logs
        if (job.logs && job.logs.length > 0) {
            const logsContainer = document.getElementById('progress-logs');
            job.logs.forEach(log => {
                if (!logsContainer.querySelector(`[data-log-id="${log.timestamp}"]`)) {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry ${log.level || 'info'}`;
                    logEntry.setAttribute('data-log-id', log.timestamp);
                    logEntry.textContent = `[${this.formatDateTime(log.timestamp)}] ${log.message}`;
                    logsContainer.appendChild(logEntry);
                    
                    // Auto-scroll para o fim
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }
            });
        }
    },

    /**
     * Finaliza monitoramento de job
     */
    finishJobMonitoring(job) {
        this.currentJobId = null;
        
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        
        if (job) {
            if (job.status === 'success') {
                this.showToast('Operação concluída com sucesso!', 'success');
            } else if (job.status === 'failed') {
                this.showToast('Operação falhou. Verifique os logs.', 'error');
            }
        }
        
        // Atualizar histórico e status
        setTimeout(() => {
            this.loadHistory();
            this.loadStatus();
            
            // Esconder área de progresso após 5 segundos
            setTimeout(() => {
                document.getElementById('progress-container').classList.remove('active');
            }, 5000);
        }, 1000);
    },

    /**
     * Atualiza barra de progresso
     */
    updateProgress(percent) {
        const percentInt = Math.round(percent);
        const percentText = percentInt + '%';
        
        // Atualizar barra principal
        const bar = document.getElementById('progress-bar');
        bar.style.width = percentInt + '%';
        bar.setAttribute('aria-valuenow', percentInt);
        
        // Atualizar texto dentro da barra
        const barText = document.getElementById('progress-bar-text');
        if (barText) {
            barText.textContent = percentText;
        }
        
        // Atualizar badge no header
        const badge = document.getElementById('progress-percentage-badge');
        if (badge) {
            badge.textContent = percentText;
            
            // Mudar cor do badge conforme progresso
            badge.className = 'badge';
            if (percentInt < 33) {
                badge.classList.add('badge-warning');
            } else if (percentInt < 66) {
                badge.classList.add('badge-info');
            } else if (percentInt < 100) {
                badge.classList.add('badge-primary');
            } else {
                badge.classList.add('badge-success');
            }
            badge.style.fontSize = '1.1rem';
            badge.style.padding = '8px 15px';
        }
        
        // Atualizar texto acima da barra
        const percentageText = document.getElementById('progress-percentage-text');
        if (percentageText) {
            percentageText.textContent = percentText;
        }
        
        // Mudar cor da barra conforme progresso
        bar.className = 'progress-bar progress-bar-striped progress-bar-animated';
        if (percentInt < 33) {
            bar.classList.add('bg-warning');
        } else if (percentInt < 66) {
            bar.classList.add('bg-info');
        } else if (percentInt < 100) {
            bar.classList.add('bg-primary');
        } else {
            bar.classList.add('bg-success');
        }
        bar.style.fontSize = '1.1rem';
        bar.style.fontWeight = 'bold';
    },

    /**
     * Exibe detalhes de um job
     */
    async viewJobDetails(jobId) {
        try {
            const response = await fetch(`/admin/database/api/sync/${jobId}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar detalhes');
            }
            
            const job = data.job;
            
            alert(`Job #${job.id}
Tipo: ${job.type}
Status: ${job.status}
Origem: ${job.source_db || '-'}
Destino: ${job.target_db || '-'}
Progresso: ${job.progress}%
Iniciado: ${this.formatDateTime(job.started_at)}
Concluído: ${this.formatDateTime(job.finished_at)}
Duração: ${this.calculateDuration(job.started_at, job.finished_at)}

Logs: ${job.logs ? job.logs.length : 0} entradas`);
            
        } catch (error) {
            console.error('Erro ao carregar detalhes:', error);
            this.showToast('Erro ao carregar detalhes: ' + error.message, 'error');
        }
    },

    /**
     * Atualiza status manualmente
     */
    refreshStatus() {
        this.loadStatus();
        this.loadHistory();
        this.showToast('Status atualizado', 'info');
    },

    /**
     * Exibe toast de notificação
     */
    showToast(message, type = 'info') {
        // Se houver sistema de toasts no projeto, usar
        // Caso contrário, usar alert simples
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Tentar usar Bootstrap toast se disponível
        if (typeof bootstrap !== 'undefined') {
            // TODO: Implementar toast do Bootstrap
        }
        
        // Fallback para alert
        if (type === 'error') {
            alert('Erro: ' + message);
        }
    }
};

// Funções globais para os botões
function syncDatabase() {
    DatabaseManager.syncDatabase();
}

function initDatabase() {
    DatabaseManager.initDatabase();
}

function backupDatabase() {
    DatabaseManager.backupDatabase();
}

function testConnection() {
    DatabaseManager.testConnection();
}

function refreshStatus() {
    DatabaseManager.refreshStatus();
}

function switchToDatabase(dbType) {
    alert('Alternar banco requer reiniciar a aplicação.\n\nEm desenvolvimento.');
}
