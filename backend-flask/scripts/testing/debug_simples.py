#!/usr/bin/env python3
"""
Debug simples - testa apenas uma API por vez para identificar o problema
"""

import requests
import json
import time
import os

CONTRATO_TESTE = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL

CONTRATANTE: Empresa teste
CONTRATADA: MAYMIDIA SERVIÇOS E MARKETING

DO OBJETO: É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL.

DO PREÇO: R$ 12.678,00 (doze mil seiscentos e setenta e oito reais).

DO FORO: Porto Alegre, Rio Grande do Sul.
"""

def test_api_individual():
    """Testa apenas uma API por vez"""
    print("🔍 TESTE SIMPLES - UMA API POR VEZ")
    print("=" * 50)
    
    # Testar apenas OpenAI primeiro
    try:
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f"Analise este contrato brevemente: {CONTRATO_TESTE}"}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        analise = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        print("✅ OpenAI GPT-4o funcionando")
        print(f"📊 Tokens usados: {tokens}")
        print(f"📝 Preview: {analise[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro OpenAI: {e}")
        return False

def test_via_api():
    """Testa via API HTTP do sistema"""
    print("\n🌐 TESTE VIA API HTTP")
    print("=" * 50)
    
    files = {
        'texto_documento': (None, CONTRATO_TESTE),
        'agentes_selecionados': (None, '1')  # Apenas 1 agente
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/multi-agente-real/analise-real",
            files=files,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            print(f"ID: {data.get('id')}")
            print(f"Agentes: {data.get('total_agentes')}")
            return True
        else:
            print(f"❌ Erro {response.status_code}")
            print(f"Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

if __name__ == "__main__":
    # Primeiro testar API diretamente
    sucesso_direto = test_api_individual()
    
    # Depois testar via HTTP
    sucesso_api = test_via_api()
    
    print("\n" + "=" * 50)
    if sucesso_direto and sucesso_api:
        print("✅ AMBOS OS TESTES PASSARAM")
    elif sucesso_direto:
        print("⚠️ API DIRETA OK, HTTP COM PROBLEMA")
    elif sucesso_api:
        print("⚠️ HTTP OK, API DIRETA COM PROBLEMA")
    else:
        print("❌ AMBOS COM PROBLEMAS")