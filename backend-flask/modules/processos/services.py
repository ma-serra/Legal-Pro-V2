"""
ProcessoService - CRUD e lógica de negócio para processos
Fase 2 - Backend Core
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from decimal import Decimal
from datetime import datetime

from main import db
from models import (
    Processo,
    ProcessoCamposEspecificos,
    Tributo,
    TeseTributaria,
    ProcessoTributario,
    ProcessoTese,
    ProcessoTrabalhista,
    ProcessoCivel,
    IndiceMonetario,
    ProcessoAtualizacaoMonetaria
)


class ProcessoService:
    """
    Service para operações de processos jurídicos
    
    Responsabilidades:
    - CRUD de processos
    - Validações de negócio
    - Gestão de campos específicos por natureza
    - Cálculos de atualização monetária
    - Prognósticos
    """
    
    @staticmethod
    def criar_processo(data: Dict[str, Any]) -> Processo:
        """
        Cria um novo processo
        
        Args:
            data: Dados do processo
            
        Returns:
            Processo criado
            
        Raises:
            ValueError: Se dados inválidos
            IntegrityError: Se violação de constraint
        """
        try:
            # Criar processo principal
            processo = Processo(
                numero_cnj=data.get('numero_cnj'),
                pasta=data.get('pasta'),
                natureza_id=data.get('natureza_id'),
                status_id=data.get('status_id'),
                cliente_id=data.get('cliente_id'),
                posicao_cliente_id=data.get('posicao_cliente_id'),
                acao_id=data.get('acao_id'),
                procedimento_id=data.get('procedimento_id'),
                fase_id=data.get('fase_id'),
                orgao_id=data.get('orgao_id'),
                comarca_id=data.get('comarca_id'),
                vara_turma_id=data.get('vara_turma_id'),
                justica_cnj_id=data.get('justica_cnj_id'),
                instancia_cnj_id=data.get('instancia_cnj_id'),
                classe_cnj_id=data.get('classe_cnj_id'),
                data_distribuicao=data.get('data_distribuicao'),
                valor_causa=data.get('valor_causa'),
                valor_envolvido=data.get('valor_envolvido'),
                contingencia=data.get('contingencia'),
                tipo_probabilidade_id=data.get('tipo_probabilidade_id'),
                risco_id=data.get('risco_id'),
                titulo=data.get('titulo'),
                observacao_pasta=data.get('observacao_pasta'),
                tenant_id=data.get('tenant_id')
            )
            
            db.session.add(processo)
            db.session.flush()  # Para obter o ID
            
            # Criar campos específicos se fornecidos
            if 'campos_especificos' in data:
                ProcessoService._criar_campos_especificos(
                    processo.id_processo,
                    data['natureza_id'],
                    data['campos_especificos']
                )
            
            # Criar dados específicos por natureza
            natureza_nome = ProcessoService._get_natureza_nome(data.get('natureza_id'))
            
            if natureza_nome == 'Tributário' and 'dados_tributario' in data:
                ProcessoService._criar_processo_tributario(
                    processo.id_processo,
                    data['dados_tributario']
                )
            
            elif natureza_nome == 'Trabalhista' and 'dados_trabalhista' in data:
                ProcessoService._criar_processo_trabalhista(
                    processo.id_processo,
                    data['dados_trabalhista']
                )
            
            elif natureza_nome == 'Cível' and 'dados_civel' in data:
                ProcessoService._criar_processo_civel(
                    processo.id_processo,
                    data['dados_civel']
                )
            
            db.session.commit()
            return processo
            
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError(f"Erro de integridade: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def listar_processos(
        filtros: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
        ordenacao: str = 'data_criacao',
        ordem: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Lista processos com paginação e filtros
        
        Args:
            filtros: Dicionário de filtros
            page: Página atual
            per_page: Itens por página
            ordenacao: Campo para ordenar
            ordem: asc ou desc
            
        Returns:
            Dict com processos, total, páginas
        """
        query = Processo.query.filter_by(ativo=True)
        
        # Aplicar filtros
        if filtros:
            if 'numero_cnj' in filtros:
                query = query.filter(Processo.numero_cnj.ilike(f"%{filtros['numero_cnj']}%"))
            
            if 'pasta' in filtros:
                query = query.filter(Processo.pasta.ilike(f"%{filtros['pasta']}%"))
            
            if 'natureza_id' in filtros:
                query = query.filter_by(natureza_id=filtros['natureza_id'])
            
            if 'status_id' in filtros:
                query = query.filter_by(status_id=filtros['status_id'])
            
            if 'cliente_id' in filtros:
                query = query.filter_by(cliente_id=filtros['cliente_id'])
            
            if 'data_inicio' in filtros:
                query = query.filter(Processo.data_distribuicao >= filtros['data_inicio'])
            
            if 'data_fim' in filtros:
                query = query.filter(Processo.data_distribuicao <= filtros['data_fim'])
            
            if 'busca' in filtros:
                termo = f"%{filtros['busca']}%"
                query = query.filter(
                    or_(
                        Processo.numero_cnj.ilike(termo),
                        Processo.pasta.ilike(termo),
                        Processo.titulo.ilike(termo)
                    )
                )
        
        # Ordenação
        if ordem == 'desc':
            query = query.order_by(getattr(Processo, ordenacao).desc())
        else:
            query = query.order_by(getattr(Processo, ordenacao).asc())
        
        # Paginação
        paginacao = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'processos': [p.to_dict() for p in paginacao.items],
            'total': paginacao.total,
            'paginas': paginacao.pages,
            'pagina_atual': page,
            'por_pagina': per_page
        }
    
    @staticmethod
    def obter_processo(processo_id: int, incluir_detalhes: bool = True) -> Optional[Processo]:
        """
        Obtém um processo por ID
        
        Args:
            processo_id: ID do processo
            incluir_detalhes: Se deve incluir dados específicos
            
        Returns:
            Processo ou None
        """
        processo = Processo.query.filter_by(id_processo=processo_id, ativo=True).first()
        
        if not processo:
            return None
        
        if incluir_detalhes:
            # Eager load relationships
            # Já carregados por lazy='select' ou 'joined'
            pass
        
        return processo
    
    @staticmethod
    def atualizar_processo(processo_id: int, data: Dict[str, Any]) -> Optional[Processo]:
        """
        Atualiza um processo
        
        Args:
            processo_id: ID do processo
            data: Dados para atualizar
            
        Returns:
            Processo atualizado ou None
        """
        processo = ProcessoService.obter_processo(processo_id)
        
        if not processo:
            return None
        
        try:
            # Atualizar campos principais
            campos_atualizaveis = [
                'numero_cnj', 'pasta', 'status_id', 'natureza_id', 'cliente_id',
                'posicao_cliente_id', 'acao_id', 'procedimento_id', 'fase_id',
                'orgao_id', 'comarca_id', 'vara_turma_id', 'justica_cnj_id',
                'instancia_cnj_id', 'classe_cnj_id', 'data_distribuicao',
                'valor_causa', 'valor_envolvido', 'contingencia',
                'tipo_probabilidade_id', 'risco_id', 'titulo', 'observacao_pasta'
            ]
            
            for campo in campos_atualizaveis:
                if campo in data:
                    setattr(processo, campo, data[campo])
            
            # Atualizar campos específicos se fornecidos
            if 'campos_especificos' in data:
                ProcessoService._atualizar_campos_especificos(
                    processo_id,
                    processo.natureza_id,
                    data['campos_especificos']
                )
            
            processo.data_atualizacao = datetime.utcnow()
            
            db.session.commit()
            return processo
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def deletar_processo(processo_id: int, soft_delete: bool = True) -> bool:
        """
        Deleta um processo (soft ou hard delete)
        
        Args:
            processo_id: ID do processo
            soft_delete: Se True, apenas marca como inativo
            
        Returns:
            True se deletado com sucesso
        """
        processo = ProcessoService.obter_processo(processo_id)
        
        if not processo:
            return False
        
        try:
            if soft_delete:
                processo.ativo = False
                db.session.commit()
            else:
                db.session.delete(processo)
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise
    
    @staticmethod
    def buscar_processos(termo: str, limite: int = 10) -> List[Processo]:
        """
        Busca processos por termo (número CNJ, pasta, título)
        
        Args:
            termo: Termo de busca
            limite: Máximo de resultados
            
        Returns:
            Lista de processos
        """
        termo_like = f"%{termo}%"
        
        processos = Processo.query.filter(
            and_(
                Processo.ativo == True,
                or_(
                    Processo.numero_cnj.ilike(termo_like),
                    Processo.pasta.ilike(termo_like),
                    Processo.titulo.ilike(termo_like)
                )
            )
        ).limit(limite).all()
        
        return processos
    
    # ========================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ========================================================================
    
    @staticmethod
    def _criar_campos_especificos(
        processo_id: int,
        natureza_id: int,
        campos: Dict[str, Any]
    ) -> ProcessoCamposEspecificos:
        """Cria registro de campos específicos JSONB"""
        campos_esp = ProcessoCamposEspecificos(
            processo_id=processo_id,
            natureza_id=natureza_id,
            campos_tributario=campos.get('tributario'),
            campos_trabalhista=campos.get('trabalhista'),
            campos_civel=campos.get('civel')
        )
        
        db.session.add(campos_esp)
        return campos_esp
    
    @staticmethod
    def _atualizar_campos_especificos(
        processo_id: int,
        natureza_id: int,
        campos: Dict[str, Any]
    ):
        """Atualiza campos específicos"""
        campos_esp = ProcessoCamposEspecificos.query.filter_by(
            processo_id=processo_id
        ).first()
        
        if campos_esp:
            if 'tributario' in campos:
                campos_esp.campos_tributario = campos['tributario']
            if 'trabalhista' in campos:
                campos_esp.campos_trabalhista = campos['trabalhista']
            if 'civel' in campos:
                campos_esp.campos_civel = campos['civel']
        else:
            ProcessoService._criar_campos_especificos(
                processo_id, natureza_id, campos
            )
    
    @staticmethod
    def _criar_processo_tributario(processo_id: int, dados: Dict[str, Any]):
        """Cria registro específico de processo tributário"""
        proc_trib = ProcessoTributario(
            processo_id=processo_id,
            tributo_id=dados.get('tributo_id'),
            numero_aiim=dados.get('numero_aiim'),
            numero_cda=dados.get('numero_cda'),
            data_lancamento=dados.get('data_lancamento'),
            valor_inscrito_cda=dados.get('valor_inscrito_cda'),
            valor_principal=dados.get('valor_principal'),
            valor_multa=dados.get('valor_multa'),
            percentual_multa=dados.get('percentual_multa'),
            base_calculo_multa=dados.get('base_calculo_multa'),
            valor_juros=dados.get('valor_juros'),
            indice_juros=dados.get('indice_juros'),
            descricao_indice_juros=dados.get('descricao_indice_juros')
        )
        
        db.session.add(proc_trib)
    
    @staticmethod
    def _criar_processo_trabalhista(processo_id: int, dados: Dict[str, Any]):
        """Cria registro específico de processo trabalhista"""
        proc_trab = ProcessoTrabalhista(
            processo_id=processo_id,
            tolerancia_acordo=dados.get('tolerancia_acordo'),
            acordo_realizado=dados.get('acordo_realizado'),
            data_acordo=dados.get('data_acordo'),
            observacoes_acordo=dados.get('observacoes_acordo')
        )
        
        db.session.add(proc_trab)
    
    @staticmethod
    def _criar_processo_civel(processo_id: int, dados: Dict[str, Any]):
        """Cria registro específico de processo cível"""
        proc_civel = ProcessoCivel(
            processo_id=processo_id,
            tolerancia_acordo=dados.get('tolerancia_acordo'),
            acordo_realizado=dados.get('acordo_realizado'),
            data_acordo=dados.get('data_acordo'),
            observacoes_acordo=dados.get('observacoes_acordo')
        )
        
        db.session.add(proc_civel)
    
    @staticmethod
    def _get_natureza_nome(natureza_id: int) -> Optional[str]:
        """Obtém nome da natureza por ID (mocado por enquanto)"""
        # TODO: Integrar com tabela natureza_processo quando existir
        naturezas = {
            1: 'Tributário',
            2: 'Trabalhista',
            3: 'Cível'
        }
        return naturezas.get(natureza_id)
