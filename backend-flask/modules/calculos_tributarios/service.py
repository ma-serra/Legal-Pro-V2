
from decimal import Decimal
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import logging
import io
from uuid import uuid4

# Imports Database e Models
from main import db
from .models import SimulacaoTributaria

# Imports PDF ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

logger = logging.getLogger(__name__)

class CalculadoraTributariaService:
    """
    Serviço centralizado para cálculos tributários e simulações.
    Suporta: Lucro Presumido, Simples Nacional, Lucro Real (Básico) e Teses de Recuperação.
    """

    # TABELAS SIMPLES NACIONAL 2024/2025 (Simplificada)
    TABELAS_SIMPLES = {
        'ANEXO_I': [
            {'limite': 180000, 'aliquota': 4.00, 'deducao': 0},
            {'limite': 360000, 'aliquota': 7.30, 'deducao': 5940},
            {'limite': 720000, 'aliquota': 9.50, 'deducao': 13860},
            {'limite': 1800000, 'aliquota': 10.70, 'deducao': 22500},
            {'limite': 3600000, 'aliquota': 14.30, 'deducao': 87300},
            {'limite': 4800000, 'aliquota': 19.00, 'deducao': 378000},
        ],
        'ANEXO_III': [
            {'limite': 180000, 'aliquota': 6.00, 'deducao': 0},
            {'limite': 360000, 'aliquota': 11.20, 'deducao': 9360},
            {'limite': 720000, 'aliquota': 13.50, 'deducao': 17640},
            {'limite': 1800000, 'aliquota': 16.00, 'deducao': 35640},
            {'limite': 3600000, 'aliquota': 21.00, 'deducao': 125640},
            {'limite': 4800000, 'aliquota': 33.00, 'deducao': 648000},
        ],
        'ANEXO_V': [
             {'limite': 180000, 'aliquota': 15.50, 'deducao': 0},
             # ... simplificado
        ]
    }

    PRESUNCAO_IRPJ = {
        'comercio': 0.08, 'industria': 0.08, 'servicos': 0.32,
        'revenda_combustiveis': 0.016, 'transporte_carga': 0.08, 'transporte_passageiros': 0.16
    }
    PRESUNCAO_CSLL = {'comercio': 0.12, 'industria': 0.12, 'servicos': 0.32}

    @staticmethod
    def calcular_lucro_presumido(receita_trimestral: float, atividade: str, folha_pagamento: float = 0) -> Dict[str, float]:
        atividade = atividade.lower()
        presuncao_irpj = CalculadoraTributariaService.PRESUNCAO_IRPJ.get(atividade, 0.32)
        presuncao_csll = CalculadoraTributariaService.PRESUNCAO_CSLL.get(atividade, 0.32)

        base_irpj = receita_trimestral * presuncao_irpj
        irpj = base_irpj * 0.15
        adicional_irpj = (base_irpj - 60000) * 0.10 if base_irpj > 60000 else 0
        total_irpj = irpj + adicional_irpj

        base_csll = receita_trimestral * presuncao_csll
        csll = base_csll * 0.09

        pis = receita_trimestral * 0.0065
        cofins = receita_trimestral * 0.03

        iss_icms = receita_trimestral * 0.05 if 'servi' in atividade else receita_trimestral * 0.18
        encargos_folha = folha_pagamento * (0.278 + 0.08)

        total_impostos = total_irpj + csll + pis + cofins + iss_icms + encargos_folha

        return {
            'irpj': float(total_irpj), 'csll': float(csll), 'pis': float(pis), 'cofins': float(cofins),
            'iss_icms_estimado': float(iss_icms), 'encargos_folha': float(encargos_folha),
            'total': float(total_impostos),
            'aliquota_efetiva': float((total_impostos / receita_trimestral) * 100) if receita_trimestral > 0 else 0
        }

    @staticmethod
    def calcular_simples_nacional(receita_mensal: float, receita_bruta_12_meses: float, folha_12_meses: float, anexo: str = 'ANEXO_III') -> Dict[str, float]:
        if anexo not in CalculadoraTributariaService.TABELAS_SIMPLES: anexo = 'ANEXO_III'
        
        fator_r = folha_12_meses / receita_bruta_12_meses if receita_bruta_12_meses > 0 else 0
        anexo_efetivo = anexo
        fator_r_msg = "N/A"
        
        if anexo == 'ANEXO_V' and fator_r >= 0.28:
             anexo_efetivo = 'ANEXO_III'
             fator_r_msg = f"{fator_r:.2%} (Migrou para Anexo III)"

        tabela = CalculadoraTributariaService.TABELAS_SIMPLES.get(anexo_efetivo, CalculadoraTributariaService.TABELAS_SIMPLES['ANEXO_III'])
        
        faixa_encontrada = tabela[-1]
        for faixa in tabela:
            if receita_bruta_12_meses <= faixa['limite']:
                faixa_encontrada = faixa
                break
        
        aliquota_efetiva = ((receita_bruta_12_meses * (faixa_encontrada['aliquota'] / 100)) - faixa_encontrada['deducao']) / receita_bruta_12_meses if receita_bruta_12_meses > 0 else faixa_encontrada['aliquota'] / 100
        valor_devido = receita_mensal * aliquota_efetiva

        return {
            'anexo_usado': anexo_efetivo, 'fator_r': float(fator_r), 'fator_r_status': fator_r_msg,
            'aliquota_nominal': faixa_encontrada['aliquota'], 'aliquota_efetiva': float(aliquota_efetiva * 100),
            'valor_simples': float(valor_devido), 'total': float(valor_devido)
        }

    @staticmethod
    def simular_tese_exclusao_icms(faturamento_mensal: float, aliquota_icms: float, meses: int = 60) -> Dict[str, float]:
        valor_icms_mensal = faturamento_mensal * (aliquota_icms / 100)
        recuperacao_mensal = valor_icms_mensal * 0.0925
        total_recuperar = recuperacao_mensal * meses
        correcao_estimada = total_recuperar * 0.40
        
        return {
            'faturamento_mensal': faturamento_mensal, 'icms_destacado_mensal': valor_icms_mensal,
            'economia_mensal': recuperacao_mensal, 'total_periodo_principal': total_recuperar,
            'correcao_selic_estimada': correcao_estimada, 'total_final_estimado': total_recuperar + correcao_estimada
        }

    # === PERSISTÊNCIA ===

    @staticmethod
    def salvar_simulacao(cliente_nome: str, tipo: str, parametros: Dict, resultado: Dict, usuario_id: Optional[int] = None) -> SimulacaoTributaria:
        try:
            nova_sim = SimulacaoTributaria(
                cliente_nome=cliente_nome,
                tipo_simulacao=tipo,
                parametros_input=parametros,
                resultado_output=resultado,
                usuario_id=usuario_id
            )
            db.session.add(nova_sim)
            db.session.commit()
            return nova_sim
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar simulação: {e}")
            raise

    @staticmethod
    def listar_simulacoes(cliente_nome: Optional[str] = None):
        query = SimulacaoTributaria.query
        if cliente_nome:
            query = query.filter(SimulacaoTributaria.cliente_nome.ilike(f"%{cliente_nome}%"))
        return query.order_by(SimulacaoTributaria.data_criacao.desc()).limit(50).all()

    @staticmethod
    def gerar_pdf_simulacao(simulacao_id: str) -> io.BytesIO:
        simulacao = SimulacaoTributaria.query.get(simulacao_id)
        if not simulacao:
            raise ValueError("Simulação não encontrada")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = styles["Heading1"]
        title_style.alignment = 1
        header_style = styles["Heading3"]
        normal_style = styles["Normal"]
        
        # Header
        elements.append(Paragraph("Relatório de Simulação Tributária", title_style))
        elements.append(Spacer(1, 1*cm))
        
        # Info Cliente
        elements.append(Paragraph(f"Cliente: {simulacao.cliente_nome or 'Não identificado'}", header_style))
        elements.append(Paragraph(f"Data da Simulação: {simulacao.data_criacao.strftime('%d/%m/%Y %H:%M')}", normal_style))
        elements.append(Paragraph(f"Tipo: {simulacao.tipo_simulacao}", normal_style))
        elements.append(Spacer(1, 0.5*cm))

        # Tabela Input
        elements.append(Paragraph("Parâmetros Utilizados:", header_style))
        input_data = [['Parâmetro', 'Valor']]
        for k, v in simulacao.parametros_input.items():
            input_data.append([str(k).replace('_', ' ').title(), str(v)])
        
        t_input = Table(input_data, colWidths=[8*cm, 8*cm])
        t_input.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(t_input)
        elements.append(Spacer(1, 0.5*cm))

        # Tabela Output
        elements.append(Paragraph("Resultados:", header_style))
        output_data = [['Indicador', 'Valor']]
        
        res = simulacao.resultado_output
        def format_val(val):
            if isinstance(val, (int, float)):
                return f"R$ {val:,.2f}" if abs(val) > 100 else f"{val:,.2f}"
            return str(val)

        # Flatten output
        if simulacao.tipo_simulacao == 'COMPARATIVO_REGIME':
            # Estrutura complexa: Simples vs Presumido
            # Vamos mostrar Totais
            if 'simples' in res:
                output_data.append(['--- SIMPLES NACIONAL ---', ''])
                output_data.append(['Total Estimado', format_val(res['simples'].get('total', 0))])
                output_data.append(['Alíquota Efetiva', f"{res['simples'].get('aliquota_efetiva', 0):.2f}%"])
            if 'presumido' in res:
                output_data.append(['--- LUCRO PRESUMIDO ---', ''])
                output_data.append(['Total Estimado', format_val(res['presumido'].get('total', 0))])
                output_data.append(['Alíquota Efetiva', f"{res['presumido'].get('aliquota_efetiva', 0):.2f}%"])
                
        else:
            # Genérico
            for k, v in res.items():
                output_data.append([str(k).replace('_', ' ').title(), format_val(v)])
        
        t_output = Table(output_data, colWidths=[10*cm, 6*cm])
        t_output.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t_output)
        
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("Aviso Legal: Os valores apresentados são estimativas baseadas nos parâmetros informados e na legislação vigente em 2024/2025. Não substituem assessoria contábil detalhada.", styles["Italic"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer
