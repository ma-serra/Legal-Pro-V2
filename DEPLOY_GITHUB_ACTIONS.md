# 🚀 DEPLOY AUTOMÁTICO COM GITHUB ACTIONS

## ✅ Solução ZERO comandos

O deploy agora é **automático pelo GitHub**. Não precisa rodar nada no terminal.

---

## 📋 Como Funciona

Quando você faz **push** para este branch, o GitHub automaticamente:
1. ✅ Instala dependências
2. ✅ Testa o build
3. ✅ Faz deploy no Vercel
4. ✅ Te avisa se deu erro

**Você não faz NADA.** O GitHub faz tudo.

---

## ⚙️ Configuração (SÓ UMA VEZ)

### Passo 1: Obter Token do Vercel

1. Vá em https://vercel.com/account/tokens
2. Clique em "Create Token"
3. Nome: `github-actions`
4. Copie o token (começa com `vercel_...`)

### Passo 2: Configurar no GitHub

1. Vá no repositório GitHub: https://github.com/ma-serra/Legal-Pro-V2
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

Adicione estes 3 secrets:

**Secret 1:**
- Name: `VERCEL_TOKEN`
- Value: Cole o token que você copiou

**Secret 2:**  
- Name: `VERCEL_ORG_ID`
- Value: Seu Organization ID do Vercel (veja abaixo como pegar)

**Secret 3:**
- Name: `VERCEL_PROJECT_ID`
- Value: Seu Project ID do Vercel (veja abaixo como pegar)

### Como Pegar Organization ID e Project ID

1. Vá em https://vercel.com
2. Clique no seu projeto (ou crie um novo)
3. Settings → General
4. Copie:
   - **Project ID** (está em "Project ID")
   - **Organization ID** (está em "Organization ID" ou "Team ID")

---

## 🎯 Depois de Configurar

Pronto! Agora **todo push** faz deploy automaticamente.

Para ver o deploy:
1. Vá em GitHub → Actions
2. Veja o workflow "Deploy Frontend to Vercel"
3. Acompanhe o progresso

Se der erro, o GitHub te avisa por email.

---

## 🔧 Deploy Manual (sem GitHub Actions)

Se não quiser usar GitHub Actions, use o site do Vercel:

### Opção 1: Importar do GitHub (MAIS FÁCIL)

1. https://vercel.com
2. Login com GitHub
3. "Add New" → "Project"
4. "Import Git Repository"
5. Selecione: Legal-Pro-V2
6. Configure:
   - **Root Directory:** `frontend-react/frontend-react`
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
7. Environment Variables:
   - `VITE_API_URL` = `https://legal-pro-saas.up.railway.app`
8. Deploy!

O Vercel vai fazer deploy automaticamente em cada push.

### Opção 2: Usar Vercel CLI

Se você REALMENTE quer usar CLI:

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Ir pro frontend
cd frontend-react/frontend-react

# 3. Login
vercel login

# 4. Deploy
vercel --prod
```

---

## ❌ Por Que o Script Anterior Não Funcionou?

Os scripts que criei (`deploy-vercel.sh`) **funcionam**, mas:
- Exigem instalar Vercel CLI
- Podem dar erro de permissão
- Requerem login manual

**GitHub Actions é MELHOR porque:**
- ✅ Zero instalação
- ✅ Zero comandos
- ✅ Deploy automático
- ✅ Logs no GitHub
- ✅ Email se der erro

---

## 🎯 Resumo

**Recomendado:** Use GitHub Actions (configurar uma vez, funciona sempre)

**Alternativa:** Use o site do Vercel (importar do GitHub)

**Não recomendado:** Scripts bash (muitas dependências, pode dar erro)

---

## 📞 Precisa de Ajuda?

Se der erro:
1. Verifique GitHub Actions logs
2. Verifique se configurou os 3 secrets
3. Me chame com print do erro

---

**Arquivo criado:** `.github/workflows/deploy-frontend.yml`
**Status:** Pronto para usar após configurar os secrets
