#!/usr/bin/env python3
"""
Script para revisar e validar o dataset de 2000 processos jurídicos
"""
import pandas as pd
import numpy as np
from datetime import datetime

def revisar_dataset():
    print("🔍 ANÁLISE COMPLETA DO DATASET JURÍDICO")
    print("="*60)
    
    # Carregar dataset
    df = pd.read_csv('modelos_juridicos/data/dataset_defesas_1756659091707.csv')
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de processos: {len(df)}")
    print(f"   Total de colunas: {len(df.columns)}")
    print(f"   Colunas: {', '.join(df.columns.tolist())}")
    print()
    
    # Verificar dados faltantes
    print("🔍 ANÁLISE DE DADOS FALTANTES:")
    missing_data = df.isnull().sum()
    for col, missing in missing_data.items():
        if missing > 0:
            print(f"   ❌ {col}: {missing} valores faltantes ({missing/len(df)*100:.2f}%)")
    
    if missing_data.sum() == 0:
        print("   ✅ Nenhum dado faltante encontrado!")
    print()
    
    # Distribuição por área
    print("📈 DISTRIBUIÇÃO POR ÁREA JURÍDICA:")
    areas = df['area'].value_counts()
    for area, count in areas.items():
        porcentagem = count/len(df)*100
        print(f"   {area}: {count} casos ({porcentagem:.1f}%)")
    print()
    
    # Distribuição por foro
    print("🏛️  DISTRIBUIÇÃO POR FORO:")
    foros = df['foro'].value_counts()
    for foro, count in foros.items():
        porcentagem = count/len(df)*100
        print(f"   {foro}: {count} casos ({porcentagem:.1f}%)")
    print()
    
    # Distribuição por juiz
    print("⚖️  DISTRIBUIÇÃO POR JUIZ:")
    juizes = df['juiz'].value_counts()
    for juiz, count in juizes.items():
        porcentagem = count/len(df)*100
        print(f"   {juiz}: {count} casos ({porcentagem:.1f}%)")
    print()
    
    # Análise de valores monetários
    print("💰 ANÁLISE DE VALORES DA CAUSA:")
    print(f"   Valor mínimo: R$ {df['valor_causa'].min():,.2f}")
    print(f"   Valor máximo: R$ {df['valor_causa'].max():,.2f}")
    print(f"   Valor médio: R$ {df['valor_causa'].mean():,.2f}")
    print(f"   Valor mediano: R$ {df['valor_causa'].median():,.2f}")
    print()
    
    # Análise temporal
    print("📅 ANÁLISE TEMPORAL:")
    anos = df['ano'].value_counts().sort_index()
    for ano, count in anos.items():
        porcentagem = count/len(df)*100
        print(f"   {int(ano)}: {count} casos ({porcentagem:.1f}%)")
    print()
    
    # Análise de defesas
    print("🛡️  ANÁLISE DE ESTRATÉGIAS DE DEFESA:")
    defesas = ['prescricao', 'impugnacao_pericia', 'nulidade_prova', 'acordo_proposto', 'ilegitimidade', 'decadencia']
    
    for defesa in defesas:
        total_casos = df[defesa].sum()
        porcentagem = total_casos/len(df)*100
        print(f"   {defesa.replace('_', ' ').title()}: {total_casos} casos ({porcentagem:.1f}%)")
    print()
    
    # Taxa de vitória
    print("🏆 ANÁLISE DE RESULTADOS:")
    vitorias = df['vitoria'].sum()
    taxa_vitoria = vitorias/len(df)*100
    print(f"   Vitórias: {vitorias} casos ({taxa_vitoria:.1f}%)")
    print(f"   Derrotas: {len(df) - vitorias} casos ({100-taxa_vitoria:.1f}%)")
    print()
    
    # Taxa de vitória por área
    print("📊 TAXA DE VITÓRIA POR ÁREA:")
    for area in df['area'].unique():
        area_df = df[df['area'] == area]
        taxa = area_df['vitoria'].mean() * 100
        total = len(area_df)
        vitorias_area = area_df['vitoria'].sum()
        print(f"   {area}: {vitorias_area}/{total} ({taxa:.1f}%)")
    print()
    
    # Validação de integridade
    print("🔍 VALIDAÇÃO DE INTEGRIDADE:")
    erros = []
    
    # Verificar valores numéricos
    for col in ['valor_causa', 'ano'] + defesas + ['vitoria']:
        if df[col].dtype not in ['int64', 'float64']:
            erros.append(f"Coluna {col} não é numérica")
        
        # Verificar valores válidos para campos binários
        if col in defesas + ['vitoria']:
            valores_unicos = df[col].unique()
            if not all(v in [0, 1] for v in valores_unicos):
                erros.append(f"Coluna {col} tem valores inválidos: {valores_unicos}")
    
    # Verificar anos válidos
    anos_validos = range(2020, 2025)
    if not df['ano'].isin(anos_validos).all():
        anos_invalidos = df[~df['ano'].isin(anos_validos)]['ano'].unique()
        erros.append(f"Anos inválidos encontrados: {anos_invalidos}")
    
    # Verificar valores monetários
    if (df['valor_causa'] <= 0).any():
        casos_valor_zero = len(df[df['valor_causa'] <= 0])
        erros.append(f"Encontrados {casos_valor_zero} casos com valor da causa <= 0")
    
    if erros:
        for erro in erros:
            print(f"   ❌ {erro}")
    else:
        print("   ✅ Todos os dados passaram na validação de integridade!")
    
    print()
    
    # Amostras de casos para verificação manual
    print("🔍 AMOSTRAS DE CASOS PARA VERIFICAÇÃO:")
    casos_amostra = [1, 500, 1000, 1500, 2000]
    
    for caso_id in casos_amostra:
        if caso_id <= len(df):
            caso = df.iloc[caso_id - 1]
            print(f"   Caso {caso_id}: {caso['area']} | {caso['foro']} | R$ {caso['valor_causa']:,.2f} | {caso['ano']}")
    
    print()
    print("="*60)
    print("✅ ANÁLISE COMPLETA FINALIZADA!")
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_path = f'modelos_juridicos/reports/analise_dataset_{timestamp}.txt'
    
    # Criar relatório em arquivo
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ANÁLISE DO DATASET JURÍDICO\n")
        f.write("="*50 + "\n")
        f.write(f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de processos analisados: {len(df)}\n\n")
        
        # Resumo executivo
        f.write("RESUMO EXECUTIVO:\n")
        f.write(f"- Dataset com {len(df)} processos jurídicos\n")
        f.write(f"- {len(df['area'].unique())} áreas jurídicas: {', '.join(df['area'].unique())}\n")
        f.write(f"- {len(df['foro'].unique())} foros: {', '.join(df['foro'].unique())}\n")
        f.write(f"- Período: {int(df['ano'].min())} a {int(df['ano'].max())}\n")
        f.write(f"- Taxa de vitória geral: {df['vitoria'].mean()*100:.1f}%\n")
        f.write(f"- Valor médio das causas: R$ {df['valor_causa'].mean():,.2f}\n")
        
        if not erros:
            f.write("\n✅ Dataset aprovado para uso em produção!\n")
        else:
            f.write(f"\n❌ {len(erros)} problemas identificados que precisam correção.\n")
    
    print(f"📄 Relatório salvo em: {relatorio_path}")
    return len(df), len(erros) == 0

if __name__ == "__main__":
    revisar_dataset()