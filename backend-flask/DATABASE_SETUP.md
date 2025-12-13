# 🗄️ Guia de Configuração de Banco de Dados - Legal Pro

## 📋 Visão Geral

O Legal Pro suporta **3 modos de banco de dados**:

1. **SQLite Local** - Desenvolvimento básico offline
2. **PostgreSQL Local** - Desenvolvimento com 100% compatibilidade
3. **PostgreSQL Neon** - Produção na nuvem

---

## 🔧 Modo 1: SQLite Local

**Quando usar**: Desenvolvimento rápido, testes básicos, offline

### Configuração

```bash
# Variáveis de ambiente
export USE_LOCAL_DB=true
export LOCAL_DB_TYPE=sqlite
# ou simplesmente (sqlite é o padrão):
export USE_LOCAL_DB=true
```

### Inicialização

```bash
# Inicializar banco
python init_local_db.py init

# Sincronizar dados do Neon
python init_local_db.py sync
```

### Características

- ✅ Configuração simples
- ✅ Sem dependências externas
- ✅ Arquivo único: `local_legal_pro.db`
- ⚠️ Limitações com JSONB e tipos PostgreSQL
- ⚠️ Sincronização linha por linha (mais lenta)

---

## 🐘 Modo 2: PostgreSQL Local (Recomendado para Dev)

**Quando usar**: Desenvolvimento completo, testes de compatibilidade, preparação para produção

### Setup Rápido com Docker

```bash
# 1. Execute o script de setup
./docker-postgres-setup.sh

# 2. Configure variáveis de ambiente
export USE_LOCAL_DB=true
export LOCAL_DB_TYPE=postgres
export LOCAL_DATABASE_URL=postgresql://postgres:legal_pro_2025@localhost:5432/legal_pro_local
```

### Ou Configure Manualmente

```bash
# Opção A: URL completa (recomendado)
export USE_LOCAL_DB=true
export LOCAL_DB_TYPE=postgres
export LOCAL_DATABASE_URL=postgresql://usuario:senha@localhost:5432/banco

# Opção B: Variáveis separadas
export USE_LOCAL_DB=true
export LOCAL_DB_TYPE=postgres
export LOCAL_PG_USER=postgres
export LOCAL_PG_PASSWORD=sua_senha
export LOCAL_PG_HOST=localhost
export LOCAL_PG_PORT=5432
export LOCAL_PG_DATABASE=legal_pro_local
```

### Inicialização

```bash
# Inicializar estrutura
python init_local_db.py init

# Sincronizar dados do Neon (MUITO mais rápido!)
python init_local_db.py sync
```

### Características

- ✅ 100% compatível com produção
- ✅ JSONB, arrays, tipos avançados funcionam perfeitamente
- ✅ Sincronização ultra-rápida via `pg_dump`/`pg_restore`
- ✅ Testes realistas
- ⚠️ Requer PostgreSQL (via Docker ou instalação local)

### Comandos Docker Úteis

```bash
# Iniciar PostgreSQL
docker start legal-pro-postgres

# Parar PostgreSQL
docker stop legal-pro-postgres

# Ver logs
docker logs legal-pro-postgres

# Acessar console
docker exec -it legal-pro-postgres psql -U postgres -d legal_pro_local

# Backup manual
docker exec legal-pro-postgres pg_dump -U postgres legal_pro_local > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i legal-pro-postgres psql -U postgres -d legal_pro_local
```

---

## ☁️ Modo 3: PostgreSQL Neon (Produção)

**Quando usar**: Produção, dados reais, acesso remoto

### Configuração

```bash
# Usar banco Neon
export USE_LOCAL_DB=false
export DATABASE_URL=postgresql://usuario:senha@ep-xxx.neon.tech/legal_pro
```

### Características

- ✅ Banco na nuvem
- ✅ Alta disponibilidade
- ✅ Backups automáticos
- ✅ Escalabilidade
- ❌ Requer internet
- ❌ Pode ter latência

---

## 🔄 Sincronização de Dados

### Sincronização Inteligente

O sistema detecta automaticamente o tipo de banco e usa o método mais eficiente:

```bash
# Sincronizar Neon → Local
python init_local_db.py sync
```

