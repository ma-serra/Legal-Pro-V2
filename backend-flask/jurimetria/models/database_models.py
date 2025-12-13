"""
Modelos de banco de dados para jurimetria
Define toda a estrutura relacional do sistema
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from jurimetria.config.database import Base
import uuid
import json

# Tipo UUID para compatibilidade
try:
    # PostgreSQL
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    UUID_TYPE = PG_UUID(as_uuid=True)
except ImportError:
    # SQLite fallback
    UUID_TYPE = String(36)

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ===== TABELAS DE CONFIGURAÇÃO =====

class AreaJuridica(BaseModel):
    __tablename__ = 'areas_juridicas'
    
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    ativa = Column(Boolean, default=True)
    
    # Valores base para cálculos
    valor_base_moral = Column(Float, default=0)
    valor_base_material = Column(Float, default=0)
    valor_base_emergente = Column(Float, default=0)
    
    # Fatores multiplicadores
    fator_complexidade_baixa = Column(Float, default=0.8)
    fator_complexidade_media = Column(Float, default=1.0)
    fator_complexidade_alta = Column(Float, default=1.3)

class Comarca(BaseModel):
    __tablename__ = 'comarcas'
    
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    estado = Column(String(2), nullable=False)
    tipo = Column(String(20), nullable=False)  # capital, metropolitana, interior
    regiao = Column(String(20), nullable=False)  # sudeste, sul, nordeste, norte, centro_oeste
    
    # Fatores específicos da comarca
    fator_valor = Column(Float, default=1.0)
    custo_vida_index = Column(Float, default=1.0)
    
    ativa = Column(Boolean, default=True)

class TipoProcesso(BaseModel):
    __tablename__ = 'tipos_processo'
    
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    area_juridica_id = Column(UUID_TYPE, ForeignKey('areas_juridicas.id'))
    
    # Probabilidades base por tipo histórico do réu
    prob_primario = Column(Float, default=0.65)
    prob_reincidente = Column(Float, default=0.40)
    prob_multiplas = Column(Float, default=0.25)
    
    ativo = Column(Boolean, default=True)
    
    # Relacionamento
    area_juridica = relationship("AreaJuridica")

# ===== TABELAS DE DADOS HISTÓRICOS =====

class ProcessoJuridico(BaseModel):
    __tablename__ = 'processos_juridicos'
    
    numero_processo = Column(String(100), unique=True, nullable=False)
    tipo_processo_id = Column(UUID_TYPE, ForeignKey('tipos_processo.id'))
    comarca_id = Column(UUID_TYPE, ForeignKey('comarcas.id'))
    
    # Dados do processo
    data_distribuicao = Column(DateTime)
    data_sentenca = Column(DateTime)
    data_transito_julgado = Column(DateTime)
    
    # Características
    valor_causa = Column(Float)
    complexidade = Column(String(20))  # baixa, media, alta
    representacao = Column(String(30))  # com_advogado, defensoria, pro_se
    urgencia = Column(String(20))  # normal, prioritaria, urgente
    
    # Resultados
    resultado = Column(String(30))  # procedente, improcedente, parcialmente_procedente
    valor_condenacao = Column(Float)
    tempo_duracao_meses = Column(Integer)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    tipo_processo = relationship("TipoProcesso")
    comarca = relationship("Comarca")

class IndenizacaoHistorica(BaseModel):
    __tablename__ = 'indenizacoes_historicas'
    
    processo_id = Column(UUID_TYPE, ForeignKey('processos_juridicos.id'))
    
    # Características da vítima
    idade_vitima = Column(Integer)
    genero_vitima = Column(String(10))
    profissao_vitima = Column(String(100))
    
    # Tipo de lesão/dano
    tipo_lesao = Column(String(30))  # moral, material, emergente, estetico
    gravidade = Column(Integer)  # 1-10
    
    # Valor da indenização
    valor_indenizacao = Column(Float, nullable=False)
    
    # Fatores adicionais
    precedentes_citados = Column(JSON)
    argumentos_principais = Column(Text)
    
    # Relacionamento
    processo = relationship("ProcessoJuridico")

class TendenciaProcessual(BaseModel):
    __tablename__ = 'tendencias_processuais'
    
    # Período da tendência
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    
    # Identificação
    tipo_processo_id = Column(UUID_TYPE, ForeignKey('tipos_processo.id'))
    comarca_id = Column(UUID_TYPE, ForeignKey('comarcas.id'))
    
    # Métricas
    total_processos = Column(Integer, default=0)
    processos_procedentes = Column(Integer, default=0)
    processos_improcedentes = Column(Integer, default=0)
    tempo_medio_meses = Column(Float, default=0)
    valor_medio_indenizacao = Column(Float, default=0)
    
    # Índices únicos
    __table_args__ = (
        UniqueConstraint('ano', 'mes', 'tipo_processo_id', 'comarca_id'),
        Index('idx_tendencia_periodo', 'ano', 'mes'),
        Index('idx_tendencia_tipo', 'tipo_processo_id'),
        Index('idx_tendencia_comarca', 'comarca_id')
    )
    
    # Relacionamentos
    tipo_processo = relationship("TipoProcesso")
    comarca = relationship("Comarca")

# ===== TABELAS DE ANÁLISE DE DOCUMENTOS =====

class DocumentoAnalise(BaseModel):
    __tablename__ = 'documentos_analise'
    
    # Identificação
    titulo = Column(String(500), nullable=False)
    tipo_documento = Column(String(50))  # peticao, contestacao, sentenca, recurso
    
    # Conteúdo
    conteudo_texto = Column(Text, nullable=False)
    conteudo_preprocessado = Column(Text)
    
    # Análise de sentimento
    polaridade = Column(Float)  # -1 a 1
    subjetividade = Column(Float)  # 0 a 1
    categoria_sentimento = Column(String(20))  # positivo, negativo, neutro
    confianca_sentimento = Column(Float)
    
    # Classificação automática
    categoria_documento = Column(String(50))
    confianca_classificacao = Column(Float)
    
    # Entidades extraídas
    entidades = Column(JSON)  # pessoas, leis, artigos, valores
    
    # Padrões identificados
    padroes_estruturais = Column(JSON)
    score_argumentativo = Column(Float)
    complexidade_sintatica = Column(Float)
    densidade_juridica = Column(Float)
    
    # Vetorização
    embedding_vector = Column(JSON)  # Para busca semântica
    
    # Status
    processado = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)

# ===== TABELAS DE MODELOS ESTATÍSTICOS =====

class ModeloEstatistico(BaseModel):
    __tablename__ = 'modelos_estatisticos'
    
    # Identificação
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50), nullable=False)  # regressao, arvore, neural, series, sobrevivencia
    versao = Column(String(20), default='1.0')
    
    # Configuração
    parametros = Column(JSON)
    hiperparametros = Column(JSON)
    
    # Performance
    acuracia = Column(Float)
    precisao = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    r_quadrado = Column(Float)
    mae = Column(Float)
    rmse = Column(Float)
    
    # Dados de treinamento
    data_treinamento = Column(DateTime)
    total_samples = Column(Integer)
    features_utilizadas = Column(JSON)
    
    # Status
    ativo = Column(Boolean, default=True)
    em_producao = Column(Boolean, default=False)
    
    # Arquivo do modelo serializado
    caminho_modelo = Column(String(500))

class PredicaoRealizada(BaseModel):
    __tablename__ = 'predicoes_realizadas'
    
    # Modelo utilizado
    modelo_id = Column(UUID_TYPE, ForeignKey('modelos_estatisticos.id'))
    
    # Entrada
    dados_entrada = Column(JSON, nullable=False)
    
    # Resultado da predição
    resultado_predicao = Column(JSON, nullable=False)
    confianca = Column(Float)
    
    # Feedback (opcional)
    resultado_real = Column(JSON)
    acertou_predicao = Column(Boolean)
    erro_absoluto = Column(Float)
    
    # Contexto
    ip_usuario = Column(String(50))
    user_agent = Column(String(500))
    
    # Relacionamento
    modelo = relationship("ModeloEstatistico")

# ===== TABELAS DE CACHE E PERFORMANCE =====

class CacheAnalise(BaseModel):
    __tablename__ = 'cache_analises'
    
    # Chave do cache
    hash_entrada = Column(String(64), unique=True, nullable=False)
    
    # Dados originais
    dados_entrada = Column(JSON, nullable=False)
    
    # Resultado cached
    resultado = Column(JSON, nullable=False)
    
    # Metadados
    tipo_analise = Column(String(50))
    tempo_processamento_ms = Column(Integer)
    hits = Column(Integer, default=0)
    
    # Expiração
    expira_em = Column(DateTime)
    ativo = Column(Boolean, default=True)

class LogAnalise(BaseModel):
    __tablename__ = 'logs_analises'
    
    # Identificação
    tipo_analise = Column(String(50), nullable=False)
    usuario_id = Column(String(100))
    sessao_id = Column(String(100))
    
    # Timing
    inicio_processamento = Column(DateTime, nullable=False)
    fim_processamento = Column(DateTime)
    tempo_total_ms = Column(Integer)
    
    # Entrada
    dados_entrada = Column(JSON)
    tamanho_entrada_bytes = Column(Integer)
    
    # Resultado
    sucesso = Column(Boolean, default=False)
    codigo_erro = Column(String(50))
    mensagem_erro = Column(Text)
    
    # Performance
    memoria_utilizada_mb = Column(Float)
    cpu_utilizado_percent = Column(Float)
    
    # IP e User Agent
    ip_cliente = Column(String(50))
    user_agent = Column(String(500))

class MetricasSistema(BaseModel):
    __tablename__ = 'metricas_sistema'
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=func.now())
    
    # Métricas de uso
    total_usuarios_ativos = Column(Integer, default=0)
    total_analises_dia = Column(Integer, default=0)
    total_predicoes_dia = Column(Integer, default=0)
    
    # Performance
    tempo_medio_resposta_ms = Column(Float, default=0)
    taxa_erro_percent = Column(Float, default=0)
    uptime_percent = Column(Float, default=100)
    
    # Recursos
    uso_cpu_percent = Column(Float, default=0)
    uso_memoria_percent = Column(Float, default=0)
    uso_disco_percent = Column(Float, default=0)
    
    # Banco de dados
    total_registros_db = Column(Integer, default=0)
    tamanho_db_mb = Column(Float, default=0)
    
    # Cache
    hit_rate_cache_percent = Column(Float, default=0)
    tamanho_cache_mb = Column(Float, default=0)

# ===== ÍNDICES PARA PERFORMANCE =====

# Índices adicionais para otimização
Index('idx_processo_data_distribuicao', ProcessoJuridico.data_distribuicao)
Index('idx_processo_data_sentenca', ProcessoJuridico.data_sentenca)
Index('idx_processo_valor_causa', ProcessoJuridico.valor_causa)
Index('idx_indenizacao_tipo_lesao', IndenizacaoHistorica.tipo_lesao)
Index('idx_indenizacao_gravidade', IndenizacaoHistorica.gravidade)
Index('idx_documento_tipo', DocumentoAnalise.tipo_documento)
Index('idx_documento_categoria', DocumentoAnalise.categoria_documento)
Index('idx_predicao_data', PredicaoRealizada.created_at)
Index('idx_log_tipo_analise', LogAnalise.tipo_analise)
Index('idx_log_timestamp', LogAnalise.inicio_processamento)
Index('idx_cache_tipo', CacheAnalise.tipo_analise)
Index('idx_cache_expiracao', CacheAnalise.expira_em)