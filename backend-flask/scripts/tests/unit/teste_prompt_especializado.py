#!/usr/bin/env python3
"""
Teste do sistema multi-agente com novos prompts especializados
"""

import requests
import json
import time

def testar_analise_especializada():
    """Testa a análise com os novos prompts especializados"""
    
    # Documento de teste (contrato simples)
    documento_teste = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: Empresa ABC Ltda., CNPJ 12.345.678/0001-90
CONTRATADA: Tech Solutions ME, CNPJ 98.765.432/0001-10

OBJETO: Desenvolvimento de sistema web
VALOR: R$ 50.000,00
PRAZO: 60 dias

O pagamento será realizado em duas parcelas.
A CONTRATADA se responsabiliza pelo desenvolvimento.
Em caso de descumprimento, aplicam-se penalidades.
"""
    
    print("🧪 Testando análise multi-agente com prompts especializados...")
    print(f"📄 Documento: {len(documento_teste)} caracteres")
    
    # URL da API (assumindo que está rodando localmente)
    url = "http://localhost:5000/api/analise-unica-api"
    
    # Dados para a análise
    dados = {
        "conteudo": documento_teste,
        "nome_arquivo": "contrato_teste.txt"
    }
    
    try:
        print("⏳ Enviando documento para análise...")
        inicio = time.time()
        
        response = requests.post(url, json=dados, timeout=120)
        
        fim = time.time()
        tempo_total = fim - inicio
        
        print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
            print(f"🔍 APIs utilizadas: {len(resultado.get('resultados', []))}")
            
            # Verificar se o formato das respostas segue o novo padrão
            for i, analise in enumerate(resultado.get('resultados', []), 1):
                api_nome = analise.get('api', 'Desconhecida')
                conteudo = analise.get('resultado', '')
                
                print(f"\n📋 ANÁLISE {i} - {api_nome}")
                print(f"📝 Tamanho: {len(conteudo)} caracteres")
                
                # Verificar se contém as seções obrigatórias do novo formato
                secoes_obrigatorias = [
                    "ANÁLISE ESPECIALIZADA",
                    "ESTRUTURA DO DOCUMENTO", 
                    "ALTERAÇÕES PROPOSTAS",
                    "RISCOS JURÍDICOS IDENTIFICADOS",
                    "RESUMO EXECUTIVO"
                ]
                
                secoes_encontradas = []
                for secao in secoes_obrigatorias:
                    if secao in conteudo:
                        secoes_encontradas.append(secao)
                
                print(f"✅ Seções do novo formato encontradas: {len(secoes_encontradas)}/{len(secoes_obrigatorias)}")
                
                # Mostrar as primeiras linhas da análise
                linhas = conteudo.split('\n')[:10]
                print("📝 Preview da análise:")
                for linha in linhas:
                    if linha.strip():
                        print(f"   {linha[:80]}...")
                        
                print("-" * 50)
            
            # Resumo final
            print(f"\n🎯 TESTE CONCLUÍDO")
            print(f"✅ Sistema respondeu adequadamente")
            print(f"📊 Total de análises: {len(resultado.get('resultados', []))}")
            print(f"⏱️ Performance: {tempo_total:.1f}s")
            
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            print(f"📋 Resposta: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Análise demorou mais que 120 segundos")
    except requests.exceptions.ConnectionError:
        print("🔌 ERRO DE CONEXÃO - Verifique se o servidor está rodando")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    testar_analise_especializada()