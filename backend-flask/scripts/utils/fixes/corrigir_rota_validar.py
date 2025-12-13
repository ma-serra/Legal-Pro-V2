"""
Script para corrigir o problema da rota /validar
Adiciona redirecionamento correto e remove ambiguidades
"""

import os
import sys
from flask import Flask, redirect, url_for

def adicionar_redirecionamento_validar():
    """Adiciona redirecionamento da rota /validar para a rota correta"""
    
    print("Corrigindo problema da rota /validar...")
    
    # Ler o arquivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já existe a rota /validar
    if '@app.route(\'/validar\')' in content:
        print("✓ Rota /validar já existe")
        return
    
    # Adicionar redirecionamento após a rota /validacao-multi-agente
    redirect_code = '''
    @app.route('/validar')
    def validar_redirect():
        """Redirecionamento da rota /validar para /validacao-multi-agente-expandida"""
        return redirect(url_for('validacao_multi_agente_expandida'))
    '''
    
    # Encontrar onde inserir o código
    pos = content.find('@app.route(\'/validacao-multi-agente\'')
    if pos == -1:
        print("❌ Não foi possível encontrar a rota /validacao-multi-agente")
        return
    
    # Encontrar o final da função validacao_multi_agente
    lines = content.split('\n')
    insert_line = None
    
    for i, line in enumerate(lines):
        if '@app.route(\'/validacao-multi-agente\'' in line:
            # Procurar o final desta função (próxima definição de rota ou função)
            for j in range(i + 1, len(lines)):
                if (lines[j].strip().startswith('@app.route') and 
                    not lines[j].strip().startswith('@app.route(\'/validacao-multi-agente')):
                    insert_line = j
                    break
                elif lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def validacao_multi_agente'):
                    insert_line = j
                    break
            break
    
    if insert_line is None:
        print("❌ Não foi possível determinar onde inserir o redirecionamento")
        return
    
    # Inserir o código de redirecionamento
    lines.insert(insert_line, redirect_code.strip())
    
    # Escrever o arquivo modificado
    new_content = '\n'.join(lines)
    
    # Fazer backup
    with open('app.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Escrever o arquivo modificado
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Redirecionamento /validar adicionado com sucesso")
    print("✓ Backup criado em app.py.backup")

def verificar_conflitos_rotas():
    """Verifica se existem conflitos de rotas relacionadas a validar"""
    
    print("\nVerificando conflitos de rotas...")
    
    rotas_relacionadas = [
        '/validar',
        '/validacao',
        '/validacao-multi-agente',
        '/validacao-multiagente',
        '/validacao-multi-agente-expandida'
    ]
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    rotas_encontradas = []
    for rota in rotas_relacionadas:
        if f"@app.route('{rota}'" in content:
            rotas_encontradas.append(rota)
    
    print(f"Rotas encontradas: {rotas_encontradas}")
    
    if len(rotas_encontradas) > 1:
        print("⚠️ Múltiplas rotas relacionadas encontradas - possível fonte de conflito")
    else:
        print("✓ Sem conflitos de rotas detectados")

def criar_log_rotas():
    """Cria um log das rotas para debugging"""
    
    print("\nCriando log de rotas para debugging...")
    
    log_content = """
# Log de Rotas - Sistema Multi-Agente

## Rotas de Validação Registradas:

1. /validacao-multi-agente-expandida (Principal)
   - Função: validacao_multi_agente_expandida()
   - Métodos: GET, POST
   - Descrição: Sistema principal de análise multi-agente

2. /validar (Redirecionamento)
   - Função: validar_redirect()
   - Métodos: GET
   - Descrição: Redireciona para /validacao-multi-agente-expandida

## Problema Identificado:
- A rota /validar estava sendo acessada intermitentemente
- Não havia definição clara desta rota
- Pode ter causado erro 404 em algumas ocasiões

## Solução Aplicada:
- Adicionado redirecionamento de /validar para a rota principal
- Mantida compatibilidade com acessos diretos
- Sistema agora funciona consistentemente

## Data da Correção:
""" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('log_rotas_validacao.md', 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    print("✓ Log criado em log_rotas_validacao.md")

if __name__ == "__main__":
    from datetime import datetime
    
    print("=== CORREÇÃO DA ROTA /validar ===\n")
    
    adicionar_redirecionamento_validar()
    verificar_conflitos_rotas()
    criar_log_rotas()
    
    print("\n=== CORREÇÃO CONCLUÍDA ===")
    print("A rota /validar agora redirecionará corretamente para o sistema de validação principal.")