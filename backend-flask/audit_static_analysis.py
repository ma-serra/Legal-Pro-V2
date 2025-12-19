
import os
import re

def audit_static():
    print("="*60)
    print("🔍 AUDITORIA ESTÁTICA DO SISTEMA (SAFE MODE)")
    print("="*60)
    
    base_dir = os.getcwd()
    main_path = os.path.join(base_dir, 'main.py')
    
    # 1. Verificar Main.py
    print("\n📄 Verificando main.py...")
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    checks = {
        'CHECK_PROCESSOS_BP_IMPORT': r'from modules\.processos\.routes import processos_bp',
        'CHECK_PROCESSOS_BP_REGISTER': r'app\.register_blueprint\(processos_bp\)',
        'CHECK_ML_BP_REGISTER': r'app\.register_blueprint\(ml_tributario_bp\)',
        'CHECK_TRIBUTARIO_BP_REGISTER': r'app\.register_blueprint\(tributario_bp\)',
        'CHECK_OPTIONS_HANDLER': r'@app\.before_request'
    }
    
    for label, regex in checks.items():
        found = re.search(regex, content)
        status = "✅ PASSOU" if found else "❌ FALHOU"
        print(f"  - {label}: {status}")

    # 2. Verificar Modules
    modules = {
        'PROCESSOS': 'modules/processos/routes.py',
        'ML TRIBUTARIO': 'modules/ml_tributario/routes.py',
        'TRIBUTARIO': 'modules/processos_tributario/routes.py'
    }
    
    for name, rel_path in modules.items():
        print(f"\n📦 MÓDULO: {name}")
        path = os.path.join(base_dir, rel_path)
        if not os.path.exists(path):
            print(f"  ❌ ARQUIVO NÃO ENCONTRADO: {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        endpoints = []
        for line in lines:
            if '@' in line and '.route' in line:
                match = re.search(r"\.route\('([^']+)'", line)
                if match:
                    endpoints.append(match.group(1))
        
        if endpoints:
            print(f"  ✅ {len(endpoints)} endpoints detectados:")
            for e in endpoints:
                print(f"    - {e}")
        else:
            print("  ⚠️ NENHUM ENDPOINT ENCONTRADO (possível erro de parse ou arquivo vazio)")

if __name__ == "__main__":
    audit_static()
