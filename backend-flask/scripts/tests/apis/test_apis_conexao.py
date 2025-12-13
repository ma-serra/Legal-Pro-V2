#!/usr/bin/env python3
"""
Script de teste para verificar conectividade com todas as APIs do Legal Design Pro V2
Execute antes de iniciar o desenvolvimento no Cursor
"""

import os
import sys
from typing import Dict, Any
import traceback

def test_openai_connection() -> Dict[str, Any]:
    """Testa conexão com OpenAI"""
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {"status": "FAIL", "error": "OPENAI_API_KEY não encontrada"}
        
        client = openai.OpenAI(api_key=api_key)
        
        # Teste simples
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Teste de conectividade"}],
            max_tokens=10
        )
        
        return {
            "status": "OK", 
            "model": "gpt-4o-mini",
            "tokens": response.usage.total_tokens if response.usage else 0
        }
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_anthropic_connection() -> Dict[str, Any]:
    """Testa conexão com Anthropic"""
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {"status": "FAIL", "error": "ANTHROPIC_API_KEY não encontrada"}
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Teste simples
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Teste"}]
        )
        
        return {
            "status": "OK", 
            "model": "claude-3-5-sonnet",
            "tokens": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_google_connection() -> Dict[str, Any]:
    """Testa conexão com Google Gemini"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return {"status": "FAIL", "error": "GOOGLE_API_KEY não encontrada"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Teste simples
        response = model.generate_content("Teste")
        
        return {
            "status": "OK", 
            "model": "gemini-2.0-flash",
            "response_length": len(response.text) if response.text else 0
        }
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_database_connection() -> Dict[str, Any]:
    """Testa conexão com PostgreSQL"""
    try:
        import psycopg2
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return {"status": "FAIL", "error": "DATABASE_URL não encontrada"}
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Teste básico
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Verificar extensão pgvector
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "OK",
            "version": version[:50] + "..." if len(version) > 50 else version,
            "pgvector": "OK" if vector_ext else "NOT_INSTALLED"
        }
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_qdrant_connection() -> Dict[str, Any]:
    """Testa conexão com Qdrant"""
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_key = os.getenv('QDRANT_API_KEY')
        
        if not qdrant_url or not qdrant_key:
            return {"status": "FAIL", "error": "QDRANT_URL ou QDRANT_API_KEY não encontradas"}
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        
        # Teste básico
        collections = client.get_collections()
        
        return {
            "status": "OK",
            "collections_count": len(collections.collections),
            "url": qdrant_url[:30] + "..." if len(qdrant_url) > 30 else qdrant_url
        }
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def test_assemblyai_connection() -> Dict[str, Any]:
    """Testa conexão com AssemblyAI"""
    try:
        import assemblyai as aai
        
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            return {"status": "FAIL", "error": "ASSEMBLYAI_API_KEY não encontrada"}
        
        aai.settings.api_key = api_key
        
        # Teste básico - verificar quota
        import requests
        response = requests.get(
            "https://api.assemblyai.com/v2/realtime/token",
            headers={"authorization": api_key}
        )
        
        if response.status_code == 200:
            return {"status": "OK", "api_key_valid": True}
        else:
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
        
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def load_environment():
    """Carrega variáveis de ambiente do .env se existir"""
    try:
        from python_dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv('.env')
            print("✅ Arquivo .env carregado")
        else:
            print("⚠️  Arquivo .env não encontrado - usando variáveis do sistema")
    except ImportError:
        print("⚠️  python-dotenv não instalado - usando variáveis do sistema")

def main():
    """Executa todos os testes de conectividade"""
    print("🔍 TESTE DE CONECTIVIDADE - Legal Design Pro V2")
    print("=" * 60)
    
    # Carregar environment
    load_environment()
    
    # Lista de testes
    tests = [
        ("OpenAI GPT-4o", test_openai_connection),
        ("Anthropic Claude", test_anthropic_connection),
        ("Google Gemini", test_google_connection),
        ("PostgreSQL", test_database_connection),
        ("Qdrant Cloud", test_qdrant_connection),
        ("AssemblyAI", test_assemblyai_connection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testando {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            
            if result["status"] == "OK":
                print(f"✅ {test_name}: CONECTADO")
                if "model" in result:
                    print(f"   Modelo: {result['model']}")
                if "tokens" in result:
                    print(f"   Tokens: {result['tokens']}")
                if "version" in result:
                    print(f"   Versão: {result['version']}")
                if "pgvector" in result:
                    print(f"   pgvector: {result['pgvector']}")
                if "collections_count" in result:
                    print(f"   Collections: {result['collections_count']}")
            else:
                print(f"❌ {test_name}: FALHOU")
                print(f"   Erro: {result['error']}")
                
        except Exception as e:
            print(f"❌ {test_name}: ERRO CRÍTICO")
            print(f"   Exceção: {str(e)}")
            results[test_name] = {"status": "ERROR", "error": str(e)}
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    success_count = sum(1 for r in results.values() if r["status"] == "OK")
    total_count = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if result["status"] == "OK" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
    
    print(f"\n📈 Resultado: {success_count}/{total_count} APIs conectadas")
    
    if success_count == total_count:
        print("🎉 SISTEMA PRONTO PARA DESENVOLVIMENTO!")
        return 0
    elif success_count >= 4:
        print("⚠️  Sistema parcialmente funcional - verifique APIs que falharam")
        return 1
    else:
        print("🚫 Muitas APIs falharam - verificar configuração")
        return 2

if __name__ == "__main__":
    sys.exit(main())