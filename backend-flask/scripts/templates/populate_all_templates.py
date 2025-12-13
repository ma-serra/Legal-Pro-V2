"""
Script completo para popular todos os 99 templates com conteúdos únicos
Segue modelos padrão para cada área jurídica
"""

import os
from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def update_all_templates():
    """Atualiza todos os templates restantes com conteúdos únicos"""
    
    templates_content = {
        # DIREITO BANCÁRIO
        "CDC Bancário": """**AÇÃO CONSUMERISTA BANCÁRIA**

**I - DA RELAÇÃO DE CONSUMO**
Relação de consumo configurada entre {nome_consumidor} e {nome_banco}.

**II - DAS PRÁTICAS ABUSIVAS**
a) Cobrança de tarifas não autorizadas
b) Juros abusivos acima do limite legal
c) Capitalização indevida de juros

**III - DO DIREITO**
Aplicação do CDC - Lei 8.078/90 e Resolução BACEN.

**IV - DOS PEDIDOS**
Requer-se:
a) Declaração de nulidade das cláusulas abusivas
b) Restituição em dobro dos valores cobrados indevidamente
c) Indenização por danos morais

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Cartão de Crédito": """**AÇÃO REVISIONAL - CARTÃO DE CRÉDITO**

**I - DO CONTRATO**
Contrato de cartão de crédito nº {numero_contrato} com {nome_banco}.

**II - DAS IRREGULARIDADES**
a) Taxa de juros abusiva ({taxa_atual}% ao mês)
b) Cobrança de anuidade não informada
c) Capitalização irregular de juros

**III - DO DÉBITO**
Débito atual: R$ {valor_debito}
Encargos questionados: R$ {valor_encargos}

**IV - DOS PEDIDOS**
Requer-se revisão contratual e limitação da taxa de juros.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Compliance Bancário": """**RELATÓRIO DE COMPLIANCE BANCÁRIO**

**INSTITUIÇÃO:** {nome_banco}
**PERÍODO:** {periodo_analise}

**I - NORMAS APLICÁVEIS**
- Lei 9.613/98 (Lavagem de Dinheiro)
- Resolução BACEN 4.595/17
- Circular BACEN 3.978/20

**II - ANÁLISE DE CONFORMIDADE**
{analise_conformidade}

**III - RISCOS IDENTIFICADOS**
{riscos_mapeados}

**IV - PLANO DE AÇÃO**
{plano_acao_compliance}

**V - RECOMENDAÇÕES**
{recomendacoes_compliance}

{local}, {data}
{nome_compliance_officer}
Oficial de Compliance""",

        "Consignado": """**CONTRATO DE CRÉDITO CONSIGNADO**

**CREDOR:** {nome_banco}
**DEVEDOR:** {nome_servidor}

**CLÁUSULA 1ª - DO OBJETO**
Empréstimo consignado de R$ {valor_emprestimo}.

**CLÁUSULA 2ª - DAS CONDIÇÕES**
- Taxa de juros: {taxa_juros}% ao mês
- Prazo: {prazo_meses} meses
- Prestação: R$ {valor_prestacao}
- Margem consignável: {percentual_margem}%

**CLÁUSULA 3ª - DO DESCONTO**
Autorização de desconto em folha de pagamento.

**CLÁUSULA 4ª - DA GARANTIA**
Garantia mediante consignação em folha.

{local}, {data}
_____________________          _____________________
{representante_banco}         {nome_servidor}""",

        "Conta Corrente": """**CONTRATO DE CONTA CORRENTE**

**BANCO:** {nome_banco}
**CORRENTISTA:** {nome_cliente}

**CLÁUSULA 1ª - DA ABERTURA**
Abertura de conta corrente nº {numero_conta}.

**CLÁUSULA 2ª - DOS SERVIÇOS**
- Movimentação de conta
- Cheque especial até R$ {limite_especial}
- Cartão de débito

**CLÁUSULA 3ª - DAS TARIFAS**
Conforme Tabela de Tarifas vigente.

**CLÁUSULA 4ª - DOS JUROS**
Cheque especial: {taxa_especial}% ao mês.

**CLÁUSULA 5ª - DAS OBRIGAÇÕES**
{obrigacoes_cliente}

