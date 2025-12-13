#!/bin/bash

# Script de Deploy Automatizado para VPS Hostinger
# Legal Design Pro V2 - Sistema Jurídico Multi-Agente

set -e  # Parar execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configurações (modificar conforme necessário)
APP_NAME="legal-design-pro-v2"
APP_USER="legaldesign"
APP_DIR="/home/$APP_USER/apps/$APP_NAME"
REPO_URL="https://github.com/SEU_USUARIO/legal-design-pro-v2.git"
DOMAIN="seu_dominio.com"
DB_NAME="legal_design_pro_v2"
DB_USER="legaldesign"
DB_PASS="senha_super_segura_123!@#"

# Verificar se está executando como root
if [[ $EUID -eq 0 ]]; then
   log_error "Este script não deve ser executado como root"
   exit 1
fi

log_info "Iniciando deploy do Legal Design Pro V2 na VPS Hostinger..."

# 1. Verificar e instalar dependências do sistema
log_info "Verificando dependências do sistema..."

if ! command -v python3.11 &> /dev/null; then
    log_warning "Python 3.11 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
fi

if ! command -v git &> /dev/null; then
    log_warning "Git não encontrado. Instalando..."
    sudo apt install -y git
fi

if ! command -v nginx &> /dev/null; then
    log_warning "Nginx não encontrado. Instalando..."
    sudo apt install -y nginx
fi

if ! command -v psql &> /dev/null; then
    log_warning "PostgreSQL não encontrado. Favor instalar manualmente seguindo o guia."
    exit 1
fi

log_success "Dependências do sistema verificadas"

# 2. Criar estrutura de diretórios
log_info "Criando estrutura de diretórios..."

mkdir -p /home/$APP_USER/apps
mkdir -p /home/$APP_USER/backups
mkdir -p /home/$APP_USER/logs

log_success "Estrutura de diretórios criada"

# 3. Clonar ou atualizar repositório
log_info "Configurando código da aplicação..."

if [ ! -d "$APP_DIR" ]; then
    log_info "Clonando repositório..."
    cd /home/$APP_USER/apps
    git clone $REPO_URL $APP_NAME
else
    log_info "Atualizando repositório existente..."
    cd $APP_DIR
    git pull origin main
fi

cd $APP_DIR
log_success "Código da aplicação configurado"

# 4. Configurar ambiente Python
log_info "Configurando ambiente Python..."

if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    python3.11 -m venv venv
fi

source venv/bin/activate

log_info "Atualizando pip..."
pip install --upgrade pip

log_info "Instalando dependências Python..."
if [ -f "vps-requirements.txt" ]; then
    pip install -r vps-requirements.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    log_error "Arquivo de dependências não encontrado!"
    exit 1
fi

log_success "Ambiente Python configurado"

# 5. Criar diretórios da aplicação
log_info "Criando diretórios da aplicação..."

mkdir -p logs uploads temp static/exports instance
chmod 755 logs uploads temp static/exports

