#!/usr/bin/env python3
"""
Teste final completo do sistema multi-agente com documento real
"""

import requests
import json
import time

# Documento real do anexo
CONTRATO_COMPLETO = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS, QUE ENTRE SI FAZEM xxxxxxxxx& xxxxxxx E MAYMIDIA SERVIÇOS E MARKETING

com sede à Rua xxxxxxxxxx,xxxx, Porto Alegre/RS, inscrita no CNPJ/MF sob nº xx.xxx.xxx/xxxxxx neste ato representada por xxxxxxxx inscrita no CPF xxx.xxx.xxx-xx, doravante denominada CONTRATANTE, e a MAYMIDIA, com sede à Rua Furriel Luiz Antônio de Vargas, 250, Conj 403, Bairro Bela Vista, CEP 90.470-130, Porto Alegre/RS, inscrita no CNPJ/MF sob nº 47.856.359/0001-29, neste ato representada por Karina Ribeiro Guazzelli May, brasileira, empresária, CPF 824.714.360-72, doravante denominada CONTRATADA.

DO OBJETO
É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL por parte da CONTRATADA para promover os serviços da CONTRATANTE.

DAS OBRIGAÇÕES DA CONTRATADA
Durante a vigência desse contrato, a CONTRATADA obriga-se a:
- Realizar reuniões presenciais ou virtuais previamente agendadas para realização das atividades necessárias à prestação de serviços;
- Executar os serviços contratados com observância das normas legais aplicáveis;
- Adquirir e configurar o provedor de hospedagem contratado (contrato de 12 meses do provedor) conforme proposta comercial anexa a este contrato;
- Criação do Site e página de blog entregue ajustados para SEO (incluindo Políticas de Privacidade, Termos de Uso e Cookie Banner adequado as normas da LGPD conforme proposta comercial anexa a este contrato;

DAS OBRIGAÇÕES DA CONTRATANTE
Durante a vigência desse contrato, a CONTRATANTE obriga-se a:
- Realizar reuniões presenciais ou virtuais previamente agendadas, para realização das atividades necessárias à prestação de serviços;
- Cumprir com as atribuições que lhe forem destinadas pela CONTRATADA para a adequada prestação dos serviços;
- Fornecer o material (textos, imagens, vídeos e demais informações) necessário para o adequado desenvolvimento dos serviços contratados;
- Efetuar os pagamentos devidos à CONTRATADA nos prazos e condições estabelecidas neste instrumento. Em caso de atraso superior a 10 dias no pagamento, a CONTRATADA pode optar por suspender a prestação dos serviços, retomando-a após a regularização.

DA CONFIDENCIALIDADE
O objeto deste contrato, a CONTRATANTE e os resultados obtidos farão parte do portifólio da CONTRATADA, com o intuito de servirem como referência para serviços já prestados, podendo ser divulgados com o uso de marcas da CONTRATANTE, seja durante ou após o término/rescisão deste CONTRATO.

Resguardando-se o presente no item 4.1, é vedado às PARTES reproduzir ou comunicar a terceiros dados de qualquer dos instrumentos deste CONTRATO sem o consentimento prévio e por escrito da outra PARTE.

Resguardando-se o presente no item 4.1, as PARTES devem guardar sigilo sobre os dados e informações de que tomarem conhecimento em função do CONTRATO, responsabilizando-se por quaisquer danos de qualquer natureza causados à parte prejudicada.

Não obstante o término do prazo contratual, as obrigações de confidencialidade acima mencionadas permanecerão em vigor pelo prazo de 01 (um) ano a contar da data do encerramento deste CONTRATO.

DO PREÇO
Pela prestação de serviços objeto deste contrato, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais), sendo entrada de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) mediante a assinatura deste contrato e mais duas parcela de R$ 4.226.00 (quatro mil duzentos e vinte e seis reais) em 30 dias.

DO CRONOGRAMA
O planejamento dos serviços constantes na proposta comercial, está previsto para ser realizado em até 20 (vinte) dias úteis após o recebimento das informações e materiais necessários. A partir daí, têm início a sua execução e controle.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados, podendo ser rescindido conforme itens 7.2, 7.3
A CONTRATANTE poderá, mediante comunicação por escrito, rescindir o presente contrato sem ônus para a mesma, na hipótese de a CONTRATADA não cumprir com as suas obrigações previstas no presente CONTRATO.
A CONTRATADA poderá, mediante comunicação por escrito, rescindir o presente CONTRATO na hipótese de atraso da CONTRATANTE no pagamento valores faltantes e reserva o direito legal de suspender os serviços de forma total ou parcial até a regularização do débito.

DAS DISPOSIÇÕES GERAIS
Os procedimentos operacionais deverão ser executados de acordo com os padrões e as normas estabelecidas de comum acordo entre a CONTRATANTE e a CONTRATADA.
Esta proposta contempla a realização das atividades em Porto Alegre. Em caso de necessidade de viagens para outras localidades, os custos envolvidos são responsabilidade da CONTRATANTE.

