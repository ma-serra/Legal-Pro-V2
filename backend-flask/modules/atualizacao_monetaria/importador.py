"""
Importador de Índices Monetários
Busca dados de SELIC, IPCA, INPC, IGP-M, CDI do Banco Central
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from main import db
from models import IndiceMonetario, HistoricoIndice

logger = logging.getLogger(__name__)


class ImportadorIndices:
    """
    Importa dados de índices monetários de fontes oficiais
    """
    
    # URLs das APIs do Banco Central
    BACEN_API_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
    
    # Códigos dos índices no Sistema Gerenciador de Séries Temporais (SGS) do BACEN
    CODIGOS_BACEN = {
        # Taxas de Juros
        'SELIC': 11,           # Taxa SELIC - Meta
        'SELIC-EFETIVA': 1178, # Taxa SELIC Efetiva
        'CDI': 12,             # Taxa CDI
        'TJLP': 256,           # Taxa de Juros de Longo Prazo
        'TR': 226,             # Taxa Referencial
        
        # Índices de Preços
        'IPCA': 433,           # IPCA - IBGE
        'IPCA-E': 10764,       # IPCA-E (Especial)
        'INPC': 188,           # INPC - IBGE
        'IGP-M': 189,          # IGP-M - FGV
        'IGP-DI': 190,         # IGP-DI - FGV
        'IPC-FIPE': 193,       # IPC-FIPE
        
        # Poupança
        'POUPANCA': 196,       # Poupança - Rentabilidade mensal
        'POUPANCA-NOVA': 195,  # Poupança nova regra
        
        # Câmbio
        'DOLAR-PTAX': 1,       # Dólar PTAX (compra)
        'EURO-PTAX': 21619,    # Euro PTAX
        
        # Especiais Tributários
        'UFIR': 17,            # UFIR (antiga, até 2000)
    }
    
    @staticmethod
    def buscar_dados_bacen(
        indice_nome: str,
        data_inicio: date,
        data_fim: date
    ) -> List[Dict[str, Any]]:
        """
        Busca dados de índice no Banco Central
        
        Args:
            indice_nome: Nome do índice (SELIC, IPCA, etc)
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Lista de dicionários com {data, valor}
        """
        codigo = ImportadorIndices.CODIGOS_BACEN.get(indice_nome)
        
        if not codigo:
            raise ValueError(f"Índice {indice_nome} não suportado")
        
        # Formatar datas para API (dd/MM/yyyy)
        data_inicio_str = data_inicio.strftime('%d/%m/%Y')
        data_fim_str = data_fim.strftime('%d/%m/%Y')
        
        # Montar URL
        url = ImportadorIndices.BACEN_API_BASE.format(code=codigo)
        params = {
            'formato': 'json',
            'dataInicial': data_inicio_str,
            'dataFinal': data_fim_str
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            dados = response.json()
            
            # Converter formato BACEN para nosso formato
            resultado = []
            for item in dados:
                try:
                    data_ref = datetime.strptime(item['data'], '%d/%m/%Y').date()
                    valor = Decimal(item['valor'].replace(',', '.'))
                    
                    resultado.append({
                        'data': data_ref,
                        'valor': valor
                    })
                except (KeyError, ValueError) as e:
                    logger.warning(f"Erro ao processar item: {item} - {e}")
                    continue
            
            logger.info(f"Importados {len(resultado)} registros de {indice_nome}")
            return resultado
            
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar dados do BACEN para {indice_nome}: {e}")
            raise
    
    @staticmethod
    def importar_historico(
        indice_nome: str,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        sobrescrever: bool = False
    ) -> int:
        """
        Importa histórico de um índice
        
        Args:
            indice_nome: Nome do índice
            data_inicio: Data inicial (padrão: 1 ano atrás)
            data_fim: Data final (padrão: hoje)
            sobrescrever: Se True, sobrescreve dados existentes
            
        Returns:
            Número de registros importados
        """
        # Buscar índice no DB
        indice = IndiceMonetario.query.filter_by(nome=indice_nome, ativo=True).first()
        
        if not indice:
            raise ValueError(f"Índice {indice_nome} não encontrado no banco")
        
        # Datas padrão
        if not data_fim:
            data_fim = date.today()
        if not data_inicio:
            # Se não passar data, tenta buscar último registro do banco
            ultimo = HistoricoIndice.query.filter_by(indice_id=indice.id_indice).order_by(HistoricoIndice.data_referencia.desc()).first()
            if ultimo:
                 data_inicio = ultimo.data_referencia + timedelta(days=1)
            else:
                 # Sem dados: importar últimos 5 anos por padrão
                 data_inicio = data_fim - timedelta(days=1825)
        
        # Buscar dados do BACEN
        dados = ImportadorIndices.buscar_dados_bacen(indice_nome, data_inicio, data_fim)
        
        # Importar para o DB
        registros_criados = 0
        
        try:
            for item in dados:
                # Verificar se já existe
                existente = HistoricoIndice.query.filter_by(
                    indice_id=indice.id_indice,
                    data_referencia=item['data']
                ).first()
                
                if existente:
                    if sobrescrever:
                        existente.valor = item['valor']
                        existente.data_importacao = datetime.utcnow()
                    # Ignorar se não sobrescrever
                else:
                    # Criar novo
                    historico = HistoricoIndice(
                        indice_id=indice.id_indice,
                        data_referencia=item['data'],
                        valor=item['valor']
                    )
                    db.session.add(historico)
                    registros_criados += 1
            
            db.session.commit()
            logger.info(f"Importados {registros_criados} novos registros de {indice_nome}")
            
            return registros_criados
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao importar histórico: {e}")
            raise
    
    @staticmethod
    def importar_todos_indices(
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Importa histórico de todos os índices
        
        Returns:
            Dict com {indice: registros_importados}
        """
        resultado = {}
        
        for indice_nome in ImportadorIndices.CODIGOS_BACEN.keys():
            try:
                count = ImportadorIndices.importar_historico(
                    indice_nome, data_inicio, data_fim
                )
                resultado[indice_nome] = count
                
            except Exception as e:
                logger.error(f"Erro ao importar {indice_nome}: {e}")
                resultado[indice_nome] = 0
        
        return resultado
    
    @staticmethod
    def atualizar_indices_recentes(dias: int = 30) -> Dict[str, int]:
        """
        Atualiza índices dos últimos N dias
        
        Args:
            dias: Número de dias para atualizar
            
        Returns:
            Dict com {indice: registros_importados}
        """
        data_inicio = date.today() - timedelta(days=dias)
        data_fim = date.today()
        
        return ImportadorIndices.importar_todos_indices(
            data_inicio, data_fim
        )
    
    @staticmethod
    def verificar_atualizacao_pendente(indice_nome: str) -> bool:
        """
        Verifica se há necessidade de atualização
        
        Returns:
            True se última atualização tem mais de 1 dia
        """
        indice = IndiceMonetario.query.filter_by(nome=indice_nome, ativo=True).first()
        
        if not indice:
            return False
        
        # Buscar último registro
        ultimo = HistoricoIndice.query.filter_by(
            indice_id=indice.id_indice
        ).order_by(HistoricoIndice.data_referencia.desc()).first()
        
        if not ultimo:
            return True  # Sem dados, precisa atualizar
        
        # Verificar se último registro tem mais de 1 dia
        dias_desde_ultima = (date.today() - ultimo.data_referencia).days
        
        return dias_desde_ultima > 1
    
    @staticmethod
    def importar_taxa_tr() -> int:
        """
        Importa Taxa Referencial (TR)
        Fonte: BACEN código 226
        """
        indice = IndiceMonetario.query.filter_by(nome='TR', ativo=True).first()
        
        if not indice:
            logger.warning("Índice TR não encontrado")
            return 0
        
        data_inicio = date.today() - timedelta(days=365)
        data_fim = date.today()
        
        # API BACEN para TR
        url = ImportadorIndices.BACEN_API_BASE.format(code=226)
        params = {
            'formato': 'json',
            'dataInicial': data_inicio.strftime('%d/%m/%Y'),
            'dataFinal': data_fim.strftime('%d/%m/%Y')
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            dados = response.json()
            
            registros = 0
            for item in dados:
                try:
                    data_ref = datetime.strptime(item['data'], '%d/%m/%Y').date()
                    valor = Decimal(item['valor'].replace(',', '.'))
                    
                    # Verificar existente
                    existente = HistoricoIndice.query.filter_by(
                        indice_id=indice.id_indice,
                        data_referencia=data_ref
                    ).first()
                    
                    if not existente:
                        hist = HistoricoIndice(
                            indice_id=indice.id_indice,
                            data_referencia=data_ref,
                            valor=valor
                        )
                        db.session.add(hist)
                        registros += 1
                        
                except (KeyError, ValueError):
                    continue
            
            db.session.commit()
            logger.info(f"Importados {registros} registros de TR")
            return registros
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao importar TR: {e}")
            return 0
