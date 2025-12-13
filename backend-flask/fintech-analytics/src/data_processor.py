"""
DATASET FINTECH - PROCESSAMENTO ETL COMPLETO
===============================================

Implementação baseada no dataset_fintech_limpo.py fornecido
Processa 11.454 registros → 11.446 registros válidos
Taxa de sucesso esperada: 65.4%
"""

import pandas as pd
import numpy as np
import warnings
import re
from datetime import datetime
import os

warnings.filterwarnings('ignore')

class FintechETL:
    """
    Classe principal para processamento ETL dos dados da Fintech
    Baseada nas especificações do relatorio_etl_fintech.md
    """
    
    def __init__(self):
        self.df_raw = None
        self.df_processed = None
        self.stats = {}
        
        # Dicionário de mapeamento das colunas do arquivo original para nomes padronizados
        self.column_mapping = {
            'Nº Processo ': 'numero_processo',
            'Adverso Principal ': 'adverso_principal', 
            'Juízo ': 'juizo',
            'Órgão ': 'orgao',
            'Estado ': 'estado',
            'Comarca ': 'comarca',
            'Causa* ': 'codigo_causa',
            'Banco ': 'banco_emissor',
            'Emissor é corréu? ': 'emissor_correu',
            'Tipo decisão* Históricos': 'tipo_decisao_original',
            'Data Históricos': 'data_historico',
            'Ocorrência* Históricos': 'descricao_ocorrencia'
        }
        
    def load_raw_data(self, file_path):
        """
        Carrega dados brutos do Excel
        """
        try:
            print("🔄 Carregando dados brutos...")
            self.df_raw = pd.read_excel(file_path)
            print(f"✅ Dados carregados: {len(self.df_raw)} registros")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def clean_data(self):
        """
        Limpeza de dados conforme especificações do relatório ETL
        """
        print("🧹 Iniciando limpeza de dados...")
        
        df = self.df_raw.copy()
        initial_count = len(df)
        
        # 1. Renomear colunas usando o dicionário de mapeamento
        print("🔄 Renomeando colunas...")
        df = df.rename(columns=self.column_mapping)
        print(f"✅ Colunas renomeadas: {list(df.columns[:6])}...")
        
        # 2. Remover registros inválidos
        df = df.dropna(subset=['numero_processo', 'data_historico'])
        df = df[df['numero_processo'].astype(str).str.len() > 5]
        
        # 3. Padronização de textos
        text_columns = ['adverso_principal', 'tipo_decisao_original', 'descricao_ocorrencia']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
                # Remover caracteres especiais problemáticos
                df[col] = df[col].str.replace(r'[^\w\s\-\.\,]', '', regex=True)
        
        # 4. Padronização de números de processo
        if 'numero_processo' in df.columns:
            df['numero_processo'] = df['numero_processo'].astype(str).str.replace(r'[^\d\-\.]', '', regex=True)
        
        # 5. Converter data para datetime
        if 'data_historico' in df.columns:
            df['data_historico'] = pd.to_datetime(df['data_historico'], errors='coerce')
        
        cleaned_count = len(df)
        removed_count = initial_count - cleaned_count
        
        print(f"🗑️ Registros removidos: {removed_count}")
        print(f"✅ Registros válidos: {cleaned_count}")
        
        self.df_processed = df
        return df
    
    def enrich_data(self):
        """
        Enriquecimento de dados conforme especificações
        """
        print("🔧 Iniciando enriquecimento de dados...")
        
        df = self.df_processed.copy()
        
        # 1. Dimensões Temporais
        if 'data_historico' in df.columns:
            df['ano'] = df['data_historico'].dt.year
            df['mes'] = df['data_historico'].dt.month
            df['trimestre'] = df['data_historico'].dt.quarter
            df['semestre'] = (df['mes'] - 1) // 6 + 1
            
            # Contexto COVID
            df['periodo_covid'] = df['ano'].apply(self._classify_covid_period)
        
        # 2. Dimensões Geográficas  
        if 'estado' in df.columns:
            df['regiao'] = df['estado'].apply(self._get_region)
        
        # 3. Classificação de Resultados
        if 'tipo_decisao_original' in df.columns:
            df['resultado'] = df['tipo_decisao_original'].apply(self._classify_result)
            df['grau_favorabilidade'] = df['resultado'].apply(self._get_favorability_score)
        
        # 4. Dimensões Jurídicas
        if 'orgao' in df.columns:
            df['instancia'] = df['orgao'].apply(self._classify_instance)
        
        # 5. APLICAR FORMATAÇÃO PADRÃO FINTECH
        print("🎨 Aplicando formatação padrão Fintech...")
        try:
            from src.data_formatter import format_fintech_data
            df = format_fintech_data(df)
        except ImportError:
            print("⚠️ Módulo de formatação não encontrado, pulando formatação")
        
        print("✅ Enriquecimento concluído")
        self.df_processed = df
        return df
    
    def _classify_covid_period(self, year):
        """Classifica período COVID"""
        if year < 2020:
            return 'Pré-COVID'
        elif year <= 2021:
            return 'COVID'
        else:
            return 'Pós-COVID'
    
    def _get_region(self, estado):
        """Mapeia estado para região"""
        # Mapeamento direto por nome completo (seguindo padrão do exemplo)
        regiao_mapping = {
            'São Paulo': 'Sudeste',
            'Rio de Janeiro': 'Sudeste',
            'Minas Gerais': 'Sudeste',
            'Espírito Santo': 'Sudeste',
            'Paraná': 'Sul',
            'Santa Catarina': 'Sul',
            'Rio Grande do Sul': 'Sul',
            'Bahia': 'Nordeste',
            'Pernambuco': 'Nordeste',
            'Ceará': 'Nordeste',
            'Paraíba': 'Nordeste',
            'Rio Grande do Norte': 'Nordeste',
            'Alagoas': 'Nordeste',
            'Sergipe': 'Nordeste',
            'Maranhão': 'Nordeste',
            'Piauí': 'Nordeste',
            'Goiás': 'Centro-Oeste',
            'Mato Grosso': 'Centro-Oeste',
            'Mato Grosso do Sul': 'Centro-Oeste',
            'Distrito Federal': 'Centro-Oeste',
            'Acre': 'Norte',
            'Amazonas': 'Norte',
            'Amapá': 'Norte',
            'Pará': 'Norte',
            'Rondônia': 'Norte',
            'Roraima': 'Norte',
            'Tocantins': 'Norte'
        }
        
        return regiao_mapping.get(estado, 'Não Identificado')
    
    def _classify_result(self, decision_text):
        """Classifica resultado baseado no texto da decisão"""
        if pd.isna(decision_text):
            return 'Neutro'
        
        decision_text = str(decision_text).upper()
        
        # Palavras-chave para favorável
        favorable_keywords = [
            'PROCEDENTE', 'FAVORÁVEL', 'DEFERIDO', 'ACEITO', 'PROVIDO',
            'GANHO', 'VENCEDOR', 'SUCESSO', 'APROVADO'
        ]
        
        # Palavras-chave para desfavorável  
        unfavorable_keywords = [
            'IMPROCEDENTE', 'DESFAVORÁVEL', 'INDEFERIDO', 'NEGADO', 'IMPROVIDO',
            'PERDA', 'PERDEDOR', 'REJEITADO', 'NEGATIVO'
        ]
        
        for keyword in favorable_keywords:
            if keyword in decision_text:
                return 'Favorável'
        
        for keyword in unfavorable_keywords:
            if keyword in decision_text:
                return 'Desfavorável'
        
        return 'Neutro'
    
    def _get_favorability_score(self, resultado):
        """Converte resultado em score 1-5"""
        score_map = {
            'Desfavorável': 1,
            'Neutro': 3,
            'Favorável': 5
        }
        return score_map.get(resultado, 3)
    
    def _classify_instance(self, orgao):
        """Classifica instância jurídica"""
        if pd.isna(orgao):
            return '1º Grau'
        
        orgao_str = str(orgao).upper()
        
        if any(word in orgao_str for word in ['TRIBUNAL', 'TJ', 'TRT', 'TRF']):
            return '2º Grau'
        else:
            return '1º Grau'
    
    def calculate_final_stats(self):
        """
        Calcula estatísticas finais para validação
        """
        if self.df_processed is None:
            return {}
        
        df = self.df_processed
        
        # Estatísticas gerais
        total_registros = len(df)
        
        # Distribuição de resultados
        resultado_dist = df['resultado'].value_counts()
        resultado_pct = df['resultado'].value_counts(normalize=True) * 100
        
        # Taxa de sucesso
        taxa_sucesso = (df['resultado'] == 'Favorável').mean() * 100
        
        # Cobertura geográfica
        estados_unicos = df['estado'].nunique() if 'estado' in df.columns else 0
        regioes_unicas = df['regiao'].nunique() if 'regiao' in df.columns else 0
        
        # Órgãos jurídicos
        orgaos_unicos = df['orgao'].nunique() if 'orgao' in df.columns else 0
        
        # Período de dados
        if 'ano' in df.columns:
            periodo_inicio = df['ano'].min()
            periodo_fim = df['ano'].max()
        else:
            periodo_inicio = periodo_fim = 'N/A'
        
        self.stats = {
            'total_registros': total_registros,
            'taxa_sucesso_geral': round(taxa_sucesso, 1),
            'distribuicao_resultados': {
                'favoravel': resultado_dist.get('Favorável', 0),
                'desfavoravel': resultado_dist.get('Desfavorável', 0),
                'neutro': resultado_dist.get('Neutro', 0)
            },
            'percentuais_resultados': {
                'favoravel': round(resultado_pct.get('Favorável', 0), 1),
                'desfavoravel': round(resultado_pct.get('Desfavorável', 0), 1),
                'neutro': round(resultado_pct.get('Neutro', 0), 1)
            },
            'cobertura_geografica': {
                'estados': estados_unicos,
                'regioes': regioes_unicas
            },
            'orgaos_juridicos': orgaos_unicos,
            'periodo': f"{periodo_inicio}-{periodo_fim}"
        }
        
        return self.stats
    
    def generate_final_dataset(self):
        """
        Gera dataset final com 21 colunas conforme especificação
        """
        if self.df_processed is None:
            return None
        
        # Colunas obrigatórias conforme relatório ETL
        required_columns = [
            'numero_processo', 'adverso_principal', 'data_historico', 'ano', 'mes', 
            'trimestre', 'semestre', 'estado', 'regiao', 'comarca', 'juizo', 
            'orgao', 'instancia', 'codigo_causa', 'banco_emissor', 'emissor_correu',
            'tipo_decisao_original', 'resultado', 'grau_favorabilidade', 
            'periodo_covid', 'descricao_ocorrencia'
        ]
        
        df_final = self.df_processed.copy()
        
        # Garantir que todas as colunas existam
        for col in required_columns:
            if col not in df_final.columns:
                df_final[col] = np.nan
        
        # Reordenar colunas
        df_final = df_final[required_columns]
        
        # Aplicar tipos de dados otimizados
        dtype_mapping = {
            'numero_processo': 'string',
            'adverso_principal': 'string',
            'ano': 'Int64',
            'mes': 'Int64', 
            'trimestre': 'Int64',
            'semestre': 'Int64',
            'estado': 'category',
            'regiao': 'category',
            'comarca': 'string',
            'juizo': 'Int64',
            'orgao': 'category',
            'instancia': 'category',
            'codigo_causa': 'float64',
            'banco_emissor': 'category',
            'emissor_correu': 'category',
            'tipo_decisao_original': 'string',
            'resultado': 'category',
            'grau_favorabilidade': 'Int64',
            'periodo_covid': 'category',
            'descricao_ocorrencia': 'string'
        }
        
        for col, dtype in dtype_mapping.items():
            if col in df_final.columns:
                try:
                    if dtype == 'category':
                        df_final[col] = df_final[col].astype('category')
                    else:
                        df_final[col] = df_final[col].astype(dtype)
                except:
                    pass  # Manter tipo original se conversão falhar
        
        return df_final
    
    def save_processed_data(self, output_path):
        """
        Salva dados processados em CSV
        """
        df_final = self.generate_final_dataset()
        if df_final is not None:
            df_final.to_csv(output_path, index=False, encoding='utf-8')
            print(f"✅ Dataset salvo em: {output_path}")
            return True
        return False
    
    def run_complete_etl(self, input_file, output_file):
        """
        Executa ETL completo
        """
        print("🚀 INICIANDO ETL COMPLETO - DATASET FINTECH")
        print("=" * 60)
        
        # 1. Carregar dados
        if not self.load_raw_data(input_file):
            return False
        
        # 2. Limpar dados
        self.clean_data()
        
        # 3. Enriquecer dados
        self.enrich_data()
        
        # 4. Calcular estatísticas
        stats = self.calculate_final_stats()
        
        # 5. Salvar dados processados
        success = self.save_processed_data(output_file)
        
        # 6. Relatório final
        if success:
            print("\n📊 RELATÓRIO ETL FINAL")
            print("=" * 30)
            print(f"Total de registros: {stats['total_registros']}")
            print(f"Taxa de sucesso: {stats['taxa_sucesso_geral']}%")
            print(f"Período: {stats['periodo']}")
            print(f"Estados únicos: {stats['cobertura_geografica']['estados']}")
            print(f"Órgãos únicos: {stats['orgaos_juridicos']}")
            print("\nDistribuição de resultados:")
            print(f"  Favorável: {stats['distribuicao_resultados']['favoravel']} ({stats['percentuais_resultados']['favoravel']}%)")
            print(f"  Desfavorável: {stats['distribuicao_resultados']['desfavoravel']} ({stats['percentuais_resultados']['desfavoravel']}%)")
            print(f"  Neutro: {stats['distribuicao_resultados']['neutro']} ({stats['percentuais_resultados']['neutro']}%)")
            print("\n🎉 ETL CONCLUÍDO COM SUCESSO!")
            
            return True
        
        return False

