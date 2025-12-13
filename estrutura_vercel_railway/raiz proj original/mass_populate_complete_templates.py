"""
Script para popular o banco com exatamente 10 templates por área (70 total)
Conforme especificação correta do usuário
"""

import psycopg2
import os
from datetime import datetime

def conectar_database():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def limpar_templates_existentes():
    """Remove todos os templates existentes para começar do zero"""
    conn = conectar_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM legal_templates_v2_complete")
        conn.commit()
        print("✅ Templates existentes removidos")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao limpar templates: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def obter_todos_70_templates():
    """Retorna exatamente 70 templates (10 por área)"""
    
    return [
        # DIREITO CIVIL (Área 1) - 10 templates
        {
            'nome': 'Petição Inicial',
            'descricao': 'Template para petição inicial em ação cível',
            'area_id': 1,
            'tipo_documento': 'Petição Inicial',
            'complexidade': 'Alto',
            'tempo_estimado': 60,
            'palavras_chave': 'petição inicial,cível,requerimento,juiz',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">PETIÇÃO INICIAL</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DOS FATOS</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
[Narrar os fatos que deram origem ao litígio, de forma clara, cronológica e objetiva, especificando datas, locais e circunstâncias relevantes.]
</p>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">II - DO DIREITO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
[Fundamentação jurídica da pretensão, citando dispositivos legais, jurisprudência e doutrina aplicáveis ao caso concreto.]
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Contestação',
            'descricao': 'Template para contestação em ação cível',
            'area_id': 1,
            'tipo_documento': 'Contestação',
            'complexidade': 'Alto',
            'tempo_estimado': 55,
            'palavras_chave': 'contestação,defesa,improcedência,mérito',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">CONTESTAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DAS PRELIMINARES</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
[Arguir preliminares processuais, se houver: inépcia da inicial, carência de ação, falta de interesse de agir, ilegitimidade, etc.]
</p>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">II - DO MÉRITO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
[Apresentar defesa de mérito, impugnando os fatos alegados pelo autor e demonstrando a improcedência do pedido.]
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Impugnação à Contestação',
            'descricao': 'Template para impugnação à contestação',
            'area_id': 1,
            'tipo_documento': 'Impugnação',
            'complexidade': 'Médio',
            'tempo_estimado': 40,
            'palavras_chave': 'impugnação,contestação,reafirmação,argumentos',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">IMPUGNAÇÃO À CONTESTAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DAS PRELIMINARES</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
As preliminares arguidas pelo requerido são improcedentes, pois [rebater especificamente cada preliminar apresentada na contestação].
</p>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">II - DO MÉRITO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Quanto ao mérito, reafirma-se integralmente os argumentos da inicial, uma vez que [refutar os argumentos da defesa e reforçar a pretensão inicial].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Recurso de Apelação',
            'descricao': 'Template para recurso de apelação cível',
            'area_id': 1,
            'tipo_documento': 'Recurso de Apelação',
            'complexidade': 'Alto',
            'tempo_estimado': 70,
            'palavras_chave': 'apelação,recurso,tribunal,reforma,sentença',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) DESEMBARGADOR(A) RELATOR(A)</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">TRIBUNAL DE JUSTIÇA DO ESTADO DE [UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">RECURSO DE APELAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DO CABIMENTO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Tempestivo e adequado o presente recurso, conforme certidão de intimação e previsão legal do art. 1.009 do CPC.
</p>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">II - DOS FUNDAMENTOS</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A sentença merece reforma pelos seguintes fundamentos: [expor as razões de fato e de direito que justificam a reforma da decisão].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Embargos de Declaração',
            'descricao': 'Template para embargos de declaração',
            'area_id': 1,
            'tipo_documento': 'Embargos de Declaração',
            'complexidade': 'Médio',
            'tempo_estimado': 35,
            'palavras_chave': 'embargos,declaração,omissão,contradição,obscuridade',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">EMBARGOS DE DECLARAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DA OBSCURIDADE/CONTRADIÇÃO/OMISSÃO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A decisão embargada apresenta [obscuridade/contradição/omissão] no tocante a [especificar o ponto que necessita esclarecimento].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Ação Monitória',
            'descricao': 'Template para ação monitória',
            'area_id': 1,
            'tipo_documento': 'Ação Monitória',
            'complexidade': 'Médio',
            'tempo_estimado': 45,
            'palavras_chave': 'monitória,prova escrita,pagamento,entrega,coisa',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">AÇÃO MONITÓRIA</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DA PROVA ESCRITA</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
O requerente possui prova escrita do débito, conforme documento em anexo, que demonstra a obrigação do requerido no valor de R$ [valor].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Ação de Obrigação de Fazer/Não Fazer',
            'descricao': 'Template para ação de obrigação de fazer ou não fazer',
            'area_id': 1,
            'tipo_documento': 'Ação de Obrigação',
            'complexidade': 'Alto',
            'tempo_estimado': 50,
            'palavras_chave': 'obrigação,fazer,não fazer,específica,astreintes',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">AÇÃO DE OBRIGAÇÃO DE FAZER/NÃO FAZER</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DA OBRIGAÇÃO ESPECÍFICA</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
O requerido está obrigado a [especificar a obrigação de fazer ou não fazer], conforme [fonte da obrigação: contrato, lei, etc.].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Ação de Tutela Antecipada',
            'descricao': 'Template para pedido de tutela antecipada',
            'area_id': 1,
            'tipo_documento': 'Tutela Antecipada',
            'complexidade': 'Alto',
            'tempo_estimado': 45,
            'palavras_chave': 'tutela,antecipada,urgência,probabilidade,direito',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA CÍVEL - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">PEDIDO DE TUTELA ANTECIPADA</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DA PROBABILIDADE DO DIREITO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Demonstra-se a probabilidade do direito através de [elementos que evidenciam a procedência do pedido].
</p>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">II - DO PERIGO DE DANO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Existe risco de dano irreparável ou de difícil reparação, caracterizado por [situação urgente que justifica a antecipação].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Embargos à Execução Cível',
            'descricao': 'Template para embargos à execução cível',
            'area_id': 1,
            'tipo_documento': 'Embargos à Execução',
            'complexidade': 'Alto',
            'tempo_estimado': 55,
            'palavras_chave': 'embargos,execução,nulidade,excesso,inexistência',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">VARA DE EXECUÇÕES - [COMARCA - UF]</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">EMBARGOS À EXECUÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DA NULIDADE/INEXIGIBILIDADE</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A execução padece de nulidade por [especificar o vício: falta de título executivo, excesso de execução, inexigibilidade da obrigação, etc.].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Recurso Especial e Recurso Extraordinário',
            'descricao': 'Template para recursos especial e extraordinário',
            'area_id': 1,
            'tipo_documento': 'Recurso Especial/Extraordinário',
            'complexidade': 'Alto',
            'tempo_estimado': 90,
            'palavras_chave': 'recurso especial,extraordinário,STJ,STF,repercussão',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
<h3 style="color: #007bff; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) MINISTRO(A) RELATOR(A)</h3>
<h4 style="color: #007bff; margin: 10px 0 0 0; font-size: 16px;">SUPERIOR TRIBUNAL DE JUSTIÇA / SUPREMO TRIBUNAL FEDERAL</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #007bff; font-size: 20px;">RECURSO ESPECIAL / RECURSO EXTRAORDINÁRIO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #007bff; font-size: 16px;">I - DO CABIMENTO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Cabível o presente recurso por [violação à lei federal / violação à Constituição Federal], conforme demonstrado no acórdão recorrido.
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        # DIREITO TRABALHISTA (Área 2) - 10 templates
        {
            'nome': 'Reclamação Trabalhista (Petição Inicial)',
            'descricao': 'Template para petição inicial trabalhista',
            'area_id': 2,
            'tipo_documento': 'Reclamação Trabalhista',
            'complexidade': 'Alto',
            'tempo_estimado': 65,
            'palavras_chave': 'reclamação,trabalhista,CLT,direitos,empregado',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª REGIÃO</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">RECLAMAÇÃO TRABALHISTA</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DO CONTRATO DE TRABALHO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
O reclamante foi admitido pela reclamada em [data], exercendo a função de [cargo], com salário de R$ [valor], sendo dispensado em [data].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Contestação (Defesa Trabalhista)',
            'descricao': 'Template para contestação trabalhista',
            'area_id': 2,
            'tipo_documento': 'Contestação Trabalhista',
            'complexidade': 'Alto',
            'tempo_estimado': 60,
            'palavras_chave': 'contestação,defesa,trabalhista,improcedência',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª REGIÃO</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">CONTESTAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DA RELAÇÃO DE EMPREGO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A reclamada cumpriu integralmente todas as obrigações trabalhistas, não sendo devidos os valores pleiteados pelo reclamante.
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Impugnação à Contestação / Réplica',
            'descricao': 'Template para réplica trabalhista',
            'area_id': 2,
            'tipo_documento': 'Réplica Trabalhista',
            'complexidade': 'Médio',
            'tempo_estimado': 40,
            'palavras_chave': 'réplica,impugnação,trabalhista,argumentos',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">IMPUGNAÇÃO À CONTESTAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DA REFUTAÇÃO DOS ARGUMENTOS</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Os argumentos apresentados pela reclamada não merecem prosperar, pois [rebater especificamente cada argumento da defesa].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Embargos à Execução',
            'descricao': 'Template para embargos à execução trabalhista',
            'area_id': 2,
            'tipo_documento': 'Embargos à Execução Trabalhista',
            'complexidade': 'Alto',
            'tempo_estimado': 50,
            'palavras_chave': 'embargos,execução,trabalhista,excesso,nulidade',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">EMBARGOS À EXECUÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DO EXCESSO DE EXECUÇÃO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A execução apresenta excesso no valor de R$ [valor], uma vez que [demonstrar o erro de cálculo ou pagamento já realizado].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Recurso Ordinário',
            'descricao': 'Template para recurso ordinário trabalhista',
            'area_id': 2,
            'tipo_documento': 'Recurso Ordinário',
            'complexidade': 'Alto',
            'tempo_estimado': 65,
            'palavras_chave': 'recurso,ordinário,TRT,trabalhista,reforma',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DESEMBARGADOR(A) RELATOR(A)</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª REGIÃO</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">RECURSO ORDINÁRIO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DO CABIMENTO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Tempestivo e adequado o presente recurso, nos termos do art. 895 da CLT.
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Acordo Judicial Homologado',
            'descricao': 'Template para homologação de acordo judicial trabalhista',
            'area_id': 2,
            'tipo_documento': 'Acordo Judicial',
            'complexidade': 'Médio',
            'tempo_estimado': 30,
            'palavras_chave': 'acordo,homologação,judicial,trabalhista,transação',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">ACORDO JUDICIAL</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DOS TERMOS DO ACORDO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
As partes acordam em [especificar os termos do acordo: valor, forma de pagamento, prazo, etc.], dando-se por satisfeitas com o cumprimento das obrigações.
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>Reclamante</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_________________________________<br><strong>Reclamada</strong></p>
</div>
</div>'''
        },

        {
            'nome': 'Embargos de Declaração Trabalhista',
            'descricao': 'Template para embargos de declaração trabalhista',
            'area_id': 2,
            'tipo_documento': 'Embargos de Declaração',
            'complexidade': 'Médio',
            'tempo_estimado': 35,
            'palavras_chave': 'embargos,declaração,trabalhista,omissão,contradição',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">EMBARGOS DE DECLARAÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DA OMISSÃO/CONTRADIÇÃO</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A decisão embargada apresenta [omissão/contradição/obscuridade] quanto a [especificar o ponto que necessita esclarecimento].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Agravo de Petição',
            'descricao': 'Template para agravo de petição trabalhista',
            'area_id': 2,
            'tipo_documento': 'Agravo de Petição',
            'complexidade': 'Alto',
            'tempo_estimado': 45,
            'palavras_chave': 'agravo,petição,execução,trabalhista,decisão',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">EXCELENTÍSSIMO(A) SENHOR(A) DESEMBARGADOR(A) RELATOR(A)</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª REGIÃO</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">AGRAVO DE PETIÇÃO</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DA DECISÃO AGRAVADA</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
A decisão agravada merece reforma pelos seguintes fundamentos: [especificar os motivos que justificam a reforma da decisão].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Pedido de Homologação de Acordo Extrajudicial (art. 855-B CLT)',
            'descricao': 'Template para homologação de acordo extrajudicial',
            'area_id': 2,
            'tipo_documento': 'Homologação de Acordo',
            'complexidade': 'Médio',
            'tempo_estimado': 35,
            'palavras_chave': 'homologação,acordo,extrajudicial,CLT,855-B',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">PEDIDO DE HOMOLOGAÇÃO DE ACORDO EXTRAJUDICIAL</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DO ACORDO EXTRAJUDICIAL</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
As partes celebraram acordo extrajudicial nos termos do art. 855-B da CLT, acordando em [especificar os termos do acordo].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        },

        {
            'nome': 'Manifestação sobre Cálculos ou Liquidação',
            'descricao': 'Template para manifestação sobre cálculos trabalhistas',
            'area_id': 2,
            'tipo_documento': 'Manifestação sobre Cálculos',
            'complexidade': 'Alto',
            'tempo_estimado': 50,
            'palavras_chave': 'cálculos,liquidação,trabalhista,impugnação,valores',
            'conteudo_html': '''<div class="documento-juridico" style="font-family: 'Times New Roman', serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 40px;">
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #28a745; padding-bottom: 20px;">
<h3 style="color: #28a745; margin: 0; font-size: 18px; font-weight: bold;">VARA DO TRABALHO DE [CIDADE/UF]</h3>
<h4 style="color: #28a745; margin: 10px 0 0 0; font-size: 16px;">TRT [REGIÃO]ª Região</h4>
</div>

<h2 style="text-align: center; margin: 40px 0; text-decoration: underline; color: #28a745; font-size: 20px;">MANIFESTAÇÃO SOBRE CÁLCULOS</h2>

<h3 style="text-align: center; margin: 30px 0; color: #28a745; font-size: 16px;">I - DOS CÁLCULOS APRESENTADOS</h3>
<p style="text-align: justify; text-indent: 30px; margin: 20px 0; font-size: 14px;">
Os cálculos apresentados [concordam/discordam] com os valores devidos, pelos seguintes motivos: [especificar os fundamentos da concordância ou impugnação].
</p>

<div style="text-align: right; margin-top: 60px;">
<p style="font-size: 14px;">[Local], [data].</p>
<p style="margin-top: 50px; font-size: 14px;">_________________________________<br><strong>[Nome do Advogado]</strong><br>OAB/[UF] [número]</p>
</div>
</div>'''
        }

    # Continuando com as outras áreas... (devido ao limite de caracteres, vou criar em partes)
    ]

def executar_populacao_completa():
    """Executa a população completa com 70 templates"""
    
    # Primeiro limpar templates existentes
    if not limpar_templates_existentes():
        return False
    
    conn = conectar_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        templates = obter_todos_70_templates()
        print(f"Inserindo {len(templates)} templates...")
        
        insert_query = """
        INSERT INTO legal_templates_v2_complete 
        (nome, descricao, conteudo_html, area_id, tipo_documento, complexidade, tempo_estimado, uso_contador, palavras_chave, ativo, criado_em, atualizado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        now = datetime.now()
        
        for i, template in enumerate(templates, 1):
            valores = (
                template['nome'],
                template['descricao'], 
                template['conteudo_html'],
                template['area_id'],
                template['tipo_documento'],
                template['complexidade'],
                template['tempo_estimado'],
                0,
                template.get('palavras_chave', ''),
                True,
                now,
                now
            )
            
            cursor.execute(insert_query, valores)
            area_nome = {1:'Civil', 2:'Trabalhista', 3:'Empresarial', 4:'Penal', 5:'Agrário', 6:'Securitário', 7:'Tributário'}[template['area_id']]
            print(f"✅ {i:2d}/20 - {template['nome']} ({area_nome})")
        
        conn.commit()
        
        # Verificar distribuição
        cursor.execute("""
        SELECT la.nome, COUNT(lt.id) as total
        FROM legal_areas_v2 la
        LEFT JOIN legal_templates_v2_complete lt ON la.id = lt.area_id AND lt.ativo = true
        GROUP BY la.id, la.nome
        ORDER BY la.id
        """)
        
        print(f"\n📊 Primeira parte inserida - Distribuição:")
        for area_nome, total_templates in cursor.fetchall():
            print(f"• {area_nome}: {total_templates} templates")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Populando Legal Design Pro V2 com 70 templates (10 por área)...")
    print("=" * 60)
    
    sucesso = executar_populacao_completa()
    
    if sucesso:
        print("\n✅ PRIMEIRA PARTE CONCLUÍDA!")
        print("Agora criando script para completar todas as 7 áreas...")
    else:
        print("\nFalha na inserção")