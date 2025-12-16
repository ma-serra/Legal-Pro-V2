"""
Modelos de dados para o Sistema Multi-Agente.
"""
import datetime
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, UniqueConstraint, Index, Float, JSON, Numeric
from sqlalchemy.orm import relationship
from main import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Classes para o editor de fluxos
@dataclass
class FluxoConfiguracao:
    """Configuração de um fluxo de trabalho."""
    llm_provider: str = "openai"
    modo_debug: bool = False
    timeout_segundos: int = 300
    
@dataclass
class FluxoAgente:
    """Agente em um fluxo de trabalho."""
    id: str
    tipo: str
    nome: str
    descricao: str = ""
    posicao_x: int = 0
    posicao_y: int = 0
    configuracao: Dict[str, Any] = field(default_factory=dict)
    parametros: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class FluxoConexao:
    """Conexão entre agentes em um fluxo de trabalho."""
    origem: str
    destino: str
    tipo: str = "default"
    condicao: str = ""
    
@dataclass
class Fluxo:
    """Fluxo de trabalho completo."""
    id: Optional[int] = None
    nome: str = "Novo Fluxo"
    descricao: str = ""
    agentes: List[FluxoAgente] = field(default_factory=list)
    conexoes: List[FluxoConexao] = field(default_factory=list)
    configuracao: FluxoConfiguracao = field(default_factory=FluxoConfiguracao)
    ativo: bool = True
    criado_em: datetime.datetime = field(default_factory=datetime.datetime.now)
    ultima_atualizacao: Optional[datetime.datetime] = None
    ultima_execucao: Optional[datetime.datetime] = None
    criado_por_id: Optional[int] = None


class FluxoModel(db.Model):
    """
    Modelo para fluxos de trabalho no banco de dados.
    """
    __tablename__ = 'fluxo'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    agentes = Column(Text, nullable=True)  # JSON serializado
    conexoes = Column(Text, nullable=True)  # JSON serializado
    configuracao = Column(Text, nullable=True)  # JSON serializado
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    ultima_execucao = Column(DateTime, nullable=True)
    criado_por_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relacionamentos
    criado_por = relationship("User", backref="fluxos_criados")
    execucoes = relationship("ExecucaoFluxo", back_populates="fluxo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Fluxo {self.id}: {self.nome}>'


# Modelo para Componentes do Editor
class ComponenteEditor(db.Model):
    """Modelo para gerenciar componentes do editor de fluxos"""
    __tablename__ = 'componente_editor'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=False)  # extrator, classificador, analisador, etc.
    tipo = Column(String(100), nullable=False)  # tipo específico do componente
    descricao = Column(Text)
    descricao_detalhada = Column(Text)
    icone = Column(String(100), default='fas fa-cog')
    cor = Column(String(20), default='#47b6b5')
    ativo = Column(Boolean, default=True)
    configuracao = Column(JSON)  # configurações específicas do componente
    prompt_sistema = Column(Text)  # prompt específico do componente
    prompt_usuario = Column(Text)  # template de prompt para usuário
    capacidades = Column(JSON)  # lista de capacidades do componente
    parametros = Column(JSON)  # parâmetros configuráveis
    base_conhecimento = Column(String(200))  # tabela de base vetorial associada
    temperatura = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)
    top_k = Column(Integer, default=5)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Índices para performance
    __table_args__ = (
        Index('idx_componente_categoria', 'categoria'),
        Index('idx_componente_tipo', 'tipo'),
        Index('idx_componente_ativo', 'ativo'),
    )
    
    def __repr__(self):
        return f'<ComponenteEditor {self.id}: {self.nome}>'

    
    @property
    def to_dict(self):
        """Converte o modelo para um dicionário."""
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'descricao_detalhada': self.descricao_detalhada,
            'icone': self.icone,
            'cor': self.cor,
            'ativo': self.ativo,
            'configuracao': self.configuracao or {},
            'prompt_sistema': self.prompt_sistema,
            'prompt_usuario': self.prompt_usuario,
            'capacidades': self.capacidades or [],
            'parametros': self.parametros or {},
            'base_conhecimento': self.base_conhecimento,
            'temperatura': self.temperatura,
            'max_tokens': self.max_tokens,
            'top_k': self.top_k,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    @property
    def to_fluxo(self):
        """Converte o modelo para um objeto Fluxo."""
        try:
            fluxo_dict = self.to_dict
            fluxo = Fluxo(
                id=fluxo_dict['id'],
                nome=fluxo_dict['nome'],
                descricao=fluxo_dict['descricao'],
                ativo=fluxo_dict['ativo'],
                criado_por_id=fluxo_dict['criado_por_id']
            )
            
            # Adiciona os agentes
            for agente_dict in fluxo_dict['agentes']:
                fluxo.agentes.append(FluxoAgente(**agente_dict))
            
            # Adiciona as conexões
            for conexao_dict in fluxo_dict['conexoes']:
                fluxo.conexoes.append(FluxoConexao(**conexao_dict))
            
            # Adiciona a configuração
            if fluxo_dict.get('configuracao'):
                try:
                    fluxo.configuracao = FluxoConfiguracao(**fluxo_dict['configuracao'])
                except:
                    fluxo.configuracao = FluxoConfiguracao()
            
            return fluxo
        except Exception as e:
            # Em caso de erro, retorna um fluxo padrão
            print(f"Erro ao converter para fluxo: {str(e)}")
            return Fluxo(
                id=self.id,
                nome=self.nome,
                descricao=self.descricao
            )


