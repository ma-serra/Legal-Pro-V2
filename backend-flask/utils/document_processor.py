"""
Processador de documentos para análise multi-agente
Extrai texto de diferentes formatos de arquivo
"""

import os
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Classe para processar diferentes tipos de documentos
    """
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.docx', '.txt'}
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extrai texto do arquivo baseado na extensão
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return await self._extract_from_pdf(file_path)
        elif file_ext == '.docx':
            return await self._extract_from_docx(file_path)
        elif file_ext == '.txt':
            return await self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file_ext}")
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """
        Extrai texto de arquivo PDF
        """
        try:
            import PyPDF2
            
            def extract_pdf_sync():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, extract_pdf_sync)
            
            if not text:
                raise ValueError("Não foi possível extrair texto do PDF")
            
            return text
            
        except ImportError:
            logger.error("PyPDF2 não está instalado")
            raise ValueError("Processamento de PDF não disponível")
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
            raise ValueError(f"Erro ao processar PDF: {str(e)}")
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """
        Extrai texto de arquivo DOCX
        """
        try:
            from docx import Document
            
            def extract_docx_sync():
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, extract_docx_sync)
            
            if not text:
                raise ValueError("Documento DOCX está vazio")
            
            return text
            
        except ImportError:
            logger.error("python-docx não está instalado")
            raise ValueError("Processamento de DOCX não disponível")
        except Exception as e:
            logger.error(f"Erro ao extrair texto do DOCX: {str(e)}")
            raise ValueError(f"Erro ao processar DOCX: {str(e)}")
    
    async def _extract_from_txt(self, file_path: str) -> str:
        """
        Extrai texto de arquivo TXT
        """
        try:
            def read_txt_sync():
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, read_txt_sync)
            
            if not text.strip():
                raise ValueError("Arquivo de texto está vazio")
            
            return text.strip()
            
        except UnicodeDecodeError:
            # Tentar com diferentes encodings
            try:
                def read_txt_latin1():
                    with open(file_path, 'r', encoding='latin-1') as file:
                        return file.read()
                
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(None, read_txt_latin1)
                return text.strip()
                
            except Exception as e:
                logger.error(f"Erro de encoding ao ler arquivo de texto: {str(e)}")
                raise ValueError("Erro de encoding no arquivo de texto")
        except Exception as e:
            logger.error(f"Erro ao extrair texto do arquivo: {str(e)}")
            raise ValueError(f"Erro ao processar arquivo de texto: {str(e)}")
    
    def validate_file(self, file_path: str, max_size_mb: int = 50) -> bool:
        """
        Valida se o arquivo pode ser processado
        """
        if not os.path.exists(file_path):
            return False
        
        # Verificar tamanho
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False
        
        # Verificar extensão
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.supported_formats