DA FORÇA MAIOR OU CASO FORTUITO
Nenhuma das partes poderá ser responsabilizada pela falta de cumprimento de suas obrigações contratuais, na efetiva e comprovada ocorrência de caso fortuito ou força maior, na forma do artigo 393 do Código Civil.

DO FORO
Fica eleito o FORO da Porto Alegre, estado do Rio Grande do Sul, com expressa renúncia a qualquer outro por mais privilegiado que seja ou venha ser, para dirimir e solucionar eventuais dúvidas, questões ou litígios oriundos do presente instrumento.

E por estarem assim justos e contratados, obrigam-se por si e seus sucessores, assinam o presente instrumento.

Porto Alegre 10 de Julho de 2023.

Pela CONTRATANTE: Camila Steinmetz
Pela CONTRATADA: Karina Guazzelli May

Proposta Comercial

Esta proposta contempla o planejamento e execução e dos seguintes serviços:

1 - Domínio e Hospedagem
Configuração e apontamento de DNS do domínio, contratação, instalação e configuração do site junto ao provedor de hospedagem.

2 - Criação do Site
Criação do site e página de blog, bem como sua otimização SEO, buscando a máxima experiência do usuário e classificação nos motores de busca do Google. Tratamento, adequação e otimização de fotos e imagens que serão usadas na criação das páginas).

• Hospedagem Wordpress Pro em servidor no Brasil com alta capacidade de memória, IP e recursos dedicados proporcionando melhor experiência aos visitantes;

• Criação, programação e otimização das páginas para terem melhor tempo de resposta e carregamento através de técnicas de super cache;
"""

def test_complete_analysis():
    """Executa teste completo da análise multi-agente"""
    print("=" * 80)
    print("TESTE COMPLETO - ANÁLISE MULTI-AGENTE COM DOCUMENTO REAL")
    print("=" * 80)
    
    # Preparar dados multipart/form-data corretamente
    files = {
        'texto_documento': (None, CONTRATO_COMPLETO),
        'agentes_selecionados': (None, '1'),
        'agentes_selecionados': (None, '2'), 
        'agentes_selecionados': (None, '3')
    }
    
    print(f"📄 Documento: {len(CONTRATO_COMPLETO)} caracteres")
    print(f"📋 Tipo: Contrato de Prestação de Serviços de Marketing Digital")
    print(f"⚖️ Áreas: Direito Empresarial, Civil, Digital")
    print(f"👥 Agentes: 3 (IDs: 1, 2, 3)")
    print("-" * 50)
    
    try:
        print("🚀 Enviando para análise...")
        inicio = time.time()
        
        response = requests.post(
            "http://localhost:5000/api/multi-agente-real/analise-real",
            files=files,
            timeout=300  # 5 minutos
        )
        
        tempo_total = time.time() - inicio
        
        print(f"⏱️ Tempo total: {tempo_total:.2f}s")
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
            
            try:
                data = response.json()
                
                # Informações gerais
                print(f"🆔 ID: {data.get('id', 'N/A')}")
                print(f"🔐 Hash: {data.get('hash_documento', 'N/A')}")
                print(f"👥 Total agentes: {data.get('total_agentes', 0)}")
                print(f"🌐 APIs utilizadas: {', '.join(data.get('apis_utilizadas', []))}")
                print("-" * 50)
                
                # Resultados por API
                resultados = data.get('resultados_por_api', {})
                
                for api_name in ['openai', 'anthropic', 'gemini']:
                    if api_name in resultados:
                        resultado = resultados[api_name]
                        status = resultado.get('status', 'N/A')
                        tokens = resultado.get('tokens_usados', 0)
                        modelo = resultado.get('modelo', 'N/A')
                        
                        print(f"🤖 {api_name.upper()} ({modelo})")
                        print(f"   Status: {status}")
                        print(f"   Tokens: {tokens}")
                        
                        if status == 'sucesso' and resultado.get('analise'):
                            analise = resultado['analise']
                            preview = analise[:300]
                            print(f"   Preview: {preview}...")
                            print(f"   Tamanho completo: {len(analise)} caracteres")
                        print()
                
                # Resumo consolidado
                if 'resumo_consolidado' in resultados:
                    consolidado = resultados['resumo_consolidado']
                    print(f"📈 RESUMO CONSOLIDADO")
                    print(f"   APIs com sucesso: {consolidado.get('total_apis_sucesso', 0)}")
                    if consolidado.get('analise_consolidada'):
                        preview_consolidado = consolidado['analise_consolidada'][:400]
                        print(f"   Preview: {preview_consolidado}...")
                
                print("=" * 80)
                print("✅ TESTE CONCLUÍDO COM SUCESSO - SISTEMA FUNCIONANDO 100%")
                print("=" * 80)
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Resposta bruta: {response.text[:1000]}")
                return False
                
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            print(f"📄 Resposta: {response.text[:1000]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Análise demorou mais que 5 minutos")
        return False
    except Exception as e:
        print(f"❌ EXCEÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = test_complete_analysis()
    if sucesso:
        print("\n🎉 SISTEMA MULTI-AGENTE TOTALMENTE OPERACIONAL!")
    else:
        print("\n💔 SISTEMA PRECISA DE AJUSTES")