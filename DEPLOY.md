# 🚀 Guia de Deploy - Railway & Vercel

Este guia fornece instruções passo a passo para fazer deploy do **Sistema Legal Pro** na Railway (backend) e Vercel (frontend).

## 📋 Pré-requisitos

- Conta no [Railway.app](https://railway.app)
- Conta no [Vercel.com](https://vercel.com)
- Repositório Git (GitHub, GitLab, ou Bitbucket)
- Banco de dados PostgreSQL (recomendado: [Neon](https://neon.tech) ou Railway Postgres)

## 🎯 Visão Geral da Arquitetura

```
┌─────────────────┐       HTTPS        ┌──────────────────┐
│  Frontend React │  ◄──────────────►  │  Backend Flask   │
│  (Vercel)       │                     │  (Railway)       │
└─────────────────┘                     └──────────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  PostgreSQL  │
                                        │  (Neon/RW)   │
                                        └──────────────┘
```

---

## 🔧 Parte 1: Deploy do Backend (Railway)

### 1.1 Preparar o Código

Certifique-se de que todos os arquivos de configuração estão no diretório `backend-flask/`:
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `runtime.txt`
- ✅ `requirements.txt`
- ✅ `.env.example`

### 1.2 Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Conecte seu repositório e selecione o branch principal
5. Railway detectará automaticamente que é um projeto Python

### 1.3 Configurar Banco de Dados PostgreSQL

**Opção A: PostgreSQL no Railway**
1. No projeto Railway, clique em **"New"** → **"Database"** → **"PostgreSQL"**
2. Copie a `DATABASE_URL` gerada

**Opção B: PostgreSQL no Neon (Recomendado)**
1. Crie um projeto em [neon.tech](https://neon.tech)
2. Copie a connection string (formato: `postgresql://user:password@host/dbname`)

### 1.4 Configurar Variáveis de Ambiente

No dashboard do Railway, vá em **"Variables"** e adicione:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Flask Secrets (gere valores seguros)
SECRET_KEY=seu-secret-key-aqui-use-senha-forte
SESSION_SECRET=seu-session-secret-aqui-use-senha-forte
FLASK_ENV=production

# AI API Keys (obrigatório para funcionalidades de IA)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
ASSEMBLYAI_API_KEY=...

# Performance (opcional)
FAST_STARTUP=true
```

> **⚠️ IMPORTANTE:** Gere chaves secretas fortes para `SECRET_KEY` e `SESSION_SECRET`. Você pode usar:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 1.5 Deploy

1. Faça commit e push das alterações para o repositório
2. Railway iniciará o build automaticamente
3. Aguarde o deploy (pode levar 5-10 minutos na primeira vez)
4. Após conclusão, Railway fornecerá uma URL pública (ex: `https://seu-app.up.railway.app`)

### 1.6 Verificar Deploy

Teste o health check:
```bash
curl https://seu-app.up.railway.app/health
```

Deve retornar: `OK`

---

## 🎨 Parte 2: Deploy do Frontend (Vercel)

### 2.1 Preparar o Código

Certifique-se de que todos os arquivos estão em `frontend-react/frontend-react/`:
- ✅ `vercel.json`
- ✅ `.env.example`
- ✅ `package.json`
- ✅ `vite.config.ts`

### 2.2 Criar Projeto no Vercel

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em **"Add New Project"**
3. Importe seu repositório do GitHub
4. Configure o projeto:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend-react/frontend-react`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.3 Configurar Variável de Ambiente

Em **"Environment Variables"**, adicione:

```bash
VITE_API_URL=https://seu-app.up.railway.app
```

> **Substitua** `https://seu-app.up.railway.app` pela URL do seu backend Railway (Parte 1.5).

### 2.4 Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (2-5 minutos)
3. Vercel fornecerá uma URL pública (ex: `https://seu-app.vercel.app`)

### 2.5 Verificar Deploy

1. Acesse a URL do Vercel no navegador
2. Verifique se a interface carrega corretamente
3. Teste a conexão com o backend (login, dados, etc.)

---

## 🔐 Configuração de CORS (Backend)

O backend já está configurado para aceitar requisições do frontend. Se encontrar erros de CORS:

1. Verifique se a URL do Vercel está correta em `VITE_API_URL`
2. Verifique os logs do Railway para erros de CORS
3. Se necessário, adicione configuração CORS específica no `main.py`

---

## 📊 Monitoramento e Logs

### Railway (Backend)
- Acesse o dashboard do projeto
- Clique em **"Deployments"** para ver histórico
- Clique em **"Logs"** para monitorar em tempo real

### Vercel (Frontend)
- Acesse o dashboard do projeto
- Veja **"Deployments"** para builds anteriores
- Clique em **"Logs"** para debugging

---

## 🔄 Atualizações

### Atualizar Backend
1. Faça commit das alterações no código
2. Push para o repositório
3. Railway fará redeploy automaticamente

### Atualizar Frontend
1. Faça commit das alterações no código
2. Push para o repositório
3. Vercel fará redeploy automaticamente

---

## 🐛 Troubleshooting

### Backend não inicia
- ✅ Verifique se todas as variáveis de ambiente estão configuradas
- ✅ Verifique logs do Railway para erros
- ✅ Confirme que `DATABASE_URL` está correto
- ✅ Teste health check: `curl https://seu-app.up.railway.app/health`

### Frontend não conecta ao backend
- ✅ Verifique se `VITE_API_URL` aponta para a URL correta do Railway
- ✅ Confirme que backend está rodando (teste `/health`)
- ✅ Verifique erros de CORS nos logs do Railway
- ✅ Inspecione console do navegador para erros

### Erro 404 em rotas do frontend
- ✅ Confirme que `vercel.json` tem rewrites configurados
- ✅ Reconstrua o projeto no Vercel

### Dependências faltando (Backend)
- ✅ Verifique `requirements.txt`
- ✅ Force redeploy no Railway

---

## 📝 Checklist Pós-Deploy

- [ ] Backend responde em `/health`
- [ ] Frontend carrega interface
- [ ] Login funciona
- [ ] Dados do banco são carregados
- [ ] Funcionalidades de IA estão operacionais (se API keys configuradas)
- [ ] Logs não mostram erros críticos
- [ ] Performance está aceitável

---

## 🆘 Suporte

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **Vite Docs**: https://vitejs.dev

---

## 🎉 Deploy Concluído!

Seu sistema está no ar:
- 🎨 **Frontend**: https://seu-app.vercel.app
- 🔧 **Backend**: https://seu-app.up.railway.app

**Próximos passos:**
1. Configure domínio customizado (opcional)
2. Configure SSL/HTTPS (já incluído em Railway e Vercel)
3. Configure monitoramento e alertas
4. Faça backup regular do banco de dados
