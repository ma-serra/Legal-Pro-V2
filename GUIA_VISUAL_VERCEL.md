# 📸 GUIA VISUAL - PASSO A PASSO COM PRINTS

## 🎯 O Que Fazer EXATAMENTE

Siga estes passos **EXATAMENTE** como mostrado:

---

## PASSO 1: Abrir Vercel

1. Abra seu navegador
2. Digite: `vercel.com`
3. Clique em **"Log In"**
4. Faça login com GitHub

---

## PASSO 2: Criar Novo Projeto

Na página inicial do Vercel:

1. Clique no botão: **"Add New..."** (canto superior direito)
2. No menu que abre, clique em: **"Project"**

---

## PASSO 3: Importar do GitHub

Na tela "Import Git Repository":

1. Procure por: **"Legal-Pro-V2"** na lista de repositórios
2. Clique no botão **"Import"** ao lado do repositório

---

## PASSO 4: Configurar o Projeto

Na tela "Configure Project", preencha:

### Build and Output Settings

**Framework Preset:**
- Selecione: **Vite** (na lista dropdown)

**Root Directory:**
- Clique em **"Edit"**
- Digite: `frontend-react/frontend-react`
- Clique em **"Continue"**

**Build Command:**
- Deixe como está: `npm run build` (já vem preenchido)

**Output Directory:**
- Deixe como está: `dist` (já vem preenchido)

**Install Command:**
- Deixe como está: `npm install` (já vem preenchido)

---

## PASSO 5: Environment Variables

Ainda na mesma tela:

1. Clique em **"Environment Variables"** (pode estar expandido ou não)
2. No campo **"NAME"**, digite: `VITE_API_URL`
3. No campo **"VALUE"**, digite: `https://legal-pro-saas.up.railway.app`
4. Clique no botão **"Add"** (ou pressione Enter)

---

## PASSO 6: Deploy!

No fim da página:

1. Clique no botão grande: **"Deploy"**
2. Aguarde 3-5 minutos (vai aparecer um loading)

---

## PASSO 7: Acessar o Site

Quando o deploy terminar:

1. Vercel vai mostrar: **"Congratulations!"** ou similar
2. Clique no link do seu site (algo como: `legal-pro-v2-xxxxx.vercel.app`)
3. Seu site está no ar! 🎉

---

## 📝 RESUMO: O Que Você Digitou

Se precisar refazer, aqui estão os valores:

```
Root Directory: frontend-react/frontend-react
Framework: Vite
Environment Variable:
  - Name: VITE_API_URL
  - Value: https://legal-pro-saas.up.railway.app
```

Só esses 3 valores!

---

## ✅ Checklist

Marque conforme faz:

- [ ] Abri vercel.com
- [ ] Fiz login
- [ ] Cliquei em "Add New" → "Project"
- [ ] Importei Legal-Pro-V2
- [ ] Selecionei Framework: Vite
- [ ] Coloquei Root Directory: `frontend-react/frontend-react`
- [ ] Adicionei VITE_API_URL
- [ ] Cliquei em Deploy
- [ ] Esperei 3-5 minutos
- [ ] Abri o link do site

---

## 🎥 Se Preferir Vídeo

Procure no YouTube: "How to deploy Vite React to Vercel"

O processo é exatamente igual, só muda:
- Root Directory (use `frontend-react/frontend-react`)
- Environment Variable (adicione VITE_API_URL)

---

## 🆘 Deu Erro?

**Erro: "No framework detected"**
→ Você esqueceu de colocar Root Directory

**Erro: "Build failed"**
→ Veja os logs, geralmente é falta da variável VITE_API_URL

**Erro: "Cannot connect to backend"**
→ Verifique se colocou VITE_API_URL corretamente

Me mande print do erro que eu ajudo!

---

## 🎯 DICA PRO

Depois que o projeto estiver criado no Vercel:

- Todo push no GitHub faz deploy automático
- Não precisa repetir esses passos
- Só empurrar código e pronto!

---

**Tempo estimado:** 5-10 minutos
**Dificuldade:** Fácil (só copiar e colar)
**Resultado:** Site no ar, funcionando!
