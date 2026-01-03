#!/bin/bash

# ============================================
# Legal Pro V2 - Script Automático de Deploy
# ============================================

set -e  # Para ao primeiro erro

echo "================================================"
echo "🚀 Legal Pro V2 - Deploy Automático"
echo "================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Vercel CLI está instalado
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI não encontrado. Instalando...${NC}"
    npm install -g vercel
fi

echo -e "${GREEN}✅ Vercel CLI instalado${NC}"
echo ""

# Ir para o diretório do frontend
cd "$(dirname "$0")"
echo "📂 Diretório atual: $(pwd)"
echo ""

# Verificar se tem node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
else
    echo -e "${GREEN}✅ Dependências já instaladas${NC}"
fi

echo ""
echo "🔨 Testando build..."
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build falhou! Corrija os erros antes de fazer deploy.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build passou!${NC}"
echo ""

echo "================================================"
echo "🎯 Fazendo Deploy no Vercel"
echo "================================================"
echo ""
echo "IMPORTANTE: Você será solicitado a:"
echo "1. Fazer login no Vercel (se ainda não logou)"
echo "2. Vincular este projeto"
echo "3. Confirmar configurações"
echo ""
echo "Pressione ENTER para continuar..."
read

# Deploy no Vercel
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo -e "${GREEN}✅ DEPLOY COMPLETO!${NC}"
    echo "================================================"
    echo ""
    echo "Seu site está no ar!"
    echo "Vercel forneceu a URL acima ⬆️"
    echo ""
    echo "Próximos passos:"
    echo "1. Abra a URL no navegador"
    echo "2. Teste o login"
    echo "3. Verifique se está conectando ao backend"
    echo ""
else
    echo -e "${RED}❌ Deploy falhou. Verifique os erros acima.${NC}"
    exit 1
fi
