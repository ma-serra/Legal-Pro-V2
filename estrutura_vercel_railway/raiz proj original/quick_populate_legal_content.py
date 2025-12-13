"""
Script rápido para atualizar templates com conteúdo jurídico completo
"""

import os
from datetime import datetime
import sqlite3
import psycopg2

# Conteúdo jurídico completo para atualização direta
def update_templates_directly():
    try:
        # Conecta ao PostgreSQL usando a URL do ambiente
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Conteúdo completo para Petição Inicial
        conteudo_peticao = '''<div class="documento-juridico">
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
em face de <strong>[NOME COMPLETO DO RÉU]</strong>, [qualificação completa do réu], pelos fatos e fundamentos jurídicos a seguir expostos:
</p>

<h3 style="text-align: center; margin: 25px 0;">I - DOS FATOS</h3>

<p style="text-align: justify; text-indent: 30px;">
1. No dia [data por extenso], o Requerente foi vítima de [descrição detalhada do fato gerador do dano], conforme documentos que instruem a presente inicial.
</p>

<p style="text-align: justify; text-indent: 30px;">
2. A conduta ilícita praticada pelo Requerido causou ao Autor [especificar os danos materiais com valores], além de intenso sofrimento psíquico, constrangimento, humilhação e abalo emocional.
</p>

<p style="text-align: justify; text-indent: 30px;">
3. Os danos materiais perfazem o montante de R$ [valor por extenso], devidamente comprovados pelos documentos anexos, incluindo [despesas médicas, danos ao patrimônio, lucros cessantes].
</p>

<h3 style="text-align: center; margin: 25px 0;">II - DO DIREITO</h3>

<p style="text-align: justify; text-indent: 30px;">
4. O presente caso configura hipótese de responsabilidade civil, nos termos do artigo 927 do Código Civil: "Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo."
</p>

<p style="text-align: justify; text-indent: 30px;">
5. A Constituição Federal, art. 5º, incisos V e X, assegura indenização por dano moral: "V - é assegurado o direito de resposta, proporcional ao agravo, além da indenização por dano material, moral ou à imagem."
</p>

<h3 style="text-align: center; margin: 25px 0;">III - DOS PEDIDOS</h3>

<p style="text-align: justify; text-indent: 30px;">Diante do exposto, requer-se:</p>
<p style="margin-left: 50px;">
a) A citação do Requerido para responder aos termos da presente ação;<br>
b) A procedência dos pedidos, condenando-se o Requerido ao pagamento de indenização por danos materiais no valor de R$ [valor];<br>
c) A condenação ao pagamento de indenização por danos morais não inferior a R$ [valor];<br>
d) A condenação às custas processuais e honorários advocatícios, nos termos do art. 85 do CPC;<br>
e) A aplicação de juros legais e correção monetária desde a data do evento danoso.
</p>

<p style="text-align: center; margin: 30px 0;"><strong>Termos em que pede deferimento.</strong></p>

<div style="text-align: right; margin-top: 50px;">
<p>[Local], [data por extenso].</p>
<p style="margin-top: 40px;">_________________________________<br>
<strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>

<p style="text-align: center; margin-top: 30px; font-size: 12px;">
<strong>ROL DE DOCUMENTOS ANEXOS:</strong><br>
1. Documento de identidade e CPF do Autor;<br>
2. Comprovante de residência;<br>
3. Documentos que comprovam os fatos;<br>
4. Documentos que comprovam os danos materiais;<br>
5. Procuração ad judicia.
</p>
</div>'''

        # Atualiza a Petição Inicial
        cursor.execute("""
            UPDATE legal_templates_juridicos 
            SET conteudo_html = %s, data_atualizacao = %s 
            WHERE nome = 'Petição Inicial - Ação Indenizatória'
        """, (conteudo_peticao, datetime.now()))
        
        # Conteúdo para Contestação Civil
        conteudo_contestacao = '''<div class="documento-juridico">
<div style="text-align: center; margin-bottom: 30px;">
<h3>EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA [VARA CÍVEL]</h3>
<h4>[COMARCA - UF]</h4>
</div>

<p style="text-align: justify; text-indent: 30px; margin: 20px 0;">
<strong>[NOME COMPLETO DO RÉU]</strong>, [qualificação completa], nos autos da ação movida por [NOME DO AUTOR], vem apresentar a presente
</p>

<h2 style="text-align: center; margin: 30px 0; text-decoration: underline;">CONTESTAÇÃO</h2>

<h3 style="text-align: center; margin: 25px 0;">I - DAS PRELIMINARES</h3>

<h4>1.1 - DA INÉPCIA DA PETIÇÃO INICIAL</h4>
<p style="text-align: justify; text-indent: 30px;">
A petição inicial não preenche os requisitos do artigo 319 do CPC, sendo inepta por [especificar motivo], devendo ser indeferida nos termos do art. 485, I, do CPC.
</p>

<h4>1.2 - DA FALTA DE INTERESSE DE AGIR</h4>
<p style="text-align: justify; text-indent: 30px;">
O Autor não possui interesse de agir, faltando condição da ação, devendo o processo ser extinto sem resolução do mérito.
</p>

<h3 style="text-align: center; margin: 25px 0;">II - DO MÉRITO</h3>

<h4>2.1 - DA AUSÊNCIA DOS PRESSUPOSTOS DA RESPONSABILIDADE CIVIL</h4>
<p style="text-align: justify; text-indent: 30px;">
Não estão presentes os pressupostos da responsabilidade civil: conduta ilícita, dano e nexo causal. O Contestante não praticou ato ilícito.
</p>

<h4>2.2 - DA VERSÃO DOS FATOS</h4>
<p style="text-align: justify; text-indent: 30px;">
Os fatos ocorreram de forma diversa da narrada na inicial: [narrar versão dos fatos segundo o réu].
</p>

<h4>2.3 - DA INEXISTÊNCIA DE DANOS</h4>
<p style="text-align: justify; text-indent: 30px;">
Não houve danos materiais ou morais. O alegado não passou de mero dissabor cotidiano, insuscetível de indenização.
</p>

<h3 style="text-align: center; margin: 25px 0;">III - DOS PEDIDOS</h3>

<p style="text-align: justify; text-indent: 30px;">Requer-se:</p>
<p style="margin-left: 50px;">
a) O acolhimento das preliminares com extinção do processo;<br>
b) A total improcedência dos pedidos;<br>
c) A condenação do Autor às custas e honorários advocatícios.
</p>

<p style="text-align: center; margin: 30px 0;"><strong>Termos em que pede deferimento.</strong></p>

<div style="text-align: right; margin-top: 50px;">
<p>[Local], [data por extenso].</p>
<p style="margin-top: 40px;">_________________________________<br>
<strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''

        cursor.execute("""
            UPDATE legal_templates_juridicos 
            SET conteudo_html = %s, data_atualizacao = %s 
            WHERE nome = 'Contestação Civil'
        """, (conteudo_contestacao, datetime.now()))

        # Conteúdo para Contrato de Compra e Venda
        conteudo_contrato = '''<div class="documento-juridico">
