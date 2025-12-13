#!/usr/bin/env python3
"""
Script para sincronizar ícones dos cards principais com páginas de detalhes e edição
Extrai os ícones do arquivo especialistas.html e aplica nas rotas de detalhes/edição
"""

import re
import os
from pathlib import Path

def extract_icon_mappings():
    """Extrai mapeamento de ícones do arquivo de especialistas"""
    especialistas_file = "templates/juridico/especialistas.html"
    
    if not os.path.exists(especialistas_file):
        print(f"❌ Arquivo {especialistas_file} não encontrado")
        return {}
    
    with open(especialistas_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões para extrair mapeamentos de ícones
    icon_mappings = {}
    
    # Padrão 1: {% elif "Nome" in agente.nome %}
    pattern1 = r'{% elif "([^"]+)" in agente\.nome[^%]*%}\s*<i class="([^"]+)"[^>]*></i>'
    matches1 = re.findall(pattern1, content, re.MULTILINE)
    
    for keyword, icon_class in matches1:
        icon_mappings[keyword] = icon_class
    
    # Padrão 2: Mapeamentos diretos por categoria
    pattern2 = r'{% if agente\.categoria[^%]*%}\s*<i class="([^"]+)"[^>]*></i>'
    matches2 = re.findall(pattern2, content, re.MULTILINE)
    
    # Adicionar ícones padrão por categoria
    default_icons = {
        "Criminal": "fas fa-gavel",
        "Penal": "fas fa-gavel", 
        "Execução Penal": "fas fa-balance-scale",
        "Tribunal do Júri": "fas fa-users",
        "Sustentação": "fas fa-microphone",
        "Evidências": "fas fa-search",
        "Revisor": "fas fa-check-double",
        "Empresarial": "fas fa-building",
        "Societário": "fas fa-building",
        "Contratos": "fas fa-handshake",
        "Trabalhista": "fas fa-hard-hat",
        "CLT": "fas fa-hard-hat",
        "Bancário": "fas fa-university",
        "Compliance Bancário": "fas fa-shield-alt",
        "Contencioso Bancário": "fas fa-balance-scale",
        "Securitário": "fas fa-shield-alt",
        "Sinistros": "fas fa-file-medical",
        "Compliance SUSEP": "fas fa-shield",
        "Contencioso Securitário": "fas fa-briefcase",
        "Consumidor": "fas fa-shopping-cart",
        "CDC": "fas fa-shopping-cart",
        "Recuperação": "fas fa-money-bill-wave",
        "Crédito": "fas fa-money-bill-wave",
        "Riscos": "fas fa-chart-line"
    }
    
    icon_mappings.update(default_icons)
    
    print(f"✅ Extraídos {len(icon_mappings)} mapeamentos de ícones")
    return icon_mappings

def get_icon_for_agent_name(agent_name, icon_mappings):
    """Retorna o ícone apropriado para um nome de agente"""
    for keyword, icon_class in icon_mappings.items():
        if keyword.lower() in agent_name.lower():
            return icon_class
    
    # Ícone padrão
    return "fas fa-user-tie"

def create_icon_function():
    """Cria função Python para determinar ícones"""
    icon_mappings = extract_icon_mappings()
    
    function_code = '''
def get_agent_icon(agent_name, categoria_nome=None):
    """
    Retorna o ícone apropriado para um agente baseado no nome e categoria
    Esta função replica a lógica do template especialistas.html
    """
    agent_name = agent_name or ""
    categoria_nome = categoria_nome or ""
    
    # Mapeamento de ícones baseado no nome do agente
    icon_mappings = {
'''
    
    for keyword, icon_class in icon_mappings.items():
        function_code += f'        "{keyword}": "{icon_class}",\n'
    
    function_code += '''    }
    
    # Verificar correspondências por palavra-chave
    for keyword, icon_class in icon_mappings.items():
        if keyword.lower() in agent_name.lower():
            return icon_class
    
    # Ícones por categoria se não encontrar por nome
    if "penal" in categoria_nome.lower() or "criminal" in categoria_nome.lower():
        return "fas fa-gavel"
    elif "empresarial" in categoria_nome.lower():
        return "fas fa-building"
    elif "trabalhista" in categoria_nome.lower():
        return "fas fa-hard-hat"
    elif "bancário" in categoria_nome.lower():
        return "fas fa-university"
    elif "securitário" in categoria_nome.lower():
        return "fas fa-shield-alt"
    elif "consumidor" in categoria_nome.lower():
        return "fas fa-shopping-cart"
    
    # Ícone padrão
    return "fas fa-user-tie"
'''
    
    return function_code

def update_app_py():
    """Adiciona função de ícones ao app.py"""
    app_file = "app.py"
    
    if not os.path.exists(app_file):
        print(f"❌ Arquivo {app_file} não encontrado")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se a função já existe
    if "def get_agent_icon(" in content:
        print("✅ Função get_agent_icon já existe no app.py")
        return True
    
    # Criar a função
    icon_function = create_icon_function()
    
    # Encontrar local para inserir (após imports)
    import_pattern = r'(from flask import[^\n]+\n)'
    match = re.search(import_pattern, content)
    
    if match:
        insert_pos = match.end()
        new_content = (content[:insert_pos] + "\n" + icon_function + "\n" + 
                      content[insert_pos:])
        
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Função get_agent_icon adicionada ao app.py")
        return True
    else:
        print("❌ Não foi possível encontrar local para inserir a função")
        return False

def update_detail_templates():
    """Atualiza templates de detalhes para usar ícones consistentes"""
    templates_to_update = [
        "templates/agente_detalhe.html",
        "templates/agente_edit.html", 
        "templates/juridico/agente_detalhes.html",
        "templates/juridico/agente_editar.html"
    ]
    
    for template_path in templates_to_update:
        if os.path.exists(template_path):
            update_template_icons(template_path)

def update_template_icons(template_path):
    """Atualiza um template específico para usar ícones consistentes"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar ícones hardcoded
    icon_pattern = r'<i class="fas fa-[^"]*"[^>]*></i>'
    
    # Substituir por chamada da função
    replacement = '{{ get_agent_icon(agente.nome, agente.categoria.nome if agente.categoria else "") | safe }}'
    
    # Se já tem a função, não alterar
    if "get_agent_icon" in content:
        print(f"✅ Template {template_path} já usa função de ícones")
        return
    
    # Procurar por padrões específicos de ícones e substituir
    patterns_to_replace = [
        r'<i class="fas fa-user-tie[^"]*"[^>]*></i>',
        r'<i class="fas fa-gavel[^"]*"[^>]*></i>',
        r'<i class="fas fa-building[^"]*"[^>]*></i>',
        r'<i class="fas fa-hard-hat[^"]*"[^>]*></i>'
    ]
    
    updated = False
    for pattern in patterns_to_replace:
        if re.search(pattern, content):
            content = re.sub(pattern, f'<i class="{replacement}"></i>', content)
            updated = True
    
    if updated:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Template {template_path} atualizado com ícones consistentes")
    else:
        print(f"ℹ️  Template {template_path} não precisou de atualizações")

def create_template_filter():
    """Cria filtro Jinja2 para ícones"""
    filter_code = '''
# Adicionar ao app.py após a criação do app
@app.template_filter('agent_icon')
def agent_icon_filter(agent_name, categoria_nome=None):
    """Filtro para obter ícone do agente"""
    return get_agent_icon(agent_name, categoria_nome)

# Também disponibilizar como função global no template
@app.template_global()
def get_agent_icon_template(agent_name, categoria_nome=None):
    """Função global para templates obterem ícone do agente"""
    return get_agent_icon(agent_name, categoria_nome)
'''
    
    return filter_code

def main():
    """Função principal"""
    print("🔄 Iniciando sincronização de ícones dos agentes especialistas...")
    
    # 1. Extrair mapeamentos de ícones
    icon_mappings = extract_icon_mappings()
    
    if not icon_mappings:
        print("❌ Nenhum mapeamento de ícone encontrado")
        return
    
    # 2. Atualizar app.py com função de ícones
    if update_app_py():
        print("✅ Função de ícones adicionada ao app.py")
    
    # 3. Atualizar templates de detalhes
    update_detail_templates()
    
    # 4. Criar exemplo de uso
    example_code = create_template_filter()
    
    with open("icon_integration_example.py", "w", encoding="utf-8") as f:
        f.write("# Código para adicionar ao app.py\n" + example_code)
    
    print("\n✅ Sincronização de ícones concluída!")
    print("📝 Arquivo 'icon_integration_example.py' criado com código adicional")
    print("\n📋 Próximos passos manuais:")
    print("1. Adicionar o filtro template ao app.py")
    print("2. Testar as páginas de detalhes/edição")
    print("3. Verificar se os ícones estão consistentes")

if __name__ == "__main__":
    main()