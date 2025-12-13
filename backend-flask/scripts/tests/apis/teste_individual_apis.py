#!/usr/bin/env python3
"""
TESTE INDIVIDUAL DAS 3 APIS PARA IDENTIFICAR QUAL FUNCIONA
"""

import requests
import time
import json

documento = "CONTRATO DE TESTE JURÍDICO - análise rápida para diagnóstico"

print("🔍 TESTE INDIVIDUAL DAS 3 APIS")
print("=" * 50)

# Lista de APIs para testar
apis_teste = [
    {"nome": "OpenAI", "endpoint": "/api/teste-openai-individual"},
    {"nome": "Anthropic", "endpoint": "/api/teste-anthropic-individual"}, 
    {"nome": "Gemini", "endpoint": "/api/teste-gemini-individual"}
]

for api in apis_teste:
    print(f"\n🎯 TESTANDO {api['nome']}")
    print("-" * 30)
    
    url = f"http://localhost:5000{api['endpoint']}"
    payload = {"texto_documento": documento}
    
    inicio = time.time()
    
    try:
        response = requests.post(url, data=payload, timeout=120)
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.1f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('status') == 'sucesso':
                    tokens = data.get('tokens_usados', 0)
                    print(f"✅ {api['nome']}: SUCESSO - {tokens} tokens")
                else:
                    print(f"⚠️ {api['nome']}: {data.get('erro', 'Erro desconhecido')}")
            except:
                print(f"❌ {api['nome']}: JSON inválido")
        elif response.status_code == 404:
            print(f"❌ {api['nome']}: Endpoint não encontrado")
        else:
            print(f"❌ {api['nome']}: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        tempo = time.time() - inicio
        print(f"⏰ {api['nome']}: TIMEOUT após {tempo:.1f}s")
    except Exception as e:
        tempo = time.time() - inicio
        print(f"❌ {api['nome']}: ERRO após {tempo:.1f}s - {str(e)[:50]}")

print("\n" + "=" * 50)