"""
Script para remover as rotas conflitantes /validar e /validacao-multi-agente
Mantém apenas /validacao-multi-agente-expandida como rota principal
"""

import re

def remover_rotas_conflitantes():
    """Remove as rotas /validar e /validacao-multi-agente do app.py"""
    
    print("Removendo rotas conflitantes...")
    
    # Ler o arquivo
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fazer backup
    with open('app.py.backup_before_removal', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Dividir em linhas
    lines = content.split('\n')
    
    # Encontrar e remover a rota /validar
    new_lines = []
    skip_until_next_def = False
    
    for i, line in enumerate(lines):
        # Detectar início da rota /validar
        if "@app.route('/validar')" in line:
            print(f"✓ Removendo rota /validar na linha {i+1}")
            skip_until_next_def = True
            continue
        
        # Detectar início da rota /validacao-multi-agente
        if "@app.route('/validacao-multi-agente'" in line:
            print(f"✓ Removendo rota /validacao-multi-agente na linha {i+1}")
            skip_until_next_def = True
            continue
        
        # Parar de pular quando encontrar próxima definição de função ou rota
        if skip_until_next_def:
            if (line.strip().startswith('def ') and 
                not line.strip().startswith('def validar_redirect') and
                not line.strip().startswith('def validacao_multi_agente')):
                skip_until_next_def = False
                new_lines.append(line)
            elif line.strip().startswith('@app.route') and '/validar' not in line:
                skip_until_next_def = False
                new_lines.append(line)
            # Continuar pulando esta linha
            continue
        
        new_lines.append(line)
    
    # Remover referências nas funções que redirecionam para as rotas removidas
    final_lines = []
    for line in new_lines:
        # Substituir redirecionamentos para validacao_multi_agente por validacao_multi_agente_expandida
        if "redirect(url_for('validacao_multi_agente'))" in line:
            line = line.replace("redirect(url_for('validacao_multi_agente'))", 
                              "redirect(url_for('validacao_multi_agente_expandida'))")
            print("✓ Redirecionamento atualizado para validacao_multi_agente_expandida")
        
        final_lines.append(line)
    
    # Escrever arquivo modificado
    new_content = '\n'.join(final_lines)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Rotas conflitantes removidas com sucesso")
    print("✓ Backup criado: app.py.backup_before_removal")

def verificar_rotas_restantes():
    """Verifica quais rotas de validação ainda existem"""
    
    print("\nVerificando rotas restantes...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    rotas_encontradas = []
    
    # Buscar todas as rotas relacionadas
    if "@app.route('/validar')" in content:
        rotas_encontradas.append('/validar')
    
    if "@app.route('/validacao-multi-agente'" in content:
        rotas_encontradas.append('/validacao-multi-agente')
    
    if "@app.route('/validacao-multi-agente-expandida'" in content:
        rotas_encontradas.append('/validacao-multi-agente-expandida')
    
    if rotas_encontradas:
        print(f"Rotas encontradas: {rotas_encontradas}")
    else:
        print("Nenhuma rota de validação encontrada")
    
    return rotas_encontradas

def criar_relatorio_remocao():
    """Cria relatório da remoção das rotas"""
    
    relatorio = """
# Relatório de Remoção de Rotas Conflitantes

## Rotas Removidas:
1. `/validar` - Rota de redirecionamento removida
2. `/validacao-multi-agente` - Rota antiga removida

## Rota Mantida:
- `/validacao-multi-agente-expandida` - Rota principal do sistema

## Alterações Realizadas:
- Remoção completa das funções validar_redirect() e validacao_multi_agente()
- Atualização de redirecionamentos para apontar para validacao_multi_agente_expandida
- Backup criado antes das modificações

## Resultado:
- Eliminação de conflitos de rotas
- Sistema unificado com uma única rota de validação
- Melhor organização e manutenibilidade do código

## Data da Remoção:
""" + str(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('relatorio_remocao_rotas.md', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("✓ Relatório criado: relatorio_remocao_rotas.md")

if __name__ == "__main__":
    print("=== REMOÇÃO DE ROTAS CONFLITANTES ===\n")
    
    remover_rotas_conflitantes()
    rotas_restantes = verificar_rotas_restantes()
    criar_relatorio_remocao()
    
    print("\n=== REMOÇÃO CONCLUÍDA ===")
    
    if '/validacao-multi-agente-expandida' in rotas_restantes:
        print("✓ Sistema mantém apenas a rota principal: /validacao-multi-agente-expandida")
    else:
        print("⚠️ Atenção: Rota principal não encontrada")