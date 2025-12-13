#!/usr/bin/env python3
"""
Teste de funcionalidade das APIs de IA
"""
import os
import logging
from openai import OpenAI
import anthropic
from google import genai
from google.genai import types

def testar_openai():
    """Testa conectividade com OpenAI"""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Responda apenas 'OK' se está funcionando"}],
            max_tokens=10,
            temperature=0
        )
        
        resultado = response.choices[0].message.content.strip()
        print(f"✅ OpenAI: {resultado}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI: Erro - {str(e)}")
        return False

def testar_anthropic():
    """Testa conectividade com Anthropic"""
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Responda apenas 'OK' se está funcionando"}]
        )
        
        resultado = message.content[0].text.strip()
        print(f"✅ Anthropic: {resultado}")
        return True
        
    except Exception as e:
        print(f"❌ Anthropic: Erro - {str(e)}")
        return False

def testar_gemini():
    """Testa conectividade com Gemini"""
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Responda apenas 'OK' se está funcionando"
        )
        
        resultado = response.text.strip() if response.text else "Sem resposta"
        print(f"✅ Gemini: {resultado}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini: Erro - {str(e)}")
        return False

def main():
    print("🔍 TESTANDO CONECTIVIDADE DAS APIs DE IA")
    print("=" * 50)
    
    apis_funcionais = []
    
    if testar_openai():
        apis_funcionais.append("OpenAI")
    
    if testar_anthropic():
        apis_funcionais.append("Anthropic")
        
    if testar_gemini():
        apis_funcionais.append("Gemini")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {len(apis_funcionais)}/3 APIs funcionais")
    print(f"✅ APIs ativas: {', '.join(apis_funcionais)}")
    
    if len(apis_funcionais) == 3:
        print("🎉 Todas as APIs estão funcionais!")
    elif len(apis_funcionais) >= 1:
        print("⚠️ Pelo menos uma API está funcional - sistema pode operar")
    else:
        print("❌ Nenhuma API funcional - verificar configurações")

if __name__ == "__main__":
    main()