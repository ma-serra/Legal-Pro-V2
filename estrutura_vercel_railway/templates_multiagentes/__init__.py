"""
Módulo para gerenciamento de templates de agentes.
"""
import os
import json
import logging
import uuid
from datetime import datetime

# Configuração de logging
logger = logging.getLogger('multiagent')

# Diretórios para templates
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_TEMPLATES_SISTEMA = DIRETORIO_BASE
DIRETORIO_TEMPLATES_CUSTOM = os.path.join(DIRETORIO_BASE, 'templates_customizados')
ARQUIVO_TEMPLATES_SISTEMA = os.path.join(DIRETORIO_TEMPLATES_SISTEMA, 'agentes_preconfigurados.json')

# Categorias padrão para templates
CATEGORIAS_PADRAO = [
    'geral',
    'juridico',
    'financeiro',
    'seguros',
    'contratos'
]

# Garante que o diretório de templates customizados existe
os.makedirs(DIRETORIO_TEMPLATES_CUSTOM, exist_ok=True)

def carregar_templates_agentes():
    """
    Carrega os templates de agentes disponíveis.
    
    Returns:
        Lista de templates
    """
    templates = []
    
    # Carrega templates do sistema
    try:
        if os.path.exists(ARQUIVO_TEMPLATES_SISTEMA):
            with open(ARQUIVO_TEMPLATES_SISTEMA, 'r', encoding='utf-8') as f:
                templates_sistema = json.load(f)
                
                # Se for um objeto com uma chave 'templates', extrai a lista
                if isinstance(templates_sistema, dict) and 'templates' in templates_sistema:
                    templates.extend(templates_sistema['templates'])
                # Senão, assume que é uma lista direta de templates
                elif isinstance(templates_sistema, list):
                    templates.extend(templates_sistema)
                    
                logger.info(f"Carregados {len(templates)} templates do sistema")
    except Exception as e:
        logger.error(f"Erro ao carregar templates do sistema: {str(e)}")
    
    # Carrega templates customizados
    try:
        for arquivo in os.listdir(DIRETORIO_TEMPLATES_CUSTOM):
            if arquivo.endswith('.json'):
                caminho_arquivo = os.path.join(DIRETORIO_TEMPLATES_CUSTOM, arquivo)
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        template['customizado'] = True
                        templates.append(template)
                except Exception as e:
                    logger.error(f"Erro ao carregar template customizado {arquivo}: {str(e)}")
        
        logger.info(f"Carregados {len(templates)} templates no total")
    except Exception as e:
        logger.error(f"Erro ao listar templates customizados: {str(e)}")
    
    return templates

def obter_template_por_id(template_id):
    """
    Obtém um template pelo ID.
    
    Args:
        template_id: ID do template
        
    Returns:
        Template (sempre como dicionário) ou None se não encontrado
    """
    if not template_id:
        return None
        
    # Carrega todos os templates
    templates = carregar_templates_agentes()
    
    # Busca pelo ID
    for template in templates:
        if isinstance(template, dict) and template.get('id') == template_id:
            return template
            
    # Tratamento especial para templates que podem estar em formato de string
    # Tentar converter para dicionário se possível
    try:
        import json
        for template in templates:
            if not isinstance(template, dict):
                # Verificar se é uma string JSON e tentar converter
                if isinstance(template, str):
                    try:
                        template_dict = json.loads(template)
                        if isinstance(template_dict, dict) and template_dict.get('id') == template_id:
                            return template_dict
                    except:
                        # Se não for possível converter, ignorar
                        pass
    except Exception as e:
        # Em caso de erro, apenas logar e continuar
        import logging
        logger = logging.getLogger('multiagent')
        logger.error(f"Erro ao processar template em formato de string: {str(e)}")
            
    # Se não encontrar, retorna um dicionário vazio com ID para evitar erros
    # É melhor retornar um dicionário vazio do que None para evitar erros 'str' object has no attribute 'get'
    return {
        'id': template_id,
        'nome': f'Template {template_id}',
        'descricao': 'Template não encontrado',
        'tipo': 'desconhecido',
        'categoria': 'não especificada',
        'prompt_template': {
            'sistema': 'Template não encontrado ou formato inválido.',
            'usuario': 'Template não encontrado ou formato inválido.'
        }
    }

