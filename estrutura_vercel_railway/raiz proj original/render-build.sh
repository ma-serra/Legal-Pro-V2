#!/bin/bash
# Script de build personalizado para o Render
# Garante que todas as dependências e estruturas sejam criadas

echo "🚀 Iniciando build personalizado para Legal Design Pro V2..."

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
if [ -f "requirements-render.txt" ]; then
    echo "Usando requirements-render.txt (otimizado para Render)"
    pip install -r requirements-render.txt
elif [ -f "requirements.txt" ]; then
    echo "Usando requirements.txt (fallback)"
    pip install -r requirements.txt
else
    echo "❌ Nenhum arquivo de dependências encontrado!"
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p logs
mkdir -p uploads
mkdir -p temp
mkdir -p static/exports
mkdir -p static/uploads
mkdir -p instance

# Criar arquivos de log vazios
touch logs/debug.log
touch logs/transcricao_debug.log
touch logs/transcricao_completa.log

# Configurar permissões
chmod 755 logs uploads temp static/exports static/uploads
chmod 644 logs/*.log

echo "✅ Build personalizado concluído com sucesso!"
echo "📋 Estrutura criada:"
echo "  - logs/ (com arquivos de log)"
echo "  - uploads/ (para arquivos enviados)"
echo "  - temp/ (para processamento temporário)"
echo "  - static/exports/ (para arquivos exportados)"
echo "  - instance/ (para configurações)"

echo "🎯 Sistema pronto para executar com todas as funcionalidades!"