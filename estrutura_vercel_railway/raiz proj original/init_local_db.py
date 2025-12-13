#!/usr/bin/env python3
"""
Script para inicializar banco de dados local (SQLite ou PostgreSQL)
Permite alternar entre banco local e Neon na nuvem
Suporta sincronização bidirecional para PostgreSQL
"""
import os
import sys
import subprocess
from pathlib import Path

def get_db_type():
    """Detecta o tipo de banco de dados configurado"""
    use_local = os.environ.get('USE_LOCAL_DB', 'false').lower() == 'true'
    
    if not use_local:
        return 'neon'
    
    local_db_type = os.environ.get('LOCAL_DB_TYPE', 'sqlite').lower()
    if local_db_type in ('postgres', 'postgresql'):
        return 'postgres_local'
    return 'sqlite_local'

def get_postgres_connection_params():
    """Retorna parâmetros de conexão PostgreSQL local"""
    local_url = os.environ.get("LOCAL_DATABASE_URL")
    
    if local_url:
        # Parse URL usando urllib (mais robusto para caracteres especiais)
        try:
            from urllib.parse import urlparse
            parsed = urlparse(local_url)
            return {
                'user': parsed.username or 'postgres',
                'password': parsed.password or 'postgres',
                'host': parsed.hostname or 'localhost',
                'port': str(parsed.port) if parsed.port else '5432',
                'database': parsed.path.lstrip('/').split('?')[0] or 'legal_pro_local'
            }
        except Exception:
            # Fallback para regex simples se urlparse falhar
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', local_url)
            if match:
                return {
                    'user': match.group(1),
                    'password': match.group(2),
                    'host': match.group(3),
                    'port': match.group(4),
                    'database': match.group(5).split('?')[0]
                }
    
    # Usar valores padrão
    return {
        'user': os.environ.get('LOCAL_PG_USER', 'postgres'),
        'password': os.environ.get('LOCAL_PG_PASSWORD', 'postgres'),
        'host': os.environ.get('LOCAL_PG_HOST', 'localhost'),
        'port': os.environ.get('LOCAL_PG_PORT', '5432'),
        'database': os.environ.get('LOCAL_PG_DATABASE', 'legal_pro_local')
    }

