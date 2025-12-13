#!/usr/bin/env python3
"""
Teste individual das 3 APIs para identificar problemas de timeout SSL
"""

import os
import time
import asyncio

def teste_openai():
    print("🔵 TESTANDO OPENAI GPT-4o...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Análise jurídica breve de um contrato de marketing digital"}],
            max_tokens=500,
            timeout=15  # Timeout baixo para teste
        )
        end = time.time()
        
        print(f"   ✅ OpenAI OK - {end-start:.2f}s - {len(response.choices[0].message.content)} chars")
        return True
    except Exception as e:
        print(f"   ❌ OpenAI ERRO: {e}")
        return False

def teste_anthropic():
    print("🟡 TESTANDO ANTHROPIC CLAUDE...")
    try:
        import anthropic
        import httpx
        
        # Cliente otimizado para evitar timeouts
        http_client = httpx.Client(
            timeout=httpx.Timeout(15.0, connect=5.0, read=10.0),
            limits=httpx.Limits(max_connections=1, max_keepalive_connections=0),
            verify=True
        )
        
        client = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
            http_client=http_client
        )
        
        start = time.time()
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": "Análise jurídica breve de um contrato de marketing digital"}]
        )
        end = time.time()
        
        analise = response.content[0].text if response.content else ""
        print(f"   ✅ Anthropic OK - {end-start:.2f}s - {len(analise)} chars")
        return True
    except Exception as e:
        print(f"   ❌ Anthropic ERRO: {e}")
        return False

def teste_gemini():
    print("🟢 TESTANDO GOOGLE GEMINI...")
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        start = time.time()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Análise jurídica breve de um contrato de marketing digital",
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.3
            )
        )
        end = time.time()
        
        print(f"   ✅ Gemini OK - {end-start:.2f}s - {len(response.text or '')} chars")
        return True
    except Exception as e:
        print(f"   ❌ Gemini ERRO: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TESTE INDIVIDUAL DAS 3 APIS")
    print("=" * 60)
    
    resultados = {
        'openai': teste_openai(),
        'anthropic': teste_anthropic(),
        'gemini': teste_gemini()
    }
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS:")
    funcionais = [api for api, ok in resultados.items() if ok]
    print(f"✅ APIs funcionais: {funcionais}")
    print(f"❌ APIs com problema: {[api for api, ok in resultados.items() if not ok]}")
    print(f"📈 Taxa de sucesso: {len(funcionais)}/3 ({len(funcionais)/3*100:.1f}%)")
    print("=" * 60)