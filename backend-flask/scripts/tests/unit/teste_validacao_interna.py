#!/usr/bin/env python3
"""
Teste de validação interna completa do sistema multi-agente com prompts especializados
"""

import requests
import json
import time

def teste_validacao_completa():
    """Testa o sistema completo usando diferentes endpoints"""
    
    # Documento real para teste
    documento_teste = """
    CONTRATO DE ARRENDAMENTO RURAL

    ARRENDANTES: João Silva e Maria Silva, brasileiros, casados
    ARRENDATÁRIO: Pedro Santos, brasileiro, solteiro

    Cláusula Primeira - Do Objeto
    Os ARRENDANTES arrendam ao ARRENDATÁRIO área de 100 hectares
    para cultivo de soja, conforme Lei n° 4.504/1964 (Estatuto da Terra).

    Cláusula Segunda - Do Prazo  
    Prazo de 3 anos, início em 01/03/2025, término em 28/02/2028.

    Cláusula Terceira - Do Preço
    Pagamento de 11 sacos de soja de 60kg por hectare/ano.

    Cláusula Quarta - Das Obrigações
    Arrendatário deve conservar o solo e cumprir normas ambientais.
    """
    
    print("🧪 TESTE DE VALIDAÇÃO INTERNA COMPLETA")
    print("=" * 50)
    print(f"📄 Documento: {len(documento_teste)} caracteres")
    
    # Teste 1: API analise-unica-api
    print("\n🔍 TESTE 1: API analise-unica-api")
    print("-" * 30)
    
    url1 = "http://localhost:5000/api/analise-unica-api"
    dados1 = {
        "texto_documento": documento_teste,
        "api": "openai"
    }
    
    try:
        inicio = time.time()
        response = requests.post(url1, data=dados1, timeout=120)
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.1f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Resposta JSON válida")
                print(f"🔍 Chaves: {list(data.keys())}")
                
                if 'resultado' in data:
                    resultado = data['resultado']
                    if 'analise' in resultado:
                        analise = resultado['analise']
                        print(f"📝 Análise: {len(analise)} caracteres")
                        
                        # Verificar se contém seções especializadas
                        secoes_especializadas = [
                            "ANÁLISE ESPECIALIZADA",
                            "ESTRUTURA DO DOCUMENTO",
                            "RISCOS JURÍDICOS",
                            "ALTERAÇÕES PROPOSTAS",
                            "RESUMO EXECUTIVO"
                        ]
                        
                        secoes_encontradas = []
                        for secao in secoes_especializadas:
                            if secao in analise:
                                secoes_encontradas.append(secao)
                        
                        print(f"✅ Seções especializadas: {len(secoes_encontradas)}/{len(secoes_especializadas)}")
                        
                        if len(secoes_encontradas) >= 3:
                            print("🎯 PROMPTS ESPECIALIZADOS FUNCIONANDO!")
                        else:
                            print("⚠️ Prompts especializados podem não estar ativos")
                            
                        # Mostrar preview
                        print("\n📝 PREVIEW DA ANÁLISE:")
                        print("-" * 20)
                        linhas = analise.split('\n')[:8]
                        for linha in linhas:
                            if linha.strip():
                                print(f"   {linha[:70]}...")
                    else:
                        print("❌ Campo 'analise' não encontrado")
                else:
                    print("❌ Campo 'resultado' não encontrado")
                    print(f"📋 Dados recebidos: {json.dumps(data, indent=2)[:500]}...")
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
                print(f"📋 Texto: {response.text[:300]}...")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"📋 Resposta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Interface web
    print("\n🔍 TESTE 2: Interface Web Multi-Agente")
    print("-" * 30)
    
    url2 = "http://localhost:5000/api/analise-unica-api"
    dados2 = {
        "conteudo": documento_teste,
        "nome_arquivo": "contrato_teste.txt"
    }
    
    try:
        inicio = time.time()
        response = requests.post(url2, json=dados2, timeout=120)
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.1f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Interface web respondeu")
                print(f"🔍 Chaves: {list(data.keys())}")
                
                if 'resultados' in data:
                    resultados = data['resultados']
                    print(f"📊 Total de resultados: {len(resultados)}")
                    
                    for i, resultado in enumerate(resultados, 1):
                        print(f"\nResultado {i}:")
                        print(f"   API: {resultado.get('api', 'N/A')}")
                        print(f"   Tamanho: {len(str(resultado.get('resultado', '')))} chars")
                else:
                    print("📋 Estrutura diferente, analisando...")
                    print(f"   {json.dumps(data, indent=2)[:300]}...")
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na interface web: {e}")
    
    print("\n🎯 VALIDAÇÃO CONCLUÍDA")
    print("=" * 50)

if __name__ == "__main__":
    teste_validacao_completa()