{local}, {data}
_____________________          _____________________
{gerente_banco}               {nome_cliente}""",

        "Financiamento Imobiliário": """**CONTRATO DE FINANCIAMENTO IMOBILIÁRIO**

**FINANCIADOR:** {nome_banco}
**MUTUÁRIO:** {nome_mutuario}

**CLÁUSULA 1ª - DO OBJETO**
Financiamento de R$ {valor_financiamento} para aquisição do imóvel localizado em {endereco_imovel}.

**CLÁUSULA 2ª - DAS CONDITIONS**
- Prazo: {prazo_anos} anos
- Taxa de juros: {taxa_juros}% ao ano + TR
- Sistema: Tabela {sistema_amortizacao}

**CLÁUSULA 3ª - DA GARANTIA**
Hipoteca do imóvel financiado.

**CLÁUSULA 4ª - DO SEGURO**
Seguro obrigatório: DFI e MIP.

{local}, {data}
_____________________          _____________________
{representante_banco}         {nome_mutuario}""",

        "Leasing": """**CONTRATO DE ARRENDAMENTO MERCANTIL**

**ARRENDADOR:** {nome_arrendador}
**ARRENDATÁRIO:** {nome_arrendatario}

**CLÁUSULA 1ª - DO OBJETO**
Arrendamento do bem: {descricao_bem}

**CLÁUSULA 2ª - DO PRAZO**
Prazo: {prazo_meses} meses

**CLÁUSULA 3ª - DO VALOR**
- Valor do bem: R$ {valor_bem}
- Contraprestação mensal: R$ {valor_prestacao}
- VRG: R$ {valor_residual}

**CLÁUSULA 4ª - DA OPÇÃO DE COMPRA**
Ao final, opção de compra pelo VRG.

{local}, {data}
_____________________          _____________________
{arrendador}                  {arrendatario}""",

        # DIREITO EMPRESARIAL
        "Capital de Risco": """**CONTRATO DE INVESTIMENTO EM CAPITAL DE RISCO**

**FUNDO:** {nome_fundo}
**EMPRESA INVESTIDA:** {nome_empresa}

**CLÁUSULA 1ª - DO INVESTIMENTO**
Investimento de R$ {valor_investimento} em troca de {percentual_participacao}% do capital.

**CLÁUSULA 2ª - DAS CONDITIONS**
- Direito a assento no conselho
- Aprovação em decisões estratégicas
- Cláusulas de drag along e tag along

**CLÁUSULA 3ª - DA GOVERNANÇA**
{regras_governanca}

**CLÁUSULA 4ª - DA SAÍDA**
{mecanismos_saida}

{local}, {data}
_____________________          _____________________
{representante_fundo}         {representante_empresa}""",

        "Compliance Corporativo": """**PROGRAMA DE COMPLIANCE CORPORATIVO**

**EMPRESA:** {nome_empresa}

**I - OBJETIVO**
Estabelecer diretrizes de conformidade e combate à corrupção.

**II - PRINCÍPIOS**
- Integridade e transparência
- Prevenção de riscos
- Conformidade legal

**III - ESTRUTURA**
{estrutura_compliance}

**IV - POLÍTICAS**
- Código de Conduta
- Política Anticorrupção
- Canal de Denúncias

**V - MONITORAMENTO**
{sistema_monitoramento}

{local}, {data}
{nome_compliance_officer}
Chief Compliance Officer""",

        "Contrato de Franquia": """**CONTRATO DE FRANQUIA EMPRESARIAL**

**FRANQUEADOR:** {nome_franqueador}
**FRANQUEADO:** {nome_franqueado}

**CLÁUSULA 1ª - DO OBJETO**
Concessão de franquia da marca {nome_marca}.

**CLÁUSULA 2ª - DO TERRITÓRIO**
Território exclusivo: {area_territorio}

**CLÁUSULA 3ª - DAS TAXAS**
- Taxa de franquia: R$ {taxa_franquia}
- Royalties: {percentual_royalties}% do faturamento
- Taxa de marketing: {percentual_marketing}%

**CLÁUSULA 4ª - DAS OBRIGAÇÕES**
{obrigacoes_franqueador}
{obrigacoes_franqueado}

{local}, {data}
_____________________          _____________________
{franqueador}                 {franqueado}""",

        "Dissolução Societária": """**INSTRUMENTO DE DISSOLUÇÃO SOCIETÁRIA**

