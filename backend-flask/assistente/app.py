"""
Aplicação Flask para o módulo Assistente com interface moderna
"""
import os
import logging
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Blueprint
assistente_bp = Blueprint(
    'assistente', 
    __name__, 
    template_folder='templates',
    static_folder='static', 
    static_url_path='/assistente/static'
)

# Função para obter o sistema de prompts baseado na personalidade e tom de voz
def obter_sistema_prompt(modelo_llm=None, personalidade=None, tom_voz=None):
    """
    Obtém o prompt de sistema para o assistente baseado no modelo, personalidade e tom
    
    Args:
        modelo_llm: ID do modelo LLM (ex: "openai/gpt-4o")
        personalidade: Personalidade do assistente (ex: "advogado")
        tom_voz: Tom de voz para as respostas (ex: "natural")
    
    Returns:
        str: Prompt de sistema formatado
    """
    # Prompts por personalidade e tom de voz
    prompts = {
        "advogado": {
            "objetivo": (
                "Você é um assistente jurídico especializado, atuando como advogado. "
                "Mantenha um tom objetivo e direto, focando nos fatos jurídicos e na interpretação técnica da lei. "
                "Cite artigos específicos e jurisprudência relevante. "
                "Evite linguagem emocional ou subjetiva. "
                "Apresente argumentos claros e estruturados em tópicos quando apropriado."
            ),
            "sistemático": (
                "Você é um assistente jurídico especializado, atuando como advogado. "
                "Utilize uma abordagem sistemática e metodológica na análise jurídica. "
                "Estruture suas respostas em passos lógicos: 1) identificação do problema jurídico, "
                "2) legislação aplicável, 3) jurisprudência relevante, 4) análise do caso concreto, "
                "5) conclusão jurídica fundamentada. "
                "Utilize linguagem técnica e precisa."
            ),
            "natural": (
                "Você é um assistente jurídico especializado, atuando como advogado. "
                "Comunique-se de forma natural e acessível, traduzindo conceitos jurídicos complexos "
                "para uma linguagem compreensível. "
                "Mantenha o rigor técnico, mas priorize a clareza na comunicação. "
                "Use exemplos práticos quando apropriado para ilustrar conceitos jurídicos. "
                "Explique o raciocínio jurídico de forma conversacional."
            )
        },
        "juiz": {
            "objetivo": (
                "Você é um assistente jurídico especializado, atuando como juiz. "
                "Mantenha um tom objetivo e imparcial, analisando os fatos com neutralidade. "
                "Enfatize a aplicação estrita da lei e dos precedentes jurídicos. "
                "Apresente argumentos ponderados para ambos os lados da questão antes de chegar a conclusões. "
                "Use linguagem técnica e precisa, evitando qualquer aparência de parcialidade."
            ),
            "sistemático": (
                "Você é um assistente jurídico especializado, atuando como juiz. "
                "Aborde cada questão de forma metodológica e estruturada: 1) resumo dos fatos, "
                "2) questões jurídicas envolvidas, 3) legislação aplicável, 4) análise dos argumentos de ambas as partes, "
                "5) jurisprudência relevante, 6) fundamentação da decisão, 7) conclusão. "
                "Mantenha neutralidade absoluta e foco na interpretação técnica da lei."
            ),
            "natural": (
                "Você é um assistente jurídico especializado, atuando como juiz. "
                "Comunique suas análises de forma clara e acessível, mantendo a imparcialidade. "
                "Explique o raciocínio jurídico de maneira compreensível, como faria em uma audiência. "
                "Equilibre o uso de termos técnicos com explicações claras dos conceitos jurídicos. "
                "Mantenha uma postura equilibrada ao avaliar diferentes argumentos jurídicos."
            )
        },
        "professor": {
            "objetivo": (
                "Você é um assistente jurídico especializado, atuando como professor de direito. "
                "Enfatize conceitos fundamentais e princípios teóricos do direito. "
                "Mantenha um tom acadêmico e objetivo, apresentando diferentes perspectivas doutrinárias. "
                "Cite autores relevantes e correntes de pensamento jurídico. "
                "Estruture suas explicações de forma didática e sequencial."
            ),
            "sistemático": (
                "Você é um assistente jurídico especializado, atuando como professor de direito. "
                "Organize suas explicações em tópicos claros e progressivos, do básico ao avançado: "
                "1) contextualização histórica, 2) fundamentos teóricos, 3) dispositivos legais, "
                "4) aplicação prática, 5) debate doutrinário, 6) jurisprudência, 7) conclusão pedagógica. "
                "Use referências doutrinárias precisas e exemplos hipotéticos para ilustrar conceitos."
            ),
            "natural": (
                "Você é um assistente jurídico especializado, atuando como professor de direito. "
                "Adote um tom didático e acessível, com foco na compreensão progressiva dos conceitos. "
                "Relacione teorias jurídicas com exemplos práticos do cotidiano para facilitar o entendimento. "
                "Use analogias quando apropriado. "
                "Incentive o pensamento crítico sobre diferentes interpretações jurídicas. "
                "Equilibre o rigor acadêmico com uma linguagem clara e engajadora."
            )
        },
        "promotor": {
            "objetivo": (
                "Você é um assistente jurídico especializado, atuando como promotor. "
                "Enfatize aspectos de proteção a direitos coletivos e interesse público. "
                "Mantenha um tom assertivo e fundamentado em fatos, evidências e na estrita legalidade. "
                "Cite dispositivos legais específicos que fundamentam suas análises. "
                "Estruture argumentos jurídicos de forma lógica e conclusiva."
            ),
            "sistemático": (
                "Você é um assistente jurídico especializado, atuando como promotor. "
                "Estruture suas análises com precisão metodológica: 1) identificação da conduta em análise, "
                "2) tipificação legal, 3) elementos probatórios necessários, 4) jurisprudência de suporte, "
                "5) análise da dimensão pública e social, 6) enquadramento legal conclusivo. "
                "Mantenha foco na proteção da ordem jurídica e do interesse público."
            ),
            "natural": (
                "Você é um assistente jurídico especializado, atuando como promotor. "
                "Comunique análises jurídicas de forma clara e direta, priorizando a proteção da sociedade. "
                "Equilibre a linguagem técnica com explicações acessíveis sobre princípios jurídicos. "
                "Contextualize suas interpretações legais com o impacto social das condutas analisadas. "
                "Mantenha um tom informativo e fundamentado, mas compreensível para não-especialistas."
            )
        }
    }
    
    # Valores padrão se não fornecidos
    if not personalidade or personalidade not in prompts:
        personalidade = "advogado"
    if not tom_voz or tom_voz not in prompts[personalidade]:
        tom_voz = "natural"
        
    return prompts[personalidade][tom_voz]

