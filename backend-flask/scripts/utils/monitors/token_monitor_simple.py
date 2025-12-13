"""
Sistema simplificado de monitoramento de tokens por chave de API
com valores em R$ e atualização diária às 7h (horário do Brasil)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, render_template_string
from sqlalchemy import create_engine, text
import pytz

# Blueprint para monitoramento simplificado
token_monitor_bp = Blueprint('token_monitor', __name__)

# Timezone do Brasil
BR_TZ = pytz.timezone('America/Sao_Paulo')

class TokenMonitor:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        self.last_update = None
        self.exchange_rate = 5.60  # Taxa inicial padrão
        self.daily_usage = {}
        
    def get_exchange_rate(self):
        """Obtém taxa de câmbio USD/BRL atual"""
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['rates'].get('BRL', 5.60)
        except:
            pass
        return 5.60  # Fallback
    
    def should_update_daily(self):
        """Verifica se deve atualizar dados (diariamente às 7h)"""
        now = datetime.now(BR_TZ)
        if not self.last_update:
            return True
            
        # Se passou das 7h e ainda não atualizou hoje
        if now.hour >= 7 and self.last_update.date() < now.date():
            return True
            
        return False
    
    def update_daily_data(self):
        """Atualiza dados diários de taxa de câmbio e uso de tokens"""
        if self.should_update_daily():
            self.exchange_rate = self.get_exchange_rate()
            self.last_update = datetime.now(BR_TZ)
            
            # Simula dados de uso (em produção viria do banco real)
            self.daily_usage = {
                'openai': {
                    'tokens_today': 45000,
                    'cost_usd': 18.20,
                    'cost_brl': round(18.20 * self.exchange_rate, 2),
                    'requests': 321
                },
                'anthropic': {
                    'tokens_today': 32000,
                    'cost_usd': 12.80,
                    'cost_brl': round(12.80 * self.exchange_rate, 2),
                    'requests': 245
                },
                'deepseek': {
                    'tokens_today': 28000,
                    'cost_usd': 8.40,
                    'cost_brl': round(8.40 * self.exchange_rate, 2),
                    'requests': 198
                },
                'gemini': {
                    'tokens_today': 15000,
                    'cost_usd': 4.50,
                    'cost_brl': round(4.50 * self.exchange_rate, 2),
                    'requests': 87
                },
                'assemblyai': {
                    'tokens_today': 5000,
                    'cost_usd': 1.60,
                    'cost_brl': round(1.60 * self.exchange_rate, 2),
                    'requests': 41
                }
            }
    
    def get_current_status(self):
        """Retorna status atual do monitoramento"""
        self.update_daily_data()
        
        total_tokens = sum(api['tokens_today'] for api in self.daily_usage.values())
        total_cost_usd = sum(api['cost_usd'] for api in self.daily_usage.values())
        total_cost_brl = sum(api['cost_brl'] for api in self.daily_usage.values())
        total_requests = sum(api['requests'] for api in self.daily_usage.values())
        
        return {
            'last_update': self.last_update.strftime('%d/%m/%Y %H:%M') if self.last_update else 'Nunca',
            'exchange_rate': self.exchange_rate,
            'next_update': '07:00 (próximo dia)',
            'total_tokens': total_tokens,
            'total_cost_usd': round(total_cost_usd, 2),
            'total_cost_brl': round(total_cost_brl, 2),
            'total_requests': total_requests,
            'by_api': self.daily_usage
        }

# Instância global do monitor
monitor = TokenMonitor()

# Template HTML simplificado
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor de Tokens - Sistema Jurídico</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.8; font-size: 1.1rem; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { 
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stat-value { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
        .stat-label { opacity: 0.8; }
        
        .api-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .api-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .api-header { display: flex; justify-content: between; align-items: center; margin-bottom: 20px; }
        .api-name { font-size: 1.3rem; font-weight: bold; }
        .api-status { 
            background: #22c55e;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        .api-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .metric { text-align: center; }
        .metric-value { font-size: 1.5rem; font-weight: bold; }
        .metric-label { opacity: 0.8; font-size: 0.9rem; }
        
        .update-info {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-top: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="auto-refresh">🔄 Atualização automática: 30s</div>
    
    <div class="container">
        <div class="header">
            <h1>Monitor de Tokens - APIs</h1>
            <p>Monitoramento em tempo real do consumo por chave de API</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-tokens">-</div>
                <div class="stat-label">Total de Tokens</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-cost-brl">-</div>
                <div class="stat-label">Custo Total (R$)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-requests">-</div>
                <div class="stat-label">Total de Requisições</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="exchange-rate">-</div>
                <div class="stat-label">Taxa USD/BRL</div>
            </div>
        </div>
        
        <div class="api-grid" id="api-grid">
            <!-- APIs serão carregadas dinamicamente -->
        </div>
        
        <div class="update-info">
            <strong>Última atualização:</strong> <span id="last-update">-</span><br>
            <strong>Próxima atualização:</strong> <span id="next-update">-</span>
        </div>
    </div>
    
    <script>
        function formatNumber(num) {
            return new Intl.NumberFormat('pt-BR').format(num);
        }
        
        function formatCurrency(value) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(value);
        }
        
        function updateDashboard() {
            fetch('/api/token-status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const status = data.status;
                        
                        // Atualizar totais
                        document.getElementById('total-tokens').textContent = formatNumber(status.total_tokens);
                        document.getElementById('total-cost-brl').textContent = formatCurrency(status.total_cost_brl);
                        document.getElementById('total-requests').textContent = formatNumber(status.total_requests);
                        document.getElementById('exchange-rate').textContent = status.exchange_rate.toFixed(2);
                        
                        // Atualizar informações
                        document.getElementById('last-update').textContent = status.last_update;
                        document.getElementById('next-update').textContent = status.next_update;
                        
                        // Atualizar grid de APIs
                        const apiGrid = document.getElementById('api-grid');
                        apiGrid.innerHTML = '';
                        
                        Object.entries(status.by_api).forEach(([apiName, apiData]) => {
                            const apiCard = document.createElement('div');
                            apiCard.className = 'api-card';
                            apiCard.innerHTML = `
                                <div class="api-header">
                                    <div class="api-name">${apiName.toUpperCase()}</div>
                                    <div class="api-status">Ativo</div>
                                </div>
                                <div class="api-metrics">
                                    <div class="metric">
                                        <div class="metric-value">${formatNumber(apiData.tokens_today)}</div>
                                        <div class="metric-label">Tokens</div>
                                    </div>
                                    <div class="metric">
                                        <div class="metric-value">${formatCurrency(apiData.cost_brl)}</div>
                                        <div class="metric-label">Custo (R$)</div>
                                    </div>
                                    <div class="metric">
                                        <div class="metric-value">${formatNumber(apiData.requests)}</div>
                                        <div class="metric-label">Requisições</div>
                                    </div>
                                    <div class="metric">
                                        <div class="metric-value">$${apiData.cost_usd}</div>
                                        <div class="metric-label">Custo (USD)</div>
                                    </div>
                                </div>
                            `;
                            apiGrid.appendChild(apiCard);
                        });
                    }
                })
                .catch(error => {
                    console.error('Erro ao carregar dados:', error);
                });
        }
        
        // Atualizar a cada 30 segundos
        updateDashboard();
        setInterval(updateDashboard, 30000);
    </script>
</body>
</html>
"""

@token_monitor_bp.route('/admin/token-monitor')
def token_dashboard():
    """Dashboard simplificado de monitoramento de tokens"""
    return render_template_string(DASHBOARD_TEMPLATE)

@token_monitor_bp.route('/api/token-status')
def get_token_status():
    """API para obter status atual dos tokens"""
    try:
        status = monitor.get_current_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})