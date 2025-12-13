#!/usr/bin/env python3
"""
Correção de vulnerabilidades SQL injection no app.py
"""

import re

def fix_sql_vulnerabilities():
    """Corrige todas as vulnerabilidades SQL injection identificadas"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão inseguro: text(f"SELECT COUNT(*) FROM {table}")
    unsafe_pattern = r'text\(f"SELECT COUNT\(\*\) FROM \{table\}"\)'
    safe_replacement = 'text("SELECT COUNT(*) FROM " + table)'
    
    # Adicionar validação antes de cada uso
    validation_code = '''# Validar nome da tabela para prevenir SQL injection
                        if not re.match(r'^[a-zA-Z0-9_]+$', table):
                            continue
                        '''
    
    # Encontrar todas as ocorrências
    matches = list(re.finditer(unsafe_pattern, content))
    
    print(f"Encontradas {len(matches)} vulnerabilidades SQL injection")
    
    # Substituir de trás para frente para não afetar posições
    for match in reversed(matches):
        start, end = match.span()
        
        # Encontrar o início da linha para adicionar validação
        line_start = content.rfind('\n', 0, start) + 1
        line_content = content[line_start:end]
        
        # Verificar se já tem validação
        if 'if not re.match' not in content[max(0, line_start - 200):line_start]:
            # Adicionar validação antes da query
            indent = len(line_content) - len(line_content.lstrip())
            validation = ' ' * indent + validation_code.strip().replace('\n                        ', '\n' + ' ' * indent)
            
            new_content = (content[:line_start] + 
                          validation + '\n' + 
                          content[line_start:start] + 
                          safe_replacement + 
                          content[end:])
        else:
            # Apenas substituir a query
            new_content = content[:start] + safe_replacement + content[end:]
        
        content = new_content
    
    # Salvar arquivo corrigido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Vulnerabilidades SQL injection corrigidas")

if __name__ == "__main__":
    fix_sql_vulnerabilities()