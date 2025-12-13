"""
Módulo para gerenciamento de prompts do assistente.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float,
    create_engine, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configurar logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Definir base para modelos
Base = declarative_base()

# Modelo de dados para prompt template
class PromptTemplate(Base):
    __tablename__ = 'assistente_prompt_templates'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(500))
    modelo_llm = Column(String(100), nullable=False)  # openai/gpt-4o, anthropic/claude-3, etc.
    template_sistema = Column(Text, nullable=False)
    contexto_padrao = Column(Text)
    config_json = Column(Text, default='{}')
    temperatura = Column(Float, default=0.7)
    top_p = Column(Float, default=0.9)
    top_k = Column(Integer, default=40)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    criado_por = Column(String(100))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'modelo_llm': self.modelo_llm,
            'template_sistema': self.template_sistema,
            'contexto_padrao': self.contexto_padrao,
            'config_json': self.config_json,
            'temperatura': self.temperatura,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'criado_por': self.criado_por
        }


# Inicializar o banco de dados
def init_db():
    """Inicializa o banco de dados e retorna uma sessão"""
    # Obter a URL do banco de dados das variáveis de ambiente
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL não encontrada nas variáveis de ambiente")
        return None
    
    # Criar engine
    engine = create_engine(database_url)
    
    # Criar tabelas se não existirem
    Base.metadata.create_all(engine)
    
    # Criar sessão
    Session = sessionmaker(bind=engine)
    return Session()


# Inicializar prompts padrão
def inicializar_prompts_padrao():
    """Inicializa prompts padrão para os diferentes modelos se não existirem"""
    try:
        db_session = init_db()
        if not db_session:
            logger.error("Não foi possível inicializar o banco de dados")
            return False
        
        # Verificar se já existem prompts
        prompts_existentes = db_session.query(PromptTemplate).count()
        
        if prompts_existentes == 0:
            logger.info("Inicializando prompts padrão...")
            
            # Definir templates para cada modelo
            templates = [
                {
                    "nome": "OpenAI GPT-4o - Prompt Jurídico Técnico",
                    "descricao": "Template técnico para consultas jurídicas usando o GPT-4o",
                    "modelo_llm": "openai/gpt-4o",
                    "template_sistema": """Você é um assistente jurídico altamente especializado usando o modelo GPT-4o.

Ao responder consultas jurídicas, siga estas diretrizes:

1. Forneça análises técnicas precisas com fundamentação legal específica.
2. Cite artigos de lei, súmulas e jurisprudência relevantes com seus números e fontes exatas.
3. Estruture respostas em tópicos numerados para facilitar a compreensão.
4. Mantenha o foco técnico-jurídico, evitando generalizações e simplificações excessivas.
5. Utilize terminologia jurídica precisa e apropriada.
6. Quando cabível, mencione posições doutrinárias relevantes e atuais.
7. Indique expressamente quando houver divergência jurisprudencial sobre o tema.
8. Para consultas vagas ou genéricas, solicite especificações sobre a área jurídica e questão específica.

IMPORTANTE: Suas respostas não constituem aconselhamento jurídico formal e não substituem a consulta a um profissional juridicamente habilitado.""",
                    "contexto_padrao": "Análise baseada na legislação brasileira vigente e jurisprudência atual dos tribunais superiores.",
                    "ativo": True,
                    "criado_por": "sistema"
                },
                {
                    "nome": "Anthropic Claude 3.5 - Consultas Jurídicas",
                    "descricao": "Template para respostas jurídicas formais usando Claude 3.5",
                    "modelo_llm": "anthropic/claude-3-5-sonnet",
                    "template_sistema": """Você é um assistente jurídico especializado utilizando o modelo Claude 3.5 Sonnet.

Ao responder consultas jurídicas, você deve:

1. Priorizar precisão técnica com referências específicas às fontes legais aplicáveis.
2. Citar dispositivos legais, precedentes judiciais e súmulas com exatidão.
3. Explicar conceitos jurídicos com clareza, mantendo o rigor técnico apropriado.
4. Organizar respostas em tópicos claramente identificados quando aplicável.
5. Incluir referências a doutrina jurídica relevante quando apropriado.
6. Apresentar perspectivas jurídicas divergentes quando existirem.
7. Solicitar esclarecimentos quando a consulta for imprecisa ou insuficiente.

Suas análises devem refletir o estado atual do ordenamento jurídico brasileiro, incluindo legislação vigente e entendimentos jurisprudenciais consolidados.

