#!/usr/bin/env python3
"""
Script para analisar o arquivo de advogados
"""

import re

def analyze_file():
    file_path = "../attached_assets/Pasted-Dr-a-Fernando-Aparecida-Total-de-Casos-1-Efici-ncia-0-0-Carteira-Total-R-0-Remune-1758303938097_1758303938098.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    print(f"📄 Tamanho do arquivo: {len(content)} caracteres")
    print(f"📄 Primeiras 500 caracteres:")
    print(content[:500])
    print("\n" + "="*50 + "\n")
    
    # Tentar diferentes padrões
    patterns = [
        r'^(Dr(?:a)?\.?\s*[^\n]+)$',
        r'(Dr(?:a)?\.?\s*[^\n]+)',
        r'^(Dr\(?a\)?\.\s*[^\n]+)',
        r'(Dr\(?a\)?\.\s*[^\n]+)',
        r'(Dr(?:\(a\))?\.?\s*[^\n]*(?:Aparecida|Silveira|Advocacia|Law|Criminal|Consumidor|Previdência)[^\n]*)'
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"🔍 Testando padrão {i}: {pattern}")
        matches = re.findall(pattern, content, re.MULTILINE)
        print(f"   Encontradas {len(matches)} correspondências")
        
        if matches:
            print("   Primeiras 5 correspondências:")
            for j, match in enumerate(matches[:5], 1):
                print(f"   {j}. {match}")
        print()
    
    # Análise linha por linha das primeiras 100 linhas
    lines = content.split('\n')
    print(f"📄 Total de linhas: {len(lines)}")
    print("📄 Primeiras 50 linhas:")
    
    lawyer_lines = []
    for i, line in enumerate(lines[:50], 1):
        line_clean = line.strip()
        if line_clean and ('Dr' in line_clean or 'Dra' in line_clean):
            lawyer_lines.append((i, line_clean))
            print(f"   {i:2d}: ⭐ {line_clean}")
        else:
            print(f"   {i:2d}: {line_clean}")
    
    print(f"\n✅ Linhas com advogados encontradas: {len(lawyer_lines)}")
    
    # Extrair todos os advogados manualmente
    all_lawyers = []
    current_lawyer = None
    
    for line in lines:
        line_clean = line.strip()
        if line_clean.startswith('Dr') and ('Aparecida' in line_clean or 'Silveira' in line_clean or 'Advocacia' in line_clean or 'Law' in line_clean or 'Criminal' in line_clean):
            current_lawyer = line_clean
            if current_lawyer not in all_lawyers:
                all_lawyers.append(current_lawyer)
    
    print(f"\n🎯 Advogados extraídos manualmente: {len(all_lawyers)}")
    for i, lawyer in enumerate(all_lawyers[:10], 1):
        print(f"   {i}. {lawyer}")

if __name__ == "__main__":
    analyze_file()