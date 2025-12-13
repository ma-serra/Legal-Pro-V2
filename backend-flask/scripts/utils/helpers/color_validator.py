#!/usr/bin/env python3
"""
Ferramenta de Validação e Rastreamento de Cores do Sistema
Rastrea cores específicas em todos os arquivos do sistema Bootstrap
"""

import os
import re
import glob
from collections import defaultdict

class ColorValidator:
    def __init__(self):
        self.colors_to_track = [
            '#355d6c',
            '#355d6c', 
            '#336866',
            '#40aba0',
            '#40a9a3',
            '#336b69',
            '#575b5c',
            '#21333d',
            '#fcfffb',
            '#768082'
        ]
        
        self.file_patterns = [
            '**/*.html',
            '**/*.css', 
            '**/*.js',
            '**/*.py'
        ]
        
        self.results = defaultdict(lambda: defaultdict(list))
    
    def scan_files(self):
        """Escaneia todos os arquivos em busca das cores especificadas"""
        print("🔍 Iniciando varredura completa do sistema...")
        
        for pattern in self.file_patterns:
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                # Ignora arquivos de cache e temporários
                if any(skip in file_path for skip in ['.cache', '__pycache__', '.git', 'node_modules', 'venv']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        line_number = 0
                        
                        for line in content.split('\n'):
                            line_number += 1
                            
                            for color in self.colors_to_track:
                                if color.lower() in line.lower():
                                    self.results[color][file_path].append({
                                        'line': line_number,
                                        'content': line.strip()
                                    })
                                    
                except Exception as e:
                    print(f"❌ Erro ao ler {file_path}: {e}")
    
    def find_bootstrap_elements(self, target_color='#355d6c'):
        """Encontra elementos Bootstrap específicos com a cor alvo"""
        print(f"\n🎯 Buscando elementos Bootstrap com cor {target_color}...")
        
        bootstrap_patterns = [
            r'\.btn[^{]*{[^}]*background-color:\s*' + re.escape(target_color),
            r'\.bg-[^{]*{[^}]*background-color:\s*' + re.escape(target_color),
            r'\.card-[^{]*{[^}]*background-color:\s*' + re.escape(target_color),
            r'style=["\'][^"\']*background-color:\s*' + re.escape(target_color),
            r'\.border-[^{]*{[^}]*border-color:\s*' + re.escape(target_color)
        ]
        
        bootstrap_results = []
        
        for pattern in self.file_patterns:
            files = glob.glob(pattern, recursive=True)
            
            for file_path in files:
                if any(skip in file_path for skip in ['.cache', '__pycache__', '.git']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for bp_pattern in bootstrap_patterns:
                            matches = re.finditer(bp_pattern, content, re.IGNORECASE | re.MULTILINE)
                            
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                bootstrap_results.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'pattern': bp_pattern,
                                    'match': match.group()
                                })
                                
                except Exception as e:
                    continue
        
        return bootstrap_results
    
    def generate_report(self):
        """Gera relatório completo das cores encontradas"""
        print("\n📊 RELATÓRIO DE VALIDAÇÃO DE CORES")
        print("=" * 50)
        
        total_occurrences = 0
        
        for color, files in self.results.items():
            if files:
                color_count = sum(len(occurrences) for occurrences in files.values())
                total_occurrences += color_count
                
                print(f"\n🎨 COR: {color}")
                print(f"   Total de ocorrências: {color_count}")
                
                for file_path, occurrences in files.items():
                    print(f"   📁 {file_path} ({len(occurrences)} ocorrências)")
                    
                    for occ in occurrences[:3]:  # Mostra apenas as 3 primeiras
                        print(f"      Linha {occ['line']}: {occ['content'][:80]}...")
                    
                    if len(occurrences) > 3:
                        print(f"      ... e mais {len(occurrences) - 3} ocorrências")
        
        print(f"\n📈 TOTAL GERAL: {total_occurrences} ocorrências encontradas")
        
        # Busca elementos Bootstrap específicos
        bootstrap_elements = self.find_bootstrap_elements('#355d6c')
        if bootstrap_elements:
            print(f"\n⚠️  ELEMENTOS BOOTSTRAP NÃO CONVERTIDOS ({len(bootstrap_elements)}):")
            for elem in bootstrap_elements:
                print(f"   📁 {elem['file']} (linha {elem['line']})")
                print(f"      {elem['match'][:100]}...")
    
    def fix_remaining_colors(self, old_color='#355d6c', new_color='#355d6c'):
        """Corrige cores remanescentes automaticamente"""
        print(f"\n🔧 Corrigindo cores remanescentes: {old_color} → {new_color}")
        
        fixed_files = []
        
        if old_color in self.results:
            for file_path in self.results[old_color].keys():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Substitui todas as ocorrências (case insensitive)
                    new_content = re.sub(
                        re.escape(old_color), 
                        new_color, 
                        content, 
                        flags=re.IGNORECASE
                    )
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        fixed_files.append(file_path)
                        
                except Exception as e:
                    print(f"❌ Erro ao corrigir {file_path}: {e}")
        
        print(f"✅ {len(fixed_files)} arquivos corrigidos")
        return fixed_files

def main():
    validator = ColorValidator()
    
    # Executa varredura completa
    validator.scan_files()
    
    # Gera relatório
    validator.generate_report()
    
    # Corrige cores remanescentes
    fixed = validator.fix_remaining_colors('#355d6c', '#355d6c')
    
    if fixed:
        print("\n🔄 Executando nova varredura após correções...")
        validator.results.clear()
        validator.scan_files()
        validator.generate_report()

if __name__ == "__main__":
    main()