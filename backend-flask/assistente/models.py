"""
Modelos SQLAlchemy para o módulo Assistente
"""
import os
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Modelo para conversa
class Conversa(Base):
    __tablename__ = 'conversa_assistente'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(String(255), nullable=False, default="Nova Conversa")
    modelo_llm = Column(String(50), nullable=False)
    personalidade = Column(String(50), nullable=False, default="Advogado")
    tom_voz = Column(String(50), nullable=False, default="Natural")
    usuario_id = Column(String(36), nullable=True)  # Pode ser null para conversas anônimas
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    mensagens = relationship("Mensagem", back_populates="conversa", cascade="all, delete-orphan")

# Modelo para mensagem
class Mensagem(Base):
    __tablename__ = 'mensagem_assistente'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversa_id = Column(String(36), ForeignKey('conversa_assistente.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    metadados = Column(Text, nullable=True)  # JSON com informações adicionais
    
    # Relacionamentos
    conversa = relationship("Conversa", back_populates="mensagens")
    anexos = relationship("Anexo", back_populates="mensagem", cascade="all, delete-orphan")

# Modelo para anexo
class Anexo(Base):
    __tablename__ = 'anexo_assistente'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mensagem_id = Column(String(36), ForeignKey('mensagem_assistente.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    filetype = Column(String(50), nullable=False)  # 'image', 'document', etc.
    filesize = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    processado = Column(Boolean, default=False)
    
    # Relacionamentos
    mensagem = relationship("Mensagem", back_populates="anexos")

# Criação de tabelas e sessão
def init_db():
    """
    Inicializa o banco de dados e cria as tabelas necessárias
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(os.getenv("DATABASE_URL"), pool_pre_ping=True, pool_recycle=300)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()