"""
Modelos de banco de dados para o Sistema Administrativo Vetorial
"""

from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

class ArquivoVetorial(db.Model):
    """Modelo para arquivos com processamento vetorial"""
    __tablename__ = 'arquivos_vetoriais'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text)
    area_juridica = Column(String(100))
    embeddings_count = Column(Integer, default=0)
    processed_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Metadados adicionais
    file_size = Column(Integer)
    processing_time = Column(Float)
    quality_score = Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'area_juridica': self.area_juridica,
            'embeddings_count': self.embeddings_count,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'file_size': self.file_size,
            'quality_score': self.quality_score
        }

class ArquivoRelacional(db.Model):
    """Modelo para arquivos com armazenamento relacional simples"""
    __tablename__ = 'arquivos_relacionais'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Metadados
    mime_type = Column(String(100))
    checksum = Column(String(64))
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'mime_type': self.mime_type
        }

class SystemMetrics(db.Model):
    """Modelo para métricas do sistema"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    additional_data = Column(Text)  # JSON string para dados extras
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit
        }

def init_admin_vectorial_tables():
    """Inicializa as tabelas do sistema administrativo vetorial"""
    try:
        # Criar todas as tabelas
        db.create_all()
        
        # Inserir métricas iniciais se não existirem
        if not SystemMetrics.query.first():
            initial_metrics = [
                SystemMetrics(metric_name='system_health', metric_value=100.0, metric_unit='percent'),
                SystemMetrics(metric_name='total_uploads', metric_value=0.0, metric_unit='count'),
                SystemMetrics(metric_name='vectorial_uploads', metric_value=0.0, metric_unit='count'),
                SystemMetrics(metric_name='storage_size', metric_value=0.0, metric_unit='mb')
            ]
            
            for metric in initial_metrics:
                db.session.add(metric)
            
            db.session.commit()
            
        return True
        
    except Exception as e:
        print(f"Erro ao inicializar tabelas: {e}")
        return False