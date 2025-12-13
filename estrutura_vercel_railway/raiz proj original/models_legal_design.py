"""
Modelos de dados específicos para o Legal Design Pro
Arquivo separado para evitar conflitos de SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from main import db

class LegalAreaJuridica(db.Model):
    """Áreas jurídicas para o Legal Design Pro"""
    __tablename__ = 'legal_areas_juridicas'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    icone = Column(String(50), nullable=False)
    descricao = Column(Text)
    cor_tema = Column(String(7), default='#007bff')
    ativo = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    templates = relationship('LegalTemplateJuridico', back_populates='area_juridica', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LegalAreaJuridica {self.nome}>'

class LegalTipoDocumento(db.Model):
    """Tipos de documentos para o Legal Design Pro"""
    __tablename__ = 'legal_tipos_documento'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)
    descricao = Column(Text)
    icone = Column(String(50))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    templates = relationship('LegalTemplateJuridico', back_populates='tipo_documento', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LegalTipoDocumento {self.nome}>'

class LegalTemplateJuridico(db.Model):
    """Templates de documentos para o Legal Design Pro"""
    __tablename__ = 'legal_templates_juridicos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    conteudo_html = Column(Text, nullable=False)
    conteudo_texto = Column(Text)
    
    area_juridica_id = Column(Integer, ForeignKey('legal_areas_juridicas.id'), nullable=False)
    tipo_documento_id = Column(Integer, ForeignKey('legal_tipos_documento.id'), nullable=False)
    
    palavras_chave = Column(Text)
    complexidade = Column(String(20), default='intermediario')
    tempo_estimado = Column(Integer)
    
    versao = Column(String(10), default='1.0')
    criado_por = Column(String(100))
    modificado_por = Column(String(100))
    criado_em = Column(DateTime, default=datetime.utcnow)
    modificado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ativo = Column(Boolean, default=True)
    uso_contador = Column(Integer, default=0)
    favorito = Column(Boolean, default=False)
    
    # Relacionamentos
    area_juridica = relationship('LegalAreaJuridica', back_populates='templates')
    tipo_documento = relationship('LegalTipoDocumento', back_populates='templates')
    historico_uso = relationship('LegalHistoricoUsoTemplate', back_populates='template', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_legal_template_area_tipo', 'area_juridica_id', 'tipo_documento_id'),
        Index('idx_legal_template_ativo', 'ativo'),
        Index('idx_legal_template_palavras_chave', 'palavras_chave'),
        Index('idx_legal_template_complexidade', 'complexidade'),
    )
    
    def __repr__(self):
        return f'<LegalTemplateJuridico {self.nome}>'
    
    def incrementar_uso(self):
        """Incrementa contador de uso do template"""
        self.uso_contador += 1
        db.session.commit()

class LegalHistoricoUsoTemplate(db.Model):
    """Histórico de uso dos templates do Legal Design Pro"""
    __tablename__ = 'legal_historico_uso_templates'
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('legal_templates_juridicos.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    usado_em = Column(DateTime, default=datetime.utcnow)
    
    projeto_nome = Column(String(200))
    modificacoes_realizadas = Column(Boolean, default=False)
    
    # Relacionamentos
    template = relationship('LegalTemplateJuridico', back_populates='historico_uso')
    
    def __repr__(self):
        return f'<LegalHistoricoUsoTemplate {self.template_id}>'

class LegalFavoritoTemplate(db.Model):
    """Templates favoritos dos usuários do Legal Design Pro"""
    __tablename__ = 'legal_favoritos_templates'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('legal_templates_juridicos.id'), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_legal_favorito_unico', 'usuario_id', 'template_id', unique=True),
    )
    
    def __repr__(self):
        return f'<LegalFavoritoTemplate {self.usuario_id}:{self.template_id}>'