class ExecucaoFluxo(db.Model):
    """
    Modelo para execuções de fluxos.
    """
    __tablename__ = 'execucao_fluxo'
    
    id = Column(Integer, primary_key=True)
    fluxo_id = Column(Integer, ForeignKey('fluxo.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    dados_entrada = Column(Text, nullable=True)  # JSON serializado
    resultado = Column(Text, nullable=True)  # JSON serializado
    status = Column(String(20), nullable=False, default='iniciada')  # iniciada, em_execucao, concluida, erro
    mensagem_erro = Column(Text, nullable=True)
    data_inicio = Column(DateTime, default=datetime.datetime.now)
    data_conclusao = Column(DateTime, nullable=True)
    duracao_segundos = Column(Float, nullable=True)
    log_execucao = Column(Text, nullable=True)
    
    # Relacionamentos
    fluxo = relationship("FluxoModel", back_populates="execucoes")
    usuario = relationship("User", backref="execucoes_fluxo")
    
    def __repr__(self):
        return f'<ExecucaoFluxo {self.id}: Fluxo {self.fluxo_id}>'

# Tabela de associação entre papéis e permissões
role_permissions = Table(
    'role_permissions',
    db.Model.metadata,
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.id'), primary_key=True)
)

class AuditLog(db.Model):
    """
    Modelo para logs de auditoria.
    """
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Para suportar IPv6
    
    user = relationship("User", backref="audit_logs")

class User(UserMixin, db.Model):
    """
    Modelo para usuários do sistema.
    """
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    role = relationship("Role", backref="users")
    
    def set_password(self, password):
        """
        Define a senha do usuário.
        
        Args:
            password: Senha em texto puro
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifica se a senha fornecida corresponde à senha armazenada.
        
        Args:
            password: Senha em texto puro
            
        Returns:
            bool: True se a senha está correta, False caso contrário
        """
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission_code):
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            permission_code: Código da permissão
            
        Returns:
            bool: True se o usuário tem a permissão, False caso contrário
        """
        if self.is_admin:
            return True
            
        if not self.role:
            return False
            
        for permission in self.role.permissions:
            if permission.code == permission_code:
                return True
                
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    """
    Modelo para papéis (roles) no sistema.
    """
    __tablename__ = 'role'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        backref=db.backref("roles", lazy="dynamic")
    )
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    """
    Modelo para permissões no sistema.
    """
    __tablename__ = 'permission'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    code = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<Permission {self.code}>'

# Classes para sistema de permissões de áreas jurídicas
class PermissaoAreaJuridica(db.Model):
    """
    Modelo para permissões de visualização de áreas jurídicas.
    """
    __tablename__ = 'permissao_area_juridica'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    area_juridica = Column(String(64), nullable=False)  # Nome da área jurídica
    pode_visualizar = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relacionamentos
    usuario = relationship("User", backref="permissoes_areas_juridicas")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'area_juridica', name='uix_user_area_juridica'),
    )
    
    def __repr__(self):
        return f'<PermissaoAreaJuridica {self.usuario.username}: {self.area_juridica}>'

# Classes para sistema de agentes jurídicos especializados

class CategoriaJuridica(db.Model):
    """
    Modelo para categorias jurídicas (especialidades).
    """
    __tablename__ = 'categoria_juridica'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)
    icone = Column(String(50), nullable=True)  # Ícone Font Awesome
    cor = Column(String(20), nullable=True)  # Cor em hexadecimal ou nome
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relacionamentos
    agentes = relationship("AgenteJuridico", back_populates="categoria")
    
    def __repr__(self):
        return f'<CategoriaJuridica {self.nome}>'

class AgenteJuridico(db.Model):
    """
    Modelo para informações sobre agentes jurídicos no sistema.
    """
    __tablename__ = 'agente_juridico'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    classe = Column(String(100), nullable=False)  # Nome da classe Python
    descricao = Column(Text, nullable=True)
    detalhes_tecnicos = Column(Text, nullable=True)  # Especificações técnicas em JSON
    categoria_id = Column(Integer, ForeignKey('categoria_juridica.id'), nullable=True)
    nivel_especializacao = Column(Integer, default=1)  # 1-5, onde 5 é o mais especializado
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Campos técnicos adicionais
    nivel = Column(String(50), nullable=True)  # Nível de especialização textual
    modelo_ai = Column(String(50), nullable=True)  # Modelo de IA específico
    temperatura = Column(Float, default=0.7)  # Parâmetro de temperatura (0-2)
    top_p = Column(Float, default=0.95)  # Parâmetro top_p (0-1)
    top_k = Column(Integer, default=50)  # Parâmetro top_k (1-100)
    max_tokens = Column(Integer, default=2000)  # Limite de tokens
    icone = Column(String(100), nullable=True)  # Ícone Font Awesome
    cor_destaque = Column(String(20), nullable=True)  # Cor em hexadecimal
    
    # NOVOS CAMPOS - Integração Frontend
    tipo = Column(String(50), default='juridico')  # juridico, resumidor, sentimento, extrator, tradutor, classificador, gerador, sintetizador, formatador
    customizado = Column(Boolean, default=False)  # True = criado pelo usuário, False = pré-configurado
    prompt_template = Column(Text, nullable=True)  # Template de prompt personalizado (renomeado de template_prompt)
    configuracoes_llm = Column(JSONB, default={})  # Configurações LLM completas (provider, model, temperatura, parâmetros, etc.)
    total_conversas = Column(Integer, default=0)  # Total de conversas realizadas
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)  # Usuário que criou (para customizados)
    template_prompt = Column(Text, nullable=True)  # DEPRECATED - usar prompt_template
    
    # Configurações de fragmentação de texto
    modo_fragmentacao = Column(String(20), default='geral')  # geral, paragrafo, doc_completo
    identificador_segmento = Column(String(10), default='\\n\\n')  # Delimitador de segmento
    comprimento_max_fragmento = Column(Integer, default=1024)  # Tamanho máximo do fragmento
    sobreposicao_blocos = Column(Integer, default=50)  # Sobreposição entre fragmentos
    comprimento_fragmento_filho = Column(Integer, default=512)  # Para modo doc_completo
    preprocessamento_texto = Column(Boolean, default=True)  # Ativar pré-processamento
    
    # Configurações RAG (Retrieval-Augmented Generation)
    base_vetorial_ativa = Column(Boolean, default=True)  # Habilitar busca em base vetorial
    documentos_contexto = Column(Integer, default=5)  # Quantidade de documentos do RAG
    threshold_relevancia = Column(Float, default=0.82)  # Score mínimo de relevância (0-1) - Alto para precisão
    
    # Capacidades específicas do agente (JSON array com 5 capacidades)
    capacidades = Column(JSON, nullable=True)
    
    # Relacionamentos
    categoria = relationship("CategoriaJuridica", back_populates="agentes")
    avaliacoes = relationship("AvaliacaoAgente", back_populates="agente")
    # Relações para segunda opinião separadas por papel (original ou revisor)
    revisoes_realizadas = relationship("SegundaOpiniao", 
                                      foreign_keys="SegundaOpiniao.agente_revisor_id",
                                      back_populates="agente_revisor")
    # Relacionamento com documentos carregados para especialização
    documentos_carregados = relationship("DocumentoCarregado", back_populates="agente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<AgenteJuridico {self.nome}>'
    
    @property
    def rating_medio(self):
        """Calcula a média das avaliações do agente."""
        if not self.avaliacoes:
            return 0
        return sum(a.rating for a in self.avaliacoes) / len(self.avaliacoes)
    
    @property
    def total_avaliacoes(self):
        """Retorna o número total de avaliações do agente."""
        return len(self.avaliacoes)
    
    def get_detalhes_tecnicos(self):
        """Retorna os detalhes técnicos do agente em formato de dicionário."""
        if not self.detalhes_tecnicos:
            return {
                'provider': 'openai',
                'temperatura': self.temperatura or 0.7,
                'top_p': self.top_p or 0.95,
                'top_k': self.top_k or 50,
                'max_tokens': self.max_tokens or 2000,
                'timeout': 60,
                'retry_attempts': 3,
                'capacidades': [],
                'fontes_conhecimento': []
            }
        try:
            import json
            detalhes = json.loads(self.detalhes_tecnicos)
            # Garantir valores padrão
            detalhes.setdefault('provider', 'openai')
            detalhes.setdefault('temperatura', self.temperatura or 0.7)
            detalhes.setdefault('top_p', self.top_p or 0.95)
            detalhes.setdefault('top_k', self.top_k or 50)
            detalhes.setdefault('max_tokens', self.max_tokens or 2000)
            detalhes.setdefault('timeout', 60)
            detalhes.setdefault('retry_attempts', 3)
            detalhes.setdefault('capacidades', [])
            detalhes.setdefault('fontes_conhecimento', [])
            return detalhes
        except:
            return {
                'provider': 'openai',
                'temperatura': self.temperatura or 0.7,
                'top_p': self.top_p or 0.95,
                'top_k': self.top_k or 50,
                'max_tokens': self.max_tokens or 2000,
                'timeout': 60,
                'retry_attempts': 3,
                'capacidades': [],
                'fontes_conhecimento': []
            }

class AvaliacaoAgente(db.Model):
    """
    Modelo para avaliações de agentes jurídicos pelos usuários.
    """
    __tablename__ = 'avaliacao_agente'
    
    id = Column(Integer, primary_key=True)
    agente_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    documento_id = Column(Integer, nullable=True)  # ID do documento analisado (se aplicável)
    rating = Column(Integer, nullable=False)  # 1-5 estrelas
    comentario = Column(Text, nullable=True)
    data_avaliacao = Column(DateTime, default=datetime.datetime.now)
    
    # Relacionamentos
    agente = relationship("AgenteJuridico", back_populates="avaliacoes")
    usuario = relationship("User", backref="avaliacoes_feitas", overlaps="avaliacoes_recebidas,avaliado_por")
    
    def __repr__(self):
        return f'<AvaliacaoAgente {self.id} - Rating: {self.rating}>'

class SegundaOpiniao(db.Model):
    """
    Modelo para segunda opinião (revisão) feita por um agente revisor.
    """
    __tablename__ = 'segunda_opiniao'
    
    id = Column(Integer, primary_key=True)
    agente_original_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    agente_revisor_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    documento_id = Column(Integer, nullable=True)  # ID do documento analisado
    resultado_original = Column(Text, nullable=False)  # Resultado do agente original
    resultado_revisao = Column(Text, nullable=False)  # Resultado da revisão
    nivel_concordancia = Column(Integer, nullable=True)  # 1-5, onde 5 é concordância total
    pontos_divergentes = Column(Text, nullable=True)  # Pontos em que os agentes discordam
    pontos_complementares = Column(Text, nullable=True)  # Pontos adicionais na revisão
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    
    # Relacionamentos
    agente_original = relationship("AgenteJuridico", foreign_keys=[agente_original_id], backref="analises_revisadas")
    agente_revisor = relationship("AgenteJuridico", foreign_keys=[agente_revisor_id], back_populates="revisoes_realizadas")
    
    def __repr__(self):
        return f'<SegundaOpiniao {self.id}>'

class Conversa(db.Model):
    """
    Modelo para armazenar conversas de chat com assistentes.
    """
    __tablename__ = 'conversa'
    
    id = Column(Integer, primary_key=True)
    assistente_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # Opcional - pode ser anônimo
    titulo = Column(String(200), nullable=False)
    mensagens = Column(JSONB, default=[])  # Array de mensagens {role, content, timestamp}
    provider_usado = Column(String(50), nullable=True)  # openai, anthropic, google
    modelo_usado = Column(String(100), nullable=True)  # gpt-5.2, claude-sonnet-4.5, etc
    arquivos_anexados = Column(JSON, default=[])  # Lista de {nome, url, tipo, tamanho}
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    ativa = Column(Boolean, default=True)
    
    # Relacionamentos
    assistente = relationship("AgenteJuridico", backref="chat_conversas")
    usuario = relationship("User", backref="chat_conversas", foreign_keys=[usuario_id])
    
    # Índices
    __table_args__ = (
        Index('idx_conversa_assistente', 'assistente_id'),
        Index('idx_conversa_usuario', 'usuario_id'),
        Index('idx_conversa_ativa', 'ativa'),
    )
    
    def __repr__(self):
        return f'<Conversa {self.id}: {self.titulo}>'

# Modelo para documentos e suas versões
class Documento(db.Model):
    """
    Modelo para armazenar documentos e suas versões.
    """
    __tablename__ = 'documento'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String(50), nullable=True)  # Tipo de documento (contrato, parecer, etc.)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    tags = Column(String(255), nullable=True)  # Tags separadas por vírgula
    hash_conteudo = Column(String(64), nullable=True)  # Hash SHA-256 do conteúdo para comparação
    
    # Relacionamentos
    usuario = relationship("User", backref="documentos")
    versoes = relationship("VersaoDocumento", back_populates="documento", cascade="all, delete-orphan")
    analises = relationship("AnaliseDocumento", back_populates="documento", cascade="all, delete-orphan")
    entidades = relationship("EntidadeDocumento", back_populates="documento", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Documento {self.id}: {self.titulo}>'
    
    def versao_atual(self):
        """Retorna a versão mais recente do documento."""
        return VersaoDocumento.query.filter_by(documento_id=self.id).order_by(VersaoDocumento.numero_versao.desc()).first()
    
    def total_versoes(self):
        """Retorna o número total de versões do documento."""
        return VersaoDocumento.query.filter_by(documento_id=self.id).count()


class VersaoDocumento(db.Model):
    """
    Modelo para armazenar versões de documentos.
    """
    __tablename__ = 'versao_documento'
    
    id = Column(Integer, primary_key=True)
    documento_id = Column(Integer, ForeignKey('documento.id'), nullable=False)
    numero_versao = Column(Integer, nullable=False)
    conteudo = Column(Text, nullable=False)
    conteudo_html = Column(Text, nullable=True)  # Versão formatada em HTML
    comentario = Column(String(255), nullable=True)  # Comentário sobre a versão
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    hash_conteudo = Column(String(64), nullable=True)  # Hash SHA-256 do conteúdo
    
    # Relacionamentos
    documento = relationship("Documento", back_populates="versoes")
    usuario = relationship("User", backref="versoes_documento")
    
    __table_args__ = (
        UniqueConstraint('documento_id', 'numero_versao', name='uix_versao_documento'),
    )
    
    def __repr__(self):
        return f'<VersaoDocumento {self.id}: Doc {self.documento_id} V{self.numero_versao}>'


class AnaliseDocumento(db.Model):
    """
    Modelo para armazenar análises de documentos realizadas por agentes.
    """
    __tablename__ = 'analise_documento'
    
    id = Column(Integer, primary_key=True)
    documento_id = Column(Integer, ForeignKey('documento.id'), nullable=False)
    versao_id = Column(Integer, ForeignKey('versao_documento.id'), nullable=True)
    agente_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    conteudo_analise = Column(Text, nullable=False)
    conteudo_analise_html = Column(Text, nullable=True)  # Versão formatada em HTML
    data_analise = Column(DateTime, default=datetime.datetime.now)
    metadados = Column(Text, nullable=True)  # JSON com metadados da análise
    
    # Relacionamentos
    documento = relationship("Documento", back_populates="analises")
    versao = relationship("VersaoDocumento", backref="analises")
    agente = relationship("AgenteJuridico", backref="analises")
    comparacoes = relationship("AnaliseComparativa", foreign_keys="[AnaliseComparativa.analise_principal_id]", back_populates="analise_principal")
    
    def __repr__(self):
        return f'<AnaliseDocumento {self.id}: Doc {self.documento_id}>'


class AnaliseComparativa(db.Model):
    """
    Modelo para armazenar comparações entre análises de diferentes agentes.
    """
    __tablename__ = 'analise_comparativa'
    
    id = Column(Integer, primary_key=True)
    analise_principal_id = Column(Integer, ForeignKey('analise_documento.id'), nullable=False)
    analise_comparada_id = Column(Integer, ForeignKey('analise_documento.id'), nullable=False)
    resultado_comparacao = Column(Text, nullable=False)
    resultado_comparacao_html = Column(Text, nullable=True)  # Versão formatada em HTML
    nivel_concordancia = Column(Integer, nullable=True)  # 1-5, onde 5 é concordância total
    pontos_concordantes = Column(Text, nullable=True)  # Pontos em que os agentes concordam
    pontos_divergentes = Column(Text, nullable=True)  # Pontos em que os agentes discordam
    pontos_complementares = Column(Text, nullable=True)  # Pontos adicionais na comparação
    data_comparacao = Column(DateTime, default=datetime.datetime.now)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # Usuário que solicitou a comparação
    
    # Relacionamentos
    analise_principal = relationship("AnaliseDocumento", foreign_keys=[analise_principal_id], back_populates="comparacoes")
    analise_comparada = relationship("AnaliseDocumento", foreign_keys=[analise_comparada_id], backref="comparacoes_como_secundaria")
    usuario = relationship("User", backref="comparacoes_solicitadas")
    
    def __repr__(self):
        return f'<AnaliseComparativa {self.id}: {self.analise_principal_id} vs {self.analise_comparada_id}>'


class EntidadeDocumento(db.Model):
    """
    Modelo para armazenar entidades extraídas de documentos.
    """
    __tablename__ = 'entidade_documento'
    
    id = Column(Integer, primary_key=True)
    documento_id = Column(Integer, ForeignKey('documento.id'), nullable=False)
    versao_id = Column(Integer, ForeignKey('versao_documento.id'), nullable=True)
    tipo_entidade = Column(String(50), nullable=False)  # Pessoa, organização, local, data, valor, etc.
    nome_entidade = Column(String(200), nullable=False)
    contexto = Column(Text, nullable=True)  # Texto onde a entidade foi encontrada
    metadados = Column(Text, nullable=True)  # JSON com metadados da entidade
    data_extracao = Column(DateTime, default=datetime.datetime.now)
    
    # Relacionamentos
    documento = relationship("Documento", back_populates="entidades")
    versao = relationship("VersaoDocumento", backref="entidades")
    
    def __repr__(self):
        return f'<EntidadeDocumento {self.id}: {self.tipo_entidade} - {self.nome_entidade}>'


class CacheRespostaAPI(db.Model):
    """
    Modelo para armazenar em cache respostas de APIs.
    """
    __tablename__ = 'cache_resposta_api'
    
    id = Column(Integer, primary_key=True)
    provedor = Column(String(50), nullable=False)  # openai, anthropic, google, etc.
    modelo = Column(String(50), nullable=False)  # gpt-4, claude-3, gemini, etc.
    hash_prompt = Column(String(64), nullable=False)  # Hash SHA-256 do prompt
    prompt = Column(Text, nullable=False)  # Prompt original
    resposta = Column(Text, nullable=False)  # Resposta da API
    parametros = Column(Text, nullable=True)  # JSON com parâmetros da chamada
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_expiracao = Column(DateTime, nullable=True)  # Data em que o cache expira
    contador_uso = Column(Integer, default=0)  # Contador de uso do cache
    
    def __repr__(self):
        return f'<CacheRespostaAPI {self.id}: {self.provedor}/{self.modelo}>'
    
    # Índice para melhorar a performance da busca
    __table_args__ = (
        Index('idx_cache_resposta_api_hash', 'hash_prompt', 'provedor', 'modelo'),
    )


# Modelo para categorias de templates
class CategoriaTemplate(db.Model):
    """
    Modelo para armazenar categorias de templates.
    """
    __tablename__ = 'categoria_template'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    icone = Column(String(50), nullable=True)  # Ícone Font Awesome
    cor = Column(String(20), nullable=True)  # Cor em hexadecimal
    ordem = Column(Integer, default=1)
    ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_modificacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<CategoriaTemplate {self.nome}>'

# Extensão das classes existentes (removida para evitar warnings de overlapping)

class SystemConfig(db.Model):
    """
    Modelo para armazenar configurações globais do sistema.
    """
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    
    # Configurações do Sistema Principal
    system_name = Column(String(200), default='Sistema Jurídico de Transcrição IA')
    debug_mode = Column(Boolean, default=False)
    log_level = Column(String(20), default='INFO')
    max_agents = Column(Integer, default=10)
    
    # Configurações de Transcrição IA
    assemblyai_enabled = Column(Boolean, default=True)
    whisper_enabled = Column(Boolean, default=True)
    speaker_detection = Column(Boolean, default=True)
    auto_summary = Column(Boolean, default=True)
    
    # Configurações de APIs
    openai_model = Column(String(50), default='gpt-4o')
    anthropic_model = Column(String(50), default='claude-3-5-sonnet-20241022')
    temperature = Column(Float, default=0.3)
    max_tokens = Column(Integer, default=4000)
    
    # Configurações de Segurança
    session_timeout = Column(Integer, default=120)
    max_login_attempts = Column(Integer, default=5)
    lockout_duration = Column(Integer, default=15)
    
    # Configurações de Monitoramento
    enable_monitoring = Column(Boolean, default=True)
    enable_cost_tracking = Column(Boolean, default=True)
    cost_alert_threshold = Column(Float, default=100.0)
    token_limit_daily = Column(Integer, default=100000)
    
    # Configurações de Exportação
    enable_pdf_export = Column(Boolean, default=True)
    enable_docx_export = Column(Boolean, default=True)
    default_font_size = Column(Integer, default=12)
    
    # Metadados
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relacionamentos
    updated_by_user = relationship("User", foreign_keys=[updated_by], backref="config_updates")
    
    def __repr__(self):
        return f'<SystemConfig {self.id}: {self.system_name}>'


class TemaPagina(db.Model):
    """
    Modelo para armazenar configurações de tema e cores para cada página do sistema.
    """
    __tablename__ = 'tema_pagina'
    
    id = Column(Integer, primary_key=True)
    rota = Column(String(100), nullable=False, unique=True)  # Rota da página (ex: '/historico')
    descricao = Column(String(255), nullable=True)  # Descrição amigável da página
    
    # Cores e estilos salvos em formato JSON
    cores = Column(Text, nullable=False, default='{}')
    
    # Usuário que fez a última modificação
    modificado_por = Column(Integer, ForeignKey('user.id'), nullable=True)
    modificado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Indicador se o tema está ativo
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    usuario = relationship("User", foreign_keys=[modificado_por], backref="temas_modificados")
    
    def get_cores(self):
        """
        Retorna as cores em formato de dicionário.
        """
        if not self.cores:
            return {}
        try:
            return json.loads(self.cores)
        except:
            return {}
    
    def set_cores(self, cores_dict):
        """
        Atualiza as cores a partir de um dicionário.
        
        Args:
            cores_dict: Dicionário com as cores e estilos
        """
        self.cores = json.dumps(cores_dict)
    
    def to_dict(self):
        """
        Converte o objeto para dicionário para serialização JSON.
        """
        return {
            'id': self.id,
            'rota': self.rota,
            'descricao': self.descricao,
            'cores': self.get_cores(),
            'ativo': self.ativo,
            'modificado_por': self.modificado_por,
            'modificado_em': self.modificado_em.isoformat() if self.modificado_em else None
        }
    
    def __repr__(self):
        return f'<TemaPagina {self.rota}>'

# Modelo para arquivos de audio para transcricao
class ArquivoTranscricao(db.Model):
    """
    Modelo para armazenar os arquivos de áudio enviados para transcrição.
    Mantém uma relação com o modelo de Transcricao.
    """
    __tablename__ = 'arquivo_transcricao'
    
    id = Column(String(36), primary_key=True)  # UUID como string
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_upload = Column(DateTime, default=datetime.datetime.now)
    
    # Informações do arquivo
    arquivo_nome = Column(String(255), nullable=False)  # Nome original do arquivo
    arquivo_path = Column(String(500), nullable=False)  # Caminho do arquivo no sistema
    arquivo_tipo = Column(String(100), nullable=False)  # Tipo MIME do arquivo (audio/mp3, audio/wav, etc)
    arquivo_tamanho = Column(Integer, nullable=False)  # Tamanho em bytes
    hash_arquivo = Column(String(64), nullable=True)  # Hash SHA-256 para verificação de integridade
    
    # Metadados extraídos do arquivo
    duracao = Column(Integer, nullable=True)  # Duração em segundos
    taxa_amostragem = Column(Integer, nullable=True)  # Sample rate (Hz)
    bitrate = Column(Integer, nullable=True)  # Bitrate (kbps)
    canais = Column(Integer, nullable=True)  # Número de canais (1=mono, 2=stereo)
    metadados = Column(Text, nullable=True)  # Outros metadados em formato JSON
    
    # Status e controle
    status = Column(String(30), default='pendente')  # pendente, em_processamento, processado, erro
    status_mensagem = Column(String(255), nullable=True)  # Mensagem de erro ou informação adicional
    
    # Configurações para processamento
    prioridade = Column(Integer, default=0)  # Prioridade de processamento (maior = mais prioritário)
    configuracoes = Column(Text, nullable=True)  # Configurações para processamento em formato JSON
    
    # Relações
    usuario = relationship("User", backref="arquivos_transcricao")
    transcricoes = relationship("Transcricao", backref="arquivo", cascade="all, delete-orphan")
    
    def get_metadados(self):
        """Retorna os metadados como dicionário."""
        if not self.metadados:
            return {}
        try:
            return json.loads(self.metadados)
        except:
            return {}
    
    def set_metadados(self, metadados_dict):
        """Define os metadados a partir de um dicionário."""
        self.metadados = json.dumps(metadados_dict)
    
    def get_configuracoes(self):
        """Retorna as configurações como dicionário."""
        if not self.configuracoes:
            return {}
        try:
            return json.loads(self.configuracoes)
        except:
            return {}
    
    def set_configuracoes(self, config_dict):
        """Define as configurações a partir de um dicionário."""
        self.configuracoes = json.dumps(config_dict)
        
    def to_dict(self):
        """
        Converte o objeto para um dicionário para uso em APIs.
        
        Returns:
            dict: Dicionário com os dados do arquivo
        """
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'arquivo_nome': self.arquivo_nome,
            'arquivo_tipo': self.arquivo_tipo,
            'arquivo_tamanho': self.arquivo_tamanho,
            'duracao': self.duracao,
            'taxa_amostragem': self.taxa_amostragem,
            'bitrate': self.bitrate,
            'canais': self.canais,
            'status': self.status,
            'status_mensagem': self.status_mensagem,
            'prioridade': self.prioridade,
            'metadados': self.get_metadados(),
            'configuracoes': self.get_configuracoes(),
            'transcricoes_count': len(self.transcricoes) if self.transcricoes else 0
        }
        
    def __repr__(self):
        return f'<ArquivoTranscricao {self.id}: {self.arquivo_nome}>'

# Modelo para Resultados de Análise Multi-Agente
class ResultadoAnaliseMultiAgente(db.Model):
    """
    Modelo para armazenar resultados de análise multi-agente de documentos jurídicos.
    """
    __tablename__ = 'resultado_analise_multiagente'
    
    # Identificação única
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informações do usuário e data
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Documento analisado
    documento_original = Column(Text, nullable=False)  # Texto integral do documento
    documento_nome = Column(String(255), nullable=True)  # Nome do arquivo original
    tipo_analise = Column(String(50), default='multiplos_agentes')  # Tipo de análise realizada
    
    # Resultados da análise
    resultado_principal = Column(JSON, nullable=True)  # Resultado principal consolidado
    resultados_agentes = Column(JSON, nullable=True)  # Array com resultados de cada agente
    agentes_utilizados = Column(JSON, nullable=True)  # Lista dos agentes que processaram
    
    # Metadados
    tempo_processamento = Column(Integer, nullable=True)  # Tempo total em segundos
    status = Column(String(30), default='concluido')  # concluido, processando, erro
    provider_principal = Column(String(50), nullable=True)  # API principal utilizada
    
    # Relações
    usuario = relationship("User", backref="analises_multiagente")
    
    def to_dict(self):
        """Converte o resultado para dicionário."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'documento_original': self.documento_original,
            'tipo_analise': self.tipo_analise,
            'resultado_principal': self.resultado_principal,
            'resultados_agentes': self.resultados_agentes,
            'agentes_utilizados': self.agentes_utilizados,
            'tempo_processamento': self.tempo_processamento,
            'status': self.status,
            'provider_principal': self.provider_principal
        }
    
    def __repr__(self):
        return f'<ResultadoAnaliseMultiAgente {self.id[:8]}...>'

