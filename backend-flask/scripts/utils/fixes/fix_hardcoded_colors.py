#!/usr/bin/env python3
"""
Script para corrigir cores hardcoded que impedem alterações nas categorias
Direito Tributário, Direito Digital e Direito Imobiliário
"""

import os
import re
from models import db, CategoriaJuridica
from app import app

def fix_hardcoded_colors():
    """Remove cores hardcoded e aplica sistema dinâmico baseado no banco"""
    
    print("🔧 Iniciando correção de cores hardcoded...")
    
    # 1. Buscar cores atuais no banco de dados
    with app.app_context():
        categorias = db.session.query(CategoriaJuridica).filter(
            CategoriaJuridica.nome.in_([
                'Direito Tributário', 
                'Direito Digital', 
                'Direito Imobiliário'
            ])
        ).all()
        
        cores_atuais = {}
        for cat in categorias:
            cores_atuais[cat.nome] = cat.cor
            print(f"📊 {cat.nome}: {cat.cor}")
    
    # 2. Arquivo principal a corrigir
    template_path = 'templates/juridico/especialistas.html'
    
    # 3. Cores hardcoded a remover/substituir
    problematic_colors = [
        '#3bafa5',  # Direito Tributário
        '#e54b3e',  # Direito Digital/Imobiliário
        '#e34c41',  # Direito Imobiliário (nova)
        '#40a9a3',  # Cores de form
        '#40aba0'   # Cores de upload
    ]
    
    print("🎨 Corrigindo template principal...")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup do arquivo original
        backup_path = template_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Backup criado: {backup_path}")
        
        # 4. Remover definições CSS específicas por área que impedem mudanças
        areas_to_clean = [
            'digital', 'tributario', 'imobiliario', 'consumidor'
        ]
        
        for area in areas_to_clean:
            # Padrão para encontrar e remover blocos CSS específicos de área
            pattern = rf'\.agent-card\[data-area="{area}"\]\s*\{{[^}}]*\}}'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                content = content.replace(match, '')
                print(f"🗑️  Removido CSS hardcoded para {area}")
        
        # 5. Substituir cores hardcoded por variáveis CSS dinâmicas
        color_replacements = [
            ('#40a9a3', 'var(--accent-main)'),
            ('#40aba0', 'var(--accent-main)'),
            ('#3bafa5', 'var(--accent-main)'),
            ('#e54b3e', 'var(--accent-main)'),
            ('#e34c41', 'var(--accent-main)')
        ]
        
        for old_color, new_color in color_replacements:
            if old_color in content:
                content = content.replace(old_color, new_color)
                print(f"🔄 Substituído {old_color} → {new_color}")
        
        # 6. Adicionar sistema dinâmico de cores baseado no banco
        dynamic_css = """
        /* Sistema dinâmico de cores baseado no banco de dados */
        {% for categoria_nome, categoria_data in categorias_info.items() %}
        .agent-card[data-area="{{ categoria_data.area_code }}"] {
            border-left: 4px solid {{ categoria_data.cor }};
        }
        .agent-card[data-area="{{ categoria_data.area_code }}"] .agent-logo i,
        .agent-card[data-area="{{ categoria_data.area_code }}"] .capability-item i {
            color: {{ categoria_data.cor }} !important;
        }
        .agent-card[data-area="{{ categoria_data.area_code }}"] .btn-details,
        .agent-card[data-area="{{ categoria_data.area_code }}"] .area-tag,
        .agent-card[data-area="{{ categoria_data.area_code }}"] .badge {
            background: {{ categoria_data.cor }} !important;
            color: white !important;
        }
        .agent-card[data-area="{{ categoria_data.area_code }}"] .btn-edit,
        .agent-card[data-area="{{ categoria_data.area_code }}"] .btn-use {
            border-color: {{ categoria_data.cor }} !important;
            color: {{ categoria_data.cor }} !important;
        }
        {% endfor %}
        """
        
        # Inserir o CSS dinâmico antes do fechamento da tag <style>
        if '</style>' in content:
            content = content.replace('</style>', dynamic_css + '\n        </style>')
            print("✅ Adicionado sistema dinâmico de cores")
        
        # 7. Salvar arquivo corrigido
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("💾 Template corrigido e salvo")
        
        # 8. Verificar app.py para garantir que area_code está sendo enviado
        app_path = 'app.py'
        print("🔧 Verificando mapeamento de área em app.py...")
        
        with open(app_path, 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Verificar se o mapeamento de área existe
        area_mapping_pattern = r'area_mapping\s*=\s*\{[^}]+\}'
        if not re.search(area_mapping_pattern, app_content):
            print("⚠️  Mapeamento de área não encontrado em app.py")
        else:
            print("✅ Mapeamento de área encontrado em app.py")
        
        print("🎉 Correção concluída com sucesso!")
        print("\n📋 Resumo das correções:")
        print("   ✓ Cores hardcoded removidas/substituídas")
        print("   ✓ CSS específico por área removido")
        print("   ✓ Sistema dinâmico baseado no banco implementado")
        print("   ✓ Backup do arquivo original criado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        return False

def verify_colors_in_database():
    """Verifica e exibe cores atuais no banco de dados"""
    print("\n🔍 Verificando cores no banco de dados...")
    
    with app.app_context():
        categorias = db.session.query(CategoriaJuridica).filter(
            CategoriaJuridica.nome.in_([
                'Direito Tributário', 
                'Direito Digital', 
                'Direito Imobiliário'
            ])
        ).all()
        
        for cat in categorias:
            print(f"   {cat.nome}: {cat.cor} ({cat.icone})")

if __name__ == "__main__":
    verify_colors_in_database()
    fix_hardcoded_colors()
    verify_colors_in_database()