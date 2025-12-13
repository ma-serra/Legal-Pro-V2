#!/usr/bin/env python3
"""
Script automatizado para atualizar GitHub com arquivos MCP
Legal Design Pro V2 - MultiAgentMatriz_Cursor
"""

import subprocess
import os
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar colorama para cores no terminal
init(autoreset=True)

def run_command(command, description=""):
    """Executa comando e retorna resultado"""
    try:
        print(f"{Fore.BLUE}🔧 {description}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Executando: {command}{Style.RESET_ALL}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ Sucesso!{Style.RESET_ALL}")
            if result.stdout.strip():
                print(f"{Fore.WHITE}{result.stdout.strip()}{Style.RESET_ALL}")
            return True, result.stdout
        else:
            print(f"{Fore.RED}❌ Erro!{Style.RESET_ALL}")
            if result.stderr.strip():
                print(f"{Fore.RED}{result.stderr.strip()}{Style.RESET_ALL}")
            return False, result.stderr
            
    except Exception as e:
        print(f"{Fore.RED}❌ Exceção: {str(e)}{Style.RESET_ALL}")
        return False, str(e)

def check_git_status():
    """Verifica status do git"""
    print(f"{Fore.YELLOW}🔍 VERIFICANDO STATUS DO GIT{Style.RESET_ALL}")
    
    # Verificar se é repositório git
    if not os.path.exists('.git'):
        print(f"{Fore.RED}❌ Não é um repositório Git{Style.RESET_ALL}")
        return False
    
    # Verificar remote
    success, output = run_command("git remote -v", "Verificando remotes")
    if not success:
        return False
    
    # Verificar se remote aponta para repositório correto
    if "MultiAgentMatriz_Cursor" not in output:
        print(f"{Fore.YELLOW}⚠️ Remote incorreto detectado{Style.RESET_ALL}")
        
        # Corrigir remote
        success, _ = run_command(
            "git remote set-url origin https://github.com/arsdatascience/MultiAgentMatriz_Cursor.git",
            "Corrigindo URL do remote"
        )
        if not success:
            return False
    
    return True

def categorize_files():
    """Categoriza arquivos para commit organizado"""
    categories = {
        "mcp_servers": [],
        "config_files": [],
        "documentation": [],
        "scripts": []
    }
    
    # Verificar arquivos MCP
    mcp_files = [
        'mcp_server/legal_design_server.py',
        'mcp_server/database_server.py',
        'mcp_server/ai_apis_server.py',
        'mcp_server/__init__.py'
    ]
    
    for file in mcp_files:
        if os.path.exists(file):
            categories["mcp_servers"].append(file)
    
    # Arquivos de configuração
    config_files = [
        'cursor-mcp-config.json',
        '.env.example'
    ]
    
    for file in config_files:
        if os.path.exists(file):
            categories["config_files"].append(file)
    
    # Documentação
    doc_files = [
        'CONFIGURACAO_MCP_CURSOR.md',
        'MCP_QUICK_SETUP.md', 
        'ALTERNATIVAS_MCP_COMPARACAO.md',
        'MIGRACAO_CONTINUE_DEV.md',
        'README_GITHUB_UPDATE.md'
    ]
    
    for file in doc_files:
        if os.path.exists(file):
            categories["documentation"].append(file)
    
    # Scripts
    script_files = [
        'check_github_status.py',
        'update_github.py'
    ]
    
    for file in script_files:
        if os.path.exists(file):
            categories["scripts"].append(file)
    
    return categories

def add_files_to_git(categories):
    """Adiciona arquivos categorizados ao git"""
    print(f"{Fore.YELLOW}📁 ADICIONANDO ARQUIVOS AO GIT{Style.RESET_ALL}")
    
    total_files = 0
    
    for category, files in categories.items():
        if files:
            print(f"\n{Fore.CYAN}📂 Categoria: {category.upper()}{Style.RESET_ALL}")
            for file in files:
                success, _ = run_command(f"git add {file}", f"Adicionando {file}")
                if success:
                    total_files += 1
                    print(f"  ✅ {file}")
                else:
                    print(f"  ❌ {file}")
    
    return total_files

def create_commit_message(categories):
    """Cria mensagem de commit detalhada"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    message = f"""feat: Add MCP Tools integration for Legal Design Pro V2

