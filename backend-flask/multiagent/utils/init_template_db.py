"""
Utilitários para inicialização de dados de templates no banco de dados.
"""
import logging
import os
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models import db

logger = logging.getLogger(__name__)

def init_categorias_templates():
    """
    Inicializa as categorias de templates no banco de dados se não existirem.
    """
    logger.info("Inicializando categorias de templates...")
    
    # Verifica se já existem categorias
    from sqlalchemy import text, exc
    
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM categoria_template"))
        count = result.scalar()
        
        if count and count > 0:
            logger.info(f"Já existem {count} categorias de templates. Pulando inicialização.")
            return
    except (exc.ProgrammingError, exc.OperationalError) as e:
        # A tabela não existe ainda, vamos apenas registrar e continuar
        logger.warning(f"A tabela categoria_template não existe. Pulando inicialização. Erro: {str(e)}")
        return
    
    # Categorias padrão
    categorias = [
        {
            'nome': 'Geral',
            'descricao': 'Templates gerais para processamento de documentos',
            'icone': 'fa-file-alt',
            'cor': '#3498db',
            'ordem': 1,
            'ativa': True
        },
        {
            'nome': 'Jurídico',
            'descricao': 'Templates para análise de documentos jurídicos',
            'icone': 'fa-balance-scale',
            'cor': '#2c3e50',
            'ordem': 2,
            'ativa': True
        },
        {
            'nome': 'Financeiro',
            'descricao': 'Templates para análise de documentos financeiros',
            'icone': 'fa-money-bill-wave',
            'cor': '#27ae60',
            'ordem': 3,
            'ativa': True
        },
        {
            'nome': 'Comercial',
            'descricao': 'Templates para análise de contratos comerciais',
            'icone': 'fa-handshake',
            'cor': '#e67e22',
            'ordem': 4,
            'ativa': True
        },
        {
            'nome': 'Personalizado',
            'descricao': 'Templates criados pelo usuário',
            'icone': 'fa-user-edit',
            'cor': '#9b59b6',
            'ordem': 5,
            'ativa': True
        }
    ]
    
    try:
        # Insere as categorias no banco de dados
        for categoria in categorias:
            now = datetime.now()
            insert_query = text("""
                INSERT INTO categoria_template 
                (nome, descricao, icone, cor, ordem, ativa, data_criacao, data_modificacao)
                VALUES (:nome, :descricao, :icone, :cor, :ordem, :ativa, :data_criacao, :data_modificacao)
            """)
            
            db.session.execute(insert_query, {
                'nome': categoria['nome'],
                'descricao': categoria['descricao'],
                'icone': categoria['icone'],
                'cor': categoria['cor'],
                'ordem': categoria['ordem'],
                'ativa': categoria['ativa'],
                'data_criacao': now,
                'data_modificacao': now
            })
        
        db.session.commit()
        logger.info(f"Categorias de templates inicializadas com sucesso: {len(categorias)} categorias")
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro ao inicializar categorias de templates: {str(e)}")
        raise

