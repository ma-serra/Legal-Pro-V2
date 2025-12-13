"""
Script para popular templates com conteúdo jurídico completo e autêntico
Adiciona texto padrão completo que documentos legais reais devem conter
"""

import os
import sys
from datetime import datetime
from main import app, db
from models import LegalTemplatesJuridicos, LegalAreaJuridica

# Conteúdo jurídico completo e autêntico para templates
TEMPLATES_CONTEUDO_COMPLETO = {
    "Petição Inicial - Ação Indenizatória": """
<div class="documento-juridico">
<div style="text-align: center; margin-bottom: 30px;">
<h3>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA [VARA CÍVEL]</h3>
<h4>[COMARCA - UF]</h4>
</div>

<p style="text-align: justify; text-indent: 30px; margin: 20px 0;">
<strong>[NOME COMPLETO DO AUTOR]</strong>, [nacionalidade], [estado civil], [profissão], portador do RG nº [número], inscrito no CPF/MF sob o nº [número], residente e domiciliado na [endereço completo], por intermédio de seu advogado que esta subscreve, vem, respeitosamente, à presença de Vossa Excelência, propor a presente
</p>

<h2 style="text-align: center; margin: 30px 0; text-decoration: underline;">
AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS
</h2>

<p style="text-align: justify; text-indent: 30px;">
em face de <strong>[NOME COMPLETO DO RÉU]</strong>, [qualificação completa do réu: nacionalidade, estado civil, profissão, RG, CPF, endereço], pelos fatos e fundamentos jurídicos a seguir expostos:
</p>

<h3 style="text-align: center; margin: 25px 0;">I - DOS FATOS</h3>

<p style="text-align: justify; text-indent: 30px;">
1. No dia [data por extenso], o Requerente foi vítima de [descrição detalhada do fato gerador do dano], conforme documentos que instruem a presente inicial.
</p>

<p style="text-align: justify; text-indent: 30px;">
2. A conduta ilícita praticada pelo Requerido causou ao Autor [especificar os danos materiais com valores e documentos comprobatórios], além de intenso sofrimento psíquico, constrangimento, humilhação e abalo emocional.
</p>

<p style="text-align: justify; text-indent: 30px;">
3. Os danos materiais perfazem o montante de R$ [valor por extenso] ([valor em números]), devidamente comprovados pelos documentos anexos, incluindo [especificar: despesas médicas, danos ao patrimônio, lucros cessantes, etc.].
</p>

<p style="text-align: justify; text-indent: 30px;">
4. Quanto aos danos morais, o Autor experimentou profundo sofrimento psíquico, vergonha, constrangimento e humilhação perante terceiros, situação que extrapola o mero dissabor cotidiano, caracterizando inequívoca lesão à dignidade da pessoa humana.
</p>

<h3 style="text-align: center; margin: 25px 0;">II - DO DIREITO</h3>

<p style="text-align: justify; text-indent: 30px;">
5. O presente caso configura hipótese de responsabilidade civil, nos termos do artigo 927 do Código Civil Brasileiro: "Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo."
</p>

<p style="text-align: justify; text-indent: 30px;">
6. Para caracterização da responsabilidade civil, necessários se fazem três elementos: a) conduta humana (ação ou omissão); b) nexo causal; c) dano ou prejuízo. Todos estes elementos encontram-se presentes no caso em tela.
</p>

<p style="text-align: justify; text-indent: 30px;">
7. A Constituição Federal de 1988, em seu artigo 5º, incisos V e X, assegura o direito à indenização por dano moral: "V - é assegurado o direito de resposta, proporcional ao agravo, além da indenização por dano material, moral ou à imagem; X - são invioláveis a intimidade, a vida privada, a honra e a imagem das pessoas, assegurado o direito a indenização pelo dano material ou moral decorrente de sua violação."
</p>

<p style="text-align: justify; text-indent: 30px;">
8. O Superior Tribunal de Justiça já pacificou o entendimento de que o dano moral é passível de reparação, independentemente de prova do prejuízo, bastando a demonstração do fato que gerou a dor, o sofrimento, sentimento de reprovação, e de diminuição no conceito público.
</p>

<p style="text-align: justify; text-indent: 30px;">
9. Quanto ao valor da indenização, deve ser arbitrado com moderação, considerando-se a extensão do dano, as condições econômicas das partes e o caráter pedagógico da medida, de modo a coibir a reiteração da conduta lesiva.
</p>

<h3 style="text-align: center; margin: 25px 0;">III - DO VALOR DA CAUSA</h3>

<p style="text-align: justify; text-indent: 30px;">
10. Atribui-se à presente causa o valor de R$ [valor por extenso] ([valor em números]), sendo R$ [valor] a título de danos materiais e R$ [valor] a título de danos morais.
</p>

<h3 style="text-align: center; margin: 25px 0;">IV - DOS PEDIDOS</h3>

<p style="text-align: justify; text-indent: 30px;">
Diante do exposto, respeitosamente requer-se a Vossa Excelência:
</p>

<p style="margin-left: 50px;">
a) A citação do Requerido para responder aos termos da presente ação, no prazo legal, sob pena de revelia;
</p>

<p style="margin-left: 50px;">
b) A procedência total dos pedidos, condenando-se o Requerido ao pagamento de indenização por danos materiais no valor de R$ [valor por extenso] ([valor em números]);
</p>

<p style="margin-left: 50px;">
c) A condenação do Requerido ao pagamento de indenização por danos morais no valor não inferior a R$ [valor por extenso] ([valor em números]);
</p>

<p style="margin-left: 50px;">
d) A condenação do Requerido ao pagamento das custas processuais e honorários advocatícios, nos termos do artigo 85 do Código de Processo Civil;
</p>

<p style="margin-left: 50px;">
e) A aplicação de juros legais e correção monetária sobre os valores das condenações, desde a data do evento danoso até o efetivo pagamento;
</p>

<p style="margin-left: 50px;">
f) A produção de todas as provas em direito admitidas, especialmente prova documental, testemunhal e pericial, se necessário;
</p>

<p style="margin-left: 50px;">
g) A concessão dos benefícios da justiça gratuita, caso aplicável.
</p>

<p style="text-align: center; margin: 30px 0;">
<strong>Termos em que pede deferimento.</strong>
</p>

<div style="text-align: right; margin-top: 50px;">
<p>[Local], [data por extenso].</p>
<p style="margin-top: 40px;">
_________________________________<br>
<strong>[Nome do Advogado]</strong><br>
OAB/[UF] [número]
</p>
</div>

<p style="text-align: center; margin-top: 30px; font-size: 12px;">
<strong>ROL DE DOCUMENTOS ANEXOS:</strong><br>
1. Documento de identidade e CPF do Autor;<br>
2. Comprovante de residência;<br>
3. [Documentos específicos que comprovam os fatos];<br>
4. [Documentos que comprovam os danos materiais];<br>
5. Procuração ad judicia.
</p>
</div>
""",

    "Contestação Civil": """
<div class="documento-juridico">
<div style="text-align: center; margin-bottom: 30px;">
<h3>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA [VARA CÍVEL]</h3>
<h4>[COMARCA - UF]</h4>
</div>

<p style="text-align: justify; text-indent: 30px; margin: 20px 0;">
<strong>[NOME COMPLETO DO RÉU]</strong>, [nacionalidade], [estado civil], [profissão], portador do RG nº [número], inscrito no CPF/MF sob o nº [número], residente e domiciliado na [endereço completo], por intermédio de seu advogado que esta subscreve, vem, respeitosamente, à presença de Vossa Excelência, nos autos da ação movida por [NOME DO AUTOR], apresentar a presente
</p>

<h2 style="text-align: center; margin: 30px 0; text-decoration: underline;">
CONTESTAÇÃO
</h2>

<p style="text-align: justify; text-indent: 30px;">
pelas razões de fato e de direito a seguir expostas:
</p>

<h3 style="text-align: center; margin: 25px 0;">I - DAS PRELIMINARES</h3>

<h4 style="margin: 20px 0;">1.1 - DA INÉPCIA DA PETIÇÃO INICIAL</h4>
<p style="text-align: justify; text-indent: 30px;">
A petição inicial não preenche os requisitos do artigo 319 do Código de Processo Civil, sendo inepta por [especificar: falta de causa de pedir, pedido indeterminado, ausência de documentos indispensáveis, etc.], razão pela qual deve ser indeferida liminarmente ou extinto o processo sem resolução do mérito, nos termos do artigo 485, I, do CPC.
</p>

<h4 style="margin: 20px 0;">1.2 - DA FALTA DE INTERESSE DE AGIR</h4>
<p style="text-align: justify; text-indent: 30px;">
O Autor não possui interesse de agir, uma vez que [especificar razões: inexistência de lesão, adequação da via eleita, necessidade da tutela jurisdicional], faltando-lhe, portanto, uma das condições da ação, devendo o processo ser extinto sem resolução do mérito, nos termos do artigo 485, VI, do Código de Processo Civil.
</p>

<h4 style="margin: 20px 0;">1.3 - DA ILEGITIMIDADE PASSIVA</h4>
<p style="text-align: justify; text-indent: 30px;">
O Contestante não possui legitimidade para figurar no polo passivo da presente demanda, porquanto [especificar razões da ilegitimidade], devendo ser reconhecida a ilegitimidade passiva e, consequentemente, a extinção do processo sem resolução do mérito, nos termos do artigo 485, VI, do CPC.
</p>

<h4 style="margin: 20px 0;">1.4 - DA PRESCRIÇÃO</h4>
<p style="text-align: justify; text-indent: 30px;">
Encontra-se prescrita a pretensão do Autor, tendo em vista que [especificar o prazo prescricional aplicável e quando se iniciou a contagem], nos termos do artigo [artigo específico] do Código Civil, razão pela qual deve ser reconhecida a prescrição e julgado improcedente o pedido.
</p>

<h3 style="text-align: center; margin: 25px 0;">II - DO MÉRITO</h3>

<h4 style="margin: 20px 0;">2.1 - DA AUSÊNCIA DOS PRESSUPOSTOS DA RESPONSABILIDADE CIVIL</h4>
<p style="text-align: justify; text-indent: 30px;">
Não estão presentes os pressupostos necessários à configuração da responsabilidade civil, quais sejam: conduta ilícita, dano e nexo causal. O Contestante não praticou qualquer ato ilícito que pudesse ensejar reparação, conforme será demonstrado a seguir.
</p>

<h4 style="margin: 20px 0;">2.2 - DA VERSÃO DOS FATOS</h4>
<p style="text-align: justify; text-indent: 30px;">
Contrariamente ao alegado na inicial, os fatos ocorreram da seguinte forma: [narrar detalhadamente a versão dos fatos segundo a ótica do réu, refutando as alegações do autor].
</p>

<p style="text-align: justify; text-indent: 30px;">
Os documentos anexos à presente contestação comprovam que [especificar o que os documentos comprovam e como refutam as alegações do autor].
</p>

<h4 style="margin: 20px 0;">2.3 - DA INEXISTÊNCIA DE DANOS MATERIAIS</h4>
<p style="text-align: justify; text-indent: 30px;">
O Autor não comprovou a existência de danos materiais, não havendo nos autos qualquer documento idôneo que demonstre os prejuízos alegados. Os supostos danos não guardam relação com a conduta do Contestante, inexistindo nexo causal entre a conduta e o resultado.
</p>

<h4 style="margin: 20px 0;">2.4 - DA INEXISTÊNCIA DE DANOS MORAIS</h4>
<p style="text-align: justify; text-indent: 30px;">
Não houve qualquer lesão à esfera extrapatrimonial do Autor. O alegado dano moral não passou de mero dissabor cotidiano, aborrecimento comum da vida em sociedade, insuscetível de gerar direito à indenização. Conforme pacífico entendimento jurisprudencial, nem todo constrangimento ou aborrecimento gera direito à reparação por danos morais.
</p>

<h4 style="margin: 20px 0;">2.5 - DA EXCLUDENTE DE RESPONSABILIDADE</h4>
<p style="text-align: justify; text-indent: 30px;">
Ainda que se admita a ocorrência de algum dano, a responsabilidade do Contestante está excluída por [especificar: caso fortuito, força maior, fato de terceiro, culpa exclusiva da vítima], nos termos do artigo 393 do Código Civil.
</p>

<h4 style="margin: 20px 0;">2.6 - DO VALOR EXCESSIVO PLEITEADO</h4>
<p style="text-align: justify; text-indent: 30px;">
Subsidiariamente, caso não acolhidas as preliminares e argumentos de mérito, os valores pleiteados são excessivos e não guardam proporcionalidade com os supostos danos, devendo ser reduzidos para montante compatível com a extensão do alegado prejuízo.
</p>

<h3 style="text-align: center; margin: 25px 0;">III - DOS PEDIDOS CONTRATUAIS</h3>

<p style="text-align: justify; text-indent: 30px;">
Diante do exposto, respeitosamente requer-se a Vossa Excelência:
</p>

<p style="margin-left: 50px;">
a) O acolhimento das preliminares arguidas, com a consequente extinção do processo sem resolução do mérito;
</p>

<p style="margin-left: 50px;">
b) Subsidiariamente, o reconhecimento da prescrição da pretensão do Autor;
</p>

<p style="margin-left: 50px;">
c) Alternativamente, a total improcedência dos pedidos formulados na inicial;
</p>

<p style="margin-left: 50px;">
d) A condenação do Autor ao pagamento das custas processuais e honorários advocatícios, nos termos do artigo 85 do Código de Processo Civil;
</p>

<p style="margin-left: 50px;">
e) A produção de todas as provas em direito admitidas, especialmente prova documental, testemunhal e pericial;
</p>

<p style="margin-left: 50px;">
f) A intimação do Autor para especificar as provas que pretende produzir, sob pena de preclusão.
</p>

<p style="text-align: center; margin: 30px 0;">
<strong>Termos em que pede deferimento.</strong>
</p>

<div style="text-align: right; margin-top: 50px;">
<p>[Local], [data por extenso].</p>
<p style="margin-top: 40px;">
_________________________________<br>
<strong>[Nome do Advogado]</strong><br>
OAB/[UF] [número]
</p>
</div>

<p style="text-align: center; margin-top: 30px; font-size: 12px;">
<strong>ROL DE DOCUMENTOS ANEXOS:</strong><br>
1. Documento de identidade e CPF do Contestante;<br>
2. Comprovante de residência;<br>
3. [Documentos que comprovam a versão dos fatos];<br>
4. [Documentos que refutam as alegações do autor];<br>
5. Procuração ad judicia.
</p>
</div>
""",

    "Contrato de Compra e Venda": """
<div class="documento-juridico">
<h2 style="text-align: center; margin: 30px 0;">CONTRATO DE COMPRA E VENDA</h2>

<p style="text-align: justify; text-indent: 30px;">
Pelo presente instrumento particular de contrato de compra e venda, de um lado <strong>[NOME COMPLETO DO VENDEDOR]</strong>, [nacionalidade], [estado civil], [profissão], portador do RG nº [número], inscrito no CPF/MF sob o nº [número], residente e domiciliado na [endereço completo], doravante denominado <strong>VENDEDOR</strong>, e de outro lado <strong>[NOME COMPLETO DO COMPRADOR]</strong>, [qualificação completa], doravante denominado <strong>COMPRADOR</strong>, têm entre si justo e acordado o seguinte:
</p>

<h3 style="margin: 25px 0;">CLÁUSULA PRIMEIRA - DO OBJETO</h3>
<p style="text-align: justify; text-indent: 30px;">
O VENDEDOR vende ao COMPRADOR o bem descrito como: [descrição detalhada do bem: marca, modelo, ano, características específicas, número de série, etc.], doravante denominado simplesmente <strong>BEM</strong>.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA SEGUNDA - DO PREÇO E FORMA DE PAGAMENTO</h3>
<p style="text-align: justify; text-indent: 30px;">
O preço total da venda é de R$ [valor por extenso] ([valor em números]), que será pago da seguinte forma:
</p>
<p style="margin-left: 50px;">
a) R$ [valor] ([valor por extenso]) na data da assinatura deste contrato, a título de sinal e princípio de pagamento;<br>
b) O saldo remanescente de R$ [valor] ([valor por extenso]) será pago em [número] parcelas mensais e consecutivas de R$ [valor] ([valor por extenso]) cada, vencendo a primeira em [data] e as demais no mesmo dia dos meses subsequentes.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA TERCEIRA - DA ENTREGA DO BEM</h3>
<p style="text-align: justify; text-indent: 30px;">
A entrega do BEM será realizada na data de [data], no local [endereço], correndo por conta do [VENDEDOR/COMPRADOR] as despesas de transporte e entrega.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA QUARTA - DAS GARANTIAS</h3>
<p style="text-align: justify; text-indent: 30px;">
O VENDEDOR garante que o BEM encontra-se livre e desembaraçado de qualquer ônus, gravame, hipoteca, penhor, alienação fiduciária ou qualquer outro encargo, respondendo pela evicção na forma da lei.
</p>

<p style="text-align: justify; text-indent: 30px;">
O BEM é vendido no estado em que se encontra, tendo o COMPRADOR pleno conhecimento de suas condições, renunciando a qualquer reclamação posterior quanto a vícios aparentes.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA QUINTA - DA TRANSFERÊNCIA DE PROPRIEDADE</h3>
<p style="text-align: justify; text-indent: 30px;">
A propriedade do BEM somente será transferida ao COMPRADOR após o pagamento integral do preço convencionado, permanecendo o BEM em poder do COMPRADOR na qualidade de depositário, nos termos do artigo 1.267 do Código Civil.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA SEXTA - DO INADIMPLEMENTO</h3>
<p style="text-align: justify; text-indent: 30px;">
No caso de inadimplemento de qualquer parcela por mais de [número] dias corridos após o vencimento, incidirão sobre o valor em atraso:
</p>
<p style="margin-left: 50px;">
a) Multa de [percentual]% sobre o valor da parcela em atraso;<br>
b) Juros de mora de [percentual]% ao mês, pro rata die;<br>
c) Correção monetária pelo índice [especificar índice], desde o vencimento até o efetivo pagamento.
</p>

<p style="text-align: justify; text-indent: 30px;">
O inadimplemento superior a [número] dias consecutivos facultará ao VENDEDOR considerar rescindido o presente contrato, independentemente de notificação judicial ou extrajudicial, podendo exigir a devolução imediata do BEM.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA SÉTIMA - DA RESCISÃO</h3>
<p style="text-align: justify; text-indent: 30px;">
Em caso de rescisão por inadimplemento do COMPRADOR, este perderá o direito às parcelas já pagas, que ficará com o VENDEDOR a título de perdas e danos e pelo uso do BEM, sem prejuízo de outras cominações legais.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA OITAVA - DO SEGURO</h3>
<p style="text-align: justify; text-indent: 30px;">
O COMPRADOR obriga-se a manter o BEM devidamente segurado contra roubo, furto, incêndio e danos, em valor não inferior ao saldo devedor, indicando o VENDEDOR como beneficiário até a quitação integral do contrato.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA NONA - DAS DESPESAS</h3>
<p style="text-align: justify; text-indent: 30px;">
Todas as despesas decorrentes da transferência de propriedade, tais como taxas, impostos, cartório e documentação, correrão por conta do COMPRADOR.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA DÉCIMA - DO FORO</h3>
<p style="text-align: justify; text-indent: 30px;">
As partes elegem o foro da Comarca de [cidade-UF] para dirimir quaisquer questões oriundas do presente contrato, renunciando a qualquer outro, por mais privilegiado que seja.
</p>

<h3 style="margin: 25px 0;">CLÁUSULA DÉCIMA PRIMEIRA - DAS DISPOSIÇÕES GERAIS</h3>
<p style="text-align: justify; text-indent: 30px;">
Este contrato obriga as partes e seus sucessores a qualquer título. Qualquer alteração deverá ser feita por escrito e assinada por ambas as partes. O presente contrato está sujeito às normas do Código Civil Brasileiro e legislação correlata.
</p>

<p style="text-align: justify; text-indent: 30px;">
E por estarem assim justas e contratadas, assinam o presente instrumento em [número] vias de igual teor e forma, na presença de duas testemunhas abaixo qualificadas.
</p>

<div style="text-align: center; margin: 50px 0;">
<p>[Local], [data por extenso].</p>
</div>

<div style="margin: 50px 0;">
<p>_________________________________<br>
<strong>[Nome do Vendedor]</strong><br>
VENDEDOR</p>

<p style="margin-top: 30px;">_________________________________<br>
<strong>[Nome do Comprador]</strong><br>
COMPRADOR</p>
</div>

<div style="margin: 50px 0;">
<h4>TESTEMUNHAS:</h4>
<p>1. _________________________________<br>
Nome: [Nome completo]<br>
RG: [número] CPF: [número]</p>

<p>2. _________________________________<br>
Nome: [Nome completo]<br>
RG: [número] CPF: [número]</p>
</div>
</div>
""",

    "Recurso de Apelação": """
<div class="documento-juridico">
<div style="text-align: center; margin-bottom: 30px;">
<h3>EXCELENTÍSSIMO(A) SENHOR(A) DESEMBARGADOR(A) RELATOR(A)</h3>
<h4>EGRÉGIO TRIBUNAL DE JUSTIÇA DO ESTADO DE [UF]</h4>
</div>

<p style="text-align: justify; text-indent: 30px; margin: 20px 0;">
<strong>[NOME COMPLETO DO APELANTE]</strong>, [qualificação completa], nos autos da ação que move contra [NOME DO APELADO], vem, respeitosamente, por seu advogado que esta subscreve, tempestivamente, interpor o presente
</p>

<h2 style="text-align: center; margin: 30px 0; text-decoration: underline;">
RECURSO DE APELAÇÃO
</h2>

<p style="text-align: justify; text-indent: 30px;">
contra a r. sentença de fls. [número], que [descrever sucintamente o dispositivo da sentença], pelos fundamentos a seguir expostos:
</p>

<h3 style="text-align: center; margin: 25px 0;">I - DO CABIMENTO E TEMPESTIVIDADE</h3>

<p style="text-align: justify; text-indent: 30px;">
O presente recurso é cabível, nos termos do artigo 1.009 do Código de Processo Civil, contra sentença que extinguiu o processo com ou sem resolução do mérito, sendo interposto no prazo legal de 15 (quinze) dias, conforme certificado nos autos.
</p>

<h3 style="text-align: center; margin: 25px 0;">II - DOS FATOS</h3>

<p style="text-align: justify; text-indent: 30px;">
Conforme amplamente demonstrado nos autos, [narrar resumidamente os fatos relevantes para o recurso, destacando os pontos que fundamentam a irresignação com a sentença].
</p>

<h3 style="text-align: center; margin: 25px 0;">III - DAS RAZÕES DO RECURSO</h3>

<h4 style="margin: 20px 0;">3.1 - DO EQUÍVOCO NA ANÁLISE DAS PRELIMINARES</h4>
<p style="text-align: justify; text-indent: 30px;">
O MM. Juiz a quo equivocou-se ao [acolher/rejeitar] a preliminar de [especificar a preliminar], uma vez que [fundamentar detalhadamente por que a decisão está incorreta, citando doutrina e jurisprudência].
</p>

<h4 style="margin: 20px 0;">3.2 - DO ERRO NA ANÁLISE DO MÉRITO</h4>
<p style="text-align: justify; text-indent: 30px;">
A r. sentença recorrida incorreu em grave erro ao [especificar o erro cometido na análise do mérito], contrariando frontalmente [citar dispositivos legais, súmulas, jurisprudência aplicável].
</p>

<p style="text-align: justify; text-indent: 30px;">
Com o devido respeito ao entendimento do MM. Juiz a quo, a questão deve ser analisada sob a ótica de [expor o fundamento jurídico correto], conforme pacífico entendimento dos Tribunais Superiores.
</p>

<h4 style="margin: 20px 0;">3.3 - DA VIOLAÇÃO AO DEVIDO PROCESSO LEGAL</h4>
<p style="text-align: justify; text-indent: 30px;">
A decisão recorrida violou o princípio do devido processo legal, ao [especificar como houve a violação: cerceamento de defesa, falta de fundamentação, contradição com as provas dos autos, etc.].
</p>

<h4 style="margin: 20px 0;">3.4 - DA APLICAÇÃO INCORRETA DA LEI</h4>
<p style="text-align: justify; text-indent: 30px;">
O dispositivo legal aplicado não se adequa ao caso concreto, sendo pertinente a aplicação do [artigo correto], que estabelece [transcrever o dispositivo e explicar sua aplicação ao caso].
</p>

<h4 style="margin: 20px 0;">3.5 - DA DIVERGÊNCIA JURISPRUDENCIAL</h4>
<p style="text-align: justify; text-indent: 30px;">
A decisão contraria entendimento consolidado dos Tribunais Superiores, conforme se verifica dos seguintes precedentes:
</p>

<p style="margin-left: 50px;">
"[Transcrever ementa de acórdão do STJ ou STF que fundamente a tese do apelante]" (STJ, REsp nº [número], Rel. Min. [nome], j. [data]).
</p>

<h3 style="text-align: center; margin: 25px 0;">IV - DO PEDIDO DE EFEITO SUSPENSIVO</h3>

<p style="text-align: justify; text-indent: 30px;">
Requer-se a concessão de efeito suspensivo ao presente recurso, uma vez que presentes os requisitos do artigo 1.012, § 1º, do CPC, qual seja, [fundamentar a necessidade do efeito suspensivo: risco de dano grave e de difícil reparação].
</p>

<h3 style="text-align: center; margin: 25px 0;">V - DA JURISPRUDÊNCIA APLICÁVEL</h3>

<p style="text-align: justify; text-indent: 30px;">
O Egrégio Tribunal de Justiça deste Estado já se manifestou sobre a questão:
</p>

<p style="margin-left: 50px;">
"[Transcrever ementa de acórdão do TJUF que fundamente a tese]" (TJUF, Apelação nº [número], Rel. Des. [nome], j. [data]).
</p>

<p style="text-align: justify; text-indent: 30px;">
No mesmo sentido, o Superior Tribunal de Justiça:
</p>

<p style="margin-left: 50px;">
"[Transcrever ementa do STJ]" (STJ, REsp nº [número], Rel. Min. [nome], j. [data]).
</p>

<h3 style="text-align: center; margin: 25px 0;">VI - DOS PEDIDOS</h3>

<p style="text-align: justify; text-indent: 30px;">
Diante do exposto, respeitosamente requer-se ao Egrégio Tribunal:
</p>

<p style="margin-left: 50px;">
a) O conhecimento e recebimento do presente recurso;
</p>

<p style="margin-left: 50px;">
b) A concessão de efeito suspensivo, se o caso;
</p>

<p style="margin-left: 50px;">
c) O provimento do recurso, para [especificar exatamente o que se pretende: reformar a sentença, anular o processo, julgar procedente/improcedente o pedido, etc.];
</p>

<p style="margin-left: 50px;">
d) A inversão dos ônus sucumbenciais, condenando-se o Apelado ao pagamento das custas processuais e honorários advocatícios.
</p>

<p style="text-align: center; margin: 30px 0;">
<strong>Termos em que pede deferimento.</strong>
</p>

<div style="text-align: right; margin-top: 50px;">
<p>[Local], [data por extenso].</p>
<p style="margin-top: 40px;">
_________________________________<br>
<strong>[Nome do Advogado]</strong><br>
OAB/[UF] [número]
</p>
</div>

<h3 style="text-align: center; margin: 25px 0;">CONTRARRAZÕES</h3>

<p style="text-align: justify; text-indent: 30px;">
Caso seja o Apelado intimado para apresentar contrarrazões, desde já as refuta pelos seguintes fundamentos:
</p>

<p style="text-align: justify; text-indent: 30px;">
[Antecipar os possíveis argumentos do apelado e refutá-los preventivamente, demonstrando que não merecem acolhida].
</p>

<p style="text-align: center; margin-top: 30px; font-size: 12px;">
<strong>ROL DE DOCUMENTOS:</strong><br>
1. Cópia da sentença recorrida;<br>
2. Certidão de intimação;<br>
3. Substabelecimento (se houver);<br>
4. Procuração ad judicia.
</p>
</div>
"""
}

def atualizar_templates_com_conteudo_completo():
    """Atualiza templates existentes com conteúdo jurídico completo"""
    try:
        with app.app_context():
            templates_atualizados = 0
            
            for nome_template, conteudo_completo in TEMPLATES_CONTEUDO_COMPLETO.items():
                template = LegalTemplatesJuridicos.query.filter_by(nome=nome_template).first()
                
                if template:
                    template.conteudo_html = conteudo_completo
                    template.data_atualizacao = datetime.now()
                    print(f"✅ Template '{nome_template}' atualizado com conteúdo completo")
                    templates_atualizados += 1
                else:
                    print(f"⚠️ Template '{nome_template}' não encontrado no banco")
            
            db.session.commit()
            print(f"\n✅ {templates_atualizados} templates atualizados com conteúdo jurídico completo!")
            
            return templates_atualizados
            
    except Exception as e:
        print(f"❌ Erro ao atualizar templates: {str(e)}")
        db.session.rollback()
        return 0

if __name__ == "__main__":
    print("🔄 Iniciando atualização de templates com conteúdo jurídico completo...")
    resultado = atualizar_templates_com_conteudo_completo()
    print(f"\n📊 Resultado: {resultado} templates atualizados com texto padrão completo")