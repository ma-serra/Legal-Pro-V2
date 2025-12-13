"""
Módulo de Integração com a API da Plataforma Judit
==================================================
Sistema completo de busca processual, monitoramento e consulta de documentos
através da API da Judit para escritórios de advocacia.

Autor: Legal Pro Team
Data: 2025-08-24
Versão: 1.0
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class JuditAPIClient:
    """Cliente para integração com a API da Judit"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente da API Judit
        
        Args:
            api_key: Chave da API Judit (opcional, busca de variável de ambiente)
        """
        self.api_key = api_key or os.environ.get('JUDIT_API_KEY')
        self.base_url_requests = "https://requests.prod.judit.io"
        self.base_url_tracking = "https://tracking.prod.judit.io"
        self.base_url_lawsuits = "https://lawsuits.production.judit.io"
        
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Tribunais cobertos pela API Judit organizados por tipo
        self.tribunais_brasil = {
            "tribunais_justica_estadual": {
                "nome": "Tribunais de Justiça Estaduais (TJ)",
                "descricao": "27 Tribunais de Justiça (um por estado + DF)",
                "tribunais": [
                    {"codigo": "TJAC", "nome": "Tribunal de Justiça do Acre", "uf": "AC"},
                    {"codigo": "TJAL", "nome": "Tribunal de Justiça de Alagoas", "uf": "AL"},
                    {"codigo": "TJAP", "nome": "Tribunal de Justiça do Amapá", "uf": "AP"},
                    {"codigo": "TJAM", "nome": "Tribunal de Justiça do Amazonas", "uf": "AM"},
                    {"codigo": "TJBA", "nome": "Tribunal de Justiça da Bahia", "uf": "BA"},
                    {"codigo": "TJCE", "nome": "Tribunal de Justiça do Ceará", "uf": "CE"},
                    {"codigo": "TJDF", "nome": "Tribunal de Justiça do Distrito Federal", "uf": "DF"},
                    {"codigo": "TJES", "nome": "Tribunal de Justiça do Espírito Santo", "uf": "ES"},
                    {"codigo": "TJGO", "nome": "Tribunal de Justiça de Goiás", "uf": "GO"},
                    {"codigo": "TJMA", "nome": "Tribunal de Justiça do Maranhão", "uf": "MA"},
                    {"codigo": "TJMT", "nome": "Tribunal de Justiça de Mato Grosso", "uf": "MT"},
                    {"codigo": "TJMS", "nome": "Tribunal de Justiça de Mato Grosso do Sul", "uf": "MS"},
                    {"codigo": "TJMG", "nome": "Tribunal de Justiça de Minas Gerais", "uf": "MG"},
                    {"codigo": "TJPA", "nome": "Tribunal de Justiça do Pará", "uf": "PA"},
                    {"codigo": "TJPB", "nome": "Tribunal de Justiça da Paraíba", "uf": "PB"},
                    {"codigo": "TJPR", "nome": "Tribunal de Justiça do Paraná", "uf": "PR"},
                    {"codigo": "TJPE", "nome": "Tribunal de Justiça de Pernambuco", "uf": "PE"},
                    {"codigo": "TJPI", "nome": "Tribunal de Justiça do Piauí", "uf": "PI"},
                    {"codigo": "TJRJ", "nome": "Tribunal de Justiça do Rio de Janeiro", "uf": "RJ"},
                    {"codigo": "TJRN", "nome": "Tribunal de Justiça do Rio Grande do Norte", "uf": "RN"},
                    {"codigo": "TJRS", "nome": "Tribunal de Justiça do Rio Grande do Sul", "uf": "RS"},
                    {"codigo": "TJRO", "nome": "Tribunal de Justiça de Rondônia", "uf": "RO"},
                    {"codigo": "TJRR", "nome": "Tribunal de Justiça de Roraima", "uf": "RR"},
                    {"codigo": "TJSC", "nome": "Tribunal de Justiça de Santa Catarina", "uf": "SC"},
                    {"codigo": "TJSP", "nome": "Tribunal de Justiça de São Paulo", "uf": "SP"},
                    {"codigo": "TJSE", "nome": "Tribunal de Justiça de Sergipe", "uf": "SE"},
                    {"codigo": "TJTO", "nome": "Tribunal de Justiça do Tocantins", "uf": "TO"}
                ]
            },
            "tribunais_trabalho": {
                "nome": "Tribunais Regionais do Trabalho (TRT)",
                "descricao": "24 Tribunais Regionais do Trabalho + TST",
                "tribunais": [
                    {"codigo": "TRT1", "nome": "TRT da 1ª Região", "regiao": "Rio de Janeiro"},
                    {"codigo": "TRT2", "nome": "TRT da 2ª Região", "regiao": "São Paulo"},
                    {"codigo": "TRT3", "nome": "TRT da 3ª Região", "regiao": "Minas Gerais"},
                    {"codigo": "TRT4", "nome": "TRT da 4ª Região", "regiao": "Rio Grande do Sul"},
                    {"codigo": "TRT5", "nome": "TRT da 5ª Região", "regiao": "Bahia"},
                    {"codigo": "TRT6", "nome": "TRT da 6ª Região", "regiao": "Pernambuco"},
                    {"codigo": "TRT7", "nome": "TRT da 7ª Região", "regiao": "Ceará"},
                    {"codigo": "TRT8", "nome": "TRT da 8ª Região", "regiao": "Pará e Amapá"},
                    {"codigo": "TRT9", "nome": "TRT da 9ª Região", "regiao": "Paraná"},
                    {"codigo": "TRT10", "nome": "TRT da 10ª Região", "regiao": "Distrito Federal e Tocantins"},
                    {"codigo": "TRT11", "nome": "TRT da 11ª Região", "regiao": "Amazonas e Roraima"},
                    {"codigo": "TRT12", "nome": "TRT da 12ª Região", "regiao": "Santa Catarina"},
                    {"codigo": "TRT13", "nome": "TRT da 13ª Região", "regiao": "Paraíba"},
                    {"codigo": "TRT14", "nome": "TRT da 14ª Região", "regiao": "Rondônia e Acre"},
                    {"codigo": "TRT15", "nome": "TRT da 15ª Região", "regiao": "Campinas e Região"},
                    {"codigo": "TRT16", "nome": "TRT da 16ª Região", "regiao": "Maranhão"},
                    {"codigo": "TRT17", "nome": "TRT da 17ª Região", "regiao": "Espírito Santo"},
                    {"codigo": "TRT18", "nome": "TRT da 18ª Região", "regiao": "Goiás"},
                    {"codigo": "TRT19", "nome": "TRT da 19ª Região", "regiao": "Alagoas"},
                    {"codigo": "TRT20", "nome": "TRT da 20ª Região", "regiao": "Sergipe"},
                    {"codigo": "TRT21", "nome": "TRT da 21ª Região", "regiao": "Rio Grande do Norte"},
                    {"codigo": "TRT22", "nome": "TRT da 22ª Região", "regiao": "Piauí"},
                    {"codigo": "TRT23", "nome": "TRT da 23ª Região", "regiao": "Mato Grosso"},
                    {"codigo": "TRT24", "nome": "TRT da 24ª Região", "regiao": "Mato Grosso do Sul"},
                    {"codigo": "TST", "nome": "Tribunal Superior do Trabalho", "regiao": "Brasília"}
                ]
            },
            "tribunais_federais": {
                "nome": "Tribunais Regionais Federais (TRF)",
                "descricao": "6 Tribunais Regionais Federais",
                "tribunais": [
                    {"codigo": "TRF1", "nome": "TRF da 1ª Região", "estados": "AC, AM, AP, BA, DF, GO, MA, MT, PA, PI, RO, RR, TO"},
                    {"codigo": "TRF2", "nome": "TRF da 2ª Região", "estados": "ES, RJ"},
                    {"codigo": "TRF3", "nome": "TRF da 3ª Região", "estados": "MS, SP"},
                    {"codigo": "TRF4", "nome": "TRF da 4ª Região", "estados": "PR, RS, SC"},
                    {"codigo": "TRF5", "nome": "TRF da 5ª Região", "estados": "AL, CE, PB, PE, RN, SE"},
                    {"codigo": "TRF6", "nome": "TRF da 6ª Região", "estados": "MG"}
                ]
            },
            "tribunais_superiores": {
                "nome": "Tribunais Superiores",
                "descricao": "5 Tribunais Superiores do Brasil",
                "tribunais": [
                    {"codigo": "STF", "nome": "Supremo Tribunal Federal", "instancia": "Suprema"},
                    {"codigo": "STJ", "nome": "Superior Tribunal de Justiça", "instancia": "Superior"},
                    {"codigo": "TST", "nome": "Tribunal Superior do Trabalho", "instancia": "Superior"},
                    {"codigo": "STM", "nome": "Superior Tribunal Militar", "instancia": "Superior"},
                    {"codigo": "TSE", "nome": "Tribunal Superior Eleitoral", "instancia": "Superior"}
                ]
            },
            "tribunais_militares": {
                "nome": "Tribunais de Justiça Militar",
                "descricao": "3 Tribunais de Justiça Militar Estaduais",
                "tribunais": [
                    {"codigo": "TJMMG", "nome": "Tribunal de Justiça Militar de Minas Gerais", "uf": "MG"},
                    {"codigo": "TJMRS", "nome": "Tribunal de Justiça Militar do Rio Grande do Sul", "uf": "RS"},
                    {"codigo": "TJMSP", "nome": "Tribunal de Justiça Militar de São Paulo", "uf": "SP"}
                ]
            },
            "tribunais_eleitorais": {
                "nome": "Tribunais Regionais Eleitorais (TRE)",
                "descricao": "27 Tribunais Regionais Eleitorais",
                "tribunais": [
                    {"codigo": "TREAC", "nome": "TRE do Acre", "uf": "AC"},
                    {"codigo": "TREAL", "nome": "TRE de Alagoas", "uf": "AL"},
                    {"codigo": "TREAP", "nome": "TRE do Amapá", "uf": "AP"},
                    {"codigo": "TREAM", "nome": "TRE do Amazonas", "uf": "AM"},
                    {"codigo": "TREBA", "nome": "TRE da Bahia", "uf": "BA"},
                    {"codigo": "TRECE", "nome": "TRE do Ceará", "uf": "CE"},
                    {"codigo": "TREDF", "nome": "TRE do Distrito Federal", "uf": "DF"},
                    {"codigo": "TREES", "nome": "TRE do Espírito Santo", "uf": "ES"},
                    {"codigo": "TREGO", "nome": "TRE de Goiás", "uf": "GO"},
                    {"codigo": "TREMA", "nome": "TRE do Maranhão", "uf": "MA"},
                    {"codigo": "TREMT", "nome": "TRE de Mato Grosso", "uf": "MT"},
                    {"codigo": "TREMS", "nome": "TRE de Mato Grosso do Sul", "uf": "MS"},
                    {"codigo": "TREMG", "nome": "TRE de Minas Gerais", "uf": "MG"},
                    {"codigo": "TREPA", "nome": "TRE do Pará", "uf": "PA"},
                    {"codigo": "TREPB", "nome": "TRE da Paraíba", "uf": "PB"},
                    {"codigo": "TREPR", "nome": "TRE do Paraná", "uf": "PR"},
                    {"codigo": "TREPE", "nome": "TRE de Pernambuco", "uf": "PE"},
                    {"codigo": "TREPI", "nome": "TRE do Piauí", "uf": "PI"},
                    {"codigo": "TRERJ", "nome": "TRE do Rio de Janeiro", "uf": "RJ"},
                    {"codigo": "TRERN", "nome": "TRE do Rio Grande do Norte", "uf": "RN"},
                    {"codigo": "TRERS", "nome": "TRE do Rio Grande do Sul", "uf": "RS"},
                    {"codigo": "TRERO", "nome": "TRE de Rondônia", "uf": "RO"},
                    {"codigo": "TRERR", "nome": "TRE de Roraima", "uf": "RR"},
                    {"codigo": "TRESC", "nome": "TRE de Santa Catarina", "uf": "SC"},
                    {"codigo": "TRESP", "nome": "TRE de São Paulo", "uf": "SP"},
                    {"codigo": "TRESE", "nome": "TRE de Sergipe", "uf": "SE"},
                    {"codigo": "TRETO", "nome": "TRE do Tocantins", "uf": "TO"}
                ]
            },
            "conselhos_justica": {
                "nome": "Conselhos de Justiça",
                "descricao": "Órgãos de administração e controle do Poder Judiciário",
                "tribunais": [
                    {"codigo": "CNJ", "nome": "Conselho Nacional de Justiça", "funcao": "Administração e controle"},
                    {"codigo": "CJF", "nome": "Conselho da Justiça Federal", "funcao": "Administração da Justiça Federal"},
                    {"codigo": "CSJT", "nome": "Conselho Superior da Justiça do Trabalho", "funcao": "Administração da Justiça do Trabalho"}
                ]
            }
        }
        
        # Validar se a API key está configurada
        if not self.api_key:
            logger.warning("⚠️ JUDIT_API_KEY não configurada. Funcionalidades limitadas.")
    
    def obter_tribunais_por_categoria(self) -> Dict:
        """
        Retorna todos os tribunais organizados por categoria
        
        Returns:
            Dict: Estrutura completa dos tribunais brasileiros cobertos pela Judit
        """
        return self.tribunais_brasil
    
    def obter_lista_codigos_tribunais(self) -> List[str]:
        """
        Retorna lista de todos os códigos de tribunais disponíveis
        
        Returns:
            List[str]: Lista com códigos de todos os tribunais
        """
        codigos = []
        for categoria in self.tribunais_brasil.values():
            for tribunal in categoria['tribunais']:
                codigos.append(tribunal['codigo'])
        return sorted(codigos)
    
    def buscar_tribunal_por_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Busca tribunal específico pelo código
        
        Args:
            codigo: Código do tribunal (ex: TJSP, TRF3, etc.)
            
        Returns:
            Dict: Dados do tribunal encontrado ou None
        """
        for categoria in self.tribunais_brasil.values():
            for tribunal in categoria['tribunais']:
                if tribunal['codigo'] == codigo.upper():
                    return tribunal
        return None
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Executa requisição HTTP para a API Judit
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            url: URL completa para a requisição
            data: Dados para envio no body (POST)
            params: Parâmetros de query string (GET)
            
        Returns:
            Dict: Resposta da API
            
        Raises:
            Exception: Em caso de erro na requisição
        """
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            else:
                logger.error(f"❌ Erro API Judit: {response.status_code} - {response.text}")
                return {
                    'error': True,
                    'status_code': response.status_code,
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro de conexão Judit: {str(e)}")
            return {
                'error': True,
                'message': f"Erro de conexão: {str(e)}"
            }
    
    # =====================================================
    # BUSCA PROCESSUAL E POR DOCUMENTO
    # =====================================================
    
    def buscar_processo_cnj(self, numero_cnj: str, incluir_anexos: bool = False) -> Dict:
        """
        Busca processo por número CNJ
        
        Args:
            numero_cnj: Número CNJ do processo
            incluir_anexos: Se deve incluir anexos na busca
            
        Returns:
            Dict: Dados da busca processual
        """
        url = f"{self.base_url_requests}/requests"
        
        data = {
            "search": {
                "search_type": "lawsuit_cnj",
                "search_key": numero_cnj
            },
            "with_attachments": incluir_anexos
        }
        
        logger.info(f"🔍 Iniciando busca por CNJ: {numero_cnj}")
        result = self._make_request('POST', url, data)
        
        if not result.get('error'):
            logger.info(f"✅ Busca por CNJ iniciada com sucesso")
        
        return result
    
    def buscar_por_documento(self, documento: str, tipo_documento: str = "cpf", 
                           filtros: Optional[Dict] = None) -> Dict:
        """
        Busca processos por CPF/CNPJ
        
        Args:
            documento: CPF ou CNPJ
            tipo_documento: Tipo do documento ("cpf", "cnpj")
            filtros: Filtros adicionais para a busca
            
        Returns:
            Dict: Dados da busca por documento
        """
        url = f"{self.base_url_requests}/requests"
        
        # Filtros padrão se não fornecidos
        if not filtros:
            filtros = {
                "filter": {
                    "side": "Passive",
                    "tribunals": {
                        "keys": ["TJSP", "TJRJ", "TJMG"],
                        "not_equal": False
                    }
                }
            }
        
        data = {
            "search": {
                "search_type": tipo_documento,
                "search_key": documento,
                "search_params": filtros
            }
        }
        
        logger.info(f"🔍 Iniciando busca por {tipo_documento.upper()}: {documento}")
        result = self._make_request('POST', url, data)
        
        if not result.get('error'):
            logger.info(f"✅ Busca por {tipo_documento.upper()} iniciada com sucesso")
        
        return result
    
    def buscar_por_oab(self, numero_oab: str, uf_oab: str, filtros: Optional[Dict] = None) -> Dict:
        """
        Busca processos por número OAB
        
        Args:
            numero_oab: Número da OAB
            uf_oab: UF da OAB
            filtros: Filtros adicionais
            
        Returns:
            Dict: Dados da busca por OAB
        """
        url = f"{self.base_url_requests}/requests"
        
        if not filtros:
            filtros = {
                "filter": {
                    "side": "Active",
                    "tribunals": {
                        "keys": ["TJSP"],
                        "not_equal": False
                    }
                }
            }
        
        data = {
            "search": {
                "search_type": "oab",
                "search_key": f"{numero_oab}/{uf_oab}",
                "search_params": filtros
            }
        }
        
        logger.info(f"🔍 Iniciando busca por OAB: {numero_oab}/{uf_oab}")
        result = self._make_request('POST', url, data)
        
        return result
    
    def consultar_status_busca(self, request_id: str) -> Dict:
        """
        Consulta o status de uma busca em andamento
        
        Args:
            request_id: ID da requisição de busca
            
        Returns:
            Dict: Status da busca
        """
        url = f"{self.base_url_requests}/requests/{request_id}"
        
        logger.info(f"📊 Consultando status da busca: {request_id}")
        result = self._make_request('GET', url)
        
        return result
    
    def obter_resultado_busca(self, request_id: str, page_size: int = 100, page: int = 1) -> Dict:
        """
        Obtém os resultados de uma busca concluída
        
        Args:
            request_id: ID da requisição
            page_size: Tamanho da página (máximo 100)
            page: Número da página
            
        Returns:
            Dict: Resultados da busca
        """
        url = f"{self.base_url_requests}/responses"
        
        params = {
            'request_id': request_id,
            'page_size': min(page_size, 100),
            'page': page
        }
        
        logger.info(f"📄 Obtendo resultados da busca: {request_id}")
        result = self._make_request('GET', url, params=params)
        
        return result
    
    def baixar_documento_anexo(self, numero_processo: str, numero_instancia: str, 
                              id_anexo: str) -> Dict:
        """
        Baixa um documento anexo específico
        
        Args:
            numero_processo: Número do processo
            numero_instancia: Número da instância
            id_anexo: ID do anexo
            
        Returns:
            Dict: Dados do documento
        """
        url = f"{self.base_url_lawsuits}/lawsuits/{numero_processo}/{numero_instancia}/attachments/{id_anexo}"
        
        logger.info(f"📎 Baixando anexo: {id_anexo}")
        result = self._make_request('GET', url)
        
        return result
    
    # =====================================================
    # MONITORAMENTO DE PROCESSOS
    # =====================================================
    
    def criar_monitoramento_cnj(self, numero_cnj: str, recorrencia: int = 1) -> Dict:
        """
        Cria monitoramento para um processo por CNJ
        
        Args:
            numero_cnj: Número CNJ do processo
            recorrencia: Intervalo de recorrência em dias
            
        Returns:
            Dict: Dados do monitoramento criado
        """
        url = f"{self.base_url_tracking}/tracking"
        
        data = {
            "recurrence": recorrencia,
            "search": {
                "search_type": "lawsuit_cnj",
                "search_key": numero_cnj
            }
        }
        
        logger.info(f"🔔 Criando monitoramento CNJ: {numero_cnj}")
        result = self._make_request('POST', url, data)
        
        if not result.get('error'):
            logger.info(f"✅ Monitoramento CNJ criado com sucesso")
        
        return result
    
    def criar_monitoramento_documento(self, documento: str, tipo_documento: str = "cpf",
                                    recorrencia: int = 1, filtros: Optional[Dict] = None) -> Dict:
        """
        Cria monitoramento por documento (CPF/CNPJ)
        
        Args:
            documento: CPF ou CNPJ
            tipo_documento: Tipo do documento
            recorrencia: Intervalo em dias
            filtros: Filtros de busca
            
        Returns:
            Dict: Dados do monitoramento
        """
        url = f"{self.base_url_tracking}/tracking"
        
        if not filtros:
            filtros = {
                "filter": {
                    "side": "Passive",
                    "tribunals": {
                        "keys": ["TJSP", "TJRJ"],
                        "not_equal": False
                    }
                }
            }
        
        data = {
            "recurrence": recorrencia,
            "search": {
                "search_type": tipo_documento,
                "search_key": documento,
                "search_params": filtros
            }
        }
        
        logger.info(f"🔔 Criando monitoramento {tipo_documento.upper()}: {documento}")
        result = self._make_request('POST', url, data)
        
        return result
    
    def criar_monitoramento_customizado(self, filtros: Dict, recorrencia: int = 2) -> Dict:
        """
        Cria monitoramento customizado com filtros específicos
        
        Args:
            filtros: Filtros customizados de busca
            recorrencia: Intervalo em dias
            
        Returns:
            Dict: Dados do monitoramento
        """
        url = f"{self.base_url_tracking}/tracking"
        
        data = {
            "recurrence": recorrencia,
            "search": {
                "search_type": "custom",
                "search_key": "",
                "search_params": filtros
            }
        }
        
        logger.info(f"🔔 Criando monitoramento customizado")
        result = self._make_request('POST', url, data)
        
        return result
    
    def listar_monitoramentos(self, user_id: Optional[str] = None, 
                            page_size: int = 10, status: Optional[str] = None) -> Dict:
        """
        Lista todos os monitoramentos
        
        Args:
            user_id: ID do usuário (opcional)
            page_size: Tamanho da página
            status: Status específico ('updated', etc.)
            
        Returns:
            Dict: Lista de monitoramentos
        """
        url = f"{self.base_url_tracking}/tracking/"
        
        params = {
            'page_size': page_size
        }
        
        if user_id:
            params['user_id'] = user_id
        if status:
            params['status'] = status
        
        logger.info(f"📋 Listando monitoramentos")
        result = self._make_request('GET', url, params=params)
        
        return result
    
    def consultar_monitoramento(self, tracking_id: str) -> Dict:
        """
        Consulta um monitoramento específico
        
        Args:
            tracking_id: ID do monitoramento
            
        Returns:
            Dict: Dados do monitoramento
        """
        url = f"{self.base_url_tracking}/tracking/{tracking_id}"
        
        logger.info(f"🔍 Consultando monitoramento: {tracking_id}")
        result = self._make_request('GET', url)
        
        return result
    
    # =====================================================
    # MÉTODOS AUXILIARES
    # =====================================================
    
    def verificar_conexao(self) -> bool:
        """
        Verifica se a conexão com a API está funcionando
        
        Returns:
            bool: True se a conexão está OK
        """
        try:
            # Tenta fazer uma consulta simples
            result = self.listar_monitoramentos(page_size=1)
            return not result.get('error', False)
        except Exception as e:
            logger.error(f"❌ Erro ao verificar conexão Judit: {e}")
            return False
    
    def processar_busca_completa(self, request_id: str, timeout_segundos: int = 300) -> Dict:
        """
        Processa uma busca completa aguardando o resultado
        
        Args:
            request_id: ID da requisição
            timeout_segundos: Timeout máximo em segundos
            
        Returns:
            Dict: Resultado completo da busca
        """
        inicio = time.time()
        
        while (time.time() - inicio) < timeout_segundos:
            status = self.consultar_status_busca(request_id)
            
            if status.get('error'):
                return status
            
            # Verificar se a busca foi concluída
            if status.get('status') == 'completed':
                logger.info(f"✅ Busca concluída: {request_id}")
                return self.obter_resultado_busca(request_id)
            elif status.get('status') == 'failed':
                logger.error(f"❌ Busca falhou: {request_id}")
                return {
                    'error': True,
                    'message': 'Busca falhou'
                }
            
            # Aguardar antes da próxima verificação
            time.sleep(5)
        
        logger.warning(f"⏰ Timeout na busca: {request_id}")
        return {
            'error': True,
            'message': 'Timeout na busca'
        }


class JuditService:
    """Serviço de alto nível para operações com a Judit"""
    
    def __init__(self):
        self.client = JuditAPIClient()
    
    def busca_rapida_cnj(self, numero_cnj: str) -> Dict:
        """
        Executa busca rápida por CNJ com resultado completo
        
        Args:
            numero_cnj: Número CNJ
            
        Returns:
            Dict: Resultado da busca
        """
        # Iniciar busca
        busca = self.client.buscar_processo_cnj(numero_cnj)
        
        if busca.get('error'):
            return busca
        
        request_id = busca.get('request_id')
        if not request_id:
            return {
                'error': True,
                'message': 'ID da requisição não retornado'
            }
        
        # Aguardar resultado
        return self.client.processar_busca_completa(request_id)
    
    def busca_rapida_documento(self, documento: str, tipo: str = "cpf") -> Dict:
        """
        Executa busca rápida por documento com resultado completo
        
        Args:
            documento: CPF ou CNPJ
            tipo: Tipo do documento
            
        Returns:
            Dict: Resultado da busca
        """
        # Iniciar busca
        busca = self.client.buscar_por_documento(documento, tipo)
        
        if busca.get('error'):
            return busca
        
        request_id = busca.get('request_id')
        if not request_id:
            return {
                'error': True,
                'message': 'ID da requisição não retornado'
            }
        
        # Aguardar resultado
        return self.client.processar_busca_completa(request_id)
    
    def monitoramento_inteligente(self, parametros: Dict) -> Dict:
        """
        Cria monitoramento inteligente baseado nos parâmetros
        
        Args:
            parametros: Parâmetros de monitoramento
            
        Returns:
            Dict: Resultado da criação do monitoramento
        """
        tipo = parametros.get('tipo', 'cnj')
        
        if tipo == 'cnj':
            return self.client.criar_monitoramento_cnj(
                parametros['numero_cnj'],
                parametros.get('recorrencia', 1)
            )
        elif tipo in ['cpf', 'cnpj']:
            return self.client.criar_monitoramento_documento(
                parametros['documento'],
                tipo,
                parametros.get('recorrencia', 1),
                parametros.get('filtros')
            )
        elif tipo == 'custom':
            return self.client.criar_monitoramento_customizado(
                parametros['filtros'],
                parametros.get('recorrencia', 2)
            )
        else:
            return {
                'error': True,
                'message': 'Tipo de monitoramento inválido'
            }
    
    def dashboard_monitoramentos(self, user_id: Optional[str] = None) -> Dict:
        """
        Obtém dados para dashboard de monitoramentos
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict: Dados do dashboard
        """
        monitoramentos = self.client.listar_monitoramentos(user_id)
        
        if monitoramentos.get('error'):
            return monitoramentos
        
        # Processar estatísticas
        lista = monitoramentos.get('data', [])
        
        stats = {
            'total': len(lista),
            'ativos': sum(1 for m in lista if m.get('status') == 'active'),
            'atualizados': sum(1 for m in lista if m.get('status') == 'updated'),
            'por_tipo': {}
        }
        
        for monitoramento in lista:
            tipo = monitoramento.get('search', {}).get('search_type', 'unknown')
            stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1
        
        return {
            'monitoramentos': lista,
            'estatisticas': stats
        }


# Instância global do serviço
judit_service = JuditService()


def registrar_rotas_judit(app):
    """
    Registra todas as rotas da integração Judit
    
    Args:
        app: Instância do Flask
    """
    from flask import request, jsonify, render_template, flash, redirect, url_for
    from flask_login import login_required, current_user
    
    @app.route('/api/judit/buscar-cnj', methods=['POST'])
    @login_required
    def api_judit_buscar_cnj():
        """API para busca por CNJ"""
        try:
            data = request.get_json()
            numero_cnj = data.get('numero_cnj')
            
            if not numero_cnj:
                return jsonify({
                    'error': True,
                    'message': 'Número CNJ é obrigatório'
                }), 400
            
            resultado = judit_service.busca_rapida_cnj(numero_cnj)
            
            # Se solicitado, sincronizar com banco de dados
            salvar_no_banco = data.get('salvar_no_banco', False)
            if salvar_no_banco and not resultado.get('error'):
                sync_result = sincronizar_processo_com_banco(resultado, 'cnj', numero_cnj)
                resultado['sync_info'] = sync_result
            
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro na busca CNJ: {e}")
            return jsonify({
                'error': True,
                'message': f"Erro interno: {str(e)}"
            }), 500
    
    @app.route('/api/judit/buscar-documento', methods=['POST'])
    @login_required
    def api_judit_buscar_documento():
        """API para busca por documento"""
        try:
            data = request.get_json()
            documento = data.get('documento')
            tipo = data.get('tipo', 'cpf')
            
            if not documento:
                return jsonify({
                    'error': True,
                    'message': 'Documento é obrigatório'
                }), 400
            
            resultado = judit_service.busca_rapida_documento(documento, tipo)
            
            # Se solicitado, sincronizar com banco de dados
            salvar_no_banco = data.get('salvar_no_banco', False)
            if salvar_no_banco and not resultado.get('error'):
                sync_result = sincronizar_processo_com_banco(resultado, tipo, documento)
                resultado['sync_info'] = sync_result
            
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro na busca por documento: {e}")
            return jsonify({
                'error': True,
                'message': f"Erro interno: {str(e)}"
            }), 500
    
    @app.route('/api/judit/criar-monitoramento', methods=['POST'])
    @login_required
    def api_judit_criar_monitoramento():
        """API para criar monitoramento"""
        try:
            data = request.get_json()
            
            resultado = judit_service.monitoramento_inteligente(data)
            
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar monitoramento: {e}")
            return jsonify({
                'error': True,
                'message': f"Erro interno: {str(e)}"
            }), 500
    
    @app.route('/api/judit/listar-monitoramentos')
    @login_required
    def api_judit_listar_monitoramentos():
        """API para listar monitoramentos"""
        try:
            user_id = request.args.get('user_id')
            
            resultado = judit_service.dashboard_monitoramentos(user_id)
            
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar monitoramentos: {e}")
            return jsonify({
                'error': True,
                'message': f"Erro interno: {str(e)}"
            }), 500
    
    @app.route('/api/judit/status')
    def api_judit_status():
        """Verifica status da integração Judit"""
        status = {
            'judit_connected': judit_service.client.verificar_conexao(),
            'api_key_configured': bool(judit_service.client.api_key),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
    
    @app.route('/api/judit/sincronizar-processo/<int:processo_id>', methods=['POST'])
    @login_required
    def api_judit_sincronizar_processo(processo_id):
        """Sincroniza um processo específico com dados da Judit"""
        try:
            from models import ProcessoJuridico, db
            
            processo = ProcessoJuridico.query.get_or_404(processo_id)
            
            # Buscar dados na Judit usando CNJ do processo
            if not processo.numero_processo_cnj:
                return jsonify({
                    'error': True,
                    'message': 'Processo não possui número CNJ válido'
                }), 400
            
            logger.info(f"🔄 Sincronizando processo {processo.numero_processo_cnj} com Judit")
            
            # Buscar dados na Judit
            resultado = judit_service.busca_rapida_cnj(processo.numero_processo_cnj)
            
            if resultado.get('error'):
                return jsonify({
                    'error': True,
                    'message': f'Erro na busca Judit: {resultado.get("message", "Erro desconhecido")}'
                }), 400
            
            # Sincronizar dados
            sync_result = sincronizar_processo_com_banco(resultado, 'cnj', processo.numero_processo_cnj, processo)
            
            return jsonify({
                'success': True,
                'message': 'Processo sincronizado com sucesso',
                'sync_info': sync_result,
                'processo_id': processo.id
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar processo: {e}")
            return jsonify({
                'error': True,
                'message': f"Erro interno: {str(e)}"
            }), 500
    
    @app.route('/processos/<int:processo_id>/judit-status')
    @login_required
    def processo_judit_status(processo_id):
        """Retorna status da integração Judit para um processo específico"""
        try:
            from models import ProcessoJuridico
            
            processo = ProcessoJuridico.query.get_or_404(processo_id)
            resumo = processo.obter_resumo_judit()
            
            return jsonify({
                'processo_id': processo.id,
                'numero_cnj': processo.numero_processo_cnj,
                'judit_sincronizado': processo.judit_sincronizado,
                'precisa_atualizacao': processo.precisa_atualizacao_judit(),
                'resumo_judit': resumo
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status Judit: {e}")
            return jsonify({
                'error': True,
                'message': str(e)
            }), 500
    
    logger.info("✅ Rotas da integração Judit registradas")


def sincronizar_processo_com_banco(resultado_judit, tipo_busca, valor_busca, processo_existente=None):
    """
    Sincroniza resultado da Judit com o banco de dados
    
    Args:
        resultado_judit: Resultado da busca na Judit
        tipo_busca: Tipo de busca ('cnj', 'cpf', 'cnpj')
        valor_busca: Valor da busca
        processo_existente: Processo existente para atualizar (opcional)
        
    Returns:
        Dict: Resultado da sincronização
    """
    try:
        from models import ProcessoJuridico, db
        from flask_login import current_user
        from datetime import datetime
        
        dados = resultado_judit.get('data', [])
        if not dados:
            return {
                'success': False,
                'message': 'Nenhum dado encontrado na Judit'
            }
        
        processos_atualizados = []
        processos_criados = []
        erros = []
        
        for item in dados:
            try:
                numero_cnj = item.get('numero_processo') or item.get('numero_cnj') or item.get('numero')
                if not numero_cnj:
                    continue
                
                # Se um processo específico foi passado, apenas atualizá-lo
                if processo_existente:
                    if processo_existente.numero_processo_cnj == numero_cnj:
                        processo_existente.atualizar_dados_judit({
                            'dados': item,
                            'request_id': resultado_judit.get('request_id'),
                            'movimentacoes': item.get('movimentacoes', []),
                            'partes': item.get('partes', []),
                            'anexos': item.get('anexos', [])
                        })
                        processos_atualizados.append(processo_existente.id)
                        logger.info(f"✅ Processo {numero_cnj} atualizado com dados Judit")
                        break
                    continue
                
                # Buscar processo existente
                processo = ProcessoJuridico.buscar_por_cnj(numero_cnj)
                
                if processo:
                    # Atualizar processo existente
                    processo.atualizar_dados_judit({
                        'dados': item,
                        'request_id': resultado_judit.get('request_id'),
                        'movimentacoes': item.get('movimentacoes', []),
                        'partes': item.get('partes', []),
                        'anexos': item.get('anexos', [])
                    })
                    processos_atualizados.append(processo.id)
                    logger.info(f"✅ Processo {numero_cnj} atualizado com dados Judit")
                
                else:
                    # Criar novo processo com dados básicos
                    dados_basicos = extrair_dados_basicos_judit(item)
                    if dados_basicos:
                        novo_processo = ProcessoJuridico(
                            numero_processo_cnj=numero_cnj,
                            usuario_id=current_user.id,
                            **dados_basicos
                        )
                        
                        # Adicionar dados Judit
                        novo_processo.atualizar_dados_judit({
                            'dados': item,
                            'request_id': resultado_judit.get('request_id'),
                            'movimentacoes': item.get('movimentacoes', []),
                            'partes': item.get('partes', []),
                            'anexos': item.get('anexos', [])
                        })
                        
                        db.session.add(novo_processo)
                        processos_criados.append(numero_cnj)
                        logger.info(f"✅ Novo processo {numero_cnj} criado com dados Judit")
            
            except Exception as e:
                erros.append(f"Erro ao processar {numero_cnj}: {str(e)}")
                logger.error(f"❌ Erro ao processar processo {numero_cnj}: {e}")
        
        # Salvar alterações
        try:
            db.session.commit()
            logger.info(f"✅ Sincronização concluída: {len(processos_atualizados)} atualizados, {len(processos_criados)} criados")
            
            return {
                'success': True,
                'processos_atualizados': len(processos_atualizados),
                'processos_criados': len(processos_criados),
                'ids_atualizados': processos_atualizados,
                'ids_criados': processos_criados,
                'erros': erros
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro ao salvar no banco: {e}")
            return {
                'success': False,
                'message': f'Erro ao salvar no banco: {str(e)}'
            }
    
    except Exception as e:
        logger.error(f"❌ Erro na sincronização: {e}")
        return {
            'success': False,
            'message': f'Erro na sincronização: {str(e)}'
        }


def extrair_dados_basicos_judit(dados_judit):
    """Extrai dados básicos do resultado Judit para criar ProcessoJuridico"""
    try:
        dados_basicos = {
            'area_juridica': dados_judit.get('area_juridica', dados_judit.get('classe', 'Cível')),
            'cliente': dados_judit.get('autor', dados_judit.get('requerente', 'Cliente via Judit')),
            'autor': dados_judit.get('autor', dados_judit.get('requerente', 'Autor via Judit')),
            'advogado_do_caso': dados_judit.get('advogado', 'Advogado via Judit'),
            'estado': dados_judit.get('tribunal', dados_judit.get('uf', 'BR'))[:50],
            'comarca': dados_judit.get('comarca', dados_judit.get('origem', 'Comarca via Judit'))[:100],
            'juizo': dados_judit.get('juizo', dados_judit.get('orgao_julgador', 'Juízo via Judit'))[:200],
            'resumo_dos_fatos': dados_judit.get('assunto', dados_judit.get('classe', 'Processo importado via Plataforma Judit'))[:500],
            'valor_da_causa': float(dados_judit.get('valor_causa', 0)) if dados_judit.get('valor_causa') else 0.0,
        }
        
        # Tentar extrair data de distribuição
        data_dist = dados_judit.get('data_distribuicao') or dados_judit.get('data_ajuizamento')
        if data_dist:
            try:
                from datetime import datetime
                if isinstance(data_dist, str):
                    dados_basicos['data_distribuicao'] = datetime.strptime(data_dist[:10], '%Y-%m-%d')
                else:
                    dados_basicos['data_distribuicao'] = data_dist
            except:
                from datetime import datetime
                dados_basicos['data_distribuicao'] = datetime.now()
        else:
            from datetime import datetime
            dados_basicos['data_distribuicao'] = datetime.now()
        
        return dados_basicos
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair dados básicos: {e}")
        return None


# Exportar classes e funções principais
__all__ = [
    'JuditAPIClient',
    'JuditService', 
    'judit_service',
    'registrar_rotas_judit',
    'sincronizar_processo_com_banco',
    'extrair_dados_basicos_judit'
]