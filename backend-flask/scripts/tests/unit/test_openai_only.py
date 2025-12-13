#!/usr/bin/env python3
"""
Teste isolado apenas do OpenAI para identificar o problema
"""

import os
import sys
import json

def testar_openai_isolado():
    """Teste OpenAI completamente isolado"""
    
    try:
        print("=== TESTE OPENAI ISOLADO ===")
        print(f"Python: {sys.version}")
        
        # Verificar chave
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada")
            return False
        
        print(f"✅ API Key encontrada: {api_key[:10]}...")
        
        # Importar e criar cliente
        import openai
        print(f"✅ OpenAI version: {openai.__version__}")
        
        # TESTE 1: Cliente padrão
        print("\n--- TESTE 1: Cliente padrão ---")
        try:
            client = openai.OpenAI(api_key=api_key)
            print("✅ Cliente OpenAI criado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar cliente: {e}")
            return False
        
        # TESTE 2: Chamada simples
        print("\n--- TESTE 2: Chamada simples ---")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Diga apenas 'OK'"}],
                max_tokens=5
            )
            resultado = response.choices[0].message.content
            print(f"✅ Resposta: {resultado}")
            print(f"✅ Tokens: {response.usage.total_tokens if response.usage else 0}")
            return True
        except Exception as e:
            print(f"❌ Erro na chamada: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_openai_isolado()
    if sucesso:
        print("\n🎉 TESTE PASSOU! OpenAI funcionando")
        sys.exit(0)
    else:
        print("\n💥 TESTE FALHOU! Problema com OpenAI")
        sys.exit(1)