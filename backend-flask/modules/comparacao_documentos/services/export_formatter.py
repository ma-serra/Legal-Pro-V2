"""
Serviço de formatação avançada para exportação de documentos de comparação
Responsável por gerar PDFs e DOCX com formatação profissional
"""

import os
import re
import logging
from datetime import datetime
from io import BytesIO

# Imports para DOCX
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn

# Imports para PDF  
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.colors import HexColor, black, red, green
from reportlab.lib import colors

logger = logging.getLogger(__name__)

class ComparacaoExportFormatter:
    """Formatador avançado para exportação de comparações de documentos"""
    
    def __init__(self):
        self.cores_tema = {
            'primary': '#496d79',
            'success': '#00734d', 
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'adicao': '#d1fdd1',  # Verde claro para adições
            'remocao': '#fdd1d1',  # Vermelho claro para remoções
            'texto_normal': '#212529'
        }
    
    def gerar_docx_formatado(self, comparacao, lado='a', incluir_marcacoes=True):
        """
        Gera documento DOCX com formatação profissional aprimorada
        """
        try:
            doc = Document()
            
            # Configurar estilos personalizados
            self._configurar_estilos_docx(doc)
            
            # Cabeçalho principal
            self._adicionar_cabecalho_docx(doc, comparacao)
            
            # Metadados da comparação
            self._adicionar_metadados_docx(doc, comparacao)
            
            # Conteúdo do documento
            html_content = comparacao.resultado_editado_a if lado == 'a' else comparacao.resultado_editado_b
            
            if incluir_marcacoes:
                self._processar_html_com_marcacoes_melhoradas(doc, html_content)
                # Adicionar legenda das marcações
                self._adicionar_legenda_marcacoes_docx(doc)
            else:
                self._processar_html_simples(doc, html_content)
            
            # Análise IA (se disponível)
            if comparacao.analise_ia:
                self._adicionar_analise_ia_docx(doc, comparacao.analise_ia)
            
            # Rodapé
            self._adicionar_rodape_docx(doc, comparacao)
            
            return doc
            
        except Exception as e:
            logger.error(f"Erro ao gerar DOCX formatado: {e}")
            raise
    
    def gerar_pdf_formatado(self, comparacao, lado='a', incluir_marcacoes=True):
        """
        Gera documento PDF com formatação profissional
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2.5*cm,
                bottomMargin=2*cm
            )
            
            # Configurar estilos
            styles = self._configurar_estilos_pdf()
            story = []
            
            # Cabeçalho
            self._adicionar_cabecalho_pdf(story, styles, comparacao)
            
            # Metadados
            self._adicionar_metadados_pdf(story, styles, comparacao)
            
            # Conteúdo
            html_content = comparacao.resultado_editado_a if lado == 'a' else comparacao.resultado_editado_b
            
            if incluir_marcacoes:
                self._processar_html_pdf_com_marcacoes(story, styles, html_content)
                # Legenda das marcações
                self._adicionar_legenda_marcacoes_pdf(story, styles)
            else:
                self._processar_html_pdf_simples(story, styles, html_content)
            
            # Análise IA
            if comparacao.analise_ia:
                self._adicionar_analise_ia_pdf(story, styles, comparacao.analise_ia)
            
            # Construir PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF formatado: {e}")
            raise
    
    def _configurar_estilos_docx(self, doc):
        """Configura estilos personalizados para DOCX"""
        styles = doc.styles
        
        # Estilo para título principal
        if 'Titulo Principal' not in [s.name for s in styles]:
            titulo_style = styles.add_style('Titulo Principal', WD_STYLE_TYPE.PARAGRAPH)
            titulo_style.font.name = 'Arial'
            titulo_style.font.size = Pt(18)
            titulo_style.font.bold = True
            titulo_style.font.color.rgb = RGBColor.from_string(self.cores_tema['primary'].replace('#', ''))
            titulo_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            titulo_style.paragraph_format.space_after = Pt(12)
        
        # Estilo para subtítulos
        if 'Subtitulo' not in [s.name for s in styles]:
            sub_style = styles.add_style('Subtitulo', WD_STYLE_TYPE.PARAGRAPH)
            sub_style.font.name = 'Arial'
            sub_style.font.size = Pt(14)
            sub_style.font.bold = True
            sub_style.font.color.rgb = RGBColor.from_string(self.cores_tema['dark'].replace('#', ''))
            sub_style.paragraph_format.space_before = Pt(12)
            sub_style.paragraph_format.space_after = Pt(6)
        
        # Estilo para metadados
        if 'Metadados' not in [s.name for s in styles]:
            meta_style = styles.add_style('Metadados', WD_STYLE_TYPE.PARAGRAPH)
            meta_style.font.name = 'Arial'
            meta_style.font.size = Pt(11)
            meta_style.font.italic = True
            meta_style.paragraph_format.space_after = Pt(6)
    
    def _configurar_estilos_pdf(self):
        """Configura estilos personalizados para PDF"""
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor(self.cores_tema['primary']),
            alignment=1,  # Centro
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor(self.cores_tema['dark']),
            spaceBefore=12,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Metadados
        styles.add(ParagraphStyle(
            name='Metadados',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.grey,
            spaceAfter=6,
            fontName='Helvetica-Oblique'
        ))
        
        # Conteúdo normal com melhor espaçamento
        styles.add(ParagraphStyle(
            name='ConteudoNormal',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=4,
            fontName='Helvetica',
            leading=16
        ))
        
        # Texto adicionado (verde)
        styles.add(ParagraphStyle(
            name='TextoAdicionado',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#FFFFFF'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#22c55e'),
            borderColor=HexColor('#16a34a'),
            borderWidth=1
        ))
        
        # Texto removido (vermelho)
        styles.add(ParagraphStyle(
            name='TextoRemovido',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#FFFFFF'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#ef4444'),
            borderColor=HexColor('#dc2626'),
            borderWidth=1
        ))
        
        return styles
    
    def _adicionar_cabecalho_profissional_docx(self, doc, comparacao):
        """Adiciona cabeçalho profissional ao documento DOCX"""
        # Título principal
        titulo = doc.add_heading(comparacao.titulo, level=1)
        titulo.style = 'Titulo Principal'
        
        # Subtítulo com área jurídica
        sub_p = doc.add_paragraph()
        sub_p.style = 'Subtitulo'
        sub_p.add_run(f"Análise Comparativa - {comparacao.descricao_area}")
        
        # Linha separadora visual
        doc.add_paragraph("─" * 80)
    
    def _adicionar_metadados_tabela_docx(self, doc, comparacao):
        """Adiciona metadados em formato de tabela profissional"""
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Light Grid Accent 1'
        
        # Cabeçalho da tabela
        cells = table.rows[0].cells
        cells[0].text = "Informação"
        cells[1].text = "Valor"
        
        # Dados
        data = [
            ("Área do Processo", f"{comparacao.descricao_area} ({comparacao.area_processo})"),
            ("Cliente", comparacao.documento_cliente),
            ("Data de Comparação", comparacao.data_comparacao.strftime('%d/%m/%Y às %H:%M')),
            ("ID da Comparação", str(comparacao.id))
        ]
        
        for i, (label, value) in enumerate(data, 1):
            cells = table.rows[i].cells
            cells[0].text = label
            cells[1].text = value
            
        doc.add_paragraph()  # Espaço após tabela
    
    def _processar_html_com_marcacoes_melhoradas(self, doc, html_content):
        """Processa HTML com marcações melhoradas para DOCX"""
        if not html_content:
            doc.add_paragraph("Conteúdo não disponível.")
            return
        
        # Título da seção
        doc.add_heading("Conteúdo do Documento", level=2)
        
        # Processar HTML linha por linha
        linhas = html_content.split('<br>')
        for linha in linhas:
            if not linha.strip():
                continue
                
            p = doc.add_paragraph()
            
            # Verificar marcações de diferenças
            if '<ins>' in linha:
                # Texto adicionado
                texto_limpo = re.sub('<[^>]*>', '', linha)
                run = p.add_run(texto_limpo)
                run.font.color.rgb = RGBColor(0, 115, 77)  # Verde
                run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
                run.bold = True
            elif '<del>' in linha:
                # Texto removido
                texto_limpo = re.sub('<[^>]*>', '', linha)
                run = p.add_run(texto_limpo)
                run.font.color.rgb = RGBColor(220, 53, 69)  # Vermelho
                run.font.highlight_color = WD_COLOR_INDEX.RED
                run.font.strike = True
            else:
                # Texto normal
                texto_limpo = re.sub('<[^>]*>', '', linha)
                p.add_run(texto_limpo)
        
        # Texto com adição
        styles.add(ParagraphStyle(
            name='TextoAdicao',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.cores_tema['success']),
            fontName='Helvetica-Bold',
            backColor=HexColor(self.cores_tema['adicao'])
        ))
        
        # Texto com remoção  
        styles.add(ParagraphStyle(
            name='TextoRemocao',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.cores_tema['danger']),
            fontName='Helvetica',
            backColor=HexColor(self.cores_tema['remocao'])
        ))
        
        return styles
    
    def _adicionar_cabecalho_docx(self, doc, comparacao):
        """Adiciona cabeçalho formatado ao DOCX"""
        # Título principal
        titulo = doc.add_heading(level=1)
        run = titulo.runs[0] if titulo.runs else titulo.add_run()
        run.text = f"Comparação de Documentos: {comparacao.titulo}"
        titulo.style = 'Titulo Principal'
        
        # Linha separadora
        doc.add_paragraph("─" * 80).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _adicionar_cabecalho_pdf(self, story, styles, comparacao):
        """Adiciona cabeçalho formatado ao PDF"""
        story.append(Paragraph(
            f"Comparação de Documentos: {comparacao.titulo}",
            styles['TituloPrincipal']
        ))
        story.append(Spacer(1, 20))
    
    def _adicionar_metadados_docx(self, doc, comparacao):
        """Adiciona metadados formatados ao DOCX"""
        meta_table = doc.add_table(rows=5, cols=2)
        meta_table.style = 'Table Grid'
        
        # Configurar larguras das colunas
        meta_table.columns[0].width = Inches(1.5)
        meta_table.columns[1].width = Inches(4.5)
        
        # Preencher dados
        dados = [
            ('Área Jurídica:', f"{comparacao.descricao_area} ({comparacao.area_processo})"),
            ('Data da Comparação:', comparacao.data_comparacao.strftime('%d/%m/%Y %H:%M')),
            ('Cliente/Processo:', comparacao.documento_cliente or 'Não informado'),
            ('Usuário:', getattr(comparacao, 'created_by', None).username if getattr(comparacao, 'created_by', None) else 'Sistema'),
            ('Status:', 'Finalizada' if comparacao.status == 'concluida' else comparacao.status.title())
        ]
        
        for i, (campo, valor) in enumerate(dados):
            cells = meta_table.rows[i].cells
            cells[0].text = campo
            cells[0].paragraphs[0].runs[0].bold = True
            cells[1].text = valor
        
        doc.add_paragraph()  # Espaçamento
    
    def _adicionar_metadados_pdf(self, story, styles, comparacao):
        """Adiciona metadados formatados ao PDF"""
        dados = [
            ['Área Jurídica:', f"{comparacao.descricao_area} ({comparacao.area_processo})"],
            ['Data da Comparação:', comparacao.data_comparacao.strftime('%d/%m/%Y %H:%M')],
            ['Cliente/Processo:', comparacao.documento_cliente or 'Não informado'],
            ['Usuário:', getattr(comparacao, 'created_by', None).username if getattr(comparacao, 'created_by', None) else 'Sistema'],
            ['Status:', 'Finalizada' if comparacao.status == 'concluida' else comparacao.status.title()]
        ]
        
        table = Table(dados, colWidths=[4*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor(self.cores_tema['light'])),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(self.cores_tema['dark'])),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    def _processar_html_com_marcacoes_melhoradas(self, doc, html_content):
        """Processa HTML com marcações melhoradas para DOCX"""
        if not html_content:
            doc.add_paragraph("Conteúdo não disponível.")
            return
        
        # Adicionar subtítulo
        subtitulo = doc.add_paragraph()
        subtitulo.style = 'Subtitulo'
        subtitulo.add_run("Conteúdo do Documento com Marcações")
        
        try:
            # Dividir por quebras de linha
            linhas = html_content.replace('<br>', '\n').replace('<br/>', '\n').split('\n')
            
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                
                paragraph = doc.add_paragraph()
                self._processar_linha_com_marcacoes_docx(paragraph, linha)
                
        except Exception as e:
            logger.error(f"Erro ao processar HTML com marcações: {e}")
            # Fallback para texto limpo
            texto_limpo = re.sub('<[^>]*>', '', html_content)
            doc.add_paragraph(texto_limpo)
    
    def _processar_linha_com_marcacoes_docx(self, paragraph, linha):
        """Processa uma linha HTML com marcações para DOCX"""
        # Padrões de marcação mais robustos
        padroes_marcacao = [
            (r'<ins[^>]*>(.*?)</ins>', 'ins'),
            (r'<del[^>]*>(.*?)</del>', 'del'),
            (r'<span[^>]*class="[^"]*(?:diff-adicionado|adicao)[^"]*"[^>]*>(.*?)</span>', 'ins'),
            (r'<span[^>]*class="[^"]*(?:diff-deletado|remocao)[^"]*"[^>]*>(.*?)</span>', 'del'),
            (r'<span[^>]*style="[^"]*background-color:\s*#ddffdd[^"]*"[^>]*>(.*?)</span>', 'ins'),
            (r'<span[^>]*style="[^"]*background-color:\s*#ffdddd[^"]*"[^>]*>(.*?)</span>', 'del'),
        ]
        
        tags_encontradas = []
        
        # Encontrar todas as marcações
        for padrao, tipo in padroes_marcacao:
            for match in re.finditer(padrao, linha, re.IGNORECASE):
                tags_encontradas.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': tipo,
                    'content': match.group(1),
                    'full_match': match.group(0)
                })
        
        # Ordenar por posição
        tags_encontradas.sort(key=lambda x: x['start'])
        
        # Processar texto com tags
        posicao_atual = 0
        
        for tag in tags_encontradas:
            # Texto antes da tag
            if tag['start'] > posicao_atual:
                texto_antes = linha[posicao_atual:tag['start']]
                texto_limpo = re.sub('<[^>]*>', '', texto_antes)
                if texto_limpo.strip():
                    paragraph.add_run(texto_limpo)
            
            # Conteúdo da tag com formatação
            conteudo_tag = re.sub('<[^>]*>', '', tag['content'])
            if conteudo_tag.strip():
                run = paragraph.add_run(conteudo_tag)
                
                if tag['type'] == 'ins':
                    # Texto adicionado - verde e negrito
                    run.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
                    run.bold = True
                elif tag['type'] == 'del':
                    # Texto removido - vermelho e riscado
                    run.font.highlight_color = WD_COLOR_INDEX.RED
                    run.font.strike = True
            
            posicao_atual = tag['end']
        
        # Texto restante
        if posicao_atual < len(linha):
            texto_final = linha[posicao_atual:]
            texto_limpo = re.sub('<[^>]*>', '', texto_final)
            if texto_limpo.strip():
                paragraph.add_run(texto_limpo)
        
        # Se não há tags, adicionar texto completo
        if not tags_encontradas:
            texto_limpo = re.sub('<[^>]*>', '', linha)
            if texto_limpo.strip():
                paragraph.add_run(texto_limpo)
    
    def _adicionar_legenda_marcacoes_docx(self, doc):
        """Adiciona legenda das marcações ao DOCX"""
        doc.add_paragraph()
        
        legenda_titulo = doc.add_paragraph()
        legenda_titulo.style = 'Subtitulo'
        legenda_titulo.add_run("Legenda das Marcações")
        
        # Texto adicionado
        p_add = doc.add_paragraph()
        p_add.add_run("• Texto Adicionado: ")
        run_add = p_add.add_run("destacado em verde e negrito")
        run_add.font.highlight_color = WD_COLOR_INDEX.BRIGHT_GREEN
        run_add.bold = True
        
        # Texto removido
        p_del = doc.add_paragraph()
        p_del.add_run("• Texto Removido: ")
        run_del = p_del.add_run("destacado em vermelho e riscado")
        run_del.font.highlight_color = WD_COLOR_INDEX.RED
        run_del.font.strike = True
    
    def _adicionar_legenda_marcacoes_pdf(self, story, styles):
        """Adiciona legenda das marcações ao PDF"""
        story.append(Spacer(1, 20))
        story.append(Paragraph("Legenda das Marcações", styles['Subtitulo']))
        
        story.append(Paragraph(
            "• <b>Texto Adicionado:</b> <font color='#00734d' backColor='#d1fdd1'>destacado em verde</font>",
            styles['Normal']
        ))
        
        story.append(Paragraph(
            "• <b>Texto Removido:</b> <font color='#dc3545' backColor='#fdd1d1'>destacado em vermelho</font>",
            styles['Normal']
        ))
    
    def _processar_html_pdf_com_marcacoes(self, story, styles, html_content):
        """Processa HTML com marcações para PDF"""
        if not html_content:
            story.append(Paragraph("Conteúdo não disponível.", styles['Normal']))
            return
        
        story.append(Paragraph("Conteúdo do Documento com Marcações", styles['Subtitulo']))
        
        try:
            # Processar o HTML de forma simplificada para PDF
            texto_processado = self._converter_html_para_pdf(html_content)
            story.append(Paragraph(texto_processado, styles['Normal']))
        except Exception as e:
            logger.error(f"Erro ao processar HTML para PDF: {e}")
            texto_limpo = re.sub('<[^>]*>', '', html_content)
            story.append(Paragraph(texto_limpo, styles['Normal']))
    
    def _converter_html_para_pdf(self, html_content):
        """Converte HTML para formato compatível com ReportLab"""
        # Substituições básicas para PDF
        texto = html_content
        
        # Marcações de adição
        texto = re.sub(
            r'<(?:ins|span[^>]*class="[^"]*(?:diff-adicionado|adicao)[^"]*")[^>]*>(.*?)</(?:ins|span)>',
            r'<font color="#00734d" backColor="#d1fdd1"><b>\1</b></font>',
            texto,
            flags=re.IGNORECASE
        )
        
        # Marcações de remoção
        texto = re.sub(
            r'<(?:del|span[^>]*class="[^"]*(?:diff-deletado|remocao)[^"]*")[^>]*>(.*?)</(?:del|span)>',
            r'<font color="#dc3545" backColor="#fdd1d1">\1</font>',
            texto,
            flags=re.IGNORECASE
        )
        
        # Quebras de linha
        texto = texto.replace('<br>', '<br/>')
        
        # Remover outras tags não suportadas
        texto = re.sub(r'<(?!/?(?:b|i|u|font|br)[^>]*>)[^>]*>', '', texto)
        
        return texto
    
    def _processar_html_simples(self, doc, html_content):
        """Processa HTML sem marcações para DOCX"""
        if not html_content:
            doc.add_paragraph("Conteúdo não disponível.")
            return
        
        subtitulo = doc.add_paragraph()
        subtitulo.style = 'Subtitulo'
        subtitulo.add_run("Conteúdo do Documento")
        
        texto_limpo = re.sub('<[^>]*>', '', html_content)
        texto_limpo = texto_limpo.replace('<br>', '\n').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        paragrafos = texto_limpo.split('\n')
        for paragrafo in paragrafos:
            paragrafo = paragrafo.strip()
            if paragrafo:
                doc.add_paragraph(paragrafo)
    
    def _processar_html_pdf_simples(self, story, styles, html_content):
        """Processa HTML sem marcações para PDF"""
        if not html_content:
            story.append(Paragraph("Conteúdo não disponível.", styles['Normal']))
            return
        
        story.append(Paragraph("Conteúdo do Documento", styles['Subtitulo']))
        
        texto_limpo = re.sub('<[^>]*>', '', html_content)
        texto_limpo = texto_limpo.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        story.append(Paragraph(texto_limpo, styles['Normal']))
    
    def _adicionar_analise_ia_docx(self, doc, analise_ia):
        """Adiciona análise da IA ao DOCX"""
        if not analise_ia:
            return
        
        doc.add_page_break()
        
        titulo_analise = doc.add_paragraph()
        titulo_analise.style = 'Subtitulo'
        titulo_analise.add_run("Análise Inteligente")
        
        try:
            import json
            if isinstance(analise_ia, str):
                analise_data = json.loads(analise_ia)
            else:
                analise_data = analise_ia
            
            # Resumo das diferenças
            if 'resumo_diferencas' in analise_data:
                doc.add_paragraph("Resumo das Diferenças:", style='Heading 3')
                doc.add_paragraph(analise_data['resumo_diferencas'])
            
            # Principais alterações
            if 'principais_alteracoes' in analise_data:
                doc.add_paragraph("Principais Alterações:", style='Heading 3')
                for alteracao in analise_data['principais_alteracoes']:
                    p = doc.add_paragraph()
                    p.style = 'List Bullet'
                    p.add_run(alteracao)
            
            # Análise de impacto
            if 'analise_impacto' in analise_data:
                doc.add_paragraph("Análise de Impacto:", style='Heading 3')
                doc.add_paragraph(analise_data['analise_impacto'])
                
        except Exception as e:
            logger.error(f"Erro ao processar análise IA: {e}")
            doc.add_paragraph("Análise disponível no sistema.")
    
    def _adicionar_analise_ia_pdf(self, story, styles, analise_ia):
        """Adiciona análise da IA ao PDF"""
        if not analise_ia:
            return
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Análise Inteligente", styles['Subtitulo']))
        
        try:
            import json
            if isinstance(analise_ia, str):
                analise_data = json.loads(analise_ia)
            else:
                analise_data = analise_ia
            
            # Resumo das diferenças
            if 'resumo_diferencas' in analise_data:
                story.append(Paragraph("<b>Resumo das Diferenças:</b>", styles['Normal']))
                story.append(Paragraph(analise_data['resumo_diferencas'], styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Principais alterações
            if 'principais_alteracoes' in analise_data:
                story.append(Paragraph("<b>Principais Alterações:</b>", styles['Normal']))
                for alteracao in analise_data['principais_alteracoes']:
                    story.append(Paragraph(f"• {alteracao}", styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Análise de impacto
            if 'analise_impacto' in analise_data:
                story.append(Paragraph("<b>Análise de Impacto:</b>", styles['Normal']))
                story.append(Paragraph(analise_data['analise_impacto'], styles['Normal']))
                
        except Exception as e:
            logger.error(f"Erro ao processar análise IA: {e}")
            story.append(Paragraph("Análise disponível no sistema.", styles['Normal']))
    
    def _adicionar_rodape_docx(self, doc, comparacao):
        """Adiciona rodapé ao DOCX"""
        doc.add_paragraph()
        rodape = doc.add_paragraph()
        rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rodape.style = 'Metadados'
        
        run = rodape.add_run(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        run.font.size = Pt(9)
        
        rodape.add_run("\nSistema Legal Design Pro - Comparação de Documentos")
    
    def gerar_relatorio_completo_pdf(self, comparacao):
        """
        Gera relatório PDF completo com ambos os lados da comparação e análise
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2.5*cm,
                bottomMargin=2*cm
            )
            
            styles = self._configurar_estilos_pdf()
            story = []
            
            # Cabeçalho do relatório
            story.append(Paragraph(
                f"Relatório Completo de Comparação: {comparacao.titulo}",
                styles['TituloPrincipal']
            ))
            story.append(Spacer(1, 20))
            
            # Metadados
            self._adicionar_metadados_pdf(story, styles, comparacao)
            
            # Resumo executivo
            story.append(Paragraph("Resumo Executivo", styles['Subtitulo']))
            
            # Análise IA primeiro
            if comparacao.analise_ia:
                self._adicionar_analise_ia_pdf(story, styles, comparacao.analise_ia)
            else:
                story.append(Paragraph("Análise automática não disponível para esta comparação.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Documento Original (Lado A)
            story.append(Paragraph("Documento Original (Versão A)", styles['Subtitulo']))
            if comparacao.resultado_editado_a:
                self._processar_html_pdf_com_marcacoes(story, styles, comparacao.resultado_editado_a)
            else:
                story.append(Paragraph("Conteúdo do documento A não disponível.", styles['Normal']))
            
            # Nova página para documento B
            from reportlab.platypus import PageBreak
            story.append(PageBreak())
            
            # Documento Modificado (Lado B)
            story.append(Paragraph("Documento Modificado (Versão B)", styles['Subtitulo']))
            if comparacao.resultado_editado_b:
                self._processar_html_pdf_com_marcacoes(story, styles, comparacao.resultado_editado_b)
            else:
                story.append(Paragraph("Conteúdo do documento B não disponível.", styles['Normal']))
            
            # Legenda das marcações
            self._adicionar_legenda_marcacoes_pdf(story, styles)
            
            # Rodapé com informações do relatório
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Sistema Legal Design Pro",
                styles['Metadados']
            ))
            
            # Construir PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório completo PDF: {e}")
            raise