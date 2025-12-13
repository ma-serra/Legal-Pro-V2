#!/bin/bash

# Script para configurar PostgreSQL local via Docker para Legal Pro
# Compatível 100% com PostgreSQL Neon para sincronização perfeita
# Data: 2025-11-03

set -e

echo "========================================"
echo "🐘 SETUP POSTGRESQL LOCAL - LEGAL PRO"
echo "========================================"
echo ""

# Configurações padrão
CONTAINER_NAME="legal-pro-postgres"
PG_VERSION="16"
PG_USER="postgres"
PG_PASSWORD="legal_pro_2025"
PG_DATABASE="legal_pro_local"
PG_PORT="5432"

echo "📋 Configurações:"
echo "   Container: $CONTAINER_NAME"
echo "   PostgreSQL: $PG_VERSION"
echo "   Usuário: $PG_USER"
echo "   Banco: $PG_DATABASE"
echo "   Porta: $PG_PORT"
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado!"
    echo ""
    echo "Instale o Docker primeiro:"
    echo "  https://docs.docker.com/get-docker/"
    echo ""
    exit 1
fi

echo "✅ Docker encontrado"

# Verificar se o container já existe
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "⚠️  Container '$CONTAINER_NAME' já existe!"
    echo ""
    read -p "Deseja remover e recriar? (s/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "🗑️  Removendo container antigo..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        echo "✅ Container removido"
    else
        echo "❌ Operação cancelada"
        exit 0
    fi
fi

echo ""
echo "🚀 Criando container PostgreSQL..."
echo ""

# Criar e iniciar container
docker run -d \
    --name $CONTAINER_NAME \
    -e POSTGRES_USER=$PG_USER \
    -e POSTGRES_PASSWORD=$PG_PASSWORD \
    -e POSTGRES_DB=$PG_DATABASE \
    -p $PG_PORT:5432 \
    -v legal_pro_pgdata:/var/lib/postgresql/data \
    --restart unless-stopped \
    postgres:$PG_VERSION

echo "✅ Container criado com sucesso!"

# Aguardar PostgreSQL ficar pronto
echo ""
echo "⏳ Aguardando PostgreSQL inicializar (pode levar alguns segundos)..."
sleep 5

# Loop de verificação
for i in {1..10}; do
    if docker exec $CONTAINER_NAME pg_isready -U $PG_USER > /dev/null 2>&1; then
        echo "✅ PostgreSQL está pronto!"
        break
    fi
    echo "   Tentativa $i/10..."
    sleep 2
done

# Verificar se está rodando
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Erro: Container não está rodando"
    echo ""
    echo "Ver logs com: docker logs $CONTAINER_NAME"
    exit 1
fi

echo ""
echo "========================================"
echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "📝 Configure estas variáveis de ambiente:"
echo ""
echo "# Opção 1: Variáveis separadas"
echo "export USE_LOCAL_DB=true"
echo "export LOCAL_DB_TYPE=postgres"
echo "export LOCAL_PG_USER=$PG_USER"
echo "export LOCAL_PG_PASSWORD=$PG_PASSWORD"
echo "export LOCAL_PG_HOST=localhost"
echo "export LOCAL_PG_PORT=$PG_PORT"
echo "export LOCAL_PG_DATABASE=$PG_DATABASE"
echo ""
echo "# Opção 2: URL completa (mais simples)"
echo "export USE_LOCAL_DB=true"
echo "export LOCAL_DB_TYPE=postgres"
echo "export LOCAL_DATABASE_URL=postgresql://$PG_USER:$PG_PASSWORD@localhost:$PG_PORT/$PG_DATABASE"
echo ""
echo "========================================"
echo ""
echo "🔧 Comandos úteis:"
echo ""
echo "  # Parar PostgreSQL"
echo "  docker stop $CONTAINER_NAME"
echo ""
echo "  # Iniciar PostgreSQL"
echo "  docker start $CONTAINER_NAME"
echo ""
echo "  # Ver logs"
echo "  docker logs $CONTAINER_NAME"
echo ""
echo "  # Acessar console PostgreSQL"
echo "  docker exec -it $CONTAINER_NAME psql -U $PG_USER -d $PG_DATABASE"
echo ""
echo "  # Status do container"
echo "  docker ps -f name=$CONTAINER_NAME"
echo ""
echo "  # Backup do banco"
echo "  docker exec $CONTAINER_NAME pg_dump -U $PG_USER $PG_DATABASE > backup.sql"
echo ""
echo "  # Restaurar backup"
echo "  cat backup.sql | docker exec -i $CONTAINER_NAME psql -U $PG_USER -d $PG_DATABASE"
echo ""
echo "  # Remover container (⚠️  APAGA DADOS!)"
echo "  docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME && docker volume rm legal_pro_pgdata"
echo ""
echo "========================================"
echo ""
echo "🎯 Próximos passos:"
echo ""
echo "1. Configure as variáveis de ambiente acima"
echo "2. Inicialize o banco: python init_local_db.py init"
echo "3. Sincronize dados: python init_local_db.py sync"
echo "4. Execute o sistema: python main.py"
echo ""
echo "✨ Pronto para usar!"
echo ""
