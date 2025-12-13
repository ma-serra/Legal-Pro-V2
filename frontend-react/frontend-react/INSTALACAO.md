# 🚀 Frontend React Refatorado - Guia de Instalação e Uso

## Status Atual
✅ **PRONTO PARA USAR** - Sistema criado e testado com sucesso!

---

## 📦 Instalação Rápida

### 1. Navegue para a pasta
```bash
cd frontend-react
```

### 2. Instale as dependências (se não estiverem instaladas)
```bash
npm install
```

### 3. Inicie o servidor de desenvolvimento
```bash
npm run dev
```

Acesse em: **http://localhost:5173**

---

## 🔧 Comandos Disponíveis

```bash
# Iniciar desenvolvimento com hot-reload
npm run dev

# Build para produção (otimizado)
npm run build

# Preview do build
npm run preview

# Lint (se configurado)
npm run lint
```

---

## 📁 Estrutura do Projeto

```
frontend-react/
│
├── src/                      # Código-fonte
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Layout.tsx       # Layout principal
│   │   └── Navigation.tsx   # Barra de navegação
│   │
│   ├── pages/              # Páginas da aplicação
│   │   ├── Home.tsx        # Página inicial
│   │   ├── Dashboard.tsx   # Dashboard
│   │   └── NotFound.tsx    # Página 404
│   │
│   ├── lib/                # Utilitários
│   │   └── api.ts          # Cliente HTTP (axios)
│   │
│   ├── hooks/              # Custom React Hooks
│   │   └── useApi.ts       # Hook para requisições HTTP
│   │
│   ├── types/              # Tipos TypeScript
│   │   └── index.ts        # Definições de tipos
│   │
│   ├── styles/             # Estilos globais
│   │   └── index.css       # CSS com Tailwind
│   │
│   ├── App.tsx             # Componente raiz
│   └── main.tsx            # Ponto de entrada
│
├── public/                  # Arquivos estáticos
│
├── index.html               # Template HTML
├── vite.config.ts           # Configuração Vite
├── tsconfig.json            # Configuração TypeScript
├── tailwind.config.js       # Configuração Tailwind CSS
└── package.json             # Dependências e scripts
```

---

## 🔌 Conectar com Backend Flask

O frontend está configurado para se conectar automaticamente com o backend em `http://localhost:5000`.

### Configure a URL da API (opcional)
Crie um arquivo `.env.local`:
```
VITE_API_URL=http://localhost:5000
```

### Fazer requisições
```typescript
import api from '@/lib/api'

// GET
const { data } = await api.get('/processos')

// POST
const { data } = await api.post('/processos', { 
  titulo: 'Novo Processo'
})

// O token JWT é enviado automaticamente!
```

---

## 🛠️ Desenvolvimento

### Criar um novo componente
```bash
# Criar arquivo em: src/components/MeuComponente.tsx

export default function MeuComponente() {
  return <div>Meu componente aqui</div>
}
```

### Criar uma nova página
```bash
# Criar arquivo em: src/pages/MinhaPage.tsx
# Adicionar rota em: src/App.tsx

import MinhaPage from '@/pages/MinhaPage'

// Em App.tsx adicione:
<Route path="/minha-page" element={<MinhaPage />} />
```

### Usar o hook de API
```typescript
import { useApi } from '@/hooks/useApi'

export default function MeuComponente() {
  const { data, loading, error, refetch } = useApi<Processo[]>('/processos')

  if (loading) return <div>Carregando...</div>
  if (error) return <div>Erro: {error.message}</div>

  return (
    <div>
      {data?.map(p => <div key={p.id}>{p.titulo}</div>)}
    </div>
  )
}
```

---

## 🎨 Personalizar Tema

Edite as cores em `frontend-react/src/styles/index.css`:

```css
:root {
  --background: #ffffff;
  --foreground: #000000;
  --primary: #3b576f;        /* Cor principal */
  --accent: #4a9eff;         /* Cor de destaque */
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ffffff;
    /* ... cores escuras ... */
  }
}
```

---

## 📊 Build para Produção

### 1. Build otimizado
```bash
npm run build
```

Isso cria a pasta `dist/` com os arquivos compilados.

### 2. Deploy em Vercel
```bash
# Opção 1: Via dashboard Vercel
# - Conecte seu repositório GitHub
# - Vercel detecta Next.js/Vite automaticamente
# - Deploy automático

# Opção 2: Via CLI
npm install -g vercel
vercel
```

### 3. Deploy em Railway
```bash
# Railway detecta automáticamente Node.js
# Configure em: https://railway.app/
# Conecte seu repositório GitHub
```

---

## 🔒 Segurança

### Token de Autenticação
O token JWT é armazenado em `localStorage` e incluído automaticamente em todas as requisições:

```typescript
// Em src/lib/api.ts
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Práticas Recomendadas
- ✅ Nunca exposição de secrets no cliente
- ✅ Use variáveis de ambiente com `VITE_`
- ✅ Valide dados no backend
- ✅ Use HTTPS em produção

---

## 📱 Responsivo

Tailwind CSS já está configurado para mobile-first design:

```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {/* 1 coluna em mobile, 3 em desktop */}
</div>
```

---

## 🐛 Troubleshooting

### "Cannot find module '@/...'"
- Verificar se o arquivo existe
- Verificar `tsconfig.json` e `vite.config.ts`

### "API retorna CORS error"
- Adicionar CORS no backend Flask:
  ```python
  from flask_cors import CORS
  CORS(app)
  ```

### "Build falha com erros TypeScript"
- Executar: `npm run build -- --force`
- Verificar tipo de dados em `src/types/index.ts`

---

## 📚 Recursos

- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)

---

## ✅ Próximos Passos

1. **Iniciar servidor de dev:** `npm run dev`
2. **Implementar Login:** Criar `src/pages/Login.tsx`
3. **Conectar com backend:** Testar chamadas API
4. **Refatorar páginas:** Converter templates HTML principais
5. **Deploy:** Fazer build e enviar para Vercel/Railway

---

**Criado:** 13 de Dezembro, 2025
**Versão:** 1.0.0
**Status:** ✅ Pronto para uso
