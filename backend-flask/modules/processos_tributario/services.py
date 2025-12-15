"""
Services para Processos Tributários
Gestão de teses, prognósticos e atualização monetária
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from main import db
from models import (
    Processo,
    ProcessoTributario,
    Tributo,
    TeseTributaria,
    ProcessoTese,
    ProcessoPrognosticoTributario,
    IndiceMonetario,
    HistoricoIndice,
    ProcessoAtualizacaoMonetaria
)


class TeseTributariaService:
    """
    Service para gestão de teses tributárias
    """
    
    @staticmethod
    def criar_tese(data: Dict[str, Any]) -> TeseTributaria:
        """
        Cria uma nova tese tributária
        
        Args:
            data: Dados da tese
            
        Returns:
            TeseTributaria criada
        """
        try:
            tese = TeseTributaria(
                tenant_id=data.get('tenant_id'),
                codigo=data['codigo'],
                titulo=data['titulo'],
                descricao=data.get('descricao'),
                tributo_id=data.get('tributo_id'),
                tema_repercussao_geral=data.get('tema_repercussao_geral'),
                tema_repetitivo=data.get('tema_repetitivo'),
                tribunal_origem=data.get('tribunal_origem'),
                probabilidade_sucesso=data.get('probabilidade_sucesso'),
                fundamentacao=data.get('fundamentacao'),
                situacao=data.get('situacao', 'Pendente'),
                criado_por=data.get('criado_por')
            )
            
            db.session.add(tese)
            db.session.commit()
            
            return tese
            
        except IntegrityError as e:
            db.session.rollback()
            if 'unique' in str(e).lower():
                raise ValueError(f"Tese com código '{data['codigo']}' já existe")
            raise
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def listar_teses(
        filtros: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Lista teses com filtros
        
        Args:
            filtros: Filtros opcionais
            page: Página
            per_page: Itens por página
            
        Returns:
            Dict com teses e paginação
        """
        query = TeseTributaria.query.filter_by(ativo=True)
        
        if filtros:
            if 'tributo_id' in filtros:
                query = query.filter_by(tributo_id=filtros['tributo_id'])
            
            if 'situacao' in filtros:
                query = query.filter_by(situacao=filtros['situacao'])
            
            if 'busca' in filtros:
                termo = f"%{filtros['busca']}%"
                query = query.filter(
                    or_(
                        TeseTributaria.codigo.ilike(termo),
                        TeseTributaria.titulo.ilike(termo),
                        TeseTributaria.descricao.ilike(termo)
                    )
                )
        
        paginacao = query.order_by(TeseTributaria.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'teses': [t.to_dict() for t in paginacao.items],
            'total': paginacao.total,
            'paginas': paginacao.pages,
            'pagina_atual': page
        }
    
    @staticmethod
    def obter_tese(tese_id: int) -> Optional[TeseTributaria]:
        """Obtém tese por ID"""
        return TeseTributaria.query.filter_by(id_tese=tese_id, ativo=True).first()
    
    @staticmethod
    def atualizar_tese(tese_id: int, data: Dict[str, Any]) -> Optional[TeseTributaria]:
        """Atualiza uma tese"""
        tese = TeseTributariaService.obter_tese(tese_id)
        
        if not tese:
            return None
        
        try:
            campos = [
                'titulo', 'descricao', 'tributo_id',
                'tema_repercussao_geral', 'tema_repetitivo', 'tribunal_origem',
                'probabilidade_sucesso', 'fundamentacao', 'situacao'
            ]
            
            for campo in campos:
                if campo in data:
                    setattr(tese, campo, data[campo])
            
            tese.data_atualizacao = datetime.utcnow()
            
            db.session.commit()
            return tese
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def deletar_tese(tese_id: int) -> bool:
        """Deleta tese (soft delete)"""
        tese = TeseTributariaService.obter_tese(tese_id)
        
        if not tese:
            return False
        
        tese.ativo = False
        db.session.commit()
        return True
    
    @staticmethod
    def vincular_tese_processo(processo_id: int, tese_id: int, ordem: int = 1) -> ProcessoTese:
        """
        Vincula uma tese a um processo
        
        Args:
            processo_id: ID do processo
            tese_id: ID da tese
            ordem: Ordem de prioridade
            
        Returns:
            ProcessoTese criado
        """
        try:
            vinculo = ProcessoTese(
                processo_id=processo_id,
                tese_id=tese_id,
                ordem=ordem,
                status='Aguardando'
            )
            
            db.session.add(vinculo)
            db.session.commit()
            
            return vinculo
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Tese já vinculada a este processo")
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def desvincular_tese_processo(processo_id: int, tese_id: int) -> bool:
        """Desvincula tese de processo"""
        vinculo = ProcessoTese.query.filter_by(
            processo_id=processo_id,
            tese_id=tese_id
        ).first()
        
        if not vinculo:
            return False
        
        db.session.delete(vinculo)
        db.session.commit()
        return True
    
    @staticmethod
    def atualizar_status_tese_processo(
        processo_id: int,
        tese_id: int,
        novo_status: str
    ) -> Optional[ProcessoTese]:
        """Atualiza status de uma tese no processo"""
        vinculo = ProcessoTese.query.filter_by(
            processo_id=processo_id,
            tese_id=tese_id
        ).first()
        
        if not vinculo:
            return None
        
        vinculo.status = novo_status
        db.session.commit()
        
        return vinculo
    
    @staticmethod
    def listar_teses_processo(processo_id: int) -> List[Dict[str, Any]]:
        """Lista teses vinculadas a um processo"""
        vinculos = ProcessoTese.query.filter_by(
            processo_id=processo_id
        ).order_by(ProcessoTese.ordem).all()
        
        return [{
            'tese': vinculo.tese.to_dict(),
            'ordem': vinculo.ordem,
            'status': vinculo.status,
            'data_vinculacao': vinculo.data_vinculacao.isoformat()
        } for vinculo in vinculos]


