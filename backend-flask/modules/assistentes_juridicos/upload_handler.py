"""
Processador de Upload de Arquivos
Suporte para .docx, .pdf, imagens
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Importações opcionais
try:
    import docx
    DOCX_DISPONIVEL = True
except ImportError:
    DOCX_DISPONIVEL = False
    logger.warning("python-docx não disponível - processamento de DOCX desabilitado")

try:
    import PyPDF2
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False
    logger.warning("PyPDF2 não disponível - processamento de PDF desabilitado")

try:
    from PIL import Image
    import pytesseract
    OCR_DISPONIVEL = True
except ImportError:
    OCR_DISPONIVEL = False
    logger.warning("pytesseract/PIL não disponível - OCR de imagens desabilitado")

class ProcessadorArquivos:
    """Processa uploads de diferentes tipos de arquivo"""
    
    def __init__(self):
        self.tipos_suportados = ['.docx', '.pdf', '.jpg', '.jpeg', '.png']
    
    def extrair_texto(self, arquivo_path: str) -> str:
        """Extrai texto de diferentes tipos de arquivo"""
        try:
            extensao = os.path.splitext(arquivo_path)[1].lower()
            
            if extensao == '.docx':
                return self._extrair_texto_docx(arquivo_path)
            elif extensao == '.pdf':
                return self._extrair_texto_pdf(arquivo_path)
            elif extensao in ['.jpg', '.jpeg', '.png']:
                return self._extrair_texto_imagem(arquivo_path)
            else:
                return f"Tipo de arquivo não suportado: {extensao}"
                
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            return f"Erro ao processar arquivo: {str(e)}"
    
    def _extrair_texto_docx(self, arquivo_path: str) -> str:
        """Extrai texto de arquivo .docx"""
        if not DOCX_DISPONIVEL:
            return "Processamento de DOCX não disponível. Instale python-docx."
        
        try:
            doc = docx.Document(arquivo_path)
            texto = []
            for paragrafo in doc.paragraphs:
                texto.append(paragrafo.text)
            return '\n'.join(texto)
        except Exception as e:
            return f"Erro ao processar DOCX: {str(e)}"
    
    def _extrair_texto_pdf(self, arquivo_path: str) -> str:
        """Extrai texto de arquivo .pdf"""
        if not PDF_DISPONIVEL:
            return "Processamento de PDF não disponível. Instale PyPDF2."
        
        try:
            texto = []
            with open(arquivo_path, 'rb') as arquivo:
                leitor_pdf = PyPDF2.PdfReader(arquivo)
                for pagina in leitor_pdf.pages:
                    texto.append(pagina.extract_text())
            return '\n'.join(texto)
        except Exception as e:
            return f"Erro ao processar PDF: {str(e)}"
    
    def _extrair_texto_imagem(self, arquivo_path: str) -> str:
        """Extrai texto de imagem usando OCR"""
        if not OCR_DISPONIVEL:
            return "OCR de imagens não disponível. Instale pytesseract e PIL."
        
        try:
            imagem = Image.open(arquivo_path)
            texto = pytesseract.image_to_string(imagem, lang='por')
            return texto
        except Exception as e:
            return f"Erro ao processar imagem (OCR): {str(e)}"