def carregar_dataset_fintech(arquivo_csv):
    """
    Função para carregar dataset já processado
    Baseada na função original do dataset_fintech_limpo.py
    """
    dtype_mapping = {
        'numero_processo': 'string',
        'adverso_principal': 'string',
        'ano': 'Int64',
        'mes': 'Int64',
        'trimestre': 'Int64',
        'semestre': 'Int64',
        'estado': 'category',
        'regiao': 'category',
        'comarca': 'string',
        'juizo': 'Int64',
        'orgao': 'category',
        'instancia': 'category',
        'codigo_causa': 'float64',
        'banco_emissor': 'category',
        'emissor_correu': 'category',
        'tipo_decisao_original': 'string',
        'resultado': 'category',
        'grau_favorabilidade': 'Int64',
        'periodo_covid': 'category',
        'descricao_ocorrencia': 'string'
    }
    
    # Carregar CSV com tratamento robusto
    try:
        # Tentar múltiplos encodings e configurações
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                print(f"🔄 Tentando carregar com encoding {encoding}...")
                df = pd.read_csv(
                    arquivo_csv, 
                    dtype=dtype_mapping, 
                    parse_dates=['data_historico'],
                    encoding=encoding,
                    on_bad_lines='skip',
                    quoting=1,  # QUOTE_ALL - trata aspas corretamente
                    skipinitialspace=True,
                    escapechar='\\',
                    doublequote=True
                )
                print(f"✅ Dataset carregado ({encoding}): {len(df)} registros")
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                print(f"⚠️ Falha com {encoding}: {str(e)[:100]}...")
                continue
        
        if df is None:
            print("❌ Falha ao carregar com todos os encodings. Tentando método alternativo...")
            # Método alternativo: ler como texto e limpar
            df = pd.read_csv(arquivo_csv, encoding='utf-8', on_bad_lines='skip')
            
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        # Fallback para leitura básica
        df = pd.read_csv(arquivo_csv)
    
    # Configurar categorias ordenadas
    df['resultado'] = df['resultado'].astype(pd.CategoricalDtype(['Desfavorável', 'Neutro', 'Favorável'], ordered=True))
    df['grau_favorabilidade'] = df['grau_favorabilidade'].astype(pd.CategoricalDtype([1,2,3,4,5], ordered=True))
    df['periodo_covid'] = df['periodo_covid'].astype(pd.CategoricalDtype(['Pré-COVID', 'COVID', 'Pós-COVID'], ordered=True))
    
    return df

