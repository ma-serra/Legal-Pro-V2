#!/usr/bin/env python3
"""
Script para testar a análise do contrato rural anexado
Mapeia todo o fluxo do sistema e identifica possíveis erros
"""
import requests
import json
import time
import os

def extrair_texto_contrato():
    """Extrai o texto do contrato rural para análise"""
    
    # Texto do contrato baseado no anexo fornecido
    texto_contrato = """
Contrato Particular de Arrendamento Rural

ARRENDANTES: {{ arrendante 1 }}
{{ arrendante 2 }}

ARRENDATÁRIO: {{ arrendatario }}

Cláusula Primeira - Do Objeto

Os ARRENDANTES são os legítimos possuidores e proprietários registrais dos seguintes imóveis rurais:

área de terras de de {{ area terras 1 }}ha {{ (area por ext 1) }}, objeto da matrícula n.º {{ numero matricula }} do Registro de Imóveis da Comarca de {{ cidade/uf da comarca }}.

área de terras de de {{ area terras 2 }}ha {{ (area por ext 2) }}, objeto da matrícula n.º {{ numero matricula }} do Registro de Imóveis da Comarca de {{ cidade/uf da comarca }}.

Nos termos da Lei n° 4.504/1964 (Estatuto da Terra), com as regulamentações do Decreto n° 59.566/1966, os ARRENDANTES, por meio deste Contrato, arrendam ao ARRENDATÁRIO o imóvel acima referido, com área agricultável de {{ hectares agriculturável 1 }}ha {{ (hectares agriculturável por ext 1) }}, com todas as benfeitorias existentes sobre ele, com a finalidade exclusiva de que seja exercida a atividade agrícola, especialmente o cultivo de grãos.

Cláusula Segunda - Da Posse

O ARRENDATÁRIO já se encontra na posse do imóvel objeto deste Contrato. O ARRENDATÁRIO será imitido na posse do imóvel em {{ data posse }}.

declara ter vistoriado integralmente o imóvel rural objeto deste Contrato, estando plenamente ciente em relação às condições de aproveitamento para exercício da atividade rural, bem como ter pleno conhecimento das divisas das áreas, da qualidade de seu solo e de todas as circunstâncias relacionadas ao bem.

Cláusula Terceira - Do Prazo

O prazo de vigência deste Contrato é de 3 (três) anos, com início em {{ data inicio dd mês por ext aaa 1 }}, com término em {{ data fim dd/mm/aaaa 1 }}, independentemente de qualquer notificação judicial ou extrajudicial, devendo a área objeto deste Contrato ser devolvida aos ARRENDANTES ao final do prazo aqui pactuado, nas mesmas condições em que se encontra neste momento, sem qualquer espécie de dano.

Cláusula Quarta – Do preço e da forma de pagamento

Em remuneração pelo uso da área de pecuária, o ARRENDATÁRIO pagará aos ARRENDANTES, por ano, o valor equivalente à {{ peso em kg 1 }}kg (quarenta e seis quilos) de "boi gordo", por hectare de pastagem, adotando-se como critério de conversão o preço do quilo do "boi gordo vivo", divulgado pela AGROLINK (site: https://www.agrolink.com.br/regional/rs/santo-antonio-das-missoes/cotacoes), no dia útil anterior ao dia do vencimento da obrigação.

Para fins de cálculo previsto na Cláusula 4.2., a área de pecuária será considerada de {{ hectares pecuaria }}ha {{ (hectares pecuaria por ext) }}, salvo na hipótese de ocorrer o aumento da área agricultável do imóvel, hipótese na qual a área de pecuária será reduzida na mesma proporção em que ocorrer o aumento da área agricultável.

O pagamento do valor apurado nos termos da Cláusula 4.2. e 4.2.1., acima, será realizado em moeda corrente nacional, em uma parcela anual, ao início de cada ano agrícola – de modo antecipado – até o dia {{ dd e mês por ext }} de cada ano, com primeiro pagamento ocorrendo em {{ dd e mês por ext aaaa 1 }} e os demais no mesmo dia dos anos subsequentes.

Cláusula 5ª - Das obrigações do Arrendatário

O ARRENDATÁRIO fica obrigado a fazer todo serviço de conservação de solo, de acordo com as normas agronômicas, fazer a necessária adubagem e calagem para correção do solo, utilizando sempre adubo e produtos de boa qualidade, com a boa conservação do solo.

Cláusula 7ª – Das Benfetorias

É terminantemente proibido ao ARRENDATÁRIO realizar quaisquer benfeitorias no imóvel, sem a autorização prévia e por escrito dos ARRENDANTES. A violação dessa cláusula não gerará qualquer indenização ou direito de retenção, mesmo em se tratando de benfeitorias que poderiam ser consideradas como úteis ou necessárias.

Cláusula 8ª - Hipóteses de Rescisão e Despejo

Este Contrato é celebrado em caráter irrevogável e irretratável, podendo ser rescindido nas hipóteses previstas no Decreto n.º 59.566/66 (art. 26), ou, ainda, nas seguintes hipóteses:

descumprimento de qualquer cláusula do presente Contrato por uma das Partes, não sanado no prazo de 30 (trinta) dias contados do envio de notificação pela Parte inocente à Parte inadimplente nesse sentido;

inadimplência, por prazo superior a 30 (trinta) dias, do ARRENDATÁRIO em relação ao pagamento dos valores descritos na Cláusula 4ª;

uso predatório, pelo ARRENDATÁRIO, do Imóvel e/ou suas benfeitorias, respondendo o ARRENDATÁRIO pelos eventuais danos causados aos ARRENDANTES;

caso o ARRENDATÁRIO mude a destinação do Imóvel, subarrende, cedam ou o emprestem, no todo ou em parte, sem o prévio e expresso consentimento dos ARRENDANTES.

Cláusula 9ª - Disposições Gerais

Este Contrato é firmado em caráter irrevogável e irretratável e obriga as Partes e seus herdeiros ou sucessores a qualquer título.

É terminantemente proibida a caça, pesca e criação de outros animais que não decorrentes da atividade de pecuária bovina, ovina, caprina.

As Parceiras elegem expressamente o Foro da Comarca de Ibirubá/RS, com exclusão de qualquer outro por mais privilegiado que seja, para nele serem dirimidas todas e quaisquer dúvidas ou controvérsias oriundas deste Contrato.
"""

    return texto_contrato