# Modelo para Validação Multi-Agente
class ValidacaoMultiAgente(db.Model):
    """
    Modelo para armazenar resultados de validação multi-agente de documentos jurídicos.
    """
    __tablename__ = 'validacao_multi_agente'
    
    # Identificação única
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_validacao = Column(String(20), unique=True, nullable=False)  # Código único visível ao usuário
    
    # Informações do usuário e data
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Documento analisado
    documento_original = Column(Text, nullable=False)  # Texto integral do documento
    documento_nome = Column(String(255), nullable=True)  # Nome do arquivo original
    documento_tipo = Column(String(100), nullable=True)  # Tipo de documento (contrato, petição, etc.)
    
    # Metadados da validação
    agentes_utilizados = Column(JSON, nullable=False)  # Lista com informações dos agentes
    total_agentes = Column(Integer, nullable=False)  # Número de agentes utilizados
    areas_juridicas = Column(JSON, nullable=False)  # Áreas jurídicas analisadas
    
    # Status do processamento
    status = Column(String(30), default='processando')  # processando, concluido, erro
    status_mensagem = Column(String(500), nullable=True)
    tempo_processamento = Column(Integer, nullable=True)  # Tempo em segundos
    
    # Opinião consolidada
    opiniao_consolidada = Column(Text, nullable=True)  # Síntese das análises
    pontos_criticos = Column(JSON, nullable=True)  # Pontos críticos identificados
    recomendacoes_gerais = Column(Text, nullable=True)  # Recomendações consolidadas
    
    # Configurações utilizadas
    configuracoes = Column(JSON, nullable=True)  # Configurações da validação
    
    # Relacionamentos
    usuario = relationship("User", backref="validacoes_multi_agente")
    analises_individuais = relationship("AnaliseIndividualAgente", backref="validacao", cascade="all, delete-orphan")
    
    def gerar_codigo_validacao(self):
        """Gera um código único para a validação (formato: VAL-YYYYMMDD-XXXX)"""
        from datetime import datetime
        import random
        import string
        
        hoje = datetime.now().strftime('%Y%m%d')
        sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"VAL-{hoje}-{sufixo}"
    
    def to_dict(self):
        """Converte para dicionário para APIs"""
        return {
            'id': self.id,
            'codigo_validacao': self.codigo_validacao,
            'usuario_id': self.usuario_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'documento_nome': self.documento_nome,
            'documento_tipo': self.documento_tipo,
            'agentes_utilizados': self.agentes_utilizados,
            'total_agentes': self.total_agentes,
            'areas_juridicas': self.areas_juridicas,
            'status': self.status,
            'tempo_processamento': self.tempo_processamento,
            'analises_count': len(self.analises_individuais) if self.analises_individuais else 0
        }
    
    def __repr__(self):
        return f'<ValidacaoMultiAgente {self.codigo_validacao}>'

# Modelo para Análises Individuais dos Agentes
class AnaliseIndividualAgente(db.Model):
    """
    Modelo para armazenar a análise individual de cada agente especialista.
    """
    __tablename__ = 'analise_individual_agente'
    
    # Identificação
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    validacao_id = Column(String(36), ForeignKey('validacao_multi_agente.id'), nullable=False)
    
    # Informações do agente
    agente_id = Column(Integer, nullable=False)  # ID do agente no sistema
    agente_nome = Column(String(255), nullable=False)
    agente_especialidade = Column(String(255), nullable=False)
    agente_nivel_experiencia = Column(String(50), nullable=False)  # junior, pleno, senior, especialista
    
    # Análise realizada
    opiniao_juridica = Column(Text, nullable=False)  # Opinião detalhada do agente
    fundamentacao_legal = Column(Text, nullable=True)  # Base legal utilizada
    jurisprudencia_citada = Column(JSON, nullable=True)  # Jurisprudências mencionadas
    doutrina_citada = Column(JSON, nullable=True)  # Doutrinas mencionadas
    legislacao_aplicavel = Column(JSON, nullable=True)  # Legislação aplicável
    
    # Avaliação e recomendações
    pontos_positivos = Column(JSON, nullable=True)  # Aspectos positivos identificados
    pontos_negativos = Column(JSON, nullable=True)  # Problemas identificados
    riscos_identificados = Column(JSON, nullable=True)  # Riscos jurídicos
    recomendacoes = Column(Text, nullable=True)  # Recomendações específicas
    
    # Classificação da análise
    nivel_confianca = Column(Float, nullable=True)  # Nível de confiança (0.0 a 1.0)
    complexidade_documento = Column(String(20), nullable=True)  # baixa, media, alta
    urgencia_recomendada = Column(String(20), nullable=True)  # baixa, media, alta, critica
    
    # Metadados técnicos
    data_analise = Column(DateTime, default=datetime.datetime.now)
    tempo_processamento = Column(Integer, nullable=True)  # Tempo em segundos
    modelo_ia_utilizado = Column(String(100), nullable=True)  # Modelo de IA usado
    tokens_utilizados = Column(Integer, nullable=True)  # Tokens consumidos
    
    # Base de conhecimento utilizada
    embeddings_consultados = Column(Integer, nullable=True)  # Número de embeddings consultados
    documentos_referencia = Column(JSON, nullable=True)  # Documentos da base consultados
    
    def to_dict(self):
        """Converte para dicionário para APIs"""
        return {
            'id': self.id,
            'agente_nome': self.agente_nome,
            'agente_especialidade': self.agente_especialidade,
            'agente_nivel_experiencia': self.agente_nivel_experiencia,
            'opiniao_juridica': self.opiniao_juridica,
            'fundamentacao_legal': self.fundamentacao_legal,
            'jurisprudencia_citada': self.jurisprudencia_citada,
            'doutrina_citada': self.doutrina_citada,
            'legislacao_aplicavel': self.legislacao_aplicavel,
            'pontos_positivos': self.pontos_positivos,
            'pontos_negativos': self.pontos_negativos,
            'riscos_identificados': self.riscos_identificados,
            'recomendacoes': self.recomendacoes,
            'nivel_confianca': self.nivel_confianca,
            'complexidade_documento': self.complexidade_documento,
            'urgencia_recomendada': self.urgencia_recomendada,
            'data_analise': self.data_analise.isoformat() if self.data_analise else None,
            'modelo_ia_utilizado': self.modelo_ia_utilizado,
            'tokens_utilizados': self.tokens_utilizados
        }
    
    def __repr__(self):
        return f'<AnaliseIndividualAgente {self.agente_nome} - {self.validacao_id}>'

# Modelo para Análises de Agente Especializado Individual
class AnaliseEspecialistaIndividual(db.Model):
    """
    Modelo para armazenar análises de agente especializado individual (não multi-agente).
    """
    __tablename__ = 'analise_especialista_individual'
    
    # Identificação única
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_analise = Column(String(20), unique=True, nullable=False)  # Código único visível ao usuário
    
    # Informações do usuário e data
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Documento analisado
    documento_original = Column(Text, nullable=False)  # Texto integral do documento
    documento_nome = Column(String(255), nullable=True)  # Nome do arquivo original
    documento_tipo = Column(String(100), nullable=True)  # Tipo de documento
    
    # Informações do agente especialista
    agente_id = Column(Integer, nullable=False)  # ID do agente no sistema
    agente_nome = Column(String(255), nullable=False)
    agente_especialidade = Column(String(255), nullable=False)
    agente_nivel_experiencia = Column(String(50), nullable=False)  # junior, pleno, senior, especialista
    area_juridica = Column(String(255), nullable=False)  # Área jurídica principal
    
    # Análise realizada
    opiniao_juridica = Column(Text, nullable=False)  # Opinião detalhada do agente
    fundamentacao_legal = Column(Text, nullable=True)  # Base legal utilizada
    jurisprudencia_citada = Column(JSON, nullable=True)  # Jurisprudências mencionadas
    doutrina_citada = Column(JSON, nullable=True)  # Doutrinas mencionadas
    legislacao_aplicavel = Column(JSON, nullable=True)  # Legislação aplicável
    
    # Avaliação e recomendações
    pontos_positivos = Column(JSON, nullable=True)  # Aspectos positivos identificados
    pontos_negativos = Column(JSON, nullable=True)  # Problemas identificados
    riscos_identificados = Column(JSON, nullable=True)  # Riscos jurídicos
    recomendacoes = Column(Text, nullable=True)  # Recomendações específicas
    conclusao_geral = Column(Text, nullable=True)  # Conclusão da análise
    
    # Classificação da análise
    nivel_confianca = Column(Float, nullable=True)  # Nível de confiança (0.0 a 1.0)
    complexidade_documento = Column(String(20), nullable=True)  # baixa, media, alta
    urgencia_recomendada = Column(String(20), nullable=True)  # baixa, media, alta, critica
    
    # Status do processamento
    status = Column(String(30), default='concluido')  # processando, concluido, erro
    tempo_processamento = Column(Integer, nullable=True)  # Tempo em segundos
    
    # Metadados técnicos
    modelo_ia_utilizado = Column(String(100), nullable=True)  # Modelo de IA usado
    tokens_utilizados = Column(Integer, nullable=True)  # Tokens consumidos
    embeddings_consultados = Column(Integer, nullable=True)  # Número de embeddings consultados
    documentos_referencia = Column(JSON, nullable=True)  # Documentos da base consultados
    
    # Relacionamento
    usuario = relationship("User", backref="analises_especialista_individual")
    
    def gerar_codigo_analise(self):
        """Gera um código único para a análise (formato: ANA-YYYYMMDD-XXXX)"""
        from datetime import datetime
        import random
        import string
        
        hoje = datetime.now().strftime('%Y%m%d')
        sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ANA-{hoje}-{sufixo}"
    
    def to_dict(self):
        """Converte para dicionário para APIs"""
        return {
            'id': self.id,
            'codigo_analise': self.codigo_analise,
            'usuario_id': self.usuario_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'documento_nome': self.documento_nome,
            'documento_tipo': self.documento_tipo,
            'agente_nome': self.agente_nome,
            'agente_especialidade': self.agente_especialidade,
            'area_juridica': self.area_juridica,
            'opiniao_juridica': self.opiniao_juridica,
            'nivel_confianca': self.nivel_confianca,
            'complexidade_documento': self.complexidade_documento,
            'status': self.status,
            'modelo_ia_utilizado': self.modelo_ia_utilizado
        }
    
    def __repr__(self):
        return f'<AnaliseEspecialistaIndividual {self.codigo_analise}>'

