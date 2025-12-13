# Legal Pro Frontend - React Refatorado

Frontend refatorado do Legal Pro em React + TypeScript + Tailwind CSS

## Estrutura

```
frontend-react/
├── src/
│   ├── pages/          # Páginas da aplicação
│   ├── components/     # Componentes reutilizáveis
│   ├── lib/           # Utilitários e APIs
│   ├── hooks/         # Custom hooks
│   ├── styles/        # CSS global
│   └── types/         # Tipos TypeScript
├── public/            # Arquivos estáticos
└── vite.config.ts     # Configuração Vite
```

## Instalação

```bash
cd frontend-react
npm install
```

## Desenvolvimento

```bash
npm run dev
```

Acessa em http://localhost:5173

## Build para Produção

```bash
npm run build
```

## Integração com Backend

O frontend se conecta ao backend Flask em `http://localhost:5000`.

Configure `.env.local`:
```
VITE_API_URL=http://localhost:5000
```

## Status

- ✅ Estrutura React criada
- ✅ Roteamento com React Router
- ✅ Componentes base (Navigation, Layout)
- ✅ Paginas iniciais (Home, Dashboard)
- ✅ API client com axios
- ✅ Tailwind CSS configurado
- ⏳ Integração com backend
- ⏳ Autenticação
- ⏳ Componentes jurídicos específicos
