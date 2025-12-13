"""
Gerenciador de Exportação de Relatórios
Suporta exportação para PDF, DOCX e Markdown
"""

import os
import io
import markdown
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

class ReportExportManager:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            alignment=1  # CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=HexColor('#3498db')
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leftIndent=0,
            rightIndent=0
        )
    
    def export_to_pdf(self, markdown_content: str, titulo: str = "Relatório Jurídico") -> bytes:
        """Exporta conteúdo markdown para PDF"""
        buffer = io.BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Converter markdown para HTML e depois para elementos PDF
        story = []
        
        # Título principal
        story.append(Paragraph(titulo, self.title_style))
        story.append(Spacer(1, 20))
        
        # Processar conteúdo markdown
        lines = markdown_content.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                story.append(Spacer(1, 12))
                continue
            
            if line.startswith('# '):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                story.append(Paragraph(line[2:], self.title_style))
                story.append(Spacer(1, 12))
            elif line.startswith('## '):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                story.append(Paragraph(line[3:], self.heading_style))
                story.append(Spacer(1, 8))
            elif line.startswith('### '):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                heading_style = ParagraphStyle(
                    'SubHeading',
                    parent=self.styles['Heading3'],
                    fontSize=12,
                    spaceBefore=15,
                    spaceAfter=8,
                    textColor=HexColor('#2c3e50')
                )
                story.append(Paragraph(line[4:], heading_style))
            elif line.startswith('- '):
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                bullet_style = ParagraphStyle(
                    'Bullet',
                    parent=self.body_style,
                    leftIndent=20,
                    bulletIndent=10
                )
                story.append(Paragraph(f"• {line[2:]}", bullet_style))
            elif line.startswith('**') and line.endswith('**'):
                # Texto em negrito
                if current_section:
                    story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                bold_style = ParagraphStyle(
                    'Bold',
                    parent=self.body_style,
                    fontSize=11,
                    spaceAfter=8
                )
                story.append(Paragraph(f"<b>{line[2:-2]}</b>", bold_style))
            else:
                current_section.append(line)
        
        # Adicionar qualquer conteúdo restante
        if current_section:
            story.append(Paragraph(' '.join(current_section), self.body_style))
        
        # Rodapé
        story.append(Spacer(1, 50))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=HexColor('#7f8c8d'),
            alignment=1
        )
        story.append(Paragraph(
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - Sistema Multi-Agente de Validação Jurídica",
            footer_style
        ))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_to_docx(self, markdown_content: str, titulo: str = "Relatório Jurídico") -> bytes:
        """Exporta conteúdo markdown para DOCX"""
        doc = Document()
        
        # Configurar margens
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Título principal
        title_paragraph = doc.add_heading(titulo, level=0)
        title_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Adicionar linha separadora
        doc.add_paragraph('_' * 80)
        
        # Processar conteúdo markdown
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                doc.add_paragraph()
                continue
            
            if line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            elif line.startswith('#### '):
                doc.add_heading(line[5:], level=4)
            elif line.startswith('- '):
                p = doc.add_paragraph(line[2:], style='List Bullet')
            elif line.startswith('**') and line.endswith('**'):
                p = doc.add_paragraph()
                run = p.add_run(line[2:-2])
                run.bold = True
            elif line.startswith('---'):
                doc.add_paragraph('_' * 80)
            else:
                # Texto normal com formatação básica
                p = doc.add_paragraph()
                
                # Processar formatação inline simples
                if '**' in line:
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            p.add_run(part)
                        else:
                            run = p.add_run(part)
                            run.bold = True
                else:
                    p.add_run(line)
        
        # Adicionar rodapé
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = footer.add_run(
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - "
            "Sistema Multi-Agente de Validação Jurídica"
        )
        run.italic = True
        run.font.size = 9
        
        # Salvar em buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_markdown_file(self, markdown_content: str, titulo: str = "Relatório Jurídico") -> str:
        """Cria arquivo markdown com metadados"""
        header = f"""---
title: {titulo}
date: {datetime.now().strftime('%Y-%m-%d')}
author: Sistema Multi-Agente de Validação Jurídica
---

"""
        return header + markdown_content

# Instância global do gerenciador de exportação
export_manager = ReportExportManager()