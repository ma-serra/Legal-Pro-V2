#!/usr/bin/env python3
"""
TESTE DA API MULTI-AGENTE FUNCIONAL (OpenAI + Anthropic)
"""

import requests
import time

documento = "CONTRATO DE ARRENDAMENTO RURAL - Analise jurídica completa necessária para identificar possíveis falhas, cláusulas inadequadas e sugestões de melhorias. O contrato envolve propriedade rural de 500 hectares para plantio de soja, com prazo de 5 anos e valor de R$ 150.000,00 anuais."

print("🎯 TESTE API MULTI-AGENTE FUNCIONAL")
print("=" * 60)
print("📋 Usando apenas OpenAI + Anthropic (APIs comprovadamente funcionais)")
print("=" * 60)

url = "http://localhost:5000/api/multi-agente-funcional"
payload = {'texto_documento': documento}

inicio = time.time()

try:
    print("🚀 Iniciando análise multi-agente...")
    response = requests.post(url, data=payload, timeout=300)
    tempo = time.time() - inicio
    
    print(f"⏱️ Tempo total: {tempo:.1f}s")
    print(f"📊 Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('status') == 'sucesso':
                print("✅ ANÁLISE MULTI-AGENTE CONCLUÍDA COM SUCESSO!")
                print("-" * 50)
                
                # Mostrar resumo
                resumo = data.get('resumo_consolidado', {})
                print(f"📊 APIs processadas: {resumo.get('apis_sucesso', 0)}/{resumo.get('total_apis_processadas', 0)}")
                print(f"🔢 Total tokens: {resumo.get('total_tokens', 0)}")
                print(f"⏱️ Tempo total: {resumo.get('tempo_total', 0)}s")
                print(f"✅ APIs funcionais: {', '.join(resumo.get('apis_funcionais', []))}")
                
                # Mostrar resultados por API
                resultados = data.get('resultados_por_api', {})
                for api, resultado in resultados.items():
                    if resultado.get('status') == 'sucesso':
                        tokens = resultado.get('tokens_usados', 0)
                        tempo_api = resultado.get('tempo_processamento', 0)
                        modelo = resultado.get('modelo', 'N/A')
                        print(f"\n✅ {api.upper()}: {tokens} tokens em {tempo_api}s ({modelo})")
                        print(f"   📝 Análise: {len(resultado.get('analise', ''))} caracteres")
                    else:
                        print(f"\n❌ {api.upper()}: {resultado.get('status', 'erro')}")
                
                print("\n" + "=" * 60)
                print("💡 Sistema multi-agente funcional usando 2 APIs comprovadas!")
                
            else:
                print(f"⚠️ Erro na resposta: {data.get('status', 'desconhecido')}")
        except Exception as e:
            print(f"❌ Erro JSON: {e}")
    else:
        print(f"❌ HTTP {response.status_code}")
        if response.status_code == 500:
            print("💡 Erro interno - verificar logs do servidor")
            
except requests.exceptions.Timeout:
    tempo = time.time() - inicio
    print(f"⏰ TIMEOUT após {tempo:.1f}s")
except Exception as e:
    tempo = time.time() - inicio
    print(f"❌ ERRO após {tempo:.1f}s: {str(e)[:100]}")

print("=" * 60)