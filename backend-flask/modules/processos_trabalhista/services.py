"""
Services para Processos Trabalhistas
Gestão de acordos e prognósticos
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from main import db
from models import (
    Processo,
    ProcessoTrabalhista,
    ProcessoPrognosticoTrabalhista
)


class TrabalhistaService:
    """
    Service para gestão de processos trabalhistas
    """
    
    @staticmethod
    def criar_ou_atualizar_dados(
        processo_id: int,
        data: Dict[str, Any]
    ) -> ProcessoTrabalhista:
        """
        Cria ou atualiza dados específicos do processo trabalhista
        
        Args:
            processo_id: ID do processo
            data: Dados trabalhistas
            
        Returns:
            ProcessoTrabalhista
        """
        # Verificar se processo existe
        processo = Processo.query.filter_by(id_processo=processo_id).first()
        if not processo:
            raise ValueError("Processo não encontrado")
        
        # Buscar dados existentes
        proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo_id).first()
        
        try:
            if proc_trab:
                # Atualizar
                proc_trab.tolerancia_acordo = data.get('tolerancia_acordo')
                proc_trab.acordo_realizado = data.get('acordo_realizado')
                proc_trab.data_acordo = data.get('data_acordo')
                proc_trab.observacoes_acordo = data.get('observacoes_acordo')
                proc_trab.data_atualizacao = datetime.utcnow()
            else:
                # Criar
                proc_trab = ProcessoTrabalhista(
                    processo_id=processo_id,
                    tolerancia_acordo=data.get('tolerancia_acordo'),
                    acordo_realizado=data.get('acordo_realizado'),
                    data_acordo=data.get('data_acordo'),
                    observacoes_acordo=data.get('observacoes_acordo')
                )
                db.session.add(proc_trab)
            
            db.session.commit()
            return proc_trab
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def obter_dados(processo_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados trabalhistas de um processo"""
        proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo_id).first()
        
        if not proc_trab:
            return None
        
        return {
            'processo_id': proc_trab.processo_id,
            'tolerancia_acordo': float(proc_trab.tolerancia_acordo) if proc_trab.tolerancia_acordo else None,
            'acordo_realizado': float(proc_trab.acordo_realizado) if proc_trab.acordo_realizado else None,
            'data_acordo': proc_trab.data_acordo.isoformat() if proc_trab.data_acordo else None,
            'observacoes_acordo': proc_trab.observacoes_acordo
        }
    
    @staticmethod
    def registrar_acordo(
        processo_id: int,
        valor_acordo: Decimal,
        data_acordo: date,
        observacoes: Optional[str] = None
    ) -> ProcessoTrabalhista:
        """Registra acordo realizado"""
        proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo_id).first()
        
        if not proc_trab:
            raise ValueError("Dados trabalhistas não encontrados para este processo")
        
        proc_trab.acordo_realizado = valor_acordo
        proc_trab.data_acordo = data_acordo
        if observacoes:
            proc_trab.observacoes_acordo = observacoes
        
        db.session.commit()
        return proc_trab
    
    @staticmethod
    def verificar_viabilidade_acordo(
        processo_id: int,
        valor_proposta: Decimal
    ) -> Dict[str, Any]:
        """
        Verifica se proposta de acordo está dentro da tolerância
        
        Returns:
            Dict com status, mensagem e percentual
        """
        proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo_id).first()
        
        if not proc_trab or not proc_trab.tolerancia_acordo:
            return {
                'viavel': None,
                'mensagem': 'Tolerância não definida',
                'tolerancia': None,
                'proposta': float(valor_proposta)
            }
        
        viavel = valor_proposta <= proc_trab.tolerancia_acordo
        percentual = (valor_proposta / proc_trab.tolerancia_acordo * 100) if proc_trab.tolerancia_acordo > 0 else 0
        
        return {
            'viavel': viavel,
            'mensagem': 'Acordo viável' if viavel else 'Acima da tolerância',
            'tolerancia': float(proc_trab.tolerancia_acordo),
            'proposta': float(valor_proposta),
            'percentual_tolerancia': float(percentual)
        }


