#!/usr/bin/env python3
"""
Script de Debug para Página /juridico/especialistas
Analisa e encontra erros de sintaxe JavaScript
"""

import re
import os
from pathlib import Path

class JSDebugger:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suspicious_patterns = []
    
    def check_file(self, file_path, file_type="unknown"):
        """Analisa um arquivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n🔍 Analisando {file_type}: {file_path}")
            
            # Verificar chaves desbalanceadas
            self.check_braces_balance(content, file_path)
            
            # Verificar vírgulas extras
            self.check_trailing_commas(content, file_path)
            
            # Verificar blocos JavaScript
            if file_type == "HTML":
                self.check_script_blocks(content, file_path)
            
            # Verificar sintaxe JavaScript comum
            if file_type in ["JS", "HTML"]:
                self.check_common_js_errors(content, file_path)
                
            return True
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Erro ao analisar {file_path}: {e}")
            return False
    
    def check_braces_balance(self, content, file_path):
        """Verifica se chaves {} estão balanceadas"""
        stack = []
        in_string = False
        escape_next = False
        string_char = None
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                # Detectar strings
                if char in ['"', "'", '`'] and not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and in_string:
                    in_string = False
                    string_char = None
                elif not in_string:
                    if char == '{':
                        stack.append(('brace', line_num, i))
                    elif char == '}':
                        if not stack:
                            self.errors.append({
                                'file': file_path,
                                'line': line_num,
                                'column': i,
                                'type': 'Unexpected closing brace',
                                'context': line.strip()
                            })
                        else:
                            last = stack.pop()
                            if last[0] != 'brace':
                                self.errors.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'column': i,
                                    'type': 'Mismatched braces',
                                    'context': line.strip()
                                })
        
        # Chaves não fechadas
        for item in stack:
            if item[0] == 'brace':
                self.errors.append({
                    'file': file_path,
                    'line': item[1],
                    'column': item[2],
                    'type': 'Unclosed brace',
                    'context': lines[item[1]-1].strip()
                })
    
    def check_trailing_commas(self, content, file_path):
        """Verifica vírgulas extras que podem causar erros"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Procurar por vírgulas seguidas de } ou ]
            if re.search(r',\s*[}\]]', line):
                self.warnings.append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'Trailing comma before closing bracket',
                    'context': line.strip()
                })
            
            # Procurar por vírgulas duplas
            if ',' in line:
                self.errors.append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'Double comma',
                    'context': line.strip()
                })
    
    def check_script_blocks(self, content, file_path):
        """Analisa blocos <script> em HTML"""
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        for i, script_content in enumerate(scripts):
            print(f"  📄 Analisando bloco script #{i+1}")
            self.check_common_js_errors(script_content, f"{file_path} (script block {i+1})")
    
    def check_common_js_errors(self, content, file_path):
        """Verifica erros comuns de JavaScript"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Função sem parênteses
            if re.search(r'function\s+\w+\s*\{', line):
                self.errors.append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'Function without parentheses',
                    'context': line.strip()
                })
            
            # Objeto com propriedade sem valor
            if re.search(r':\s*,', line):
                self.errors.append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'Property without value',
                    'context': line.strip()
                })
            
            # Chaves extras suspeitas
            if line.strip() == '}' and line_num > 1:
                prev_line = lines[line_num-2].strip()
                if prev_line.endswith(',') or prev_line.endswith('}'):
                    self.suspicious_patterns.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'Suspicious closing brace',
                        'context': f"Previous: {prev_line} | Current: {line.strip()}"
                    })
    
    def check_especialistas_page(self):
        """Analisa especificamente a página de especialistas"""
        files_to_check = [
            ('templates/juridico/especialistas.html', 'HTML'),
            ('static/js/salvamento_validacao_multi_agente.js', 'JS'),
            ('static/css/unique-agent-icons.css', 'CSS'),
            ('static/css/135-unique-logos.css', 'CSS'),
        ]
        
        print("🔍 DEBUG DA PÁGINA /juridico/especialistas")
        print("="*60)
        
        for file_path, file_type in files_to_check:
            if os.path.exists(file_path):
                self.check_file(file_path, file_type)
            else:
                print(f"⚠️ Arquivo não encontrado: {file_path}")
        
        # Verificar outros arquivos JS no diretório static
        static_js_dir = Path('static/js')
        if static_js_dir.exists():
            for js_file in static_js_dir.glob('*.js'):
                if 'especialista' in js_file.name.lower() or 'agente' in js_file.name.lower():
                    self.check_file(str(js_file), 'JS')
    
    def generate_report(self):
        """Gera relatório final"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE DEBUG")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS ({len(self.errors)}):")
            print("-" * 40)
            for error in self.errors:
                print(f"🔸 {error['file']} (linha {error.get('line', '?')}):")
                print(f"   Tipo: {error['type']}")
                print(f"   Contexto: {error['context']}")
                print()
        
        if self.warnings:
            print(f"\n⚠️ AVISOS ({len(self.warnings)}):")
            print("-" * 40)
            for warning in self.warnings:
                print(f"🔸 {warning['file']} (linha {warning.get('line', '?')}):")
                print(f"   Tipo: {warning['type']}")
                print(f"   Contexto: {warning['context']}")
                print()
        
        if self.suspicious_patterns:
            print(f"\n🤔 PADRÕES SUSPEITOS ({len(self.suspicious_patterns)}):")
            print("-" * 40)
            for pattern in self.suspicious_patterns:
                print(f"🔸 {pattern['file']} (linha {pattern.get('line', '?')}):")
                print(f"   Tipo: {pattern['type']}")
                print(f"   Contexto: {pattern['context']}")
                print()
        
        if not self.errors and not self.warnings and not self.suspicious_patterns:
            print("\n✅ Nenhum erro JavaScript óbvio encontrado!")
            print("O erro pode estar em:")
            print("- Dados dinâmicos injetados no template")
            print("- Arquivos externos não verificados")
            print("- Problemas de codificação de caracteres")
        
        print("\n" + "="*60)
        
        return len(self.errors) == 0

def main():
    debugger = JSDebugger()
    debugger.check_especialistas_page()
    
    success = debugger.generate_report()
    
    if not success:
        print("🔧 SUGESTÕES DE CORREÇÃO:")
        print("1. Verificar chaves {} balanceadas")
        print("2. Remover vírgulas extras antes de } ou ]")
        print("3. Verificar strings com aspas não fechadas")
        print("4. Validar dados JSON injetados no template")
    
    return success

if __name__ == "__main__":
    main()