**PostgreSQL → PostgreSQL:**
- ✅ Usa `pg_dump` e `pg_restore`
- ✅ Copia estrutura + dados
- ✅ Muito rápido (segundos)
- ✅ Preserva todos os tipos

**Neon → SQLite:**
- ⚠️ Sincronização linha por linha
- ⚠️ Apenas tabelas essenciais
- ⚠️ Pode ser lento com muitos dados

### Tabelas Sincronizadas (SQLite)

```python
- role
- categoria_assistente
- user
- assistente_juridico
- template_juridico
```

---

## 📊 Verificar Status

```bash
# Ver status de todos os bancos
python init_local_db.py status
```

Mostra:
- Tipo de banco local (se configurado)
- Status do banco Neon
- Banco ativo no momento

---

## 🎯 Fluxos de Trabalho Recomendados

### Desenvolvimento Inicial

```bash
# 1. Setup PostgreSQL local
./docker-postgres-setup.sh

# 2. Configurar ambiente
export USE_LOCAL_DB=true
export LOCAL_DB_TYPE=postgres
export LOCAL_DATABASE_URL=postgresql://postgres:legal_pro_2025@localhost:5432/legal_pro_local

# 3. Sincronizar dados
python init_local_db.py sync

# 4. Executar aplicação
python main.py
```

### Desenvolvimento Offline (sem Neon)

```bash
# Usar SQLite local
export USE_LOCAL_DB=true

python init_local_db.py init
python main.py
```

### Testar em Produção

```bash
# Voltar para Neon
export USE_LOCAL_DB=false
export DATABASE_URL=postgresql://...neon.tech/legal_pro

python main.py
```

---

## 🔍 Solução de Problemas

### Erro: "DATABASE_URL não configurada"

**Causa**: Tentando usar Neon sem configurar URL

**Solução**:
```bash
export DATABASE_URL=postgresql://usuario:senha@ep-xxx.neon.tech/legal_pro
```

### Erro: "pg_dump não encontrado"

**Causa**: PostgreSQL client tools não instalados

**Solução**:
```bash
# Ubuntu/Debian
sudo apt install postgresql-client

# Mac
brew install postgresql

# Windows (via WSL)
sudo apt install postgresql-client
```

### Docker não inicia PostgreSQL

**Verificar logs**:
```bash
docker logs legal-pro-postgres
```

**Recriar container**:
```bash
docker stop legal-pro-postgres
docker rm legal-pro-postgres
./docker-postgres-setup.sh
```

### Sincronização muito lenta (SQLite)

**Recomendação**: Use PostgreSQL local para sincronização muito mais rápida

```bash
export LOCAL_DB_TYPE=postgres
```

---

## 📝 Variáveis de Ambiente - Referência Rápida

```bash
# === BANCO LOCAL SQLite ===
USE_LOCAL_DB=true
LOCAL_DB_TYPE=sqlite
LOCAL_DB_PATH=local_legal_pro.db  # opcional

# === BANCO LOCAL PostgreSQL (Opção 1: URL) ===
USE_LOCAL_DB=true
LOCAL_DB_TYPE=postgres
LOCAL_DATABASE_URL=postgresql://user:pass@host:port/db

# === BANCO LOCAL PostgreSQL (Opção 2: Separado) ===
USE_LOCAL_DB=true
LOCAL_DB_TYPE=postgres
LOCAL_PG_USER=postgres
LOCAL_PG_PASSWORD=senha
LOCAL_PG_HOST=localhost
LOCAL_PG_PORT=5432
LOCAL_PG_DATABASE=legal_pro_local

# === BANCO NEON (Produção) ===
USE_LOCAL_DB=false
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/legal_pro
```

---

## ✨ Dicas

1. **Para desenvolvimento**: Use PostgreSQL local via Docker
2. **Para testes rápidos**: SQLite está OK
3. **Para produção**: Sempre Neon
4. **Sincronização**: PostgreSQL → PostgreSQL é 10x+ mais rápido
5. **Backup**: Use `pg_dump` para backups completos
6. **Logs**: Sempre verifique logs com `docker logs` se algo der errado

---

**Precisa de ajuda?** Consulte a documentação principal em `replit.md`
