"""
Modelos de banco de dados para Templates de Documentos Jurídicos
"""

from main import db
from datetime import datetime
from sqlalchemy import Text, JSON


class CategoriaDocumento(db.Model):
    """Categorias dos templates de documentos jurídicos"""
    __tablename__ = 'categorias_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    icone = db.Column(db.String(50), default='fas fa-folder')
    cor_tema = db.Column(db.String(7), default='#007bff')  # Código hexadecimal da cor
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    templates = db.relationship('TemplateDocumento', backref='categoria', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CategoriaDocumento {self.nome}>'


class TemplateDocumento(db.Model):
    """Templates de documentos jurídicos migrados da rota /juridico/especialistas"""
    __tablename__ = 'templates_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_documento.id'), nullable=False)
    
    # Dados migrados dos templates originais
    template_original_id = db.Column(db.Integer)  # ID do template original
    modulo_origem = db.Column(db.String(50))  # criminal, empresarial, bancario, etc.
    modulo_nome = db.Column(db.String(100))  # Nome completo do módulo
    area_juridica = db.Column(db.String(50))  # Área jurídica específica
    
    # Metadados do template
    icone = db.Column(db.String(50), default='fas fa-file-alt')
    tipo_documento = db.Column(db.String(100))  # Tipo do documento gerado
    complexidade = db.Column(db.String(20), default='media')  # basica, media, avancada
    
    # Campos e estrutura do template
    campos_obrigatorios = db.Column(JSON)  # Lista de campos obrigatórios
    campos_opcionais = db.Column(JSON)  # Lista de campos opcionais
    estrutura_template = db.Column(Text)  # Estrutura HTML/texto do template
    
    # Conteúdo do template
    conteudo_template = db.Column(Text)  # Conteúdo base do template
    variaveis_template = db.Column(JSON)  # Variáveis disponíveis no template
    
    # Configurações de uso
    requer_assinatura = db.Column(db.Boolean, default=False)
    permite_edicao = db.Column(db.Boolean, default=True)
    versao = db.Column(db.String(10), default='1.0')
    
    # Estatísticas de uso
    total_utilizacoes = db.Column(db.Integer, default=0)
    ultima_utilizacao = db.Column(db.DateTime)
    
    # Metadados do sistema
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relacionamentos
    historico = db.relationship('HistoricoDocumento', backref='template', lazy=True)
    
    def incrementar_uso(self):
        """Incrementa contador de uso do template"""
        self.total_utilizacoes = (self.total_utilizacoes or 0) + 1
        self.ultima_utilizacao = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Converte template para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'categoria': self.categoria.nome if self.categoria else None,
            'modulo_origem': self.modulo_origem,
            'modulo_nome': self.modulo_nome,
            'area_juridica': self.area_juridica,
            'icone': self.icone,
            'tipo_documento': self.tipo_documento,
            'complexidade': self.complexidade,
            'campos_obrigatorios': self.campos_obrigatorios,
            'campos_opcionais': self.campos_opcionais,
            'total_utilizacoes': self.total_utilizacoes,
            'ultima_utilizacao': self.ultima_utilizacao.isoformat() if self.ultima_utilizacao else None,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
    
    def __repr__(self):
        return f'<TemplateDocumento {self.nome}>'


class HistoricoDocumento(db.Model):
    """Histórico de documentos gerados a partir dos templates"""
    __tablename__ = 'historico_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('templates_documento.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Dados do documento gerado
    titulo_documento = db.Column(db.String(300), nullable=False)
    formato_exportacao = db.Column(db.String(10), default='pdf')  # pdf, docx, html
    tamanho_arquivo = db.Column(db.Integer)  # em bytes
    
    # Dados utilizados na geração
    campos_preenchidos = db.Column(JSON)  # Valores dos campos preenchidos
    configuracoes_geracao = db.Column(JSON)  # Configurações específicas da geração
    
    # Metadados da geração
    ip_usuario = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Status do documento
    status = db.Column(db.String(20), default='gerado')  # gerado, baixado, enviado, arquivado
    caminho_arquivo = db.Column(db.String(500))  # Caminho do arquivo gerado (se armazenado)
    
    # Timestamps
    gerado_em = db.Column(db.DateTime, default=datetime.utcnow)
    baixado_em = db.Column(db.DateTime)
    
    # Relacionamentos
    usuario = db.relationship('User', backref='documentos_gerados')
    
    def marcar_como_baixado(self):
        """Marca documento como baixado"""
        self.status = 'baixado'
        self.baixado_em = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Converte histórico para dicionário"""
        return {
            'id': self.id,
            'template_nome': self.template.nome if self.template else None,
            'titulo_documento': self.titulo_documento,
            'formato_exportacao': self.formato_exportacao,
            'tamanho_arquivo': self.tamanho_arquivo,
            'status': self.status,
            'gerado_em': self.gerado_em.isoformat() if self.gerado_em else None,
            'baixado_em': self.baixado_em.isoformat() if self.baixado_em else None
        }
    
    def __repr__(self):
        return f'<HistoricoDocumento {self.titulo_documento}>'