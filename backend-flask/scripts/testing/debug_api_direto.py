#!/usr/bin/env python3
"""
Debug direto da função de análise sem HTTP
"""

import os
import sys
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o path do projeto
sys.path.append('/home/runner/workspace')

# Importar as funções necessárias
from main import executar_analise_robusta_multi_api

# Documento de teste
DOCUMENTO_TESTE = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS ENTRE MAYMIDIA E CONTRATANTE

DO OBJETO
É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL.

DAS OBRIGAÇÕES DA CONTRATADA
- Executar os serviços contratados com observância das normas legais aplicáveis;
- Criação do Site e página de blog entregue ajustados para SEO;

DO PREÇO
Pela prestação de serviços, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados.

Porto Alegre 10 de Julho de 2023.
Pela CONTRATANTE: Camila Steinmetz
Pela CONTRATADA: Karina Guazzelli May
"""

def test_direct_function():
    """Testa a função diretamente sem HTTP"""
    print("=" * 60)
    print("TESTE DIRETO DA FUNÇÃO SEQUENCIAL")
    print("=" * 60)
    
    try:
        # Simular agentes objetos
        class AgenteSimulado:
            def __init__(self, nome, descricao):
                self.nome = nome
                self.descricao = descricao
        
        agentes_simulados = [
            AgenteSimulado("Especialista Civil", "Análise de contratos civis"),
            AgenteSimulado("Especialista Empresarial", "Análise empresarial"),
        ]
        
        print(f"📄 Documento: {len(DOCUMENTO_TESTE)} caracteres")
        print(f"👥 Agentes simulados: {len(agentes_simulados)}")
        print("-" * 40)
        
        # Executar função diretamente
        print("🚀 Executando função sequencial diretamente...")
        inicio = time.time()
        
        resultados = executar_analise_robusta_multi_api(DOCUMENTO_TESTE, agentes_simulados)
        
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.2f}s")
        print("✅ Função executada com sucesso!")
        print("-" * 40)
        
        # Analisar resultados
        for api in ['openai', 'anthropic', 'gemini']:
            if api in resultados and resultados[api]:
                resultado = resultados[api]
                status = resultado.get('status', 'N/A')
                tokens = resultado.get('tokens_usados', 0)
                
                print(f"🤖 {api.upper()}: {status} ({tokens} tokens)")
                
                if status == 'sucesso' and resultado.get('analise'):
                    preview = resultado['analise'][:200]
                    print(f"   Preview: {preview}...")
                elif status == 'erro':
                    error = resultado.get('analise', 'N/A')
                    print(f"   Erro: {error[:100]}...")
                print()
        
        # Resumo
        if 'resumo_consolidado' in resultados:
            consolidado = resultados['resumo_consolidado']
            apis_sucesso = consolidado.get('total_apis_sucesso', 0)
            total_tokens = consolidado.get('total_tokens_usados', 0)
            
            print(f"📊 RESUMO: {apis_sucesso}/3 APIs com sucesso")
            print(f"🔢 Total tokens: {total_tokens:,}")
            print(f"📋 Observações: {consolidado.get('observacoes', 'N/A')}")
        
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERRO na execução direta: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keys():
    """Testa se as chaves de API estão disponíveis"""
    print("🔑 VERIFICANDO CHAVES DE API:")
    
    keys = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY'),
        'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY')
    }
    
    for name, key in keys.items():
        if key:
            print(f"✅ {name}: Disponível ({key[:10]}...)")
        else:
            print(f"❌ {name}: NÃO DISPONÍVEL")
    print()

if __name__ == "__main__":
    test_keys()
    sucesso = test_direct_function()
    
    if sucesso:
        print("🎯 TESTE DIRETO CONCLUÍDO COM SUCESSO!")
        print("💡 A função sequencial está funcionando corretamente")
        print("🔍 O problema pode estar na API HTTP ou configuração do Flask")
    else:
        print("💔 PROBLEMA IDENTIFICADO NA FUNÇÃO DIRETA")
        print("🔧 Necessário debug adicional na implementação")