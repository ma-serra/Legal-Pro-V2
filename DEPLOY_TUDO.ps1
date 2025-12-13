# ===================================
# DEPLOY BACKEND (Railway)
# ===================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY BACKEND - RAILWAY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navegar para diretório do backend
Set-Location "h:/Meu Drive/Sistemas/Marketing Hub/backend-flask"

# Verificar status
Write-Host "📊 Status do Git:" -ForegroundColor Yellow
git status --short

# Add todas as mudanças
Write-Host "`n📦 Adicionando arquivos..." -ForegroundColor Yellow
git add -A

# Commit
Write-Host "`n💾 Criando commit..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "deploy: Force Railway deployment - $timestamp"

# Push
Write-Host "`n📤 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Backend push concluído!" -ForegroundColor Green
Write-Host "⏳ Aguardando Railway detectar mudanças..." -ForegroundColor Yellow
Write-Host "   URL: https://legal-pro-saas.up.railway.app`n" -ForegroundColor Cyan

# ===================================
# DEPLOY FRONTEND (Vercel)
# ===================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY FRONTEND - VERCEL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Navegar para diretório do frontend
Set-Location "h:/Meu Drive/Sistemas/Marketing Hub/frontend-react/frontend-react"

# Verificar status
Write-Host "📊 Status do Git:" -ForegroundColor Yellow
git status --short

# Add todas as mudanças
Write-Host "`n📦 Adicionando arquivos..." -ForegroundColor Yellow
git add -A

# Commit
Write-Host "`n💾 Criando commit..." -ForegroundColor Yellow
git commit -m "deploy: Force Vercel deployment - $timestamp"

# Push
Write-Host "`n📤 Enviando para GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Frontend push concluído!" -ForegroundColor Green
Write-Host "⏳ Aguardando Vercel detectar mudanças..." -ForegroundColor Yellow
Write-Host "   URL: https://hub-legal-pro.vercel.app`n" -ForegroundColor Cyan

# ===================================
# RESUMO
# ===================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYS INICIADOS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Backend (Railway):"
Write-Host "  - Código enviado para GitHub ✅"
Write-Host "  - Deploy iniciará automaticamente"
Write-Host "  - Tempo estimado: 2-3 minutos"
Write-Host "  - Verificar em: https://railway.app`n"

Write-Host "Frontend (Vercel):"
Write-Host "  - Código enviado para GitHub ✅"
Write-Host "  - Deploy iniciará automaticamente"
Write-Host "  - Tempo estimado: 2-3 minutos"
Write-Host "  - Verificar em: https://vercel.com`n"

Write-Host "🎯 Próximos Passos:" -ForegroundColor Yellow
Write-Host "1. Aguardar 2-3 minutos"
Write-Host "2. Verificar logs no Railway e Vercel"
Write-Host "3. Testar: https://hub-legal-pro.vercel.app"
Write-Host "4. Sistema deve entrar direto sem login!`n"

# Voltar para diretório raiz
Set-Location "h:/Meu Drive/Sistemas/Marketing Hub"

Write-Host "✨ Processo concluído!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
