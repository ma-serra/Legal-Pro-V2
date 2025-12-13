#!/usr/bin/env python3
"""
Script para popular a tabela historico_pagamentos com dados reais baseados nos processos existentes.
Gera múltiplos tipos de pagamentos para cada processo de forma realista.
"""

import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

from main import app, db
from models import ProcessoJuridico, HistoricoPagamento


# Tipos de pagamento por área jurídica
TIPOS_PAGAMENTO = {
    'Direito Tributário': [
        'Honorários Advocatícios',
        'Custas Processuais',
        'Depósito Judicial',
        'Taxa de Recurso',
        'Honorários Periciais',
        'Despesas Cartorárias'
    ],
    'Direito Civil': [
        'Honorários Advocatícios',
        'Custas Processuais',
        'Depósito Recursal',
        'Honorários Periciais',
        'Despesas com Diligências',
        'Taxa de Citação'
    ],
    'Direito Trabalhista': [
        'Honorários Advocatícios',
        'Depósito Recursal',
        'Custas Processuais',
        'Acordo Trabalhista',
        'Honorários Periciais',
        'Despesas com Audiência'
    ],
    'default': [
        'Honorários Advocatícios',
        'Custas Processuais',
        'Depósito Judicial',
        'Honorários Periciais',
        'Taxa de Recurso',
        'Despesas com Diligências'
    ]
}

# Formas de pagamento
FORMAS_PAGAMENTO = [
    'Transferência Bancária',
    'Boleto Bancário',
    'PIX',
    'Depósito em Conta',
    'Cheque',
    'Débito em Conta'
]


def gerar_valor_pagamento(tipo_pagamento, valor_causa):
    """Gera um valor realista baseado no tipo de pagamento e valor da causa"""
    
    # Percentuais base por tipo de pagamento
    percentuais = {
        'Honorários Advocatícios': (0.05, 0.20),  # 5% a 20% do valor da causa
        'Acordo': (0.30, 0.70),  # 30% a 70% do valor da causa
        'Depósito Recursal': (0.10, 0.30),  # 10% a 30% do valor da causa
        'Depósito Judicial': (0.05, 0.15),  # 5% a 15% do valor da causa
        'Custas Processuais': (0.005, 0.02),  # 0.5% a 2% do valor da causa
        'Honorários Periciais': (0.02, 0.08),  # 2% a 8% do valor da causa
        'Taxa de Recurso': (0.01, 0.03),  # 1% a 3% do valor da causa
        'default': (0.01, 0.05)  # 1% a 5% do valor da causa
    }
    
    # Pegar percentual apropriado
    min_perc, max_perc = percentuais.get(tipo_pagamento, percentuais['default'])
    
    # Calcular valor
    percentual = random.uniform(min_perc, max_perc)
    valor = float(valor_causa) * percentual
    
    # Arredondar para 2 casas decimais
    return round(valor, 2)


def gerar_data_pagamento(data_inicio, data_fim=None):
    """Gera uma data aleatória entre data_inicio e data_fim (ou hoje)"""
    if data_fim is None:
        data_fim = datetime.now()
    
    # Garantir que data_inicio seja datetime
    if isinstance(data_inicio, str):
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
    
    # Calcular diferença em dias
    delta_dias = (data_fim - data_inicio).days
    
    if delta_dias <= 0:
        return data_inicio
    
    # Gerar data aleatória
    dias_aleatorios = random.randint(0, delta_dias)
    return data_inicio + timedelta(days=dias_aleatorios)


def criar_descricao(tipo_pagamento, processo):
    """Cria uma descrição detalhada para o pagamento"""
    descricoes = {
        'Honorários Advocatícios': f'Pagamento de honorários advocatícios referente ao processo {processo.numero_processo_cnj}',
        'Acordo': f'Pagamento de acordo judicial - Processo {processo.numero_processo_cnj}',
        'Depósito Recursal': f'Depósito recursal - Processo {processo.numero_processo_cnj}',
        'Depósito Judicial': f'Depósito judicial em garantia - Processo {processo.numero_processo_cnj}',
        'Custas Processuais': f'Pagamento de custas processuais - Processo {processo.numero_processo_cnj}',
        'Honorários Periciais': f'Honorários do perito judicial - Processo {processo.numero_processo_cnj}',
        'Taxa de Recurso': f'Taxa de preparo de recurso - Processo {processo.numero_processo_cnj}',
        'Acordo Trabalhista': f'Acordo trabalhista homologado - Processo {processo.numero_processo_cnj}',
        'default': f'Pagamento referente ao processo {processo.numero_processo_cnj}'
    }
    
    return descricoes.get(tipo_pagamento, descricoes['default'])


