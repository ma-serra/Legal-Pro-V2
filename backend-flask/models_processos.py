
# ============================================================================
# SISTEMA DE PROCESSOS DINÂMICOS
# Adicionado em: 15 Dezembro 2025
# ============================================================================

class Processo(db.Model):
    """Tabela principal de processos jurídicos com campos dinâmicos"""
    __tablename__ = 'processos'
    
    id_processo = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    tenant_id = Column(Integer, nullable=True)
    
    # Dados Básicos
    numero_cnj = Column(String(25))
    pasta = Column(String(50))
    status_id = Column(Integer)
    natureza_id = Column(Integer)
    
    # Cliente
    cliente_id = Column(Integer)
    posicao_cliente_id = Column(Integer)
    
    # Classificação Jurídica
    acao_id = Column(Integer)
    procedimento_id = Column(Integer)
    fase_id = Column(Integer)
    
    # Localização Processual
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
    
    # Prognóstico
    tipo_probabilidade_id = Column(Integer)
    risco_id = Column(Integer)
    
    # Partes (autor e réu)
    autor = Column(String(255))
    reu = Column(String(255))
    
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
        """Serialização básica"""
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
    """Campos específicos por natureza armazenados em JSONB"""
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
    """Teses jurídicas tributárias"""
    __tablename__ = 'teses_tributarias'
    
    id_tese = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    descricao = Column(Text)
    tributo_id = Column(Integer, ForeignKey('tributos.id_tributo'))
    
    # Jurisprudência
    tema_repercussao_geral = Column(String(50))
    tema_repetitivo = Column(String(50))
    tribunal_origem = Column(String(100))
    
    # Prognóstico padrão
    probabilidade_sucesso = Column(Numeric(5, 2))
    fundamentacao = Column(Text)
    situacao = Column(String(50))  # Favorável, Desfavorável, Pendente, Superada
    
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
    """Dados específicos de processos tributários"""
    __tablename__ = 'processo_tributario'
    
    id_processo_tributario = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Tributo
    tributo_id = Column(Integer, ForeignKey('tributos.id_tributo'))
    
    # Documentos Fiscais
    numero_aiim = Column(String(100))
    numero_cda = Column(String(100))
    data_lancamento = Column(DateTime)
    
    # Valores Específicos
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
    """Relacionamento N:N entre processos e teses tributárias"""
    __tablename__ = 'processo_tese'
    
    id_processo_tese = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False)
    tese_id = Column(Integer, ForeignKey('teses_tributarias.id_tese', ondelete='CASCADE'), nullable=False)
    
    # Ordem de importância
    ordem = Column(Integer, default=1)
    status = Column(String(50))  # Aguardando, Em análise, Aceita, Rejeitada
    
    data_vinculacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    processo = relationship('Processo', back_populates='teses')
    tese = relationship('TeseTributaria', back_populates='processos')
    
    __table_args__ = (
        UniqueConstraint('processo_id', 'tese_id', name='uk_processo_tese'),
    )


class ProcessoPrognosticoTributario(db.Model):
    """Prognóstico detalhado para processos tributários"""
    __tablename__ = 'processo_prognostico_tributario'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_tributario.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Êxito Provável (70%)
    tese_provavel_id = Column(Integer, ForeignKey('teses_tributarias.id_tese'))
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # Êxito Possível (50%)
    tese_possivel_id = Column(Integer, ForeignKey('teses_tributarias.id_tese'))
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # Êxito Remoto (25%)
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
    """Dados específicos de processos trabalhistas"""
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
    """Prognóstico para processos trabalhistas"""
    __tablename__ = 'processo_prognostico_trabalhista'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_trabalhista.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Êxito Provável
    tese_provavel = Column(Text)
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # Êxito Possível
    tese_possivel = Column(Text)
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # Êxito Remoto
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
    """Dados específicos de processos cíveis"""
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
    """Prognóstico para processos cíveis"""
    __tablename__ = 'processo_prognostico_civel'
    
    id_prognostico = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processo_civel.processo_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Êxito Provável
    tese_provavel = Column(Text)
    valor_provavel = Column(Numeric(18, 2))
    percentual_provavel = Column(Numeric(5, 2), default=70.00)
    
    # Êxito Possível
    tese_possivel = Column(Text)
    valor_possivel = Column(Numeric(18, 2))
    percentual_possivel = Column(Numeric(5, 2), default=50.00)
    
    # Êxito Remoto
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
    """Cadastro de índices de correção monetária"""
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
    """Histórico de valores dos índices monetários"""
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
    """Registro de atualizações monetárias realizadas"""
    __tablename__ = 'processo_atualizacao_monetaria'
    
    id_atualizacao = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey('processos.id_processo', ondelete='CASCADE'), nullable=False)
    
    # Configuração
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
    """Configuração dinâmica de formulários por natureza"""
    __tablename__ = 'configuracao_formulario'
    
    id_configuracao = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)
    natureza_id = Column(Integer)
    
    # Estrutura do formulário em JSON
    campos_obrigatorios = Column(JSONB, nullable=False, default=[])
    campos_opcionais = Column(JSONB, nullable=False, default=[])
    validacoes = Column(JSONB, nullable=False, default={})
    layout = Column(JSONB, nullable=False, default={})
    
    # Versão
    versao = Column(Integer, default=1)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Auditoria
    criado_por = Column(Integer)
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'natureza_id', 'versao', name='uk_tenant_natureza_versao'),
    )
