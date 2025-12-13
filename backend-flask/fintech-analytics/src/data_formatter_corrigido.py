"""
FORMATADOR DE DADOS FINTECH - VERSÃO CORRIGIDA
================================================

Versão corrigida com encoding UTF-8 robusto e tratamento de erros.
"""

import pandas as pd
import numpy as np
import re
import warnings
from typing import Dict, Any, List
import unicodedata

# Suprimir avisos do pandas
warnings.filterwarnings('ignore')

class FintechDataFormatterCorrigido:
    """
    Formatador com encoding UTF-8 robusto e tratamento de erros
    """
    
    def __init__(self):
        self.regiao_mapping = {
            'São Paulo': 'Sudeste',
            'Rio de Janeiro': 'Sudeste', 
            'Minas Gerais': 'Sudeste',
            'Espírito Santo': 'Sudeste',
            'Rio Grande do Sul': 'Sul',
            'Santa Catarina': 'Sul',
            'Paraná': 'Sul',
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
        
        self.favorabilidade_mapping = {
            'Muito Desfavorável': 1,
            'Desfavorável': 2,
            'Neutro': 3,
            'Favorável': 4,
            'Muito Favorável': 5
        }
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto removendo caracteres problemáticos"""
        if pd.isna(text) or text == '':
            return text
        
        # Converter para string se necessário
        text = str(text)
        
        # Normalizar Unicode (NFD -> NFC)
        text = unicodedata.normalize('NFC', text)
        
        # Remover caracteres de controle problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Limpeza adicional de caracteres problemáticos
        text = text.replace('\ufeff', '')  # BOM
        text = text.replace('\u00a0', ' ')  # Non-breaking space
        
        return text.strip()
    
    def format_proper_name(self, name: str) -> str:
        """Formata nomes próprios com capitalização correta"""
        if pd.isna(name) or name == '':
            return name
        
        # Normalizar texto primeiro
        name = self.normalize_text(name)
        
        # Lista de preposições que ficam minúsculas
        prepositions = [
            'da', 'de', 'do', 'das', 'dos', 'e', 'em', 'na', 'no', 'nas', 'nos',
            'para', 'por', 'com', 'sem', 'sob', 'sobre', 'entre', 'até', 'após',
            'ante', 'contra', 'desde', 'perante', 'segundo', 'mediante'
        ]
        
        # Dividir por espaços e processar cada palavra
        words = name.split()
        formatted_words = []
        
        for i, word in enumerate(words):
            # Limpar a palavra
            clean_word = re.sub(r'[^\w\s]', '', word).lower()
            
            # Se é uma preposição e não é a primeira palavra, manter minúscula
            if clean_word in prepositions and i > 0:
                formatted_words.append(clean_word)
            else:
                # Capitalizar primeira letra
                if word:
                    formatted_word = word[0].upper() + word[1:].lower()
                    formatted_words.append(formatted_word)
        
        return ' '.join(formatted_words)
    
    def safe_numeric_conversion(self, value, default=0):
        """Conversão segura para numérico"""
        if pd.isna(value):
            return default
        
        # Se já é numérico, retornar
        if isinstance(value, (int, float)):
            return value
        
        # Tentar converter string
        if isinstance(value, str):
            # Normalizar texto
            value = self.normalize_text(value)
            
            # Tentar extrair número
            number_match = re.search(r'(\d+(?:\.\d+)?)', value.replace(',', '.'))
            if number_match:
                try:
                    return float(number_match.group(1))
                except ValueError:
                    return default
        
        return default
    
    def load_csv_robust(self, file_path: str) -> pd.DataFrame:
        """Carrega CSV com encoding robusto"""
        print(f"🔄 Carregando CSV: {file_path}")
        
        # Lista de encodings para testar
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                print(f"   Tentando encoding: {encoding}")
                
                # Carregar com parâmetros seguros
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    on_bad_lines='skip',  # Pular linhas problemáticas
                    quoting=1,  # QUOTE_ALL
                    escapechar='\\',
                    dtype=str,  # Carregar tudo como string primeiro
                    low_memory=False
                )
                
                print(f"   ✅ Sucesso com {encoding}: {len(df)} registros")
                return df
                
            except Exception as e:
                print(f"   ❌ Falha com {encoding}: {e}")
                continue
        
        raise Exception("Não foi possível carregar o CSV com nenhum encoding testado")
    
    def format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formata DataFrame com tratamento robusto de encoding"""
        print("🎨 FORMATAÇÃO FINTECH - VERSÃO CORRIGIDA")
        print("=" * 50)
        
        df_formatted = df.copy()
        
        # 1. Normalizar todos os textos
        print("📝 Normalizando textos...")
        for col in df_formatted.select_dtypes(include=['object']).columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: self.normalize_text(x) if pd.notna(x) else x
            )
        
        # 2. Formatar nomes próprios
        print("👤 Formatando nomes próprios...")
        if 'adverso_principal' in df_formatted.columns:
            df_formatted['adverso_principal'] = df_formatted['adverso_principal'].apply(
                self.format_proper_name
            )
        
        # 3. Mapear regiões
        print("🗺️ Mapeando regiões...")
        if 'estado' in df_formatted.columns:
            df_formatted['regiao'] = df_formatted['estado'].map(
                self.regiao_mapping
            ).fillna('Não Identificado')
        
        # 4. Formatar instâncias
        print("⚖️ Formatando instâncias...")
        if 'instancia' in df_formatted.columns:
            df_formatted['instancia'] = df_formatted['instancia'].replace({
                '1': '1º Grau',
                '2': '2º Grau',
                '3': '3º Grau',
                1: '1º Grau',
                2: '2º Grau',
                3: '3º Grau'
            })
        
        # 5. Normalizar resultados
        print("📊 Normalizando resultados...")
        if 'resultado' in df_formatted.columns:
            df_formatted['resultado'] = df_formatted['resultado'].replace({
                'favoravel': 'Favorável',
                'desfavoravel': 'Desfavorável',
                'neutro': 'Neutro',
                'Favoravel': 'Favorável',
                'Desfavoravel': 'Desfavorável',
                'FAVORÁVEL': 'Favorável',
                'DESFAVORÁVEL': 'Desfavorável',
                'NEUTRO': 'Neutro'
            })
        
        # 6. Converter campos numéricos de forma segura
        print("🔢 Convertendo campos numéricos...")
        numeric_fields = ['ano', 'mes', 'trimestre', 'semestre', 'juizo', 'codigo_causa', 'grau_favorabilidade']
        
        for field in numeric_fields:
            if field in df_formatted.columns:
                df_formatted[field] = df_formatted[field].apply(
                    lambda x: self.safe_numeric_conversion(x)
                )
        
        # 7. Classificar período COVID
        print("🦠 Classificando período COVID...")
        if 'ano' in df_formatted.columns:
            df_formatted['periodo_covid'] = df_formatted['ano'].apply(
                lambda x: 'Pré-COVID' if self.safe_numeric_conversion(x) < 2020 
                         else 'COVID' if self.safe_numeric_conversion(x) == 2020 
                         else 'Pós-COVID'
            )
        
        # 8. Limpeza final
        print("🧹 Limpeza final...")
        
        # Remover duplicatas
        df_formatted = df_formatted.drop_duplicates()
        
        # Resetar índice
        df_formatted = df_formatted.reset_index(drop=True)
        
        print(f"✅ Formatação concluída: {len(df_formatted)} registros")
        return df_formatted
    
    def save_csv_utf8(self, df: pd.DataFrame, output_path: str):
        """Salva CSV com UTF-8 garantido"""
        print(f"💾 Salvando CSV UTF-8: {output_path}")
        
        try:
            # Salvar com parâmetros seguros
            df.to_csv(
                output_path,
                index=False,
                encoding='utf-8',
                quoting=1,  # QUOTE_ALL para garantir segurança
                escapechar='\\',
                lineterminator='\n'
            )
            
            print(f"✅ CSV salvo com sucesso: {len(df)} registros")
            
            # Verificar se arquivo foi salvo corretamente
            test_df = pd.read_csv(output_path, encoding='utf-8', nrows=5)
            print(f"✅ Verificação de integridade OK: {len(test_df)} linhas testadas")
            
        except Exception as e:
            print(f"❌ Erro ao salvar CSV: {e}")
            raise
    
    def process_fintech_dataset(self, input_path: str, output_path: str) -> pd.DataFrame:
        """Processa dataset completo com correção de encoding"""
        try:
            print("🚀 PROCESSAMENTO FINTECH - ENCODING CORRIGIDO")
            print("=" * 60)
            
            # 1. Carregar com encoding robusto
            df = self.load_csv_robust(input_path)
            
            # 2. Formatar dados
            df_formatted = self.format_dataframe(df)
            
            # 3. Salvar com UTF-8 garantido
            self.save_csv_utf8(df_formatted, output_path)
            
            print("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            return df_formatted
            
        except Exception as e:
            print(f"❌ ERRO NO PROCESSAMENTO: {e}")
            raise

def processar_dataset_fintech_corrigido():
    """Função principal para processamento corrigido"""
    formatter = FintechDataFormatterCorrigido()
    
    input_path = "fintech-analytics/data/raw/dataset_fintech.xlsx"
    output_path = "fintech-analytics/data/processed/dataset_fintech_limpo_corrigido.csv"
    
    try:
        # Se não existe Excel, tentar CSV atual
        import os
        if not os.path.exists(input_path):
            input_path = "fintech-analytics/data/processed/dataset_fintech_limpo.csv"
        
        df = formatter.process_fintech_dataset(input_path, output_path)
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   Total de registros: {len(df):,}")
        print(f"   Colunas: {len(df.columns)}")
        print(f"   Arquivo salvo: {output_path}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    processar_dataset_fintech_corrigido()