# Modelo para Transcrições
class Transcricao(db.Model):
    """
    Modelo para armazenar transcrições de áudio realizadas no sistema.
    """
    __tablename__ = 'transcricao'
    
    id = Column(String(36), primary_key=True)  # UUID como string
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    arquivo_id = Column(String(36), ForeignKey('arquivo_transcricao.id'), nullable=True)  # Referência ao arquivo original
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Informações do arquivo (mantidas por compatibilidade com código existente)
    arquivo_nome = Column(String(255), nullable=False)
    arquivo_caminho = Column(String(500), nullable=True)  # Pode ser nulo para arquivos temporários
    arquivo_tamanho = Column(Integer, nullable=True)  # Tamanho em bytes
    arquivo_duracao = Column(Integer, nullable=True)  # Duração em segundos
    
    # Informações de processamento
    status = Column(String(20), default='pendente')  # pendente, processando, concluido, erro, cancelado
    provedor = Column(String(50), nullable=True)  # openai, google, anthropic
    modelo = Column(String(50), nullable=True)  # whisper, cloud-speech, etc
    
    # Conteúdo da transcrição
    texto = Column(Text, nullable=True)
    
    # Metadados e resultados adicionais (JSON)
    metadados = Column(Text, nullable=True)  # Configurações, parâmetros
    resultado_json = Column(Text, nullable=True)  # Resultado completo como JSON
    
    # Análises
    sentimento = Column(String(20), nullable=True)  # positivo, neutro, negativo
    score_sentimento = Column(db.Float, nullable=True)  # -1.0 a 1.0
    
    # Relações
    usuario = relationship("User", backref="transcricoes")
    
    def get_metadados(self):
        """Retorna os metadados como dicionário."""
        if not self.metadados:
            return {}
        try:
            return json.loads(self.metadados)
        except:
            return {}
    
    def set_metadados(self, metadados_dict):
        """Define os metadados a partir de um dicionário."""
        self.metadados = json.dumps(metadados_dict)
    
    def get_resultado(self):
        """Retorna o resultado completo como dicionário."""
        if not self.resultado_json:
            return {}
        try:
            return json.loads(self.resultado_json)
        except:
            return {}
    
    def set_resultado(self, resultado_dict):
        """Define o resultado a partir de um dicionário."""
        self.resultado_json = json.dumps(resultado_dict)
    
    def to_dict(self, resumido=False):
        """
        Converte o objeto para um dicionário.
        
        Args:
            resumido: Se True, retorna uma versão resumida do texto para listas
        
        Returns:
            dict: Dicionário com os dados da transcrição
        """
        if resumido:
            return {
                'id': self.id,
                'usuario_id': self.usuario_id,
                'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
                'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
                'arquivo_nome': self.arquivo_nome,
                'arquivo_tamanho': self.arquivo_tamanho,
                'arquivo_duracao': self.arquivo_duracao,
                'status': self.status,
                'provedor': self.provedor,
                'modelo': self.modelo,
                'texto': self.texto[:200] + '...' if self.texto and len(self.texto) > 200 else self.texto,
                'sentimento': self.sentimento,
                'score_sentimento': self.score_sentimento
            }
        else:
            return {
                'id': self.id,
                'usuario_id': self.usuario_id,
                'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
                'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
                'arquivo_nome': self.arquivo_nome,
                'arquivo_caminho': self.arquivo_caminho,
                'arquivo_tamanho': self.arquivo_tamanho,
                'arquivo_duracao': self.arquivo_duracao,
                'status': self.status,
                'provedor': self.provedor,
                'modelo': self.modelo,
                'texto': self.texto,
                'sentimento': self.sentimento,
                'score_sentimento': self.score_sentimento,
                'metadados': self.get_metadados(),
                'resultado': self.get_resultado()
            }
    
    def __repr__(self):
        return f'<Transcricao {self.id}: {self.status}>'

class TemplateJuridico(db.Model):
    """Modelo completo para templates jurídicos."""
    __tablename__ = 'template_juridico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    
    # Campos originais mantidos para compatibilidade
    modulo_origem = db.Column(db.String(50))
    campos = db.Column(db.JSON)
    modelo_texto = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    data_modificacao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Novos campos para o módulo completo
    tipo_documento = db.Column(db.String(100))  # petição, contrato, parecer, etc.
    area_juridica = db.Column(db.String(100))   # penal, civil, trabalhista, etc.
    
    # Estrutura do template
    campos_obrigatorios = db.Column(db.JSON)     # campos que devem ser preenchidos
    campos_opcionais = db.Column(db.JSON)        # campos opcionais
    template_conteudo = db.Column(db.Text)       # template base do documento
    formatacao = db.Column(db.JSON)              # configurações de formatação
    
    # Metadados
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria_template.id'))
    nivel_complexidade = db.Column(db.String(20), default='intermediario')  # basico, intermediario, avancado
    tempo_estimado = db.Column(db.Integer, default=15)  # minutos para preenchimento
    
    # Status e controle
    ativo = db.Column(db.Boolean, default=True)
    versao = db.Column(db.String(10), default='1.0')
    aprovado = db.Column(db.Boolean, default=False)
    
    # Auditoria
    criado_por = db.Column(db.Integer, db.ForeignKey('user.id'))
    criado_em = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modificado_em = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Estatísticas de uso
    total_utilizacoes = db.Column(db.Integer, default=0)
    ultima_utilizacao = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<TemplateJuridico {self.id}: {self.nome}>'
    
    def incrementar_uso(self):
        """Incrementa contador de uso do template"""
        if not hasattr(self, 'total_utilizacoes'):
            return
        self.total_utilizacoes = getattr(self, 'total_utilizacoes', 0) + 1
        self.ultima_utilizacao = datetime.datetime.utcnow()
        db.session.commit()


class HistoricoTemplate(db.Model):
    """Histórico de uso de templates jurídicos"""
    __tablename__ = 'historico_template'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template_juridico.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Dados do documento gerado
    campos_preenchidos = db.Column(db.JSON)
    documento_gerado = db.Column(db.Text)
    formato_saida = db.Column(db.String(10), default='docx')
    
    # Metadados
    gerado_em = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ip_usuario = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    # Relacionamentos
    template = db.relationship('TemplateJuridico', backref='historico_uso')
    usuario = db.relationship('User', backref='templates_utilizados')
    
    def __repr__(self):
        return f'<HistoricoTemplate {self.template_id} - {self.usuario_id}>'

# Modelos para Upload de Documentos e Especialização de Agentes

class DocumentoCarregado(db.Model):
    """
    Modelo para documentos carregados pelos usuários para especialização de agentes.
    """
    __tablename__ = 'documento_carregado'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Informações do arquivo
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True)  # MD5 hash para evitar duplicatas
    file_size = Column(Integer, nullable=True)  # Tamanho em bytes
    file_type = Column(String(50), nullable=True)  # pdf, docx, txt, etc
    
    # Descrição e metadados
    description = Column(Text, nullable=True)
    
    # Informações de processamento
    processing_type = Column(String(20), default='vectorial')  # vectorial, relational
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, error
    processing_message = Column(Text, nullable=True)
    chunks_count = Column(Integer, default=0)
    embeddings_count = Column(Integer, default=0)
    questions_generated = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relacionamentos
    agente = relationship('AgenteJuridico', back_populates='documentos_carregados')
    usuario = relationship('User', backref='documentos_carregados')
    chunks = relationship('ChunkDocumento', back_populates='documento', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o documento para dicionário."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'filename': self.filename,
            'description': self.description,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'processing_type': self.processing_type,
            'processing_status': self.processing_status,
            'chunks_count': self.chunks_count,
            'embeddings_count': self.embeddings_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self):
        return f'<DocumentoCarregado {self.id}: {self.filename} - Agente {self.agent_id}>'

class ChunkDocumento(db.Model):
    """
    Modelo para chunks semânticos extraídos dos documentos carregados.
    """
    __tablename__ = 'chunk_documento'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documento_carregado.id'), nullable=False)
    
    # Identificação do chunk
    chunk_id = Column(String(50), nullable=False)  # chunk_0001, chunk_0002, etc
    chunk_index = Column(Integer, nullable=False, default=0)
    
    # Estrutura detectada
    titulo = Column(String(200), nullable=True)
    subtitulo = Column(String(200), nullable=True)
    referencia = Column(String(100), nullable=True)  # Art. 123, § 2º, etc
    
    # Conteúdo
    conteudo = Column(Text, nullable=False)
    conteudo_simplificado = Column(Text, nullable=True)  # Versão simplificada se gerada
    palavras = Column(Integer, nullable=False, default=0)
    
    # Scoring e metadados
    relevance_score = Column(Integer, default=1)  # 1-5
    densidade_juridica = Column(Float, nullable=True)  # Percentual de termos jurídicos
    
    # Embedding (será armazenado na tabela vetorial específica)
    embedding_stored = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamentos
    documento = relationship('DocumentoCarregado', back_populates='chunks')
    perguntas = relationship('PerguntaChunk', back_populates='chunk', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o chunk para dicionário."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_id': self.chunk_id,
            'titulo': self.titulo,
            'subtitulo': self.subtitulo,
            'referencia': self.referencia,
            'conteudo': self.conteudo[:500] + '...' if len(self.conteudo) > 500 else self.conteudo,
            'palavras': self.palavras,
            'relevance_score': self.relevance_score,
            'embedding_stored': self.embedding_stored,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChunkDocumento {self.chunk_id}: {self.palavras} palavras>'

class PerguntaChunk(db.Model):
    """
    Modelo para perguntas geradas automaticamente a partir dos chunks.
    """
    __tablename__ = 'pergunta_chunk'
    
    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey('chunk_documento.id'), nullable=False)
    
    # Identificação da pergunta
    question_id = Column(String(50), nullable=False)  # q_0_0, q_0_1, etc
    group_index = Column(Integer, nullable=False, default=0)  # Grupo de 10 chunks
    
    # Conteúdo da pergunta
    nivel = Column(String(20), nullable=False)  # básica, intermediária, avançada, especializada
    pergunta = Column(Text, nullable=False)
    contexto = Column(Text, nullable=True)  # Contexto/trecho usado para gerar a pergunta
    
    # Metadados
    generated_by = Column(String(50), default='openai')  # Qual modelo gerou
    confidence_score = Column(Float, nullable=True)  # Score de confiança se disponível
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamentos
    chunk = relationship('ChunkDocumento', back_populates='perguntas')
    
    def to_dict(self):
        """Converte a pergunta para dicionário."""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'nivel': self.nivel,
            'pergunta': self.pergunta,
            'contexto': self.contexto,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PerguntaChunk {self.question_id}: {self.nivel}>'

class LogProcessamentoDocumento(db.Model):
    """
    Modelo para logs de processamento de documentos.
    """
    __tablename__ = 'log_processamento_documento'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documento_carregado.id'), nullable=True)
    
    # Informações do log
    nivel = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    mensagem = Column(Text, nullable=False)
    detalhes = Column(Text, nullable=True)  # JSON com detalhes técnicos
    
    # Contexto
    fase_processamento = Column(String(50), nullable=True)  # extraction, chunking, embedding, etc
    tempo_processamento = Column(Float, nullable=True)  # Tempo em segundos
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamentos
    documento = relationship('DocumentoCarregado', backref='logs_processamento')
    
    def __repr__(self):
        return f'<LogProcessamento {self.nivel}: {self.mensagem[:50]}>'

class ArquivoRelacional(db.Model):
    """
    Modelo para arquivos salvos apenas no banco relacional (sem processamento vetorial).
    """
    __tablename__ = 'arquivo_relacional'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)  # caminho no sistema de arquivos
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento com usuário
    user = relationship("User")
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category': self.category,
            'description': self.description,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processing_type': 'relational'
        }
    
    def __repr__(self):
        return f'<ArquivoRelacional {self.id}: {self.filename}>'

# Modelo para Análises Jurídicas Multi-Agente
class AnaliseJuridica(db.Model):
    """
    Modelo para armazenar análises jurídicas multi-agente com numeração única
    """
    __tablename__ = 'analise_juridica'
    
    # Identificação única
    id = Column(Integer, primary_key=True)
    numero_registro = Column(String(50), unique=True, nullable=False)  # Número único de registro
    
    # Informações do usuário e data
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Documento analisado
    texto_original = Column(Text, nullable=False)  # Texto original para análise
    
    # Resultados da análise multi-agente
    resultados_json = Column(Text, nullable=False)  # JSON com resultados de todos os agentes
    total_agentes = Column(Integer, nullable=False)  # Número de agentes utilizados
    
    # Status e metadados
    status = Column(String(20), default='em_andamento')  # em_andamento, concluida, erro
    
    # Relacionamentos
    usuario = relationship('User', backref='analises_juridicas')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numero_registro': self.numero_registro,
            'usuario_id': self.usuario_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'texto_original': self.texto_original,
            'total_agentes': self.total_agentes,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<AnaliseJuridica {self.numero_registro}>'


        
# Atualizar relacionamento no modelo AgenteJuridico
# (Será necessário adicionar esta linha na classe AgenteJuridico se ainda não existir)
# documentos_carregados = relationship('DocumentoCarregado', back_populates='agente', cascade='all, delete-orphan')

