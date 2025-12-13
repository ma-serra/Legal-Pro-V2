#!/usr/bin/env python3
"""
Teste do sistema sequencial com todas as 3 APIs
"""

import requests
import json
import time

# Documento anexado para teste
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

DA CONFIDENCIALIDADE
O objeto deste contrato, a CONTRATANTE e os resultados obtidos farão parte do portifólio da CONTRATADA, com o intuito de servirem como referência para serviços já prestados, podendo ser divulgados com o uso de marcas da CONTRATANTE, seja durante ou após o término/rescisão deste CONTRATO.

DO PREÇO
Pela prestação de serviços objeto deste contrato, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais), sendo entrada de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) mediante a assinatura deste contrato e mais duas parcela de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) em 30 dias.

DO CRONOGRAMA
O planejamento dos serviços constantes na proposta comercial, está previsto para ser realizado em até 20 (vinte) dias úteis após o recebimento das informações e materiais necessários. A partir daí, têm início a sua execução e controle.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados, podendo ser rescindido conforme itens 7.2, 7.3

DO FORO
Fica eleito o FORO da Porto Alegre, estado do Rio Grande do Sul, com expressa renúncia a qualquer outro por mais privilegiado que seja ou venha ser, para dirimir e solucionar eventuais dúvidas, questões ou litígios oriundos do presente instrumento.

E por estarem assim justos e contratados, obrigam-se por si e seus sucessores, assinam o presente instrumento.

Porto Alegre 10 de Julho de 2023.

Pela CONTRATANTE: Camila Steinmetz
Pela CONTRATADA: Karina Guazzelli May
"""

def test_sequential_apis():
    """Testa processamento sequencial das 3 APIs"""
    print("=" * 80)
    print("TESTE SISTEMA SEQUENCIAL - 3 APIS (6800 TOKENS CADA, TIMEOUT 90S)")
    print("=" * 80)
    
    files = {
        'texto_documento': (None, DOCUMENTO_MAYMIDIA),
        'agentes_selecionados': (None, '1'),
        'agentes_selecionados': (None, '2'),
        'agentes_selecionados': (None, '3')
    }
    
    print(f"📄 Documento: {len(DOCUMENTO_MAYMIDIA)} caracteres")
    print(f"📋 Contrato: MAYMIDIA - Marketing Digital")
    print(f"👥 Agentes: 3 especializados")
    print(f"💰 Valor: R$ 12.678,00")
    print("-" * 50)
    print("⚙️ CONFIGURAÇÃO SEQUENCIAL:")
    print("• PASSO 1: OpenAI GPT-4o (6800 tokens, 90s)")
    print("• PASSO 2: Anthropic Claude (6800 tokens, 90s)")
    print("• PASSO 3: Google Gemini (6800 tokens, 90s)")
    print("• Servidor timeout: 300s")
    print("• Execução: Uma API por vez (sequencial)")
    print("-" * 50)
    
    try:
        print("🚀 Iniciando processamento sequencial...")
        inicio = time.time()
        
        response = requests.post(
            "http://localhost:5000/api/multi-agente-real/analise-real",
            files=files,
            timeout=300  # 5 minutos para todas as 3 APIs sequenciais
        )
        
        tempo_total = time.time() - inicio
        
        print(f"⏱️ Tempo total: {tempo_total:.2f}s")
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PROCESSAMENTO SEQUENCIAL CONCLUÍDO!")
            print("=" * 50)
            
            # Informações gerais
            print(f"🆔 ID: {data.get('id', 'N/A')}")
            print(f"👥 Agentes processados: {data.get('total_agentes', 0)}")
            print(f"🕒 Tempo processamento: {data.get('tempo_total', 0):.2f}s")
            print("=" * 50)
            
            # Resultados detalhados por API (sequencial)
            resultados = data.get('resultados_por_api', {})
            
            for step, api_name in enumerate(['openai', 'anthropic', 'gemini'], 1):
                if api_name in resultados:
                    resultado = resultados[api_name]
                    status = resultado.get('status', 'N/A')
                    tokens = resultado.get('tokens_usados', 0)
                    modelo = resultado.get('modelo', 'N/A')
                    
                    print(f"🤖 PASSO {step}: {api_name.upper()} ({modelo})")
                    print(f"   Status: {status}")
                    print(f"   Tokens: {tokens:,}")
                    
                    if status == 'sucesso' and resultado.get('analise'):
                        analise = resultado['analise']
                        preview = analise[:300].replace('\n', ' ')
                        print(f"   Caracteres: {len(analise):,}")
                        print(f"   Preview: {preview}...")
                    elif status == 'erro':
                        error_msg = resultado.get('analise', 'N/A')
                        print(f"   Erro: {error_msg[:100]}...")
                    print()
            
            # Resumo consolidado
            if 'resumo_consolidado' in resultados:
                consolidado = resultados['resumo_consolidado']
                apis_sucesso = consolidado.get('total_apis_sucesso', 0)
                total_tokens = consolidado.get('total_tokens_usados', 0)
                
                print(f"📈 RESUMO FINAL SEQUENCIAL")
                print(f"   APIs processadas com sucesso: {apis_sucesso}/3")
                print(f"   Total de tokens utilizados: {total_tokens:,}")
                print(f"   Observações: {consolidado.get('observacoes', 'N/A')}")
                
                if consolidado.get('analise_consolidada'):
                    consolidada_size = len(consolidado['analise_consolidada'])
                    print(f"   Análise consolidada: {consolidada_size:,} caracteres")
            
            print("=" * 80)
            
            if apis_sucesso >= 2:
                print("🎉 SISTEMA SEQUENCIAL FUNCIONANDO PERFEITAMENTE!")
                print(f"✅ {apis_sucesso}/3 APIs processaram sequencialmente")
                print(f"📊 Total: {total_tokens:,} tokens utilizados")
                print("⚙️ Processamento sequencial: Cada API processou uma por vez")
            elif apis_sucesso == 1:
                print("⚠️ SISTEMA PARCIALMENTE OPERACIONAL")
                print(f"✅ {apis_sucesso}/3 APIs funcionaram sequencialmente")
                print("💡 Algumas APIs podem ter problemas de conectividade")
            else:
                print("❌ SISTEMA COM PROBLEMAS")
                print("❓ Nenhuma API processou com sucesso")
                
            print("=" * 80)
            return True
            
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Processamento demorou mais que 5 minutos")
        print("💡 Isso pode indicar problemas nas APIs ou conectividade")
        return False
    except Exception as e:
        print(f"❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = test_sequential_apis()
    if sucesso:
        print("\n🎯 TESTE SEQUENCIAL CONCLUÍDO!")
        print("📋 Sistema configurado para processamento sequencial das 3 APIs")
        print("⚙️ Cada API processa com 6800 tokens e timeout de 90s")
    else:
        print("\n💔 SISTEMA SEQUENCIAL PRECISA DE AJUSTES")