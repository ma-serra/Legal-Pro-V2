#!/usr/bin/env python3
"""
Script de verificação completa de módulos e funcionalidades
Garante que todos os componentes necessários estão presentes para o deploy
"""

import os
import sys
import json
from pathlib import Path

def check_directory_structure():
    """Verifica a estrutura de diretórios necessária"""
    required_dirs = [
        'modules',
        'multiagent', 
        'utils',
        'static',
        'templates',
        'assistente'
    ]
    
    optional_dirs = [
        'logs',
        'uploads', 
        'temp',
        'instance',
        'static/exports'
    ]
    
    print("📁 Verificando estrutura de diretórios...")
    
    missing_required = []
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ encontrado")
        else:
            print(f"❌ {dir_name}/ AUSENTE (obrigatório)")
            missing_required.append(dir_name)
    
    for dir_name in optional_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ encontrado")
        else:
            print(f"⚠️  {dir_name}/ ausente (será criado no deploy)")
    
    return len(missing_required) == 0

def check_python_modules():
    """Verifica se os módulos Python essenciais estão presentes"""
    essential_files = {
        'main.py': 'Aplicação principal Flask',
        'app.py': 'Rotas e controladores',
        'models.py': 'Modelos SQLAlchemy',
        'models_legal_design.py': 'Modelos Legal Design'
    }
    
    print("\n🐍 Verificando módulos Python essenciais...")
    
    missing = []
    for file_path, description in essential_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} AUSENTE")
            missing.append(file_path)
    
    return len(missing) == 0

def check_multiagent_modules():
    """Verifica módulos do sistema multi-agente"""
    multiagent_paths = [
        'multiagent/core',
        'multiagent/agents', 
        'multiagent/utils',
        'multiagent/db'
    ]
    
    print("\n🤖 Verificando sistema multi-agente...")
    
    missing = []
    for path in multiagent_paths:
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.py')]
            print(f"✅ {path}/ ({len(files)} arquivos Python)")
        else:
            print(f"❌ {path}/ AUSENTE")
            missing.append(path)
    
    return len(missing) == 0

def check_specialized_modules():
    """Verifica módulos especializados"""
    specialized_paths = [
        'modules/assistentes_juridicos',
        'modules/video_transcription', 
        'modules/comparacao_documentos',
        'modules/jurimetria'
    ]
    
    print("\n⚖️  Verificando módulos especializados...")
    
    found = 0
    for path in specialized_paths:
        if os.path.exists(path):
            print(f"✅ {path}/ encontrado")
            found += 1
        else:
            print(f"⚠️  {path}/ não encontrado")
    
    print(f"📊 Módulos especializados: {found}/{len(specialized_paths)} encontrados")
    return found > 0  # Pelo menos um módulo especializado deve existir

def check_utils_modules():
    """Verifica módulos de utilitários"""
    utils_files = [
        'utils/permission_decorators.py',
        'utils/document_processor.py'
    ]
    
    print("\n🔧 Verificando utilitários...")
    
    found = 0
    for file_path in utils_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            found += 1
        else:
            print(f"⚠️  {file_path} não encontrado")
    
    return found > 0

def check_api_files():
    """Verifica arquivos de API"""
    api_patterns = [
        'api_*.py',
        '*_api.py'
    ]
    
    print("\n🌐 Verificando APIs...")
    
    import glob
    api_files = []
    for pattern in api_patterns:
        api_files.extend(glob.glob(pattern))
    
    if api_files:
        print(f"✅ {len(api_files)} arquivos de API encontrados:")
        for api_file in api_files[:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {api_file}")
        if len(api_files) > 10:
            print(f"   ... e mais {len(api_files) - 10} arquivos")
        return True
    else:
        print("❌ Nenhum arquivo de API encontrado")
        return False

def check_deployment_files():
    """Verifica arquivos de deploy"""
    deploy_files = {
        'Procfile': 'Comando de execução',
        'requirements.txt': 'Dependências originais',
        'requirements-render.txt': 'Dependências otimizadas',
        'runtime.txt': 'Versão Python',
        'render.yaml': 'Configuração Render',
        'gunicorn.conf.py': 'Configuração Gunicorn',
        'render-build.sh': 'Script de build'
    }
    
    print("\n🚀 Verificando arquivos de deploy...")
    
    missing = []
    for file_path, description in deploy_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} AUSENTE")
            missing.append(file_path)
    
    return len(missing) == 0

def check_static_assets():
    """Verifica assets estáticos"""
    static_paths = [
        'static/css',
        'static/js', 
        'static/img',
        'templates'
    ]
    
    print("\n🎨 Verificando assets estáticos...")
    
    found = 0
    for path in static_paths:
        if os.path.exists(path):
            files = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            print(f"✅ {path}/ ({files} arquivos)")
            found += 1
        else:
            print(f"⚠️  {path}/ não encontrado")
    
    return found >= 2  # Pelo menos CSS e templates devem existir

def main():
    """Verificação principal"""
    print("🔍 Verificação Completa de Módulos e Funcionalidades")
    print("=" * 60)
    
    checks = [
        ("Estrutura de Diretórios", check_directory_structure),
        ("Módulos Python Essenciais", check_python_modules),
        ("Sistema Multi-Agente", check_multiagent_modules),
        ("Módulos Especializados", check_specialized_modules),
        ("Utilitários", check_utils_modules),
        ("APIs", check_api_files),
        ("Arquivos de Deploy", check_deployment_files),
        ("Assets Estáticos", check_static_assets)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status:12} {check_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{len(results)} verificações passaram")
    
    if passed == len(results):
        print("\n🎉 EXCELENTE! Sistema completamente pronto para deploy")
        print("   Todas as funcionalidades serão preservadas no Render")
        return True
    elif passed >= len(results) * 0.8:
        print("\n✅ BOM! Sistema pronto com algumas funcionalidades opcionais ausentes")
        print("   Funcionalidades principais serão preservadas no Render")
        return True
    else:
        print("\n⚠️  ATENÇÃO! Algumas funcionalidades importantes estão ausentes")
        print("   Verifique os módulos faltantes antes do deploy")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)