# Modelo para Comparação de Documentos
class ComparacaoDocumento(db.Model):
    """
    Modelo para armazenar comparações de versões de documentos jurídicos
    """
    __tablename__ = 'comparacao_documento'
    
    # Identificação única
    id = Column(String(36), primary_key=True)  # UUID como string
    titulo = Column(String(200), nullable=False)
    area_processo = Column(String(100), nullable=False)  # Nome da área jurídica
    descricao_area = Column(String(100), nullable=True)  # Nome da área
    documento_cliente = Column(String(20), nullable=True)  # CPF/CNPJ limpo
    
    # Informações do usuário e data
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    data_comparacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Resultados da comparação (HTML com marcações)
    resultado_html_lado_a = Column(Text, nullable=False)  # Documento original com marcações
    resultado_html_lado_b = Column(Text, nullable=False)  # Documento modificado com marcações
    
    # Resultados editados (podem ser modificados pelo usuário)
    resultado_editado_a = Column(Text, nullable=True)  # Versão editada do lado A
    resultado_editado_b = Column(Text, nullable=True)  # Versão editada do lado B
    
    # Metadados da comparação
    total_diferencas = Column(Integer, default=0)
    total_adicoes = Column(Integer, default=0)
    total_remocoes = Column(Integer, default=0)
    percentual_similaridade = Column(Float, nullable=True)
    
    # Configurações de exportação
    formato_exportacao = Column(String(10), default='docx')  # docx, pdf, html
    incluir_marcacoes = Column(Boolean, default=True)
    
    # Status
    status = Column(String(20), default='concluida')  # em_andamento, concluida, erro
    status_mensagem = Column(Text, nullable=True)
    
    # Análise de IA (novo campo)
    analise_ia = Column(Text, nullable=True)  # JSON com resultados da análise de IA
    
    # Relacionamentos
    user = relationship('User', backref='comparacoes_documentos')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'area_processo': self.area_processo,
            'descricao_area': self.descricao_area,
            'documento_cliente': self.documento_cliente,
            'user_id': self.user_id,
            'data_comparacao': self.data_comparacao.isoformat() if self.data_comparacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'total_diferencas': self.total_diferencas,
            'total_adicoes': self.total_adicoes,
            'total_remocoes': self.total_remocoes,
            'percentual_similaridade': self.percentual_similaridade,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<ComparacaoDocumento {self.id}: {self.titulo}>'