<h2 style="text-align: center; margin: 30px 0;">CONTRATO DE COMPRA E VENDA</h2>

<p style="text-align: justify; text-indent: 30px;">
Pelo presente instrumento, <strong>[NOME DO VENDEDOR]</strong>, [qualificação], denominado VENDEDOR, e <strong>[NOME DO COMPRADOR]</strong>, [qualificação], denominado COMPRADOR, acordam:
</p>

<h3>CLÁUSULA PRIMEIRA - DO OBJETO</h3>
<p style="text-align: justify; text-indent: 30px;">
O VENDEDOR vende ao COMPRADOR: [descrição detalhada do bem].
</p>

<h3>CLÁUSULA SEGUNDA - DO PREÇO</h3>
<p style="text-align: justify; text-indent: 30px;">
O preço é de R$ [valor por extenso], pago: [forma de pagamento].
</p>

<h3>CLÁUSULA TERCEIRA - DA ENTREGA</h3>
<p style="text-align: justify; text-indent: 30px;">
A entrega será em [data] no local [endereço].
</p>

<h3>CLÁUSULA QUARTA - DAS GARANTIAS</h3>
<p style="text-align: justify; text-indent: 30px;">
O VENDEDOR garante que o bem está livre de ônus, respondendo pela evicção.
</p>

<h3>CLÁUSULA QUINTA - DO INADIMPLEMENTO</h3>
<p style="text-align: justify; text-indent: 30px;">
O inadimplemento acarreta multa de [%], juros de [%] ao mês e correção monetária.
</p>

<h3>CLÁUSULA SEXTA - DO FORO</h3>
<p style="text-align: justify; text-indent: 30px;">
Foro da Comarca de [cidade-UF] para dirimir questões.
</p>

<div style="text-align: center; margin: 50px 0;">
<p>[Local], [data].</p>
</div>

<div style="margin: 50px 0;">
<p>_________________________<br><strong>VENDEDOR</strong></p>
<p>_________________________<br><strong>COMPRADOR</strong></p>
</div>

<div>
<h4>TESTEMUNHAS:</h4>
<p>1. _________________________<br>Nome: CPF:</p>
<p>2. _________________________<br>Nome: CPF:</p>
</div>
</div>'''

        cursor.execute("""
            UPDATE legal_templates_juridicos 
            SET conteudo_html = %s, data_atualizacao = %s 
            WHERE nome LIKE '%Compra e Venda%'
        """, (conteudo_contrato, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Templates atualizados com conteúdo jurídico completo!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    update_templates_directly()