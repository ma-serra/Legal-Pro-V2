from main import db
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, ForeignKey, JSON, func, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import datetime
import uuid

# Import existing models from models.py to avoid duplicates
from models import (
    Processo,
    ProcessoCamposEspecificos,
    ProcessoTributario,
    ProcessoTese,
    ProcessoPrognosticoTributario,
    ProcessoTrabalhista,
    ProcessoPrognosticoTrabalhista,
    ProcessoCivel,
    ProcessoPrognosticoCivel,
    ProcessoAtualizacaoMonetaria
)

# ============================================================================
# SISTEMA DE PROCESSOS DINÂMICOS - EXTENSÕES
# Refatorado: Classes base (Processo, etc) importadas de models.py
# ============================================================================

class Tributo(db.Model):
    """Cadastro de tributos"""
    __tablename__ = 'tributos'
    
    id_tributo = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    esfera = Column(String(20))  # Federal, Estadual, Municipal
    ativo = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships definition requires ProcessoTributario to be available (back_populates)
    teses = relationship('TeseTributaria', back_populates='tributo')
    processos_tributarios = relationship('ProcessoTributario', back_populates='tributo')
    
    def __repr__(self):
        return f'<Tributo {self.codigo}: {self.nome}>'


class TeseTributaria(db.Model):
    """Teses jurídicas tributárias"""
    __tablename__ = 'teses_tributarias'
    
    id_tese = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    descricao = Column(Text)
    tributo_id = Column(Integer, ForeignKey('tributos.id_tributo'))
    
    # Jurisprudência
    tema_repercussao_geral = Column(String(50))
    tema_repetitivo = Column(String(50))
    tribunal_origem = Column(String(100))
    
    # Prognóstico padrão
    probabilidade_sucesso = Column(Numeric(5, 2))
    fundamentacao = Column(Text)
    situacao = Column(String(50))  # Favorável, Desfavorável, Pendente, Superada
    
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Auditoria
    criado_por = Column(Integer)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    tributo = relationship('Tributo', back_populates='teses')
    processos = relationship('ProcessoTese', back_populates='tese')
    
    def __repr__(self):
        return f'<TeseTributaria {self.codigo}: {self.titulo[:50]}>'
    
    def to_dict(self):
        return {
            'id_tese': self.id_tese,
            'codigo': self.codigo,
            'titulo': self.titulo,
            'tributo': self.tributo.nome if self.tributo else None,
            'probabilidade_sucesso': float(self.probabilidade_sucesso) if self.probabilidade_sucesso else None,
            'situacao': self.situacao
        }

class IndiceMonetario(db.Model):
    """Cadastro de índices de correção monetária"""
    __tablename__ = 'indices_monetarios'
    
    id_indice = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text)
    fonte_oficial = Column(String(200))
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    historico = relationship('HistoricoIndice', back_populates='indice', cascade='all, delete-orphan')
    atualizacoes = relationship('ProcessoAtualizacaoMonetaria', back_populates='indice')
    
    def __repr__(self):
        return f'<IndiceMonetario {self.nome}>'


class HistoricoIndice(db.Model):
    """Histórico de valores dos índices monetários"""
    __tablename__ = 'historico_indices'
    
    id_historico = Column(Integer, primary_key=True)
    indice_id = Column(Integer, ForeignKey('indices_monetarios.id_indice'), nullable=False)
    data_referencia = Column(DateTime, nullable=False)
    valor = Column(Numeric(10, 6), nullable=False)
    
    data_importacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    indice = relationship('IndiceMonetario', back_populates='historico')
    
    __table_args__ = (
        UniqueConstraint('indice_id', 'data_referencia', name='uk_indice_data'),
        Index('idx_hist_indice', 'indice_id'),
        Index('idx_hist_data', 'data_referencia'),
    )


class ConfiguracaoFormulario(db.Model):
    """Configuração dinâmica de formulários por natureza"""
    __tablename__ = 'configuracao_formulario'
    
    id_configuracao = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    natureza_id = Column(Integer)
    
    # Estrutura do formulário em JSON
    campos_obrigatorios = Column(JSONB, nullable=False, default=[])
    campos_opcionais = Column(JSONB, nullable=False, default=[])
    validacoes = Column(JSONB, nullable=False, default={})
    layout = Column(JSONB, nullable=False, default={})
    
    # Versão
    versao = Column(Integer, default=1)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Auditoria
    criado_por = Column(Integer)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'natureza_id', 'versao', name='uk_tenant_natureza_versao'),
    )
