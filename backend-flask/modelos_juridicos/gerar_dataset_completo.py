#!/usr/bin/env python3
"""
Dataset Gerador Completo - Legal Pro
Gera dataset com 5000+ casos sintéticos cobrindo todas as 13 áreas jurídicas implementadas
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime

# Definir áreas jurídicas completas
AREAS_JURIDICAS = {
    'civil': {
        'nome': 'Direito Civil',
        'tipo_processo': 'Civil',
        'peso': 0.20,  # 20% dos casos
        'complexidade_media': 'Média',
        'duracao_base': 12
    },
    'consumidor': {
        'nome': 'Direito do Consumidor', 
        'tipo_processo': 'Civil',
        'peso': 0.15,  # 15% dos casos
        'complexidade_media': 'Baixa',
        'duracao_base': 10
    },
    'trabalhista': {
        'nome': 'Direito Trabalhista',
        'tipo_processo': 'Trabalhista', 
        'peso': 0.18,  # 18% dos casos
        'complexidade_media': 'Média',
        'duracao_base': 8
    },
    'agrario': {
        'nome': 'Direito Agrário',
        'tipo_processo': 'Agrário',
        'peso': 0.12,  # 12% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 15
    },
    'penal': {
        'nome': 'Direito Penal',
        'tipo_processo': 'Penal',
        'peso': 0.10,  # 10% dos casos
        'complexidade_media': 'Alta', 
        'duracao_base': 18
    },
    'tributario': {
        'nome': 'Direito Tributário',
        'tipo_processo': 'Tributário',
        'peso': 0.08,  # 8% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 24
    },
    'empresarial': {
        'nome': 'Direito Empresarial',
        'tipo_processo': 'Empresarial',
        'peso': 0.06,  # 6% dos casos
        'complexidade_media': 'Média',
        'duracao_base': 14
    },
    'administrativo': {
        'nome': 'Direito Administrativo',
        'tipo_processo': 'Administrativo',
        'peso': 0.05,  # 5% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 20
    },
    'previdenciario': {
        'nome': 'Direito Previdenciário',
        'tipo_processo': 'Previdenciário',
        'peso': 0.04,  # 4% dos casos
        'complexidade_media': 'Média',
        'duracao_base': 16
    },
    'ambiental': {
        'nome': 'Direito Ambiental',
        'tipo_processo': 'Ambiental',
        'peso': 0.01,  # 1% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 22
    },
    'constitucional': {
        'nome': 'Direito Constitucional',
        'tipo_processo': 'Constitucional',
        'peso': 0.005,  # 0.5% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 30
    },
    'eleitoral': {
        'nome': 'Direito Eleitoral',
        'tipo_processo': 'Eleitoral',
        'peso': 0.003,  # 0.3% dos casos
        'complexidade_media': 'Média',
        'duracao_base': 6
    },
    'militar': {
        'nome': 'Direito Militar',
        'tipo_processo': 'Militar',
        'peso': 0.002,  # 0.2% dos casos
        'complexidade_media': 'Alta',
        'duracao_base': 12
    }
}

# Estados brasileiros
FOROS = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 'ES', 'MT', 'MS', 'DF']

# Estratégias de defesa por área
ESTRATEGIAS_POR_AREA = {
    'civil': ['prescricao', 'nulidade_prova', 'ilegitimidade'],
    'consumidor': ['nulidade_prova', 'acordo_proposto', 'ilegitimidade'],
    'trabalhista': ['prescricao', 'nulidade_prova', 'acordo_proposto'],
    'agrario': ['prescricao', 'ilegitimidade', 'impugnacao_pericia'],
    'penal': ['nulidade_prova', 'ilegitimidade', 'incompetencia'],
    'tributario': ['prescricao', 'nulidade_prova', 'ilegitimidade'],
    'empresarial': ['nulidade_prova', 'acordo_proposto', 'conexao'],
    'administrativo': ['incompetencia', 'nulidade_prova', 'ilegitimidade'],
    'previdenciario': ['prescricao', 'impugnacao_pericia', 'acordo_proposto'],
    'ambiental': ['incompetencia', 'impugnacao_pericia', 'conexao'],
    'constitucional': ['incompetencia', 'nulidade_prova', 'conexao'],
    'eleitoral': ['decadencia', 'incompetencia', 'nulidade_prova'],
    'militar': ['incompetencia', 'nulidade_prova', 'ilegitimidade']
}

def gerar_valor_causa(area):
    """Gerar valor da causa baseado na área"""
    ranges = {
        'civil': (5000, 500000),
        'consumidor': (1000, 50000),
        'trabalhista': (2000, 100000),
        'agrario': (50000, 5000000),
        'penal': (0, 0),  # Penal não tem valor econômico
        'tributario': (10000, 10000000),
        'empresarial': (100000, 50000000),
        'administrativo': (5000, 1000000),
        'previdenciario': (3000, 200000),
        'ambiental': (100000, 100000000),
        'constitucional': (0, 0),
        'eleitoral': (0, 0),
        'militar': (0, 0)
    }
    
    min_val, max_val = ranges.get(area, (1000, 100000))
    if min_val == 0 and max_val == 0:
        return 0
    return random.randint(min_val, max_val)

def gerar_descricao_caso(area):
    """Gerar descrição sintética baseada na área"""
    descricoes = {
        'civil': [
            'Ação de indenização por danos morais e materiais decorrente de acidente de trânsito',
            'Cobrança de dívida com pedido de penhora de bens',
            'Ação de despejo por falta de pagamento',
            'Rescisão contratual com pedido de restituição de valores'
        ],
        'consumidor': [
            'Cobrança indevida de tarifa bancária com pedido de repetição',
            'Vício em produto com pedido de substituição',
            'Propaganda enganosa com pedido de indenização',
            'Negativação indevida do nome do consumidor'
        ],
        'trabalhista': [
            'Reclamação trabalhista com pedido de horas extras',
            'Ação de rescisão indireta por assédio moral',
            'Cobrança de verbas rescisórias não pagas',
            'Equiparação salarial entre empregados'
        ],
        'agrario': [
            'Ação de usucapião de imóvel rural',
            'Desapropriação para fins de reforma agrária',
            'Conflito de terras entre posseiros',
            'Regularização fundiária de propriedade rural'
        ],
        'penal': [
            'Ação penal por crime contra o patrimônio',
            'Processo por lesão corporal dolosa',
            'Investigação de crime tributário',
            'Ação penal por crime ambiental'
        ],
        'tributario': [
            'Mandado de segurança contra cobrança de ICMS',
            'Execução fiscal de débito previdenciário',
            'Ação anulatória de auto de infração',
            'Repetição de indébito tributário'
        ]
    }
    
    opcoes = descricoes.get(area, ['Processo jurídico na área de ' + area])
    return random.choice(opcoes)

def gerar_dataset_completo(num_casos=5000):
    """Gerar dataset completo com todas as áreas jurídicas"""
    
    casos = []
    
    # Calcular quantidade de casos por área baseado no peso
    for area_key, config in AREAS_JURIDICAS.items():
        num_casos_area = max(1, int(num_casos * config['peso']))
        
        for _ in range(num_casos_area):
            # Definir estratégias de defesa para esta área
            estrategias_disponiveis = ESTRATEGIAS_POR_AREA.get(area_key, ['prescricao', 'nulidade_prova'])
            
            # Decidir quais estratégias aplicar (1-3 estratégias por caso)
            num_estrategias = random.randint(1, min(3, len(estrategias_disponiveis)))
            estrategias_caso = random.sample(estrategias_disponiveis, num_estrategias)
            
            # Definir probabilidade de sucesso baseada na área e estratégias
            prob_base = {
                'civil': 0.65,
                'consumidor': 0.75,
                'trabalhista': 0.70,
                'agrario': 0.55,
                'penal': 0.45,
                'tributario': 0.60,
                'empresarial': 0.68,
                'administrativo': 0.52,
                'previdenciario': 0.72,
                'ambiental': 0.58,
                'constitucional': 0.48,
                'eleitoral': 0.62,
                'militar': 0.50
            }
            
            probabilidade = prob_base[area_key] + (num_estrategias * 0.05)  # Bonus por mais estratégias
            probabilidade = min(0.95, max(0.15, probabilidade))  # Limitar entre 15% e 95%
            
            # Gerar complexidade com variação
            complexidades = ['Baixa', 'Média', 'Alta']
            if config['complexidade_media'] == 'Baixa':
                complexidade = random.choices(complexidades, weights=[60, 30, 10])[0]
            elif config['complexidade_media'] == 'Média':
                complexidade = random.choices(complexidades, weights=[25, 50, 25])[0]
            else:  # Alta
                complexidade = random.choices(complexidades, weights=[10, 30, 60])[0]
            
            # Ajustar duração baseada na complexidade
            duracao = config['duracao_base']
            if complexidade == 'Alta':
                duracao += random.randint(3, 8)
            elif complexidade == 'Baixa':
                duracao -= random.randint(1, 4)
                duracao = max(1, duracao)
            
            # Criar o caso
            caso = {
                'area': area_key,
                'area_juridica': config['nome'],
                'tipo_processo': config['tipo_processo'],
                'foro': random.choice(FOROS),
                'valor_causa': gerar_valor_causa(area_key),
                'complexidade': complexidade,
                'duracao_esperada': duracao,
                'descricao': gerar_descricao_caso(area_key),
                'probabilidade_sucesso': round(probabilidade, 3),
                
                # Estratégias de defesa (1 se aplicável, 0 se não)
                'prescricao': 1 if 'prescricao' in estrategias_caso else 0,
                'nulidade_prova': 1 if 'nulidade_prova' in estrategias_caso else 0,
                'ilegitimidade': 1 if 'ilegitimidade' in estrategias_caso else 0,
                'impugnacao_pericia': 1 if 'impugnacao_pericia' in estrategias_caso else 0,
                'acordo_proposto': 1 if 'acordo_proposto' in estrategias_caso else 0,
                'decadencia': 1 if 'decadencia' in estrategias_caso else 0,
                'incompetencia': 1 if 'incompetencia' in estrategias_caso else 0,
                'conexao': 1 if 'conexao' in estrategias_caso else 0
            }
            
            casos.append(caso)
    
    # Criar DataFrame e embaralhar os casos
    df = pd.DataFrame(casos)
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    print("🔄 Gerando dataset completo com 5000+ casos jurídicos...")
    
    # Gerar dataset
    df_completo = gerar_dataset_completo(5000)
    
    # Salvar arquivo
    timestamp = int(datetime.now().timestamp())
    filename = f"dataset_defesas_completo_{timestamp}.csv"
    df_completo.to_csv(f"modelos_juridicos/data/{filename}", index=False, encoding='utf-8')
    
    # Estatísticas do dataset
    print(f"✅ Dataset gerado com {len(df_completo)} casos")
    print(f"📁 Arquivo salvo como: {filename}")
    print("\n📊 Distribuição por área:")
    
    distribuicao = df_completo['area_juridica'].value_counts()
    for area, count in distribuicao.items():
        percentual = (count / len(df_completo)) * 100
        print(f"  {area}: {count} casos ({percentual:.1f}%)")
    
    print(f"\n🎯 Estados cobertos: {sorted(df_completo['foro'].unique())}")
    print(f"🎯 Tipos de processo: {sorted(df_completo['tipo_processo'].unique())}")
    print(f"🎯 Complexidades: {sorted(df_completo['complexidade'].unique())}")
    
    # Estatísticas das estratégias
    estrategias_cols = ['prescricao', 'nulidade_prova', 'ilegitimidade', 'impugnacao_pericia', 
                       'acordo_proposto', 'decadencia', 'incompetencia', 'conexao']
    
    print(f"\n🛡️ Uso de estratégias de defesa:")
    for estrategia in estrategias_cols:
        uso = df_completo[estrategia].sum()
        percentual = (uso / len(df_completo)) * 100
        print(f"  {estrategia}: {uso} casos ({percentual:.1f}%)")
    
    print(f"\n✅ Dataset completo pronto para uso em produção!")