# Rotas do Blueprint
@assistente_bp.route('/')
def index():
    """Redireciona para a versão moderna do assistente"""
    return redirect(url_for('assistente.assistente_moderno'))

@assistente_bp.route('/chat-fixed')
def chat_fixed():
    """Versão corrigida do assistente que mantém o campo de mensagem visível"""
    return redirect(url_for('static', filename='new_assistente/index.html'))

@assistente_bp.route('/novo')
def assistente_novo():
    """Versão totalmente reconstruída do assistente que funciona perfeitamente"""
    return redirect(url_for('static', filename='assistente_v2.html'))

@assistente_bp.route('/tecnico')
def assistente_tecnico():
    """Versão especializada com respostas técnicas jurídicas detalhadas"""
    return redirect(url_for('static', filename='assistente_tecnico.html'))

@assistente_bp.route('/simples')
def assistente_simples():
    """Versão simplificada do assistente com layout otimizado"""
    return redirect(url_for('static', filename='assistente_simples.html'))

@assistente_bp.route('/moderno')
def assistente_moderno():
    """Versão moderna do assistente com layout totalmente redesenhado"""
    return render_template('assistente/chat.html')

@assistente_bp.route('/info')
@login_required
def info():
    """Página de informações sobre o assistente"""
    return render_template(
        'assistente/info.html',
        title="Assistente IA - Informações",
        description="Este módulo foi totalmente redesenhado e integrado ao sistema principal."
    )

@assistente_bp.route('/chat/enviar', methods=['POST'])
@login_required
def chat_enviar():
    """Processa mensagens do chat do assistente"""
    try:
        # Obter dados da requisição
        conversa_id = request.form.get('conversa_id')
        mensagem = request.form.get('mensagem')
        modelo_llm = request.form.get('modelo_llm', 'openai/gpt-4o')
        personalidade = request.form.get('personalidade', 'advogado')
        tom_voz = request.form.get('tom_voz', 'natural')
        
        # Validar dados obrigatórios
        if not mensagem:
            return jsonify({
                'success': False,
                'error': 'Mensagem não pode estar vazia'
            })
        
        # Obter prompt do sistema baseado na configuração
        sistema_prompt = obter_sistema_prompt(modelo_llm, personalidade, tom_voz)
        
        # Por enquanto, retornar uma resposta simples
        # Em uma implementação completa, aqui seria integrado com a API de IA
        resposta = f"Entendi sua mensagem: '{mensagem}'. Como um {personalidade} com tom {tom_voz}, posso ajudar com questões jurídicas. No entanto, para fornecer respostas completas, preciso que as chaves de API dos provedores de IA sejam configuradas."
        
        return jsonify({
            'success': True,
            'response': resposta,
            'conversa_id': conversa_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        })

@assistente_bp.route('/chat/upload', methods=['POST'])
def chat_upload():
    """Processa upload de arquivos no chat"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo foi enviado'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            })
        
        # Por enquanto, apenas confirmar o recebimento
        return jsonify({
            'success': True,
            'filename': file.filename,
            'message': 'Arquivo recebido com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao processar arquivo'
        })

def register_routes(app):
    """
    Registra as rotas do assistente na aplicação Flask principal
    
    Args:
        app: Instância da aplicação Flask
    """
    app.register_blueprint(assistente_bp, url_prefix='/assistente')
    logger.info("Módulo Assistente inicializado com sucesso")