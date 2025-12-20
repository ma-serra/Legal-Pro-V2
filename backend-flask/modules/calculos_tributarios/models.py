
from sqlalchemy import Column, String, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from main import db
import uuid

class SimulacaoTributaria(db.Model):
    __tablename__ = 'simulacoes_tributarias'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_nome = Column(String(255), nullable=True)
    tipo_simulacao = Column(String(50), nullable=False)
    parametros_input = Column(JSONB, nullable=False)
    resultado_output = Column(JSONB, nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())
    usuario_id = Column(Integer, nullable=True)
    status = Column(String(20), default='SALVO')

    def to_dict(self):
        return {
            'id': str(self.id),
            'cliente_nome': self.cliente_nome,
            'tipo_simulacao': self.tipo_simulacao,
            'parametros_input': self.parametros_input,
            'resultado_output': self.resultado_output,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'status': self.status
        }
