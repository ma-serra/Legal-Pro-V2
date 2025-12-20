
from decimal import Decimal
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class CalculadoraTributariaService:
    """
    Serviço centralizado para cálculos tributários e simulações.
    Suporta: Lucro Presumido, Simples Nacional, Lucro Real (Básico) e Teses de Recuperação.
    """

    # TABELAS SIMPLES NACIONAL 2024/2025 (Simplificada - Faixas principais)
    TABELAS_SIMPLES = {
        'ANEXO_I': [ # Comércio
            {'limite': 180000, 'aliquota': 4.00, 'deducao': 0},
            {'limite': 360000, 'aliquota': 7.30, 'deducao': 5940},
            {'limite': 720000, 'aliquota': 9.50, 'deducao': 13860},
            {'limite': 1800000, 'aliquota': 10.70, 'deducao': 22500},
            {'limite': 3600000, 'aliquota': 14.30, 'deducao': 87300},
            {'limite': 4800000, 'aliquota': 19.00, 'deducao': 378000},
        ],
        'ANEXO_III': [ # Serviços
            {'limite': 180000, 'aliquota': 6.00, 'deducao': 0},
            {'limite': 360000, 'aliquota': 11.20, 'deducao': 9360},
            {'limite': 720000, 'aliquota': 13.50, 'deducao': 17640},
            {'limite': 1800000, 'aliquota': 16.00, 'deducao': 35640},
            {'limite': 3600000, 'aliquota': 21.00, 'deducao': 125640},
            {'limite': 4800000, 'aliquota': 33.00, 'deducao': 648000},
        ],
        # Adicionar outros anexos conforme necessidade
    }

    # PERCENTUAIS DE PRESUNÇÃO (LUCRO PRESUMIDO)
    PRESUNCAO_IRPJ = {
        'comercio': 0.08,
        'industria': 0.08,
        'servicos': 0.32,
        'revenda_combustiveis': 0.016,
        'transporte_carga': 0.08,
        'transporte_passageiros': 0.16
    }

    PRESUNCAO_CSLL = {
        'comercio': 0.12,
        'industria': 0.12,
        'servicos': 0.32
    }

    @staticmethod
    def calcular_lucro_presumido(
        receita_trimestral: float,
        atividade: str,
        folha_pagamento: float = 0
    ) -> Dict[str, float]:
        """
        Calcula carga tributária estimada no Lucro Presumido (Trimestral).
        """
        atividade = atividade.lower()
        presuncao_irpj = CalculadoraTributariaService.PRESUNCAO_IRPJ.get(atividade, 0.32)
        presuncao_csll = CalculadoraTributariaService.PRESUNCAO_CSLL.get(atividade, 0.32)

        # 1. IRPJ
        base_irpj = receita_trimestral * presuncao_irpj
        irpj = base_irpj * 0.15
        adicional_irpj = (base_irpj - 60000) * 0.10 if base_irpj > 60000 else 0
        total_irpj = irpj + adicional_irpj

        # 2. CSLL
        base_csll = receita_trimestral * presuncao_csll
        csll = base_csll * 0.09

        # 3. PIS/COFINS (Cumulativo)
        pis = receita_trimestral * 0.0065
        cofins = receita_trimestral * 0.03

        # 4. ISS/ICMS (Estimativa)
        # Se for serviço -> ISS (ex: 5%), Se for comércio -> ICMS (ex: 18% com créditos, efetivo varia, usar input se tiver)
        iss_icms = 0
        if 'servi' in atividade:
             iss_icms = receita_trimestral * 0.05 # ISS Médio
        else:
             iss_icms = receita_trimestral * 0.18 # ICMS Cheio (pior cenário)
        
        # 5. Folha (CPP + FGTS + Outros) - Presumido paga CPP 20%
        # CPP Patronal (20%) + RAT (~2%) + Terceiros (~5.8%) = ~27.8%
        # FGTS (8%)
        encargos_folha = folha_pagamento * (0.278 + 0.08)

        total_impostos = total_irpj + csll + pis + cofins + iss_icms + encargos_folha

        return {
            'irpj': float(total_irpj),
            'csll': float(csll),
            'pis': float(pis),
            'cofins': float(cofins),
            'iss_icms_estimado': float(iss_icms),
            'encargos_folha': float(encargos_folha),
            'total': float(total_impostos),
            'aliquota_efetiva': float((total_impostos / receita_trimestral) * 100) if receita_trimestral > 0 else 0
        }

    @staticmethod
    def calcular_simples_nacional(
        receita_mensal: float,
        receita_bruta_12_meses: float,
        folha_12_meses: float,
        anexo: str = 'ANEXO_III'
    ) -> Dict[str, float]:
        """
        Calcula Simples Nacional com base na RBT12 e Fator R.
        """
        if anexo not in ['ANEXO_I', 'ANEXO_II', 'ANEXO_III', 'ANEXO_IV', 'ANEXO_V']:
             anexo = 'ANEXO_III' # Default Serviços

        # Fator R
        fator_r = folha_12_meses / receita_bruta_12_meses if receita_bruta_12_meses > 0 else 0
        
        # Ajuste de anexo por Fator R (III vs V)
        anexo_efetivo = anexo
        fator_r_msg = "N/A"
        
        if anexo == 'ANEXO_III' and fator_r < 0.28:
             # Sujeito ao fator R pode ir para o V? Na verdade III é padrão, sujeito a V se atividade intelectual.
             # O usuário passou o anexo base. Vamos assumir Anexo III standard.
             # Se for atividade intelectual (V), e fator R >= 28%, vai pro III.
             # Se for V e fator R < 28%, fica no V.
             pass
        elif anexo == 'ANEXO_V' and fator_r >= 0.28:
             anexo_efetivo = 'ANEXO_III'
             fator_r_msg = f"{fator_r:.2%} (Migrou para Anexo III)"

        tabela = CalculadoraTributariaService.TABELAS_SIMPLES.get(anexo_efetivo, CalculadoraTributariaService.TABELAS_SIMPLES['ANEXO_III'])
        
        # Encontrar faixa
        faixa_encontrada = tabela[-1] # Default ultima
        for faixa in tabela:
            if receita_bruta_12_meses <= faixa['limite']:
                faixa_encontrada = faixa
                break
        
        # Fórmula: ((RBT12 x Aliq) - PD) / RBT12
        if receita_bruta_12_meses > 0:
            aliquota_efetiva = ((receita_bruta_12_meses * (faixa_encontrada['aliquota'] / 100)) - faixa_encontrada['deducao']) / receita_bruta_12_meses
        else:
            aliquota_efetiva = faixa_encontrada['aliquota'] / 100
            
        valor_devido = receita_mensal * aliquota_efetiva

        return {
            'anexo_usado': anexo_efetivo,
            'fator_r': float(fator_r),
            'fator_r_status': fator_r_msg,
            'aliquota_nominal': faixa_encontrada['aliquota'],
            'aliquota_efetiva': float(aliquota_efetiva * 100),
            'valor_simples': float(valor_devido),
            'total': float(valor_devido)
        }

    @staticmethod
    def simular_tese_exclusao_icms(
        faturamento_mensal: float,
        aliquota_icms: float,
        meses: int = 60
    ) -> Dict[str, float]:
        """
        Simula o valor a recuperar na tese da Exclusão do ICMS da base do PIS/COFINS (Tese do Século).
        Considera regime Lucro Real (9.25%) ou Presumido (3.65%).
        """
        # Exemplo conservador: Lucro Real (9.25%)
        # Base de cálculo reduzida = ICMS destacado
        valor_icms_mensal = faturamento_mensal * (aliquota_icms / 100)
        
        # Recuperação PIS (1.65%) + COFINS (7.60%) = 9.25% sobre o ICMS
        recuperacao_mensal = valor_icms_mensal * 0.0925
        
        total_recuperar = recuperacao_mensal * meses
        
        # Adicionar correção SELIC estimada (ex: 40% acumulado em 5 anos)
        correcao_estimada = total_recuperar * 0.40
        
        return {
            'faturamento_mensal': faturamento_mensal,
            'icms_destacado_mensal': valor_icms_mensal,
            'reducao_base_mensal': valor_icms_mensal,
            'economia_mensal': recuperacao_mensal,
            'total_periodo_principal': total_recuperar,
            'correcao_selic_estimada': correcao_estimada,
            'total_final_estimado': total_recuperar + correcao_estimada
        }
