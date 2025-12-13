#!/usr/bin/env python3
"""
Health check script para verificar o status da aplicação antes do deploy
"""

import requests
import sys
import json
import time
from datetime import datetime

def check_health():
    """Verifica a saúde da aplicação"""
    base_url = "http://localhost:5000"
    
    checks = {
        "server": f"{base_url}/",
        "health": f"{base_url}/health",
        "api_status": f"{base_url}/api/status",
        "auth_login": f"{base_url}/auth/login",
        "home": f"{base_url}/home",
    }
    
    results = {}
    total_checks = len(checks)
    passed_checks = 0
    
    print("🔍 Executando health check...")
    print(f"Timestamp: {datetime.now()}")
    print("-" * 50)
    
    for name, url in checks.items():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=False)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)
            
            if response.status_code in [200, 302]:  # 302 para redirects
                status = "✅ PASS"
                passed_checks += 1
            else:
                status = f"❌ FAIL ({response.status_code})"
            
            results[name] = {
                "status": status,
                "code": response.status_code,
                "time": f"{response_time}ms"
            }
            
            print(f"{name:12} | {status:15} | {response.status_code} | {response_time}ms")
            
        except Exception as e:
            results[name] = {
                "status": "❌ ERROR",
                "error": str(e),
                "time": "N/A"
            }
            print(f"{name:12} | ❌ ERROR        | {str(e)[:30]}...")
    
    print("-" * 50)
    print(f"Resultado: {passed_checks}/{total_checks} checks passaram")
    
    if passed_checks == total_checks:
        print("🎉 Aplicação PRONTA para deploy!")
        return True
    else:
        print("⚠️  Aplicação precisa de ajustes antes do deploy")
        return False

def check_apis():
    """Verifica se as APIs estão configuradas"""
    import os
    
    print("\n🔑 Verificando configuração de APIs...")
    
    apis = {
        "OpenAI": os.environ.get("OPENAI_API_KEY"),
        "AssemblyAI": os.environ.get("ASSEMBLYAI_API_KEY"),
        "Database": os.environ.get("DATABASE_URL"),
        "Session Secret": os.environ.get("SESSION_SECRET"),
    }
    
    configured = 0
    for name, key in apis.items():
        if key and len(key) > 10:
            print(f"✅ {name}: Configurado")
            configured += 1
        else:
            print(f"❌ {name}: Não configurado")
    
    print(f"APIs configuradas: {configured}/{len(apis)}")
    return configured >= 2  # Pelo menos OpenAI e Database

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LEGAL PRO - HEALTH CHECK PARA DEPLOY")
    print("=" * 60)
    
    # Verificar APIs
    apis_ok = check_apis()
    
    # Verificar endpoints
    server_ok = check_health()
    
    print("\n" + "=" * 60)
    if server_ok and apis_ok:
        print("🎯 STATUS FINAL: PRONTO PARA DEPLOY!")
        sys.exit(0)
    else:
        print("🚨 STATUS FINAL: NECESSÁRIA CONFIGURAÇÃO")
        sys.exit(1)