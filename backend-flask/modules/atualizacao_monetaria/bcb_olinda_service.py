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
        """
        Busca cotação PTAX de uma moeda para uma data específica
        
        Args:
            data: Data da cotação
            moeda: Código da moeda (USD, EUR, GBP, etc.)
            
        Returns:
            Dict com cotações de compra e venda
        """
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
                cotacao = dados['value'][-1]  # Última cotação do dia
                return {
                    'moeda': moeda,
                    'data': data.isoformat(),
                    'cotacao_compra': float(cotacao.get('cotacaoCompra', 0)),
                    'cotacao_venda': float(cotacao.get('cotacaoVenda', 0)),
                    'paridade_compra': float(cotacao.get('paridadeCompra', 1)),
                    'paridade_venda': float(cotacao.get('paridadeVenda', 1)),
                    'hora': cotacao.get('dataHoraCotacao', '')
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar PTAX {moeda}: {e}")
            return None
    
    @staticmethod
    def buscar_ptax_periodo(data_inicio: date, data_fim: date, moeda: str = 'USD') -> List[Dict]:
        """
        Busca cotações PTAX de um período
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            moeda: Código da moeda
            
        Returns:
            Lista de cotações diárias
        """
        inicio_str = data_inicio.strftime('%m-%d-%Y')
        fim_str = data_fim.strftime('%m-%d-%Y')
        
        url = f"{BCBOlindaService.PTAX_BASE}/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@inicio,dataFinalCotacao=@fim)"
        params = {
            '@moeda': f"'{moeda}'",
            '@inicio': f"'{inicio_str}'",
            '@fim': f"'{fim_str}'",
            '$format': 'json',
            '$orderby': 'dataHoraCotacao desc'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            dados = response.json()
            
            resultado = []
            for item in dados.get('value', []):
                resultado.append({
                    'moeda': moeda,
                    'data': item.get('dataHoraCotacao', '')[:10],
                    'cotacao_compra': float(item.get('cotacaoCompra', 0)),
                    'cotacao_venda': float(item.get('cotacaoVenda', 0)),
                    'tipo': item.get('tipoBoletim', 'Fechamento')
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar PTAX período: {e}")
            return []
    
    @staticmethod
    def listar_moedas_disponiveis() -> List[Dict]:
        """Lista todas as moedas disponíveis na PTAX"""
        url = f"{BCBOlindaService.PTAX_BASE}/Moedas"
        params = {'$format': 'json'}
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            dados = response.json()
            
            return [
                {
                    'simbolo': m.get('simbolo'),
                    'nome': m.get('nomeFormatado'),
                    'tipo': m.get('tipoMoeda')
                }
                for m in dados.get('value', [])
            ]
            
        except Exception as e:
            logger.error(f"Erro ao listar moedas: {e}")
            return []
    
    # ============================================================================
    # EXPECTATIVAS DE MERCADO (FOCUS)
    # ============================================================================
    
    @staticmethod
    def buscar_expectativas_mercado(indicador: str = 'IPCA', top: int = 10) -> List[Dict]:
        """
        Busca expectativas de mercado (Relatório Focus)
        
        Args:
            indicador: IPCA, Selic, PIB, Câmbio, IGP-M, etc.
            top: Número de registros
            
        Returns:
            Lista de expectativas
        """
        url = f"{BCBOlindaService.EXPECTATIVAS_BASE}/ExpectativasMercadoAnuais"
        params = {
            '$filter': f"Indicador eq '{indicador}'",
            '$top': top,
            '$orderby': 'Data desc',
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            dados = response.json()
            
            resultado = []
            for item in dados.get('value', []):
                resultado.append({
                    'indicador': item.get('Indicador'),
                    'data': item.get('Data'),
                    'data_referencia': item.get('DataReferencia'),
                    'media': float(item.get('Media', 0)),
                    'mediana': float(item.get('Mediana', 0)),
                    'desvio_padrao': float(item.get('DesvioPadrao', 0)),
                    'minimo': float(item.get('Minimo', 0)),
                    'maximo': float(item.get('Maximo', 0)),
                    'num_respondentes': item.get('numeroRespondentes', 0)
                })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar expectativas {indicador}: {e}")
            return []
    
    @staticmethod
    def buscar_expectativas_top5() -> List[Dict]:
        """
        Busca expectativas Top 5 (instituições mais precisas)
        """
        url = f"{BCBOlindaService.EXPECTATIVAS_BASE}/ExpectativasMercadoTop5Anuais"
        params = {
            '$top': 20,
            '$orderby': 'Data desc',
            '$format': 'json'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            dados = response.json()
            
            return [
                {
                    'indicador': item.get('Indicador'),
                    'data': item.get('Data'),
                    'data_referencia': item.get('DataReferencia'),
                    'tipo_calculo': item.get('tipoCalculo'),
                    'media': float(item.get('Media', 0)),
                    'mediana': float(item.get('Mediana', 0))
                }
                for item in dados.get('value', [])
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar Top 5: {e}")
            return []
    
    @staticmethod  
    def buscar_expectativas_selic() -> List[Dict]:
        """Busca expectativas para a taxa Selic"""
        return BCBOlindaService.buscar_expectativas_mercado('Selic', 30)
    
    @staticmethod
    def buscar_expectativas_ipca() -> List[Dict]:
        """Busca expectativas para o IPCA"""
        return BCBOlindaService.buscar_expectativas_mercado('IPCA', 30)
    
    @staticmethod
    def buscar_expectativas_pib() -> List[Dict]:
        """Busca expectativas para o PIB"""
        return BCBOlindaService.buscar_expectativas_mercado('PIB Total', 30)
    
    @staticmethod
    def buscar_expectativas_cambio() -> List[Dict]:
        """Busca expectativas para o Câmbio"""
        return BCBOlindaService.buscar_expectativas_mercado('Câmbio', 30)


# ============================================================================
# ROTAS FLASK
# ============================================================================

def registrar_rotas_olinda(app):
    """Registra endpoints da API Olinda"""
    from flask import Blueprint, jsonify, request
    
    olinda_bp = Blueprint('olinda', __name__, url_prefix='/api/bcb')
    
    @olinda_bp.route('/ptax/hoje', methods=['GET'])
    def ptax_hoje():
        """Cotação PTAX de hoje"""
        moeda = request.args.get('moeda', 'USD')
        resultado = BCBOlindaService.buscar_ptax_dia(date.today(), moeda)
        
        if not resultado:
            # Tentar dia anterior (fim de semana/feriado)
            resultado = BCBOlindaService.buscar_ptax_dia(date.today() - timedelta(days=1), moeda)
        
        if resultado:
            return jsonify(resultado)
        return jsonify({'erro': 'Cotação não disponível'}), 404
    
    @olinda_bp.route('/ptax/periodo', methods=['GET'])
    def ptax_periodo():
        """Cotações PTAX de um período"""
        moeda = request.args.get('moeda', 'USD')
        dias = request.args.get('dias', 30, type=int)
        
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)
        
        resultado = BCBOlindaService.buscar_ptax_periodo(data_inicio, data_fim, moeda)
        return jsonify(resultado)
    
    @olinda_bp.route('/ptax/moedas', methods=['GET'])
    def moedas_disponiveis():
        """Lista moedas disponíveis"""
        return jsonify(BCBOlindaService.listar_moedas_disponiveis())
    
    @olinda_bp.route('/expectativas/<indicador>', methods=['GET'])
    def expectativas_indicador(indicador):
        """Expectativas de mercado para um indicador"""
        top = request.args.get('top', 20, type=int)
        resultado = BCBOlindaService.buscar_expectativas_mercado(indicador, top)
        return jsonify(resultado)
    
    @olinda_bp.route('/expectativas/resumo', methods=['GET'])
    def expectativas_resumo():
        """Resumo de todas as expectativas principais"""
        return jsonify({
            'selic': BCBOlindaService.buscar_expectativas_selic()[:5],
            'ipca': BCBOlindaService.buscar_expectativas_ipca()[:5],
            'pib': BCBOlindaService.buscar_expectativas_pib()[:5],
            'cambio': BCBOlindaService.buscar_expectativas_cambio()[:5]
        })
    
    @olinda_bp.route('/expectativas/top5', methods=['GET'])
    def expectativas_top5():
        """Expectativas Top 5"""
        return jsonify(BCBOlindaService.buscar_expectativas_top5())
    
    app.register_blueprint(olinda_bp)
    return olinda_bp
