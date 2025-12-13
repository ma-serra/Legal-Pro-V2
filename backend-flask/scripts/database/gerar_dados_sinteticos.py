#!/usr/bin/env python3
"""
Script para geração de dados sintéticos jurídicos usando o LegalSyntheticDataGenerator
Alternativa ao SDV com foco específico em dados jurídicos brasileiros
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.synthetic_data_generator import LegalSyntheticDataGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Gerador de Dados Sintéticos para Sistema Jurídico',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Gerar 50 processos padrão
  python gerar_dados_sinteticos.py -q 50

  # Gerar 100 processos focados em trabalhista
  python gerar_dados_sinteticos.py -q 100 --area "Direito Trabalhista" -p 60

  # Gerar dados e exportar para SQL
  python gerar_dados_sinteticos.py -q 200 --sql processos.sql

  # Gerar dados com distribuição personalizada
  python gerar_dados_sinteticos.py -q 150 --config distribuicao.json

  # Mostrar apenas estatísticas sem gerar arquivo
  python gerar_dados_sinteticos.py -q 75 --stats-only
        """
    )
    
    # Argumentos principais
    parser.add_argument(
        '-q', '--quantidade',
        type=int,
        default=50,
        help='Quantidade de processos a gerar (padrão: 50)'
    )
    
    parser.add_argument(
        '--area',
        type=str,
        help='Área jurídica específica para focar a geração'
    )
    
    parser.add_argument(
        '-p', '--percentual',
        type=int,
        default=40,
        help='Percentual da área específica quando --area for usado (padrão: 40%%)'
    )
    
    # Opções de saída
    parser.add_argument(
        '--sql',
        type=str,
        help='Exportar dados para arquivo SQL'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Exportar dados para arquivo JSON'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Arquivo JSON com distribuição personalizada de áreas'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Mostrar apenas estatísticas, sem gerar arquivos'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Seed para reprodutibilidade dos dados gerados'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Saída detalhada'
    )
    
    args = parser.parse_args()
    
    if args.seed:
        import random
        random.seed(args.seed)
        if args.verbose:
            print(f"Usando seed: {args.seed}")
    
    # Configurar distribuição de áreas
    distribuicao_areas = None
    
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                distribuicao_areas = json.load(f)
            if args.verbose:
                print(f"Carregada distribuição do arquivo: {args.config}")
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.area:
        # Criar distribuição focada na área especificada
        outras_areas = [
            "Direito Civil", "Direito Trabalhista", "Direito do Consumidor",
            "Direito Empresarial", "Direito Tributário", "Direito Criminal",
            "Direito Previdenciário", "Direito Imobiliário"
        ]
        
        if args.area not in outras_areas:
            outras_areas.append(args.area)
        
        distribuicao_areas = {args.area: args.percentual}
        percentual_restante = 100 - args.percentual
        percentual_por_area = percentual_restante // (len(outras_areas) - 1)
        
        for area in outras_areas:
            if area != args.area:
                distribuicao_areas[area] = percentual_por_area
        
        if args.verbose:
            print(f"Focando {args.percentual}% em {args.area}")
    
    # Gerar dados
    if args.verbose:
        print(f"Gerando {args.quantidade} processos sintéticos...")
    
    gerador = LegalSyntheticDataGenerator()
    
    inicio = datetime.now()
    processos = gerador.gerar_lote_processos(args.quantidade, distribuicao_areas)
    fim = datetime.now()
    
    if args.verbose:
        tempo_geracao = (fim - inicio).total_seconds()
        print(f"Geração concluída em {tempo_geracao:.2f} segundos")
    
    # Gerar estatísticas
    relatorio = gerador.gerar_relatorio_estatistico(processos)
    
    # Mostrar estatísticas
    print("\n" + "="*60)
    print("RELATÓRIO DE DADOS SINTÉTICOS GERADOS")
    print("="*60)
    print(f"Total de processos: {relatorio['total_processos']:,}")
    print(f"Valor total das causas: R$ {relatorio['valor_total_causas']:,.2f}")
    
    print("\nDistribuição por Área Jurídica:")
    for area, quantidade in sorted(relatorio['distribuicao_por_area'].items()):
        percentual = (quantidade / relatorio['total_processos']) * 100
        print(f"  {area:<25}: {quantidade:>4} ({percentual:>5.1f}%)")
    
    print("\nDistribuição por Estado:")
    for estado, quantidade in sorted(relatorio['distribuicao_por_estado'].items()):
        percentual = (quantidade / relatorio['total_processos']) * 100
        print(f"  {estado}: {quantidade:>4} ({percentual:>5.1f}%)")
    
    print("\nDistribuição por Risco:")
    for risco, quantidade in sorted(relatorio['distribuicao_por_risco'].items()):
        percentual = (quantidade / relatorio['total_processos']) * 100
        print(f"  {risco:<8}: {quantidade:>4} ({percentual:>5.1f}%)")
    
    if relatorio['valores_financeiros']:
        print("\nValores Médios por Área:")
        for area, valores in relatorio['valores_financeiros'].items():
            print(f"  {area}:")
            print(f"    Média: R$ {valores['media']:,.2f}")
            print(f"    Mínimo: R$ {valores['minimo']:,.2f}")
            print(f"    Máximo: R$ {valores['maximo']:,.2f}")
            print(f"    Total: R$ {valores['total']:,.2f}")
    
    # Exportar arquivos se solicitado
    if not args.stats_only:
        arquivos_gerados = []
        
        if args.sql:
            arquivo_sql = gerador.exportar_para_sql(processos, args.sql)
            arquivos_gerados.append(arquivo_sql)
            if args.verbose:
                print(f"\nArquivo SQL exportado: {arquivo_sql}")
        
        if args.json:
            # Converter datas para string para JSON
            processos_json = []
            for processo in processos:
                processo_json = processo.copy()
                for campo, valor in processo_json.items():
                    if isinstance(valor, datetime):
                        processo_json[campo] = valor.isoformat()
                    elif hasattr(valor, 'strftime'):  # date
                        processo_json[campo] = valor.strftime('%Y-%m-%d')
                processos_json.append(processo_json)
            
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'total_processos': len(processos_json),
                        'data_geracao': datetime.now().isoformat(),
                        'gerador': 'LegalSyntheticDataGenerator v1.0'
                    },
                    'estatisticas': relatorio,
                    'processos': processos_json
                }, f, ensure_ascii=False, indent=2)
            
            arquivos_gerados.append(args.json)
            if args.verbose:
                print(f"Arquivo JSON exportado: {args.json}")
        
        # Se nenhum formato específico foi solicitado, gerar SQL padrão
        if not args.sql and not args.json:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_padrao = f"processos_sinteticos_{timestamp}.sql"
            gerador.exportar_para_sql(processos, arquivo_padrao)
            arquivos_gerados.append(arquivo_padrao)
            print(f"\nArquivo SQL padrão gerado: {arquivo_padrao}")
        
        if arquivos_gerados:
            print(f"\nArquivos gerados: {', '.join(arquivos_gerados)}")
    
    print("\n" + "="*60)
    print("✅ Geração de dados sintéticos concluída com sucesso!")
    print("="*60)


def gerar_config_exemplo():
    """Gera arquivo de configuração de exemplo"""
    config_exemplo = {
        "Direito Trabalhista": 30,
        "Direito Civil": 25,
        "Direito do Consumidor": 15,
        "Direito Empresarial": 12,
        "Direito Tributário": 8,
        "Direito Criminal": 5,
        "Direito Previdenciário": 3,
        "Direito Imobiliário": 2
    }
    
    with open('distribuicao_exemplo.json', 'w', encoding='utf-8') as f:
        json.dump(config_exemplo, f, ensure_ascii=False, indent=2)
    
    print("Arquivo de configuração exemplo criado: distribuicao_exemplo.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gerar-config':
        gerar_config_exemplo()
    else:
        main()