# Modelo para Validação Multi-Agente Expandida
class ValidacaoMultiAgenteAnalise(db.Model):
    """
    Modelo para armazenar análises da validação multi-agente expandida
    com identificadores únicos triplos (ID, UUID, SHA-256)
    """
    __tablename__ = 'validacao_multi_agente_analise'
    
    # Identificadores únicos triplos
    id = Column(Integer, primary_key=True, autoincrement=True)  # ID sequencial
    uuid_analise = Column(String(36), unique=True, nullable=False)  # UUID único
    hash_sha256 = Column(String(64), unique=True, nullable=False)  # Hash SHA-256
    numero_registro = Column(String(20), unique=True, nullable=False)  # Número de registro único
    
    # Informações básicas
    titulo_analise = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Dados do documento analisado
    documento_original = Column(Text, nullable=False)  # Texto do documento
    documento_nome = Column(String(255), nullable=True)  # Nome do arquivo
    documento_tipo = Column(String(50), nullable=True)  # Tipo/extensão
    documento_tamanho = Column(Integer, nullable=True)  # Tamanho em caracteres
    
    # Configurações da análise
    total_agentes_utilizados = Column(Integer, nullable=False)
    areas_juridicas_envolvidas = Column(JSON, nullable=False)  # Lista de áreas
    configuracao_analise = Column(JSON, nullable=True)  # Configurações específicas
    
    # Resultados da análise
    resultados_agentes = Column(JSON, nullable=False)  # Array com resultados de cada agente
    opiniao_consolidada = Column(Text, nullable=True)  # Opinião consolidada final
    pontos_criticos = Column(JSON, nullable=True)  # Array de pontos críticos
    recomendacoes_prioritarias = Column(JSON, nullable=True)  # Recomendações prioritárias
    recomendacoes_importantes = Column(JSON, nullable=True)  # Recomendações importantes
    recomendacoes_sugeridas = Column(JSON, nullable=True)  # Recomendações sugeridas
    
    # Metadados de execução
    tempo_processamento_segundos = Column(Float, nullable=True)
    modelos_ia_utilizados = Column(JSON, nullable=True)  # Lista de modelos usados
    tokens_consumidos = Column(Integer, nullable=True)  # Total de tokens
    custo_estimado = Column(Float, nullable=True)  # Custo estimado em USD
    
    # Status e controle
    status = Column(String(20), default='concluida')  # em_andamento, concluida, erro
    status_mensagem = Column(Text, nullable=True)
    fallback_mode = Column(Boolean, default=False)  # Se usou modo fallback
    debug_mode = Column(Boolean, default=False)  # Se estava em modo debug
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    data_conclusao = Column(DateTime, nullable=True)
    
    # Dados de exportação
    exportado_docx = Column(Boolean, default=False)
    exportado_pdf = Column(Boolean, default=False)
    exportado_txt = Column(Boolean, default=False)
    
    # Relacionamentos
    user = relationship('User', backref='analises_validacao_multi_agente')
    
    # Índices para performance
    __table_args__ = (
        Index('idx_validacao_uuid', 'uuid_analise'),
        Index('idx_validacao_hash', 'hash_sha256'),
        Index('idx_validacao_registro', 'numero_registro'),
        Index('idx_validacao_user_data', 'user_id', 'data_criacao'),
        Index('idx_validacao_status', 'status'),
    )
    
    def gerar_identificadores_unicos(self, texto_documento):
        """
        Gera os três identificadores únicos para a análise
        """
        import hashlib
        
        # UUID único
        self.uuid_analise = str(uuid.uuid4())
        
        # Hash SHA-256 do conteúdo + timestamp
        timestamp_str = datetime.datetime.now().isoformat()
        conteudo_hash = f"{texto_documento}{timestamp_str}{self.user_id}"
        self.hash_sha256 = hashlib.sha256(conteudo_hash.encode('utf-8')).hexdigest()
        
        # Número de registro no formato REG-TIMESTAMP
        timestamp_num = int(datetime.datetime.now().timestamp() * 1000)
        self.numero_registro = f"REG-{timestamp_num}"
    
    def to_dict(self):
        """Converte para dicionário para API"""
        return {
            'id': self.id,
            'uuid_analise': self.uuid_analise,
            'hash_sha256': self.hash_sha256,
            'numero_registro': self.numero_registro,
            'titulo_analise': self.titulo_analise,
            'descricao': self.descricao,
            'user_id': self.user_id,
            'documento_nome': self.documento_nome,
            'documento_tipo': self.documento_tipo,
            'documento_tamanho': self.documento_tamanho,
            'total_agentes_utilizados': self.total_agentes_utilizados,
            'areas_juridicas_envolvidas': self.areas_juridicas_envolvidas,
            'resultados_agentes': self.resultados_agentes,
            'opiniao_consolidada': self.opiniao_consolidada,
            'pontos_criticos': self.pontos_criticos,
            'recomendacoes_prioritarias': self.recomendacoes_prioritarias,
            'recomendacoes_importantes': self.recomendacoes_importantes,
            'recomendacoes_sugeridas': self.recomendacoes_sugeridas,
            'tempo_processamento_segundos': self.tempo_processamento_segundos,
            'modelos_ia_utilizados': self.modelos_ia_utilizados,
            'tokens_consumidos': self.tokens_consumidos,
            'custo_estimado': self.custo_estimado,
            'status': self.status,
            'status_mensagem': self.status_mensagem,
            'fallback_mode': self.fallback_mode,
            'debug_mode': self.debug_mode,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'exportado_docx': self.exportado_docx,
            'exportado_pdf': self.exportado_pdf,
            'exportado_txt': self.exportado_txt
        }
    
    @classmethod
    def obter_por_uuid(cls, uuid_analise):
        """Busca análise por UUID"""
        return cls.query.filter_by(uuid_analise=uuid_analise).first()
    
    @classmethod
    def obter_por_hash(cls, hash_sha256):
        """Busca análise por hash SHA-256"""
        return cls.query.filter_by(hash_sha256=hash_sha256).first()
    
    @classmethod
    def obter_por_registro(cls, numero_registro):
        """Busca análise por número de registro"""
        return cls.query.filter_by(numero_registro=numero_registro).first()
    
    @classmethod
    def listar_por_usuario(cls, user_id, limite=20):
        """Lista análises por usuário"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.data_criacao.desc())\
                       .limit(limite).all()
    
    def marcar_exportacao(self, formato):
        """Marca que foi exportado em determinado formato"""
        if formato == 'word' or formato == 'docx':
            self.exportado_docx = True
        elif formato == 'pdf':
            self.exportado_pdf = True
        elif formato == 'txt' or formato == 'json':
            self.exportado_txt = True
        
        db.session.commit()
    
    def __repr__(self):
        return f'<ValidacaoMultiAgenteAnalise {self.numero_registro}: {self.titulo_analise}>'

# Outras classes de modelo existentes...

class ProcessoJuridico(db.Model):
    """
    Modelo para processos jurídicos - Sistema de gestão processual completo
    """
    __tablename__ = 'processo_juridico'
    
    # Campos Básicos
    id = Column(Integer, primary_key=True)
    numero_processo_cnj = Column(String(25), unique=True, nullable=False, index=True)  # NNNNNNN-DD.AAAA.J.TR.OOOO
    area_juridica = Column(String(100), nullable=False, index=True)
    cliente = Column(String(200), nullable=False)
    autor = Column(String(200), nullable=False)
    parte_contraria = Column(String(200), nullable=True)  # Requerido/Réu
    cpf_autor = Column(String(14), nullable=True)  # XXX.XXX.XXX-XX (author/person)
    cnpj = Column(String(18), nullable=True)  # XX.XXX.XXX/XXXX-XX (company)
    advogado_do_caso = Column(String(200), nullable=False)
    advogado_adverso = Column(String(200), nullable=True)
    
    # Dados Processuais
    data_registro = Column(DateTime, default=datetime.datetime.now, nullable=False)
    data_distribuicao = Column(DateTime, nullable=False)
    estado = Column(String(50), nullable=False)
    comarca = Column(String(100), nullable=False)
    juizo = Column(String(200), nullable=False)
    resumo_dos_fatos = Column(Text, nullable=False)

    valor_da_causa = Column(Float, nullable=False)
    
    # Controle Financeiro
    calculo_contadores = Column(Float, nullable=True)
    provisao = Column(Float, nullable=True)
    execucao = Column(Float, nullable=True)
    previsao_de_pagamento = Column(DateTime, nullable=True)
    bloqueio = Column(Float, nullable=True)
    risco = Column(String(50), nullable=True)  # BAIXO, MÉDIO, ALTO
    
    # Acordos e Pagamentos
    data_acordo = Column(DateTime, nullable=True)
    acordo = Column(Float, nullable=True)
    pagamento = Column(Float, nullable=True)
    deposito_recursal = Column(Float, nullable=True)
    funcao = Column(String(200), nullable=True)
    andamento_relatorio = Column(Text, nullable=True)
    fase = Column(String(100), nullable=True)  # Fase processual (Inicial, Instrução, Sentença, etc)
    
    # Novos Campos Adicionais
    titulo = Column(String(255), nullable=True)
    ano_distribuicao = Column(Integer, nullable=True)
    status = Column(String(100), nullable=True)
    polo = Column(String(100), nullable=True)
    empresa = Column(String(255), nullable=True)
    processo = Column(String(50), nullable=True)
    esfera = Column(String(50), nullable=True)
    pasta = Column(String(100), nullable=True)  # Número/código da pasta física do processo
    acao = Column(String(255), nullable=True)
    tema = Column(String(255), nullable=True)
    objeto = Column(Text, nullable=True)
    instancia = Column(String(100), nullable=True)
    fase_processual = Column(String(100), nullable=True)
    liminar = Column(Boolean, default=False)
    valor_provisao = Column(Float, nullable=True)
    estimativa_desembolso = Column(DateTime, nullable=True)
    pagamentos = Column(Float, nullable=True)
    posicao_simplificada = Column(String(255), nullable=True)
    resultado = Column(String(255), nullable=True)
    resultado_processo = Column(String(20), nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Verbas Trabalhistas (Boolean fields para cada tipo de verba)
    acidente_de_trabalho = Column(Boolean, default=False)
    acumulo_de_funcao = Column(Boolean, default=False)
    adicional_de_periculosidade = Column(Boolean, default=False)
    adicional_de_sobreaviso = Column(Boolean, default=False)
    adicional_noturno_e_reflexos = Column(Boolean, default=False)
    ajuda_de_custo = Column(Boolean, default=False)
    aplicacao_do_artigo_467_da_clt = Column(Boolean, default=False)
    apresentacao_de_documentos = Column(Boolean, default=False)
    artigo_384_da_clt = Column(Boolean, default=False)
    beneficios_previstos_na_cct_da_2a_reclamada = Column(Boolean, default=False)
    descaracterizacao_do_cargo_de_confianca = Column(Boolean, default=False)
    devolucao_de_descontos = Column(Boolean, default=False)
    devolucao_de_descontos_lancados_no_trct = Column(Boolean, default=False)
    diferencas_de_comissoes = Column(Boolean, default=False)
    diferencas_salariais = Column(Boolean, default=False)
    dsrs = Column(Boolean, default=False)
    equiparacao_salarial = Column(Boolean, default=False)
    estabilidade = Column(Boolean, default=False)
    ferias_em_dobro = Column(Boolean, default=False)
    fgts_e_a_multa_de_40_porcento = Column(Boolean, default=False)
    horas_extras_e_reflexos = Column(Boolean, default=False)
    indenizacao_aviso_previo = Column(Boolean, default=False)
    indenizacao_por_danos_materiais = Column(Boolean, default=False)
    indenizacao_por_danos_morais = Column(Boolean, default=False)
    integracao_das_comissoes = Column(Boolean, default=False)
    integracao_das_comissoes_por_fora = Column(Boolean, default=False)
    integracao_dos_premios = Column(Boolean, default=False)
    intervalo_interjornada = Column(Boolean, default=False)
    intervalo_intrajornada = Column(Boolean, default=False)
    liberacao_das_guias_trct_e_cd_sob_pena_de_indenizacao = Column(Boolean, default=False)
    multa_convencional_ou_normativa = Column(Boolean, default=False)
    multa_do_artigo_477_da_clt = Column(Boolean, default=False)
    outros = Column(Boolean, default=False)
    plr = Column(Boolean, default=False)
    quebra_de_caixa = Column(Boolean, default=False)
    plano_de_saude = Column(Boolean, default=False)
    reconhecimento_da_remuneracao_recebida = Column(Boolean, default=False)
    reembolso_km = Column(Boolean, default=False)
    reenquadramento_sindical = Column(Boolean, default=False)
    reintegracao = Column(Boolean, default=False)
    rescisao_indireta = Column(Boolean, default=False)
    responsabilizacao_subsidiaria_da_2a_reclamada_vivo = Column(Boolean, default=False)
    reversao_do_pedido_de_demissao_em_demissao_sem_justa_causa = Column(Boolean, default=False)
    reversao_justa_causa = Column(Boolean, default=False)
    salario_substituicao = Column(Boolean, default=False)
    seguro_desemprego = Column(Boolean, default=False)
    sucumbencia = Column(Boolean, default=False)
    vale_refeicao = Column(Boolean, default=False)
    vale_transporte = Column(Boolean, default=False)
    verbas_rescisoria = Column(Boolean, default=False)
    
    # Metadados
    criado_em = Column(DateTime, default=datetime.datetime.now, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Campos Judit Integration
    judit_request_id = Column(String(100), nullable=True, index=True)
    judit_ultima_consulta = Column(DateTime, nullable=True)
    judit_dados_processo = Column(JSON, nullable=True)
    judit_movimentacoes = Column(JSON, nullable=True)
    judit_partes = Column(JSON, nullable=True)
    judit_anexos = Column(JSON, nullable=True)
    judit_monitoramento_id = Column(String(100), nullable=True)
    judit_status_monitoramento = Column(String(50), nullable=True)
    judit_sincronizado = Column(Boolean, default=False, nullable=False)
    
    # Campos adicionais de gestão
    situacao_id = Column(Integer, ForeignKey('situacao.id'), nullable=True)
    cpf_cliente = Column(String(14), nullable=True)
    cnpj_autor = Column(String(18), nullable=True)
    penhora = Column(Float, nullable=True)
    data_encerramento = Column(DateTime, nullable=True)
    motivo_encerramento = Column(String(255), nullable=True)
    
    # Campos financeiros adicionais
    custas_processuais = Column(Float, nullable=True)
    honorarios_periciais = Column(Float, nullable=True)
    honorarios_sucumbencia = Column(Float, nullable=True)
    depositos_judiciais = Column(Float, nullable=True)
    valor_honorarios_contratados = Column(Float, nullable=True)
    valor_recuperado = Column(Float, nullable=True)
    data_ultimo_pagamento = Column(DateTime, nullable=True)
    recebimentos_honorarios = Column(Float, nullable=True)
    tempo_fixado_beneficio = Column(Integer, nullable=True)  # Tempo em meses do benefício fixado
    
    # Campos de análise e métricas
    tempo_tramitacao_dias = Column(Integer, nullable=True)
    taxa_sucesso = Column(Float, nullable=True)
    satisfacao_cliente = Column(Float, nullable=True)
    produtividade_financeira = Column(Float, nullable=True)
    risco_concentracao = Column(Float, nullable=True)
    sazonalidade_mes = Column(String(20), nullable=True)
    
    # Campos de projeção financeira
    previsao_custos_futuros = Column(Float, nullable=True)
    projecao_gastos_fase = Column(Text, nullable=True)
    capital_giro_necessario = Column(Float, nullable=True)
    ciclo_financeiro_dias = Column(Integer, nullable=True)
    custo_operacional_caso = Column(Float, nullable=True)
    margem_lucro_caso = Column(Float, nullable=True)
    remuneracao_cargo_colaborador = Column(Float, nullable=True)
    cenario_melhor_caso = Column(Float, nullable=True)
    cenario_pior_caso = Column(Float, nullable=True)
    indice_viabilidade_economica = Column(Float, nullable=True)
    
    # Campos de Análises Avançadas por IA
    analise_estrategica = Column(Text, nullable=True)  # Análise estratégica do processo
    analise_tecnica = Column(Text, nullable=True)  # Análise técnica jurídica
    analise_estatistica = Column(Text, nullable=True)  # Análise estatística e probabilística
    analise_preditiva = Column(Text, nullable=True)  # Análise preditiva de resultados
    data_analise_ia = Column(DateTime, nullable=True)  # Data da última análise por IA
    
    # Campos dinâmicos por área jurídica
    campos_especificos = Column(JSONB, nullable=True)  # Campos personalizados por área jurídica
    
    # Relacionamentos
    usuario = relationship('User', backref='processos_juridicos')
    
    # Índices para performance
    __table_args__ = (
        Index('idx_processo_numero_cnj', 'numero_processo_cnj'),
        Index('idx_processo_area_juridica', 'area_juridica'),
        Index('idx_processo_cliente', 'cliente'),
        Index('idx_processo_data_registro', 'data_registro'),
        Index('idx_processo_usuario', 'usuario_id'),
    )
    
    def to_dict(self):
        """Converte o processo para dicionário"""
        return {
            'id': self.id,
            'numero_processo_cnj': self.numero_processo_cnj,
            'area_juridica': self.area_juridica,
            'cliente': self.cliente,
            'autor': self.autor,
            'cpf_autor': self.cpf_autor,
            'cnpj': self.cnpj,
            'advogado_do_caso': self.advogado_do_caso,
            'advogado_adverso': self.advogado_adverso,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'data_distribuicao': self.data_distribuicao.isoformat() if self.data_distribuicao else None,
            'estado': self.estado,
            'comarca': self.comarca,
            'juizo': self.juizo,
            'resumo_dos_fatos': self.resumo_dos_fatos,
            'fase': self.fase,
            'valor_da_causa': self.valor_da_causa,
            'calculo_contadores': self.calculo_contadores,
            'provisao': self.provisao,
            'execucao': self.execucao,
            'previsao_de_pagamento': self.previsao_de_pagamento.isoformat() if self.previsao_de_pagamento else None,
            'bloqueio': self.bloqueio,
            'risco': self.risco,
            
            # Novos campos
            'titulo': self.titulo,
            'ano_distribuicao': self.ano_distribuicao,
            'status': self.status,
            'polo': self.polo,
            'empresa': self.empresa,
            'processo': self.processo,
            'esfera': self.esfera,
            'acao': self.acao,
            'tema': self.tema,
            'objeto': self.objeto,
            'instancia': self.instancia,
            'fase_processual': self.fase_processual,
            'liminar': self.liminar,
            'valor_provisao': self.valor_provisao,
            'estimativa_desembolso': self.estimativa_desembolso.isoformat() if self.estimativa_desembolso else None,
            'pagamentos': self.pagamentos,
            'posicao_simplificada': self.posicao_simplificada,
            'resultado': self.resultado,
            'observacoes': self.observacoes,
            'data_acordo': self.data_acordo.isoformat() if self.data_acordo else None,
            'acordo': self.acordo,
            'pagamento': self.pagamento,
            'deposito_recursal': self.deposito_recursal,
            'funcao': self.funcao,
            'andamento_relatorio': self.andamento_relatorio,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'usuario_id': self.usuario_id
        }
    
    def get_verbas_trabalhistas(self):
        """Retorna lista das verbas trabalhistas marcadas como True"""
        verbas = []
        campos_verbas = [
            'acidente_de_trabalho', 'acumulo_de_funcao', 'adicional_de_periculosidade',
            'adicional_de_sobreaviso', 'adicional_noturno_e_reflexos', 'ajuda_de_custo',
            'aplicacao_do_artigo_467_da_clt', 'apresentacao_de_documentos', 'artigo_384_da_clt',
            'beneficios_previstos_na_cct_da_2a_reclamada', 'descaracterizacao_do_cargo_de_confianca',
            'devolucao_de_descontos', 'devolucao_de_descontos_lancados_no_trct', 'diferencas_de_comissoes',
            'diferencas_salariais', 'dsrs', 'equiparacao_salarial', 'estabilidade',
            'ferias_em_dobro', 'fgts_e_a_multa_de_40_porcento', 'horas_extras_e_reflexos',
            'indenizacao_aviso_previo', 'indenizacao_por_danos_materiais', 'indenizacao_por_danos_morais',
            'integracao_das_comissoes', 'integracao_das_comissoes_por_fora', 'integracao_dos_premios',
            'intervalo_interjornada', 'intervalo_intrajornada', 'liberacao_das_guias_trct_e_cd_sob_pena_de_indenizacao',
            'multa_convencional_ou_normativa', 'multa_do_artigo_477_da_clt', 'outros', 'plr',
            'quebra_de_caixa', 'plano_de_saude', 'reconhecimento_da_remuneracao_recebida',
            'reembolso_km', 'reenquadramento_sindical', 'reintegracao', 'rescisao_indireta',
            'responsabilizacao_subsidiaria_da_2a_reclamada_vivo', 'reversao_do_pedido_de_demissao_em_demissao_sem_justa_causa',
            'reversao_justa_causa', 'salario_substituicao', 'seguro_desemprego', 'sucumbencia',
            'vale_refeicao', 'vale_transporte', 'verbas_rescisoria'
        ]
        
        for campo in campos_verbas:
            if getattr(self, campo, False):
                verbas.append(campo.replace('_', ' ').title())
        
        return verbas
    
    def atualizar_dados_judit(self, dados_judit):
        """Atualiza os dados de integração com Judit"""
        if isinstance(dados_judit, dict):
            self.judit_dados_processo = dados_judit.get('dados', {})
            self.judit_movimentacoes = dados_judit.get('movimentacoes', [])
            self.judit_partes = dados_judit.get('partes', [])
            self.judit_anexos = dados_judit.get('anexos', [])
            self.judit_request_id = dados_judit.get('request_id')
            self.judit_ultima_consulta = datetime.datetime.now()
            self.judit_sincronizado = True
    
    def obter_resumo_judit(self):
        """Retorna um resumo dos dados Judit sincronizados"""
        if not self.judit_sincronizado or not self.judit_dados_processo:
            return {
                'status': 'não sincronizado',
                'ultima_consulta': self.judit_ultima_consulta.isoformat() if self.judit_ultima_consulta else None
            }
        
        dados = self.judit_dados_processo if isinstance(self.judit_dados_processo, dict) else {}
        movimentacoes = self.judit_movimentacoes if isinstance(self.judit_movimentacoes, list) else []
        
        return {
            'status': 'sincronizado',
            'numero_cnj': self.numero_processo_cnj,
            'ultima_consulta': self.judit_ultima_consulta.isoformat() if self.judit_ultima_consulta else None,
            'movimentacoes_count': len(movimentacoes),
            'classe': dados.get('classe', 'N/A'),
            'assunto': dados.get('assunto', 'N/A'),
            'fase': dados.get('fase', 'N/A'),
            'request_id': self.judit_request_id
        }
    
    def precisa_atualizacao_judit(self):
        """Verifica se o processo precisa de atualização nos dados Judit"""
        if not self.judit_sincronizado:
            return True
        
        if not self.judit_ultima_consulta:
            return True
        
        # Atualizar se passou mais de 7 dias
        dias_desde_ultima_consulta = (datetime.datetime.now() - self.judit_ultima_consulta).days
        return dias_desde_ultima_consulta > 7
    
    @classmethod
    def buscar_por_cnj(cls, numero_cnj):
        """Busca processo por número CNJ"""
        return cls.query.filter_by(numero_processo_cnj=numero_cnj).first()
    
    @classmethod
    def listar_por_area(cls, area_juridica, limite=50):
        """Lista processos por área jurídica"""
        return cls.query.filter_by(area_juridica=area_juridica)\
                       .order_by(cls.data_registro.desc())\
                       .limit(limite).all()
    
    @classmethod
    def listar_por_cliente(cls, cliente, limite=50):
        """Lista processos por cliente"""
        return cls.query.filter(cls.cliente.ilike(f'%{cliente}%'))\
                       .order_by(cls.data_registro.desc())\
                       .limit(limite).all()
    
    def __repr__(self):
        return f'<ProcessoJuridico {self.numero_processo_cnj}: {self.cliente}>'


# =====================================================
# MODELS DE MÉTRICAS FINANCEIRAS E PERFORMANCE
# =====================================================

class CashFlowOperacional(db.Model):
    """Modelo para cash flow operacional mensal"""
    __tablename__ = 'cash_flow_operacional'
    
    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    honorarios_processos = Column(Float, nullable=False, default=0)
    consultorias = Column(Float, nullable=False, default=0)
    due_diligence = Column(Float, nullable=False, default=0)
    pareceres_juridicos = Column(Float, nullable=False, default=0)
    contratos_especiais = Column(Float, nullable=False, default=0)
    outras_receitas = Column(Float, nullable=False, default=0)
    custos_processuais = Column(Float, nullable=False, default=0)
    despesas_operacionais = Column(Float, nullable=False, default=0)
    pagamento_colaboradores = Column(Float, nullable=False, default=0)
    impostos_taxas = Column(Float, nullable=False, default=0)
    marketing_captacao = Column(Float, nullable=False, default=0)
    tecnologia_sistemas = Column(Float, nullable=False, default=0)
    outras_despesas = Column(Float, nullable=False, default=0)
    total_entradas = Column(Float, nullable=False, default=0)
    total_saidas = Column(Float, nullable=False, default=0)
    resultado_operacional = Column(Float, nullable=False, default=0)
    margem_operacional = Column(Float, nullable=False, default=0)
    processos_quantidade = Column(Integer, nullable=False, default=0)
    ciclo_medio_dias = Column(Integer, nullable=False, default=45)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    criado_por_id = Column(Integer)
    
    def __repr__(self):
        return f'<CashFlowOperacional {self.ano}/{self.mes}>'


class IndicadorFluxo(db.Model):
    """Modelo para indicadores de fluxo de caixa"""
    __tablename__ = 'indicador_fluxo'
    
    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    honorarios_processos = Column(Float, nullable=False, default=0)
    repasse_pagamentos_custas = Column(Float, nullable=False, default=0)
    recebimentos_acordos = Column(Float, nullable=False, default=0)
    execucoes_realizadas = Column(Float, nullable=False, default=0)
    custos_operacionais_processos = Column(Float, nullable=False, default=0)
    custas_processuais_pagas = Column(Float, nullable=False, default=0)
    despesas_escritorio = Column(Float, nullable=False, default=0)
    investimentos_marketing = Column(Float, nullable=False, default=0)
    fluxo_liquido = Column(Float, nullable=False, default=0)
    saldo_acumulado = Column(Float, nullable=False, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<IndicadorFluxo {self.ano}/{self.mes}>'


class PerformanceFinanceiraAdvogado(db.Model):
    """Modelo para performance financeira individual de advogados"""
    __tablename__ = 'performance_financeira_advogado'
    
    id = Column(Integer, primary_key=True)
    advogado_nome = Column(String(255), nullable=False)
    periodo_ano = Column(Integer, nullable=False)
    periodo_mes = Column(Integer, nullable=True)
    total_casos = Column(Integer, default=0)
    carteira_total = Column(Float, default=0)
    provisao_total = Column(Float, default=0)
    pagamento_total = Column(Float, default=0)
    honorarios_recebidos = Column(Float, default=0)
    margem_media = Column(Float, default=0)
    eficiencia_media = Column(Float, default=0)
    produtividade_financeira = Column(Float, default=0)
    roi_individual = Column(Float, default=0)
    tempo_medio_processo = Column(Float, default=0)
    taxa_sucesso = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<PerformanceFinanceiraAdvogado {self.advogado_nome} - {self.periodo_ano}/{self.periodo_mes}>'


class IndicadoresEstrategicos(db.Model):
    """Modelo para indicadores estratégicos globais"""
    __tablename__ = 'indicadores_estrategicos'
    
    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=True)
    total_processos = Column(Integer, default=0)
    processos_ativos = Column(Integer, default=0)
    processos_encerrados = Column(Integer, default=0)
    taxa_sucesso_global = Column(Float, default=0)
    valor_total_carteira = Column(Float, default=0)
    provisao_total = Column(Float, default=0)
    receita_bruta = Column(Float, default=0)
    custos_totais = Column(Float, default=0)
    margem_liquida = Column(Float, default=0)
    roi_geral = Column(Float, default=0)
    tempo_medio_conclusao = Column(Float, default=0)
    satisfacao_cliente_media = Column(Float, default=0)
    produtividade_media = Column(Float, default=0)
    capacidade_utilizada = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<IndicadoresEstrategicos {self.ano}/{self.mes}>'


class InadimplenciaPorArea(db.Model):
    """Modelo para inadimplência por área jurídica"""
    __tablename__ = 'inadimplencia_por_area'
    
    id = Column(Integer, primary_key=True)
    area_juridica = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=True)
    total_casos = Column(Integer, default=0)
    casos_inadimplentes = Column(Integer, default=0)
    taxa_inadimplencia = Column(Float, default=0)
    valor_inadimplente = Column(Float, default=0)
    tempo_medio_atraso = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    __table_args__ = (
        UniqueConstraint('area_juridica', 'ano', 'mes', name='uk_inadimplencia_area_periodo'),
    )
    
    def __repr__(self):
        return f'<InadimplenciaPorArea {self.area_juridica} - {self.ano}/{self.mes}>'


class LawyerMetrics(db.Model):
    """Modelo para métricas consolidadas de advogados"""
    __tablename__ = 'lawyer_metrics'
    
    id = Column(Integer, primary_key=True)
    advogado_nome = Column(String(200), nullable=False)
    total_casos = Column(Integer, default=0)
    eficiencia = Column(Float, default=0)
    carteira_total = Column(Float, default=0)
    remuneracao = Column(Float, default=0)
    produtividade_financeira = Column(Float, default=0)
    margem_media = Column(Float, default=0)
    produtividade_tecnica = Column(Float, default=0)
    roi_individual = Column(Float, default=0)
    casos_por_milhao = Column(Float, default=0)
    eficiencia_geral = Column(Float, default=0)
    taxa_sucesso = Column(Float, default=0)
    tempo_medio_caso = Column(Float, default=0)
    satisfacao_cliente = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<LawyerMetrics {self.advogado_nome}>'


class RelatorioConsenso(db.Model):
    """Modelo para relatórios de consenso multi-agente"""
    __tablename__ = 'relatorio_consenso'
    
    id = Column(Integer, primary_key=True)
    uuid_relatorio = Column(String(36), nullable=False, unique=True)
    numero_relatorio = Column(String(20), nullable=False, unique=True)
    analise_numero_registro = Column(String(20), nullable=False)
    titulo_relatorio = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    consenso_geral = Column(Text, nullable=False)
    nivel_concordancia = Column(Float, default=0)
    pontos_convergencia = Column(JSON, nullable=True)
    pontos_divergencia = Column(JSON, nullable=True)
    analise_riscos = Column(JSON, nullable=False)
    
    # Colunas de análise detalhada (conforme banco de dados)
    analise_melhorias = Column(JSON, nullable=True)
    estrategias_recomendadas = Column(JSON, nullable=True)
    riscos_criticos = Column(JSON, nullable=True)
    riscos_moderados = Column(JSON, nullable=True)
    riscos_baixos = Column(JSON, nullable=True)
    melhorias_urgentes = Column(JSON, nullable=True)
    melhorias_importantes = Column(JSON, nullable=True)
    melhorias_sugeridas = Column(JSON, nullable=True)
    estrategias_curto_prazo = Column(JSON, nullable=True)
    estrategias_medio_prazo = Column(JSON, nullable=True)
    estrategias_longo_prazo = Column(JSON, nullable=True)
    
    # Colunas de impacto e viabilidade
    impacto_estimado = Column(String(50), nullable=True)
    viabilidade_implementacao = Column(String(50), nullable=True)
    recursos_necessarios = Column(JSON, nullable=True)
    
    # Metadados de processamento
    modelo_ia_utilizado = Column(String(100), nullable=True)
    tokens_consumidos = Column(Integer, default=0)
    custo_estimado = Column(Float, default=0.0)
    tempo_processamento = Column(Float, default=0.0)
    
    # Status e versionamento
    status = Column(String(50), default='draft')
    status_mensagem = Column(Text, nullable=True)
    versao = Column(Integer, default=1)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.datetime.now, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    data_aprovacao = Column(DateTime, nullable=True)
    
    # Relacionamento
    usuario = relationship('User', backref='relatorios_consenso')
    
    def gerar_identificadores_unicos(self):
        """
        Gera os identificadores únicos para o relatório de consenso
        """
        import hashlib
        
        # UUID único
        self.uuid_relatorio = str(uuid.uuid4())
        
        # Número de relatório no formato REL-TIMESTAMP
        timestamp_num = int(datetime.datetime.now().timestamp() * 1000)
        self.numero_relatorio = f"REL-{timestamp_num}"
    
    def get_analise_multiagente(self):
        """
        Retorna a análise multi-agente relacionada a este relatório
        """
        return ValidacaoMultiAgenteAnalise.query.filter_by(
            numero_registro=self.analise_numero_registro
        ).first()
    
    def __repr__(self):
        return f'<RelatorioConsenso {self.numero_relatorio}: {self.titulo_relatorio}>'


class Situacao(db.Model):
    """Modelo para situação de processos (Ativo/Encerrado)"""
    __tablename__ = 'situacao'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)
    descricao = Column(String(255), nullable=True)
    criado_em = Column(DateTime, default=datetime.datetime.now, nullable=False)
    
    # Relacionamento com processos
    processos = relationship('ProcessoJuridico', backref='situacao', lazy=True)
    
    def __repr__(self):
        return f'<Situacao {self.nome}>'


class AnaliseProcessoIA(db.Model):
    """Modelo para análises de processos jurídicos por IA"""
    __tablename__ = 'analise_processo_ia'
    
    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_juridico.id'), nullable=False)
    tipo_analise = Column(String(100), nullable=False)  # estrategica, tecnica, estatistica, preditiva
    modelo_ia = Column(String(100), nullable=False)  # gpt-4, claude-sonnet, etc
    resultado = Column(JSON, nullable=False)  # Resultado estruturado da análise
    confianca = Column(Float, nullable=True)  # Nível de confiança (0-1)
    criado_em = Column(DateTime, default=datetime.datetime.now, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    usuario_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    tempo_processamento = Column(Integer, nullable=True)  # Tempo em segundos
    status = Column(String(50), default='completo')  # completo, erro, processando
    
    # Relacionamentos
    processo = relationship('ProcessoJuridico', backref='analises_ia')
    usuario = relationship('User', backref='analises_processo_ia')
    
    def __repr__(self):
        return f'<AnaliseProcessoIA {self.id}: {self.tipo_analise} - Processo {self.processo_id}>'


class UserAIPreferences(db.Model):
    """Modelo para preferências de IA do usuário"""
    __tablename__ = 'user_ai_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    area_juridica = Column(String(100), nullable=True)  # None = global, ou área específica
    provider = Column(String(50), nullable=False, default='openai')  # openai, anthropic, google, deepseek
    modelo = Column(String(100), nullable=False, default='gpt-5')  # modelo específico
    personalidade = Column(String(50), nullable=True, default='advogado')
    tom = Column(String(50), nullable=True, default='sistematico')
    estilo = Column(String(50), nullable=True, default='juridico_tecnico')
    criado_em = Column(DateTime, default=datetime.datetime.now, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    # Constraint única: um usuário pode ter apenas uma configuração por área (ou global)
    __table_args__ = (
        UniqueConstraint('user_id', 'area_juridica', name='uq_user_area_pref'),
    )
    
    # Relacionamento
    usuario = relationship('User', backref='preferencias_ia')
    
    def __repr__(self):
        area = self.area_juridica or 'global'
        return f'<UserAIPreferences {self.user_id}: {area} - {self.modelo}>'


class DatabaseJob(db.Model):
    """
    Modelo para rastrear operações de banco de dados (sync, backup, restore, init, test).
    Permite monitoramento em tempo real do progresso e histórico de operações.
    """
    __tablename__ = 'database_job'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)  # sync, backup, restore, init, test
    status = Column(String(50), default='pending', nullable=False)  # pending, running, success, failed, cancelled
    source_db = Column(String(100), nullable=True)  # neon, postgres_local, sqlite_local
    target_db = Column(String(100), nullable=True)  # neon, postgres_local, sqlite_local
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    logs = Column(JSON, nullable=True)  # Array de mensagens de log
    result_data = Column(JSON, nullable=True)  # Dados do resultado (estatísticas, arquivos gerados, etc)
    error_message = Column(Text, nullable=True)  # Mensagem de erro se status = failed
    
    # Auditoria
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Duração total em segundos
    
    # Celery task ID para rastreamento
    celery_task_id = Column(String(255), nullable=True)
    
    # Relacionamentos
    created_by = relationship('User', backref='database_jobs')
    
    # Índices para performance
    __table_args__ = (
        Index('idx_database_job_status', 'status'),
        Index('idx_database_job_type', 'type'),
        Index('idx_database_job_created_by', 'created_by_id'),
        Index('idx_database_job_started_at', 'started_at'),
        Index('idx_database_job_celery_task', 'celery_task_id'),
    )
    
    def __repr__(self):
        return f'<DatabaseJob {self.id}: {self.type} - {self.status}>'
    
    def to_dict(self):
        """Converte o job para dicionário para JSON responses"""
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'source_db': self.source_db,
            'target_db': self.target_db,
            'progress': self.progress,
            'logs': self.logs or [],
            'result_data': self.result_data,
            'error_message': self.error_message,
            'created_by': self.created_by.username if self.created_by else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'celery_task_id': self.celery_task_id
        }
    
    def add_log(self, message, level='info'):
        """Adiciona uma mensagem ao log do job"""
        if self.logs is None:
            self.logs = []
        
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
    
    def update_progress(self, progress, message=None):
        """Atualiza o progresso do job"""
        self.progress = min(100, max(0, progress))
        if message:
            self.add_log(message, 'info')


class SystemSetting(db.Model):
    """
    Modelo para configurações do sistema, incluindo configurações de banco de dados.
    Permite armazenar e gerenciar configurações de forma persistente.
    """
    __tablename__ = 'system_setting'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)  # db_mode, local_db_type, etc
    value = Column(Text, nullable=True)  # Valor da configuração (pode ser JSON)
    value_type = Column(String(50), default='string', nullable=False)  # string, integer, boolean, json
    description = Column(Text, nullable=True)  # Descrição da configuração
    category = Column(String(50), nullable=True)  # database, system, api, etc
    is_sensitive = Column(Boolean, default=False)  # Se contém dados sensíveis (senhas, etc)
    is_editable = Column(Boolean, default=True)  # Se pode ser editado via interface
    
    # Auditoria
    updated_by_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    # Relacionamentos
    updated_by = relationship('User', backref='system_settings_updated')
    
    # Índices para performance
    __table_args__ = (
        Index('idx_system_setting_key', 'key'),
        Index('idx_system_setting_category', 'category'),
    )
    
    def __repr__(self):
        return f'<SystemSetting {self.key}: {self.value}>'
    
    def to_dict(self, mask_sensitive=True):
        """Converte a configuração para dicionário"""
        value = self.value
        
        # Mascarar valores sensíveis
        if mask_sensitive and self.is_sensitive and value:
            value = '***MASKED***'
        
        return {
            'id': self.id,
            'key': self.key,
            'value': value,
            'value_type': self.value_type,
            'description': self.description,
            'category': self.category,
            'is_sensitive': self.is_sensitive,
            'is_editable': self.is_editable,
            'updated_by': self.updated_by.username if self.updated_by else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_value(key, default=None):
        """Obtém o valor de uma configuração"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return default
        
        # Converter tipo
        if setting.value_type == 'boolean':
            return setting.value.lower() in ('true', '1', 'yes', 'on')
        elif setting.value_type == 'integer':
            try:
                return int(setting.value)
            except (ValueError, TypeError):
                return default
        elif setting.value_type == 'json':
            try:
                return json.loads(setting.value)
            except (ValueError, TypeError):
                return default
        else:
            return setting.value
    
    @staticmethod
    def set_value(key, value, user_id=None, value_type='string', description=None, category=None):
        """Define o valor de uma configuração"""
        setting = SystemSetting.query.filter_by(key=key).first()
        
        # Converter valor para string
        if value_type == 'json':
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        if setting:
            setting.value = value_str
            setting.value_type = value_type
            setting.updated_by_id = user_id
            if description:
                setting.description = description
            if category:
                setting.category = category
        else:
            setting = SystemSetting(
                key=key,
                value=value_str,
                value_type=value_type,
                description=description,
                category=category,
                updated_by_id=user_id
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting


class ConversaAgente(db.Model):
    """
    Modelo para armazenar conversas salvas entre usuário e agentes jurídicos
    """
    __tablename__ = 'conversa_agente'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    agente_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    mensagens = Column(Text, nullable=False)  # JSON com array de mensagens
    data_criacao = Column(DateTime, default=datetime.datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relacionamentos
    agente = db.relationship('AgenteJuridico', backref='conversas')
    usuario = db.relationship('User', backref='conversas_agentes')
    
    def __repr__(self):
        return f'<ConversaAgente {self.titulo}>'
    
    def to_dict(self):
        """Converte a conversa para dicionário"""
        import json
        return {
            'id': self.id,
            'titulo': self.titulo,
            'agente_id': self.agente_id,
            'agente_nome': self.agente.nome if self.agente else None,
            'mensagens': json.loads(self.mensagens) if isinstance(self.mensagens, str) else self.mensagens,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'data_atualizacao': self.data_atualizacao.strftime('%d/%m/%Y %H:%M')
        }


class HistoricoPagamento(db.Model):
    """
    Modelo para armazenar histórico de pagamentos relacionados aos processos jurídicos
    """
    __tablename__ = 'historico_pagamentos'
    
    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_juridico.id'), nullable=False)
    data_pagamento = Column(DateTime, nullable=False)
    tipo_pagamento = Column(String(100), nullable=False)
    valor = Column(Numeric(15, 2), nullable=False)
    descricao = Column(Text)
    forma_pagamento = Column(String(50))
    status = Column(String(50), default='Realizado')
    comprovante = Column(String(500))
    observacoes = Column(Text)
    criado_por_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relacionamento
    processo = db.relationship('ProcessoJuridico', backref='historico_pagamentos')
    
    def __repr__(self):
        return f'<HistoricoPagamento {self.tipo_pagamento} - R$ {self.valor}>'
    
    def to_dict(self):
        """Converte o pagamento para dicionário"""
        return {
            'id': self.id,
            'processo_id': self.processo_id,
            'numero_processo_cnj': self.processo.numero_processo_cnj if self.processo else None,
            'cliente': self.processo.cliente if self.processo else None,
            'data_pagamento': self.data_pagamento.strftime('%d/%m/%Y') if self.data_pagamento else None,
            'tipo_pagamento': self.tipo_pagamento,
            'valor': float(self.valor) if self.valor else 0.0,
            'descricao': self.descricao,
            'forma_pagamento': self.forma_pagamento,
            'status': self.status,
            'comprovante': self.comprovante,
            'observacoes': self.observacoes
        }



# ============================================================================
# SISTEMA DE PROCESSOS DIN MICOS
# Adicionado em: 15 Dezembro 2025
# ============================================================================

class Processo(db.Model):
    """Tabela principal de processos jurdicos com campos dinmicos"""
    __tablename__ = 'processos'
    
    id_processo = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    tenant_id = Column(Integer, nullable=True)
    
    # Dados Bsicos
    numero_cnj = Column(String(25))
    pasta = Column(String(50))
    status_id = Column(Integer)
    natureza_id = Column(Integer)
    
    # Cliente
    cliente_id = Column(Integer)
    posicao_cliente_id = Column(Integer)
    
    # Classificao Jurdica
    acao_id = Column(Integer)
    procedimento_id = Column(Integer)
    fase_id = Column(Integer)
    
    # Localizao Processual
    orgao_id = Column(Integer)
    comarca_id = Column(Integer)
    vara_turma_id = Column(Integer)
    
    # CNJ
    justica_cnj_id = Column(Integer)
    instancia_cnj_id = Column(Integer)
    classe_cnj_id = Column(Integer)
    
    # Datas
    data_distribuicao = Column(DateTime)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Valores
    valor_causa = Column(Numeric(18, 2))
    valor_causa_atualizado = Column(Numeric(18, 2))
    valor_envolvido = Column(Numeric(18, 2))
    valor_envolvido_atualizado = Column(Numeric(18, 2))
    contingencia = Column(Numeric(18, 2))
    
    # Prognstico
    tipo_probabilidade_id = Column(Integer)
    risco_id = Column(Integer)
    
    # Metadados
    titulo = Column(Text)
    observacao_pasta = Column(Text)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    campos_especificos = relationship('ProcessoCamposEspecificos', back_populates='processo', uselist=False, cascade='all, delete-orphan')
    processo_tributario = relationship('ProcessoTributario', back_populates='processo', uselist=False, cascade='all, delete-orphan')
    processo_trabalhista = relationship('ProcessoTrabalhista', back_populates='processo', uselist=False, cascade='all, delete-orphan')
    processo_civel = relationship('ProcessoCivel', back_populates='processo', uselist=False, cascade='all, delete-orphan')
    teses = relationship('ProcessoTese', back_populates='processo', cascade='all, delete-orphan')
    atualizacoes_monetarias = relationship('ProcessoAtualizacaoMonetaria', back_populates='processo', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Processo {self.id_processo}: {self.numero_cnj or self.pasta}>'
    
    def to_dict(self):
        """Serializao bsica"""
        return {
            'id_processo': self.id_processo,
            'uuid': str(self.uuid),
            'numero_cnj': self.numero_cnj,
            'pasta': self.pasta,
            'natureza_id': self.natureza_id,
            'status_id': self.status_id,
            'data_distribuicao': self.data_distribuicao.isoformat() if self.data_distribuicao else None,
            'valor_causa': float(self.valor_causa) if self.valor_causa else None,
            'ativo': self.ativo
        }


class ProcessoCamposEspecificos(db.Model):
    """Campos especficos por natureza armazenados em JSONB"""
    __tablename__ = 'processo_campos_especificos'
    
    id_campo_especifico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False)
    natureza_id = Column(Integer)
    
    # Campos JSONB por natureza
    campos_tributario = Column(JSONB)
    campos_trabalhista = Column(JSONB)
    campos_civel = Column(JSONB)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    processo = relationship('Processo', back_populates='campos_especificos')
    
    __table_args__ = (
        UniqueConstraint('processo_id', 'natureza_id', name='uk_processo_natureza'),
    )


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
    
    # Relationships
    teses = relationship('TeseTributaria', back_populates='tributo')
    processos_tributarios = relationship('ProcessoTributario', back_populates='tributo')
    
    def __repr__(self):
        return f'<Tributo {self.codigo}: {self.nome}>'


class TeseTributaria(db.Model):
    """Teses jurdicas tributrias"""
    __tablename__ = 'teses_tributarias'
    
    id_tese = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    descricao = Column(Text)
    tributo_id = Column(Integer, ForeignKey('tributos.id_tributo'))
    
    # Jurisprudncia
    tema_repercussao_geral = Column(String(50))
    tema_repetitivo = Column(String(50))
    tribunal_origem = Column(String(100))
    
    # Prognstico padro
    probabilidade_sucesso = Column(Numeric(5, 2))
    fundamentacao = Column(Text)
    situacao = Column(String(50))  # Favorvel, Desfavorvel, Pendente, Superada
    
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


class ProcessoTributario(db.Model):
    """Dados especficos de processos tributrios"""
    __tablename__ = 'processo_tributario'
    
    id_processo_tributario = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Tributo
    tributo_id = Column(Integer, ForeignKey('tributos.id_tributo'))
    
    # Documentos Fiscais
    numero_aiim = Column(String(100))
    numero_cda = Column(String(100))
    data_lancamento = Column(DateTime)
    
    # Valores Especficos
    valor_inscrito_cda = Column(Numeric(18, 2))
    valor_principal = Column(Numeric(18, 2))
    valor_multa = Column(Numeric(18, 2))
    percentual_multa = Column(Numeric(5, 2))
    base_calculo_multa = Column(String(100))
    
    # Juros
    valor_juros = Column(Numeric(18, 2))
    indice_juros = Column(String(50))  # SELIC, Lei 13918, IPCA, CDI, Outro
    descricao_indice_juros = Column(Text)
    
    # Varas
    vara_primeira_instancia_id = Column(Integer)
    turma_segunda_instancia_id = Column(Integer)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='processo_tributario')
    tributo = relationship('Tributo', back_populates='processos_tributarios')
    prognostico = relationship('ProcessoPrognosticoTributario', back_populates='processo_tributario', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ProcessoTributario processo_id={self.processo_id}>'


class ProcessoTese(db.Model):
    """Relacionamento N:N entre processos e teses tributrias"""
    __tablename__ = 'processo_tese'
    
    id_processo_tese = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False)
    tese_id = Column(Integer, ForeignKey('teses_tributarias.id_tese', ondelete='CASCADE'), nullable=False)
    
    # Ordem de importncia
    ordem = Column(Integer, default=1)
    status = Column(String(50))  # Aguardando, Em anlise, Aceita, Rejeitada
    
    data_vinculacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='teses')
    tese = relationship('TeseTributaria', back_populates='processos')
    
    __table_args__ = (
        UniqueConstraint('processo_id', 'tese_id', name='uk_processo_tese'),
    )