**SOCIEDADE:** {nome_empresa}

**I - DA DECISÃO**
Os sócios decidem pela dissolução da sociedade em {data_decisao}.

**II - DO MOTIVO**
{motivo_dissolucao}

**III - DO LIQUIDANTE**
Nomeado como liquidante: {nome_liquidante}

**IV - DO ATIVO E PASSIVO**
Ativo total: R$ {valor_ativo}
Passivo total: R$ {valor_passivo}

**V - DA PARTILHA**
{regras_partilha}

{local}, {data}
Sócios:
{assinaturas_socios}""",

        "ESG Corporativo": """**RELATÓRIO ESG CORPORATIVO**

**EMPRESA:** {nome_empresa}
**PERÍODO:** {periodo_relatorio}

**I - ENVIRONMENTAL (AMBIENTAL)**
{indicadores_ambientais}

**II - SOCIAL**
{indicadores_sociais}

**III - GOVERNANCE (GOVERNANÇA)**
{indicadores_governanca}

**IV - METAS E OBJETIVOS**
{metas_esg}

**V - PLANO DE AÇÃO**
{plano_acao_esg}

**VI - CERTIFICAÇÕES**
{certificacoes_obtidas}

{local}, {data}
{nome_diretor_sustentabilidade}
Diretor de Sustentabilidade""",

        "Fusão e Aquisição": """**CONTRATO DE FUSÃO E AQUISIÇÃO**

**ADQUIRENTE:** {nome_adquirente}
**EMPRESA ALVO:** {nome_target}

**CLÁUSULA 1ª - DA OPERAÇÃO**
Aquisição de {percentual_aquisicao}% do capital social por R$ {valor_aquisicao}.

**CLÁUSULA 2ª - DAS CONDITIONS PRECEDENTES**
{condicoes_precedentes}

**CLÁUSULA 3ª - DAS GARANTIAS**
{garantias_vendedor}

**CLÁUSULA 4ª - DA GOVERNANÇA**
{estrutura_pos_aquisicao}

{local}, {data}
_____________________          _____________________
{adquirente}                  {vendedor}""",

        "Joint Venture": """**CONTRATO DE JOINT VENTURE**

**PARTE A:** {nome_empresa_a}
**PARTE B:** {nome_empresa_b}

**CLÁUSULA 1ª - DO OBJETO**
Constituição de joint venture para {objeto_jv}.

**CLÁUSULA 2ª - DA PARTICIPAÇÃO**
{empresa_a}: {percentual_a}%
{empresa_b}: {percentual_b}%

**CLÁUSULA 3ª - DA GESTÃO**
{estrutura_gestao}

**CLÁUSULA 4ª - DOS INVESTIMENTOS**
{compromissos_investimento}

**CLÁUSULA 5ª - DOS RESULTADOS**
{divisao_resultados}

{local}, {data}
_____________________          _____________________
{representante_a}             {representante_b}""",

        # DIREITO PENAL
        "Apelação Criminal": """**APELAÇÃO CRIMINAL**

**Excelentíssimos Senhores Desembargadores,**

{nome_apelante} vem interpor APELAÇÃO CRIMINAL da sentença que o condenou.

**I - DA SENTENÇA**
Sentença proferida em {data_sentenca} nos autos {numero_processo}.

**II - DOS FUNDAMENTOS**
a) Nulidade processual por {vicio_processual}
b) Insuficiência de provas
c) Dosimetria inadequada da pena

**III - DO MÉRITO**
{argumentacao_merito}

**IV - DOS PEDIDOS**
Requer-se:
a) Conhecimento do recurso
b) Absolvição do apelante
c) Subsidiariamente, redução da pena

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Embargos de Declaração": """**EMBARGOS DE DECLARAÇÃO**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_embargante} opõe EMBARGOS DE DECLARAÇÃO contra a decisão de {data_decisao}.

**I - DA DECISÃO EMBARGADA**
{identificacao_decisao}

**II - DAS OMISSÕES**
A decisão é omissa quanto a:
a) {omissao_1}
b) {omissao_2}

**III - DAS CONTRADIÇÕES**
{contradicoes_identificadas}