def init_templates_padroes():
    """
    Inicializa templates padrão no sistema.
    Cria o arquivo JSON com templates pré-configurados.
    """
    from multiagent.templates import ARQUIVO_TEMPLATES_SISTEMA
    
    # Verifica se o arquivo já existe
    if os.path.exists(ARQUIVO_TEMPLATES_SISTEMA):
        logger.info(f"Arquivo de templates do sistema já existe: {ARQUIVO_TEMPLATES_SISTEMA}")
        return
    
    # Templates padrão
    templates = {
        "templates": [
            {
                "id": "template_extrator",
                "nome": "Extrator de Texto",
                "descricao": "Extrai o conteúdo principal de documentos, removendo elementos irrelevantes",
                "tipo": "extrator",
                "categoria": "Geral",
                "customizado": False,
                "data_criacao": datetime.now().isoformat(),
                "prompt_sistema": "Você é um assistente especializado em extrair o conteúdo principal e relevante de documentos. Remova cabeçalhos, rodapés, metadados e outros elementos não essenciais, mantendo apenas o texto principal.",
                "prompt_usuario": "Extraia o conteúdo principal do seguinte texto, removendo elementos irrelevantes como cabeçalhos, rodapés, números de página e metadados:",
                "configuracoes": {
                    "temperatura": 0.2,
                    "modelo_preferido": "gpt-4o"
                }
            },
            {
                "id": "template_classificador",
                "nome": "Classificador de Documentos",
                "descricao": "Classifica documentos por tipo, área e conteúdo",
                "tipo": "classificador",
                "categoria": "Geral",
                "customizado": False,
                "data_criacao": datetime.now().isoformat(),
                "prompt_sistema": "Você é um assistente especializado em classificar documentos por tipo, área e conteúdo. Analise cuidadosamente o texto fornecido e determine sua categoria principal e subcategorias, se aplicável.",
                "prompt_usuario": "Classifique o seguinte documento, identificando seu tipo principal (ex: contrato, relatório, parecer) e área específica (ex: jurídico, financeiro, administrativo):",
                "configuracoes": {
                    "temperatura": 0.3,
                    "modelo_preferido": "gpt-4o"
                }
            },
            {
                "id": "template_analisador_juridico",
                "nome": "Analisador Jurídico",
                "descricao": "Analisa documentos jurídicos, identificando cláusulas importantes e riscos",
                "tipo": "analisador",
                "categoria": "Jurídico",
                "customizado": False,
                "data_criacao": datetime.now().isoformat(),
                "prompt_sistema": "Você é um especialista jurídico com ampla experiência em análise de documentos legais. Sua função é analisar cuidadosamente o texto fornecido, identificar cláusulas importantes, riscos potenciais e inconsistências no documento.",
                "prompt_usuario": "Analise este documento jurídico, destacando as principais cláusulas, identificando possíveis riscos legais e sugerindo melhorias:",
                "configuracoes": {
                    "temperatura": 0.3,
                    "modelo_preferido": "gpt-4o"
                }
            },
            {
                "id": "template_sintetizador",
                "nome": "Sintetizador de Documentos",
                "descricao": "Cria resumos concisos e estruturados de documentos extensos",
                "tipo": "sintetizador",
                "categoria": "Geral",
                "customizado": False,
                "data_criacao": datetime.now().isoformat(),
                "prompt_sistema": "Você é um especialista em criação de resumos executivos. Sua função é analisar documentos extensos e criar sínteses concisas que capturam os pontos essenciais, mantendo a estrutura lógica e destacando informações críticas.",
                "prompt_usuario": "Sintetize o seguinte documento em um resumo estruturado, destacando os pontos principais e mantendo a essência do conteúdo:",
                "configuracoes": {
                    "temperatura": 0.4,
                    "modelo_preferido": "gpt-4o"
                }
            },
            {
                "id": "template_formatador",
                "nome": "Formatador de Documentos",
                "descricao": "Melhora a formatação e estrutura de textos para maior clareza",
                "tipo": "formatador",
                "categoria": "Geral",
                "customizado": False,
                "data_criacao": datetime.now().isoformat(),
                "prompt_sistema": "Você é um especialista em formatação e estruturação de documentos. Sua função é reorganizar e reformatar conteúdos para melhorar a clareza, legibilidade e apresentação, sem alterar o significado essencial.",
                "prompt_usuario": "Reformate e reestruture o seguinte texto para melhorar sua apresentação e legibilidade, adicionando seções, parágrafos e marcadores onde apropriado:",
                "configuracoes": {
                    "temperatura": 0.3,
                    "modelo_preferido": "gpt-4o"
                }
            }
        ]
    }
    
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(ARQUIVO_TEMPLATES_SISTEMA), exist_ok=True)
    
    # Salva o arquivo
    try:
        with open(ARQUIVO_TEMPLATES_SISTEMA, 'w', encoding='utf-8') as f:
            # Convertemos os objetos datetime para string antes de serializar para JSON
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Arquivo de templates do sistema criado com sucesso: {ARQUIVO_TEMPLATES_SISTEMA}")
        logger.info(f"Total de templates padrão criados: {len(templates['templates'])}")
    
    except Exception as e:
        logger.error(f"Erro ao criar arquivo de templates do sistema: {str(e)}")
        raise

def inicializar_dados_templates():
    """
    Inicializa todos os dados de templates.
    """
    logger.info("Inicializando dados de templates...")
    
    try:
        # Inicializa categorias
        init_categorias_templates()
        
        # Inicializa templates padrão
        init_templates_padroes()
        
        logger.info("Inicialização de dados de templates concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar dados de templates: {str(e)}")
        raise