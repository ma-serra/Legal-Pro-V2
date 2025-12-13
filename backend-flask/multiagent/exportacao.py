"""
Utilitários para exportação de resultados em vários formatos.
"""
import os
import tempfile
import logging
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import html2text
from io import BytesIO

# Configuração de logging
logger = logging.getLogger('multiagent.exportacao')

def sanitizar_html(html_content):
    """
    Remove tags HTML potencialmente problemáticas e sanitiza o conteúdo.
    
    Args:
        html_content: Conteúdo HTML a ser sanitizado
        
    Returns:
        Conteúdo HTML sanitizado
    """
    # Implementação básica
    # Em um ambiente de produção, seria ideal usar uma biblioteca como bleach
    if not html_content:
        return ""
    return html_content

def html_para_texto(html_content):
    """
    Converte conteúdo HTML para texto simples.
    
    Args:
        html_content: Conteúdo HTML a ser convertido
        
    Returns:
        Conteúdo como texto simples
    """
    if not html_content:
        return ""
        
    try:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0  # Não quebra linhas
        return h.handle(html_content)
    except Exception as e:
        logger.error(f"Erro ao converter HTML para texto: {str(e)}")
        # Fallback simples se html2text falhar
        return html_content.replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n')

def exportar_para_txt(titulo, conteudo, html=True):
    """
    Exporta o resultado para um arquivo de texto.
    
    Args:
        titulo: Título do documento
        conteudo: Conteúdo a ser exportado (HTML ou texto)
        html: Se True, converte de HTML para texto
        
    Returns:
        Conteúdo do arquivo em bytes
    """
    try:
        # Converte HTML para texto se necessário
        if html:
            texto = html_para_texto(conteudo)
        else:
            texto = conteudo
            
        # Formata o documento
        texto_formatado = f"""
{titulo}
{"=" * len(titulo)}

{texto}
"""
        
        # Retorna os bytes
        return texto_formatado.encode('utf-8')
        
    except Exception as e:
        logger.error(f"Erro ao exportar para TXT: {str(e)}")
        return f"Erro ao exportar para TXT: {str(e)}".encode('utf-8')

def exportar_para_docx(titulo, conteudo, html=True):
    """
    Exporta o resultado para um arquivo DOCX.
    
    Args:
        titulo: Título do documento
        conteudo: Conteúdo a ser exportado (HTML ou texto)
        html: Se True, converte de HTML para texto
        
    Returns:
        Conteúdo do arquivo em bytes
    """
    try:
        # Cria um novo documento
        doc = Document()
        
        # Adiciona título
        titulo_docx = doc.add_heading(titulo, 0)
        titulo_docx.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Converte HTML para texto se necessário
        if html:
            texto = html_para_texto(conteudo)
        else:
            texto = conteudo
            
        # Adiciona parágrafos
        for paragrafo in texto.split('\n'):
            if paragrafo.strip():
                # Identifica se é um título pela formatação (exemplo: linhas que começam com #)
                if paragrafo.strip().startswith('#'):
                    nivel = min(paragrafo.count('#'), 6)  # Markdown headers vão de 1 a 6
                    texto_titulo = paragrafo.strip('#').strip()
                    doc.add_heading(texto_titulo, nivel)
                else:
                    p = doc.add_paragraph(paragrafo)
        
        # Salva o documento em memória
        docx_bytes = BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)
        
        # Retorna os bytes
        return docx_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao exportar para DOCX: {str(e)}")
        # Se falhar, retorna um documento com a mensagem de erro
        try:
            doc = Document()
            doc.add_heading("Erro ao exportar para DOCX", 0)
            doc.add_paragraph(str(e))
            error_bytes = BytesIO()
            doc.save(error_bytes)
            error_bytes.seek(0)
            return error_bytes.getvalue()
        except:
            return b"Erro ao exportar para DOCX."

def exportar_para_pdf(titulo, conteudo, html=True):
    """
    Exporta o resultado para um arquivo PDF.
    
    Nota: Esta é uma implementação básica que gera um DOCX e então
    tenta convertê-lo para PDF usando ferramentas externas.
    Em um ambiente de produção, seria ideal usar uma biblioteca como
    reportlab ou WeasyPrint.
    
    Args:
        titulo: Título do documento
        conteudo: Conteúdo a ser exportado (HTML ou texto)
        html: Se True, converte de HTML para texto
        
    Returns:
        Conteúdo do arquivo em bytes ou None se a conversão falhar
    """
    try:
        # Primeiro, gera um arquivo DOCX
        docx_bytes = exportar_para_docx(titulo, conteudo, html)
        
        # Cria arquivos temporários para a conversão
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_temp:
            docx_path = docx_temp.name
            docx_temp.write(docx_bytes)
            
        pdf_path = docx_path.replace('.docx', '.pdf')
        
        try:
            # Tenta converter usando LibreOffice (se disponível)
            os.system(f'libreoffice --headless --convert-to pdf --outdir {os.path.dirname(pdf_path)} {docx_path}')
            
            # Verifica se o PDF foi gerado
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                # Limpa os arquivos temporários
                os.unlink(docx_path)
                os.unlink(pdf_path)
                return pdf_bytes
                
            # Se não conseguiu com LibreOffice, tenta com unoconv
            os.system(f'unoconv -f pdf -o {pdf_path} {docx_path}')
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                # Limpa os arquivos temporários
                os.unlink(docx_path)
                os.unlink(pdf_path)
                return pdf_bytes
                
            # Se nenhuma conversão funcionou, retorna None
            logger.warning("Não foi possível converter para PDF.")
            return None
            
        finally:
            # Garante que os arquivos temporários sejam removidos
            if os.path.exists(docx_path):
                os.unlink(docx_path)
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
                
    except Exception as e:
        logger.error(f"Erro ao exportar para PDF: {str(e)}")
        return None