# Instruções de Deploy - Legal Pro

## Frontend React (Vercel)

### Arquivo: `frontend-react.zip` (40KB)

**Passos para deploy no Vercel:**

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em "Add New Project"
3. Faça upload do conteúdo descompactado de `frontend-react.zip`
4. Configure as variáveis de ambiente:
   - `VITE_API_URL` = URL do seu backend Railway (ex: https://seu-backend.railway.app)
5. Build Command: `npm run build`
6. Output Directory: `dist`
7. Clique em "Deploy"

---

## Backend Flask (Railway)

### Arquivo: `backend-flask.zip` (16MB)

**Passos para deploy no Railway:**

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em "New Project" > "Deploy from GitHub" ou faça upload manual
3. Descompacte `backend-flask.zip` e faça push para um repositório GitHub
4. Configure as variáveis de ambiente:

```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
ASSEMBLYAI_API_KEY=...
SECRET_KEY=sua-chave-secreta
```

5. Railway detectará automaticamente que é um app Python
6. Procfile já configurado: `web: gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`

---

## Estrutura dos Pacotes

### Frontend (Vercel)
- React 18 + TypeScript + Vite
- TailwindCSS
- Páginas: Dashboard, Processos, Análises, Assistentes

### Backend (Railway)
- Flask 3.0 + Python 3.11
- PostgreSQL (Neon)
- 368 agentes de IA
- APIs REST completas
- Integração com OpenAI, Anthropic, Google AI

---

## Após o Deploy

1. Configure CORS no backend para aceitar requisições do frontend Vercel
2. Teste a autenticação em /api/auth/login
3. Verifique os logs no Railway para debug
