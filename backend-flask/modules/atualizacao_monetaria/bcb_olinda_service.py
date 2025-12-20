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
    
    app.register_blueprint(olinda_bp)
    return olinda_bp