def calcular_kpis_estrategicos(df):
    """
    Calcula KPIs estratégicos do dataset
    IMPORTANTE: Considera apenas processos únicos por numero_processo (7.880 processos)
    Para dados evolutivos, pega apenas o registro mais recente de cada processo
    """
    kpis = {}
    
    # CRITICAL: Dedupilcar por numero_processo para contar apenas processos únicos
    print("🔄 Aplicando deduplicação por numero_processo...")
    
    # Ordenar por data_historico (mais recente primeiro) e pegar apenas o primeiro de cada processo
    df_unique = df.sort_values('data_historico', ascending=False).drop_duplicates(subset=['numero_processo'], keep='first')
    
    total_registros_original = len(df)
    processos_unicos = len(df_unique)
    
    print(f"📊 Registros totais no dataset: {total_registros_original}")
    print(f"📊 Processos únicos (numero_processo): {processos_unicos}")
    print(f"📊 Taxa de deduplicação: {(1 - processos_unicos/total_registros_original)*100:.1f}%")
    
    # KPIs Gerais - USANDO APENAS PROCESSOS ÚNICOS
    kpis['total_casos'] = processos_unicos  # 7.880 processos únicos, não 11.451 registros
    kpis['taxa_sucesso_geral'] = (df_unique['resultado'] == 'Favorável').mean() * 100
    kpis['periodo'] = f"{df_unique['ano'].min()}-{df_unique['ano'].max()}"
    kpis['taxa_favorabilidade'] = (df_unique['resultado'] == 'Favorável').mean()  # Para compatibilidade
    
    # Performance por Estado - USANDO APENAS PROCESSOS ÚNICOS
    kpis['performance_estados'] = df_unique.groupby('estado').agg({
        'resultado': ['count', lambda x: (x == 'Favorável').mean() * 100]
    }).round(1)
    
    # Performance por Órgão - USANDO APENAS PROCESSOS ÚNICOS  
    kpis['performance_orgaos'] = df_unique.groupby('orgao').agg({
        'resultado': ['count', lambda x: (x == 'Favorável').mean() * 100]
    }).round(1)
    
    # Evolução Temporal - USANDO APENAS PROCESSOS ÚNICOS
    kpis['evolucao_temporal'] = df_unique.groupby('ano').agg({
        'resultado': ['count', lambda x: (x == 'Favorável').mean() * 100]
    }).round(1)
    
    # Adicionar informações de validação
    kpis['validation_info'] = {
        'total_records_raw': total_registros_original,
        'unique_processes': processos_unicos,
        'deduplication_rate': round((1 - processos_unicos/total_registros_original)*100, 1),
        'data_quality_check': 'PASSED' if processos_unicos == 7880 else f'WARNING: Expected 7880, got {processos_unicos}'
    }
    
    return kpis

if __name__ == "__main__":
    # Exemplo de uso do ETL
    etl = FintechETL()
    
    # Definir caminhos
    input_file = "../data/raw/Decisões Fintech 2019 até 2025.xlsx"
    output_file = "../data/processed/dataset_fintech_limpo.csv"
    
    # Executar ETL completo
    etl.run_complete_etl(input_file, output_file)