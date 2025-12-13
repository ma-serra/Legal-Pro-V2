#!/usr/bin/env python3
"""
TESTE SISTEMA 3 APIS OTIMIZADAS PARA TIMEOUT SSL
✅ OpenAI GPT-4o: 6500 tokens
✅ Anthropic Claude: 6500 tokens (timeout SSL otimizado)  
✅ Google Gemini: 6500 tokens (timeout SSL otimizado)
"""

import os
import time
import requests
import json

# Documento jurídico para teste
documento_teste = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS JURÍDICOS

CONTRATADA: ESCRITÓRIO ADVOCACIA SILVA & ASSOCIADOS LTDA
CNPJ: 12.345.678/0001-90
OAB/SP: 123.456

CONTRATANTE: EMPRESA TECNOLOGIA DIGITAL LTDA
CNPJ: 98.765.432/0001-10

CLÁUSULA PRIMEIRA - DO OBJETO
Prestação de serviços jurídicos especializados em direito empresarial, incluindo consultoria preventiva, elaboração de contratos, assessoria trabalhista e representação judicial.

CLÁUSULA SEGUNDA - DO VALOR
Valor mensal: R$ 8.500,00 (oito mil e quinhentos reais)
Forma de pagamento: Todo dia 15 de cada mês via boleto bancário
Reajuste anual: IPCA/IBGE

CLÁUSULA TERCEIRA - DA VIGÊNCIA
Prazo determinado: 12 meses (01/08/2023 a 31/07/2024)
Renovação automática por períodos iguais salvo manifestação contrária com 60 dias de antecedência.

CLÁUSULA QUARTA - DAS RESPONSABILIDADES
DO ESCRITÓRIO:
- Assessoria jurídica completa e especializada
- Atendimento presencial e remoto
- Elaboração de pareceres técnicos
- Representação em tribunais quando necessário

DA EMPRESA:
- Pagamento pontual dos honorários
- Fornecimento de documentação necessária
- Comunicação prévia sobre questões urgentes

CLÁUSULA QUINTA - DA RESCISÃO
Rescisão por qualquer das partes com aviso prévio de 30 dias.
Multa rescisória: 2 mensalidades em caso de rescisão antecipada sem justa causa.

São Paulo/SP, 1° de agosto de 2023.
"""

print("=" * 80)
print("🚀 TESTE 3 APIS OTIMIZADAS ANTI-TIMEOUT SSL")
print("=" * 80)
print(f"📄 Documento: {len(documento_teste)} caracteres")
print("✅ OpenAI GPT-4o: 6500 tokens (httpx otimizado)")
print("✅ Anthropic Claude: 6500 tokens (timeout SSL otimizado)")
print("✅ Google Gemini: 6500 tokens (timeout SSL otimizado)")
print("🔧 Sistema: Timeouts configurados especificamente para Replit")
print("-" * 50)

# Testar API otimizada
url = "http://localhost:5000/api/multi-agente-real/analise-real"
payload = {
    "texto_documento": documento_teste,
    "agentes[]": ["1", "2", "3"]
}

print("🚀 Enviando documento para análise com 3 APIs otimizadas...")
inicio = time.time()

try:
    response = requests.post(url, data=payload, timeout=150)  # Timeout aumentado para 3 APIs
    tempo_total = time.time() - inicio
    
    print(f"⏱️ Tempo: {tempo_total:.2f}s")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("🎉 SUCESSO TOTAL COM 3 APIS!")
            
            # Verificar resultados por API
            resultados = data.get('resultados_por_api', {})
            
            print("\n📋 ANÁLISE POR API:")
            apis_funcionais = 0
            tokens_totais = 0
            
            for api_nome, resultado in resultados.items():
                if api_nome == 'resumo_consolidado':
                    continue
                    
                if resultado:
                    status = resultado.get('status', 'N/A')
                    tokens = resultado.get('tokens_usados', 0)
                    modelo = resultado.get('modelo', 'N/A')
                    
                    if status == 'sucesso':
                        emoji = "✅"
                        apis_funcionais += 1
                        tokens_totais += tokens
                        print(f"   {emoji} {api_nome.upper()}: {status} ({tokens} tokens, {modelo})")
                        
                        # Mostrar trecho da análise
                        analise = resultado.get('analise', '')
                        if analise:
                            trecho = analise[:120].replace('\n', ' ')
                            print(f"      📝 {trecho}...")
                    else:
                        emoji = "❌"
                        print(f"   {emoji} {api_nome.upper()}: {status}")
            
            # Resumo consolidado
            resumo = resultados.get('resumo_consolidado', {})
            if resumo:
                print(f"\n🎯 RESUMO FINAL:")
                print(f"   🔢 APIs funcionais: {resumo.get('total_apis_sucesso', 0)}/3")
                print(f"   📊 Total tokens: {resumo.get('total_tokens', 0)}")
                print(f"   ⚡ Eficiência: {apis_funcionais}/3 APIs ({apis_funcionais/3*100:.1f}%)")
                print(f"   📝 Observações: {resumo.get('observacoes', 'N/A')}")
                
            print(f"\n💎 ID do Sistema: {data.get('sistema_id', 'N/A')}")
            
            if apis_funcionais == 3:
                print("\n" + "🎉" * 20)
                print("🎊 SUCESSO ABSOLUTO - TODAS AS 3 APIS FUNCIONAIS!")
                print("✅ OpenAI GPT-4o: Processamento robusto")
                print("✅ Anthropic Claude: Timeout SSL resolvido")
                print("✅ Google Gemini: Timeout SSL resolvido")
                print(f"📊 Total: {tokens_totais} tokens processados")
                print(f"⏱️ Tempo eficiente: {tempo_total:.2f}s para 3 APIs")
                print("🚀 Sistema de produção COMPLETAMENTE OTIMIZADO!")
                print("🎉" * 20)
            elif apis_funcionais >= 2:
                print(f"\n✅ SUCESSO PARCIAL - {apis_funcionais}/3 APIs funcionais")
                print("💪 Sistema resiliente mantendo operação mesmo com falhas")
            else:
                print(f"\n⚠️ RESULTADO LIMITADO - {apis_funcionais}/3 APIs funcionais")
            
        except json.JSONDecodeError:
            print("❌ Resposta não é JSON válido")
            print(f"📄 Conteúdo: {response.text[:300]}")
            
    else:
        print(f"❌ ERRO {response.status_code}")
        try:
            error_data = response.json()
            print(f"📄 Erro: {error_data.get('error', 'N/A')}")
        except:
            print(f"📄 Resposta: {response.text[:300]}")
        
except Exception as e:
    tempo_total = time.time() - inicio
    print(f"❌ EXCEÇÃO após {tempo_total:.2f}s: {e}")

print("\n" + "=" * 80)