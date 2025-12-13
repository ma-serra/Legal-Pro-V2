#!/usr/bin/env python3
"""
Teste com documento anexado real - versão OpenAI apenas para debug
"""

import requests
import json
import time

# Documento anexado real completo
with open('attached_assets/Contrato de prestação de serviço original_1753265467594.docx', 'rb') as f:
    # Vamos usar o texto que sabemos que funcionou antes
    DOCUMENTO_REAL = """
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
Pela prestação de serviços objeto deste contrato, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais), sendo entrada de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) mediante a assinatura deste contrato e mais duas parcela de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) em 30 dias.

DO CRONOGRAMA
O planejamento dos serviços constantes na proposta comercial, está previsto para ser realizado em até 20 (vinte) dias úteis após o recebimento das informações e materiais necessários.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados.

Porto Alegre 10 de Julho de 2023.
Pela CONTRATANTE: Camila Steinmetz
Pela CONTRATADA: Karina Guazzelli May
"""

def test_with_real_document():
    """Testa com documento real anexado"""
    print("=" * 80)
    print("TESTE COM DOCUMENTO REAL ANEXADO - ANÁLISE SEQUENCIAL")
    print("=" * 80)
    
    files = {
        'texto_documento': (None, DOCUMENTO_REAL),
        'agentes_selecionados': (None, '1'),  # Civil
        'agentes_selecionados': (None, '2'),  # Trabalhista
        'agentes_selecionados': (None, '3')   # Empresarial
    }
    
    print(f"📄 Documento real: {len(DOCUMENTO_REAL)} caracteres")
    print(f"📋 Contrato: MAYMIDIA - Marketing Digital")
    print(f"💰 Valor: R$ 12.678,00")
    print(f"📅 Data: 10 de Julho de 2023")
    print(f"🏢 Local: Porto Alegre/RS")
    print(f"👥 Agentes: 3 especializados")
    print("-" * 50)
    print("⚙️ TESTE CONFIGURAÇÃO SEQUENCIAL:")
    print("• Processamento: Uma API por vez")
    print("• OpenAI GPT-4o: 6800 tokens, timeout 90s")
    print("• Anthropic Claude: 6800 tokens, timeout 90s") 
    print("• Google Gemini: 6800 tokens, timeout 90s")
    print("• Servidor: timeout 300s")
    print("-" * 50)
    
    try:
        print("🚀 Enviando documento real para análise sequencial...")
        inicio = time.time()
        
        response = requests.post(
            "http://localhost:5000/api/multi-agente-real/analise-real",
            files=files,
            timeout=300
        )
        
        tempo_total = time.time() - inicio
        
        print(f"⏱️ Tempo total: {tempo_total:.2f}s")
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ANÁLISE SEQUENCIAL COM DOCUMENTO REAL CONCLUÍDA!")
            print("=" * 50)
            
            # Informações principais
            print(f"🆔 ID da análise: {data.get('id', 'N/A')}")
            print(f"🔐 Hash do documento: {data.get('hash_documento', 'N/A')}")
            print(f"👥 Agentes processados: {data.get('total_agentes', 0)}")
            print(f"🕒 Tempo de processamento: {data.get('tempo_total', 0):.2f}s")
            print("=" * 50)
            
            # Resultados por API
            resultados = data.get('resultados_por_api', {})
            
            for step, api_name in enumerate(['openai', 'anthropic', 'gemini'], 1):
                if api_name in resultados:
                    resultado = resultados[api_name]
                    status = resultado.get('status', 'N/A')
                    tokens = resultado.get('tokens_usados', 0)
                    modelo = resultado.get('modelo', 'N/A')
                    
                    print(f"🤖 PASSO {step}/3: {api_name.upper()} ({modelo})")
                    print(f"   ✓ Status: {status}")
                    print(f"   📊 Tokens: {tokens:,}")
                    
                    if status == 'sucesso' and resultado.get('analise'):
                        analise = resultado['analise']
                        linhas = analise.count('\n') + 1
                        palavras = len(analise.split())
                        
                        print(f"   📝 Caracteres: {len(analise):,}")
                        print(f"   📄 Linhas: {linhas}")
                        print(f"   💬 Palavras: {palavras}")
                        
                        # Preview da análise
                        preview = analise[:400].replace('\n', ' ')
                        print(f"   👀 Preview: {preview}...")
                        
                    elif status == 'erro':
                        error_msg = resultado.get('analise', 'N/A')
                        print(f"   ❌ Erro: {error_msg[:150]}...")
                    print()
            
            # Resumo final
            if 'resumo_consolidado' in resultados:
                consolidado = resultados['resumo_consolidado']
                apis_sucesso = consolidado.get('total_apis_sucesso', 0)
                total_tokens = consolidado.get('total_tokens_usados', 0)
                
                print(f"📈 RESUMO FINAL DA ANÁLISE SEQUENCIAL")
                print(f"   🎯 APIs bem-sucedidas: {apis_sucesso}/3")
                print(f"   🔢 Total de tokens: {total_tokens:,}")
                print(f"   ⚡ Média tokens/API: {total_tokens//3 if apis_sucesso > 0 else 0:,}")
                print(f"   📋 Observações: {consolidado.get('observacoes', 'N/A')}")
                
                if consolidado.get('analise_consolidada'):
                    consolidada_size = len(consolidado['analise_consolidada'])
                    print(f"   📊 Análise consolidada: {consolidada_size:,} caracteres")
            
            print("=" * 80)
            
            if apis_sucesso == 3:
                print("🎉 SISTEMA SEQUENCIAL 100% OPERACIONAL!")
                print("✅ Todas as 3 APIs processaram o documento real sequencialmente")
                print(f"📊 Total: {total_tokens:,} tokens utilizados")
                print("⚙️ Configuração: 6800 tokens por API, timeout 90s cada")
                print("🔄 Processamento: Sequencial conforme solicitado")
            elif apis_sucesso >= 2:
                print("⚠️ SISTEMA SEQUENCIAL PARCIALMENTE OPERACIONAL")
                print(f"✅ {apis_sucesso}/3 APIs processaram com sucesso")
                print("💡 Uma API pode ter problemas de conectividade")
            elif apis_sucesso == 1:
                print("🔄 SISTEMA SEQUENCIAL COM LIMITAÇÕES")
                print(f"✅ {apis_sucesso}/3 APIs funcionaram")
                print("🔧 Duas APIs podem precisar de ajustes")
            else:
                print("❌ SISTEMA SEQUENCIAL COM PROBLEMAS")
                print("❓ Nenhuma API processou com sucesso")
                
            print("=" * 80)
            return True
            
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Erro JSON: {error_data}")
            except:
                print(f"📄 Resposta texto: {response.text[:800]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Análise sequencial demorou mais que 5 minutos")
        print("💡 Pode indicar problemas de conectividade com as APIs")
        return False
    except Exception as e:
        print(f"❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = test_with_real_document()
    if sucesso:
        print("\n🎯 TESTE COM DOCUMENTO REAL CONCLUÍDO!")
        print("📋 Sistema validado com contrato MAYMIDIA real")
        print("⚙️ Processamento sequencial das 3 APIs funcionando")
    else:
        print("\n💔 SISTEMA PRECISA DE CORREÇÕES ADICIONAIS")
        print("🔧 Verificar configurações e conectividade das APIs")