**IV - DOS PEDIDOS**
Requer-se o suprimento das omissões e esclarecimento das contradições.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Execução Penal": """**PETIÇÃO - EXECUÇÃO PENAL**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) da Execução,**

{nome_apenado} vem requerer {pedido_execucao}.

**I - DA SITUAÇÃO PROCESSUAL**
Sentença transitada em julgado em {data_transito}.
Pena: {tipo_pena} de {tempo_pena}.

**II - DO CUMPRIMENTO**
Início do cumprimento: {data_inicio}
Tempo cumprido: {tempo_cumprido}

**III - DOS REQUISITOS**
{requisitos_beneficio}

**IV - DOS PEDIDOS**
Requer-se {pedido_especifico}.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Indulto e Comutação": """**PEDIDO DE INDULTO/COMUTAÇÃO**

**Excelentíssimo Senhor Presidente da República,**

{nome_apenado} vem requerer {tipo_beneficio}.

**I - DA CONDENAÇÃO**
Condenado a {pena_aplicada} pelo crime de {tipo_crime}.

**II - DOS REQUISITOS**
Atendimento aos requisitos do Decreto nº {numero_decreto}:
a) {requisito_1}
b) {requisito_2}
c) {requisito_3}

**III - DOS FUNDAMENTOS**
{fundamentos_pedido}

**IV - DOS PEDIDOS**
Requer-se a concessão do {tipo_beneficio}.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Liberdade Provisória": """**PEDIDO DE LIBERDADE PROVISÓRIA**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_acusado} vem requerer LIBERDADE PROVISÓRIA.

**I - DA PRISÃO**
Preso em {data_prisao} com base em {fundamento_prisao}.

**II - DOS REQUISITOS**
a) Não presentes os requisitos da prisão preventiva
b) Endereço fixo: {endereco_fixo}
c) Ocupação lícita: {ocupacao}

**III - DAS MEDIDAS CAUTELARES**
Aceita as medidas do art. 319 do CPP:
{medidas_aceitas}

**IV - DOS PEDIDOS**
Requer-se a concessão da liberdade provisória.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Livramento Condicional": """**PEDIDO DE LIVRAMENTO CONDICIONAL**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) da Execução,**

{nome_apenado} vem requerer LIVRAMENTO CONDICIONAL.

**I - DA SITUAÇÃO**
Pena: {tipo_pena} de {tempo_total}
Cumprido: {tempo_cumprido}

**II - DOS REQUISITOS OBJETIVOS**
a) Cumprimento de {fracao_pena} da pena
b) Reparação do dano (quando possível)
c) Bom comportamento carcerário

**III - DOS REQUISITOS SUBJETIVOS**
{avaliacao_psicossocial}

**IV - DOS PEDIDOS**
Requer-se a concessão do livramento condicional.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Mandado de Segurança Criminal": """**MANDADO DE SEGURANÇA CRIMINAL**

**Excelentíssimo(a) Senhor(a) Doutor(a) Desembargador(a),**

{nome_impetrante} impetre MANDADO DE SEGURANÇA em favor de {nome_paciente}.

**I - DA AUTORIDADE COATORA**
{identificacao_autoridade}

**II - DO ATO COATOR**
{descricao_ato_coator}

**III - DO DIREITO LÍQUIDO E CERTO**
O direito violado consiste em {direito_violado}.

**IV - DOS FUNDAMENTOS**
{fundamentacao_juridica}

**V - DOS PEDIDOS**
Requer-se a concessão da segurança.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Progressão de Regime": """**PEDIDO DE PROGRESSÃO DE REGIME**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) da Execução,**

{nome_apenado} vem requerer PROGRESSÃO DE REGIME.

**I - DA SITUAÇÃO ATUAL**
Regime atual: {regime_atual}
Pena: {tempo_pena}
Cumprido: {tempo_cumprido}

**II - DOS REQUISITOS OBJETIVOS**
Cumprida {fracao_necessaria} da pena.

**III - DOS REQUISITOS SUBJETIVOS**
a) Bom comportamento carcerário
b) Mérito do condenado
c) {outros_requisitos}

**IV - DOS PEDIDOS**
Requer-se a progressão para o regime {regime_pretendido}.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Queixa-Crime": """**QUEIXA-CRIME**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) de Direito,**

{nome_querelante} oferece QUEIXA-CRIME contra {nome_querelado}.