IMPORTANTE: Suas respostas não constituem parecer jurídico formal e não substituem a consulta a profissionais habilitados.""",
                    "contexto_padrao": "Análise fundamentada no ordenamento jurídico brasileiro e jurisprudência dos tribunais superiores.",
                    "ativo": True,
                    "criado_por": "sistema"
                },
                {
                    "nome": "DeepSeek - Respostas Jurídicas",
                    "descricao": "Template para consultas ao modelo DeepSeek",
                    "modelo_llm": "deepseek/deepseek-chat",
                    "template_sistema": """Você é um assistente jurídico especialista trabalhando com o modelo DeepSeek.

Ao responder consultas jurídicas, você deve:

1. Fornecer análises técnicas com fundamentação normativa precisa.
2. Citar dispositivos legais e precedentes judiciais com seus números e fontes exatas.
3. Estruturar respostas em tópicos numerados para facilitar a compreensão.
4. Utilizar linguagem técnica apropriada, evitando generalizações e simplificações excessivas.
5. Incluir referências a publicações doutrinárias relevantes.
6. Indicar quando houver controvérsia jurídica sobre o tema.
7. Contextualizar as informações considerando a legislação brasileira atual.

Para consultas vagas ou genéricas, solicite ao usuário que especifique área jurídica, questão específica e contexto relevante.

IMPORTANTE: Suas respostas têm finalidade informativa e não constituem assessoria jurídica formal. Questões práticas devem ser avaliadas por profissionais habilitados.""",
                    "contexto_padrao": "Análise baseada na legislação brasileira e jurisprudência atual.",
                    "ativo": True,
                    "criado_por": "sistema"
                }
            ]
            
            # Inserir templates no banco de dados
            for template_data in templates:
                template = PromptTemplate(**template_data)
                db_session.add(template)
            
            db_session.commit()
            logger.info(f"Foram inicializados {len(templates)} prompts padrão")
            return True
        else:
            logger.info(f"Já existem {prompts_existentes} prompts cadastrados. Pulando inicialização.")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao inicializar prompts padrão: {e}")
        if db_session:
            db_session.rollback()
        return False
    finally:
        if db_session:
            db_session.close()


# Funções de acesso aos prompts
def obter_todos_prompts() -> list:
    """Retorna todos os templates de prompt cadastrados"""
    try:
        db_session = init_db()
        if not db_session:
            return []
        
        prompts = db_session.query(PromptTemplate).filter_by(ativo=True).all()
        return [prompt.to_dict() for prompt in prompts]
    except Exception as e:
        logger.error(f"Erro ao obter prompts: {e}")
        return []
    finally:
        if db_session:
            db_session.close()


def obter_prompt_por_modelo(modelo_llm: str) -> Optional[Dict[str, Any]]:
    """Obtém o template de prompt para um modelo específico"""
    try:
        db_session = init_db()
        if not db_session:
            return None
        
        prompt = db_session.query(PromptTemplate).filter_by(
            modelo_llm=modelo_llm, 
            ativo=True
        ).first()
        
        if prompt:
            return prompt.to_dict()
        return None
    except Exception as e:
        logger.error(f"Erro ao obter prompt para modelo {modelo_llm}: {e}")
        return None
    finally:
        if db_session:
            db_session.close()


def salvar_prompt(dados_prompt: Dict[str, Any]) -> Optional[int]:
    """Salva ou atualiza um template de prompt"""
    try:
        db_session = init_db()
        if not db_session:
            return None
        
        # Verificar se é uma atualização ou criação
        prompt_id = dados_prompt.get('id')
        if prompt_id:
            # Atualização
            prompt = db_session.query(PromptTemplate).get(prompt_id)
            if not prompt:
                logger.error(f"Prompt com ID {prompt_id} não encontrado")
                return None
            
            # Atualizar campos
            for key, value in dados_prompt.items():
                if key != 'id' and hasattr(prompt, key):
                    setattr(prompt, key, value)
            
            prompt.atualizado_em = datetime.now()
        else:
            # Criação
            prompt = PromptTemplate(**dados_prompt)
            db_session.add(prompt)
        
        db_session.commit()
        return prompt.id
    except Exception as e:
        logger.error(f"Erro ao salvar prompt: {e}")
        if db_session:
            db_session.rollback()
        return None
    finally:
        if db_session:
            db_session.close()


def excluir_prompt(prompt_id: int) -> bool:
    """Exclui um template de prompt (exclusão lógica)"""
    try:
        db_session = init_db()
        if not db_session:
            return False
        
        prompt = db_session.query(PromptTemplate).get(prompt_id)
        if not prompt:
            logger.error(f"Prompt com ID {prompt_id} não encontrado")
            return False
        
        # Exclusão lógica
        prompt.ativo = False
        prompt.atualizado_em = datetime.now()
        
        db_session.commit()
        return True
    except Exception as e:
        logger.error(f"Erro ao excluir prompt: {e}")
        if db_session:
            db_session.rollback()
        return False
    finally:
        if db_session:
            db_session.close()


# Função principal para uso em outros módulos
def obter_sistema_prompt(modelo_llm: str, personalidade: str = "", tom_voz: str = "") -> str:
    """
    Obtém o prompt de sistema para o modelo especificado,
    ajustando para personalidade e tom de voz se necessário
    
    Args:
        modelo_llm: ID do modelo (formato: 'provedor/modelo')
        personalidade: Personalidade do assistente (opcional)
        tom_voz: Tom de voz do assistente (opcional)
        
    Returns:
        Prompt de sistema formatado
    """
    prompt_template = obter_prompt_por_modelo(modelo_llm)
    
    if not prompt_template:
        # Fallback para um prompt genérico caso não encontre o modelo
        return """Você é um assistente jurídico especializado.
