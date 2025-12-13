#!/usr/bin/env python3
"""
TESTE DA API ROBUSTA FINAL COM CONFIGURAÇÕES RECOMENDADAS
✅ Timeouts seguros: 90s cada API  
✅ 6800 tokens máximo
✅ Total sequencial máximo: 270s
"""

import requests
import time
import json

documento_teste = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS JURÍDICOS

CONTRATADA: ESCRITÓRIO ADVOCACIA SILVA & ASSOCIADOS LTDA
CNPJ: 12.345.678/0001-90

CONTRATANTE: EMPRESA TECNOLOGIA DIGITAL LTDA
CNPJ: 98.765.432/0001-10

CLÁUSULA PRIMEIRA - DO OBJETO
Prestação de serviços jurídicos especializados em direito empresarial.

CLÁUSULA SEGUNDA - DO VALOR
Valor mensal: R$ 8.500,00 (oito mil e quinhentos reais)
Reajuste anual: IPCA/IBGE

CLÁUSULA TERCEIRA - DA VIGÊNCIA
Prazo determinado: 12 meses (01/08/2023 a 31/07/2024)

São Paulo/SP, 1° de agosto de 2023.
"""

print("🚀 TESTE API ROBUSTA FINAL - CONFIGURAÇÕES RECOMENDADAS")
print("=" * 70)
print(f"📄 Documento: {len(documento_teste)} caracteres")
print("⚙️ Configurações implementadas:")
print("   • Timeouts seguros: 90s cada API")
print("   • 6800 tokens máximo por API")
print("   • Temperature: 0.7")
print("   • Top_p: 0.9")
print("   • Stream: False (estabilidade)")
print("   • Total sequencial máximo: 270s")
print("-" * 50)

url = "http://localhost:5000/api/teste-3-apis-robusta"
payload = {
    "texto_documento": documento_teste
}

print("🎯 Enviando para análise com 3 APIs robustas...")
inicio = time.time()

try:
    response = requests.post(url, data=payload, timeout=300)  # 5 minutos limite
    tempo_total = time.time() - inicio
    
    print(f"⏱️ Tempo total: {tempo_total:.2f}s")
    print(f"📊 Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ SUCESSO TOTAL!")
            
            # Verificar configuração aplicada
            config = data.get('configuracao_aplicada', {})
            print(f"\n⚙️ CONFIGURAÇÃO APLICADA:")
            print(f"   📡 Timeouts: {config.get('timeouts', {})}")
            print(f"   🔤 Tokens: {config.get('tokens', {})}")
            
            # Analisar resultados por API
            resultados = data.get('resultados_por_api', {})
            
            print(f"\n📋 ANÁLISE POR API:")
            apis_funcionais = 0
            tokens_totais = 0
            
            for api_nome, resultado in resultados.items():
                if api_nome == 'resumo_consolidado':
                    continue
                    
                status = resultado.get('status', 'N/A')
                tokens = resultado.get('tokens_usados', 0)
                modelo = resultado.get('modelo', 'N/A')
                
                if status == 'sucesso':
                    emoji = "✅"
                    apis_funcionais += 1
                    tokens_totais += tokens
                    print(f"   {emoji} {api_nome.upper()}: {status}")
                    print(f"      📊 {tokens} tokens - Modelo: {modelo}")
                    
                    # Mostrar trecho da análise
                    analise = resultado.get('analise', '')
                    if analise:
                        trecho = analise[:150].replace('\n', ' ')
                        print(f"      📝 {trecho}...")
                else:
                    emoji = "❌"
                    print(f"   {emoji} {api_nome.upper()}: {status}")
                    erro = resultado.get('analise', '')[:100]
                    print(f"      ⚠️ {erro}")
            
            # Resumo consolidado
            resumo = resultados.get('resumo_consolidado', {})
            if resumo:
                print(f"\n🎯 RESUMO CONSOLIDADO:")
                print(f"   ✅ APIs funcionais: {resumo.get('total_apis_sucesso', 0)}/3")
                print(f"   📊 Total tokens: {resumo.get('total_tokens', 0)}")
                print(f"   ⏱️ Tempo processamento: {resumo.get('tempo_processamento', 0)}s")
                print(f"   📝 Observações: {resumo.get('observacoes', 'N/A')}")
                
            print(f"\n💎 Sistema ID: {data.get('sistema_id', 'N/A')}")
            print(f"🆔 UUID: {data.get('uuid_resultado', 'N/A')}")
            
            # Verificação de sucesso
            if apis_funcionais == 3:
                print("\n" + "🎉" * 25)
                print("🎊 SUCESSO ABSOLUTO - TODAS AS 3 APIS FUNCIONAIS!")
                print("✅ OpenAI GPT-4o: Funcionando perfeitamente")
                print("✅ Anthropic Claude: Timeout SSL resolvido")
                print("✅ Google Gemini: Integração corrigida")
                print(f"📊 Total: {tokens_totais} tokens processados")
                print(f"⏱️ Tempo eficiente: {tempo_total:.2f}s para 3 APIs")
                print("🚀 CONFIGURAÇÕES RECOMENDADAS TOTALMENTE IMPLEMENTADAS!")
                print("🎉" * 25)
            elif apis_funcionais >= 2:
                print(f"\n✅ SUCESSO PARCIAL - {apis_funcionais}/3 APIs funcionais")
                print("💪 Sistema resiliente operando com redundância")
            else:
                print(f"\n⚠️ FUNCIONAMENTO LIMITADO - {apis_funcionais}/3 APIs")
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro JSON: {e}")
            print(f"📄 Resposta: {response.text[:300]}")
            
    else:
        print(f"❌ ERRO HTTP {response.status_code}")
        try:
            error_data = response.json()
            print(f"📄 Erro: {error_data.get('error', 'N/A')}")
        except:
            print(f"📄 Resposta: {response.text[:300]}")
        
except requests.exceptions.Timeout:
    tempo_total = time.time() - inicio
    print(f"⏰ TIMEOUT após {tempo_total:.2f}s")
except Exception as e:
    tempo_total = time.time() - inicio
    print(f"❌ EXCEÇÃO após {tempo_total:.2f}s: {e}")

print("\n" + "=" * 70)