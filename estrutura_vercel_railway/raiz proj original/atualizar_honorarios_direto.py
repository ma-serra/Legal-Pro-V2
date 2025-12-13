#!/usr/bin/env python3
"""
Script direto para atualizar honorários advocatícios
Conecta direto ao PostgreSQL sem carregar Flask
"""

import psycopg2
import random
from decimal import Decimal
import os

# Configuração dos valores
HONORARIO_MIN = 8729.00
HONORARIO_MEDIO = 13508.00
HONORARIO_MAX = 27264.00

def gerar_valor_honorario():
    """
    Gera valor de honorário seguindo distribuição normal
    """
    distribuicao = random.random()
    
    if distribuicao < 0.20:  # 20% - honorários mais baixos
        valor = random.uniform(HONORARIO_MIN, 10000.00)
    elif distribuicao < 0.80:  # 60% - honorários médios (concentração)
        valor = random.uniform(10000.00, 15000.00)
    else:  # 20% - honorários mais altos
        valor = random.uniform(15000.00, HONORARIO_MAX)
    
    return round(valor, 2)

def main():
    # Conectar ao banco
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada")
        return
    
    print("=" * 60)
    print("🔧 ATUALIZAÇÃO DE HONORÁRIOS ADVOCATÍCIOS")
    print("=" * 60)
    print(f"\n📋 Limites configurados:")
    print(f"   Mínimo:  R$ {HONORARIO_MIN:,.2f}")
    print(f"   Média:   R$ {HONORARIO_MEDIO:,.2f}")
    print(f"   Máximo:  R$ {HONORARIO_MAX:,.2f}")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Buscar honorários
        cur.execute("""
            SELECT id, valor 
            FROM historico_pagamentos 
            WHERE tipo_pagamento IN ('Honorários Advocatícios', 'Honorário Advocatício')
        """)
        
        honorarios = cur.fetchall()
        print(f"\n🔍 Encontrados {len(honorarios)} pagamentos de honorários advocatícios")
        
        if not honorarios:
            print("❌ Nenhum honorário encontrado")
            cur.close()
            conn.close()
            return
        
        # Atualizar valores
        valores_atualizados = []
        for id_honorario, valor_antigo in honorarios:
            novo_valor = gerar_valor_honorario()
            valores_atualizados.append(novo_valor)
            
            cur.execute("""
                UPDATE historico_pagamentos 
                SET valor = %s 
                WHERE id = %s
            """, (novo_valor, id_honorario))
        
        conn.commit()
        
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
        if minimo < HONORARIO_MIN:
            print(f"\n⚠️  AVISO: Valor mínimo (R$ {minimo:,.2f}) está abaixo do limite")
        if maximo > HONORARIO_MAX:
            print(f"\n⚠️  AVISO: Valor máximo (R$ {maximo:,.2f}) está acima do limite")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✅ ATUALIZAÇÃO CONCLUÍDA")
    print("=" * 60)

if __name__ == '__main__':
    main()
