"""
FORMATADOR DE DADOS FINTECH
===============================

Módulo para formatação de dados seguindo o padrão exato especificado.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any

class FintechDataFormatter:
    """
    Formatador especializado para dados Fintech seguindo padrão específico
    """
    
    def __init__(self):
        # Mapeamento de regiões por estado
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
        
        # Mapeamento de grau de favorabilidade
        self.favorabilidade_mapping = {
            'Muito Desfavorável': 1,
            'Desfavorável': 2,
            'Neutro': 3,
            'Favorável': 4,
            'Muito Favorável': 5
        }
    
    def format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Formata DataFrame completo seguindo padrão Fintech
        """
        df_formatted = df.copy()
        
        print("🎨 INICIANDO FORMATAÇÃO DE DADOS FINTECH")
        print("=" * 50)
        
        # 1. Formatar nomes próprios
        df_formatted = self._format_names(df_formatted)
        
        # 2. Mapear regiões
        df_formatted = self._format_regions(df_formatted)
        
        # 3. Formatar instâncias
        df_formatted = self._format_instances(df_formatted)
        
        # 4. Formatar resultados
        df_formatted = self._format_results(df_formatted)
        
        # 5. Formatar códigos de causa
        df_formatted = self._format_causa_codes(df_formatted)
        
        # 6. Formatar tipos de decisão
        df_formatted = self._format_decision_types(df_formatted)
        
        # 7. Limpar descrições
        df_formatted = self._format_descriptions(df_formatted)
        
        # 8. Formatar grau de favorabilidade
        df_formatted = self._format_favorability(df_formatted)
        
        print("✅ Formatação concluída com sucesso")
        return df_formatted
    
    def _format_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar nomes próprios com capitalização correta"""
        if 'adverso_principal' in df.columns:
            print("📝 Formatando nomes próprios...")
            df['adverso_principal'] = df['adverso_principal'].apply(self._capitalize_name)
        return df
    
    def _capitalize_name(self, name: str) -> str:
        """Capitaliza nome próprio corretamente"""
        if pd.isna(name):
            return name
        
        # Converter para string e limpar
        name = str(name).strip()
        
        # Palavras que devem ficar minúsculas
        lowercase_words = ['da', 'de', 'do', 'das', 'dos', 'e', 'em', 'na', 'no', 'para', 'por']
        
        words = name.lower().split()
        formatted_words = []
        
        for i, word in enumerate(words):
            if i == 0 or word not in lowercase_words:
                # Primeira palavra ou palavra que não deve ficar minúscula
                formatted_words.append(word.capitalize())
            else:
                formatted_words.append(word)
        
        return ' '.join(formatted_words)
    
    def _format_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mapear estados para regiões corretas"""
        if 'estado' in df.columns:
            print("🗺️ Mapeando regiões...")
            df['regiao'] = df['estado'].map(self.regiao_mapping).fillna('Não Identificado')
        return df
    
    def _format_instances(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar instâncias para padrão correto"""
        if 'instancia' in df.columns:
            print("⚖️ Formatando instâncias...")
            df['instancia'] = df['instancia'].apply(self._clean_instance)
        return df
    
    def _clean_instance(self, instance: str) -> str:
        """Limpa e padroniza instância"""
        if pd.isna(instance):
            return instance
        
        instance = str(instance).strip()
        
        # Mapeamentos padrão
        if '1' in instance or 'primeiro' in instance.lower():
            return '1º Grau'
        elif '2' in instance or 'segundo' in instance.lower():
            return '2º Grau'
        elif 'tribunal' in instance.lower():
            return 'TRIBUNAL'
        else:
            return instance
    
    def _format_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar resultados para padrão específico"""
        if 'resultado' in df.columns:
            print("📊 Formatando resultados...")
            df['resultado'] = df['resultado'].apply(self._clean_result)
        return df
    
    def _clean_result(self, result: str) -> str:
        """Limpa e padroniza resultado"""
        if pd.isna(result):
            return result
        
        result = str(result).lower().strip()
        
        if 'favorável' in result or 'favorable' in result:
            return 'Favorável'
        elif 'desfavorável' in result or 'desfavoravel' in result:
            return 'Desfavorável'
        elif 'neutro' in result or 'neutral' in result:
            return 'Neutro'
        else:
            return 'Neutro'  # Default
    
    def _format_causa_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar códigos de causa removendo .0"""
        if 'codigo_causa' in df.columns:
            print("🔢 Formatando códigos de causa...")
            df['codigo_causa'] = df['codigo_causa'].apply(lambda x: int(x) if pd.notna(x) and str(x).endswith('.0') else x)
        return df
    
    def _format_decision_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar tipos de decisão com capitalização correta"""
        if 'tipo_decisao_original' in df.columns:
            print("📋 Formatando tipos de decisão...")
            df['tipo_decisao_original'] = df['tipo_decisao_original'].apply(self._clean_decision_type)
        return df
    
    def _clean_decision_type(self, decision: str) -> str:
        """Limpa e formata tipo de decisão"""
        if pd.isna(decision):
            return decision
        
        decision = str(decision).strip()
        
        # Aplicar capitalização de título mas manter certas palavras
        words = decision.split()
        formatted_words = []
        
        for word in words:
            if word.lower() in ['da', 'de', 'do', 'das', 'dos', 'e', 'em', 'na', 'no', 'para', 'por', '-']:
                formatted_words.append(word.lower())
            elif word.isupper() and len(word) > 3:
                # Palavras em maiúsculo que são siglas ou nomes importantes
                formatted_words.append(word.title())
            else:
                formatted_words.append(word.capitalize())
        
        return ' '.join(formatted_words)
    
    def _format_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpar e formatar descrições"""
        if 'descricao_ocorrencia' in df.columns:
            print("📝 Formatando descrições...")
            df['descricao_ocorrencia'] = df['descricao_ocorrencia'].apply(self._clean_description)
        return df
    
    def _clean_description(self, description: str) -> str:
        """Limpa e formata descrição"""
        if pd.isna(description):
            return description
        
        description = str(description).strip()
        
        # Remover múltiplos espaços
        description = re.sub(r'\s+', ' ', description)
        
        # Capitalizar primeira letra
        if description:
            description = description[0].upper() + description[1:]
        
        return description
    
    def _format_favorability(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formatar grau de favorabilidade como números simples"""
        if 'grau_favorabilidade' in df.columns:
            print("⭐ Formatando grau de favorabilidade...")
            df['grau_favorabilidade'] = df['grau_favorabilidade'].apply(lambda x: int(x) if pd.notna(x) else x)
        return df

def format_fintech_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função principal para formatação de dados Fintech
    """
    formatter = FintechDataFormatter()
    return formatter.format_dataframe(df)

if __name__ == "__main__":
    # Teste do formatador
    print("🧪 Testando formatador de dados Fintech...")