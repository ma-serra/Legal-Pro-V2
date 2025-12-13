#!/usr/bin/env python3
"""
Teste simplificado para identificar o problema exato
"""
import requests

# Teste com texto menor primeiro
texto_pequeno = """
Contrato de Arrendamento Rural

ARRENDANTES: João Silva e Maria Silva

ARRENDATÁRIO: Pedro Santos

Cláusula Primeira - Do Objeto
Os ARRENDANTES arrendam ao ARRENDATÁRIO área de 100 hectares para atividade agrícola.

Cláusula Segunda - Do Prazo
Prazo de 3 anos, início em 01/01/2025, término em 31/12/2027.

Cláusula Terceira - Do Pagamento
Pagamento anual de 46kg de boi gordo por hectare.
"""

url = "http://localhost:5000/api/analise-multi-agente"

print("🔍 TESTE 1: Texto pequeno")
dados = {
    'texto_documento': texto_pequeno,
    'agentes_selecionados': ['21']
}

response = requests.post(url, data=dados, timeout=30)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCESSO - Texto pequeno funciona")
    result = response.json()
    print(f"Fallback: {result.get('fallback_mode')}")
    print(f"Agentes: {result.get('total_agentes')}")
else:
    print(f"❌ ERRO: {response.text[:200]}")

print("\n" + "="*50)

# Agora teste com texto médio
texto_medio = texto_pequeno * 3  # Triplicar o texto

print("🔍 TESTE 2: Texto médio")
dados = {
    'texto_documento': texto_medio,
    'agentes_selecionados': ['21']
}

response = requests.post(url, data=dados, timeout=30)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCESSO - Texto médio funciona")
    result = response.json()
    print(f"Fallback: {result.get('fallback_mode')}")
    print(f"Agentes: {result.get('total_agentes')}")
else:
    print(f"❌ ERRO: {response.text[:200]}")