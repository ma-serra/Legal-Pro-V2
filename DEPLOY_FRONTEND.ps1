# ===================================
# DEPLOY RÁPIDO - FRONTEND APENAS
# ===================================

Write-Host "`n🚀 DEPLOY FRONTEND - VERCEL`n" -ForegroundColor Cyan

Set-Location "h:/Meu Drive/Sistemas/Marketing Hub/frontend-react/frontend-react"

git add -A
git commit -m "deploy: Force Vercel deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main

Write-Host "`n✅ Frontend enviado!" -ForegroundColor Green
Write-Host "⏳ Deploy iniciará em ~30 segundos" -ForegroundColor Yellow
Write-Host "📍 https://hub-legal-pro.vercel.app`n" -ForegroundColor Cyan
