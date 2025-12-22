# 🚀 Quick Start - Deploy Legal Pro V2

## TL;DR - Para Portugueses 🇧🇷

**Pergunta:** "Tá pronto pra fazer deploy e usar?"

**Resposta:** ✅ **SIM, MAS...**

O sistema está **95% pronto**. Você precisa fazer **3 coisas CRÍTICAS primeiro**:

### ⚠️ ANTES DE FAZER DEPLOY:

1. **🔐 Trocar as senhas/chaves** (10 min)
   - As senhas do banco e API estavam no Git (já removemos)
   - Você PRECISA criar novas senhas
   - Veja o arquivo `SECURITY_ALERT.md`

2. **⚙️ Configurar variáveis** (10 min)
   - Railway: adicionar DATABASE_URL, API keys, etc
   - Vercel: adicionar VITE_API_URL
   - Veja o arquivo `DEPLOYMENT_READY.md`

3. **🚀 Fazer deploy** (30 min)
   - Backend → Railway
   - Frontend → Vercel
   - Testar tudo

**Tempo total:** ~1 hora

---

## Passo a Passo Simples

### Passo 1: Segurança (OBRIGATÓRIO)

```bash
# 1. Gerar novas chaves secretas
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copie o resultado - você vai usar no Railway

# 2. Acessar Qdrant Cloud
# - Login em https://cloud.qdrant.io
# - Ir no seu cluster
# - Gerar nova API Key
# - Salvar a chave

# 3. Railway Database
# - Você pode usar a mesma DATABASE_URL ou criar nova
# - Se criar nova, copie a connection string
```

### Passo 2: Deploy Backend (Railway)

1. **Criar conta no Railway**
   - Acesse: https://railway.app
   - Faça login com GitHub

2. **Criar projeto**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Conecte este repositório
   - Selecione o branch

3. **Adicionar variáveis de ambiente**
   
   Vá em "Variables" e adicione:
   
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database
   QDRANT_URL=https://seu-cluster.gcp.cloud.qdrant.io:6333
   QDRANT_API_KEY=sua-nova-chave
   SECRET_KEY=cole-o-resultado-do-python-acima
   SESSION_SECRET=cole-outro-resultado-diferente
   FLASK_ENV=production
   FLASK_APP=main.py
   
   # Opcional - se você tem
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   ```

4. **Deploy**
   - Railway faz automaticamente
   - Aguarde 5-10 minutos
   - Copie a URL gerada (tipo: `https://legal-pro-saas.up.railway.app`)

5. **Testar**
   ```bash
   curl https://sua-url.up.railway.app/health
   # Deve retornar: OK
   ```

### Passo 3: Deploy Frontend (Vercel)

1. **Criar conta no Vercel**
   - Acesse: https://vercel.com
   - Faça login com GitHub

2. **Criar projeto**
   - Clique em "Add New Project"
   - Importe seu repositório
   - Configure:
     - **Framework:** Vite
     - **Root Directory:** `frontend-react/frontend-react`
     - **Build Command:** `npm run build`
     - **Output Directory:** `dist`

3. **Adicionar variável de ambiente**
   
   Em "Environment Variables":
   
   ```
   VITE_API_URL=https://sua-url.up.railway.app
   ```
   
   (Use a URL do Railway do Passo 2)

4. **Deploy**
   - Clique em "Deploy"
   - Aguarde 3-5 minutos
   - Copie a URL gerada (tipo: `https://hub-legal-pro.vercel.app`)

5. **Testar**
   - Abra a URL no navegador
   - Tente fazer login
   - Verifique se funciona

### Passo 4: Finalizar

1. **Rodar migrações do banco**
   ```bash
   # Via Railway CLI (instale: npm i -g @railway/cli)
   railway login
   railway link
   railway run python migrate_database.py
   ```

2. **Criar usuário admin**
   ```bash
   railway run python criar_admin.py
   # Ou use o script que já existe no backend
   ```

3. **Testar tudo**
   - Login ✓
   - Dashboard ✓
   - Assistentes IA ✓
   - Processos ✓
   - Clientes ✓

---

## ✅ O Que Já Está Pronto

- ✅ 395 Assistentes de IA configurados
- ✅ Sistema de autenticação
- ✅ 51+ páginas frontend
- ✅ 327+ endpoints de API
- ✅ Módulo CPFL/Setor Energia
- ✅ Sistema multi-agente
- ✅ Export PDF/DOCX/Excel
- ✅ Dashboard analytics
- ✅ Gestão de processos e clientes
- ✅ Configurações de deploy (Procfile, railway.json, vercel.json)
- ✅ .gitignore criado
- ✅ .env removido do Git

---

## ⚙️ O Que Precisa Configurar

- ⚙️ Variáveis de ambiente (Railway + Vercel)
- ⚙️ Trocar senhas expostas
- ⚙️ Rodar migrações no banco de produção
- ⚙️ Criar usuário admin

---

## 🔮 O Que É Opcional (Pode Fazer Depois)

- 🔮 Domínio customizado
- 🔮 SSL customizado (Railway e Vercel já têm SSL grátis)
- 🔮 Configurar email (SendGrid)
- 🔮 Configurar SMS (Twilio)
- 🔮 Configurar pagamentos (Stripe)
- 🔮 Monitoramento avançado (Sentry)

---

## 🆘 Problemas Comuns

### Backend não inicia no Railway
- Verifique se todas as variáveis estão configuradas
- Olhe os logs no Railway dashboard
- Confirme que DATABASE_URL está correto

### Frontend não conecta no backend
- Verifique se VITE_API_URL está correto no Vercel
- Confirme que o backend está rodando (teste /health)
- Veja o console do navegador (F12) para erros

### Erro de CORS
- Já está configurado no backend
- Se ainda der erro, verifique se a URL do Vercel está correta

---

## 📚 Mais Informações

- **Detalhes completos:** `DEPLOYMENT_READY.md`
- **Segurança:** `SECURITY_ALERT.md`
- **Documentação técnica:** `README.md`
- **Deploy Railway/Vercel:** `DEPLOY.md`

---

## 💬 Resumo Final

**Status atual:** ✅ Sistema está pronto para deploy

**O que você precisa fazer:**
1. Trocar senhas (10 min) - **OBRIGATÓRIO**
2. Configurar variáveis (10 min) - **OBRIGATÓRIO**
3. Deploy Railway (15 min)
4. Deploy Vercel (10 min)
5. Testar (15 min)

**Total:** ~1 hora de trabalho

**Depois disso:** Sistema no ar, funcionando, pronto para usar! 🎉

---

## 🎯 Está com Pressa?

Se você não quiser ler tudo, faça assim:

1. Leia `SECURITY_ALERT.md` → Troque as senhas
2. Siga "Passo 2" acima → Deploy Railway com variáveis
3. Siga "Passo 3" acima → Deploy Vercel com variável
4. Acesse a URL do Vercel → Teste

Pronto! 🚀

---

**Dúvidas?** Veja os arquivos de documentação ou abra uma issue no GitHub.
