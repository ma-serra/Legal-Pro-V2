"""
Debug completo da API multi-agente
"""
import os
import sys
import traceback
import requests
from werkzeug.test import Client
from werkzeug.wrappers import Response

def test_api_directly():
    """Testa a API diretamente"""
    print("🔍 Testando API multi-agente diretamente...")
    
    try:
        # Importar função
        from api_analise_simplificada import executar_analise_com_apis_reais
        
        # Dados de teste
        texto_documento = "CONTRATO DE TESTE PARA DEBUG"
        agentes_ids = ['21', '19', '38']
        
        print(f"📊 Testando com documento: {len(texto_documento)} chars")
        print(f"📊 Agentes: {agentes_ids}")
        
        # Executar função diretamente
        resultados = executar_analise_com_apis_reais(texto_documento, agentes_ids)
        
        print(f"✅ Função executada com sucesso: {len(resultados)} resultados")
        for i, r in enumerate(resultados):
            print(f"   Agente {i+1}: {r.get('agente_nome')} - {r.get('modelo_usado')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na função: {str(e)}")
        traceback.print_exc()
        return False

def test_flask_endpoint():
    """Testa o endpoint Flask"""
    print("\n🔍 Testando endpoint Flask...")
    
    try:
        # Importar app
        from main import app
        
        with app.test_client() as client:
            # Dados do formulário
            data = {
                'texto_documento': 'CONTRATO DE TESTE PARA DEBUG FLASK',
                'agentes_selecionados': ['21', '19', '38']
            }
            
            print(f"📊 Enviando dados: {data}")
            
            # Fazer requisição
            response = client.post('/api/analise-multi-agente', data=data)
            
            print(f"📡 Status: {response.status_code}")
            print(f"📡 Content-Type: {response.content_type}")
            
            if response.status_code == 200:
                import json
                result = json.loads(response.data)
                print(f"✅ Resposta JSON: success={result.get('success')}, total_agentes={result.get('total_agentes')}")
                return True
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"❌ Resposta: {response.data.decode()[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste Flask: {str(e)}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Testa dependências"""
    print("\n🔍 Testando dependências...")
    
    dependencies = ['openai', 'anthropic', 'google.genai', 'flask']
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: OK")
        except ImportError as e:
            print(f"❌ {dep}: {e}")

def test_environment():
    """Testa variáveis de ambiente"""
    print("\n🔍 Testando variáveis de ambiente...")
    
    keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY']
    
    for key in keys:
        value = os.getenv(key)
        if value:
            print(f"✅ {key}: Configurada ({len(value)} chars)")
        else:
            print(f"❌ {key}: Não configurada")

def debug_api_calls():
    """Debug das chamadas de API"""
    print("\n🔍 Testando chamadas de API individuais...")
    
    try:
        # Testar OpenAI
        if os.getenv('OPENAI_API_KEY'):
            print("🔍 Testando OpenAI...")
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), timeout=5.0)
            
            try:
                response = client.chat.completions.create(
                    model='gpt-4o',
                    messages=[{"role": "user", "content": "Teste simples"}],
                    max_tokens=50
                )
                print("✅ OpenAI: Funcionando")
            except Exception as e:
                print(f"❌ OpenAI: {str(e)[:100]}")
        
        # Testar Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            print("🔍 Testando Anthropic...")
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'), timeout=5.0)
            
            try:
                response = client.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=50,
                    messages=[{"role": "user", "content": "Teste simples"}]
                )
                print("✅ Anthropic: Funcionando")
            except Exception as e:
                print(f"❌ Anthropic: {str(e)[:100]}")
        
        # Testar Google
        if os.getenv('GEMINI_API_KEY'):
            print("🔍 Testando Google Gemini...")
            from google import genai
            client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents="Teste simples"
                )
                print("✅ Google Gemini: Funcionando")
            except Exception as e:
                print(f"❌ Google Gemini: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Erro geral no teste de APIs: {str(e)}")

if __name__ == "__main__":
    print("🚀 INICIANDO DEBUG COMPLETO DA API MULTI-AGENTE\n")
    
    # Executar todos os testes
    test_dependencies()
    test_environment()
    debug_api_calls()
    
    # Testar função principal
    if test_api_directly():
        print("\n✅ Função principal OK, testando endpoint Flask...")
        test_flask_endpoint()
    else:
        print("\n❌ Função principal falhou, endpoint Flask também falhará")
    
    print("\n🏁 DEBUG COMPLETO FINALIZADO")