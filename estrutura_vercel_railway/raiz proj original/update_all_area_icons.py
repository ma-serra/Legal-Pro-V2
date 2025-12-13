"""
Script para atualizar o CSS de todas as áreas jurídicas com o padrão de ícones
com fundo branco e bordas coloridas
"""

import re

def update_area_css():
    """Atualiza o CSS de todas as áreas com o padrão consistente"""
    
    # Definir cores por área
    area_colors = {
        'bancario': '#c29e74',
        'recuperacao': '#ffc107',
        'securitario': '#0dcaf0',
        'saude': '#fd6c6c',
        'internacional': '#17a2b8',
        'riscos': '#6f42c1',
        'negociacao': '#20c997',
        'consumidor': '#28a745',
        'agrario': '#fd7e14',
        'tributario': '#6610f2',
        'previdenciario': '#e83e8c',
        'imobiliario': '#795548',
        'digital': '#ff5722',
        'ambiental': '#4caf50'
    }
    
    # Gerar CSS para cada área
    css_content = ""
    
    for area, color in area_colors.items():
        # Converter cor hex para rgba para box-shadow
        hex_color = color.replace('#', '')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        rgba_shadow = f"rgba({r}, {g}, {b}, 0.2)"
        
        css_block = f'''
        .agent-card[data-area="{area}"] {{
            border-left: 4px solid {color};
        }}
        .agent-card[data-area="{area}"] .agent-logo i,
        .agent-card[data-area="{area}"] .capability-item i {{
            color: {color} !important;
            background-color: white !important;
            padding: 8px !important;
            border-radius: 50% !important;
            border: 2px solid {color} !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 40px !important;
            height: 40px !important;
            box-shadow: 0 2px 4px {rgba_shadow} !important;
        }}
        .agent-card[data-area="{area}"] .agent-logo i:hover,
        .agent-card[data-area="{area}"] .capability-item i:hover {{
            background-color: {color} !important;
            color: white !important;
            transform: scale(1.05) !important;
            transition: all 0.3s ease !important;
        }}
        .agent-card[data-area="{area}"] .btn-details,
        .agent-card[data-area="{area}"] .area-tag,
        .agent-card[data-area="{area}"] .badge {{
            background: {color} !important;
            color: white !important;
        }}
        .agent-card[data-area="{area}"] .btn-edit,
        .agent-card[data-area="{area}"] .btn-use {{
            border-color: {color} !important;
            color: {color} !important;
        }}'''
        
        css_content += css_block
    
    return css_content

def main():
    """Função principal"""
    print("🎨 Gerando CSS para todas as áreas jurídicas...")
    
    css_content = update_area_css()
    
    # Salvar o CSS
    with open("area_icons_complete.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    
    print("✅ CSS gerado com sucesso!")
    print("📄 Arquivo salvo: area_icons_complete.css")
    print("\n📋 Próximos passos:")
    print("1. Copiar o conteúdo do arquivo para o template")
    print("2. Substituir as seções CSS existentes")
    print("3. Verificar se todas as áreas estão funcionando")

if __name__ == "__main__":
    main()