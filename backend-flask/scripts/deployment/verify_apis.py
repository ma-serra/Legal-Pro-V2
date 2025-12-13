#!/usr/bin/env python3
"""
Script de verificação de APIs para ambiente de produção
Testa conectividade e funcionalidade de todas as APIs integradas
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def test_openai():
    """Testa API OpenAI"""
    try:
        from openai import OpenAI
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {"status": "❌", "error": "API key não encontrada"}
        
        if not api_key.startswith('sk-'):
            return {"status": "❌", "error": "Formato de API key inválido"}
        
        client = OpenAI(api_key=api_key)
        
        # Teste simples de completions
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Teste de conectividade. Responda apenas 'OK'."}],
            max_tokens=5,
            timeout=10
        )
        
        if response.choices[0].message.content:
            return {
                "status": "✅", 
                "model": "gpt-4o",
                "response_time": "< 10s",
                "test": "Completions funcionando"
            }
        else:
            return {"status": "❌", "error": "Resposta vazia"}
            
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def test_anthropic():
    """Testa API Anthropic"""
    try:
        import anthropic
        
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return {"status": "❌", "error": "API key não encontrada"}
        
        if not api_key.startswith('sk-ant-'):
            return {"status": "❌", "error": "Formato de API key inválido"}
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Teste simples de messages
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=5,
            messages=[{"role": "user", "content": "Teste. Responda apenas 'OK'."}],
            timeout=10
        )
        
        if message.content[0].text:
            return {
                "status": "✅",
                "model": "claude-3-5-sonnet",
                "response_time": "< 10s", 
                "test": "Messages funcionando"
            }
        else:
            return {"status": "❌", "error": "Resposta vazia"}
            
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def test_google():
    """Testa API Google"""
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return {"status": "❌", "error": "API key não encontrada"}
        
        genai.configure(api_key=api_key)
        
        # Teste simples de generate_content
        model = genai.GenerativeModel('gemini-1.5-pro-002')
        response = model.generate_content("Teste. Responda apenas 'OK'.")
        
        if response.text:
            return {
                "status": "✅",
                "model": "gemini-1.5-pro",
                "response_time": "< 10s",
                "test": "Generate content funcionando"
            }
        else:
            return {"status": "❌", "error": "Resposta vazia"}
            
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def test_assemblyai():
    """Testa API AssemblyAI"""
    try:
        api_key = os.environ.get('ASSEMBLYAI_API_KEY')
        if not api_key:
            return {"status": "❌", "error": "API key não encontrada"}
        
        # Teste de conectividade via HTTP
        headers = {"authorization": api_key}
        response = requests.get(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "status": "✅",
                "service": "AssemblyAI Transcription",
                "response_time": f"{response.elapsed.total_seconds():.1f}s",
                "test": "API conectada"
            }
        else:
            return {"status": "❌", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def test_database():
    """Testa conexão com PostgreSQL"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            return {"status": "❌", "error": "DATABASE_URL não encontrada"}
        
        # Teste usando psycopg2
        import psycopg2
        from urllib.parse import urlparse
        
        result = urlparse(db_url)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            user=result.username,
            password=result.password,
            database=result.path[1:],
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "✅",
            "service": "PostgreSQL",
            "version": "PostgreSQL 16" if "16" in version else "PostgreSQL",
            "test": "Conexão estabelecida"
        }
        
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def test_qdrant():
    """Testa conexão com Qdrant (opcional)"""
    try:
        qdrant_url = os.environ.get('QDRANT_URL')
        qdrant_key = os.environ.get('QDRANT_API_KEY')
        
        if not qdrant_url or not qdrant_key:
            return {"status": "⚠️", "warning": "Qdrant não configurado (opcional)"}
        
        from qdrant_client import QdrantClient
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=10)
        collections = client.get_collections()
        
        return {
            "status": "✅",
            "service": "Qdrant Vector DB",
            "collections": len(collections.collections),
            "test": "Cliente conectado"
        }
        
    except Exception as e:
        return {"status": "❌", "error": f"Erro: {str(e)[:50]}..."}

def main():
    print("=" * 80)
    print("🔍 VERIFICAÇÃO DE APIs - AMBIENTE DE PRODUÇÃO")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de testes
    tests = {
        "OpenAI GPT-4o": test_openai,
        "Anthropic Claude": test_anthropic,
        "Google Gemini": test_google,
        "AssemblyAI": test_assemblyai,
        "PostgreSQL": test_database,
        "Qdrant Vector DB": test_qdrant
    }
    
    results = {}
    passed = 0
    total = len(tests)
    
    print("Executando testes de conectividade...")
    print("-" * 80)
    
    for name, test_func in tests.items():
        print(f"Testando {name}...", end=" ", flush=True)
        
        start_time = time.time()
        result = test_func()
        end_time = time.time()
        
        results[name] = result
        result["duration"] = f"{(end_time - start_time):.1f}s"
        
        status = result["status"]
        print(f"{status}")
        
        # Mostrar detalhes
        if status == "✅":
            passed += 1
            if "model" in result:
                print(f"  └─ Modelo: {result['model']}")
            if "service" in result:
                print(f"  └─ Serviço: {result['service']}")
            if "test" in result:
                print(f"  └─ Teste: {result['test']}")
        elif status == "⚠️":
            if "warning" in result:
                print(f"  └─ {result['warning']}")
        else:  # ❌
            if "error" in result:
                print(f"  └─ {result['error']}")
        
        print()
    
    # Resumo final
    print("=" * 80)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 80)
    
    # APIs críticas (obrigatórias)
    critical_apis = ["OpenAI GPT-4o", "AssemblyAI", "PostgreSQL"]
    critical_passed = sum(1 for api in critical_apis if results[api]["status"] == "✅")
    
    print(f"APIs Críticas: {critical_passed}/{len(critical_apis)} ✅")
    print(f"APIs Opcionais: {passed - critical_passed}/{total - len(critical_apis)} ✅")
    print(f"Total Geral: {passed}/{total}")
    print()
    
    # Status final
    if critical_passed == len(critical_apis):
        print("🎉 STATUS: PRONTO PARA PRODUÇÃO!")
        print("✅ Todas as APIs críticas estão funcionando")
        
        if passed == total:
            print("✅ Todas as APIs opcionais também estão ativas")
        else:
            print("⚠️  Algumas APIs opcionais não estão configuradas")
            
        print("\n🚀 A aplicação pode ser deployada com segurança!")
        return 0
    else:
        print("🚨 STATUS: CONFIGURAÇÃO INCOMPLETA")
        print("❌ APIs críticas não estão funcionando")
        
        missing = [api for api in critical_apis if results[api]["status"] != "✅"]
        print(f"📋 APIs que precisam ser configuradas: {', '.join(missing)}")
        
        print("\n⚠️  Configure as APIs em falta antes do deploy!")
        return 1

if __name__ == "__main__":
    sys.exit(main())