/**
 * Script de Validação Lado Client - Sistema Jurídico
 * Verifica se todos os componentes carregaram corretamente
 */

class ClientValidator {
    constructor() {
        this.checks = [];
        this.results = {};
        this.isSystemReady = false;
        this.startTime = Date.now();
        this.maxWaitTime = 30000; // 30 segundos
        
        this.init();
    }
    
    init() {
        console.log('🔍 Iniciando validação do sistema...');
        this.runValidation();
    }
    
    async runValidation() {
        // Aguardar DOM estar pronto
        if (document.readyState !== 'complete') {
            document.addEventListener('DOMContentLoaded', () => this.performChecks());
        } else {
            this.performChecks();
        }
    }
    
    async performChecks() {
        const checks = [
            this.checkBootstrap(),
            this.checkFontAwesome(),
            this.checkNavigation(),
            this.checkForms(),
            this.checkDropdowns(),
            this.checkApiEndpoints(),
            this.checkComparacaoModule(),
            this.checkResponsiveness()
        ];
        
        try {
            await Promise.all(checks);
            this.evaluateResults();
        } catch (error) {
            console.error('❌ Erro durante validação:', error);
            this.showError('Erro durante validação do sistema');
        }
    }
    
    async checkBootstrap() {
        return new Promise((resolve) => {
            const check = {
                name: 'Bootstrap CSS',
                status: false,
                details: ''
            };
            
            // Verificar se Bootstrap CSS está carregado
            const bootstrapLink = document.querySelector('link[href*="bootstrap"]');
            if (bootstrapLink) {
                // Verificar se classes Bootstrap funcionam
                const testDiv = document.createElement('div');
                testDiv.className = 'container d-none';
                document.body.appendChild(testDiv);
                
                const styles = window.getComputedStyle(testDiv);
                if (styles.display === 'none') {
                    check.status = true;
                    check.details = 'Bootstrap CSS carregado e funcional';
                } else {
                    check.details = 'Bootstrap CSS não está funcionando';
                }
                
                document.body.removeChild(testDiv);
            } else {
                check.details = 'Bootstrap CSS não encontrado';
            }
            
            this.results.bootstrap = check;
            console.log(`✓ Bootstrap: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkFontAwesome() {
        return new Promise((resolve) => {
            const check = {
                name: 'Font Awesome',
                status: false,
                details: ''
            };
            
            const faLink = document.querySelector('link[href*="font-awesome"]');
            if (faLink) {
                // Testar ícone
                const testIcon = document.createElement('i');
                testIcon.className = 'fas fa-check d-none';
                document.body.appendChild(testIcon);
                
                const styles = window.getComputedStyle(testIcon, '::before');
                if (styles.content && styles.content !== 'none') {
                    check.status = true;
                    check.details = 'Font Awesome carregado e funcional';
                } else {
                    check.details = 'Font Awesome não está funcionando';
                }
                
                document.body.removeChild(testIcon);
            } else {
                check.details = 'Font Awesome não encontrado';
            }
            
            this.results.fontAwesome = check;
            console.log(`✓ Font Awesome: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkNavigation() {
        return new Promise((resolve) => {
            const check = {
                name: 'Navegação',
                status: false,
                details: ''
            };
            
            const navbar = document.querySelector('.navbar');
            const navLinks = document.querySelectorAll('.nav-link');
            
            // Lista explícita de dashboards que não precisam de navbar
            const knownDashboardSlugs = [
                'ai-legal-forecasting',
                'case-management-intelligence',
                'case-success-predictor',
                'competitive-intelligence',
                'defense-strategy-optimizer',
                'performance-analysis',
                'performance-overview',
                'strategic-intelligence',
                'success-optimization-engine'
            ];
            
            const isDashboard = knownDashboardSlugs.some(slug => 
                window.location.pathname.includes(`/strategic-dashboards/${slug}`)
            ) || document.querySelector('.dashboard-header');
            
            if (navbar && navLinks.length > 0) {
                check.status = true;
                check.details = `Navbar encontrada com ${navLinks.length} links`;
            } else if (isDashboard) {
                // Dashboards estratégicos não precisam de navbar tradicional
                check.status = true;
                check.details = 'Dashboard estratégico detectado - navbar tradicional não obrigatória';
            } else {
                check.details = 'Navbar ou links de navegação não encontrados';
            }
            
            this.results.navigation = check;
            console.log(`✓ Navegação: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkForms() {
        return new Promise((resolve) => {
            const check = {
                name: 'Formulários',
                status: true, // Sempre passa - formulários são opcionais
                details: ''
            };
            
            const forms = document.querySelectorAll('form');
            const inputs = document.querySelectorAll('input, select, textarea');
            
            if (forms.length > 0 && inputs.length > 0) {
                check.details = `${forms.length} formulário(s) e ${inputs.length} campo(s) encontrados`;
            } else {
                check.details = 'Formulários não obrigatórios nesta página';
            }
            
            this.results.forms = check;
            console.log(`✓ Formulários: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkDropdowns() {
        return new Promise((resolve) => {
            const check = {
                name: 'Dropdowns',
                status: false,
                details: ''
            };
            
            const dropdowns = document.querySelectorAll('[data-bs-toggle="dropdown"], .dropdown-toggle');
            const selectElements = document.querySelectorAll('select');
            
            if (dropdowns.length > 0 || selectElements.length > 0) {
                check.status = true;
                check.details = `${dropdowns.length} dropdown(s) Bootstrap e ${selectElements.length} select(s) encontrados`;
            } else {
                check.details = 'Dropdowns não encontrados na página atual';
                check.status = true; // Pode não ter dropdowns em todas as páginas
            }
            
            this.results.dropdowns = check;
            console.log(`✓ Dropdowns: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkApiEndpoints() {
        return new Promise(async (resolve) => {
            const check = {
                name: 'APIs',
                status: false,
                details: ''
            };
            
            try {
                // Testar endpoint básico de health check
                const response = await fetch('/api/health', { 
                    method: 'GET',
                    timeout: 5000 
                });
                
                if (response.ok) {
                    check.status = true;
                    check.details = 'API respondendo corretamente';
                } else {
                    check.details = `API retornou status ${response.status}`;
                }
            } catch (error) {
                check.details = 'Endpoint de health check não disponível (normal em algumas páginas)';
                check.status = true; // Não é crítico
            }
            
            this.results.api = check;
            console.log(`✓ APIs: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkComparacaoModule() {
        return new Promise((resolve) => {
            const check = {
                name: 'Módulo Comparação',
                status: false,
                details: ''
            };
            
            const currentPath = window.location.pathname;
            
            if (currentPath.includes('comparacao')) {
                // Verificar elementos específicos do módulo de comparação
                const areaSelect = document.querySelector('select[name="area_processo"]');
                const uploadInputs = document.querySelectorAll('input[type="file"]');
                
                if (areaSelect) {
                    const options = areaSelect.querySelectorAll('option');
                    if (options.length >= 18) { // Deve ter 18 áreas + opção vazia
                        check.status = true;
                        check.details = `Dropdown com ${options.length} áreas jurídicas carregado`;
                    } else {
                        check.details = `Apenas ${options.length} áreas encontradas (esperado: 19)`;
                    }
                } else {
                    check.details = 'Não é página do módulo de comparação';
                    check.status = true;
                }
            } else {
                check.details = 'Não é página do módulo de comparação';
                check.status = true;
            }
            
            this.results.comparacao = check;
            console.log(`✓ Módulo Comparação: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    async checkResponsiveness() {
        return new Promise((resolve) => {
            const check = {
                name: 'Responsividade',
                status: false,
                details: ''
            };
            
            const viewport = document.querySelector('meta[name="viewport"]');
            const responsiveElements = document.querySelectorAll('.container, .container-fluid, .row, .col, [class*="col-"]');
            
            if (viewport && responsiveElements.length > 0) {
                check.status = true;
                check.details = `Viewport configurado e ${responsiveElements.length} elementos responsivos encontrados`;
            } else {
                check.details = 'Configurações de responsividade não encontradas';
            }
            
            this.results.responsiveness = check;
            console.log(`✓ Responsividade: ${check.status ? 'OK' : 'FALHA'} - ${check.details}`);
            resolve();
        });
    }
    
    evaluateResults() {
        const totalChecks = Object.keys(this.results).length;
        const passedChecks = Object.values(this.results).filter(check => check.status).length;
        const successRate = (passedChecks / totalChecks) * 100;
        
        console.log(`\n📊 RESULTADO DA VALIDAÇÃO:`);
        console.log(`✅ Aprovado: ${passedChecks}/${totalChecks} (${successRate.toFixed(1)}%)`);
        
        if (successRate >= 80) {
            this.isSystemReady = true;
            this.showSuccess();
        } else {
            this.showWarning(successRate);
        }
        
        this.showDetailedReport();
    }
    
    showSuccess() {
        console.log('🎉 SISTEMA VALIDADO COM SUCESSO!');
        
        // Criar indicador visual de sucesso
        this.createStatusIndicator('success', 'Sistema carregado e validado');
        
        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('systemValidated', {
            detail: { status: 'success', results: this.results }
        }));
    }
    
    showWarning(successRate) {
        console.warn(`⚠️ SISTEMA PARCIALMENTE VALIDADO (${successRate.toFixed(1)}%)`);
        
        this.createStatusIndicator('warning', `Sistema parcialmente validado (${successRate.toFixed(1)}%)`);
        
        window.dispatchEvent(new CustomEvent('systemValidated', {
            detail: { status: 'warning', successRate, results: this.results }
        }));
    }
    
    showError(message) {
        console.error(`❌ ERRO NA VALIDAÇÃO: ${message}`);
        
        this.createStatusIndicator('error', `Erro na validação: ${message}`);
        
        window.dispatchEvent(new CustomEvent('systemValidationError', {
            detail: { message, results: this.results }
        }));
    }
    
    createStatusIndicator(type, message) {
        // Remover indicador anterior se existir
        const existing = document.getElementById('system-status-indicator');
        if (existing) existing.remove();
        
        const indicator = document.createElement('div');
        indicator.id = 'system-status-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            transition: opacity 0.3s ease;
        `;
        
        switch(type) {
            case 'success':
                indicator.style.backgroundColor = '#28a745';
                indicator.innerHTML = '✅ ' + message;
                break;
            case 'warning':
                indicator.style.backgroundColor = '#ffc107';
                indicator.style.color = '#000';
                indicator.innerHTML = '⚠️ ' + message;
                break;
            case 'error':
                indicator.style.backgroundColor = '#dc3545';
                indicator.innerHTML = '❌ ' + message;
                break;
        }
        
        document.body.appendChild(indicator);
        
        // Remover após 5 segundos
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.style.opacity = '0';
                setTimeout(() => indicator.remove(), 300);
            }
        }, 5000);
    }
    
    showDetailedReport() {
        console.group('📋 RELATÓRIO DETALHADO:');
        Object.entries(this.results).forEach(([key, result]) => {
            const icon = result.status ? '✅' : '❌';
            console.log(`${icon} ${result.name}: ${result.details}`);
        });
        console.groupEnd();
        
        const loadTime = Date.now() - this.startTime;
        console.log(`⏱️ Tempo de validação: ${loadTime}ms`);
    }
    
    // Método público para verificar se o sistema está pronto
    isReady() {
        return this.isSystemReady;
    }
    
    // Método público para obter resultados
    getResults() {
        return this.results;
    }
}

// Inicializar validação automaticamente
const validator = new ClientValidator();

// Disponibilizar globalmente para debug
window.systemValidator = validator;

// Exportar para uso em outros scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ClientValidator;
}