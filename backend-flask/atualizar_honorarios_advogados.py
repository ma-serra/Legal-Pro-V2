#!/usr/bin/env python3
"""
Script para atualizar honorários advocatícios com valores realistas

Remuneração dos advogados:
- Mínimo: R$ 8.729,00
- Média: R$ 13.508,00
- Máxima: R$ 27.264,00
"""

import os
import sys
from datetime import datetime
import random
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import db, HistoricoPagamento

# Configuração dos valores
HONORARIO_MIN = Decimal('8729.00')
HONORARIO_MEDIO = Decimal('13508.00')
HONORARIO_MAX = Decimal('27264.00')

def gerar_valor_honorario():
    """
    Gera valor de honorário seguindo distribuição normal
    Para média de R$ 13.508, usamos:
    - 60% dos valores entre R$ 10.000 - R$ 15.000
    - 20% dos valores entre R$ 8.729 - R$ 10.000
    - 20% dos valores entre R$ 15.000 - R$ 27.264
    """
    
    distribuicao = random.random()
    
    if distribuicao < 0.20:  # 20% - honorários mais baixos
        valor = random.uniform(float(HONORARIO_MIN), 10000.00)
    elif distribuicao < 0.80:  # 60% - honorários médios (concentração)
        valor = random.uniform(10000.00, 15000.00)
    else:  # 20% - honorários mais altos
        valor = random.uniform(15000.00, float(HONORARIO_MAX))
    
    # Arredondar para 2 casas decimais
    return Decimal(str(round(valor, 2)))

def atualizar_honorarios():
    """Atualiza todos os honorários advocatícios com valores realistas"""
    
    with app.app_context():
        # Buscar todos os pagamentos de honorários advocatícios
        honorarios = HistoricoPagamento.query.filter(
            HistoricoPagamento.tipo_pagamento.in_([
                'Honorários Advocatícios',
                'Honorário Advocatício'
            ])
        ).all()
        
        print(f"\n🔍 Encontrados {len(honorarios)} pagamentos de honorários advocatícios")
        
        if not honorarios:
            print("❌ Nenhum honorário encontrado para atualizar")
            return
        
        # Atualizar valores
        valores_atualizados = []
        for honorario in honorarios:
            novo_valor = gerar_valor_honorario()
            valores_atualizados.append(float(novo_valor))
            honorario.valor = novo_valor
        
        # Commit das mudanças
        try:
            db.session.commit()
            
            # Estatísticas
            minimo = min(valores_atualizados)
            maximo = max(valores_atualizados)
            media = sum(valores_atualizados) / len(valores_atualizados)
            
            print(f"\n✅ {len(honorarios)} honorários atualizados com sucesso!")
            print(f"\n📊 Estatísticas dos novos valores:")
            print(f"   💰 Mínimo:  R$ {minimo:,.2f}")
            print(f"   📊 Média:   R$ {media:,.2f}")
            print(f"   💎 Máximo:  R$ {maximo:,.2f}")
            print(f"\n🎯 Meta de média: R$ 13.508,00")
            print(f"   Diferença: R$ {abs(media - 13508.00):,.2f}")
            
            # Validação
            if minimo < float(HONORARIO_MIN):
                print(f"\n⚠️  AVISO: Valor mínimo (R$ {minimo:,.2f}) está abaixo do limite (R$ {HONORARIO_MIN:,.2f})")
            if maximo > float(HONORARIO_MAX):
                print(f"\n⚠️  AVISO: Valor máximo (R$ {maximo:,.2f}) está acima do limite (R$ {HONORARIO_MAX:,.2f})")
            if abs(media - 13508.00) > 1000:
                print(f"\n⚠️  AVISO: Média (R$ {media:,.2f}) está distante da meta (R$ 13.508,00)")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao atualizar honorários: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 ATUALIZAÇÃO DE HONORÁRIOS ADVOCATÍCIOS")
    print("=" * 60)
    print(f"\n📋 Limites configurados:")
    print(f"   Mínimo:  R$ {HONORARIO_MIN:,.2f}")
    print(f"   Média:   R$ {HONORARIO_MEDIO:,.2f}")
    print(f"   Máximo:  R$ {HONORARIO_MAX:,.2f}")
    
    atualizar_honorarios()
    
    print("\n" + "=" * 60)
    print("✅ ATUALIZAÇÃO CONCLUÍDA")
    print("=" * 60)