🔧 MCP SERVERS ({len(categories['mcp_servers'])} files):
- legal_design_server.py: 6 ferramentas principais (análise multi-agente, transcrição, mapas mentais)
- database_server.py: 5 ferramentas PostgreSQL/Qdrant (estrutura, busca, backup)
- ai_apis_server.py: 5 ferramentas APIs IA (OpenAI, Anthropic, Google, monitoramento)

📋 CONFIGURAÇÃO ({len(categories['config_files'])} files):
- cursor-mcp-config.json: Setup automático para Cursor IDE
- Variáveis de ambiente organizadas

📚 DOCUMENTAÇÃO ({len(categories['documentation'])} files):
- Guia completo de configuração MCP
- Setup rápido (3 minutos)
- Comparação com ferramentas alternativas (Continue.dev, Windsurf)
- Migração recomendada para IA local

🛠️ UTILITÁRIOS ({len(categories['scripts'])} files):
- Scripts de verificação GitHub
- Automação de updates

✨ FEATURES:
- 16 ferramentas MCP integradas no Cursor
- Análise jurídica via chat natural
- Gestão completa PostgreSQL + Qdrant
- Monitoramento APIs em tempo real
- Setup híbrido com IA local

🎯 USO:
1. Import cursor-mcp-config.json no Cursor
2. Comandos: /legal, /agents, /db, /security
3. Análise: "Use test_multi_agent_system para analisar contrato"

Created: {timestamp}"""
    
    return message

def push_to_github():
    """Faz push para GitHub"""
    print(f"{Fore.YELLOW}🚀 FAZENDO PUSH PARA GITHUB{Style.RESET_ALL}")
    
    # Verificar se há algo para commit
    success, output = run_command("git status --porcelain", "Verificando mudanças")
    if not success:
        return False
    
    if not output.strip():
        print(f"{Fore.YELLOW}⚠️ Nenhuma mudança para commit{Style.RESET_ALL}")
        return True
    
    # Fazer push
    success, output = run_command("git push origin main", "Fazendo push para GitHub")
    
    if success:
        print(f"{Fore.GREEN}🎉 PUSH REALIZADO COM SUCESSO!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔗 Repositório: https://github.com/arsdatascience/MultiAgentMatriz_Cursor{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ Erro no push{Style.RESET_ALL}")
        return False

def main():
    """Função principal"""
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🚀 GITHUB UPDATE - LEGAL DESIGN PRO V2 + MCP TOOLS{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    
    # 1. Verificar git
    if not check_git_status():
        print(f"{Fore.RED}❌ Falha na verificação do Git{Style.RESET_ALL}")
        return False
    
    # 2. Categorizar arquivos
    categories = categorize_files()
    
    # 3. Mostrar resumo
    total_files = sum(len(files) for files in categories.values())
    print(f"\n{Fore.CYAN}📊 RESUMO DE ARQUIVOS:{Style.RESET_ALL}")
    for category, files in categories.items():
        if files:
            print(f"  {Fore.GREEN}{category}: {len(files)} arquivos{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Total: {total_files} arquivos{Style.RESET_ALL}")
    
    if total_files == 0:
        print(f"{Fore.YELLOW}⚠️ Nenhum arquivo MCP encontrado{Style.RESET_ALL}")
        return False
    
    # 4. Confirmar
    confirm = input(f"\n{Fore.YELLOW}📤 Fazer push de {total_files} arquivos para GitHub? (y/N): {Style.RESET_ALL}")
    if confirm.lower() not in ['y', 'yes', 's', 'sim']:
        print(f"{Fore.YELLOW}⏸️ Operação cancelada{Style.RESET_ALL}")
        return False
    
    # 5. Adicionar arquivos
    added_files = add_files_to_git(categories)
    if added_files == 0:
        print(f"{Fore.RED}❌ Nenhum arquivo foi adicionado{Style.RESET_ALL}")
        return False
    
    # 6. Fazer commit
    commit_message = create_commit_message(categories)
    success, _ = run_command(f'git commit -m "{commit_message}"', "Criando commit")
    if not success:
        print(f"{Fore.RED}❌ Falha no commit{Style.RESET_ALL}")
        return False
    
    # 7. Push para GitHub
    if push_to_github():
        print(f"\n{Fore.GREEN}✅ ATUALIZAÇÃO GITHUB COMPLETA!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔗 Verifique: https://github.com/arsdatascience/MultiAgentMatriz_Cursor{Style.RESET_ALL}")
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏸️ Operação cancelada pelo usuário{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro inesperado: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)