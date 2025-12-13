#!/usr/bin/env python3
"""
TESTE SIMPLES DE UMA API PARA IDENTIFICAR PROBLEMA
"""

import requests
import time
import json

print("🔍 TESTE DIAGNÓSTICO - UMA API APENAS")
print("=" * 50)

# Documento mínimo
documento = "CONTRATO DE TESTE - análise simples"

url = "http://localhost:5000/api/multi-agente-real/analise-real"
payload = {
    "texto_documento": documento,
    "agentes[]": ["1"]  # Apenas 1 agente
}

print(f"📄 Documento: {len(documento)} caracteres")
print("🎯 Testando apenas 1 agente para diagnóstico")
print("-" * 30)

inicio = time.time()

try:
    print("🚀 Enviando requisição...")
    response = requests.post(url, data=payload, timeout=120)
    tempo = time.time() - inicio
    
    print(f"⏱️ Tempo: {tempo:.1f}s")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"🆔 Sistema ID: {data.get('sistema_id', 'N/A')}")
            
            resultados = data.get('resultados_por_api', {})
            for api, resultado in resultados.items():
                if resultado and api != 'resumo_consolidado':
                    status = resultado.get('status', 'N/A')
                    tokens = resultado.get('tokens_usados', 0)
                    print(f"   📡 {api.upper()}: {status} - {tokens} tokens")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido: {e}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    elif response.status_code == 500:
        print("❌ ERRO INTERNO 500")
        print(f"📄 Conteúdo: {response.text[:300]}")
    else:
        print(f"❌ Status {response.status_code}")
        print(f"📄 Resposta: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    tempo = time.time() - inicio
    print(f"⏰ TIMEOUT após {tempo:.1f}s")
except Exception as e:
    tempo = time.time() - inicio
    print(f"❌ ERRO após {tempo:.1f}s: {e}")

print("\n" + "=" * 50)