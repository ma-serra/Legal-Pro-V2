#!/usr/bin/env python3
"""
Teste simples para verificar se a inicialização do OpenAI está funcionando
"""
import os
import sys

def test_openai_basic():
    """Teste básico de inicialização do OpenAI"""
    try:
        print("🔧 Testando importação do openai...")
        import openai
        print("✅ Importação OpenAI OK")
        
        print("🔧 Verificando API key...")
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada")
            return False
        
        if not api_key.startswith('sk-'):
            print(f"❌ API key formato inválido: {api_key[:10]}...")
            return False
        
        print(f"✅ API key encontrada: {api_key[:10]}...")
        
        print("🔧 Testando inicialização do cliente...")
        client = openai.OpenAI(api_key=api_key)
        print("✅ Cliente OpenAI inicializado com sucesso")
        
        print("🔧 Testando chamada simples...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Diga apenas 'OK' se você está funcionando."}],
            max_tokens=10,
            temperature=0
        )
        result = response.choices[0].message.content
        print(f"✅ Resposta recebida: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste OpenAI: {e}")
        return False

def test_lazy_client():
    """Teste do sistema lazy loading"""
    try:
        print("\n🔧 Testando LazyAPIClient...")
        from utils.lazy_imports import create_lazy_api_client
        
        client = create_lazy_api_client('openai', 'teste')
        print("✅ LazyAPIClient criado")
        
        # Testar método get_client
        real_client = client.get_client()
        if real_client:
            print("✅ Cliente real obtido via get_client()")
        else:
            print("❌ Falha ao obter cliente real")
            return False
            
        # Testar atributo chat
        if hasattr(client, 'chat'):
            print("✅ Atributo 'chat' acessível via proxy")
        else:
            print("❌ Atributo 'chat' não acessível")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste LazyAPIClient: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes OpenAI...\n")
    
    basic_ok = test_openai_basic()
    lazy_ok = test_lazy_client()
    
    print(f"\n📊 RESULTADO:")
    print(f"   - Teste Básico: {'✅' if basic_ok else '❌'}")
    print(f"   - Teste LazyClient: {'✅' if lazy_ok else '❌'}")
    
    if basic_ok and lazy_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("💥 ALGUNS TESTES FALHARAM!")
        sys.exit(1)