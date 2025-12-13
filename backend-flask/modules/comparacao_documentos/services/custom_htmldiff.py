"""
Versão aprimorada da biblioteca htmldiff para melhor detecção e visualização de diferenças em documentos.
Esta versão resolve problemas com marcações HTML e melhora a identificação de alterações.
"""
import re
import difflib
import logging
from diff_match_patch import diff_match_patch

logger = logging.getLogger(__name__)

__all__ = ['render_html_diff', 'compare_texts_enhanced']

# Padrões de expressão regular corrigidos para evitar o uso de (?u)
_leading_space_re = re.compile(r'^(\s+)', re.UNICODE)
_trailing_space_re = re.compile(r'(\s+)$', re.UNICODE)
_whitespace_re = re.compile(r'\s+', re.UNICODE)

# Substituições de tags para destaque de diferenças
INS_START = '<span class="diff-adicionado">'
INS_END = '</span>'
DEL_START = '<span class="diff-deletado">'
DEL_END = '</span>'

def tokenize(text):
    """
    Quebra o texto em unidades para comparação.
    """
    if not text:
        return []

    words = []
    pos = 0
    text_len = len(text)

    def add_word(start, end):
        """Adiciona uma palavra ou espaço à lista de tokens."""
        if start < end:
            words.append((start, end, text[start:end]))

    while pos < text_len:
        start = pos
        # Encontrar espaços iniciais
        leading_match = _leading_space_re.search(text[pos:])
        if leading_match:
            start_spaces = pos + leading_match.end(1)
            add_word(pos, start_spaces)
            pos = start_spaces
        
        if pos >= text_len:
            break

        # Encontrar texto após os espaços
        start = pos
        while pos < text_len and not text[pos].isspace():
            pos += 1
        
        add_word(start, pos)

        # Encontrar espaços finais
        start = pos
        trailing_match = _trailing_space_re.search(text[pos:])
        if trailing_match:
            end_spaces = pos + trailing_match.end(1)
            add_word(pos, end_spaces)
            pos = end_spaces

    return words

def render_html_diff(a, b):
    """
    Renderiza a diferença entre dois textos em HTML destacando as alterações.
    
    Args:
        a: Texto original
        b: Texto modificado
        
    Returns:
        Tupla com (texto_a_html, texto_b_html) onde as diferenças estão destacadas
    """
    a_tokens = tokenize(a)
    b_tokens = tokenize(b)
    
    if not a_tokens and not b_tokens:
        return '', ''
    
    if not a_tokens:
        return '', ''.join([INS_START + b_token[2] + INS_END for b_token in b_tokens])
    
    if not b_tokens:
        return ''.join([DEL_START + a_token[2] + DEL_END for a_token in a_tokens]), ''
    
    a_token_strings = [token[2] for token in a_tokens]
    b_token_strings = [token[2] for token in b_tokens]
    
    opcodes = difflib.SequenceMatcher(None, a_token_strings, b_token_strings).get_opcodes()
    
    a_html = []
    b_html = []
    
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            for i in range(i1, i2):
                a_html.append(a_token_strings[i])
            for j in range(j1, j2):
                b_html.append(b_token_strings[j])
        elif tag == 'replace':
            for i in range(i1, i2):
                a_html.append(DEL_START + a_token_strings[i] + DEL_END)
            for j in range(j1, j2):
                b_html.append(INS_START + b_token_strings[j] + INS_END)
        elif tag == 'delete':
            for i in range(i1, i2):
                a_html.append(DEL_START + a_token_strings[i] + DEL_END)
        elif tag == 'insert':
            for j in range(j1, j2):
                b_html.append(INS_START + b_token_strings[j] + INS_END)
    
    return ''.join(a_html), ''.join(b_html)