# Criar arquivos de log vazios
touch logs/debug.log logs/transcricao_debug.log logs/transcricao_completa.log logs/gunicorn-access.log logs/gunicorn-error.log
chmod 644 logs/*.log

log_success "Diretórios da aplicação criados"

# 6. Verificar arquivo .env
log_info "Verificando configuração de ambiente..."

if [ ! -f ".env" ]; then
    log_warning "Arquivo .env não encontrado. Criando template..."
    cat > .env << EOF
# === CONFIGURAÇÕES ESSENCIAIS ===
FLASK_ENV=production
DEBUG=False
SESSION_SECRET=ALTERE_ESTA_CHAVE_SECRETA_32_CARACTERES_MINIMO

# === BANCO DE DADOS ===
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME

# === REDIS ===
REDIS_URL=redis://localhost:6379/0

# === APIs DE IA (OBRIGATÓRIAS) ===
OPENAI_API_KEY=sk-SUBSTITUA_PELA_SUA_CHAVE_OPENAI
ANTHROPIC_API_KEY=sk-ant-SUBSTITUA_PELA_SUA_CHAVE_ANTHROPIC
GOOGLE_API_KEY=SUBSTITUA_PELA_SUA_CHAVE_GOOGLE

# === TRANSCRIÇÃO DE ÁUDIO ===
ASSEMBLYAI_API_KEY=SUBSTITUA_PELA_SUA_CHAVE_ASSEMBLYAI

# === BANCO VETORIAL ===
QDRANT_URL=https://SUBSTITUA_PELA_SUA_INSTANCIA.qdrant.io
QDRANT_API_KEY=SUBSTITUA_PELA_SUA_CHAVE_QDRANT

# === CONFIGURAÇÕES DE PRODUÇÃO ===
WORKERS=4
TIMEOUT=300
BIND=0.0.0.0:8000

# === DIRETÓRIOS ===
UPLOAD_FOLDER=$APP_DIR/uploads
TEMP_FOLDER=$APP_DIR/temp
LOG_FOLDER=$APP_DIR/logs
EXPORT_FOLDER=$APP_DIR/static/exports
EOF
    log_warning "IMPORTANTE: Edite o arquivo .env com suas configurações reais!"
    log_warning "Execute: vim $APP_DIR/.env"
fi

log_success "Configuração de ambiente verificada"

# 7. Testar aplicação
log_info "Testando aplicação..."

# Testar importação
if python -c "from main import app; print('Aplicação importável')" 2>/dev/null; then
    log_success "Aplicação importável com sucesso"
else
    log_error "Erro ao importar aplicação. Verifique dependências."
    exit 1
fi

# 8. Configurar Gunicorn
log_info "Configurando Gunicorn..."

if [ ! -f "gunicorn.conf.py" ]; then
    cat > gunicorn.conf.py << 'EOF'
# Configuração do Gunicorn para VPS
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Preload
preload_app = True

# Logging
accesslog = "/home/legaldesign/apps/legal-design-pro-v2/logs/gunicorn-access.log"
errorlog = "/home/legaldesign/apps/legal-design-pro-v2/logs/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "legal-design-pro-v2"

# Server mechanics
daemon = False
pidfile = "/home/legaldesign/apps/legal-design-pro-v2/gunicorn.pid"
user = "legaldesign"
group = "legaldesign"
tmp_upload_dir = "/home/legaldesign/apps/legal-design-pro-v2/temp"
EOF
fi

log_success "Gunicorn configurado"

# 9. Configurar serviço systemd
log_info "Configurando serviço systemd..."

sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Legal Design Pro V2 - Sistema Jurídico Multi-Agente
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5
KillMode=mixed
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=$APP_DIR/logs
ReadWritePaths=$APP_DIR/uploads
ReadWritePaths=$APP_DIR/temp
ReadWritePaths=$APP_DIR/static/exports

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME

log_success "Serviço systemd configurado"

# 10. Configurar Nginx
log_info "Configurando Nginx..."

sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Logs
    access_log /var/log/nginx/legal-design-access.log;
    error_log /var/log/nginx/legal-design-error.log;

    # Upload limit
    client_max_body_size 100M;

    # Timeout configurations
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 1d;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
    }
}
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

# Remover site padrão se existir
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
if sudo nginx -t; then
    log_success "Configuração do Nginx válida"
else
    log_error "Erro na configuração do Nginx"
    exit 1
fi

log_success "Nginx configurado"

# 11. Criar script de backup
log_info "Configurando backup automático..."

cat > /home/$APP_USER/backup.sh << EOF
#!/bin/bash

# Configurações
BACKUP_DIR="/home/$APP_USER/backups"
APP_DIR="$APP_DIR"
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"
DATE=\$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p \$BACKUP_DIR

# Backup do banco de dados
pg_dump -U \$DB_USER -h localhost \$DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql

# Backup dos arquivos da aplicação
tar -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz \\
    --exclude="\$APP_DIR/venv" \\
    --exclude="\$APP_DIR/__pycache__" \\
    --exclude="\$APP_DIR/temp/*" \\
    \$APP_DIR

# Manter apenas os últimos 7 dias de backup
find \$BACKUP_DIR -type f -mtime +7 -delete

echo "Backup concluído: \$DATE"
EOF

chmod +x /home/$APP_USER/backup.sh

log_success "Backup automático configurado"

# 12. Iniciar serviços
log_info "Iniciando serviços..."

# Iniciar aplicação
sudo systemctl start $APP_NAME

# Verificar status
if sudo systemctl is-active --quiet $APP_NAME; then
    log_success "Aplicação iniciada com sucesso"
else
    log_error "Falha ao iniciar aplicação. Verificando logs..."
    sudo systemctl status $APP_NAME
    exit 1
fi

# Reiniciar Nginx
sudo systemctl restart nginx

if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx reiniciado com sucesso"
else
    log_error "Falha ao reiniciar Nginx"
    exit 1
fi

# 13. Teste final
log_info "Executando teste final..."

sleep 5

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|302"; then
    log_success "Aplicação respondendo corretamente"
else
    log_warning "Aplicação não está respondendo como esperado"
fi

# 14. Exibir informações finais
log_success "Deploy concluído com sucesso!"

echo
echo "=========================================="
echo "  LEGAL DESIGN PRO V2 - DEPLOY COMPLETO"
echo "=========================================="
echo
echo "📍 Aplicação instalada em: $APP_DIR"
echo "🌐 Domínio configurado: $DOMAIN"
echo "🔧 Serviço systemd: $APP_NAME"
echo "📝 Logs da aplicação: $APP_DIR/logs/"
echo "💾 Backups: /home/$APP_USER/backups/"
echo
echo "🔧 PRÓXIMOS PASSOS OBRIGATÓRIOS:"
echo "1. Editar arquivo .env com suas configurações:"
echo "   vim $APP_DIR/.env"
echo
echo "2. Reiniciar aplicação após configurar .env:"
echo "   sudo systemctl restart $APP_NAME"
echo
echo "3. Configurar SSL (se necessário):"
echo "   sudo certbot --nginx -d $DOMAIN"
echo
echo "4. Verificar status dos serviços:"
echo "   sudo systemctl status $APP_NAME"
echo "   sudo systemctl status nginx"
echo
echo "📊 COMANDOS ÚTEIS:"
echo "- Ver logs: tail -f $APP_DIR/logs/gunicorn-error.log"
echo "- Reiniciar app: sudo systemctl restart $APP_NAME"
echo "- Executar backup: /home/$APP_USER/backup.sh"
echo
log_success "Sistema pronto para uso!"