**I - DOS FATOS**
Em {data_fato}, o querelado praticou {descricao_fato}.

**II - DA TIPIFICAÇÃO**
A conduta configura o crime previsto no artigo {artigo_penal} do CP.

**III - DA COMPETÊNCIA**
Crime de ação penal privada.

**IV - DOS PEDIDOS**
Requer-se:
a) Recebimento da queixa
b) Citação do querelado
c) Condenação nas penas do artigo {artigo_penal}

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Recurso em Sentido Estrito": """**RECURSO EM SENTIDO ESTRITO**

**Excelentíssimos Senhores Desembargadores,**

{nome_recorrente} interpõe RECURSO EM SENTIDO ESTRITO da decisão de {data_decisao}.

**I - DA DECISÃO RECORRIDA**
{identificacao_decisao}

**II - DA TEMPESTIVIDADE**
Recurso interposto no prazo legal.

**III - DOS FUNDAMENTOS**
{fundamentacao_recurso}

**IV - DOS PEDIDOS**
Requer-se:
a) Conhecimento do recurso
b) Reforma da decisão
c) {pedido_especifico}

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Relaxamento de Prisão": """**PEDIDO DE RELAXAMENTO DE PRISÃO**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_preso} vem requerer RELAXAMENTO DE PRISÃO.

**I - DA PRISÃO**
Preso em {data_prisao} por {motivo_prisao}.

**II - DA ILEGALIDADE**
A prisão é ilegal por:
a) {motivo_ilegalidade_1}
b) {motivo_ilegalidade_2}

**III - DO DIREITO**
{fundamentacao_legal}

**IV - DOS PEDIDOS**
Requer-se o relaxamento da prisão em flagrante.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Revisão Criminal": """**REVISÃO CRIMINAL**

**Excelentíssimos Senhores Desembargadores,**

{nome_requerente} propõe REVISÃO CRIMINAL da condenação de {nome_condenado}.

**I - DA CONDENAÇÃO**
Sentença condenatória transitada em julgado em {data_transito}.

**II - DOS FUNDAMENTOS**
Art. 621 do CPP:
a) {fundamento_revisao}

**III - DAS PROVAS NOVAS**
{provas_novas_apresentadas}

**IV - DOS PEDIDOS**
Requer-se:
a) Admissibilidade da revisão
b) Absolvição do condenado
c) Anulação da condenação

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Suspensão Condicional": """**PEDIDO DE SUSPENSÃO CONDICIONAL DO PROCESSO**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

O Ministério Público propõe SUSPENSÃO CONDICIONAL DO PROCESSO.

**I - DOS REQUISITOS**
a) Pena mínima não superior a 1 ano
b) Réu não condenado por crime doloso
c) Circunstâncias do crime favoráveis

**II - DAS CONDITIONS**
Período de prova: {periodo_prova}
Condições:
a) {condicao_1}
b) {condicao_2}

**III - DOS EFEITOS**
Extinção da punibilidade se cumpridas as condições.

{local}, {data}
{nome_promotor} - Promotor de Justiça""",

        # DIREITO TRABALHISTA
        "Acidente de Trabalho": """**AÇÃO ACIDENTÁRIA**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) do Trabalho,**

{nome_trabalhador} propõe ação em face de {nome_empresa}.

**I - DOS FATOS**
Em {data_acidente}, o autor sofreu acidente de trabalho consistente em {descricao_acidente}.

**II - DA NEGLIGÊNCIA**
A empresa foi negligente ao não:
a) {negligencia_1}
b) {negligencia_2}

**III - DOS DANOS**
{descricao_lesoes}
Sequelas: {sequelas_permanentes}

**IV - DOS PEDIDOS**
Indenização por danos morais e materiais.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Acordo Trabalhista": """**TERMO DE ACORDO TRABALHISTA**

**RECLAMANTE:** {nome_empregado}
**RECLAMADA:** {nome_empresa}

**CLÁUSULA 1ª - DA TRANSAÇÃO**
As partes transacionam sobre todas as verbas do contrato de trabalho.

**CLÁUSULA 2ª - DO VALOR**
Pagamento de R$ {valor_acordo} em {forma_pagamento}.

**CLÁUSULA 3ª - DA QUITAÇÃO**
Quitação geral das verbas trabalhistas e previdenciárias.

