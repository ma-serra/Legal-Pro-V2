# 🚀 DEPLOY AUTOMÁTICO - 3 COMANDOS

## ⚡ Modo Super Rápido

Abra um terminal e cole estes comandos:

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Ir para o frontend
cd frontend-react/frontend-react

# 3. Deploy!
./deploy-vercel.sh
```

Pronto! 🎉

---

## 📱 Passo a Passo Visual

### 1️⃣ Abrir Terminal

**GitHub Codespace:**
- Terminal → New Terminal

**VSCode Local:**
- Terminal → New Terminal

**Linux/Mac:**
- Abrir Terminal

**Windows:**
- PowerShell (como administrador)

### 2️⃣ Copiar e Colar

Cole isto no terminal (tudo de uma vez):

```bash
npm install -g vercel && cd frontend-react/frontend-react && ./deploy-vercel.sh
```

Aperte ENTER.

### 3️⃣ Seguir Instruções

O script vai:
1. ✅ Instalar o que precisa
2. ✅ Testar o build
3. ❓ Perguntar se quer continuar → Digite "y" e ENTER
4. ❓ Pedir login no Vercel → Siga instruções no navegador
5. 🚀 Fazer o deploy

### 4️⃣ Resultado

Quando terminar, vai mostrar:
```
✅ DEPLOY COMPLETO!
https://seu-site.vercel.app
```

Copie a URL e abra no navegador!

---

## 🆘 Se Der Erro

### Erro: "command not found: npm"

Instale Node.js:
- Windows: https://nodejs.org/en/download/
- Mac: `brew install node`
- Linux: `sudo apt install nodejs npm`

### Erro: "permission denied"

```bash
chmod +x deploy-vercel.sh
./deploy-vercel.sh
```

### Erro: "vercel: command not found"

```bash
npm install -g vercel
# Se der erro, tente:
sudo npm install -g vercel
```

### Erro no Build

```bash
cd frontend-react/frontend-react
npm install
npm run build
# Veja os erros e me chame
```

---

## 🎯 Alternativa: Fazer Manualmente no Site

Se os comandos não funcionarem:

1. Vá em https://vercel.com
2. Login com GitHub
3. "New Project"
4. Selecione: Legal-Pro-V2
5. Root Directory: `frontend-react/frontend-react`
6. Framework: Vite
7. Build Command: `npm run build`
8. Output: `dist`
9. Deploy!

---

## ✅ Verificar se Funcionou

Depois do deploy:

1. Abra a URL fornecida
2. Deve aparecer a página inicial
3. Clique em "Login"
4. Tente fazer login

Se tudo funcionar = 🎉 Sucesso!

---

## 📞 Precisa de Ajuda?

Me chame no PR com:
- Print do erro
- O que você tentou
- Onde travou

Vou ajudar!

---

**Dica:** Se está no GitHub, crie um Codespace:
- Code → Codespaces → Create codespace
- Espere abrir
- Cole os comandos acima no terminal
