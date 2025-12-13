#!/usr/bin/env python3
"""
Script para adicionar os 12 models faltantes ao models.py
"""

MODELS_TO_ADD = '''

# ============================================================================
# MODELS ADICIONAIS - 12 Tabelas do Schema Original
# ============================================================================

class AgenteConexoes(db.Model):
    """
    Modelo para conexões entre agentes (sistema multi-agente).
    Gerencia colaboração e referências entre agentes especializados.
    """
    __tablename__ = 'agente_conexoes'
    
    id = Column(Integer, primary_key=True)
    agente_origem_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=True)
    agente_destino_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=True)
    tipo_conexao = Column(String(50), nullable=False)  # inter_area, colaboracao, referencia
    peso_confianca = Column(Numeric, default=1.0)
    areas_colaboracao = Column(ARRAY(String), nullable=True)
    descricao_conexao = Column(Text, nullable=True)
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relationships
    agente_origem = relationship("AgenteJuridico", foreign_keys=[agente_origem_id], backref="conexoes_origem")
    agente_destino = relationship("AgenteJuridico", foreign_keys=[agente_destino_id], backref="conexoes_destino")


class AgenteMensagens(db.Model):
    """
    Modelo para mensagens entre agentes no sistema multi-agente.
    """
    __tablename__ = 'agente_mensagens'
    
    id = Column(Integer, primary_key=True)
    agente_origem_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=True)
    agente_destino_id = Column(Integer, ForeignKey('agente_juridico.id'), nullable=True)
    tipo_mensagem = Column(String(50), nullable=True)  # consulta, resposta, notificacao
    conteudo_mensagem = Column(Text, nullable=True)
    prioridade = Column(String(20), default='normal')  # alta, normal, baixa
    lida = Column(Boolean, default=False)
    data_envio = Column(DateTime, default=datetime.datetime.now)
    data_leitura = Column(DateTime, nullable=True)
    
    # Relationships
    agente_origem = relationship("AgenteJuridico", foreign_keys=[agente_origem_id], backref="mensagens_enviadas")
    agente_destino = relationship("AgenteJuridico", foreign_keys=[agente_destino_id], backref="mensagens_recebidas")


class AudioTranscriptions(db.Model):
    """
    Modelo para transcrições de áudio.
    """
    __tablename__ = 'audio_transcriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    filename = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    status = Column(String(20), default='processing')  # processing, completed, failed
    transcript_text = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    speaker_detection = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", backref="audio_transcriptions")


class CadastroClientes(db.Model):
    """
    Modelo para cadastro de clientes do escritório.
    """
    __tablename__ = 'cadastro_clientes'
    
    id = Column(Integer, primary_key=True)
    tipo_pessoa = Column(String(20), nullable=True)  # fisica, juridica
    nome_completo = Column(Text, nullable=True)
    cpf = Column(String(14), nullable=True)
    cnpj = Column(String(18), nullable=True)
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    endereco = Column(Text, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.datetime.now)
    ativo = Column(Boolean, default=True)


class ConfiguracoesGlobalAgente(db.Model):
    """
    Modelo para configurações globais dos agentes.
    """
    __tablename__ = 'configuracoes_global_agente'
    
    id = Column(Integer, primary_key=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=True)
    tipo_dado = Column(String(20), nullable=True)  # texto, json, numero, boolean
    descricao = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    editavel = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class FluxoResultado(db.Model):
    """
    Modelo para resultados de execução de fluxos.
    """
    __tablename__ = 'fluxo_resultado'
    
    id = Column(Integer, primary_key=True)
    fluxo_id = Column(Integer, ForeignKey('fluxo.id'), nullable=True)
    execucao_id = Column(Integer, ForeignKey('execucao_fluxo.id'), nullable=True)
    resultado_json = Column(JSON, nullable=True)
    tempo_execucao = Column(Float, nullable=True)
    status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    fluxo = relationship("FluxoModel", backref="resultados")
    execucao = relationship("ExecucaoFluxo", backref="resultados")


class LegalDesignPieces(db.Model):
    """
    Modelo para peças do Legal Design Pro.
    """
    __tablename__ = 'legal_design_pieces'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    tipo_peca = Column(String(50), nullable=True)
    conteudo = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    template_base_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class PerfisProfissionais(db.Model):
    """
    Modelo para perfis profissionais de advogados.
    """
    __tablename__ = 'perfis_profissionais'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    nome_completo = Column(String(255), nullable=True)
    oab_numero = Column(String(20), nullable=True)
    oab_uf = Column(String(2), nullable=True)
    especializacao = Column(ARRAY(String), nullable=True)
    areas_atuacao = Column(ARRAY(String), nullable=True)
    biografia = Column(Text, nullable=True)
    foto_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    user = relationship("User", backref="perfil_profissional")


class PropriedadesRurais(db.Model):
    """
    Modelo para propriedades rurais (Direito Agrário).
    """
    __tablename__ = 'propriedades_rurais'
    
    id = Column(Integer, primary_key=True)
    nome_propriedade = Column(String(255), nullable=True)
    matricula = Column(String(50), nullable=True)
    area_hectares = Column(Numeric, nullable=True)
    municipio = Column(String(100), nullable=True)
    uf = Column(String(2), nullable=True)
    ccir = Column(String(20), nullable=True)  # Certificado de Cadastro de Imóvel Rural
    car = Column(String(20), nullable=True)  # Cadastro Ambiental Rural
    proprietario_nome = Column(String(255), nullable=True)
    proprietario_cpf = Column(String(14), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class SessoesColaborativas(db.Model):
    """
    Modelo para sessões colaborativas entre usuários.
    """
    __tablename__ = 'sessoes_colaborativas'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=True)
    descricao = Column(Text, nullable=True)
    criador_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    status = Column(String(20), default='ativa')  # ativa, pausada, finalizada
    data_inicio = Column(DateTime, default=datetime.datetime.now)
    data_fim = Column(DateTime, nullable=True)
    participantes_ids = Column(ARRAY(Integer), nullable=True)
    
    criador = relationship("User", backref="sessoes_criadas")


class TonsVoz(db.Model):
    """
    Modelo para tons de voz dos assistentes jurídicos.
    """
    __tablename__ = 'tons_voz'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)
    instrucao_prompt = Column(Text, nullable=True)
    velocidade_resposta = Column(String(20), default='normal')  # rapida, normal, detalhada
    estrutura_resposta = Column(String(20), default='topicos')  # linear, organizada, topicos
    nivel_detalhe = Column(String(20), default='equilibrado')  # conciso, equilibrado, completo
    icone = Column(String(50), nullable=True)
    cor_secundaria = Column(String(20), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class TranscricoesAudio(db.Model):
    """
    Modelo para transcrições de áudio (sistema completo).
    """
    __tablename__ = 'transcricoes_audio'
    
    id = Column(String(255), primary_key=True)
    filename = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    status = Column(String(20), default='processing')
    speaker_detection = Column(Boolean, default=True)
    speaker_count = Column(Integer, default=15)
    transcript_data = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.now)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    user = relationship("User", backref="transcricoes_audio")

'''

print("Models gerados com sucesso!")
print("\nAdicione o seguinte código ao final de models.py:")
print(MODELS_TO_ADD)