**CLÁUSULA 4ª - DO FGTS**
{tratamento_fgts}

{local}, {data}
_____________________          _____________________
{nome_empregado}              {representante_empresa}""",

        "Defesa Trabalhista": """**CONTESTAÇÃO TRABALHISTA**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) do Trabalho,**

{nome_empresa} contesta a reclamação trabalhista.

**I - PRELIMINARES**
a) {preliminar_1}
b) {preliminar_2}

**II - DO MÉRITO**
a) Cumprimento das obrigações trabalhistas
b) Inexistência de horas extras
c) Pagamento regular de verbas

**III - DOS PEDIDOS**
Requer-se a total improcedência da ação.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Execução Trabalhista": """**EXECUÇÃO TRABALHISTA**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) do Trabalho,**

{nome_exequente} requer a execução da sentença.

**I - DO TÍTULO EXECUTIVO**
Sentença transitada em julgado em {data_transito}.

**II - DOS CÁLCULOS**
Valor da execução: R$ {valor_execucao}
Atualização: R$ {valor_atualizacao}
Total: R$ {valor_total}

**III - DOS PEDIDOS**
Requer-se:
a) Citação para pagamento
b) Penhora de bens
c) Arrematação

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Recurso Ordinário Trabalhista": """**RECURSO ORDINÁRIO TRABALHISTA**

**Excelentíssimos Senhores Desembargadores,**

{nome_recorrente} interpõe RECURSO ORDINÁRIO da sentença.

**I - DA SENTENÇA**
Sentença proferida em {data_sentenca}.

**II - DOS FUNDAMENTOS**
{fundamentos_recurso}

**III - DA PROVA**
{argumentacao_probatoria}

**IV - DOS PEDIDOS**
Requer-se:
a) Conhecimento do recurso
b) Reforma da sentença
c) {pedido_especifico}

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Rescisão Trabalhista": """**TERMO DE RESCISÃO DE CONTRATO DE TRABALHO**

**EMPREGADOR:** {nome_empresa}
**EMPREGADO:** {nome_empregado}

**I - DOS DADOS**
Admissão: {data_admissao}
Demissão: {data_demissao}
Função: {cargo_funcao}
Salário: R$ {ultimo_salario}

**II - DO TIPO DE RESCISÃO**
{tipo_rescisao}

**III - DAS VERBAS**
- Saldo de salário: R$ {saldo_salario}
- Aviso prévio: R$ {aviso_previo}
- 13º salário: R$ {decimo_terceiro}
- Férias + 1/3: R$ {ferias_proporcionais}
- FGTS: R$ {saque_fgts}

**TOTAL LÍQUIDO:** R$ {valor_liquido}

{local}, {data}
_____________________          _____________________
{empregado}                   {empregador}""",

        "Teletrabalho": """**TERMO ADITIVO - TELETRABALHO**

**EMPREGADOR:** {nome_empresa}
**EMPREGADO:** {nome_empregado}

**CLÁUSULA 1ª - DA MODALIDADE**
Alteração para regime de teletrabalho conforme Lei 14.442/22.

**CLÁUSULA 2ª - DAS ATIVIDADES**
{descricao_atividades_remotas}

**CLÁUSULA 3ª - DO LOCAL**
Trabalho será prestado em {endereco_home_office}.

**CLÁUSULA 4ª - DOS EQUIPAMENTOS**
{responsabilidade_equipamentos}

**CLÁUSULA 5ª - DA JORNADA**
{definicao_jornada_remota}

**CLÁUSULA 6ª - DO CONTROLE**
{forma_controle_atividades}

{local}, {data}
_____________________          _____________________
{empregado}                   {empregador}""",

        # DIREITO DO CONSUMIDOR
        "Acordo Consumerista": """**TERMO DE ACORDO CONSUMERISTA**

**CONSUMIDOR:** {nome_consumidor}
**FORNECEDOR:** {nome_fornecedor}

**CLÁUSULA 1ª - DO OBJETO**
Acordo sobre {objeto_reclamacao}.

**CLÁUSULA 2ª - DA TRANSAÇÃO**
O fornecedor se compromete a:
a) {obrigacao_1}
b) {obrigacao_2}

