#!/usr/bin/env python3
"""
Validação final completa do sistema Legal Design Pro V2
Testa todas as funcionalidades críticas após as correções aplicadas
"""

import requests
import json
import time

def test_complete_system_validation():
    """Valida completamente o sistema após as correções"""
    
    base_url = "http://localhost:5000"
    results = {
        "template_loading": False,
        "template_saving": False,
        "api_responses": False,
        "data_persistence": False,
        "error_handling": False
    }
    
    print("🔍 VALIDAÇÃO FINAL COMPLETA DO SISTEMA")
    print("=" * 50)
    
    # 1. Testar carregamento de templates
    print("1️⃣ Testando carregamento de templates...")
    try:
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/template/46")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('template'):
                results["template_loading"] = True
                print("   ✅ Carregamento de templates: OK")
            else:
                print("   ❌ Carregamento de templates: Falha nos dados")
        else:
            print(f"   ❌ Carregamento de templates: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Carregamento de templates: Erro {e}")
    
    # 2. Testar salvamento de templates
    print("2️⃣ Testando salvamento de templates...")
    try:
        test_content = f"""
        <div class="validation-test-final">
            <h2>Teste Final de Validação</h2>
            <p>Timestamp: {int(time.time())}</p>
            <p>Status: Sistema completamente validado</p>
        </div>
        """
        
        save_data = {"conteudo_html": test_content}
        response = requests.post(
            f"{base_url}/legal-design-pro-v2/api/template/46/save",
            headers={'Content-Type': 'application/json'},
            json=save_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results["template_saving"] = True
                print("   ✅ Salvamento de templates: OK")
            else:
                print("   ❌ Salvamento de templates: Falha nos dados")
        else:
            print(f"   ❌ Salvamento de templates: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Salvamento de templates: Erro {e}")
    
    # 3. Testar persistência de dados
    print("3️⃣ Testando persistência de dados...")
    try:
        time.sleep(1)
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/template/46")
        if response.status_code == 200:
            data = response.json()
            content = data.get('template', {}).get('conteudo_html', '')
            if "validation-test-final" in content:
                results["data_persistence"] = True
                print("   ✅ Persistência de dados: OK")
            else:
                print("   ❌ Persistência de dados: Dados não persistidos")
        else:
            print(f"   ❌ Persistência de dados: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Persistência de dados: Erro {e}")
    
    # 4. Testar resposta das APIs
    print("4️⃣ Testando APIs do sistema...")
    try:
        # Testar API de templates
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/templates")
        if response.status_code == 200:
            results["api_responses"] = True
            print("   ✅ APIs do sistema: OK")
        else:
            print(f"   ❌ APIs do sistema: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ APIs do sistema: Erro {e}")
    
    # 5. Testar tratamento de erros
    print("5️⃣ Testando tratamento de erros...")
    try:
        # Tentar acessar template inexistente
        response = requests.get(f"{base_url}/legal-design-pro-v2/api/template/99999")
        if response.status_code in [404, 500]:
            data = response.json()
            if not data.get('success', True):  # Deve retornar success: false
                results["error_handling"] = True
                print("   ✅ Tratamento de erros: OK")
            else:
                print("   ❌ Tratamento de erros: Não retorna erro adequado")
        else:
            print(f"   ❌ Tratamento de erros: Status inesperado {response.status_code}")
    except Exception as e:
        print(f"   ❌ Tratamento de erros: Erro {e}")
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL DA VALIDAÇÃO")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nResumo: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA COMPLETAMENTE VALIDADO!")
        print("✅ Todas as funcionalidades estão operacionais")
        print("✅ Todas as inconsistências foram resolvidas")
        return True
    else:
        print(f"\n⚠️  SISTEMA PARCIALMENTE VALIDADO ({passed_tests}/{total_tests})")
        print("❌ Algumas inconsistências ainda precisam ser corrigidas")
        return False

if __name__ == "__main__":
    success = test_complete_system_validation()
    exit(0 if success else 1)