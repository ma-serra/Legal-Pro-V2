# Configuração pgAdmin4 - PostgreSQL Local (Replit)

## 🔐 Credenciais PostgreSQL Local

```
╔════════════════════════════════════════════════════════════════════╗
║          POSTGRESQL LOCAL - LEGAL_PRO_LOCAL                        ║
╠════════════════════════════════════════════════════════════════════╣
║  Database:      legal_pro_local                                    ║
║  Porta:         5432                                               ║
║  Usuário:       postgres                                           ║
║  Senha:         (vazia - sem senha)                                ║
║  Tabelas:       91                                                 ║
║  Tamanho:       15 MB                                              ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## ⚠️ IMPORTANTE: Acesso Externo

O PostgreSQL local no Replit **NÃO está acessível diretamente** do seu computador por padrão. 

Para conectar no pgAdmin4 do seu computador, você tem **3 opções**:

---

## 🚀 OPÇÃO 1: SSH Tunnel (Recomendado)

Se você tem acesso SSH ao Replit, crie um túnel:

### No seu terminal local (Mac/Linux/Windows com Git Bash):

```bash
# Criar túnel SSH
ssh -L 5432:localhost:5432 seu-usuario@replit-host

# Deixe essa janela aberta!
```

### No pgAdmin4:

```
Host:               localhost
Port:               5432
Maintenance DB:     legal_pro_local
Username:           postgres
Password:           (deixar vazio)
SSL Mode:           Disable
```

---

## 🔌 OPÇÃO 2: Expor PostgreSQL Publicamente (Cuidado!)

⚠️ **Não recomendado para produção - apenas desenvolvimento**

### Passo 1: Modificar postgresql.conf

No Replit, execute:

```bash
# Encontrar postgresql.conf
find /nix/store -name "postgresql.conf" 2>/dev/null | grep postgresql-16

# Editar (se tiver permissão)
# Mudar: listen_addresses = 'localhost'
# Para:  listen_addresses = '*'
```

### Passo 2: Criar usuário com senha

```bash
psql -d legal_pro_local << 'SQL'
CREATE USER pgadmin_user WITH PASSWORD 'SuaSenhaSegura123!';
GRANT ALL PRIVILEGES ON DATABASE legal_pro_local TO pgadmin_user;
GRANT ALL ON SCHEMA public TO pgadmin_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO pgadmin_user;
SQL
```

### Passo 3: Configurar pgAdmin4

```
Host:               [IP-EXTERNO-DO-REPLIT]
Port:               5432
Maintenance DB:     legal_pro_local
Username:           pgadmin_user
Password:           SuaSenhaSegura123!
SSL Mode:           Prefer
```

---

## 🎯 OPÇÃO 3: Usar Neon (Mais Simples)

**Recomendação:** Use o banco **Neon** no pgAdmin4, que tem os **mesmos dados** clonados:

```
Host:       ep-ancient-hill-acolhubu-pooler.sa-east-1.aws.neon.tech
Port:       5432
Database:   neondb
Username:   neondb_owner
Password:   npg_WztE2J7ynQiG
SSL Mode:   Require
```

✅ **Vantagens:**
- Acessível de qualquer lugar
- Mesmos dados que o PostgreSQL local
- Não precisa configurar túnel SSH
- Mais seguro

---

## 🔧 Script para Criar Usuário com Senha

Execute no terminal do Replit:

```bash
#!/bin/bash

# Criar usuário para acesso externo
psql -d legal_pro_local << 'EOF'

-- Criar usuário
CREATE USER pgadmin WITH PASSWORD 'Legal_Pro_2025!';

-- Dar permissões totais
GRANT ALL PRIVILEGES ON DATABASE legal_pro_local TO pgadmin;
GRANT ALL ON SCHEMA public TO pgadmin;
GRANT ALL ON ALL TABLES IN SCHEMA public TO pgadmin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO pgadmin;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO pgadmin;

-- Confirmar
\du pgadmin

EOF

echo "✅ Usuário 'pgadmin' criado com senha 'Legal_Pro_2025!'"
```

---

## 📊 Verificar Conexões Ativas

No Replit, execute:

```bash
# Ver quem está conectado
psql -d legal_pro_local -c "
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity 
WHERE datname = 'legal_pro_local';
"
```

---

## 🆘 Troubleshooting

### Erro: "Connection refused"
- PostgreSQL local só aceita conexões de `localhost` por padrão
- Use SSH tunnel ou Neon

### Erro: "FATAL: password authentication failed"
- PostgreSQL local usa "peer authentication" (sem senha)
- Crie um usuário com senha (veja script acima)

### Erro: "no pg_hba.conf entry"
- PostgreSQL precisa ser configurado para aceitar conexões externas
- Mais fácil: use Neon

---

## ✅ Resumo - Qual Opção Escolher?

| Opção | Dificuldade | Segurança | Recomendado? |
|-------|-------------|-----------|--------------|
| **SSH Tunnel** | Média | ✅ Alta | ✅ Sim (se tem SSH) |
| **Expor Público** | Difícil | ⚠️ Baixa | ❌ Não (produção) |
| **Usar Neon** | Fácil | ✅ Alta | ✅✅ **SIM!** |

**Recomendação final:** Use o **Neon** no pgAdmin4. Tem os mesmos dados e é muito mais simples!

---

## 📝 Comandos Úteis

```bash
# Testar conexão local
psql -d legal_pro_local -c "SELECT version();"

# Ver tabelas
psql -d legal_pro_local -c "\dt"

# Criar backup
pg_dump legal_pro_local > backup_local.sql

# Restaurar backup
psql -d legal_pro_local < backup_local.sql
```

---

Se precisar de ajuda para configurar qualquer uma dessas opções, é só pedir! 🚀
