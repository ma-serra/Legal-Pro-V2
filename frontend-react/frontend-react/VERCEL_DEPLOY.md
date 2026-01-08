# 🚀 Guia de Deploy no Vercel - Legal Pro V2

## ✅ Status: Pronto para Deploy

O frontend está configurado e testado. Build passa sem erros.

---

## 📋 Pré-requisitos

1. Conta no [Vercel](https://vercel.com)
2. Repositório conectado ao GitHub
3. Backend rodando no Railway (para obter a URL)

---

## 🔧 Configuração do Vercel

### Passo 1: Criar Projeto no Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Clique em **"Add New Project"**
3. Importe o repositório **Legal-Pro-V2**

### Passo 2: Configurações do Build

Configure exatamente assim:

```
Framework Preset: Vite
Root Directory: frontend-react/frontend-react
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Node Version: 18.x
```

**IMPORTANTE:** O `Root Directory` DEVE ser `frontend-react/frontend-react` (não apenas `frontend-react`)

### Passo 3: Variáveis de Ambiente

Adicione em **Settings → Environment Variables**:

```bash
VITE_API_URL=https://seu-backend.up.railway.app
```

**Substitua** `seu-backend.up.railway.app` pela URL real do seu backend Railway.

**IMPORTANTE:** 
- Não coloque `/` no final da URL
- Use HTTPS (não HTTP)
- Verifique se o backend está rodando antes

### Passo 4: Deploy

1. Clique em **"Deploy"**
2. Aguarde 2-5 minutos
3. Vercel fornecerá uma URL (ex: `https://legal-pro-v2.vercel.app`)

---

## ✅ Verificações Pós-Deploy

### 1. Verificar se o site carrega

```bash
curl -I https://seu-app.vercel.app
```

Deve retornar `200 OK`

### 2. Testar no navegador

1. Abra a URL no navegador
2. Deve carregar a landing page
3. Clique em "Login"
4. Tente fazer login com credenciais válidas

### 3. Verificar Console (F12)

Abra DevTools (F12) e verifique:
- ✅ Sem erros de CORS
- ✅ Sem erros 404
- ✅ API calls chegando ao backend

---

## 🐛 Troubleshooting

### Erro: "Build failed"

**Causa:** Root directory incorreto

**Solução:**
1. Vá em Settings → General
2. Configure `Root Directory: frontend-react/frontend-react`
3. Redeploy

### Erro: "Cannot connect to backend"

**Causa:** VITE_API_URL incorreto ou backend offline

**Solução:**
1. Verifique se backend está online: `curl https://seu-backend.railway.app/health`
2. Verifique VITE_API_URL em Settings → Environment Variables
3. Redeploy após corrigir

### Erro: CORS

**Causa:** Backend não está aceitando requisições do Vercel

**Solução:**
1. No backend, verifique se CORS está habilitado
2. Adicione a URL do Vercel nas origens permitidas
3. Redeploy do backend

### Erro: "Page not found" ao acessar rotas

**Causa:** Rewrites não configurados (mas já estão em vercel.json)

**Solução:**
- Verifique se `vercel.json` existe na raiz do projeto
- Deve ter rewrites configurados (já está)

### Erro: TypeScript build error

**Causa:** Erros de tipo no código

**Solução:**
```bash
cd frontend-react/frontend-react
npm run build
# Veja os erros e corrija
```

---

## 📊 Build Local (Testar Antes)

Antes de fazer deploy, teste localmente:

```bash
cd frontend-react/frontend-react

# Instalar dependências
npm install

# Testar dev server
npm run dev
# Acesse: http://localhost:5173

# Testar build de produção
npm run build

# Preview do build
npm run preview
# Acesse: http://localhost:4173
```

Se tudo funcionar localmente, funcionará no Vercel.

---

## 🔐 Segurança

O `vercel.json` já inclui headers de segurança:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

---

## 📝 Checklist Final

Antes de considerar o deploy completo:

- [ ] Build passa sem erros (`npm run build`)
- [ ] Dev server funciona (`npm run dev`)
- [ ] VITE_API_URL configurado no Vercel
- [ ] Root Directory = `frontend-react/frontend-react`
- [ ] Backend está online no Railway
- [ ] Site carrega no navegador
- [ ] Login funciona
- [ ] Sem erros de CORS no console
- [ ] Rotas funcionam (não dá 404)

---

## 🎯 Resumo Rápido

```bash
# 1. Vercel → New Project → Importar repo

# 2. Configurar:
Root Directory: frontend-react/frontend-react
Build Command: npm run build
Output Directory: dist

# 3. Environment Variables:
VITE_API_URL=https://seu-backend.up.railway.app

# 4. Deploy e aguardar

# 5. Testar:
- Abrir URL no navegador
- Fazer login
- Verificar console (F12)
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do Vercel (aba "Deployments" → clique no deploy → "View Function Logs")
2. Verifique o console do navegador (F12)
3. Teste localmente primeiro (`npm run build`)
4. Verifique se backend está online (`curl backend-url/health`)

---

**Última atualização:** 2026-01-03
**Testado em:** Vercel CLI 33.x, Node 18.x
