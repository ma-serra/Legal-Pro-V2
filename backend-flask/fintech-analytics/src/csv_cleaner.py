"""
LIMPADOR ROBUSTO DE CSV FINTECH
===================================

Módulo especializado para correção de problemas de formatação e encoding
no arquivo CSV processado do sistema Fintech.
"""

import pandas as pd
import numpy as np
import os
import re
from typing import Optional

class FintechCSVCleaner:
    """
    Limpador especializado para corrigir problemas no CSV Fintech
    """
    
    def __init__(self):
        self.original_lines = 0
        self.cleaned_lines = 0
        self.removed_lines = 0
        
    def clean_csv_file(self, input_path: str, output_path: str) -> bool:
        """
        Limpa arquivo CSV corrigindo problemas de formatação
        
        Args:
            input_path: Caminho do arquivo CSV problemático
            output_path: Caminho do arquivo CSV limpo
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            print("🧹 INICIANDO LIMPEZA ROBUSTA DO CSV")
            print("=" * 50)
            
            # 1. Ler arquivo como texto puro para limpeza linha por linha
            print("📖 Lendo arquivo como texto...")
            with open(input_path, 'r', encoding='utf-8', errors='replace') as file:
                lines = file.readlines()
            
            self.original_lines = len(lines)
            print(f"📊 Linhas originais: {self.original_lines}")
            
            # 2. Limpar e validar linha por linha
            print("🔧 Processando linha por linha...")
            cleaned_lines = self._clean_lines(lines)
            
            # 3. Salvar arquivo limpo
            print("💾 Salvando arquivo limpo...")
            with open(output_path, 'w', encoding='utf-8', newline='') as file:
                file.writelines(cleaned_lines)
            
            self.cleaned_lines = len(cleaned_lines)
            self.removed_lines = self.original_lines - self.cleaned_lines
            
            # 4. Verificar resultado com pandas
            print("✅ Validando arquivo limpo...")
            df_clean = pd.read_csv(output_path)
            
            print(f"\n📊 RESULTADO DA LIMPEZA:")
            print(f"  Linhas originais: {self.original_lines:,}")
            print(f"  Linhas limpas: {self.cleaned_lines:,}")
            print(f"  Linhas removidas: {self.removed_lines:,}")
            print(f"  Registros válidos: {len(df_clean):,}")
            print(f"  Taxa de sucesso: {(len(df_clean)/self.original_lines)*100:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {e}")
            return False
    
    def _clean_lines(self, lines: list) -> list:
        """
        Limpa linhas individuais do CSV
        """
        cleaned = []
        header = None
        current_record = ""
        expected_columns = 21  # Número esperado de colunas
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Pular linhas vazias
            if not line:
                continue
                
            # Primeira linha é o cabeçalho
            if i == 0 or header is None:
                header = line
                cleaned.append(line + '\n')
                expected_columns = len(line.split(','))
                continue
            
            # Verificar se linha parece ser início de novo registro
            if self._is_new_record_line(line, expected_columns):
                # Finalizar registro anterior se existir
                if current_record:
                    cleaned_record = self._clean_record(current_record)
                    if cleaned_record:
                        cleaned.append(cleaned_record + '\n')
                
                # Iniciar novo registro
                current_record = line
            else:
                # Linha órfã - anexar ao registro atual
                if current_record:
                    # Remover quebra de linha indevida e continuar o texto
                    current_record += " " + line
        
        # Finalizar último registro
        if current_record:
            cleaned_record = self._clean_record(current_record)
            if cleaned_record:
                cleaned.append(cleaned_record + '\n')
        
        return cleaned
    
    def _is_new_record_line(self, line: str, expected_columns: int) -> bool:
        """
        Verifica se linha é início de um novo registro
        """
        # Critérios para identificar nova linha de registro:
        # 1. Começa com número de processo (padrão brasileiro)
        # 2. Tem número aproximado de vírgulas esperadas
        
        # Padrão de número de processo brasileiro
        process_pattern = r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
        
        if re.match(process_pattern, line):
            return True
        
        # Verificar número de colunas (tolerância de ±3)
        comma_count = line.count(',')
        if abs(comma_count - (expected_columns - 1)) <= 3:
            return True
            
        return False
    
    def _clean_record(self, record: str) -> Optional[str]:
        """
        Limpa um registro individual
        """
        if not record.strip():
            return None
        
        # Remover múltiplos espaços
        record = re.sub(r'\s+', ' ', record)
        
        # Corrigir aspas quebradas
        record = self._fix_quotes(record)
        
        # Validar se tem conteúdo mínimo necessário
        if len(record.split(',')) < 10:  # Mínimo de colunas
            return None
            
        return record
    
    def _fix_quotes(self, text: str) -> str:
        """
        Corrige problemas com aspas no texto
        """
        # Substituir aspas curvas por aspas retas
        text = text.replace('"', '"').replace('"', '"')
        
        # Escapar aspas dentro de campos CSV
        # Padrão: se há aspas não balanceadas, corrigir
        quote_count = text.count('"')
        if quote_count % 2 != 0:
            # Número ímpar de aspas - adicionar aspas de fechamento no final
            text = text + '"'
        
        return text

def reprocessar_csv_fintech(input_file: str, output_file: str) -> bool:
    """
    Função principal para reprocessar CSV com problemas
    """
    cleaner = FintechCSVCleaner()
    return cleaner.clean_csv_file(input_file, output_file)

if __name__ == "__main__":
    # Teste da limpeza
    input_path = "../data/processed/dataset_fintech_limpo.csv"
    output_path = "../data/processed/dataset_fintech_limpo_corrigido.csv"
    
    success = reprocessar_csv_fintech(input_path, output_path)
    print(f"\n{'✅ Sucesso' if success else '❌ Falha'} na limpeza do CSV")