"""
BCB Olinda API Integration
Integração com API Olinda do Banco Central para:
- PTAX (Cotação de Câmbio detalhada)
- Expectativas de Mercado (Focus)
"""
import requests
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BCBOlindaService:
    """
    Serviço de integração com API Olinda do Banco Central
    https://olinda.bcb.gov.br/
    """
    
    # URLs Base
    PTAX_BASE = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
    EXPECTATIVAS_BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata"
    
    # ============================================================================
    # PTAX - COTAÇÕES DE CÂMBIO
    # ============================================================================
    
    @staticmethod
    def buscar_ptax_dia(data: date, moeda: str = 'USD') -> Optional[Dict]:
        """Busca cotação PTAX de uma moeda para uma data específica"""
        data_str = data.strftime('%m-%d-%Y')
        url = f"{BCBOlindaService.PTAX_BASE}/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@data)"
        params = {
            '@moeda': f"'{moeda}'",
            '@data': f"'{data_str}'",
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            dados = response.json()
            
            if dados.get('value'):
                cotacao = dados['value'][-1]
                return {
                    'moeda': moeda,
                    'data': data.isoformat(),
                    'cotacao_compra': float(cotacao.get('cotacaoCompra', 0)),
                    'cotacao_venda': float(cotacao.get('cotacaoVenda', 0)),
                    'hora': cotacao.get('dataHoraCotacao', '')
                }
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar PTAX {moeda}: {e}")
            return None

    # ============================================================================
    # EXPECTATIVAS DE MERCADO (FOCUS)
    # ============================================================================
    
    @staticmethod
    def buscar_expectativa_generica(endpoint: str, indicador: str, top: int = 10) -> List[Dict]:
        """
        Busca expectativas genéricas usando endpoint especificado.
        Removemos $orderby da query para evitar erros de sintaxe OData e ordenamos no Python.
        """
        url = f"{BCBOlindaService.EXPECTATIVAS_BASE}/{endpoint}"
        
        # Filtro simples
        params = {
            '$filter': f"Indicador eq '{indicador}'",
            '$top': top * 2, # Busca um pouco mais para garantir após ordenação
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            dados = response.json()
            items = dados.get('value', [])
            
            # Ordenar por data decrescente (mais recente primeiro)
            # Campo data geralmente é "dyyyy-MM-dd"
            items.sort(key=lambda x: x.get('Data', ''), reverse=True)
            
            # Limitar ao top solicitado
            items = items[:top]
            
            resultado = []
            for item in items:
                resultado.append({
                    'indicador': item.get('Indicador'),
                    'data': item.get('Data'),
                    'data_referencia': item.get('DataReferencia'),
                    'media': float(item.get('Media', 0) or 0),
                    'mediana': float(item.get('Mediana', 0) or 0),
                    'minimo': float(item.get('Minimo', 0) or 0),
                    'maximo': float(item.get('Maximo', 0) or 0)
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar expectativas {indicador} em {endpoint}: {e}")
            return []
    
    @staticmethod
    def buscar_historico_expectativas(indicador: str, dias: int = 90) -> Dict[str, List]:
        """
        Busca histórico comparativo de expectativas (Mercado Geral vs Top 5)
        """
        data_limite = (date.today() - timedelta(days=dias)).strftime('%Y-%m-%d')
        
        # 1. Mercado Geral
        url_geral = f"{BCBOlindaService.EXPECTATIVAS_BASE}/ExpectativasMercadoAnuais"
        params_geral = {
            '$filter': f"Indicador eq '{indicador}' and Data gt '{data_limite}'",
            '$format': 'json'
        }
        
        # 2. Top 5
        url_top5 = f"{BCBOlindaService.EXPECTATIVAS_BASE}/ExpectativasMercadoTop5Anuais"
        params_top5 = {
            '$filter': f"Indicador eq '{indicador}' and Data gt '{data_limite}' and tipoCalculo eq 'C'",
            '$format': 'json'
        }
        
        resultado = {'geral': [], 'top5': []}
        
        try:
            # Busca Geral
            resp_geral = requests.get(url_geral, params=params_geral, timeout=10)
            if resp_geral.ok:
                data = resp_geral.json().get('value', [])
                # Filtrar para pegar apenas a expectativa para o ano corrente/próximo ano relevante
                # Geralmente queremos a expectativa para o ano calendário atual + 1
                ano_ref = date.today().year
                data_filtrada = [x for x in data if x.get('DataReferencia') == str(ano_ref)]
                resultado['geral'] = sorted(data_filtrada, key=lambda x: x['Data'])
            
            # Busca Top 5
            resp_top5 = requests.get(url_top5, params=params_top5, timeout=10)
            if resp_top5.ok:
                data = resp_top5.json().get('value', [])
                ano_ref = date.today().year
                data_filtrada = [x for x in data if x.get('DataReferencia') == str(ano_ref)]
                resultado['top5'] = sorted(data_filtrada, key=lambda x: x['Data'])
                
        except Exception as e:
            logger.error(f"Erro ao buscar histórico expectativas: {e}")
            
        return resultado

    @staticmethod
    def buscar_expectativas_selic() -> List[Dict]:
        return BCBOlindaService.buscar_expectativa_generica('ExpectativasMercadoAnuais', 'Selic')
    
    @staticmethod
    def buscar_expectativas_ipca() -> List[Dict]:
        return BCBOlindaService.buscar_expectativa_generica('ExpectativasMercadoAnuais', 'IPCA')
    
    @staticmethod
    def buscar_expectativas_pib() -> List[Dict]:
        return BCBOlindaService.buscar_expectativa_generica('ExpectativasMercadoAnuais', 'PIB Total')
    
    @staticmethod
    def buscar_expectativas_cambio() -> List[Dict]:
        return BCBOlindaService.buscar_expectativa_generica('ExpectativasMercadoAnuais', 'Câmbio')


# ============================================================================
# ROTAS FLASK
# ============================================================================

def registrar_rotas_olinda(app):
    from flask import Blueprint, jsonify, request
    olinda_bp = Blueprint('olinda', __name__, url_prefix='/api/bcb')
    
    @olinda_bp.route('/ptax/hoje', methods=['GET'])
    def ptax_hoje():
        moeda = request.args.get('moeda', 'USD')
        # Tenta hoje e volta até 4 dias para pegar último dia útil
        for i in range(5):
             data = date.today() - timedelta(days=i)
             resultado = BCBOlindaService.buscar_ptax_dia(data, moeda)
             if resultado:
                 return jsonify(resultado)
                 
        return jsonify({'erro': 'Cotação não disponível'}), 404
    
    @olinda_bp.route('/expectativas/resumo', methods=['GET'])
    def expectativas_resumo():
        return jsonify({
            'selic': BCBOlindaService.buscar_expectativas_selic(),
            'ipca': BCBOlindaService.buscar_expectativas_ipca(),
            'pib': BCBOlindaService.buscar_expectativas_pib(),
            'cambio': BCBOlindaService.buscar_expectativas_cambio()
        })

    @olinda_bp.route('/expectativas/historico/<indicador>', methods=['GET'])
    def expectativas_historico(indicador):
        dias = request.args.get('dias', 90, type=int)
        return jsonify(BCBOlindaService.buscar_historico_expectativas(indicador, dias))
    
    app.register_blueprint(olinda_bp)
    return olinda_bp
