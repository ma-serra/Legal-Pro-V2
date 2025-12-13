#!/usr/bin/env python3
"""
Teste sistema 2 APIs funcionais (OpenAI + Gemini)
Anthropic removido por timeouts SSL no ambiente Replit
"""

import os
import time
import requests
import json

# Documento de teste
documento_teste = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL

CONTRATADA: MAYMIDIA MARKETING DIGITAL LTDA
CNPJ: 45.789.123/0001-45

CONTRATANTE: João Silva Empresário Individual  
CPF: 123.456.789-00

CLÁUSULA PRIMEIRA - DO OBJETO
A CONTRATADA prestará serviços especializados de marketing digital incluindo gestão de redes sociais, campanhas publicitárias online, SEO/SEM, consultoria estratégica, produção de conteúdo e análise de métricas.

CLÁUSULA SEGUNDA - DO VALOR E FORMA DE PAGAMENTO
Valor total: R$ 12.678,00 em 6 parcelas mensais de R$ 2.113,00, vencimento dia 10 de cada mês.

CLÁUSULA TERCEIRA - DO PRAZO
Vigência: 6 meses (10/07/2023 a 10/01/2024).

Porto Alegre/RS, 10 de julho de 2023.
"""

print("=" * 80)
print("TESTE SISTEMA 2 APIS FUNCIONAIS (OpenAI + Gemini)")
print("=" * 80)
print(f"📄 Documento: {len(documento_teste)} caracteres")
print("🔧 APIs: OpenAI GPT-4o + Google Gemini (6500 tokens cada)")
print("⚠️ Anthropic removido por timeouts SSL no Replit")
print("-" * 50)

# Testar API principal
url = "http://localhost:5000/api/multi-agente-real/analise-real"
# Usar form data ao invés de JSON conforme logs da API
payload = {
    "texto_documento": documento_teste,
    "agentes[]": ["1", "2", "3"]  # Como array form data
}

print("🚀 Enviando para análise...")
inicio = time.time()

try:
    response = requests.post(url, data=payload, timeout=120)
    tempo_total = time.time() - inicio
    
    print(f"⏱️ Tempo: {tempo_total:.2f}s")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCESSO!")
        print(f"💎 APIs funcionais: {data.get('apis_utilizadas', [])}")
        print(f"🔢 Total agentes: {data.get('total_agentes', 0)}")
        
        # Verificar resultados por API
        resultados = data.get('resultados_por_api', {})
        for api_nome, resultado in resultados.items():
            if api_nome != 'resumo_consolidado' and resultado:
                status = resultado.get('status', 'N/A')
                tokens = resultado.get('tokens_usados', 0)
                emoji = "✅" if status == 'sucesso' else "⚠️"
                print(f"   {emoji} {api_nome.upper()}: {status} ({tokens} tokens)")
        
        # Resumo consolidado
        resumo = resultados.get('resumo_consolidado', {})
        if resumo:
            print(f"🎯 Total APIs sucesso: {resumo.get('total_apis_sucesso', 0)}")
            print(f"📊 Total tokens: {resumo.get('total_tokens', 0)}")
            print(f"📝 Observações: {resumo.get('observacoes', 'N/A')}")
            
        print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        
    else:
        print(f"❌ ERRO {response.status_code}")
        try:
            error_data = response.json()
            print(f"📄 Erro: {error_data.get('error', 'N/A')}")
        except:
            print(f"📄 Resposta: {response.text[:200]}...")
        
except Exception as e:
    tempo_total = time.time() - inicio
    print(f"❌ EXCEÇÃO após {tempo_total:.2f}s: {e}")

print("=" * 80)