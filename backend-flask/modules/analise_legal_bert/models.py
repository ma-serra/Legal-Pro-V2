"""
Modelos para o módulo de Análise Legal BERTimbau
"""

from main import db
from datetime import datetime
import json


class AnaliseLegalDocumentoBert(db.Model):
    """Modelo para documentos analisados pelo sistema legal"""
    __tablename__ = 'analise_legal_documento'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    tipo_documento = db.Column(db.String(100))  # contrato, petição, sentença, etc.
    conteudo_original = db.Column(db.Text, nullable=False)
    conteudo_processado = db.Column(db.Text)
    resumo_automatico = db.Column(db.Text)
    score_confianca = db.Column(db.Float, default=0.0)
    status_analise = db.Column(db.String(50), default='pendente')  # pendente, processando, concluida, erro
    resultado_analise = db.Column(db.JSON)  # Resultado completo da análise
    
    # Metadados de processamento
    tempo_processamento = db.Column(db.Float)  # em segundos
    modelo_utilizado = db.Column(db.String(100), default='regex_nlp_tradicional')
    versao_sistema = db.Column(db.String(20), default='1.0')
    
    # Campos de auditoria
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    entidades = db.relationship('EntidadeExtraidaBert', backref='documento', cascade='all, delete-orphan', overlaps="entidades,documento")
    classificacoes = db.relationship('ClassificacaoDocumentoBert', backref='documento', cascade='all, delete-orphan', overlaps="classificacoes,documento")
    
    def __repr__(self):
        return f'<AnaliseLegalDocumentoBert {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo_documento': self.tipo_documento,
            'conteudo_original': self.conteudo_original[:200] + '...' if len(self.conteudo_original) > 200 else self.conteudo_original,
            'resumo_automatico': self.resumo_automatico,
            'score_confianca': self.score_confianca,
            'status_analise': self.status_analise,
            'resultado_analise': self.resultado_analise,
            'tempo_processamento': self.tempo_processamento,
            'modelo_utilizado': self.modelo_utilizado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EntidadeExtraidaBert(db.Model):
    """Modelo para entidades extraídas dos documentos"""
    __tablename__ = 'entidade_extraida'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('analise_legal_documento.id'), nullable=False)
    tipo_entidade = db.Column(db.String(50), nullable=False)  # PESSOA, EMPRESA, DATA, VALOR, etc.
    texto_entidade = db.Column(db.String(500), nullable=False)
    posicao_inicio = db.Column(db.Integer)
    posicao_fim = db.Column(db.Integer)
    confianca = db.Column(db.Float, default=0.0)
    contexto = db.Column(db.String(200))  # Contexto ao redor da entidade
    normalizada = db.Column(db.String(500))  # Versão normalizada da entidade
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EntidadeExtraidaBert {self.tipo_entidade}: {self.texto_entidade}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'tipo_entidade': self.tipo_entidade,
            'texto_entidade': self.texto_entidade,
            'posicao_inicio': self.posicao_inicio,
            'posicao_fim': self.posicao_fim,
            'confianca': self.confianca,
            'contexto': self.contexto,
            'normalizada': self.normalizada,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ClassificacaoDocumentoBert(db.Model):
    """Modelo para classificações de documentos"""
    __tablename__ = 'classificacao_documento'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('analise_legal_documento.id'), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)  # Categoria principal
    subcategoria = db.Column(db.String(100))  # Subcategoria específica
    confianca = db.Column(db.Float, nullable=False, default=0.0)
    justificativa = db.Column(db.Text)  # Explicação da classificação
    palavras_chave = db.Column(db.JSON)  # Palavras-chave que levaram à classificação
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClassificacaoDocumentoBert {self.categoria}: {self.confianca:.2f}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'confianca': self.confianca,
            'justificativa': self.justificativa,
            'palavras_chave': self.palavras_chave,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }