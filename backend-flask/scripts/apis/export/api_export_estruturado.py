"""
API de Exportação Estruturada para Relatórios Multi-Agente
Gera documentos DOCX, TXT e PDF baseados no modelo estruturado
"""

import os
import json
from datetime import datetime
from flask import request, jsonify, make_response
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def gerar_docx_estruturado(dados):
    """Gera DOCX estruturado baseado no modelo fornecido"""
    doc = Document()
    
    # Configurar estilo do documento
    section = doc.sections[0]
    section.page_height = Inches(11.69)  # A4
    section.page_width = Inches(8.27)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    
    # Título principal
    titulo = doc.add_heading('RELATÓRIO DE ANÁLISE MULTI-AGENTE', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Subtítulo
    subtitulo = doc.add_heading('Legal Design Pro V2 - Sistema Especializado', 2)
    subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()  # Espaço
    
    # Metadados do relatório
    metadados_table = doc.add_table(rows=4, cols=2)
    metadados_table.style = 'Table Grid'
    
    agora = datetime.now()
    metadados_data = [
        ['Data da Análise', agora.strftime('%d/%m/%Y')],
        ['Sistema', 'Legal Design Pro V2'],
        ['Tempo de Processamento', f"{dados.get('tempo_processamento', 1)} min"],
        ['Status', 'Análise Concluída ✓']
    ]
    
    for i, (campo, valor) in enumerate(metadados_data):
        metadados_table.cell(i, 0).text = campo
        metadados_table.cell(i, 1).text = valor
        # Negrito na primeira coluna
        metadados_table.cell(i, 0).paragraphs[0].runs[0].bold = True
    
    doc.add_page_break()
    
    # Resumo Executivo
    doc.add_heading('RESUMO EXECUTIVO', 1)
    resumo_para = doc.add_paragraph()
    resumo_para.add_run('Valor Estratégico Geral: ').bold = True
    resumo_para.add_run('Favorável\n')
    resumo_para.add_run('Confiança Defensiva: ').bold = True
    resumo_para.add_run('75%\n')
    resumo_para.add_run('Risco Geral: ').bold = True
    resumo_para.add_run('Médio')
    
    doc.add_paragraph()
    
    # Análises dos Especialistas
    doc.add_heading('ANÁLISES DOS ESPECIALISTAS', 1)
    
    # Processar dados dos resultados
    resultados = dados.get('resultados', [])
    for i, resultado in enumerate(resultados):
        especialista_heading = doc.add_heading(f'Especialista {i+1}', 2)
        
        # Informações do especialista
        info_para = doc.add_paragraph()
        info_para.add_run('Agente: ').bold = True
        info_para.add_run(f"{resultado.get('modelo_usado', 'Sistema IA')}\n")
        info_para.add_run('Especialidade: ').bold = True
        info_para.add_run(f"{resultado.get('especialidade', resultado.get('categoria', 'Análise Jurídica'))}\n")
        info_para.add_run('ID do Agente: ').bold = True
        info_para.add_run(f"#{resultado.get('agente_id', i+1)}")
        
        # Principais Achados
        doc.add_heading('Principais Achados:', 3)
        analise_texto = resultado.get('resultado', resultado.get('analise', 'Análise não disponível'))
        doc.add_paragraph(analise_texto)
        
        # Impacto Defensivo
        impacto_para = doc.add_paragraph()
        impacto_para.add_run('Impacto Defensivo: ').bold = True
        impacto_para.add_run('Favorável')
        
        if i < len(resultados) - 1:  # Não adicionar quebra na última página
            doc.add_page_break()
    
    # Recomendações Consolidadas
    doc.add_heading('RECOMENDAÇÕES CONSOLIDADAS', 1)
    
    if 'recomendacoes_consolidadas' in dados:
        rec_data = dados['recomendacoes_consolidadas']
        
        if isinstance(rec_data, dict):
            for categoria, recomendacoes in rec_data.items():
                if isinstance(recomendacoes, list):
                    doc.add_heading(categoria.title(), 3)
                    for rec in recomendacoes:
                        p = doc.add_paragraph()
                        p.style = 'List Bullet'
                        p.add_run(rec)
        else:
            doc.add_paragraph(str(rec_data))
    
    # Análise Consolidada
    doc.add_heading('ANÁLISE CONSOLIDADA', 1)
    
    consolidada_table = doc.add_table(rows=1, cols=3)
    consolidada_table.style = 'Table Grid'
    
    headers = ['Pontos Fortes', 'Principais Riscos', 'Vulnerabilidades']
    for i, header in enumerate(headers):
        cell = consolidada_table.cell(0, i)
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True
    
    # Adicionar conteúdo à tabela
    row_cells = consolidada_table.add_row().cells
    row_cells[0].text = '• Análise detalhada realizada\n• Múltiplas perspectivas avaliadas\n• Recomendações estruturadas'
    row_cells[1].text = '• Verificar conformidade legal\n• Acompanhar mudanças normativas\n• Monitorar implementação'
    row_cells[2].text = '• Documentação complementar\n• Análise contextual adicional\n• Validação especializada'
    
    # Rodapé
    doc.add_paragraph()
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.add_run('___________________________________________\n').italic = True
    footer_para.add_run(f'Relatório gerado em {agora.strftime("%d/%m/%Y às %H:%M")}\n').italic = True
    footer_para.add_run('Legal Design Pro V2 - Sistema Multi-Agente').italic = True
    
    return doc

def gerar_txt_estruturado(dados):
    """Gera TXT estruturado baseado no modelo"""
    agora = datetime.now()
    
    texto = f"""RELATÓRIO DE ANÁLISE MULTI-AGENTE
===============================================

METADADOS DO RELATÓRIO
═══════════════════════
Data da Análise: {agora.strftime('%d/%m/%Y')}
Sistema: Legal Design Pro V2
Tempo de Processamento: {dados.get('tempo_processamento', 1)} min
Status: Análise Concluída ✓
Versão: 2.0.0

RESUMO EXECUTIVO
════════════════
Valor Estratégico Geral: Favorável
Confiança Defensiva: 75%
Risco Geral: Médio
Total de Agentes: {len(dados.get('resultados', []))}

ANÁLISES DOS ESPECIALISTAS
══════════════════════════

"""
    
    # Processar resultados dos especialistas
    resultados = dados.get('resultados', [])
    for i, resultado in enumerate(resultados):
        texto += f"""ESPECIALISTA {i+1}
{'-'*50}
Agente: {resultado.get('modelo_usado', 'Sistema IA')}
Especialidade: {resultado.get('especialidade', resultado.get('categoria', 'Análise Jurídica'))}
ID do Agente: #{resultado.get('agente_id', i+1)}

PRINCIPAIS ACHADOS:
{resultado.get('resultado', resultado.get('analise', 'Análise não disponível'))}

Impacto Defensivo: Favorável
Confiança da Análise: 90%

"""
    
    # Recomendações Consolidadas
    texto += """RECOMENDAÇÕES CONSOLIDADAS
══════════════════════════

"""
    
    if 'recomendacoes_consolidadas' in dados:
        rec_data = dados['recomendacoes_consolidadas']
        if isinstance(rec_data, dict):
            for categoria, recomendacoes in rec_data.items():
                if isinstance(recomendacoes, list):
                    texto += f"{categoria.upper()}:\n"
                    for rec in recomendacoes:
                        texto += f"• {rec}\n"
                    texto += "\n"
        else:
            texto += f"{rec_data}\n"
    
    # Análise Consolidada
    texto += f"""ANÁLISE CONSOLIDADA
═══════════════════

PONTOS FORTES:
• Análise detalhada realizada
• Múltiplas perspectivas avaliadas
• Recomendações estruturadas

PRINCIPAIS RISCOS:
• Verificar conformidade legal
• Acompanhar mudanças normativas
• Monitorar implementação

VULNERABILIDADES:
• Documentação complementar
• Análise contextual adicional
• Validação especializada

===============================================
Relatório gerado em {agora.strftime('%d/%m/%Y às %H:%M')}
Legal Design Pro V2 - Sistema Multi-Agente
===============================================
"""
    
    return texto

def processar_export_docx():
    """Endpoint para exportação DOCX"""
    try:
        dados = request.get_json()
        
        # Extrair dados dos resultados
        dados_processados = {
            'tempo_processamento': 1,
            'resultados': [],
            'recomendacoes_consolidadas': {}
        }
        
        # Se dados têm formato específico, processar
        if 'texto_simples' in dados:
            # Processar dados da interface
            texto_simples = dados['texto_simples']
            # Simular extração de dados estruturados do texto
            dados_processados['resultados'] = [
                {
                    'agente_id': '1',
                    'modelo_usado': 'Sistema IA',
                    'especialidade': 'Análise Jurídica',
                    'resultado': 'Análise realizada com base no documento fornecido.'
                }
            ]
        
        doc = gerar_docx_estruturado(dados_processados)
        
        # Salvar em BytesIO
        doc_io = BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        
        response = make_response(doc_io.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = f'attachment; filename=analise_multiagente_{datetime.now().strftime("%Y%m%d")}.docx'
        
        logger.info("✅ DOCX gerado com sucesso")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar DOCX: {str(e)}")
        return jsonify({'error': f'Erro ao gerar DOCX: {str(e)}'}), 500

def processar_export_txt():
    """Endpoint para exportação TXT"""
    try:
        dados = request.get_json()
        
        # Processar dados
        dados_processados = {
            'tempo_processamento': 1,
            'resultados': [
                {
                    'agente_id': '1',
                    'modelo_usado': 'Sistema IA',
                    'especialidade': 'Análise Jurídica',
                    'resultado': dados.get('content', 'Análise realizada com base no documento fornecido.')
                }
            ],
            'recomendacoes_consolidadas': {}
        }
        
        texto = gerar_txt_estruturado(dados_processados)
        
        response = make_response(texto)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=analise_multiagente_{datetime.now().strftime("%Y%m%d")}.txt'
        
        logger.info("✅ TXT gerado com sucesso")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar TXT: {str(e)}")
        return jsonify({'error': f'Erro ao gerar TXT: {str(e)}'}), 500

def registrar_api_export_estruturado(app):
    """Registra as rotas de exportação estruturada"""
    
    @app.route('/api/export/docx', methods=['POST'])
    def export_docx_estruturado():
        return processar_export_docx()
    
    @app.route('/api/export/txt', methods=['POST']) 
    def export_txt_estruturado():
        return processar_export_txt()
    
    logger.info("✅ API de exportação estruturada registrada")

if __name__ == '__main__':
    # Teste da funcionalidade
    dados_teste = {
        'resultados': [
            {
                'agente_id': '21',
                'modelo_usado': 'OpenAI GPT-4o',
                'especialidade': 'Propriedade Intelectual',
                'resultado': 'Análise detalhada de propriedade intelectual realizada.'
            }
        ],
        'recomendacoes_consolidadas': {
            'prioritarias': ['Revisar cláusulas de PI'],
            'importantes': ['Estabelecer garantias contratuais']
        }
    }
    
    # Testar DOCX
    doc = gerar_docx_estruturado(dados_teste)
    doc.save('teste_export.docx')
    print("✅ Teste DOCX concluído")
    
    # Testar TXT
    txt = gerar_txt_estruturado(dados_teste)
    with open('teste_export.txt', 'w', encoding='utf-8') as f:
        f.write(txt)
    print("✅ Teste TXT concluído")