class PrognosticoTrabalhistaService:
    """
    Service para prognósticos trabalhistas
    """
    
    @staticmethod
    def criar_ou_atualizar_prognostico(
        processo_id: int,
        data: Dict[str, Any]
    ) -> ProcessoPrognosticoTrabalhista:
        """
        Cria ou atualiza prognóstico trabalhista
        
        Args:
            processo_id: ID do processo trabalhista
            data: Dados do prognóstico
            
        Returns:
            ProcessoPrognosticoTrabalhista
        """
        # Verificar se processo trabalhista existe
        proc_trab = ProcessoTrabalhista.query.filter_by(processo_id=processo_id).first()
        if not proc_trab:
            raise ValueError("Processo trabalhista não encontrado")
        
        # Buscar prognóstico existente
        prognostico = ProcessoPrognosticoTrabalhista.query.filter_by(
            processo_id=processo_id
        ).first()
        
        try:
            if prognostico:
                # Atualizar
                prognostico.tese_provavel = data.get('tese_provavel')
                prognostico.valor_provavel = data.get('valor_provavel')
                prognostico.percentual_provavel = data.get('percentual_provavel', 70.00)
                
                prognostico.tese_possivel = data.get('tese_possivel')
                prognostico.valor_possivel = data.get('valor_possivel')
                prognostico.percentual_possivel = data.get('percentual_possivel', 50.00)
                
                prognostico.tese_remota = data.get('tese_remota')
                prognostico.valor_remoto = data.get('valor_remoto')
                prognostico.percentual_remoto = data.get('percentual_remoto', 25.00)
                
                prognostico.observacoes = data.get('observacoes')
                prognostico.avaliado_por = data.get('avaliado_por')
                prognostico.data_avaliacao = date.today()
                prognostico.data_atualizacao = datetime.utcnow()
                
            else:
                # Criar
                prognostico = ProcessoPrognosticoTrabalhista(
                    processo_id=processo_id,
                    tese_provavel=data.get('tese_provavel'),
                    valor_provavel=data.get('valor_provavel'),
                    percentual_provavel=data.get('percentual_provavel', 70.00),
                    tese_possivel=data.get('tese_possivel'),
                    valor_possivel=data.get('valor_possivel'),
                    percentual_possivel=data.get('percentual_possivel', 50.00),
                    tese_remota=data.get('tese_remota'),
                    valor_remoto=data.get('valor_remoto'),
                    percentual_remoto=data.get('percentual_remoto', 25.00),
                    observacoes=data.get('observacoes'),
                    avaliado_por=data.get('avaliado_por'),
                    data_avaliacao=date.today()
                )
                db.session.add(prognostico)
            
            db.session.commit()
            return prognostico
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def obter_prognostico(processo_id: int) -> Optional[Dict[str, Any]]:
        """Obtém prognóstico de um processo"""
        prognostico = ProcessoPrognosticoTrabalhista.query.filter_by(
            processo_id=processo_id
        ).first()
        
        if not prognostico:
            return None
        
        return {
            'provavel': {
                'tese': prognostico.tese_provavel,
                'valor': float(prognostico.valor_provavel) if prognostico.valor_provavel else None,
                'percentual': float(prognostico.percentual_provavel)
            },
            'possivel': {
                'tese': prognostico.tese_possivel,
                'valor': float(prognostico.valor_possivel) if prognostico.valor_possivel else None,
                'percentual': float(prognostico.percentual_possivel)
            },
            'remoto': {
                'tese': prognostico.tese_remota,
                'valor': float(prognostico.valor_remoto) if prognostico.valor_remoto else None,
                'percentual': float(prognostico.percentual_remoto)
            },
            'observacoes': prognostico.observacoes,
            'data_avaliacao': prognostico.data_avaliacao.isoformat() if prognostico.data_avaliacao else None,
            'avaliado_por': prognostico.avaliado_por
        }
    
    @staticmethod
    def calcular_valor_esperado(processo_id: int) -> Optional[Decimal]:
        """
        Calcula valor esperado do processo baseado nos prognósticos
        """
        prognostico = ProcessoPrognosticoTrabalhista.query.filter_by(
            processo_id=processo_id
        ).first()
        
        if not prognostico:
            return None
        
        valor_esperado = Decimal('0')
        
        if prognostico.valor_provavel and prognostico.percentual_provavel:
            valor_esperado += prognostico.valor_provavel * (prognostico.percentual_provavel / 100)
        
        if prognostico.valor_possivel and prognostico.percentual_possivel:
            valor_esperado += prognostico.valor_possivel * (prognostico.percentual_possivel / 100)
        
        if prognostico.valor_remoto and prognostico.percentual_remoto:
            valor_esperado += prognostico.valor_remoto * (prognostico.percentual_remoto / 100)
        
        return valor_esperado