class ProcessoPrognosticoTributario(db.Model):
    """Prognstico detalhado para processos tributrios"""
    __tablename__ = 'processo_prognostico_tributario'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_tributario.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # `xito Provvel (70%)
    tese_provavel_id = Column(Integer, ForeignKey('teses_tributarias.id_tese'))
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # `xito Possvel (50%)
    tese_possivel_id = Column(Integer, ForeignKey('teses_tributarias.id_tese'))
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # `xito Remoto (25%)
    tese_remota_id = Column(Integer, ForeignKey('teses_tributarias.id_tese'))
    valor_remoto = Column(Numeric(18, 2))
    percentual_remoto = Column(Numeric(5, 2), default=25.00)
    
    # Metadados
    observacoes = Column(Text)
    data_avaliacao = Column(DateTime)
    avaliado_por = Column(Integer)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo_tributario = relationship('ProcessoTributario', back_populates='prognostico')
    tese_provavel = relationship('TeseTributaria', foreign_keys=[tese_provavel_id])
    tese_possivel = relationship('TeseTributaria', foreign_keys=[tese_possivel_id])
    tese_remota = relationship('TeseTributaria', foreign_keys=[tese_remota_id])


class ProcessoTrabalhista(db.Model):
    """Dados especficos de processos trabalhistas"""
    __tablename__ = 'processo_trabalhista'
    
    id_processo_trabalhista = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Acordo
    tolerancia_acordo = Column(Numeric(18, 2))
    acordo_realizado = Column(Numeric(18, 2))
    data_acordo = Column(DateTime)
    observacoes_acordo = Column(Text)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='processo_trabalhista')
    prognostico = relationship('ProcessoPrognosticoTrabalhista', back_populates='processo_trabalhista', uselist=False, cascade='all, delete-orphan')


