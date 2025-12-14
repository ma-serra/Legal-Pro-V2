# Comandos Git - Legal Pro Hub

## 🎨 Frontend (Vercel)

### Correção: TypeScript Vite Definitions
```powershell
# Adicionar arquivos corrigidos
git add "frontend-react/frontend-react/src/vite-env.d.ts"
git add "frontend-react/frontend-react/tsconfig.json"

# Commit
git commit -m "fix: add Vite TypeScript definitions to resolve Vercel build error"

# Push
git push
```

**Status**: ✅ Executado em 13/12/2024

---

## ⚙️ Backend (Railway)

### Correção: Legal Design Pro + Admin Routes
```powershell
# Adicionar arquivos corrigidos
git add "backend-flask/models_legal_design.py"
git add "backend-flask/main.py"

# Verificar status
git status

# Commit
git commit -m "fix: resolve import errors for Legal Design Pro and Admin Routes

- Add missing models_legal_design.py to backend-flask directory
- Fix admin routes import path from modules.optimized_admin_routes to admin_routes_update
- Resolves 'No module named models_legal_design' error
- Resolves 'cannot import name register_updated_admin_routes' error"

# Push
git push
```

**Status**: ⏳ Pendente

---

## 📋 Resumo das Correções

### Frontend
- ✅ Criado `vite-env.d.ts` com definições TypeScript do Vite
- ✅ Atualizado `tsconfig.json` para incluir o arquivo
- ✅ Resolve erro: `Property 'env' does not exist on type 'ImportMeta'`

### Backend
- ⏳ Copiado `models_legal_design.py` para `backend-flask`
- ⏳ Corrigido import em `main.py` linha 6890
- ⏳ Resolve erro: `No module named 'models_legal_design'`
- ⏳ Resolve erro: `cannot import name 'register_updated_admin_routes'`

---

## 🚀 Deploy Automático

Ambos Vercel e Railway estão configurados para deploy automático:
- **Frontend**: Deploy automático ao fazer push para branch `main`
- **Backend**: Deploy automático ao fazer push para branch `main`

---

## 📝 Notas

- Frontend deploy em andamento após último push (commit `ee78496`)
- Backend aguardando push das correções
- Ambos os serviços devem rebuildar automaticamente após o push
