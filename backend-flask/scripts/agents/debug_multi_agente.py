#!/usr/bin/env python3
"""
Script de debug completo para o sistema multi-agente.
Testa todas as funcionalidades da rota /validacao-multi-agente-expandida
"""

import requests
import json
import time
import sys

# Configurações
BASE_URL = "http://localhost:5000"
DOCUMENTO_TESTE = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: Empresa XYZ LTDA
CONTRATADA: MAYMIDIA SERVIÇOS E MARKETING

DO OBJETO:
É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL por parte da CONTRATADA para promover os serviços da CONTRATANTE.

DAS OBRIGAÇÕES DA CONTRATADA:
- Realizar reuniões presenciais ou virtuais previamente agendadas
- Executar os serviços contratados com observância das normas legais aplicáveis
- Adquirir e configurar o provedor de hospedagem contratado
- Criação do Site e página de blog entregue ajustados para SEO

DAS OBRIGAÇÕES DA CONTRATANTE:
- Realizar reuniões presenciais ou virtuais previamente agendadas
- Cumprir com as atribuições que lhe forem destinadas pela CONTRATADA
- Fornecer o material necessário para o adequado desenvolvimento dos serviços
- Efetuar os pagamentos devidos à CONTRATADA nos prazos estabelecidos

DO PREÇO:
Pela prestação de serviços objeto deste contrato, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais).

DO PRAZO E RESCISÃO:
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados.

DO FORO:
Fica eleito o FORO da Porto Alegre, estado do Rio Grande do Sul.
"""

def debug_info(message):
    """Imprime informações de debug com timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] DEBUG: {message}")

def test_api_connectivity():
    """Testa conectividade básica com a API"""
    debug_info("Testando conectividade com a API...")
    
    try:
        response = requests.get(f"{BASE_URL}/validacao-multi-agente-expandida", timeout=10)
        debug_info(f"Status da página principal: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        debug_info(f"Erro de conectividade: {e}")
        return False

def test_agente_selection():
    """Testa seleção automática de agentes"""
    debug_info("Testando seleção automática de agentes...")
    
    try:
        # Simular detecção de tipo de documento
        payload = {
            'texto_documento': DOCUMENTO_TESTE[:500]  # Primeiro parágrafo
        }
        
        response = requests.post(
            f"{BASE_URL}/api/detectar-agentes-automatico",
            data=payload,
            timeout=30
        )
        
        debug_info(f"Status detecção agentes: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            debug_info(f"Agentes detectados: {len(data.get('agentes_selecionados', []))}")
            debug_info(f"Tipo documento: {data.get('tipo_documento', 'N/A')}")
            return data.get('agentes_selecionados', [])
        else:
            debug_info(f"Erro na detecção: {response.text}")
            return []
            
    except Exception as e:
        debug_info(f"Erro na seleção de agentes: {e}")
        return []

def test_multi_api_analysis(agentes_selecionados):
    """Testa análise completa com as 3 APIs"""
    debug_info("Iniciando teste de análise multi-API...")
    
    if not agentes_selecionados:
        debug_info("Usando agentes padrão para teste...")
        agentes_selecionados = ['1', '2', '3']  # IDs padrão
    
    payload = {
        'texto_documento': DOCUMENTO_TESTE,
        'agentes_selecionados': agentes_selecionados
    }
    
    debug_info(f"Enviando documento ({len(DOCUMENTO_TESTE)} chars) para {len(agentes_selecionados)} agentes")
    
    try:
        inicio = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/multi-agente-real/analise-real",
            data=payload,
            timeout=300  # 5 minutos
        )
        
        tempo_total = time.time() - inicio
        debug_info(f"Tempo total de análise: {tempo_total:.2f}s")
        debug_info(f"Status da análise: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                debug_info("✅ Análise concluída com sucesso!")
                debug_info(f"ID da análise: {data.get('id', 'N/A')}")
                debug_info(f"APIs utilizadas: {data.get('apis_utilizadas', [])}")
                debug_info(f"Total de agentes: {data.get('total_agentes', 0)}")
                
                # Verificar resultados por API
                resultados = data.get('resultados_por_api', {})
                for api_name in ['openai', 'anthropic', 'gemini']:
                    if api_name in resultados:
                        resultado = resultados[api_name]
                        status = resultado.get('status', 'N/A')
                        tokens = resultado.get('tokens_usados', 0)
                        debug_info(f"  {api_name.upper()}: {status} - {tokens} tokens")
                        
                        if status == 'sucesso':
                            analise_preview = resultado.get('analise', '')[:200]
                            debug_info(f"    Preview: {analise_preview}...")
                
                return data
                
            except json.JSONDecodeError as e:
                debug_info(f"Erro ao decodificar JSON: {e}")
                debug_info(f"Resposta bruta: {response.text[:500]}")
                return None
                
        else:
            debug_info(f"❌ Erro na análise: {response.status_code}")
            debug_info(f"Resposta: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        debug_info("❌ Timeout na análise - operação demorou mais que 5 minutos")
        return None
    except Exception as e:
        debug_info(f"❌ Erro na análise: {e}")
        return None

def test_individual_apis():
    """Testa cada API individualmente"""
    debug_info("Testando APIs individualmente...")
    
    test_text = "Contrato de prestação de serviços entre duas empresas."
    
    # Teste OpenAI
    debug_info("Testando OpenAI...")
    try:
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Analise brevemente: {test_text}"}],
            max_tokens=100
        )
        debug_info("✅ OpenAI funcionando")
    except Exception as e:
        debug_info(f"❌ OpenAI erro: {e}")
    
    # Teste Anthropic
    debug_info("Testando Anthropic...")
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": f"Analise brevemente: {test_text}"}]
        )
        debug_info("✅ Anthropic funcionando")
    except Exception as e:
        debug_info(f"❌ Anthropic erro: {e}")
    
    # Teste Gemini
    debug_info("Testando Gemini...")
    try:
        from google import genai
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Analise brevemente: {test_text}"
        )
        debug_info("✅ Gemini funcionando")
    except Exception as e:
        debug_info(f"❌ Gemini erro: {e}")

def main():
    """Executa todos os testes de debug"""
    print("=" * 60)
    print("DEBUG COMPLETO - SISTEMA MULTI-AGENTE")
    print("=" * 60)
    
    # 1. Teste de conectividade
    if not test_api_connectivity():
        debug_info("❌ Falha na conectividade básica")
        return
    
    # 2. Teste de seleção de agentes
    agentes = test_agente_selection()
    
    # 3. Teste das APIs individuais
    test_individual_apis()
    
    # 4. Teste completo da análise multi-API
    resultado = test_multi_api_analysis(agentes)
    
    print("=" * 60)
    if resultado:
        debug_info("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
        debug_info(f"Resultado disponível com ID: {resultado.get('id', 'N/A')}")
    else:
        debug_info("❌ FALHAS DETECTADAS NO SISTEMA")
    print("=" * 60)

if __name__ == "__main__":
    main()