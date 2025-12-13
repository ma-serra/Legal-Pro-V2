#!/bin/bash

# Script bash simplificado para update GitHub
# Legal Design Pro V2

echo "🚀 LEGAL DESIGN PRO V2 - GitHub Update Script"
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar status
show_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verifica se está em um repositório git
if [ ! -d ".git" ]; then
    show_error "Este não é um repositório git!"
    exit 1
fi

# Verifica status do git
show_status "Verificando status do repositório..."
git_status=$(git status --porcelain)

if [ -z "$git_status" ]; then
    show_success "Repositório está limpo, nenhuma alteração para commit"
    exit 0
fi

# Mostra arquivos modificados
show_status "Arquivos modificados:"
echo "$git_status"

# Pergunta se quer continuar
echo ""
read -p "Deseja continuar com o commit e push? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[YySs]$ ]]; then
    show_warning "Operação cancelada pelo usuário"
    exit 0
fi

# Adiciona todos os arquivos modificados
show_status "Adicionando arquivos ao stage..."
git add .

if [ $? -eq 0 ]; then
    show_success "Arquivos adicionados com sucesso"
else
    show_error "Erro ao adicionar arquivos"
    exit 1
fi

# Gera mensagem de commit
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
commit_message="🔄 Update Legal Design Pro V2 - $timestamp

✨ Melhorias implementadas:
- Ajustes no scroll para integration-card
- Botão 'Voltar ao Topo' adicionado
- Estrutura de templates reorganizada
- Scripts de automação criados

🔧 Arquivos modificados: $(echo "$git_status" | wc -l) arquivo(s)"

# Aceita mensagem customizada como parâmetro
if [ ! -z "$1" ]; then
    commit_message="$*"
fi

# Faz commit
show_status "Fazendo commit..."
git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    show_success "Commit realizado com sucesso"
else
    show_error "Erro ao fazer commit"
    exit 1
fi

# Obtém branch atual
current_branch=$(git branch --show-current)
show_status "Branch atual: $current_branch"

# Faz push
show_status "Fazendo push para GitHub..."
git push origin "$current_branch"

if [ $? -eq 0 ]; then
    show_success "Push realizado com sucesso!"
    echo ""
    echo "🎉 Update concluído com sucesso!"
    echo "📦 Alterações enviadas para o GitHub"
else
    show_error "Erro ao fazer push"
    exit 1
fi

echo ""
echo "=============================================="
echo "✅ Processo finalizado com sucesso!"