"""
Rotas simplificadas para Mapa Mental Radial
"""
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
import logging
from openai import OpenAI
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def registrar_rotas_mapa_mental(app, db):
    """Registra rotas do mapa mental"""
    
    # Configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    @app.route('/mapa-mental')
    @login_required
    def mapa_mental():
        """Página principal do mapa mental"""
        app.logger.info("🎯 Acessando página do mapa mental")
        return render_template('mapa_mental_novo.html')
    
    @app.route('/api/mapa-mental/processar-documento', methods=['POST'])
    @login_required
    def api_processar_documento_mapa():
        """Processa documento e gera mapa mental radial"""
        try:
            if 'arquivo' not in request.files:
                return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
            
            arquivo = request.files['arquivo']
            if arquivo.filename == '':
                return jsonify({'success': False, 'error': 'Arquivo vazio'})
            
            # Extrair texto do documento
            texto_extraido = extrair_texto_documento(arquivo)
            
            # Gerar mapa mental com OpenAI
            mapa_data = gerar_mapa_mental_openai(texto_extraido)
            
            return jsonify({
                'success': True,
                'mapa': mapa_data,
                'texto_extraido': texto_extraido[:500] + "..."
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar documento: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/mapa-mental/processar-texto', methods=['POST'])
    @login_required
    def api_processar_texto_mapa():
        """Processa texto e gera mapa mental radial"""
        try:
            app.logger.info("🚀 Iniciando processamento de texto")
            
            data = request.get_json()
            app.logger.info(f"📝 Dados recebidos: {data}")
            
            if not data:
                app.logger.error("❌ Nenhum dado JSON recebido")
                return jsonify({'success': False, 'error': 'Dados não fornecidos'})
                
            texto = data.get('texto', '')
            app.logger.info(f"📄 Texto para processar: {texto[:100]}...")
            
            if not texto.strip():
                app.logger.error("❌ Texto vazio ou apenas espaços")
                return jsonify({'success': False, 'error': 'Texto vazio'})
            
            app.logger.info("🤖 Chamando OpenAI para gerar mapa mental")
            # Gerar mapa mental com OpenAI
            mapa_data = gerar_mapa_mental_openai(texto)
            
            app.logger.info(f"✅ Mapa mental gerado: {mapa_data}")
            
            return jsonify({
                'success': True,
                'mapa': mapa_data
            })
            
        except Exception as e:
            app.logger.error(f"💥 Erro ao processar texto: {str(e)}")
            import traceback
            app.logger.error(f"📊 Stack trace: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': str(e)})


def extrair_texto_documento(arquivo):
    """Extrai texto de documento"""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo.filename)[1]) as temp_file:
        arquivo.save(temp_file.name)
        
        if arquivo.filename.lower().endswith('.pdf'):
            import PyPDF2
            with open(temp_file.name, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                texto = ""
                for page in reader.pages:
                    texto += page.extract_text()
                return texto
        
        elif arquivo.filename.lower().endswith('.docx'):
            from docx import Document
            doc = Document(temp_file.name)
            texto = ""
            for paragraph in doc.paragraphs:
                texto += paragraph.text + "\n"
            return texto
        
        elif arquivo.filename.lower().endswith('.txt'):
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            raise ValueError("Formato não suportado")


def gerar_mapa_mental_openai(texto):
    """Gera mapa mental usando múltiplos providers com fallback"""
    
    prompt = f"""
    Analise o documento jurídico e crie um mapa mental hierárquico.
    
    DOCUMENTO: {texto[:2000]}
    
    Retorne um JSON com esta estrutura EXATA:
    {{
        "tema_central": {{
            "titulo": "Título Principal do Documento"
        }},
        "topicos": [
            {{
                "titulo": "Tópico 1",
                "subtopicos": [
                    "Subtópico 1.1",
                    "Subtópico 1.2"
                ]
            }},
            {{
                "titulo": "Tópico 2", 
                "subtopicos": [
                    "Subtópico 2.1",
                    "Subtópico 2.2"
                ]
            }}
        ]
    }}
    
    Crie 7 tópicos principais, cada um com 2-3 subtópicos em STRING simples.
    """
    
    # Provider 1: OpenAI
    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Resposta vazia da OpenAI")
        
        mapa_data = json.loads(content)
        mapa_data['provider'] = 'OpenAI'
        
    except Exception as e:
        logger.warning(f"OpenAI falhou: {str(e)}")
        
        # Provider 2: Anthropic
        try:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            
            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = message.content[0].text
            # Extrair JSON do texto (Claude não força JSON)
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                mapa_data = json.loads(json_match.group())
                mapa_data['provider'] = 'Anthropic'
            else:
                raise ValueError("Não foi possível extrair JSON da resposta")
                
        except Exception as e2:
            logger.warning(f"Anthropic falhou: {str(e2)}")
            
            # Provider 3: Google Gemini
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                response = model.generate_content(prompt)
                
                # Extrair JSON do texto
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    mapa_data = json.loads(json_match.group())
                    mapa_data['provider'] = 'Google Gemini'
                else:
                    raise ValueError("Não foi possível extrair JSON da resposta")
                    
            except Exception as e3:
                logger.error(f"Todos os providers falharam. OpenAI: {str(e)}, Anthropic: {str(e2)}, Google: {str(e3)}")
                # Fallback com estrutura padrão
                mapa_data = criar_mapa_fallback(texto)
    
    # Adicionar metadados
    mapa_data['fonte'] = 'documento'
    mapa_data['gerado_em'] = datetime.now().isoformat()
    
    return mapa_data

def criar_mapa_fallback(texto):
    """Cria mapa mental simples quando APIs falham"""
    palavras = texto.lower().split()
    
    # Identificar palavras-chave jurídicas comuns
    keywords_juridicas = ['contrato', 'partes', 'objeto', 'prazo', 'valor', 'obrigações', 'direitos']
    topicos_encontrados = []
    
    for keyword in keywords_juridicas:
        if keyword in palavras:
            topicos_encontrados.append({
                "titulo": keyword.capitalize(),
                "subtopicos": [f"Análise de {keyword}", f"Implicações de {keyword}"]
            })
    
    if not topicos_encontrados:
        topicos_encontrados = [
            {"titulo": "Análise Geral", "subtopicos": ["Conteúdo principal", "Aspectos relevantes"]},
            {"titulo": "Estrutura", "subtopicos": ["Organização", "Elementos"]}
        ]
    
    return {
        "tema_central": {"titulo": "Documento Jurídico"},
        "topicos": topicos_encontrados,
        "provider": "Fallback",
        "observacao": "Gerado automaticamente quando APIs não estão disponíveis"
    }