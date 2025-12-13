# ===================================
# DEPLOY RÁPIDO - BACKEND APENAS
# ===================================

Write-Host "`n🚀 DEPLOY BACKEND - RAILWAY`n" -ForegroundColor Cyan

Set-Location "h:/Meu Drive/Sistemas/Marketing Hub/backend-flask"

git add -A
git commit -m "deploy: Force Railway deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main

Write-Host "`n✅ Backend enviado!" -ForegroundColor Green
Write-Host "⏳ Deploy iniciará em ~30 segundos" -ForegroundColor Yellow
Write-Host "📍 https://legal-pro-saas.up.railway.app`n" -ForegroundColor Cyan
