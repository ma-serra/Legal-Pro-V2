#!/usr/bin/env python3
"""
TESTE DA API ÚNICA QUE FUNCIONA - BASEADO NOS TESTES INDIVIDUAIS
"""

import requests
import time

documento = "CONTRATO DE TESTE JURÍDICO - análise rápida para diagnóstico"

print("🎯 TESTE API ÚNICA (baseado nos testes individuais funcionais)")
print("=" * 60)

# Testar cada API individualmente
apis = ['openai', 'anthropic', 'gemini']

for api in apis:
    print(f"\n🔍 TESTANDO {api.upper()}")
    print("-" * 30)
    
    url = "http://localhost:5000/api/analise-unica-api"
    payload = {
        'texto_documento': documento,
        'api': api
    }
    
    inicio = time.time()
    
    try:
        response = requests.post(url, data=payload, timeout=120)
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.1f}s")
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'sucesso':
                    resultado = data.get('resultado', {})
                    tokens = resultado.get('tokens_usados', 0)
                    modelo = resultado.get('modelo', 'N/A')
                    print(f"✅ {api.upper()}: SUCESSO - {tokens} tokens ({modelo})")
                else:
                    print(f"⚠️ {api.upper()}: {data.get('status', 'erro')}")
            except Exception as e:
                print(f"❌ {api.upper()}: JSON inválido - {e}")
        else:
            print(f"❌ {api.upper()}: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        tempo = time.time() - inicio
        print(f"⏰ {api.upper()}: TIMEOUT após {tempo:.1f}s")
    except Exception as e:
        tempo = time.time() - inicio
        print(f"❌ {api.upper()}: ERRO após {tempo:.1f}s - {str(e)[:50]}")

print("\n" + "=" * 60)
print("💡 Esta API processa apenas 1 API por vez - baseado nos testes individuais que funcionaram")