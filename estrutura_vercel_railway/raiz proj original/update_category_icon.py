#!/usr/bin/env python3
"""
Script para localizar e atualizar a div específica com ícone da casa
"""
import os
import re

def find_and_replace_category_icon():
    """Encontra e substitui a div específica com fas fa-home e background #0f5132"""
    
    # Padrão para encontrar a div específica
    old_pattern = r'<div class="category-icon me-3" style="background: #0f5132;">\s*<i class="fas fa-home"></i>\s*</div>'
    new_replacement = '<div class="category-icon me-3" style="background: #e34c41;">\n                                    <i class="fas fa-home"></i>\n                                </div>'
    
    files_updated = []
    
    # Procurar em todos os arquivos HTML
    for root, dirs, files in os.walk('.'):
        # Pular diretórios desnecessários
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar se contém o padrão que procuramos
                    if '#0f5132' in content and 'fas fa-home' in content and 'category-icon' in content:
                        # Tentar várias variações do padrão
                        patterns = [
                            r'<div class="category-icon me-3" style="background:\s*#0f5132;">\s*<i class="fas fa-home"></i>\s*</div>',
                            r'<div class="category-icon me-3" style="background: #0f5132;">\s*<i class="fas fa-home"></i>\s*</div>',
                            r'background:\s*#0f5132'
                        ]
                        
                        updated = False
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                                if 'background' in pattern and '#0f5132' in pattern:
                                    # Substituir apenas a cor
                                    content = re.sub(r'background:\s*#0f5132', 'background: #e34c41', content)
                                    updated = True
                                    break
                                else:
                                    content = re.sub(pattern, new_replacement, content, flags=re.IGNORECASE | re.MULTILINE)
                                    updated = True
                                    break
                        
                        if updated:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            files_updated.append(file_path)
                            print(f"✅ Atualizado: {file_path}")
                
                except Exception as e:
                    print(f"❌ Erro ao processar {file_path}: {e}")
    
    if files_updated:
        print(f"\n🎯 {len(files_updated)} arquivo(s) atualizado(s)")
        for file in files_updated:
            print(f"   - {file}")
    else:
        print("⚠️  Nenhum arquivo encontrado com o padrão especificado")
        print("Procurando por arquivos que contenham as partes relevantes...")
        
        # Busca mais ampla
        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if '#0f5132' in content:
                            print(f"📂 Arquivo contém #0f5132: {file_path}")
                            # Mostrar as linhas relevantes
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if '#0f5132' in line:
                                    print(f"   Linha {i+1}: {line.strip()}")
                                    
                    except Exception as e:
                        continue

if __name__ == "__main__":
    find_and_replace_category_icon()