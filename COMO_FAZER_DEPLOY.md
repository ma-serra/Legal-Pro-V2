# ⚡ DEPLOY - 3 OPÇÕES

## 🥇 Opção 1: GitHub Actions (RECOMENDADO)

**ZERO comandos. Deploy automático.**

1. Configure secrets no GitHub (só uma vez):
   - VERCEL_TOKEN
   - VERCEL_ORG_ID  
   - VERCEL_PROJECT_ID

2. Pronto! Todo push faz deploy automaticamente.

**Ver instruções completas:** `DEPLOY_GITHUB_ACTIONS.md`

---

## 🥈 Opção 2: Site do Vercel (FÁCIL)

1. https://vercel.com
2. Login com GitHub
3. "Add New" → "Project"
4. Import: Legal-Pro-V2
5. Root Directory: `frontend-react/frontend-react`
6. Deploy!

---

## 🥉 Opção 3: Vercel CLI (Manual)

```bash
cd frontend-react/frontend-react
npm install -g vercel
vercel login
vercel --prod
```

---

## ❌ Scripts .sh NÃO FUNCIONAM BEM

Os scripts `deploy-vercel.sh` e similares podem dar erro de:
- Permissão
- Node.js não instalado
- Vercel CLI com problemas

**Use GitHub Actions ou o site do Vercel.**

---

Veja `DEPLOY_GITHUB_ACTIONS.md` para detalhes completos.
