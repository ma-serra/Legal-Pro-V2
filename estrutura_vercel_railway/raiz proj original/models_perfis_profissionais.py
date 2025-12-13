"""
Modelos para Perfis Profissionais dos Agentes
Sistema de personalização de comportamento para todos os assistentes
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class PerfilProfissional(db.Model):
    __tablename__ = 'perfis_profissionais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)  # advogado, juiz, professor, promotor
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prompt_base = db.Column(db.Text, nullable=False)
    
    # Configurações de personalidade
    formalidade = db.Column(db.String(50), default='tecnico')  # formal, tecnico, acessivel
    autoridade = db.Column(db.String(50), default='especialista')  # autoridade, especialista, consultor
    empatia = db.Column(db.String(50), default='profissional')  # alta, profissional, objetiva
    
    # Metadados
    icone = db.Column(db.String(100), default='fas fa-user-tie')
    cor_primaria = db.Column(db.String(7), default='#3b576f')
    ativo = db.Column(db.Boolean, default=True)
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'prompt_base': self.prompt_base,
            'formalidade': self.formalidade,
            'autoridade': self.autoridade,
            'empatia': self.empatia,
            'icone': self.icone,
            'cor_primaria': self.cor_primaria,
            'ativo': self.ativo
        }

class TomVoz(db.Model):
    __tablename__ = 'tons_voz'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)  # objetivo, sistematico, natural
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    instrucao_prompt = db.Column(db.Text, nullable=False)
    
    # Configurações específicas
    velocidade_resposta = db.Column(db.String(50), default='normal')  # rapida, normal, detalhada
    estrutura_resposta = db.Column(db.String(50), default='organizada')  # linear, organizada, topicos
    nivel_detalhe = db.Column(db.String(50), default='equilibrado')  # conciso, equilibrado, completo
    
    # Metadados
    icone = db.Column(db.String(100), default='fas fa-volume-up')
    cor_secundaria = db.Column(db.String(7), default='#6c757d')
    ativo = db.Column(db.Boolean, default=True)
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'instrucao_prompt': self.instrucao_prompt,
            'velocidade_resposta': self.velocidade_resposta,
            'estrutura_resposta': self.estrutura_resposta,
            'nivel_detalhe': self.nivel_detalhe,
            'icone': self.icone,
            'cor_secundaria': self.cor_secundaria,
            'ativo': self.ativo
        }

class ConfiguracaoGlobalAgente(db.Model):
    __tablename__ = 'configuracoes_global_agente'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), default='texto')  # texto, json, numero, boolean
    categoria = db.Column(db.String(100), default='geral')
    
    # Controle
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_valor(self):
        """Retorna o valor convertido para o tipo adequado"""
        if self.tipo == 'json':
            return json.loads(self.valor)
        elif self.tipo == 'numero':
            return float(self.valor)
        elif self.tipo == 'boolean':
            return self.valor.lower() in ['true', '1', 'yes', 'sim']
        return self.valor
    
    def set_valor(self, novo_valor):
        """Define o valor convertendo para string"""
        if self.tipo == 'json':
            self.valor = json.dumps(novo_valor, ensure_ascii=False)
        else:
            self.valor = str(novo_valor)

# Função para inicializar dados padrão
def inicializar_perfis_padrao():
    """Inicializa perfis profissionais padrão"""
    perfis_padrao = [
        {
            'nome': 'advogado',
            'titulo': 'Advogado Experiente',
            'descricao': 'Profissional experiente em advocacia, focado em soluções práticas e estratégias processuais eficazes.',
            'prompt_base': 'Você é um(a) advogado(a) experiente em conversa técnica com colegas. Foque em aspectos práticos, estratégias processuais e soluções aplicáveis.',
            'formalidade': 'tecnico',
            'autoridade': 'especialista',
            'empatia': 'profissional',
            'icone': 'fas fa-balance-scale',
            'cor_primaria': '#2c5282'
        },
        {
            'nome': 'juiz',
            'titulo': 'Magistrado',
            'descricao': 'Magistrado experiente com foco na imparcialidade, fundamentação jurídica sólida e análise equilibrada.',
            'prompt_base': 'Você é um(a) magistrado(a) experiente fornecendo análise técnica imparcial. Mantenha neutralidade e foque na fundamentação legal.',
            'formalidade': 'formal',
            'autoridade': 'autoridade',
            'empatia': 'objetiva',
            'icone': 'fas fa-gavel',
            'cor_primaria': '#744210'
        },
        {
            'nome': 'professor',
            'titulo': 'Professor de Direito',
            'descricao': 'Acadêmico com visão didática e aprofundamento doutrinário, focado em análise teórica e conceitual.',
            'prompt_base': 'Você é um(a) professor(a) acadêmico(a) de Direito em discussão técnica. Forneça análise doutrinária aprofundada e contexto histórico.',
            'formalidade': 'tecnico',
            'autoridade': 'especialista',
            'empatia': 'alta',
            'icone': 'fas fa-graduation-cap',
            'cor_primaria': '#2d3748'
        },
        {
            'nome': 'promotor',
            'titulo': 'Promotor de Justiça',
            'descricao': 'Membro do Ministério Público com foco no interesse público, investigação e responsabilização.',
            'prompt_base': 'Você é um(a) promotor(a) do Ministério Público em análise técnica especializada. Foque no interesse público e na responsabilização.',
            'formalidade': 'formal',
            'autoridade': 'autoridade',
            'empatia': 'profissional',
            'icone': 'fas fa-shield-alt',
            'cor_primaria': '#c53030'
        }
    ]
    
    for perfil_data in perfis_padrao:
        perfil_existente = PerfilProfissional.query.filter_by(nome=perfil_data['nome']).first()
        if not perfil_existente:
            perfil = PerfilProfissional(**perfil_data)
            db.session.add(perfil)
    
    # Tons de voz padrão
    tons_padrao = [
        {
            'nome': 'objetivo',
            'titulo': 'Tom Objetivo',
            'descricao': 'Comunicação direta e objetiva, focada em resultados e conclusões práticas.',
            'instrucao_prompt': 'Seja direto e objetivo nas suas colocações técnicas. Vá direto ao ponto essencial.',
            'velocidade_resposta': 'rapida',
            'estrutura_resposta': 'linear',
            'nivel_detalhe': 'conciso',
            'icone': 'fas fa-bullseye',
            'cor_secundaria': '#e53e3e'
        },
        {
            'nome': 'sistematico',
            'titulo': 'Tom Sistemático',
            'descricao': 'Análise estruturada e organizada, com sequência lógica e fundamentação clara.',
            'instrucao_prompt': 'Estruture sua análise de forma sistemática e organizada. Use sequência lógica e fundamentação clara.',
            'velocidade_resposta': 'normal',
            'estrutura_resposta': 'organizada',
            'nivel_detalhe': 'equilibrado',
            'icone': 'fas fa-list-ol',
            'cor_secundaria': '#3182ce'
        },
        {
            'nome': 'natural',
            'titulo': 'Tom Natural',
            'descricao': 'Linguagem técnica mas fluida e conversacional, mantendo rigor jurídico.',
            'instrucao_prompt': 'Use linguagem técnica mas fluida e conversacional. Mantenha rigor jurídico com naturalidade.',
            'velocidade_resposta': 'normal',
            'estrutura_resposta': 'topicos',
            'nivel_detalhe': 'completo',
            'icone': 'fas fa-comments',
            'cor_secundaria': '#38a169'
        }
    ]
    
    for tom_data in tons_padrao:
        tom_existente = TomVoz.query.filter_by(nome=tom_data['nome']).first()
        if not tom_existente:
            tom = TomVoz(**tom_data)
            db.session.add(tom)
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inicializar perfis padrão: {e}")
        return False