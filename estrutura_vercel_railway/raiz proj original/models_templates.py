"""
Modelos de dados para o sistema de templates jurídicos do Legal Design Pro
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from main import db

# Evitar conflitos com outras definições usando nomes únicos
__tablename_prefix__ = 'legal_design_'

class AreaJuridica(db.Model):
    """Áreas jurídicas disponíveis no sistema"""
    __tablename__ = 'areas_juridicas_templates'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    icone = Column(String(50), nullable=False)  # emoji ou classe de ícone
    descricao = Column(Text)
    cor_tema = Column(String(7), default='#007bff')  # cor hexadecimal
    ativo = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    templates = relationship('TemplateJuridico', back_populates='area_juridica', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AreaJuridica {self.nome}>'

class TipoDocumento(db.Model):
    """Tipos de documentos jurídicos"""
    __tablename__ = 'tipos_documento_templates'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)  # peticao, recurso, defesa, etc.
    descricao = Column(Text)
    icone = Column(String(50))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    templates = relationship('TemplateJuridico', back_populates='tipo_documento', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TipoDocumento {self.nome}>'

class TemplateJuridico(db.Model):
    """Templates de documentos jurídicos"""
    __tablename__ = 'templates_juridicos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    conteudo_html = Column(Text, nullable=False)
    conteudo_texto = Column(Text)  # versão em texto puro para busca
    
    # Relacionamentos
    area_juridica_id = Column(Integer, ForeignKey('areas_juridicas_templates.id'), nullable=False)
    tipo_documento_id = Column(Integer, ForeignKey('tipos_documento_templates.id'), nullable=False)
    
    # Metadados
    palavras_chave = Column(Text)  # separadas por vírgula
    complexidade = Column(String(20), default='intermediario')  # basico, intermediario, avancado
    tempo_estimado = Column(Integer)  # em minutos
    
    # Controle de versão e auditoria
    versao = Column(String(10), default='1.0')
    criado_por = Column(String(100))
    modificado_por = Column(String(100))
    criado_em = Column(DateTime, default=datetime.utcnow)
    modificado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status e uso
    ativo = Column(Boolean, default=True)
    uso_contador = Column(Integer, default=0)
    favorito = Column(Boolean, default=False)
    
    # Relacionamentos
    area_juridica = relationship('AreaJuridica', back_populates='templates')
    tipo_documento = relationship('TipoDocumento', back_populates='templates')
    historico_uso = relationship('HistoricoUsoTemplate', back_populates='template', cascade='all, delete-orphan')
    
    # Índices para otimização
    __table_args__ = (
        Index('idx_template_area_tipo', 'area_juridica_id', 'tipo_documento_id'),
        Index('idx_template_ativo', 'ativo'),
        Index('idx_template_palavras_chave', 'palavras_chave'),
        Index('idx_template_complexidade', 'complexidade'),
    )
    
    def __repr__(self):
        return f'<TemplateJuridico {self.nome}>'
    
    def incrementar_uso(self):
        """Incrementa contador de uso do template"""
        self.uso_contador += 1
        db.session.commit()

class HistoricoUsoTemplate(db.Model):
    """Histórico de uso dos templates pelos usuários"""
    __tablename__ = 'historico_uso_templates'
    
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('templates_juridicos.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'))  # pode ser null para usuários anônimos
    ip_address = Column(String(45))
    user_agent = Column(Text)
    usado_em = Column(DateTime, default=datetime.utcnow)
    
    # Contexto de uso
    projeto_nome = Column(String(200))  # nome do documento/projeto criado
    modificacoes_realizadas = Column(Boolean, default=False)  # se o usuário modificou o template
    
    # Relacionamentos
    template = relationship('TemplateJuridico', back_populates='historico_uso')
    
    def __repr__(self):
        return f'<HistoricoUsoTemplate {self.template_id} em {self.usado_em}>'

class FavoritoTemplate(db.Model):
    """Templates favoritos dos usuários"""
    __tablename__ = 'favoritos_templates'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('templates_juridicos.id'), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Índice único para evitar duplicatas
    __table_args__ = (
        Index('idx_favorito_unico', 'usuario_id', 'template_id', unique=True),
    )
    
    def __repr__(self):
        return f'<FavoritoTemplate usuario:{self.usuario_id} template:{self.template_id}>'