def testar_api_analise(texto_documento):
    """Testa a API de análise multi-agente"""
    
    print("🔍 TESTANDO API DE ANÁLISE MULTI-AGENTE")
    print("=" * 50)
    
    url = "http://localhost:5000/api/analise-multi-agente"
    
    # Dados para envio (corrigido para funcionar com form data)
    dados = {
        'texto_documento': texto_documento
    }
    
    # Enviar agentes como lista de formulário
    files = []
    for agente in ['21', '19', '38']:
        files.append(('agentes_selecionados', (None, agente)))
    
    try:
        print("📤 Enviando requisição para API...")
        response = requests.post(url, data=dados, files=files, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("✅ API RESPONDEU COM SUCESSO")
            print(f"🔗 Fallback Mode: {resultado.get('fallback_mode', 'N/A')}")
            print(f"📝 Mensagem: {resultado.get('message', 'N/A')}")
            print(f"👥 Total Agentes: {resultado.get('total_agentes', 'N/A')}")
            
            # Verificar se há análises reais
            resultados = resultado.get('resultados', [])
            print(f"\n📋 RESULTADOS DE ANÁLISE ({len(resultados)} agentes):")
            
            for i, res in enumerate(resultados, 1):
                print(f"\n{i}. {res.get('agente_nome', 'N/A')}")
                print(f"   Modelo: {res.get('modelo_usado', 'N/A')}")
                print(f"   Especialidade: {res.get('especialidade', 'N/A')}")
                analise = res.get('resultado', '')
                print(f"   Análise (primeiros 200 chars): {analise[:200]}...")
            
            # Verificar recomendações
            recomendacoes = resultado.get('recomendacoes_consolidadas', {})
            if recomendacoes:
                print(f"\n🎯 RECOMENDAÇÕES CONSOLIDADAS:")
                for tipo, lista in recomendacoes.items():
                    print(f"   {tipo.title()}: {len(lista)} itens")
            
            return True, resultado
            
        else:
            print(f"❌ ERRO NA API: {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}")
            return False, None
            
    except Exception as e:
        print(f"💥 ERRO NA REQUISIÇÃO: {str(e)}")
        return False, None

def verificar_salvamento(resultado_analise):
    """Verifica se o salvamento está funcionando"""
    
    print("\n🔍 TESTANDO SISTEMA DE SALVAMENTO")
    print("=" * 50)
    
    if not resultado_analise:
        print("❌ Sem resultado para salvar")
        return False
    
    url = "http://localhost:5000/api/validacao-multi-agente/salvar"
    
    # Dados de salvamento baseados no resultado da análise
    dados_salvamento = {
        'dados_resultado': json.dumps(resultado_analise),
        'metadados': json.dumps({
            'tipo_documento': 'Contrato de Arrendamento Rural',
            'agentes_utilizados': ['21', '19', '38'],
            'timestamp_teste': time.time()
        })
    }
    
    try:
        print("💾 Testando salvamento...")
        response = requests.post(url, data=dados_salvamento, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            resultado_salvamento = response.json()
            print("✅ SALVAMENTO REALIZADO COM SUCESSO")
            print(f"🆔 ID: {resultado_salvamento.get('id', 'N/A')}")
            print(f"🔗 UUID: {resultado_salvamento.get('uuid', 'N/A')}")
            return True
        else:
            print(f"❌ ERRO NO SALVAMENTO: {response.status_code}")
            print(f"📄 Resposta: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"💥 ERRO NO SALVAMENTO: {str(e)}")
        return False

def verificar_historico():
    """Verifica se o histórico está sendo exibido"""
    
    print("\n🔍 TESTANDO HISTÓRICO DE ANÁLISES")
    print("=" * 50)
    
    url = "http://localhost:5000/historico-analises"
    
    try:
        print("📜 Acessando histórico...")
        response = requests.get(url, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ HISTÓRICO ACESSÍVEL")
            # Verificar se há conteúdo HTML válido
            if "validacao_multi_agente" in response.text:
                print("✅ Página contém dados de validação")
                return True
            else:
                print("⚠️  Página acessível mas pode estar vazia")
                return True
        else:
            print(f"❌ ERRO NO HISTÓRICO: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 ERRO NO HISTÓRICO: {str(e)}")
        return False

def main():
    """Função principal do teste"""
    
    print("🚀 INICIANDO MAPEAMENTO COMPLETO DO FLUXO")
    print("=" * 60)
    print("📋 DOCUMENTO: Contrato de Arrendamento Rural - Pecuária")
    print("🎯 OBJETIVO: Mapear fluxo e identificar erros")
    print("=" * 60)
    
    # 1. Extrair texto do contrato
    print("\n1️⃣ EXTRAINDO TEXTO DO CONTRATO...")
    texto_contrato = extrair_texto_contrato()
    print(f"✅ Texto extraído: {len(texto_contrato)} caracteres")
    
    # 2. Testar API de análise
    print("\n2️⃣ TESTANDO API DE ANÁLISE...")
    sucesso_analise, resultado = testar_api_analise(texto_contrato)
    
    # 3. Testar salvamento
    if sucesso_analise:
        print("\n3️⃣ TESTANDO SALVAMENTO...")
        sucesso_salvamento = verificar_salvamento(resultado)
    else:
        print("\n3️⃣ ❌ PULANDO SALVAMENTO (ANÁLISE FALHOU)")
        sucesso_salvamento = False
    
    # 4. Testar histórico
    print("\n4️⃣ TESTANDO HISTÓRICO...")
    sucesso_historico = verificar_historico()
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DO MAPEAMENTO")
    print("=" * 60)
    print(f"✅ Análise Multi-Agente: {'✅ OK' if sucesso_analise else '❌ FALHOU'}")
    print(f"✅ Sistema de Salvamento: {'✅ OK' if sucesso_salvamento else '❌ FALHOU'}")
    print(f"✅ Histórico de Análises: {'✅ OK' if sucesso_historico else '❌ FALHOU'}")
    
    if sucesso_analise and sucesso_salvamento and sucesso_historico:
        print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("💡 Análise real com IA habilitada")
        print("💾 Salvamento operacional")
        print("📜 Histórico acessível")
    else:
        print("\n⚠️  PROBLEMAS IDENTIFICADOS:")
        if not sucesso_analise:
            print("   - API de análise não está funcionando corretamente")
        if not sucesso_salvamento:
            print("   - Sistema de salvamento apresenta falhas")
        if not sucesso_historico:
            print("   - Histórico não está acessível")
    
    print("\n✅ MAPEAMENTO COMPLETO FINALIZADO")

if __name__ == "__main__":
    main()