def popular_historico_pagamentos():
    """Popula a tabela historico_pagamentos com dados realistas"""
    
    with app.app_context():
        print("🚀 Iniciando população da tabela historico_pagamentos...")
        
        # Verificar se já existem pagamentos
        count_existente = HistoricoPagamento.query.count()
        if count_existente > 0:
            print(f"⚠️  Já existem {count_existente} pagamentos na base. Deseja continuar? (s/n)")
            resposta = input().strip().lower()
            if resposta != 's':
                print("❌ Operação cancelada pelo usuário.")
                return
            
            # Limpar tabela
            print("🗑️  Limpando tabela existente...")
            HistoricoPagamento.query.delete()
            db.session.commit()
        
        # Buscar todos os processos
        processos = ProcessoJuridico.query.all()
        total_processos = len(processos)
        
        if total_processos == 0:
            print("❌ Nenhum processo encontrado no banco de dados.")
            return
        
        print(f"📊 Encontrados {total_processos} processos.")
        print("💰 Gerando pagamentos...")
        
        total_pagamentos = 0
        
        for idx, processo in enumerate(processos, 1):
            # Determinar número de pagamentos para este processo (2 a 8 pagamentos)
            num_pagamentos = random.randint(2, 8)
            
            # Obter tipos de pagamento apropriados para a área jurídica
            area = processo.area_juridica_nome or 'default'
            tipos_possiveis = TIPOS_PAGAMENTO.get(area, TIPOS_PAGAMENTO['default'])
            
            # Selecionar tipos aleatórios (sem repetição)
            tipos_selecionados = random.sample(
                tipos_possiveis, 
                min(num_pagamentos, len(tipos_possiveis))
            )
            
            # Criar pagamentos
            for tipo_pagamento in tipos_selecionados:
                # Gerar valor
                valor = gerar_valor_pagamento(tipo_pagamento, processo.valor_causa or 50000)
                
                # Gerar data de pagamento entre data de distribuição e hoje
                data_distribuicao = processo.data_distribuicao or datetime(2023, 6, 1)
                data_pagamento = gerar_data_pagamento(data_distribuicao)
                
                # Criar descrição
                descricao = criar_descricao(tipo_pagamento, processo)
                
                # Forma de pagamento aleatória
                forma = random.choice(FORMAS_PAGAMENTO)
                
                # Criar pagamento
                pagamento = HistoricoPagamento(
                    processo_id=processo.id,
                    data_pagamento=data_pagamento,
                    tipo_pagamento=tipo_pagamento,
                    valor=Decimal(str(valor)),
                    descricao=descricao,
                    forma_pagamento=forma,
                    status='Realizado'
                )
                
                db.session.add(pagamento)
                total_pagamentos += 1
            
            # Commit a cada 50 processos
            if idx % 50 == 0:
                db.session.commit()
                print(f"✅ Processados {idx}/{total_processos} processos ({total_pagamentos} pagamentos)...")
        
        # Commit final
        db.session.commit()
        
        print(f"\n✅ População concluída com sucesso!")
        print(f"📊 Total de processos: {total_processos}")
        print(f"💰 Total de pagamentos criados: {total_pagamentos}")
        print(f"📈 Média de {total_pagamentos/total_processos:.1f} pagamentos por processo")
        
        # Estatísticas
        print("\n📊 Estatísticas de pagamentos por tipo:")
        from sqlalchemy import func
        stats = db.session.query(
            HistoricoPagamento.tipo_pagamento,
            func.count(HistoricoPagamento.id).label('quantidade'),
            func.sum(HistoricoPagamento.valor).label('valor_total')
        ).group_by(HistoricoPagamento.tipo_pagamento).all()
        
        for stat in stats:
            print(f"  • {stat.tipo_pagamento}: {stat.quantidade} pagamentos (R$ {stat.valor_total:,.2f})")


if __name__ == '__main__':
    try:
        popular_historico_pagamentos()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro ao popular histórico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