Forneça análises técnicas precisas com fundamentação legal específica.
Cite artigos de lei e jurisprudência relevantes quando aplicável."""
    
    sistema_prompt = prompt_template['template_sistema']
    
    # Adicionar personalização com base na personalidade
    if personalidade:
        personalidade = personalidade.lower()
        if personalidade == 'advogado':
            sistema_prompt += "\n\nAo responder, adote a perspectiva de um advogado experiente, considerando a defesa de direitos e a interpretação favorável das normas ao cliente, sem comprometer a exatidão técnica."
        elif personalidade == 'juiz':
            sistema_prompt += "\n\nAo responder, adote a perspectiva de um juiz, priorizando a imparcialidade, a aplicação equilibrada das normas e a avaliação ponderada dos argumentos de ambas as partes."
        elif personalidade == 'promotor':
            sistema_prompt += "\n\nAo responder, adote a perspectiva de um membro do Ministério Público, priorizando o interesse público, a defesa da ordem jurídica e a aplicação correta da lei."
        elif personalidade == 'professor':
            sistema_prompt += "\n\nAo responder, adote a perspectiva de um professor de direito, explicando conceitos com clareza, contextualizando historicamente e teoricamente, e fazendo referências a doutrinas e escolas de pensamento jurídico quando relevante."
        elif personalidade == 'pesquisador':
            sistema_prompt += "\n\nAo responder, adote a perspectiva de um pesquisador jurídico, priorizando a precisão científica, citando fontes acadêmicas, apresentando diferentes correntes doutrinárias e análises comparativas quando pertinente."
    
    # Adicionar personalização com base no tom de voz
    if tom_voz:
        tom_voz = tom_voz.lower()
        if tom_voz == 'formal':
            sistema_prompt += "\n\nUtilize linguagem formal e técnica, com terminologia jurídica precisa e construções textuais próprias do discurso jurídico acadêmico."
        elif tom_voz == 'natural':
            sistema_prompt += "\n\nUtilize linguagem natural e acessível, mantendo a precisão técnica, mas facilitando a compreensão por parte de profissionais e não-especialistas."
        elif tom_voz == 'simples':
            sistema_prompt += "\n\nUtilize linguagem simplificada, explicando conceitos jurídicos em termos acessíveis, com analogias e exemplos quando necessário, sem perder a precisão técnica."
        elif tom_voz == 'didático':
            sistema_prompt += "\n\nUtilize linguagem didática e estruturada, com explicações passo a passo, definições claras dos termos técnicos, exemplos práticos e resumos dos pontos principais ao final."
        elif tom_voz == 'conciso':
            sistema_prompt += "\n\nUtilize linguagem concisa e direta, focando nos pontos essenciais, evitando digressões e apresentando conclusões claras e objetivas no início da resposta."
    
    return sistema_prompt


# Para inicializar automaticamente na importação
if __name__ != "__main__":
    try:
        inicializar_prompts_padrao()
    except Exception as e:
        logger.error(f"Erro ao inicializar módulo de prompts: {e}")