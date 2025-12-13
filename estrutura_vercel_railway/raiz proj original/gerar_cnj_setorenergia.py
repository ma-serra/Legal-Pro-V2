#!/usr/bin/env python3
"""
Gera números CNJ fake para todos os processos do Setor de Energia
"""

import json
import random
from pathlib import Path

def calcular_digito_verificador(numero_sequencial, ano, segmento, tribunal, origem):
    """
    Calcula o dígito verificador do número CNJ
    Formato: NNNNNNN-DD.AAAA.J.TT.OOOO
    """
    # Concatenar todos os números
    numero_completo = f"{numero_sequencial:07d}{ano}{segmento}{tribunal:02d}{origem:04d}"
    
    # Calcular resto da divisão por 97
    resto = int(numero_completo) % 97
    
    # Dígito verificador é 98 - resto
    digito = 98 - resto
    
    return f"{digito:02d}"

def gerar_numero_cnj(index, ano_base=None):
    """
    Gera um número CNJ fake único
    Formato: NNNNNNN-DD.AAAA.J.TT.OOOO
    """
    # Número sequencial (baseado no index para garantir unicidade)
    numero_sequencial = 1000000 + index
    
    # Ano do ajuizamento (entre 2012 e 2025 se não especificado)
    if ano_base is None:
        ano = random.randint(2012, 2025)
    else:
        ano = ano_base
    
    # Segmento do judiciário (8 = Justiça Estadual)
    segmento = 8
    
    # Tribunal (21 = Rio Grande do Sul, 26 = São Paulo, 05 = Bahia)
    tribunais = [21, 26, 5]
    tribunal = random.choice(tribunais)
    
    # Vara/origem (entre 0001 e 9999)
    origem = random.randint(1, 500)
    
    # Calcular dígito verificador
    digito = calcular_digito_verificador(numero_sequencial, ano, segmento, tribunal, origem)
    
    # Montar número CNJ
    numero_cnj = f"{numero_sequencial:07d}-{digito}.{ano}.{segmento}.{tribunal:02d}.{origem:04d}"
    
    return numero_cnj

def atualizar_processos():
    """Atualiza todos os processos com números CNJ fake"""
    
    # Caminho do arquivo
    json_path = Path('cpfl-analytics/data/processed/cpfl_processos_completo.json')
    
    print(f"📂 Carregando arquivo: {json_path}")
    
    # Carregar JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        processos = json.load(f)
    
    print(f"✅ {len(processos)} processos carregados")
    
    # Gerar números CNJ fake únicos
    numeros_gerados = set()
    processos_atualizados = 0
    
    print("🔢 Gerando números CNJ fake...")
    
    for i, processo in enumerate(processos):
        # Tentar usar o ano de criação do processo se disponível
        ano_base = None
        if 'ano_criacao' in processo and processo['ano_criacao']:
            ano_base = processo['ano_criacao']
        elif 'Data criação' in processo and processo['Data criação']:
            try:
                ano_base = int(processo['Data criação'].split('-')[0])
            except:
                pass
        
        # Gerar número CNJ único
        tentativas = 0
        while tentativas < 100:
            numero_cnj = gerar_numero_cnj(i + tentativas * 10000, ano_base)
            
            if numero_cnj not in numeros_gerados:
                numeros_gerados.add(numero_cnj)
                processo['Número do Processo'] = numero_cnj
                processos_atualizados += 1
                
                # Log a cada 500 processos
                if (i + 1) % 500 == 0:
                    print(f"   ✓ {i + 1} processos atualizados...")
                
                break
            
            tentativas += 1
        
        if tentativas >= 100:
            print(f"   ⚠️  Aviso: Não foi possível gerar número único para processo {i}")
    
    print(f"\n✅ {processos_atualizados} processos atualizados com números CNJ fake")
    
    # Fazer backup do arquivo original
    backup_path = json_path.with_suffix('.json.backup')
    print(f"💾 Criando backup em: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(processos, f, ensure_ascii=False, indent=2)
    
    # Salvar arquivo atualizado
    print(f"💾 Salvando arquivo atualizado...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(processos, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Concluído! Arquivo atualizado com sucesso!")
    print(f"\n📊 Estatísticas:")
    print(f"   • Total de processos: {len(processos)}")
    print(f"   • Processos atualizados: {processos_atualizados}")
    print(f"   • Números únicos gerados: {len(numeros_gerados)}")
    print(f"\n📋 Exemplos de números CNJ gerados:")
    for i, numero in enumerate(list(numeros_gerados)[:10]):
        print(f"   {i+1}. {numero}")

if __name__ == '__main__':
    atualizar_processos()
