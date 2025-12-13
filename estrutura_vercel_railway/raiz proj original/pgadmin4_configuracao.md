# Configuração pgAdmin4 - Legal Pro

## 🔐 Credenciais do Banco de Dados

### PostgreSQL Neon (Produção - Acessível Externamente)

Use estas credenciais no pgAdmin4:

```
Nome da Conexão:  Legal Pro - Neon (Produção)
Host:             ep-ancient-hill-acolhubu-pooler.sa-east-1.aws.neon.tech
Porta:            5432
Database:         neondb
Usuário:          neondb_owner
Senha:            npg_WztE2J7ynQiG
SSL Mode:         require
```

---

## 📖 Passo a Passo - Configurar no pgAdmin4

### 1. Abrir pgAdmin4 e Criar Novo Servidor

1. Clique com botão direito em **"Servers"**
2. Selecione **"Create" → "Server..."**

### 2. Aba "General"

```
Name: Legal Pro - Neon (Produção)
```

### 3. Aba "Connection"

```
Host name/address:     ep-ancient-hill-acolhubu-pooler.sa-east-1.aws.neon.tech
Port:                  5432
Maintenance database:  neondb
Username:              neondb_owner
Password:              npg_WztE2J7ynQiG
Save password:         ✓ (marcar)
```

### 4. Aba "SSL"

```
SSL mode:              Require
```

### 5. Aba "Advanced"

```
DB restriction:        neondb
```

### 6. Salvar

Clique em **"Save"** e a conexão será estabelecida!

---

## 🎯 Verificação

Após conectar, você deverá ver:

- ✅ 91 tabelas no schema `public`
- ✅ Tamanho do banco: ~17 MB
- ✅ Dados de produção do Legal Pro

### Principais Tabelas:

- `agente_juridico` - 330+ agentes jurídicos
- `processo_juridico` - Processos legais
- `usuario` - Usuários do sistema
- `analise_processo_ia` - Análises de IA
- `cpfl_processos` - Processos CPFL/RGE
- E mais 86 outras tabelas...

---

## 🔌 PostgreSQL Local (Replit)

⚠️ **NÃO É ACESSÍVEL EXTERNAMENTE**

O PostgreSQL local rodando no Replit não pode ser acessado pelo pgAdmin4
do seu computador, pois está dentro do ambiente isolado do Replit.

**Alternativas:**

1. **Use o Neon** (recomendado) - Tem os mesmos dados clonados
2. **Acesse via Replit Shell** - Use `psql -d legal_pro_local` dentro do Replit
3. **Interface Web** - Use `/admin/database` no sistema Legal Pro

---

## 🔧 Comandos Úteis no pgAdmin4

Após conectar, você pode executar queries na aba **"Query Tool"**:

```sql
-- Ver todas as tabelas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Contar agentes jurídicos
SELECT COUNT(*) FROM agente_juridico;

-- Ver últimos processos
SELECT * FROM processo_juridico 
ORDER BY data_registro DESC 
LIMIT 10;

-- Tamanho do banco
SELECT pg_size_pretty(pg_database_size(current_database()));
```

---

## ⚠️ Importante

- ✅ **Neon é o banco de PRODUÇÃO** - Cuidado ao modificar dados
- ✅ **Backup automático** - Neon faz backups automáticos
- ✅ **Região:** sa-east-1 (São Paulo, AWS)
- ✅ **SSL obrigatório** para conexões seguras

---

## 🆘 Troubleshooting

### Erro: "Connection timeout"
- Verifique sua conexão com internet
- Confirme que o host está correto
- Certifique-se que a porta 5432 não está bloqueada

### Erro: "FATAL: password authentication failed"
- Verifique usuário e senha
- Certifique-se que copiou a senha completa

### Erro: "SSL connection required"
- Vá na aba "SSL" e selecione "Require"

---

Pronto! Você está conectado ao banco de produção do Legal Pro! 🎉
