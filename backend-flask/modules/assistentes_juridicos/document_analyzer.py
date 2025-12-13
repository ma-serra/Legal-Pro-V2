"""
Analisador Direto de Documentos para Assistentes Jurídicos
Sistema que processa diretamente arquivos anexados para respostas específicas e naturais
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """Analisador que processa diretamente documentos anexados"""
    
    def __init__(self, openai_client=None, anthropic_client=None):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        
    def extrair_texto_arquivo(self, file_path: str) -> Optional[str]:
        """Extrai texto de arquivos de diferentes formatos"""
        try:
            path_obj = Path(file_path)
            
            if path_obj.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            elif path_obj.suffix.lower() == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    texto = ""
                    for paragraph in doc.paragraphs:
                        texto += paragraph.text + "\n"
                    return texto.strip()
                except ImportError:
                    logger.warning("python-docx não disponível para .docx")
                    return None
                    
            elif path_obj.suffix.lower() == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        texto = ""
                        for page in reader.pages:
                            texto += page.extract_text() + "\n"
                    return texto.strip()
                except ImportError:
                    logger.warning("PyPDF2 não disponível para .pdf")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao extrair texto do arquivo {file_path}: {e}")
            return None
    
    def analisar_documento_especifico(self, documento_texto: str, pergunta_usuario: str, 
                                    area_juridica: str = "empresarial") -> str:
        """Analisa especificamente o documento enviado pelo usuário"""
        
        if not documento_texto or not pergunta_usuario:
            return self._resposta_padrao_sem_documento()
            
        # Detectar tipo de documento baseado no conteúdo
        tipo_documento = self._detectar_tipo_documento(documento_texto)
        
        # Criar prompt específico para análise
        prompt_personalizado = self._criar_prompt_especifico(
            documento_texto, pergunta_usuario, tipo_documento, area_juridica
        )
        
        # Processar com IA
        resposta = self._processar_com_ia(prompt_personalizado)
        
        return resposta
    
    def _detectar_tipo_documento(self, texto: str) -> str:
        """Detecta o tipo de documento baseado no conteúdo"""
        texto_lower = texto.lower()
        
        if "relatório de análise multi-agente" in texto_lower:
            return "relatorio_multiagente"
        elif "contrato de prestação de serviços" in texto_lower:
            return "contrato_servicos"
        elif "contrato de marketing" in texto_lower:
            return "contrato_marketing"
        elif "análise jurídica" in texto_lower:
            return "analise_juridica"
        elif "petição" in texto_lower:
            return "peticao"
        elif "parecer" in texto_lower:
            return "parecer"
        else:
            return "documento_generico"
    
    def _criar_prompt_especifico(self, documento: str, pergunta: str, 
                                tipo: str, area: str) -> str:
        """Cria prompt específico baseado no documento e pergunta"""
        
        prompts_especificos = {
            "relatorio_multiagente": f"""
Você é um especialista em {area} analisando um relatório multi-agente específico.

DOCUMENTO ANEXADO:
{documento}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES:
- Analise ESPECIFICAMENTE o documento anexado
- Extraia os riscos identificados pelos agentes mencionados
- Responda diretamente à pergunta com base no conteúdo específico
- Use linguagem natural e fluida
- Seja específico sobre o contrato/caso analisado
- Cite trechos relevantes do documento quando apropriado

Responda como um advogado experiente que acabou de ler este documento específico:
""",
            
            "contrato_servicos": f"""
Você é um advogado especialista em {area} analisando um contrato específico.

CONTRATO ANEXADO:
{documento}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES:
- Analise ESPECIFICAMENTE este contrato
- Identifique cláusulas, riscos e oportunidades específicas
- Responda com base no conteúdo exato do documento
- Use linguagem jurídica apropriada mas acessível
- Seja prático e específico sobre este contrato

Sua análise específica:
""",
            
            "default": f"""
Você é um advogado especialista em {area} analisando um documento específico.

DOCUMENTO:
{documento}

PERGUNTA:
{pergunta}

Analise especificamente este documento e responda de forma natural e direta:
"""
        }
        
        return prompts_especificos.get(tipo, prompts_especificos["default"])
    
    def _processar_com_ia(self, prompt: str) -> str:
        """Processa o prompt com IA disponível"""
        
        # Tentar OpenAI primeiro
        if self._tem_openai_disponivel():
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user", 
                        "content": prompt
                    }],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Erro OpenAI: {e}")
        
        # Tentar Anthropic como fallback
        if self._tem_anthropic_disponivel():
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Erro Anthropic: {e}")
        
        return self._resposta_erro_ia()
    
    def _tem_openai_disponivel(self) -> bool:
        """Verifica se OpenAI está disponível"""
        try:
            if hasattr(self.openai_client, 'get_client'):
                client = self.openai_client.get_client()
                return client is not None
            return self.openai_client is not None
        except:
            return False
    
    def _tem_anthropic_disponivel(self) -> bool:
        """Verifica se Anthropic está disponível"""
        try:
            if hasattr(self.anthropic_client, 'get_client'):
                client = self.anthropic_client.get_client()
                return client is not None
            return self.anthropic_client is not None
        except:
            return False
    
    def _resposta_padrao_sem_documento(self) -> str:
        """Resposta quando não há documento para analisar"""
        return """
Não identifiquei um documento específico para analisar. 

Para uma análise precisa e personalizada, por favor:
- Anexe o documento que deseja analisar (PDF, DOCX, TXT)
- Faça sua pergunta específica sobre o documento

Assim posso fornecer uma análise detalhada e específica do seu caso.
"""
    
    def _resposta_erro_ia(self) -> str:
        """Resposta quando há erro na IA"""
        return """
Identifiquei seu documento, mas estou com dificuldades técnicas para processá-lo no momento.

Por favor:
1. Tente novamente em alguns instantes
2. Ou reformule sua pergunta de forma mais específica
3. Verifique se o documento foi anexado corretamente

Se o problema persistir, entre em contato com o suporte técnico.
"""