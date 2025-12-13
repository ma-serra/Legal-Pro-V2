"""
Módulo para garantir a correta marcação de diferenças em documentos.
Este módulo implementa funções diretas e robustas para destacar diferenças entre textos.
"""

import re
import difflib
from typing import Tuple, List
from diff_match_patch import diff_match_patch
import logging

logger = logging.getLogger(__name__)

# Constantes para marcação HTML com estilos incorporados
DELETED_START = '<span style="background-color:#ffdddd; color:#990000; text-decoration:line-through; padding:2px 4px; border-radius:3px; display:inline-block; margin:0 1px; border-left:2px solid #ff0000; font-weight:bold;">'
DELETED_END = '</span>'
ADDED_START = '<span style="background-color:#ddffdd; color:#006600; padding:2px 4px; border-radius:3px; display:inline-block; margin:0 1px; border-left:2px solid #00aa00; font-weight:bold;">'
ADDED_END = '</span>'

def escape_html(text: str) -> str:
    """Escapa caracteres HTML para exibição segura"""
    if not text:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def split_into_paragraphs(text: str) -> List[str]:
    """Divide o texto em parágrafos para comparação"""
    if not text:
        return []
    return text.splitlines()

def mark_differences(texto_original: str, texto_modificado: str) -> Tuple[str, str]:
    """
    Marca diferenças entre dois textos seguindo exatamente estas regras:
    1. Na versão original: texto excluído aparece em vermelho
    2. Na versão modificada: texto adicionado aparece em verde
    
    Esta implementação usa estilos inline para garantir que as cores sejam exibidas
    corretamente em qualquer situação.
    
    Args:
        texto_original: Texto original
        texto_modificado: Texto modificado
        
    Returns:
        Tupla com (html_original, html_modificado) com as diferenças marcadas
    """
    try:
        # Comparação direta com diff-match-patch para máxima precisão
        dmp = diff_match_patch()
        diffs = dmp.diff_main(texto_original, texto_modificado)
        dmp.diff_cleanupSemantic(diffs)
        
        # Para documentos vazios
        if not texto_original and not texto_modificado:
            return "", ""
        
        # Adicionar símbolos visíveis para melhorar a clareza
        minus_symbol = '<span style="color:#cc0000; font-weight:bold; margin-right:3px;">−</span>'
        plus_symbol = '<span style="color:#008800; font-weight:bold; margin-right:3px;">+</span>'
        
        # Construir resultado HTML para o texto original (marca apenas o que foi removido)
        html_original = []
        for op, texto in diffs:
            texto_esc = escape_html(texto)
            if op == 0:  # Texto não modificado
                html_original.append(texto_esc)
            elif op == -1:  # Texto removido (aparece apenas no original)
                html_original.append(f"{DELETED_START}{minus_symbol}{texto_esc}{DELETED_END}")
            # Texto adicionado não aparece no original
        
        # Construir resultado HTML para o texto modificado (marca apenas o que foi adicionado)
        html_modificado = []
        for op, texto in diffs:
            texto_esc = escape_html(texto)
            if op == 0:  # Texto não modificado
                html_modificado.append(texto_esc)
            elif op == 1:  # Texto adicionado (aparece apenas no modificado)
                html_modificado.append(f"{ADDED_START}{plus_symbol}{texto_esc}{ADDED_END}")
            # Texto removido não aparece no modificado
        
        # Converter quebras de linha para HTML
        html_original_final = "".join(html_original).replace('\n', '<br>')
        html_modificado_final = "".join(html_modificado).replace('\n', '<br>')
        
        return html_original_final, html_modificado_final
    
    except Exception as e:
        logger.error(f"Erro na marcação de diferenças: {e}")
        # Em caso de erro, retornar textos originais escapados
        return escape_html(texto_original).replace('\n', '<br>'), escape_html(texto_modificado).replace('\n', '<br>')