class ProcessoPrognosticoTrabalhista(db.Model):
    """Prognstico para processos trabalhistas"""
    __tablename__ = 'processo_prognostico_trabalhista'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_trabalhista.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # `xito Provvel
    tese_provavel = Column(Text)
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # `xito Possvel
    tese_possivel = Column(Text)
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # `xito Remoto
    tese_remota = Column(Text)
    valor_remoto = Column(Numeric(18, 2))
    percentual_remoto = Column(Numeric(5, 2), default=25.00)
    
    # Metadados
    observacoes = Column(Text)
    data_avaliacao = Column(DateTime)
    avaliado_por = Column(Integer)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo_trabalhista = relationship('ProcessoTrabalhista', back_populates='prognostico')


class ProcessoCivel(db.Model):
    """Dados especficos de processos cveis"""
    __tablename__ = 'processo_civel'
    
    id_processo_civel = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Acordo
    tolerancia_acordo = Column(Numeric(18, 2))
    acordo_realizado = Column(Numeric(18, 2))
    data_acordo = Column(DateTime)
    observacoes_acordo = Column(Text)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='processo_civel')
    prognostico = relationship('ProcessoPrognosticoCivel', back_populates='processo_civel', uselist=False, cascade='all, delete-orphan')


class ProcessoPrognosticoCivel(db.Model):
    """Prognstico para processos cveis"""
    __tablename__ = 'processo_prognostico_civel'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_civel.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # `xito Provvel
    tese_provavel = Column(Text)
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # `xito Possvel
    tese_possivel = Column(Text)
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # `xito Remoto
    tese_remota = Column(Text)
    valor_remoto = Column(Numeric(18, 2))
    percentual_remoto = Column(Numeric(5, 2), default=25.00)
    
    # Metadados
    observacoes = Column(Text)
    data_avaliacao = Column(DateTime)
    avaliado_por = Column(Integer)
    
    # Auditoria
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    processo_civel = relationship('ProcessoCivel', back_populates='prognostico')


class IndiceMonetario(db.Model):
    """Cadastro de ndices de correo monetria"""
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
    """Histrico de valores dos ndices monetrios"""
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


class ProcessoAtualizacaoMonetaria(db.Model):
    """Registro de atualizaes monetrias realizadas"""
    __tablename__ = 'processo_atualizacao_monetaria'
    
    id_atualizacao = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False)
    
    # Configurao
    indice_id = Column(Integer, ForeignKey('indices_monetarios.id_indice'), nullable=False)
    data_base = Column(DateTime, nullable=False)
    valor_base = Column(Numeric(18, 2), nullable=False)
    
    # Resultado
    data_atualizacao = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    valor_atualizado = Column(Numeric(18, 2))
    percentual_correcao = Column(Numeric(10, 6))
    
    calculado_em = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='atualizacoes_monetarias')
    indice = relationship('IndiceMonetario', back_populates='atualizacoes')


class ConfiguracaoFormulario(db.Model):
    """Configurao dinmica de formulrios por natureza"""
    __tablename__ = 'configuracao_formulario'
    
    id_configuracao = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    natureza_id = Column(Integer)
    
    # Estrutura do formulrio em JSON
    campos_obrigatorios = Column(JSONB, nullable=False, default=[])
    campos_opcionais = Column(JSONB, nullable=False, default=[])
    validacoes = Column(JSONB, nullable=False, default={})
    layout = Column(JSONB, nullable=False, default={})
    
    # Verso
    versao = Column(Integer, default=1)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Auditoria
    criado_por = Column(Integer)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'natureza_id', 'versao', name='uk_tenant_natureza_versao'),
    )
