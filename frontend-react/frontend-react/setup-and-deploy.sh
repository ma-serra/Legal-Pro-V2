#!/bin/bash

# Legal Pro V2 - Setup Completo em 1 Comando
# Use: curl -fsSL https://raw.githubusercontent.com/ma-serra/Legal-Pro-V2/copilot/prepare-for-deployment/frontend-react/frontend-react/setup-and-deploy.sh | bash

set -e

echo "🚀 Legal Pro V2 - Setup Automático"
echo ""

# Instalar Vercel CLI se não tiver
if ! command -v vercel &> /dev/null; then
    echo "📦 Instalando Vercel CLI..."
    npm install -g vercel
fi

# Ir para diretório correto
if [ -d "frontend-react/frontend-react" ]; then
    cd frontend-react/frontend-react
elif [ -f "package.json" ]; then
    # Já está no diretório correto
    :
else
    echo "❌ Não encontrei o diretório do frontend"
    echo "Execute este script da raiz do repositório"
    exit 1
fi

echo "✅ Diretório correto: $(pwd)"
echo ""

# Instalar dependências
echo "📦 Instalando dependências..."
npm install

# Build
echo "🔨 Testando build..."
npm run build

# Deploy
echo ""
echo "🚀 Fazendo deploy no Vercel..."
echo "Você precisará fazer login no Vercel."
echo ""

vercel --prod

echo ""
echo "✅ Deploy completo!"
