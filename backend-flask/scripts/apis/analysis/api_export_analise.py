"""
API para exportação profissional de análises jurídicas em PDF e Word
Formatação otimizada sem espaçamentos excessivos
"""
import io
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
import logging

logger = logging.getLogger(__name__)
export_bp = Blueprint('export_analise', __name__)

def processar_texto_completo(texto):
    """Processa texto removendo apenas markdown mas mantendo estrutura completa"""
    if not texto:
        return ""
    
    # Remover formatação markdown mantendo a estrutura
    texto = re.sub(r'\*\*([^*]+)\*\*', r'\1', texto)  # **negrito**
    texto = re.sub(r'#{1,6}\s*', '', texto)           # ### títulos
    texto = re.sub(r'\*([^*]+)\*', r'\1', texto)      # *itálico*
    
    # Dividir em linhas não vazias
    linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
    
    # Manter estrutura original com quebras de linha adequadas
    return '\n'.join(linhas)

@export_bp.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Exporta análise em PDF com formatação compacta"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=3.5*cm
        )
        
        styles = getSampleStyleSheet()
        
        # Estilos compactos
        title_style = ParagraphStyle(
            'CompactTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=8*mm,
            leading=18
        )
        
        heading_style = ParagraphStyle(
            'CompactHeading',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            alignment=TA_LEFT,
            spaceAfter=3*mm,
            spaceBefore=5*mm,
            leading=15
        )
        
        body_style = ParagraphStyle(
            'ProfessionalBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=2*mm,
            spaceBefore=0,
            leading=15,
            textColor=colors.HexColor('#2c3e50'),
            leftIndent=3*mm
        )
        
        content = []
        
        # Título
        # Cabeçalho com linha decorativa
        content.append(Paragraph("RELATÓRIO DE ANÁLISE JURÍDICA MULTI-AGENTE", title_style))
        
        # Linha decorativa
        line_style = ParagraphStyle(
            'DecorativeLine',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=6*mm
        )
        content.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", line_style))
        
        # Informações básicas em tabela profissional
        numero_registro = data.get('numero_registro', 'N/A')
        resultados_agentes = data.get('resultados_agentes', data.get('resultados', []))
        total_agentes = len(resultados_agentes)
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        # Tabela de informações
        info_data = [
            ['Data da Análise:', data_geracao],
            ['Número do Registro:', numero_registro],
            ['Total de Especialistas:', str(total_agentes)],
            ['Status:', 'Análise Concluída']
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        content.append(info_table)
        content.append(Spacer(1, 6*mm))
        
        # Análises dos especialistas
        resultados = data.get('resultados_agentes', [])
        if resultados:
            content.append(Paragraph("ANÁLISES DOS ESPECIALISTAS", heading_style))
            
            for i, resultado in enumerate(resultados, 1):
                agente_nome = resultado.get('agente_nome', f'Especialista {i}')
                modelo = resultado.get('modelo_usado', 'N/A')
                analise = resultado.get('resultado', '')
                
                # Cabeçalho do especialista
                content.append(Paragraph(f"{i}. {agente_nome}", heading_style))
                content.append(Paragraph(f"Modelo: {modelo}", body_style))
                
                # Análise completa processada
                if analise and analise.strip():
                    texto_processado = processar_texto_completo(analise)
                    if texto_processado:
                        # Dividir em parágrafos para melhor apresentação
                        paragrafos = texto_processado.split('\n')
                        for paragrafo in paragrafos:
                            if paragrafo.strip():
                                content.append(Paragraph(paragrafo.strip(), body_style))
                
                if i < len(resultados_agentes):
                    content.append(Spacer(1, 3*mm))
        
        # Recomendações consolidadas
        recomendacoes = data.get('recomendacoes_consolidadas', {})
        if recomendacoes:
            content.append(Spacer(1, 5*mm))
            content.append(Paragraph("RECOMENDAÇÕES CONSOLIDADAS", heading_style))
            
            for categoria, items in recomendacoes.items():
                if items and isinstance(items, list):
                    nome_categoria = {
                        'importantes': 'Melhorias Importantes',
                        'prioritarias': 'Ações Prioritárias',
                        'sugeridas': 'Sugestões Adicionais'
                    }.get(categoria, categoria.title())
                    
                    content.append(Paragraph(f"{nome_categoria}:", body_style))
                    for item in items[:5]:
                        if item:
                            content.append(Paragraph(f"• {item}", body_style))
        
        doc.build(content)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'analise_juridica_{numero_registro}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

@export_bp.route('/api/export/word', methods=['POST'])
def export_word():
    """Exporta análise em Word com formatação Roboto compacta"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        doc = Document()
        
        # Configurar margens
        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(2)
            section.left_margin = Cm(2)
            section.right_margin = Cm(2)
            section.bottom_margin = Cm(3.5)
        
        def aplicar_formato_profissional(paragrafo, tamanho=12, negrito=False, cor='2c3e50', espacamento=6, fonte='Calibri'):
            """Aplica formatação profissional com cores e tipografia moderna"""
            for run in paragrafo.runs:
                run.font.name = fonte
                run.font.size = Pt(tamanho)
                run.font.bold = negrito
                # Aplicar cor
                if cor == '2c3e50':  # Azul escuro
                    run.font.color.rgb = RGBColor(44, 62, 80)
                elif cor == '34495e':  # Cinza escuro
                    run.font.color.rgb = RGBColor(52, 73, 94)
                elif cor == 'ffffff':  # Branco
                    run.font.color.rgb = RGBColor(255, 255, 255)
                elif cor == '3498db':  # Azul
                    run.font.color.rgb = RGBColor(52, 152, 219)
                elif cor == '27ae60':  # Verde
                    run.font.color.rgb = RGBColor(39, 174, 96)
                elif cor == 'e74c3c':  # Vermelho
                    run.font.color.rgb = RGBColor(231, 76, 60)
                elif cor == 'f39c12':  # Laranja
                    run.font.color.rgb = RGBColor(243, 156, 18)
            
            paragraph_format = paragrafo.paragraph_format
            paragraph_format.space_after = Pt(espacamento)
            paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph_format.line_spacing = Pt(16)

        
        # Título principal com design profissional
        title = doc.add_heading('RELATÓRIO DE ANÁLISE JURÍDICA MULTI-AGENTE', level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        aplicar_formato_profissional(title, tamanho=18, negrito=True, cor='2c3e50', espacamento=15)
        
        # Linha decorativa
        decorative_line = doc.add_paragraph('─' * 80)
        decorative_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
        aplicar_formato_profissional(decorative_line, tamanho=10, cor='34495e', espacamento=12)
        
        # Informações básicas
        numero_registro = data.get('numero_registro', 'N/A')
        resultados_agentes = data.get('resultados_agentes', data.get('resultados', []))
        total_agentes = len(resultados_agentes)
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        
        # Tabela de informações profissional
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Table Grid'
        info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Configurar dados da tabela
        info_data = [
            ('Data da Análise:', data_geracao),
            ('Número do Registro:', numero_registro),
            ('Total de Especialistas:', str(total_agentes)),
            ('Status:', 'Análise Concluída')
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            
            # Formatação da primeira coluna (labels)
            aplicar_formato_profissional(row.cells[0].paragraphs[0], tamanho=11, negrito=True, cor='34495e')
            # Formatação da segunda coluna (valores)
            aplicar_formato_profissional(row.cells[1].paragraphs[0], tamanho=11, cor='2c3e50')
        
        # Espaçamento após tabela
        spacer = doc.add_paragraph()
        aplicar_formato_profissional(spacer, espacamento=15)
        
        # Análises dos especialistas
        resultados = data.get('resultados_agentes', [])
        if resultados:
            main_heading = doc.add_heading('ANÁLISES DOS ESPECIALISTAS', level=2)
            aplicar_formato_profissional(main_heading, tamanho=15, negrito=True, cor='2c3e50', espacamento=10)
            
            for i, resultado in enumerate(resultados, 1):
                # Quebra de página para cada especialista (exceto o primeiro)
                if i > 1:
                    doc.add_page_break()
                
                agente_nome = resultado.get('agente_nome', f'Especialista {i}')
                modelo = resultado.get('modelo_usado', 'N/A')
                categoria = resultado.get('categoria', 'Análise Jurídica')
                especialidade = resultado.get('especialidade', 'Análise Geral')
                analise = resultado.get('resultado', '')
                
                # Cabeçalho moderno do especialista
                specialist_heading = doc.add_heading(f'🎯 ESPECIALISTA {i}: {agente_nome}', level=2)
                aplicar_formato_profissional(specialist_heading, tamanho=16, negrito=True, cor='3498db', espacamento=12)
                
                # Caixa de informações do especialista
                info_table = doc.add_table(rows=3, cols=2)
                info_table.style = 'Table Grid'
                
                info_table.cell(0, 0).text = '🤖 Modelo de IA:'
                info_table.cell(0, 1).text = modelo
                info_table.cell(1, 0).text = '📂 Categoria:'
                info_table.cell(1, 1).text = categoria
                info_table.cell(2, 0).text = '🔍 Especialidade:'
                info_table.cell(2, 1).text = especialidade
                
                # Formatação da tabela
                for row in info_table.rows:
                    aplicar_formato_profissional(row.cells[0].paragraphs[0], tamanho=10, negrito=True, cor='34495e')
                    aplicar_formato_profissional(row.cells[1].paragraphs[0], tamanho=10, cor='2c3e50')
                
                # Espaçamento após tabela
                spacer = doc.add_paragraph()
                aplicar_formato_profissional(spacer, espacamento=8)
                
                # Título da análise
                analysis_title = doc.add_heading('📋 ANÁLISE DETALHADA', level=3)
                aplicar_formato_profissional(analysis_title, tamanho=14, negrito=True, cor='27ae60', espacamento=8)
                
                # Análise completa com formatação aprimorada
                if analise and analise.strip():
                    # Processar texto com melhor estruturação
                    secoes = analise.split('\n\n')
                    for secao in secoes:
                        if secao.strip():
                            linhas = secao.split('\n')
                            for linha in linhas:
                                if linha.strip():
                                    if linha.strip().startswith('**') and linha.strip().endswith('**'):
                                        # Título de seção
                                        titulo_texto = linha.strip().replace('**', '')
                                        titulo_para = doc.add_heading(titulo_texto, level=4)
                                        aplicar_formato_profissional(titulo_para, tamanho=12, negrito=True, cor='f39c12')
                                    elif linha.strip().startswith(('*', '-')):
                                        # Item de lista
                                        item_texto = linha.strip().lstrip('*-').strip()
                                        list_para = doc.add_paragraph(f"• {item_texto}")
                                        aplicar_formato_profissional(list_para, tamanho=11, cor='2c3e50', espacamento=3)
                                    elif linha.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                                        # Lista numerada
                                        list_para = doc.add_paragraph(linha.strip())
                                        aplicar_formato_profissional(list_para, tamanho=11, cor='2c3e50', espacamento=3)
                                    else:
                                        # Parágrafo normal
                                        if linha.strip():
                                            content_para = doc.add_paragraph(linha.strip())
                                            aplicar_formato_profissional(content_para, tamanho=11, cor='2c3e50', espacamento=4)
                
                # Separador visual elegante entre análises
                if i < len(resultados):
                    separator_para = doc.add_paragraph()
                    separator_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    separator_run = separator_para.add_run('◆ ◆ ◆ ◆ ◆')
                    separator_run.font.color.rgb = RGBColor(52, 152, 219)  # Azul
                    separator_run.font.size = Pt(16)
                    aplicar_formato_profissional(separator_para, espacamento=15)
        
        # Nova página para recomendações
        doc.add_page_break()
        
        # Recomendações consolidadas com design moderno
        recomendacoes = data.get('recomendacoes_consolidadas', {})
        if recomendacoes:
            rec_heading = doc.add_heading('🎯 RECOMENDAÇÕES CONSOLIDADAS', level=1)
            aplicar_formato_profissional(rec_heading, tamanho=18, negrito=True, cor='2c3e50', espacamento=15)
            
            # Introdução às recomendações
            intro_para = doc.add_paragraph('Com base nas análises realizadas pelos especialistas, apresentamos as seguintes recomendações organizadas por nível de prioridade para otimizar a segurança jurídica do documento:')
            aplicar_formato_profissional(intro_para, tamanho=11, cor='34495e', espacamento=12)
            
            if 'prioritarias' in recomendacoes and recomendacoes['prioritarias']:
                priority_heading = doc.add_heading('🔴 ALTA PRIORIDADE', level=2)
                aplicar_formato_profissional(priority_heading, tamanho=16, negrito=True, cor='e74c3c', espacamento=10)
                
                warning_para = doc.add_paragraph('⚠️ Estas recomendações devem ser implementadas imediatamente para mitigar riscos significativos.')
                aplicar_formato_profissional(warning_para, tamanho=10, cor='e74c3c', espacamento=8)
                
                for i, rec in enumerate(recomendacoes['prioritarias'], 1):
                    rec_para = doc.add_paragraph(f"{i}. {rec}")
                    aplicar_formato_profissional(rec_para, tamanho=11, cor='2c3e50', espacamento=4)
            
            if 'importantes' in recomendacoes and recomendacoes['importantes']:
                important_heading = doc.add_heading('🟡 PRIORIDADE MÉDIA', level=2)
                aplicar_formato_profissional(important_heading, tamanho=16, negrito=True, cor='f39c12', espacamento=15)
                
                medium_para = doc.add_paragraph('⚡ Recomendações importantes para fortalecer a estrutura contratual.')
                aplicar_formato_profissional(medium_para, tamanho=10, cor='f39c12', espacamento=8)
                
                for i, rec in enumerate(recomendacoes['importantes'], 1):
                    rec_para = doc.add_paragraph(f"{i}. {rec}")
                    aplicar_formato_profissional(rec_para, tamanho=11, cor='2c3e50', espacamento=4)
            
            if 'sugeridas' in recomendacoes and recomendacoes['sugeridas']:
                suggestions_heading = doc.add_heading('🟢 SUGESTÕES ADICIONAIS', level=2)
                aplicar_formato_profissional(suggestions_heading, tamanho=16, negrito=True, cor='27ae60', espacamento=15)
                
                suggestion_para = doc.add_paragraph('💡 Melhorias que podem ser consideradas para otimização futura.')
                aplicar_formato_profissional(suggestion_para, tamanho=10, cor='27ae60', espacamento=8)
                
                for i, rec in enumerate(recomendacoes['sugeridas'], 1):
                    rec_para = doc.add_paragraph(f"{i}. {rec}")
                    aplicar_formato_profissional(rec_para, tamanho=11, cor='2c3e50', espacamento=4)
        
        # Nova página para conclusão
        doc.add_page_break()
        
        # Seção de resumo executivo
        summary_heading = doc.add_heading('📊 RESUMO EXECUTIVO', level=1)
        aplicar_formato_profissional(summary_heading, tamanho=18, negrito=True, cor='2c3e50', espacamento=15)
        
        # Estatísticas da análise
        stats_table = doc.add_table(rows=4, cols=2)
        stats_table.style = 'Table Grid'
        
        stats_table.cell(0, 0).text = '📈 Total de Especialistas:'
        stats_table.cell(0, 1).text = str(total_agentes)
        stats_table.cell(1, 0).text = '🔍 Análises Realizadas:'
        stats_table.cell(1, 1).text = str(len(resultados))
        stats_table.cell(2, 0).text = '⚡ Tempo de Processamento:'
        stats_table.cell(2, 1).text = 'Análise em tempo real'
        stats_table.cell(3, 0).text = '✅ Status:'
        stats_table.cell(3, 1).text = 'Análise Completa'
        
        # Formatação da tabela de estatísticas
        for row in stats_table.rows:
            aplicar_formato_profissional(row.cells[0].paragraphs[0], tamanho=11, negrito=True, cor='34495e')
            aplicar_formato_profissional(row.cells[1].paragraphs[0], tamanho=11, cor='2c3e50')
        
        # Espaçamento
        spacer = doc.add_paragraph()
        aplicar_formato_profissional(spacer, espacamento=12)
        
        # Aviso legal
        legal_heading = doc.add_heading('⚖️ AVISO LEGAL', level=2)
        aplicar_formato_profissional(legal_heading, tamanho=14, negrito=True, cor='e74c3c', espacamento=10)
        
        aviso_para = doc.add_paragraph('Este relatório foi gerado por sistema de inteligência artificial especializado em análise jurídica. As recomendações apresentadas são baseadas em análise automatizada e devem ser revisadas por profissional jurídico qualificado antes de qualquer implementação.')
        aplicar_formato_profissional(aviso_para, tamanho=11, cor='34495e', espacamento=15)
        
        # Linha separadora elegante
        separator_final = doc.add_paragraph()
        separator_final.alignment = WD_ALIGN_PARAGRAPH.CENTER
        separator_run_final = separator_final.add_run('◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆')
        separator_run_final.font.color.rgb = RGBColor(44, 62, 80)
        separator_run_final.font.size = Pt(14)
        aplicar_formato_profissional(separator_final, espacamento=12)
        
        # Rodapé moderno
        footer_para = doc.add_paragraph()
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        footer_run1 = footer_para.add_run('🤖 Legal Design Pro V2 - Sistema de Análise Multi-Agente\n')
        footer_run1.font.name = 'Calibri'
        footer_run1.font.size = Pt(12)
        footer_run1.font.bold = True
        footer_run1.font.color.rgb = RGBColor(44, 62, 80)
        
        footer_run2 = footer_para.add_run(f'📅 Relatório gerado em {data_geracao}\n')
        footer_run2.font.name = 'Calibri'
        footer_run2.font.size = Pt(10)
        footer_run2.font.italic = True
        footer_run2.font.color.rgb = RGBColor(102, 102, 102)
        
        footer_run3 = footer_para.add_run(f'🔐 Registro: {numero_registro}\n')
        footer_run3.font.name = 'Calibri'
        footer_run3.font.size = Pt(9)
        footer_run3.font.color.rgb = RGBColor(108, 117, 125)
        
        footer_run4 = footer_para.add_run('⚡ Powered by OpenAI GPT-4o, Anthropic Claude & Google Gemini')
        footer_run4.font.name = 'Calibri'
        footer_run4.font.size = Pt(8)
        footer_run4.font.color.rgb = RGBColor(153, 153, 153)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'analise_juridica_{numero_registro}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar Word: {str(e)}")
        return jsonify({'error': f'Erro ao gerar Word: {str(e)}'}), 500

def registrar_api_export(app):
    """Registra a API de exportação"""
    app.register_blueprint(export_bp)
    return True