class PrognosticoTributarioService:
    """
    Service para prognósticos tributários
    """
    
    @staticmethod
    def criar_ou_atualizar_prognostico(
        processo_id: int,
        data: Dict[str, Any]
    ) -> ProcessoPrognosticoTributario:
        """
        Cria ou atualiza prognóstico de processo tributário
        
        Args:
            processo_id: ID do processo tributário
            data: Dados do prognóstico
            
        Returns:
            ProcessoPrognosticoTributario
        """
        # Verificar se processo tributário existe
        proc_trib = ProcessoTributario.query.filter_by(processo_id=processo_id).first()
        if not proc_trib:
            raise ValueError("Processo tributário não encontrado")
        
        # Buscar prognóstico existente
        prognostico = ProcessoPrognosticoTributario.query.filter_by(
            processo_id=processo_id
        ).first()
        
        try:
            if prognostico:
                # Atualizar
                prognostico.tese_provavel_id = data.get('tese_provavel_id')
                prognostico.valor_provavel = data.get('valor_provavel')
                prognostico.percentual_provavel = data.get('percentual_provavel', 70.00)
                
                prognostico.tese_possivel_id = data.get('tese_possivel_id')
                prognostico.valor_possivel = data.get('valor_possivel')
                prognostico.percentual_possivel = data.get('percentual_possivel', 50.00)
                
                prognostico.tese_remota_id = data.get('tese_remota_id')
                prognostico.valor_remoto = data.get('valor_remoto')
                prognostico.percentual_remoto = data.get('percentual_remoto', 25.00)
                
                prognostico.observacoes = data.get('observacoes')
                prognostico.avaliado_por = data.get('avaliado_por')
                prognostico.data_avaliacao = date.today()
                prognostico.data_atualizacao = datetime.utcnow()
                
            else:
                # Criar
                prognostico = ProcessoPrognosticoTributario(
                    processo_id=processo_id,
                    tese_provavel_id=data.get('tese_provavel_id'),
                    valor_provavel=data.get('valor_provavel'),
                    percentual_provavel=data.get('percentual_provavel', 70.00),
                    tese_possivel_id=data.get('tese_possivel_id'),
                    valor_possivel=data.get('valor_possivel'),
                    percentual_possivel=data.get('percentual_possivel', 50.00),
                    tese_remota_id=data.get('tese_remota_id'),
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
        prognostico = ProcessoPrognosticoTributario.query.filter_by(
            processo_id=processo_id
        ).first()
        
        if not prognostico:
            return None
        
        return {
            'provavel': {
                'tese': prognostico.tese_provavel.to_dict() if prognostico.tese_provavel else None,
                'valor': float(prognostico.valor_provavel) if prognostico.valor_provavel else None,
                'percentual': float(prognostico.percentual_provavel)
            },
            'possivel': {
                'tese': prognostico.tese_possivel.to_dict() if prognostico.tese_possivel else None,
                'valor': float(prognostico.valor_possivel) if prognostico.valor_possivel else None,
                'percentual': float(prognostico.percentual_possivel)
            },
            'remoto': {
                'tese': prognostico.tese_remota.to_dict() if prognostico.tese_remota else None,
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
        
        Fórmula: (Vprovável × %provável) + (Vpossível × %possível) + (Vremoto × %remoto)
        """
        prognostico = ProcessoPrognosticoTributario.query.filter_by(
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


class AtualizacaoMonetariaService:
    """
    Service para atualização monetária de processos
    """
    
    @staticmethod
    def calcular_atualizacao(
        valor_base: Decimal,
        data_base: date,
        data_atualizacao: date,
        indice_id: int
    ) -> Dict[str, Any]:
        """
        Calcula atualização monetária
        
        Args:
            valor_base: Valor inicial
            data_base: Data do valor base
            data_atualizacao: Data para atualizar
            indice_id: ID do índice monetário
            
        Returns:
            Dict com valor atualizado e percentual
        """
        if data_atualizacao < data_base:
            raise ValueError("Data de atualização deve ser posterior à data base")
        
        # Buscar histórico de índices no período
        historico = HistoricoIndice.query.filter(
            and_(
                HistoricoIndice.indice_id == indice_id,
                HistoricoIndice.data_referencia >= data_base,
                HistoricoIndice.data_referencia <= data_atualizacao
            )
        ).order_by(HistoricoIndice.data_referencia).all()
        
        if not historico:
            raise ValueError("Sem dados de índice para o período")
        
        # Calcular fator de correção acumulado
        fator_correcao = Decimal('1.0')
        for registro in historico:
            fator_correcao *= (Decimal('1.0') + (registro.valor / Decimal('100')))
        
        # Valor atualizado
        valor_atualizado = valor_base * fator_correcao
        percentual_correcao = ((fator_correcao - Decimal('1.0')) * Decimal('100'))
        
        return {
            'valor_base': float(valor_base),
            'valor_atualizado': float(valor_atualizado),
            'percentual_correcao': float(percentual_correcao),
            'fator_correcao': float(fator_correcao),
            'meses_calculados': len(historico)
        }
    
    @staticmethod
    def registrar_atualizacao(
        processo_id: int,
        indice_id: int,
        data_base: date,
        valor_base: Decimal
    ) -> ProcessoAtualizacaoMonetaria:
        """
        Registra uma atualização monetária para um processo
        """
        # Calcular atualização
        resultado = AtualizacaoMonetariaService.calcular_atualizacao(
            valor_base=valor_base,
            data_base=data_base,
            data_atualizacao=date.today(),
            indice_id=indice_id
        )
        
        try:
            atualizacao = ProcessoAtualizacaoMonetaria(
                processo_id=processo_id,
                indice_id=indice_id,
                data_base=data_base,
                valor_base=valor_base,
                data_atualizacao=date.today(),
                valor_atualizado=Decimal(str(resultado['valor_atualizado'])),
                percentual_correcao=Decimal(str(resultado['percentual_correcao']))
            )
            
            db.session.add(atualizacao)
            db.session.commit()
            
            return atualizacao
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def listar_atualizacoes_processo(processo_id: int) -> List[Dict[str, Any]]:
        """Lista todas as atualizações de um processo"""
        atualizacoes = ProcessoAtualizacaoMonetaria.query.filter_by(
            processo_id=processo_id
        ).order_by(ProcessoAtualizacaoMonetaria.calculado_em.desc()).all()
        
        return [{
            'id': at.id_atualizacao,
            'indice': at.indice.nome,
            'data_base': at.data_base.isoformat(),
            'valor_base': float(at.valor_base),
            'data_atualizacao': at.data_atualizacao.isoformat(),
            'valor_atualizado': float(at.valor_atualizado) if at.valor_atualizado else None,
            'percentual_correcao': float(at.percentual_correcao) if at.percentual_correcao else None,
            'calculado_em': at.calculado_em.isoformat()
        } for at in atualizacoes]
