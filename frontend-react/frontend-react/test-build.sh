#!/bin/bash

echo "================================================"
echo "Legal Pro V2 - Teste de Build Frontend"
echo "================================================"
echo ""

cd "$(dirname "$0")"

echo "📦 Instalando dependências..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo ""
echo "🔨 Testando build de produção..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build falhou"
    exit 1
fi

echo ""
echo "✅ Build passou!"
echo ""
echo "📊 Arquivos gerados:"
ls -lh dist/

echo ""
echo "================================================"
echo "✅ TUDO OK! Pronto para deploy no Vercel"
echo "================================================"
echo ""
echo "Próximos passos:"
echo "1. Vá em vercel.com"
echo "2. Configure Root Directory: frontend-react/frontend-react"
echo "3. Adicione VITE_API_URL nas variáveis de ambiente"
echo "4. Deploy!"
