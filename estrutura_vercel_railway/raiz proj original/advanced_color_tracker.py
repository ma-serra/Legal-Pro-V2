#!/usr/bin/env python3
"""
Ferramenta Avançada de Rastreamento de Cores
Rastrea cores específicas em Bootstrap e permite substituições futuras
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

class AdvancedColorTracker:
    def __init__(self):
        self.color_registry = {
            '#346866': {'status': 'deprecated', 'replacement': '#355d6c', 'description': 'Cor antiga do sistema'},
            '#355d6c': {'status': 'active', 'replacement': None, 'description': 'Cor principal atual do sistema'},
            '#336866': {'status': 'active', 'replacement': None, 'description': 'Cor secundária do sistema'},
            '#40aba0': {'status': 'active', 'replacement': None, 'description': 'Cor de destaque'},
            '#40a9a3': {'status': 'active', 'replacement': None, 'description': 'Cor de destaque alternativa'},
            '#336b69': {'status': 'active', 'replacement': None, 'description': 'Cor de bordas'},
            '#575b5c': {'status': 'active', 'replacement': None, 'description': 'Cor de cards'},
            '#21333d': {'status': 'active', 'replacement': None, 'description': 'Cor de background principal'},
            '#fcfffb': {'status': 'active', 'replacement': None, 'description': 'Cor de texto clara'},
            '#768082': {'status': 'active', 'replacement': None, 'description': 'Cor de texto secundária'}
        }
        
        self.file_extensions = ['.html', '.css', '.js', '.py']
        self.exclude_paths = ['.cache', '__pycache__', '.git', 'node_modules', 'venv', 'uv.lock']
        
    def scan_system(self):
        """Escaneia todo o sistema em busca das cores registradas"""
        results = {}
        
        for root, dirs, files in os.walk('.'):
            # Remove diretórios excluídos
            dirs[:] = [d for d in dirs if not any(exc in d for exc in self.exclude_paths)]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for color in self.color_registry.keys():
                                if color.lower() in content.lower():
                                    if color not in results:
                                        results[color] = []
                                    
                                    # Encontra linhas específicas
                                    lines = content.split('\n')
                                    for i, line in enumerate(lines, 1):
                                        if color.lower() in line.lower():
                                            results[color].append({
                                                'file': file_path,
                                                'line': i,
                                                'content': line.strip(),
                                                'context': self._get_context(lines, i-1)
                                            })
                    except Exception:
                        continue
                        
        return results
    
    def _get_context(self, lines, line_index, context_lines=2):
        """Obtém contexto ao redor de uma linha"""
        start = max(0, line_index - context_lines)
        end = min(len(lines), line_index + context_lines + 1)
        return lines[start:end]
    
    def generate_detailed_report(self):
        """Gera relatório detalhado do status das cores"""
        results = self.scan_system()
        
        print("🎨 RELATÓRIO AVANÇADO DE CORES DO SISTEMA")
        print("=" * 60)
        print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Resumo por status
        active_colors = sum(1 for info in self.color_registry.values() if info['status'] == 'active')
        deprecated_colors = sum(1 for info in self.color_registry.values() if info['status'] == 'deprecated')
        
        print(f"📊 RESUMO:")
        print(f"   Cores ativas: {active_colors}")
        print(f"   Cores obsoletas: {deprecated_colors}")
        print()
        
        # Detalhes por cor
        for color, registry_info in self.color_registry.items():
            status_icon = "✅" if registry_info['status'] == 'active' else "⚠️"
            print(f"{status_icon} {color} - {registry_info['description']}")
            print(f"   Status: {registry_info['status']}")
            
            if color in results:
                total_occurrences = len(results[color])
                files_count = len(set(occ['file'] for occ in results[color]))
                print(f"   Ocorrências: {total_occurrences} em {files_count} arquivos")
                
                # Mostra arquivos principais
                file_groups = {}
                for occ in results[color]:
                    if occ['file'] not in file_groups:
                        file_groups[occ['file']] = 0
                    file_groups[occ['file']] += 1
                
                for file_path, count in sorted(file_groups.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"     📁 {file_path} ({count}x)")
            else:
                print(f"   Ocorrências: 0")
            
            print()
        
        return results
    
    def track_specific_color(self, target_color):
        """Rastrea uma cor específica com detalhes completos"""
        results = self.scan_system()
        
        if target_color not in results:
            print(f"🔍 Cor {target_color} não encontrada no sistema")
            return []
        
        print(f"🎯 RASTREAMENTO DETALHADO: {target_color}")
        print("=" * 50)
        
        color_results = results[target_color]
        
        # Agrupa por arquivo
        by_file = {}
        for result in color_results:
            file_path = result['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(result)
        
        for file_path, occurrences in by_file.items():
            print(f"\n📁 {file_path} ({len(occurrences)} ocorrências)")
            
            for occ in occurrences:
                print(f"   Linha {occ['line']}: {occ['content']}")
                
                # Mostra contexto se necessário
                if len(occ['content']) > 100:
                    print(f"   Contexto:")
                    for ctx_line in occ['context']:
                        if ctx_line.strip():
                            print(f"     {ctx_line[:80]}...")
        
        return color_results
    
    def replace_color_globally(self, old_color, new_color, dry_run=True):
        """Substitui uma cor globalmente no sistema"""
        results = self.scan_system()
        
        if old_color not in results:
            print(f"Cor {old_color} não encontrada no sistema")
            return []
        
        affected_files = list(set(occ['file'] for occ in results[old_color]))
        
        if dry_run:
            print(f"🔍 SIMULAÇÃO DE SUBSTITUIÇÃO: {old_color} → {new_color}")
            print(f"Arquivos que seriam afetados: {len(affected_files)}")
            for file_path in affected_files:
                count = sum(1 for occ in results[old_color] if occ['file'] == file_path)
                print(f"   📁 {file_path} ({count} ocorrências)")
            return affected_files
        
        # Executa substituição real
        modified_files = []
        for file_path in affected_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = re.sub(
                    re.escape(old_color), 
                    new_color, 
                    content, 
                    flags=re.IGNORECASE
                )
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified_files.append(file_path)
                    
            except Exception as e:
                print(f"Erro ao processar {file_path}: {e}")
        
        print(f"✅ {len(modified_files)} arquivos modificados")
        return modified_files
    
    def export_color_map(self, filename='color_map.json'):
        """Exporta mapa de cores para arquivo JSON"""
        results = self.scan_system()
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'color_registry': self.color_registry,
            'scan_results': {}
        }
        
        for color, occurrences in results.items():
            export_data['scan_results'][color] = {
                'total_occurrences': len(occurrences),
                'files': list(set(occ['file'] for occ in occurrences)),
                'file_counts': {}
            }
            
            for occ in occurrences:
                file_path = occ['file']
                if file_path not in export_data['scan_results'][color]['file_counts']:
                    export_data['scan_results'][color]['file_counts'][file_path] = 0
                export_data['scan_results'][color]['file_counts'][file_path] += 1
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Mapa de cores exportado para {filename}")

def main():
    tracker = AdvancedColorTracker()
    
    # Gera relatório completo
    print("Executando varredura completa do sistema...")
    results = tracker.generate_detailed_report()
    
    # Verifica cores específicas
    deprecated_colors = [color for color, info in tracker.color_registry.items() 
                        if info['status'] == 'deprecated']
    
    if deprecated_colors:
        print("⚠️  CORES OBSOLETAS ENCONTRADAS:")
        for color in deprecated_colors:
            if color in results:
                tracker.track_specific_color(color)
    
    # Exporta mapa de cores
    tracker.export_color_map()

if __name__ == "__main__":
    main()