**CLÁUSULA 3ª - DO VALOR**
Pagamento de R$ {valor_acordo} a título de {natureza_pagamento}.

**CLÁUSULA 4ª - DA QUITAÇÃO**
Quitação mútua das obrigações.

{local}, {data}
_____________________          _____________________
{consumidor}                  {fornecedor}""",

        "Ação de Indenização CDC": """**AÇÃO DE INDENIZAÇÃO - CDC**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_consumidor} propõe ação contra {nome_fornecedor}.

**I - DA RELAÇÃO DE CONSUMO**
Relação de consumo caracterizada pela aquisição de {produto_servico}.

**II - DO VÍCIO/DEFEITO**
{descricao_problema}

**III - DA RESPONSABILIDADE**
Responsabilidade objetiva do fornecedor (art. 14, CDC).

**IV - DOS DANOS**
a) Danos materiais: R$ {valor_material}
b) Danos morais: R$ {valor_moral}

**V - DOS PEDIDOS**
Condenação ao pagamento de indenização.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Defesa do Fornecedor": """**CONTESTAÇÃO - DEFESA DO FORNECEDOR**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_fornecedor} contesta a ação consumerista.

**I - PRELIMINARES**
a) {preliminar_1}
b) {preliminar_2}

**II - DO MÉRITO**
a) Cumprimento das obrigações contratuais
b) Inexistência de vício no produto/serviço
c) Ausência de danos

**III - DOS PEDIDOS**
Requer-se a total improcedência da ação.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "E-commerce": """**TERMOS DE USO - E-COMMERCE**

**EMPRESA:** {nome_empresa}
**SITE:** {endereco_site}

**1. OBJETO**
Regras para compras no site {endereco_site}.

**2. PRODUTOS**
{descricao_produtos}

**3. PREÇOS E PAGAMENTO**
{politica_precos_pagamento}

**4. ENTREGA**
{politica_entrega}

**5. DIREITO DE ARREPENDIMENTO**
Conforme art. 49 do CDC, prazo de 7 dias.

**6. PRIVACIDADE**
{politica_privacidade}

**7. RESPONSABILIDADES**
{limitacoes_responsabilidade}

Atualizado em: {data_atualizacao}""",

        "PROCON": """**NOTIFICAÇÃO PROCON**

**NOTIFICADO:** {nome_fornecedor}
**CONSUMIDOR:** {nome_consumidor}

**I - DOS FATOS**
O consumidor relata {descricao_reclamacao}.

**II - DA LEGISLAÇÃO**
Possível violação aos artigos {artigos_cdc} do CDC.

**III - DA NOTIFICAÇÃO**
Fica notificado a:
a) Resolver a reclamação em {prazo_resposta} dias
b) Apresentar defesa fundamentada

**IV - DAS SANÇÕES**
Em caso de não atendimento: {sancoes_aplicaveis}.

{local}, {data}
{nome_fiscal_procon}
Fiscal do PROCON""",

        "Planos de Saúde": """**AÇÃO CONTRA PLANO DE SAÚDE**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_beneficiario} propõe ação contra {nome_operadora}.

**I - DO CONTRATO**
Contrato de plano de saúde nº {numero_contrato}.

**II - DA NEGATIVA**
A operadora negou cobertura para {procedimento_negado}.

**III - DA ABUSIVIDADE**
A negativa é abusiva pois:
a) {fundamento_abusividade_1}
b) {fundamento_abusividade_2}

**IV - DOS PEDIDOS**
Requer-se:
a) Autorização do procedimento
b) Indenização por danos morais

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Recall": """**NOTIFICAÇÃO DE RECALL**

**FABRICANTE:** {nome_fabricante}
**PRODUTO:** {nome_produto}

**I - DA IDENTIFICAÇÃO**
Produto: {descricao_produto}
Modelo: {modelo_produto}
Lote: {numero_lote}

**II - DO PROBLEMA**
{descricao_defeito}

**III - DOS RISCOS**
{riscos_seguranca}

**IV - DAS AÇÕES**
Os consumidores devem:
a) {acao_consumidor_1}
b) {acao_consumidor_2}

**V - DO CONTATO**
{dados_contato_recall}