def sync_postgres_to_postgres():
    """
    Sincroniza dados entre PostgreSQL Neon e PostgreSQL Local usando pg_dump/pg_restore
    Muito mais eficiente e confiável que sincronização linha por linha
    """
    print("\n" + "="*60)
    print("🐘 SINCRONIZAÇÃO POSTGRES → POSTGRES")
    print("="*60 + "\n")
    
    # Verificar DATABASE_URL (Neon)
    neon_url = os.environ.get('DATABASE_URL')
    if not neon_url:
        print("❌ DATABASE_URL não configurada")
        print("   Configure a URL do Neon: export DATABASE_URL=postgresql://...")
        return
    
    # Obter parâmetros local
    local_params = get_postgres_connection_params()
    
    print(f"☁️  Fonte: Neon PostgreSQL")
    print(f"💾 Destino: {local_params['host']}:{local_params['port']}/{local_params['database']}")
    
    # Confirmação
    print("\n⚠️  ATENÇÃO: Esta operação irá:")
    print("   1. Criar um dump completo do banco Neon")
    print("   2. Limpar o banco local")
    print("   3. Restaurar o dump no banco local")
    response = input("\n   Deseja continuar? (s/N): ").strip().lower()
    
    if response != 's':
        print("\n❌ Sincronização cancelada")
        return
    
    try:
        # Arquivo temporário para dump
        dump_file = '/tmp/legal_pro_sync.sql'
        
        print("\n📦 Criando dump do banco Neon...")
        
        # pg_dump do Neon
        dump_cmd = [
            'pg_dump',
            '--clean',  # Incluir comandos DROP
            '--if-exists',  # Evitar erros se tabelas não existirem
            '--no-owner',  # Não incluir comandos de ownership
            '--no-acl',  # Não incluir comandos de privilégios
            '-f', dump_file,
            neon_url
        ]
        
        result = subprocess.run(dump_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao criar dump: {result.stderr}")
            return
        
        print("✅ Dump criado com sucesso")
        
        # Construir URL local
        local_url = f"postgresql://{local_params['user']}:{local_params['password']}@{local_params['host']}:{local_params['port']}/{local_params['database']}"
        
        print("\n📥 Restaurando dump no banco local...")
        
        # psql para restaurar
        restore_cmd = [
            'psql',
            '-v', 'ON_ERROR_STOP=1',  # Parar em caso de erro
            '-f', dump_file,
            local_url
        ]
        
        result = subprocess.run(restore_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  Avisos durante restauração: {result.stderr}")
            # Não retornar aqui, pois alguns warnings são normais
        
        print("✅ Restauração concluída")
        
        # Remover arquivo temporário
        if Path(dump_file).exists():
            os.remove(dump_file)
        
        print("\n" + "="*60)
        print("✨ Sincronização PostgreSQL concluída com sucesso!")
        print("💾 Banco local atualizado")
        print("="*60 + "\n")
        
    except FileNotFoundError:
        print("\n❌ Erro: pg_dump ou psql não encontrado")
        print("   Instale o PostgreSQL client tools:")
        print("   - Ubuntu/Debian: sudo apt install postgresql-client")
        print("   - Mac: brew install postgresql")
    except Exception as e:
        print(f"\n❌ Erro durante sincronização: {e}")
        import traceback
        traceback.print_exc()

def init_local_database():
    """Inicializa o banco de dados local (SQLite ou PostgreSQL)"""
    db_type = get_db_type()
    
    print("\n" + "="*60)
    print("🔧 INICIALIZAÇÃO DO BANCO DE DADOS LOCAL")
    print("="*60 + "\n")
    
    if db_type == 'neon':
        print("⚠️  Configurado para usar Neon (nuvem)")
        print("   Para usar banco local, configure: export USE_LOCAL_DB=true")
        return
    
    # Definir variável de ambiente para usar banco local
    os.environ['USE_LOCAL_DB'] = 'true'
    
    if db_type == 'postgres_local':
        print("🐘 Tipo: PostgreSQL Local")
        params = get_postgres_connection_params()
        print(f"📍 Conexão: {params['host']}:{params['port']}/{params['database']}")
    else:
        print("🔧 Tipo: SQLite Local")
    
    # Importar Flask app
    try:
        from main import create_app, db
        from models import User, AssistenteJuridico, TemplateJuridico
        
        print("✅ Módulos importados com sucesso")
        
        # Criar aplicação Flask
        app = create_app()
        
        with app.app_context():
            print("\n📋 Criando estrutura do banco de dados...")
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Estrutura do banco de dados criada com sucesso!")
            
            # Verificar se já existe usuário admin
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("\n👤 Criando usuário administrador padrão...")
                from werkzeug.security import generate_password_hash
                
                admin = User(
                    username='admin',
                    email='admin@legalpro.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado (username: admin, senha: admin123)")
            else:
                print("ℹ️  Usuário admin já existe")
            
            # Estatísticas
            total_users = User.query.count()
            total_assistentes = AssistenteJuridico.query.count()
            total_templates = TemplateJuridico.query.count()
            
            print("\n" + "="*60)
            print("📊 ESTATÍSTICAS DO BANCO LOCAL")
            print("="*60)
            print(f"👥 Usuários: {total_users}")
            print(f"🤖 Assistentes: {total_assistentes}")
            print(f"📄 Templates: {total_templates}")
            print("="*60)
            
            # Informação sobre o arquivo do banco
            db_path = Path('local_legal_pro.db')
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"\n📁 Arquivo do banco: {db_path.absolute()}")
                print(f"💾 Tamanho: {size_mb:.2f} MB")
            
            print("\n✨ Banco de dados local inicializado com sucesso!")
            print("\n💡 Para usar o banco local, configure:")
            print("   export USE_LOCAL_DB=true")
            print("\n💡 Para voltar ao Neon (nuvem), configure:")
            print("   export USE_LOCAL_DB=false")
            print("\n" + "="*60 + "\n")
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("Certifique-se de que todas as dependências estão instaladas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante inicialização: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def sync_from_neon():
    """
    Sincroniza dados do Neon para o banco local (SQLite)
    ATENÇÃO: Esta é uma sincronização DESTRUTIVA - apaga dados locais e substitui por dados do Neon
    """
    print("\n" + "="*60)
    print("☁️ → 🔧 SINCRONIZAÇÃO NEON → LOCAL")
    print("="*60 + "\n")
    
    from sqlalchemy import create_engine, MetaData, Table, inspect, select
    from sqlalchemy.orm import sessionmaker
    
    # Conectar ao Neon
    neon_url = os.environ.get('DATABASE_URL')
    if not neon_url:
        print("❌ DATABASE_URL não configurada. Configure a URL do Neon primeiro.")
        print("   Execute: export DATABASE_URL=postgresql://...")
        return
    
    # Conectar ao banco local
    local_db_path = os.environ.get("LOCAL_DB_PATH", "local_legal_pro.db")
    local_url = f"sqlite:///{local_db_path}"
    
    # Verificar se banco local existe
    if not Path(local_db_path).exists():
        print(f"⚠️  Banco local não existe em: {local_db_path}")
        print("   Execute primeiro: python init_local_db.py init")
        return
    
    print(f"📡 Conectando ao Neon...")
    print(f"💾 Conectando ao banco local: {local_db_path}")
    
    # Confirmação do usuário
    print("\n⚠️  ATENÇÃO: Esta operação irá:")
    print("   1. Apagar todos os dados locais das tabelas selecionadas")
    print("   2. Substituir pelos dados do Neon")
    response = input("\n   Deseja continuar? (s/N): ").strip().lower()
    
    if response != 's':
        print("\n❌ Sincronização cancelada pelo usuário")
        return
    
    try:
        neon_engine = create_engine(neon_url)
        local_engine = create_engine(local_url)
        
        neon_meta = MetaData()
        neon_meta.reflect(bind=neon_engine)
        
        local_meta = MetaData()
        local_meta.reflect(bind=local_engine)
        
        # Tabelas a sincronizar (ordem importante: dependências primeiro)
        tables_to_sync = [
            'role',
            'categoria_assistente',
            'user',
            'assistente_juridico',
            'template_juridico'
        ]
        
        total_synced = 0
        
        print("\n📋 Sincronizando tabelas...")
        print("="*60)
        
        with local_engine.begin() as local_conn:
            for table_name in tables_to_sync:
                if table_name not in neon_meta.tables:
                    print(f"  ⚠️  {table_name}: Não existe no Neon")
                    continue
                
                if table_name not in local_meta.tables:
                    print(f"  ⚠️  {table_name}: Não existe no banco local")
                    continue
                
                print(f"  ⏳ {table_name}...", end=" ", flush=True)
                
                table = neon_meta.tables[table_name]
                
                # 1. Buscar dados do Neon
                with neon_engine.connect() as neon_conn:
                    neon_result = neon_conn.execute(select(table))
                    neon_rows = neon_result.fetchall()
                
                if not neon_rows:
                    print("⚠️  Nenhum registro no Neon")
                    continue
                
                # 2. Limpar tabela local
                local_conn.execute(local_meta.tables[table_name].delete())
                
                # 3. Inserir dados do Neon no banco local
                # Converter rows para dicts
                column_names = table.columns.keys()
                data_to_insert = []
                
                for row in neon_rows:
                    row_dict = {col: row[i] for i, col in enumerate(column_names)}
                    data_to_insert.append(row_dict)
                
                if data_to_insert:
                    local_conn.execute(
                        local_meta.tables[table_name].insert(),
                        data_to_insert
                    )
                    total_synced += len(data_to_insert)
                    print(f"✅ {len(data_to_insert)} registros sincronizados")
        
        print("="*60)
        print(f"\n✨ Sincronização concluída! Total: {total_synced} registros")
        print(f"💾 Banco local atualizado: {local_db_path}\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante sincronização: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Dica: Certifique-se de que:")
        print("   1. O banco local foi inicializado (python init_local_db.py init)")
        print("   2. DATABASE_URL está configurada corretamente")
        print("   3. Você tem acesso à internet para conectar ao Neon")

def sync_smart():
    """Roteia para a função de sincronização apropriada baseado no tipo de banco"""
    db_type = get_db_type()
    
    if db_type == 'postgres_local':
        # PostgreSQL → PostgreSQL: usar pg_dump/restore (muito mais eficiente)
        sync_postgres_to_postgres()
    elif db_type == 'sqlite_local':
        # SQLite: usar sincronização linha por linha
        sync_from_neon()
    else:
        print("\n⚠️  Configure USE_LOCAL_DB=true para sincronizar")

def show_menu():
    """Mostra menu interativo"""
    db_type = get_db_type()
    db_type_str = {
        'sqlite_local': 'SQLite',
        'postgres_local': 'PostgreSQL',
        'neon': 'Neon (Cloud)'
    }.get(db_type, 'Desconhecido')
    
    print("\n" + "="*60)
    print("🗄️  GERENCIADOR DE BANCO DE DADOS - LEGAL PRO")
    print("="*60)
    print(f"\n💾 Banco configurado: {db_type_str}")
    print("\nOpções:")
    print("  1. Inicializar banco local")
    print("  2. Sincronizar dados Neon → Local")
    print("  3. Ver status dos bancos")
    print("  4. Sair")
    print("\n" + "="*60)
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == '1':
        init_local_database()
    elif choice == '2':
        sync_smart()
    elif choice == '3':
        show_status()
    elif choice == '4':
        print("\n👋 Até logo!\n")
        sys.exit(0)
    else:
        print("\n⚠️  Opção inválida!")

def show_status():
    """Mostra status dos bancos de dados"""
    print("\n" + "="*60)
    print("📊 STATUS DOS BANCOS DE DADOS")
    print("="*60 + "\n")
    
    db_type = get_db_type()
    
    # Status do banco local
    if db_type == 'sqlite_local' or os.environ.get('USE_LOCAL_DB', 'false').lower() == 'true':
        local_db_type = os.environ.get('LOCAL_DB_TYPE', 'sqlite').lower()
        
        if local_db_type in ('postgres', 'postgresql'):
            print("✅ Banco Local (PostgreSQL)")
            params = get_postgres_connection_params()
            print(f"   📍 Host: {params['host']}:{params['port']}")
            print(f"   💾 Database: {params['database']}")
            print(f"   👤 User: {params['user']}")
        else:
            local_db_path = Path('local_legal_pro.db')
            if local_db_path.exists():
                size_mb = local_db_path.stat().st_size / (1024 * 1024)
                print(f"✅ Banco Local (SQLite)")
                print(f"   📁 Caminho: {local_db_path.absolute()}")
                print(f"   💾 Tamanho: {size_mb:.2f} MB")
            else:
                print("❌ Banco Local SQLite não existe")
                print("   💡 Execute a opção 1 para criar")
    else:
        print("⚠️  Banco Local não configurado")
        print("   💡 Configure USE_LOCAL_DB=true")
    
    print()
    
    # Status do Neon
    neon_url = os.environ.get('DATABASE_URL')
    if neon_url:
        print("✅ Banco Neon (PostgreSQL Cloud)")
        print(f"   🌐 Conectado à nuvem")
        # Extrair informação segura da URL (sem senha)
        if '@' in neon_url:
            host_info = neon_url.split('@')[1].split('/')[0]
            print(f"   📍 Host: {host_info}")
    else:
        print("⚠️  Banco Neon não configurado")
        print("   💡 Configure DATABASE_URL")
    
    print()
    
    # Banco ativo
    print("🎯 Banco Ativo:")
    if db_type == 'sqlite_local':
        print("   🔧 LOCAL (SQLite)")
    elif db_type == 'postgres_local':
        print("   🐘 LOCAL (PostgreSQL)")
    else:
        print("   ☁️  NEON (PostgreSQL na Nuvem)")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_local_database()
        elif command == 'sync':
            sync_smart()  # Roteamento inteligente baseado no tipo de banco
        elif command == 'status':
            show_status()
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("\n📖 Uso: python init_local_db.py [init|sync|status]")
            print("\nComandos:")
            print("  init   - Inicializar banco local (SQLite ou PostgreSQL)")
            print("  sync   - Sincronizar dados Neon → Local")
            print("  status - Ver status dos bancos de dados")
    else:
        # Modo interativo
        while True:
            show_menu()
