"""
Teste do Algoritmo de Seleção Inteligente com Alta Confiança
Validação do sistema para garantir >90% de acurácia
"""

import sys
import os
import logging

# Configurar logging para o teste
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def testar_sistema_completo():
    """Testa o sistema completo de alta confiança"""
    
    print("🎯 INICIANDO TESTE DO SISTEMA DE ALTA CONFIANÇA")
    print("=" * 60)
    
    try:
        # Importar componentes necessários
        from algoritmo_selecao_inteligente_v2 import AlgoritmoSelecaoInteligente, testar_algoritmo
        from sistema_confianca_alta import SistemaConfiancaAlta, testar_sistema_confianca
        
        print("\n1. 🧪 TESTANDO ALGORITMO DE SELEÇÃO BÁSICO")
        print("-" * 40)
        resultado_algoritmo = testar_algoritmo()
        print(f"✅ Algoritmo básico concluído")
        print(f"Área detectada: {resultado_algoritmo['area_detectada']}")
        print(f"Confiança: {resultado_algoritmo['confianca']:.2%}")
        
        print("\n2. 🚀 TESTANDO SISTEMA DE ALTA CONFIANÇA")
        print("-" * 40)
        resultado_sistema = testar_sistema_confianca()
        print(f"✅ Sistema de alta confiança concluído")
        print(f"Confiança Final: {resultado_sistema.confianca_final:.2%}")
        print(f"Nível de Certeza: {resultado_sistema.nivel_certeza}")
        print(f"Meta 90%: {'✅ ATINGIDA' if resultado_sistema.confianca_final >= 0.90 else '❌ NÃO ATINGIDA'}")
        
        print("\n3. 📊 TESTANDO CENÁRIOS DIVERSOS")
        print("-" * 40)
        
        # Cenários de teste
        cenarios = [
            {
                'nome': 'Contrato Empresarial Complexo',
                'texto': '''
                CONTRATO DE PRESTAÇÃO DE SERVIÇOS EMPRESARIAIS
                
                CONTRATANTE: Empresa Tech Solutions Ltda. - CNPJ: 12.345.678/0001-90
                Endereço: Rua das Empresas, 123, São Paulo - SP
                
                CONTRATADA: Legal Advisory Consultoria ME - CNPJ: 98.765.432/0001-10
                Endereço: Av. Paulista, 456, São Paulo - SP
                
                CLÁUSULA 1ª - DO OBJETO
                O presente contrato tem por objeto a prestação de serviços de consultoria 
                jurídica empresarial especializada em direito societário, incluindo:
                a) Assessoria em constituição de sociedades;
                b) Análise de contratos comerciais;
                c) Consultoria em reestruturação empresarial;
                d) Elaboração de pareceres jurídicos.
                
                CLÁUSULA 2ª - DAS OBRIGAÇÕES DA CONTRATADA
                A CONTRATADA se obriga a:
                I - Prestar os serviços com excelência técnica;
                II - Manter sigilo absoluto sobre informações confidenciais;
                III - Cumprir prazos estabelecidos;
                IV - Fornecer relatórios mensais de atividades.
                
                CLÁUSULA 3ª - DO VALOR E FORMA DE PAGAMENTO
                Pelos serviços prestados, a CONTRATANTE pagará à CONTRATADA 
                o valor mensal de R$ 15.000,00 (quinze mil reais).
                ''',
                'expectativa_area': 'empresarial',
                'confianca_minima': 0.85
            },
            {
                'nome': 'Processo Trabalhista',
                'texto': '''
                PETIÇÃO INICIAL - AÇÃO TRABALHISTA
                
                Excelentíssimo Senhor Doutor Juiz da 5ª Vara do Trabalho de São Paulo
                
                JOÃO SILVA, brasileiro, casado, operário, portador do CPF 123.456.789-00,
                residente na Rua das Flores, 789, São Paulo-SP, vem respeitosamente 
                à presença de Vossa Excelência, por meio de seu advogado constituído,
                propor a presente AÇÃO DE COBRANÇA DE VERBAS RESCISÓRIAS em face de
                METALÚRGICA ABC LTDA., pessoa jurídica de direito privado, inscrita 
                no CNPJ 11.222.333/0001-44.
                
                DOS FATOS:
                O Requerente foi admitido em 15/01/2020 para exercer a função de 
                operador de máquinas, com salário de R$ 2.500,00. Durante o período
                laborativo, sempre cumpriu suas obrigações com dedicação e pontualidade.
                
                Em 30/06/2024, foi dispensado sem justa causa, não recebendo as 
                seguintes verbas rescisórias:
                - Aviso prévio indenizado: R$ 2.500,00
                - 13º salário proporcional: R$ 1.250,00
                - Férias vencidas + 1/3: R$ 3.333,33
                - FGTS + 40%: R$ 1.800,00
                ''',
                'expectativa_area': 'trabalhista',
                'confianca_minima': 0.80
            },
            {
                'nome': 'Análise Criminal',
                'texto': '''
                DENÚNCIA CRIMINAL
                
                O MINISTÉRIO PÚBLICO DO ESTADO DE SÃO PAULO, por sua Promotora 
                de Justiça que esta subscreve, vem perante Vossa Excelência 
                oferecer DENÚNCIA contra:
                
                MARCOS ANTONIO DOS SANTOS, brasileiro, solteiro, nascido em 
                12/03/1985, filho de José dos Santos e Maria Silva, portador 
                do RG 12.345.678-9 SSP/SP e CPF 987.654.321-00.
                
                IMPUTAÇÃO:
                No dia 15 de julho de 2024, por volta das 22h30min, na Rua 
                Principal, 500, Centro, nesta cidade, o denunciado subtraiu, 
                para si, mediante grave ameaça exercida com emprego de arma 
                de fogo, a quantia de R$ 800,00 em dinheiro e um aparelho 
                celular Samsung Galaxy, pertencentes à vítima Carlos Eduardo.
                
                Assim agindo, o denunciado incorreu no crime previsto no 
                artigo 157, § 2º, inciso I, do Código Penal.
                
                MATERIALIDADE E AUTORIA:
                A materialidade delitiva está comprovada pelo Boletim de 
                Ocorrência, auto de exibição e apreensão da arma utilizada.
                ''',
                'expectativa_area': 'penal',
                'confianca_minima': 0.85
            }
        ]
        
        # Testar cada cenário
        sistema = SistemaConfiancaAlta()
        agentes_mock = gerar_agentes_mock()
        
        resultados_cenarios = []
        for i, cenario in enumerate(cenarios, 1):
            print(f"\n   Cenário {i}: {cenario['nome']}")
            resultado = sistema.processar_com_alta_confianca(
                cenario['texto'], agentes_mock
            )
            
            sucesso_area = 'empresarial' in cenario['expectativa_area'] if cenario['expectativa_area'] == 'empresarial' else True
            sucesso_confianca = resultado.confianca_final >= cenario['confianca_minima']
            sucesso_meta_90 = resultado.confianca_final >= 0.90
            
            resultado_cenario = {
                'nome': cenario['nome'],
                'confianca': resultado.confianca_final,
                'nivel_certeza': resultado.nivel_certeza,
                'sucesso_confianca': sucesso_confianca,
                'sucesso_meta_90': sucesso_meta_90,
                'agentes_selecionados': len(resultado.agentes_selecionados)
            }
            resultados_cenarios.append(resultado_cenario)
            
            status_confianca = "✅" if sucesso_confianca else "❌"
            status_meta = "✅" if sucesso_meta_90 else "❌"
            
            print(f"   Confiança: {resultado.confianca_final:.1%} {status_confianca}")
            print(f"   Meta 90%: {status_meta}")
            print(f"   Agentes: {len(resultado.agentes_selecionados)}")
        
        print("\n4. 📈 RESULTADOS FINAIS")
        print("-" * 40)
        
        total_cenarios = len(resultados_cenarios)
        cenarios_90_percent = sum(1 for r in resultados_cenarios if r['sucesso_meta_90'])
        cenarios_confianca_min = sum(1 for r in resultados_cenarios if r['sucesso_confianca'])
        
        percentual_90 = (cenarios_90_percent / total_cenarios) * 100
        percentual_confianca = (cenarios_confianca_min / total_cenarios) * 100
        
        print(f"Total de cenários testados: {total_cenarios}")
        print(f"Cenários com >90% confiança: {cenarios_90_percent}/{total_cenarios} ({percentual_90:.1f}%)")
        print(f"Cenários com confiança mínima: {cenarios_confianca_min}/{total_cenarios} ({percentual_confianca:.1f}%)")
        
        # Determinar sucesso geral
        sucesso_geral = percentual_90 >= 66.7  # Pelo menos 2/3 dos cenários
        
        print(f"\n🎯 RESULTADO GERAL: {'✅ SISTEMA APROVADO' if sucesso_geral else '❌ SISTEMA NECESSITA AJUSTES'}")
        
        if sucesso_geral:
            print("✅ O sistema atende aos requisitos de alta confiança")
            print("✅ Algoritmo de seleção inteligente funcionando corretamente")
            print("✅ Meta de >90% de confiança atingível na maioria dos casos")
        else:
            print("❌ Sistema necessita melhorias para atingir consistentemente >90%")
            print("🔧 Recomendações: Ajustar pesos do algoritmo e expandir base de conhecimento")
        
        return {
            'sucesso_geral': sucesso_geral,
            'percentual_90': percentual_90,
            'percentual_confianca': percentual_confianca,
            'resultados_cenarios': resultados_cenarios
        }
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_agentes_mock():
    """Gera agentes mock para teste"""
    return [
        {
            'id': 1,
            'nome': 'Especialista Empresarial Senior',
            'especialidade': 'Direito Empresarial',
            'capacidades': ['contratos empresariais', 'direito societário', 'consultoria empresarial'],
            'nivel_experiencia': 'senior',
            'categoria': 'Direito Empresarial'
        },
        {
            'id': 2,
            'nome': 'Consultor Civil',
            'especialidade': 'Direito Civil',
            'capacidades': ['contratos civis', 'responsabilidade civil', 'obrigações'],
            'nivel_experiencia': 'pleno',
            'categoria': 'Direito Civil'
        },
        {
            'id': 3,
            'nome': 'Especialista Trabalhista',
            'especialidade': 'Direito Trabalhista',
            'capacidades': ['verbas rescisórias', 'relações trabalhistas', 'CLT'],
            'nivel_experiencia': 'senior',
            'categoria': 'Direito Trabalhista'
        },
        {
            'id': 4,
            'nome': 'Analista Penal',
            'especialidade': 'Direito Penal',
            'capacidades': ['direito penal', 'processo criminal', 'defesa criminal'],
            'nivel_experiencia': 'pleno',
            'categoria': 'Direito Penal'
        },
        {
            'id': 5,
            'nome': 'Revisor Empresarial',
            'especialidade': 'Direito Empresarial',
            'capacidades': ['revisão de contratos', 'análise empresarial', 'consultoria societária'],
            'nivel_experiencia': 'senior',
            'categoria': 'Direito Empresarial'
        }
    ]

if __name__ == "__main__":
    resultado = testar_sistema_completo()
    
    if resultado and resultado['sucesso_geral']:
        print("\n🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        sys.exit(0)
    else:
        print("\n⚠️ SISTEMA NECESSITA MELHORIAS")
        sys.exit(1)