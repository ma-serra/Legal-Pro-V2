#!/usr/bin/env python3
"""
Teste específico com o documento real anexado
"""

import requests
import json
import time

# Documento real anexado pelo usuário
CONTRATO_REAL = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS, QUE ENTRE SI FAZEM xxxxxxxxx& xxxxxxx E MAYMIDIA SERVIÇOS E MARKETING

com sede à Rua xxxxxxxxxx,xxxx, Porto Alegre/RS, inscrita no CNPJ/MF sob nº xx.xxx.xxx/xxxxxx neste ato representada por xxxxxxxx inscrita no CPF xxx.xxx.xxx-xx, doravante denominada CONTRATANTE, e a MAYMIDIA, com sede à Rua Furriel Luiz Antônio de Vargas, 250, Conj 403, Bairro Bela Vista, CEP 90.470-130, Porto Alegre/RS, inscrita no CNPJ/MF sob nº 47.856.359/0001-29, neste ato representada por Karina Ribeiro Guazzelli May, brasileira, empresária, CPF 824.714.360-72.

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
O planejamento dos serviços constantes na proposta comercial, está previsto para ser realizado em até 20 (vinte) dias úteis após o recebimento das informações e materiais necessários.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados, podendo ser rescindido conforme itens 7.2, 7.3
A CONTRATANTE poderá, mediante comunicação por escrito, rescindir o presente contrato sem ônus para a mesma, na hipótese de a CONTRATADA não cumprir com as suas obrigações previstas no presente CONTRATO.

DO FORO
Fica eleito o FORO da Porto Alegre, estado do Rio Grande do Sul, com expressa renúncia a qualquer outro por mais privilegiado que seja ou venha ser, para dirimir e solucionar eventuais dúvidas, questões ou litígios oriundos do presente instrumento.
"""

def test_with_real_contract():
    """Testa análise com o contrato real"""
    print("🔍 TESTE COM CONTRATO REAL ANEXADO")
    print("=" * 60)
    
    # Detectar tipo automaticamente
    # Simular dados do formulário HTML
    payload = {
        'texto_documento': CONTRATO_REAL
    }
    
    # Adicionar agentes como campos separados (simulando formulário HTML)
    for i, agente_id in enumerate(['1', '2', '3']):
        payload[f'agentes_selecionados'] = agente_id
    
    print(f"📄 Documento: {len(CONTRATO_REAL)} caracteres")
    print(f"📋 Tipo: Contrato de Prestação de Serviços")
    print(f"⚖️ Área: Direito Empresarial/Civil")
    
    try:
        inicio = time.time()
        
        response = requests.post(
            "http://localhost:5000/api/multi-agente-real/analise-real",
            data=payload,
            timeout=180
        )
        
        tempo = time.time() - inicio
        
        print(f"⏱️ Tempo: {tempo:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"🆔 ID: {data.get('id', 'N/A')}")
            print(f"👥 Agentes: {data.get('total_agentes', 0)}")
            
            # Verificar cada API
            resultados = data.get('resultados_por_api', {})
            for api in ['openai', 'anthropic', 'gemini']:
                if api in resultados:
                    result = resultados[api]
                    status = result.get('status', 'N/A')
                    tokens = result.get('tokens_usados', 0)
                    print(f"  🤖 {api.upper()}: {status} ({tokens} tokens)")
                    
                    if status == 'sucesso' and result.get('analise'):
                        analise = result['analise'][:200]
                        print(f"    📝 Preview: {analise}...")
                        
            return True
            
        else:
            print(f"❌ ERRO {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    test_with_real_contract()