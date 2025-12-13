#!/usr/bin/env python3
"""
Teste do sistema de 3 APIs robustas com 6500 tokens cada
Sistema anti-timeout com múltiplas tentativas e configurações otimizadas
"""

import os
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def teste_3_apis_6500_tokens():
    """Testa o sistema com 3 APIs e 6500 tokens cada"""
    
    # Documento de teste expandido
    documento_teste = """
    INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL

    Entre as partes:

    CONTRATADA: MAYMIDIA MARKETING DIGITAL LTDA
    CNPJ: 45.789.123/0001-45
    Endereço: Rua dos Comerciantes, 1234, Centro, Porto Alegre/RS, CEP 90010-000
    Telefone: (51) 3333-4444
    E-mail: contato@maymidia.com.br

    CONTRATANTE: João Silva Empresário Individual
    CPF: 123.456.789-00
    RG: 1234567 SSP/RS
    Endereço: Av. Principal, 567, Bairro Nobre, Porto Alegre/RS, CEP 91000-000
    Telefone: (51) 9999-8888
    E-mail: joao.silva@email.com

    CLÁUSULA PRIMEIRA - DO OBJETO
    1.1. A CONTRATADA prestará serviços especializados de marketing digital, incluindo:
    a) Gestão completa de redes sociais (Facebook, Instagram, LinkedIn, Twitter)
    b) Criação e execução de campanhas publicitárias online (Google Ads, Facebook Ads)
    c) Desenvolvimento de estratégias de SEO e SEM
    d) Consultoria estratégica em marketing digital
    e) Produção de conteúdo visual e textual
    f) Análise de métricas e relatórios de performance
    g) Gestão de relacionamento com influenciadores digitais

    CLÁUSULA SEGUNDA - DO VALOR E FORMA DE PAGAMENTO
    2.1. O valor total dos serviços é de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais).
    2.2. O pagamento será realizado em 6 (seis) parcelas mensais de R$ 2.113,00 (dois mil cento e treze reais).
    2.3. O vencimento das parcelas ocorrerá todo dia 10 de cada mês.
    2.4. Em caso de atraso superior a 15 dias, será aplicada multa de 2% sobre o valor em atraso.
    2.5. Após 30 dias de atraso, serão aplicados juros de mora de 1% ao mês.

    CLÁUSULA TERCEIRA - DO PRAZO E VIGÊNCIA
    3.1. O contrato terá vigência de 6 (seis) meses, iniciando em 10 de julho de 2023 e encerrando em 10 de janeiro de 2024.
    3.2. O contrato poderá ser prorrogado mediante acordo entre as partes.
    3.3. A rescisão antecipada poderá ocorrer mediante aviso prévio de 30 dias.

    CLÁUSULA QUARTA - DAS OBRIGAÇÕES DA CONTRATADA
    4.1. Entregar relatórios mensais detalhados de performance e métricas.
    4.2. Manter sigilo absoluto sobre informações comerciais do CONTRATANTE.
    4.3. Executar os serviços com qualidade e dentro dos prazos estabelecidos.
    4.4. Disponibilizar equipe técnica especializada para atendimento.
    4.5. Realizar reuniões quinzenais de alinhamento estratégico.

    CLÁUSULA QUINTA - DAS OBRIGAÇÕES DO CONTRATANTE
    5.1. Fornecer acesso às plataformas digitais necessárias para execução dos serviços.
    5.2. Disponibilizar materiais institucionais e briefings detalhados.
    5.3. Efetuar os pagamentos nas datas estabelecidas.
    5.4. Participar das reuniões de alinhamento estratégico.
    5.5. Aprovar campanhas e materiais no prazo máximo de 48 horas.

    CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL
    6.1. Todo material criado durante a vigência do contrato será de propriedade do CONTRATANTE.
    6.2. A CONTRATADA poderá utilizar os trabalhos em seu portfólio institucional.
    6.3. Materiais de terceiros utilizados deverão ter licenças adequadas.

    CLÁUSULA SÉTIMA - DA RESCISÃO
    7.1. O contrato poderá ser rescindido por qualquer das partes mediante aviso prévio de 30 dias.
    7.2. Em caso de inadimplemento, a rescisão poderá ser imediata.
    7.3. Na rescisão antecipada pelo CONTRATANTE sem justa causa, deverá ser pago 50% do valor restante.

    CLÁUSULA OITAVA - DO FORO
    8.1. Fica eleito o foro da Comarca de Porto Alegre/RS para dirimir quaisquer questões oriundas deste contrato.

    Porto Alegre/RS, 10 de julho de 2023.

    ________________________                    ________________________
    MAYMIDIA MARKETING DIGITAL LTDA             João Silva
    CONTRATADA                                   CONTRATANTE

    Testemunhas:
    1. Maria Santos - CPF: 111.222.333-44
    2. Pedro Oliveira - CPF: 555.666.777-88
    """
    
    print("=" * 100)
    print("TESTE SISTEMA 3 APIS ROBUSTAS - 6500 TOKENS CADA")
    print("=" * 100)
    print(f"📄 Documento expandido: {len(documento_teste)} caracteres")
    print("⚙️ APIs: OpenAI GPT-4o + Anthropic Claude + Google Gemini")
    print("🔧 Configuração: 6500 tokens cada, sistema anti-timeout")
    print("🛡️ Proteção: Múltiplas tentativas e configurações SSL otimizadas")
    print("-" * 80)
    
    # Simular o que será executado no sistema principal
    print("🚀 Simulando análise com 3 APIs...")
    
    from main import executar_analise_3_apis_robustas
    
    inicio = time.time()
    try:
        resultados = executar_analise_3_apis_robustas(documento_teste, [])
        tempo_total = time.time() - inicio
        
        print(f"⏱️ Tempo total: {tempo_total:.2f}s")
        print("=" * 60)
        
        # Verificar resultados de cada API
        for api_nome, resultado in resultados.items():
            if api_nome != 'resumo_consolidado' and resultado:
                status_emoji = "✅" if resultado.get('status') == 'sucesso' else "❌"
                print(f"{status_emoji} {api_nome.upper()}: {resultado.get('status', 'N/A')}")
                if resultado.get('tokens_usados'):
                    print(f"   📊 Tokens: {resultado['tokens_usados']}")
                if resultado.get('analise'):
                    preview = resultado['analise'][:200] + "..." if len(resultado['analise']) > 200 else resultado['analise']
                    print(f"   📝 Preview: {preview}")
                print()
        
        # Resumo consolidado
        if resultados.get('resumo_consolidado'):
            resumo = resultados['resumo_consolidado']
            print("=" * 60)
            print("📋 RESUMO CONSOLIDADO")
            print(f"✅ APIs bem-sucedidas: {resumo.get('total_apis_sucesso', 0)}/3")
            print(f"📊 Total tokens: {resumo.get('total_tokens', 0)}")
            print(f"📝 Observações: {resumo.get('observacoes', 'N/A')}")
            print("=" * 60)
        
        # Determinar se o teste foi bem-sucedido
        apis_sucesso = resumo.get('total_apis_sucesso', 0) if resumo else 0
        if apis_sucesso == 3:
            print("🎯 TESTE COMPLETAMENTE BEM-SUCEDIDO!")
            print("✅ Todas as 3 APIs funcionaram com 6500 tokens cada")
        elif apis_sucesso >= 2:
            print("⚠️ TESTE PARCIALMENTE BEM-SUCEDIDO!")
            print(f"✅ {apis_sucesso}/3 APIs funcionaram")
        else:
            print("❌ TESTE FALHOU!")
            print("🔧 Necessário revisar configurações")
            
    except Exception as e:
        tempo_total = time.time() - inicio
        print(f"❌ ERRO DURANTE TESTE: {e}")
        print(f"⏱️ Tempo até erro: {tempo_total:.2f}s")
    
    print("=" * 100)
    return True

if __name__ == "__main__":
    teste_3_apis_6500_tokens()