def escape_html(text):
    """Escapa caracteres HTML de forma segura"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def compare_texts_enhanced(texto_original, texto_modificado):
    """
    Versão aprimorada para comparação de textos com melhor detecção de diferenças.
    Utiliza diff_match_patch para uma comparação mais precisa e garante que as 
    marcações HTML sejam aplicadas corretamente.
    
    Args:
        texto_original: Texto da versão original
        texto_modificado: Texto da versão modificada
        
    Returns:
        Tupla com (html_original, html_modificado) contendo as diferenças destacadas
    """
    try:
        # Quebrar em parágrafos para facilitar a comparação
        paragrafos_original = texto_original.split('\n')
        paragrafos_modificado = texto_modificado.split('\n')
        
        # Criar objetos para armazenar os resultados
        html_original = []
        html_modificado = []
        
        # Comparador de parágrafos
        dmp = diff_match_patch()
        
        # Usar SequenceMatcher para alinhar parágrafos
        s = difflib.SequenceMatcher(None, paragrafos_original, paragrafos_modificado)
        
        for op, i1, i2, j1, j2 in s.get_opcodes():
            if op == 'equal':
                # Parágrafos iguais
                for k in range(i1, i2):
                    texto_escapado = escape_html(paragrafos_original[k])
                    html_original.append(texto_escapado)
                    html_modificado.append(texto_escapado)
            
            elif op == 'replace':
                # Parágrafos modificados - comparar detalhadamente
                for i in range(i1, i2):
                    if i < len(paragrafos_original):
                        para_original = paragrafos_original[i]
                        
                        # Encontrar o parágrafo modificado correspondente
                        j_idx = min(j1 + (i - i1), j2 - 1) if j1 < j2 else -1
                        
                        if j_idx >= 0 and j_idx < len(paragrafos_modificado):
                            para_modificado = paragrafos_modificado[j_idx]
                            
                            # Comparar os textos dos parágrafos
                            diffs = dmp.diff_main(para_original, para_modificado)
                            dmp.diff_cleanupSemantic(diffs)
                            
                            # Processar o lado original
                            original_parts = []
                            for d_op, texto in diffs:
                                texto_esc = escape_html(texto)
                                if d_op == 0:  # Texto não modificado
                                    original_parts.append(texto_esc)
                                elif d_op == -1:  # Texto removido
                                    original_parts.append(f'{DEL_START}{texto_esc}{DEL_END}')
                            
                            html_original.append(''.join(original_parts))
                        else:
                            # Parágrafo completamente removido
                            html_original.append(f'{DEL_START}{escape_html(para_original)}{DEL_END}')
                
                # Processar o lado modificado
                for j in range(j1, j2):
                    if j < len(paragrafos_modificado):
                        para_modificado = paragrafos_modificado[j]
                        
                        # Encontrar o parágrafo original correspondente
                        i_idx = min(i1 + (j - j1), i2 - 1) if i1 < i2 else -1
                        
                        if i_idx >= 0 and i_idx < len(paragrafos_original):
                            para_original = paragrafos_original[i_idx]
                            
                            # Comparar os textos dos parágrafos
                            diffs = dmp.diff_main(para_original, para_modificado)
                            dmp.diff_cleanupSemantic(diffs)
                            
                            # Processar o lado modificado
                            modificado_parts = []
                            for d_op, texto in diffs:
                                texto_esc = escape_html(texto)
                                if d_op == 0:  # Texto não modificado
                                    modificado_parts.append(texto_esc)
                                elif d_op == 1:  # Texto adicionado
                                    modificado_parts.append(f'{INS_START}{texto_esc}{INS_END}')
                            
                            html_modificado.append(''.join(modificado_parts))
                        else:
                            # Parágrafo completamente adicionado
                            html_modificado.append(f'{INS_START}{escape_html(para_modificado)}{INS_END}')
            
            elif op == 'delete':
                # Parágrafos removidos
                for i in range(i1, i2):
                    if i < len(paragrafos_original):
                        html_original.append(f'{DEL_START}{escape_html(paragrafos_original[i])}{DEL_END}')
            
            elif op == 'insert':
                # Parágrafos adicionados
                for j in range(j1, j2):
                    if j < len(paragrafos_modificado):
                        html_modificado.append(f'{INS_START}{escape_html(paragrafos_modificado[j])}{INS_END}')
        
        # Converter listas para strings HTML com quebras de linha
        return '<br>'.join(html_original), '<br>'.join(html_modificado)
    
    except Exception as e:
        logger.error(f"Erro na comparação de textos: {e}")
        # Fallback para o método simples em caso de erro
        return render_html_diff(texto_original, texto_modificado)