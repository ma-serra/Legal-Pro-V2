#!/usr/bin/env python3
"""
Teste da API simplificada apenas OpenAI
"""

import requests
import json
import time

DOCUMENTO_MAYMIDIA = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS, QUE ENTRE SI FAZEM xxxxxxxxx& xxxxxxx E MAYMIDIA SERVIÇOS E MARKETING

com sede à Rua xxxxxxxxxx,xxxx, Porto Alegre/RS, inscrita no CNPJ/MF sob nº xx.xxx.xxx/xxxxxx neste ato representada por xxxxxxxx inscrita no CPF xxx.xxx.xxx-xx, doravante denominada CONTRATANTE, e a MAYMIDIA, com sede à Rua Furriel Luiz Antônio de Vargas, 250, Conj 403, Bairro Bela Vista, CEP 90.470-130, Porto Alegre/RS, inscrita no CNPJ/MF sob nº 47.856.359/0001-29, neste ato representada por Karina Ribeiro Guazzelli May, brasileira, empresária, CPF 824.714.360-72, doravante denominada CONTRATADA.

DO OBJETO
É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL por parte da CONTRATADA para promover os serviços da CONTRATANTE.

DAS OBRIGAÇÕES DA CONTRATADA
Durante a vigência desse contrato, a CONTRATADA obriga-se a:
- Realizar reuniões presenciais ou virtuais previamente agendadas para realização das atividades necessárias à prestação de serviços;
- Executar os serviços contratados com observância das normas legais aplicáveis;
- Adquirir e configurar o provedor de hospedagem contratado (contrato de 12 meses do provedor) conforme proposta comercial anexa a este contrato;
- Criação do Site e página de blog entregue ajustados para SEO (incluindo Políticas de Privacidade, Termos de Uso e Cookie Banner adequado as normas da LGPD conforme proposta comercial anexa a este contrato.

DAS OBRIGAÇÕES DA CONTRATANTE
Durante a vigência desse contrato, a CONTRATANTE obriga-se a:
- Realizar reuniões presenciais ou virtuais previamente agendadas, para realização das atividades necessárias à prestação de serviços;
- Cumprir com as atribuições que lhe forem destinadas pela CONTRATADA para a adequada prestação dos serviços;
- Fornecer o material (textos, imagens, vídeos e demais informações) necessário para o adequado desenvolvimento dos serviços contratados;
- Efetuar os pagamentos devidos à CONTRATADA nos prazos e condições estabelecidas neste instrumento. Em caso de atraso superior a 10 dias no pagamento, a CONTRATADA pode optar por suspender a prestação dos serviços, retomando-a após a regularização.

DO PREÇO
Pela prestação de serviços objeto deste contrato, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oita reais), sendo entrada de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) mediante a assinatura deste contrato e mais duas parcela de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) em 30 dias.

DO CRONOGRAMA
O planejamento dos serviços constantes na proposta comercial, está previsto para ser realizado em até 20 (vinte) dias úteis após o recebimento das informações e materiais necessários.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados.

Porto Alegre 10 de Julho de 2023.
Pela CONTRATANTE: Camila Steinmetz
Pela CONTRATADA: Karina Guazzelli May
"""

def test_openai_simple():
    """Testa apenas OpenAI de forma simplificada"""
    print("=" * 70)
    print("TESTE OPENAI SIMPLES - VERIFICAÇÃO DA BASE")
    print("=" * 70)
    
    data = {
        'texto_documento': DOCUMENTO_MAYMIDIA
    }
    
    print(f"📄 Documento: {len(DOCUMENTO_MAYMIDIA)} caracteres")
    print(f"📋 Contrato: MAYMIDIA - Marketing Digital")
    print(f"💰 Valor: R$ 12.678,00")
    print("-" * 40)
    print("⚙️ CONFIGURAÇÃO TESTE:")
    print("• Modelo: OpenAI GPT-4o")
    print("• Tokens: 4000 (reduzido)")
    print("• Timeout: 60s")
    print("• API: Simplificada")
    print("-" * 40)
    
    try:
        print("🚀 Testando API OpenAI simples...")
        inicio = time.time()
        
        # Primeiro, iniciar a API simples
        print("📡 Conectando na API simplificada...")
        
        response = requests.post(
            "http://localhost:5001/api/analise-openai-simples",
            data=data,
            timeout=90
        )
        
        tempo_total = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo_total:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ANÁLISE OPENAI SIMPLES FUNCIONANDO!")
            print("-" * 40)
            
            print(f"🆔 ID: {result.get('id', 'N/A')}")
            print(f"🔐 Hash: {result.get('hash_documento', 'N/A')}")
            print(f"🤖 Modelo: {result.get('modelo', 'N/A')}")
            print(f"📊 Tokens: {result.get('tokens_usados', 0):,}")
            print(f"📝 Caracteres: {result.get('caracteres_analise', 0):,}")
            print(f"🕒 Tempo: {result.get('tempo_total', 0):.2f}s")
            
            if result.get('analise'):
                analise = result['analise']
                preview = analise[:500].replace('\n', ' ')
                print(f"👀 Preview: {preview}...")
            
            print("=" * 70)
            print("🎉 BASE OPENAI CONFIRMADA FUNCIONANDO!")
            print("✅ Sistema básico operacional")
            print("💡 Problema está no sistema completo com 3 APIs")
            print("=" * 70)
            return True
            
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Erro: {error_data}")
            except:
                print(f"📄 Resposta: {response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO")
        print("💡 API simples não está rodando na porta 5001")
        print("🔧 Execute: python api_analise_simples_openai.py")
        return False
    except Exception as e:
        print(f"❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = test_openai_simple()
    if sucesso:
        print("\n🎯 TESTE BÁSICO CONCLUÍDO!")
        print("📋 OpenAI funcionando isoladamente")
        print("🔧 Próximo: Investigar problema no sistema completo")
    else:
        print("\n💔 PROBLEMA NA BASE")
        print("🔧 Verificar configuração OpenAI")