{local}, {data}
{nome_responsavel}
Responsável Técnico""",

        # RECUPERAÇÃO DE CRÉDITO
        "Cobrança Extrajudicial": """**NOTIFICAÇÃO DE COBRANÇA EXTRAJUDICIAL**

**CREDOR:** {nome_credor}
**DEVEDOR:** {nome_devedor}

**I - DO DÉBITO**
Débito em aberto referente a {origem_divida}.
Valor original: R$ {valor_original}
Valor atualizado: R$ {valor_atualizado}

**II - DO VENCIMENTO**
Vencimento em {data_vencimento}.

**III - DA COBRANÇA**
Fica notificado a quitar o débito em {prazo_pagamento} dias.

**IV - DAS CONSEQUÊNCIAS**
Em caso de não pagamento:
a) Inclusão nos órgãos de proteção ao crédito
b) Cobrança judicial

{local}, {data}
{nome_credor}""",

        "Execução de Título": """**EXECUÇÃO DE TÍTULO EXTRAJUDICIAL**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_exequente} propõe execução contra {nome_executado}.

**I - DO TÍTULO EXECUTIVO**
{tipo_titulo} no valor de R$ {valor_titulo}.

**II - DO DÉBITO ATUALIZADO**
Valor principal: R$ {valor_principal}
Juros: R$ {valor_juros}
Correção: R$ {valor_correcao}
Total: R$ {valor_total}

**III - DOS PEDIDOS**
Requer-se:
a) Citação para pagamento
b) Penhora de bens
c) Avaliação e hasta pública

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Falência": """**PEDIDO DE FALÊNCIA**

**Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a),**

{nome_requerente} requer a falência de {nome_empresa}.

**I - DOS FATOS**
A empresa encontra-se em estado de insolvência caracterizado por:
a) {fato_insolvencia_1}
b) {fato_insolvencia_2}

**II - DO CRÉDITO**
Crédito líquido e certo de R$ {valor_credito}.

**III - DA IMPONTUALIDADE**
Protesto por falta de pagamento em {data_protesto}.

**IV - DOS PEDIDOS**
Requer-se a decretação da falência.

{local}, {data}
{nome_advogado} - OAB/{estado} nº {numero_oab}""",

        "Leilão Judicial": """**EDITAL DE LEILÃO JUDICIAL**

**PROCESSO:** {numero_processo}
**JUÍZO:** {vara_juizo}

**I - DOS BENS**
{descricao_bens_leilao}

**II - DA AVALIAÇÃO**
Valor da avaliação: R$ {valor_avaliacao}

**III - DAS CONDITIONS**
- 1ª Praça: {data_primeira_praca}
- 2ª Praça: {data_segunda_praca}
- Lance mínimo: R$ {lance_minimo}

**IV - DO PAGAMENTO**
{condicoes_pagamento}

**V - DAS INFORMAÇÕES**
{informacoes_adicionais}

{local}, {data}
{nome_leiloeiro}
Leiloeiro Oficial""",

        "Penhora de Bens": """**AUTO DE PENHORA**

**PROCESSO:** {numero_processo}
**EXEQUENTE:** {nome_exequente}
**EXECUTADO:** {nome_executado}

**I - DA PENHORA**
Fica penhorado o bem {descricao_bem}.

**II - DA AVALIAÇÃO**
Valor estimado: R$ {valor_avaliacao}

**III - DO DEPOSITÁRIO**
Nomeado depositário: {nome_depositario}

**IV - DAS OBRIGAÇÕES**
O depositário obriga-se a:
a) {obrigacao_depositario_1}
b) {obrigacao_depositario_2}

{local}, {data}
{nome_oficial_justica}
Oficial de Justiça""",
    }

    with engine.connect() as conn:
        for nome, conteudo in templates_content.items():
            query = text("""
                UPDATE template_juridico 
                SET template_conteudo = :conteudo,
                    modificado_em = :data
                WHERE nome = :nome AND ativo = true
            """)
            
            result = conn.execute(query, {
                'conteudo': conteudo,
                'nome': nome,
                'data': datetime.now()
            })
            
            if result.rowcount > 0:
                print(f"✅ Template '{nome}' atualizado")
            else:
                print(f"⚠️  Template '{nome}' não encontrado")
        
        conn.commit()
        print(f"\n🎉 Total de {len(templates_content)} templates processados!")

if __name__ == "__main__":
    update_all_templates()