def salvar_template(template):
    """
    Salva um template.
    
    Args:
        template: Dados do template
        
    Returns:
        ID do template salvo
    """
    if not template:
        raise ValueError("Dados do template não fornecidos")
        
    # Valida dados mínimos
    if not template.get('nome') or not template.get('tipo') or not template.get('prompt_template'):
        raise ValueError("Dados incompletos. Nome, tipo e prompt_template são obrigatórios")
        
    # Gera ID se não existir
    if not template.get('id'):
        template['id'] = f"custom_{uuid.uuid4().hex[:8]}"
        
    # Marca como customizado
    template['customizado'] = True
    
    # Formata o nome do arquivo
    nome_arquivo = f"{template['id']}.json"
    caminho_arquivo = os.path.join(DIRETORIO_TEMPLATES_CUSTOM, nome_arquivo)
    
    # Salva o arquivo
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Template {template['id']} salvo com sucesso em {caminho_arquivo}")
        return template['id']
    except Exception as e:
        logger.error(f"Erro ao salvar template: {str(e)}")
        raise

def salvar_template_customizado(template_data):
    """
    Salva um template customizado.
    
    Args:
        template_data: Dicionário com dados do template
            - nome: Nome do template
            - descricao: Descrição (opcional)
            - categoria: Categoria do template
            - prompt_sistema: Prompt de sistema
            - prompt_usuario: Prompt de usuário
            - configuracoes: Configurações adicionais (opcional)
            
    Returns:
        ID do template salvo
    """
    if not template_data:
        raise ValueError("Dados do template não fornecidos")
        
    # Valida dados mínimos
    if not template_data.get('nome'):
        raise ValueError("Nome do template é obrigatório")
    
    # Prepara os dados para salvar no formato esperado
    template = {
        'id': f"custom_{uuid.uuid4().hex[:8]}",
        'nome': template_data.get('nome'),
        'descricao': template_data.get('descricao', ''),
        'tipo': 'customizado',
        'categoria': template_data.get('categoria', 'geral'),
        'customizado': True,
        'data_criacao': datetime.now().isoformat(),
        'prompt_template': {
            'sistema': template_data.get('prompt_sistema', ''),
            'usuario': template_data.get('prompt_usuario', '')
        }
    }
    
    # Adiciona configurações se fornecidas
    if template_data.get('configuracoes'):
        template['configuracoes'] = template_data.get('configuracoes')
    
    # Salva o template usando a função existente
    return salvar_template(template)

def obter_categorias_templates():
    """
    Obtém as categorias de templates disponíveis.
    
    Returns:
        Lista de categorias de templates
    """
    # Inicialmente retorna as categorias padrão
    categorias = CATEGORIAS_PADRAO.copy()

    # Adiciona categorias de templates existentes
    templates = carregar_templates_agentes()
    for template in templates:
        if isinstance(template, dict) and 'categoria' in template:
            categoria = template.get('categoria')
            if categoria and categoria not in categorias:
                categorias.append(categoria)
    
    # Remove duplicatas e ordena
    categorias = sorted(list(set(categorias)))
    return categorias

def excluir_template(template_id):
    """
    Exclui um template.
    
    Args:
        template_id: ID do template
        
    Returns:
        True se excluído com sucesso
    """
    if not template_id:
        raise ValueError("ID do template não fornecido")
        
    # Busca o template
    template = obter_template_por_id(template_id)
    
    # Verifica se o template existe e é customizado
    if not template:
        raise ValueError(f"Template {template_id} não encontrado")
        
    if not template.get('customizado', False):
        raise ValueError(f"Não é possível excluir templates do sistema")
        
    # Localiza e exclui o arquivo
    nome_arquivo = f"{template_id}.json"
    caminho_arquivo = os.path.join(DIRETORIO_TEMPLATES_CUSTOM, nome_arquivo)
    
    if os.path.exists(caminho_arquivo):
        os.remove(caminho_arquivo)
        logger.info(f"Template {template_id} excluído com sucesso")
        return True
    else:
        # Procura por arquivos que contenham o ID de qualquer maneira
        for arquivo in os.listdir(DIRETORIO_TEMPLATES_CUSTOM):
            if arquivo.endswith('.json'):
                caminho = os.path.join(DIRETORIO_TEMPLATES_CUSTOM, arquivo)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = json.load(f)
                        if conteudo.get('id') == template_id:
                            os.remove(caminho)
                            logger.info(f"Template {template_id} excluído com sucesso de {arquivo}")
                            return True
                except Exception as e:
                    logger.error(f"Erro ao verificar template {arquivo}: {str(e)}")
                    
        raise FileNotFoundError(f"Arquivo de template {template_id} não encontrado")