"""
Sistema de Exportação de Relatórios para Dashboards Fintech
===============================================================

Gera relatórios profissionais em PDF e Excel para todos os 9 dashboards estratégicos.
"""

import io
import os
import base64
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfgen import canvas
import pandas as pd
from io import BytesIO
from PIL import Image as PILImage


class FintechReportExporter:
    """
    Exportador unificado de relatórios para dashboards Fintech
    """
    
    DASHBOARD_NAMES = {
        'performance-overview': 'CEO Performance Overview',
        'strategic-intelligence': 'Strategic Intelligence Dashboard',
        'case-success-predictor': 'Case Success Predictor',
        'performance-analysis': 'Performance Analysis Dashboard',
        'defense-strategy-optimizer': 'Defense Strategy Optimizer',
        'case-management-intelligence': 'Case Management Intelligence',
        'ai-legal-forecasting': 'AI-Powered Legal Forecasting',
        'success-optimization-engine': 'Success Optimization Engine',
        'competitive-intelligence': 'Competitive Intelligence Dashboard'
    }
    
    def __init__(self, dataset=None):
        """
        Inicializa o exportador com o dataset
        
        Args:
            dataset: DataFrame do Pandas com os dados do Fintech
        """
        self.dataset = dataset
        self.styles = getSampleStyleSheet()
        self._configure_styles()
    
    def _configure_styles(self):
        """Configura estilos customizados para os relatórios"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b576f'),
            spaceAfter=20
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#000000')
        ))
    
    def _process_base64_image(self, base64_data, max_width=16*cm, max_height=10*cm):
        """
        Processa imagem base64 e retorna objeto Image do ReportLab
        
        Args:
            base64_data: String base64 da imagem (com ou sem prefixo data:image/...)
            max_width: Largura máxima em cm
            max_height: Altura máxima em cm
            
        Returns:
            Image: Objeto Image do ReportLab ou None se falhar
        """
        try:
            # Remover prefixo data:image/...;base64, se presente
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decodificar base64
            image_data = base64.b64decode(base64_data)
            
            # Criar objeto Image do PIL para obter dimensões
            pil_image = PILImage.open(BytesIO(image_data))
            
            # Calcular proporções mantendo aspect ratio
            img_width, img_height = pil_image.size
            aspect = img_height / float(img_width)
            
            # Ajustar tamanho
            if max_width / max_height > aspect:
                width = max_height / aspect
                height = max_height
            else:
                width = max_width
                height = max_width * aspect
            
            # Criar objeto Image do ReportLab
            img = Image(BytesIO(image_data), width=width, height=height)
            
            return img
            
        except Exception as e:
            print(f"⚠️ Erro ao processar imagem base64: {e}")
            return None
    
    def export_to_pdf(self, dashboard_name, data):
        """
        Exporta relatório de dashboard em PDF
        
        Args:
            dashboard_name: Nome do dashboard
            data: Dados do dashboard (dict)
            
        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Elementos do documento
        elements = []
        
        # Cabeçalho
        title = self.DASHBOARD_NAMES.get(dashboard_name, dashboard_name.replace('-', ' ').title())
        elements.append(Paragraph(f"<b>Relatório: {title}</b>", self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.5*cm))
        
        # Adicionar gráficos visuais se disponíveis
        charts = data.get('charts', {})
        if charts:
            print(f"📊 Processando {len(charts)} gráficos para inclusão no PDF")
            elements.append(Paragraph("<b>Análise Visual</b>", self.styles['CustomSubtitle']))
            elements.append(Spacer(1, 0.3*cm))
            
            chart_count = 0
            for chart_id, chart_base64 in charts.items():
                if chart_base64:
                    img = self._process_base64_image(chart_base64, max_width=18*cm, max_height=11*cm)
                    if img:
                        # Adicionar título do gráfico
                        chart_title = chart_id.replace('_', ' ').title()
                        elements.append(Paragraph(f"<i>{chart_title}</i>", self.styles['CustomBody']))
                        elements.append(Spacer(1, 0.2*cm))
                        
                        # Adicionar imagem do gráfico
                        elements.append(img)
                        elements.append(Spacer(1, 0.5*cm))
                        chart_count += 1
                        
                        # Adicionar quebra de página a cada 2 gráficos para melhor layout
                        if chart_count % 2 == 0:
                            elements.append(PageBreak())
            
            # Se adicionamos gráficos, adicionar quebra de página antes do conteúdo textual
            if chart_count > 0:
                elements.append(PageBreak())
        
        # Adicionar conteúdo específico do dashboard
        if dashboard_name == 'performance-overview':
            elements.extend(self._generate_performance_overview_content(data))
        elif dashboard_name == 'strategic-intelligence':
            elements.extend(self._generate_strategic_intelligence_content(data))
        elif dashboard_name == 'case-success-predictor':
            elements.extend(self._generate_case_predictor_content(data))
        elif dashboard_name == 'performance-analysis':
            elements.extend(self._generate_performance_analysis_content(data))
        elif dashboard_name == 'defense-strategy-optimizer':
            elements.extend(self._generate_defense_optimizer_content(data))
        elif dashboard_name == 'case-management-intelligence':
            elements.extend(self._generate_case_management_content(data))
        elif dashboard_name == 'ai-legal-forecasting':
            elements.extend(self._generate_forecasting_content(data))
        elif dashboard_name == 'success-optimization-engine':
            elements.extend(self._generate_optimization_engine_content(data))
        elif dashboard_name == 'competitive-intelligence':
            elements.extend(self._generate_competitive_intelligence_content(data))
        else:
            elements.extend(self._generate_generic_content(data))
        
        # Rodapé
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(
            "<i>Este relatório foi gerado automaticamente pelo Sistema Fintech Analytics</i>",
            self.styles['CustomBody']
        ))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    def export_to_excel(self, dashboard_name, data):
        """
        Exporta relatório de dashboard em Excel
        
        Args:
            dashboard_name: Nome do dashboard
            data: Dados do dashboard (dict)
            
        Returns:
            BytesIO: Buffer com o Excel gerado
        """
        buffer = BytesIO()
        
        # Criar Excel com Pandas
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formatos
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'bg_color': '#3b576f',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter'
            })
            
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#d9d9d9',
                'border': 1
            })
            
            # Criar página de resumo
            summary_data = self._prepare_summary_data(dashboard_name, data)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Formatar página de resumo
            worksheet = writer.sheets['Resumo']
            worksheet.set_column('A:B', 30)
            worksheet.write('A1', self.DASHBOARD_NAMES.get(dashboard_name, dashboard_name), title_format)
            
            # Criar páginas adicionais baseadas no dashboard
            if dashboard_name == 'performance-overview':
                self._add_performance_overview_sheets(writer, data)
            elif dashboard_name == 'strategic-intelligence':
                self._add_strategic_intelligence_sheets(writer, data)
            elif dashboard_name == 'defense-strategy-optimizer':
                self._add_defense_optimizer_sheets(writer, data)
            # Adicionar mais conforme necessário
        
        buffer.seek(0)
        return buffer
    
    # ========================================
    # Métodos para conteúdo específico em PDF
    # ========================================
    
    def _generate_performance_overview_content(self, data):
        """Gera conteúdo para Performance Overview"""
        elements = []
        
        elements.append(Paragraph("<b>Indicadores Principais</b>", self.styles['CustomSubtitle']))
        
        # Tabela de KPIs
        kpi_data = [
            ['Métrica', 'Valor', 'Tendência'],
            ['Taxa de Sucesso', f"{data.get('success_rate', 0):.1f}%", '↑'],
            ['Total de Casos', f"{data.get('total_cases', 0):,}", '↑'],
            ['Valor Economizado', f"R$ {data.get('value_saved', 0):,.2f}", '↑'],
            ['ROI', f"{data.get('roi', 0):.1f}%", '↑']
        ]
        
        table = Table(kpi_data, colWidths=[8*cm, 6*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b576f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _generate_strategic_intelligence_content(self, data):
        """Gera conteúdo para Strategic Intelligence"""
        elements = []
        
        elements.append(Paragraph("<b>Análise Estratégica</b>", self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            f"Total de processos analisados: {data.get('total_cases', 0):,}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _generate_case_predictor_content(self, data):
        """Gera conteúdo para Case Success Predictor"""
        elements = []
        
        elements.append(Paragraph("<b>Predição de Sucesso de Casos</b>", self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            f"Precisão do modelo: {data.get('model_accuracy', 0):.1f}%",
            self.styles['CustomBody']
        ))
        
        return elements
    
    def _generate_performance_analysis_content(self, data):
        """Gera conteúdo para Performance Analysis"""
        elements = []
        
        elements.append(Paragraph("<b>Análise de Performance</b>", self.styles['CustomSubtitle']))
        
        return elements
    
    def _generate_defense_optimizer_content(self, data):
        """Gera conteúdo para Defense Strategy Optimizer"""
        elements = []
        
        elements.append(Paragraph("<b>Estratégias de Defesa Otimizadas</b>", self.styles['CustomSubtitle']))
        
        if 'strategies' in data and data['strategies']:
            strategy_data = [['Estratégia', 'Efetividade', 'Prioridade']]
            for strategy in data['strategies']:
                strategy_data.append([
                    strategy.get('name', 'N/A'),
                    f"{strategy.get('effectiveness', 0):.1f}%",
                    strategy.get('priority', 'N/A')
                ])
            
            table = Table(strategy_data, colWidths=[10*cm, 4*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b576f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        return elements
    
    def _generate_case_management_content(self, data):
        """Gera conteúdo para Case Management Intelligence"""
        elements = []
        
        elements.append(Paragraph("<b>Gestão Inteligente de Casos</b>", self.styles['CustomSubtitle']))
        
        return elements
    
    def _generate_forecasting_content(self, data):
        """Gera conteúdo para AI Legal Forecasting"""
        elements = []
        
        elements.append(Paragraph("<b>Previsões Legais com IA</b>", self.styles['CustomSubtitle']))
        
        return elements
    
    def _generate_optimization_engine_content(self, data):
        """Gera conteúdo para Success Optimization Engine"""
        elements = []
        
        elements.append(Paragraph("<b>Motor de Otimização de Sucesso</b>", self.styles['CustomSubtitle']))
        
        return elements
    
    def _generate_competitive_intelligence_content(self, data):
        """Gera conteúdo para Competitive Intelligence"""
        elements = []
        
        elements.append(Paragraph("<b>Inteligência Competitiva</b>", self.styles['CustomSubtitle']))
        
        return elements
    
    def _generate_generic_content(self, data):
        """Gera conteúdo genérico para outros dashboards"""
        elements = []
        
        elements.append(Paragraph("<b>Resumo do Dashboard</b>", self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            "Este relatório contém os dados principais do dashboard selecionado.",
            self.styles['CustomBody']
        ))
        
        return elements
    
    # ========================================
    # Métodos auxiliares para Excel
    # ========================================
    
    def _prepare_summary_data(self, dashboard_name, data):
        """Prepara dados de resumo para Excel"""
        summary = {
            'Métrica': [],
            'Valor': []
        }
        
        # Adicionar informações gerais
        summary['Métrica'].append('Dashboard')
        summary['Valor'].append(self.DASHBOARD_NAMES.get(dashboard_name, dashboard_name))
        
        summary['Métrica'].append('Data de Geração')
        summary['Valor'].append(datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        # Adicionar métricas específicas
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                summary['Métrica'].append(key.replace('_', ' ').title())
                summary['Valor'].append(value)
        
        return summary
    
    def _add_performance_overview_sheets(self, writer, data):
        """Adiciona planilhas específicas para Performance Overview"""
        # Adicionar planilha de KPIs
        if 'kpis' in data:
            df_kpis = pd.DataFrame([data['kpis']])
            df_kpis.to_excel(writer, sheet_name='KPIs', index=False)
    
    def _add_strategic_intelligence_sheets(self, writer, data):
        """Adiciona planilhas específicas para Strategic Intelligence"""
        pass
    
    def _add_defense_optimizer_sheets(self, writer, data):
        """Adiciona planilhas específicas para Defense Optimizer"""
        if 'strategies' in data and data['strategies']:
            df_strategies = pd.DataFrame(data['strategies'])
            df_strategies.to_excel(writer, sheet_name='Estratégias', index=False)
