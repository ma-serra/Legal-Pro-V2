"""
Modelo para Comparação de Documentos
"""
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class ComparacaoDocumento(db.Model):
    """
    Modelo para armazenar comparações de versões de documentos
    """
    __tablename__ = "comparacoes"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = db.Column(db.Text, nullable=False)
    area_processo = db.Column(db.String(10), nullable=False)
    descricao_area = db.Column(db.Text, nullable=False)
    documento_cliente = db.Column(db.String(18), nullable=False, index=True)
    data_comparacao = db.Column(db.DateTime, default=datetime.utcnow)
    resultado_html_lado_a = db.Column(db.Text, nullable=True)
    resultado_html_lado_b = db.Column(db.Text, nullable=True)
    resultado_editado_a = db.Column(db.Text, nullable=True)
    resultado_editado_b = db.Column(db.Text, nullable=True)
    doc_metadata = db.Column(JSONB, nullable=True)
    created_by_id = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<ComparacaoDocumento {self.titulo}>'
