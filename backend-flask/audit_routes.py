
import sys
import os
from flask import Flask

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

# Configurar variáveis de ambiente dummy para evitar erro de inicialização do DB
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'audit-debug-key'
os.environ['FAST_STARTUP'] = 'true'

try:
    from main import app
except Exception as e:
    print(f"CRITICAL ERROR: Could not import main app: {e}")
    sys.exit(1)

def audit_routes():
    print("="*60)
    print("🔍 AUDITORIA DE ROTAS REGISTRADAS (BACKEND)")
    print("="*60)
    
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'url': str(rule)
        })
    
    # Ordenar por URL
    routes.sort(key=lambda x: x['url'])
    
    # Filtrar áreas críticas
    areas = {
        'PROCESSOS': '/api/processos',
        'ML TRIBUTARIO': '/api/ml/tributario',
        'TIMELINE': '/api/timeline',
        'AUTH': '/api/auth'
    }
    
    stats = {k: 0 for k in areas.keys()}
    
    for area_name, prefix in areas.items():
        print(f"\n📦 MÓDULO: {area_name}")
        print(f"{'-'*60}")
        found = False
        for r in routes:
            if r['url'].startswith(prefix):
                print(f"  ✅ [{r['methods']}] {r['url']} -> {r['endpoint']}")
                stats[area_name] += 1
                found = True
        
        if not found:
            print(f"  ❌ NENHUMA ROTA ENCONTRADA PARA ESTE MÓDULO")
            
    print("\n" + "="*60)
    print("📊 RESUMO DA AUDITORIA")
    print("="*60)
    all_good = True
    for area, count in stats.items():
        status = "✅ OK" if count > 0 else "❌ FALHA"
        if count == 0: all_good = False
        print(f"{area}: {count} endpoints ativos [{status}]")
        
    if all_good:
        print("\n🏆 CONCLUSÃO: Todos os módulos críticos estão ativos!")
    else:
        print("\n⚠️ ALERTA: Existem módulos críticos sem rotas registradas!")

if __name__ == "__main__":
    audit_routes()
