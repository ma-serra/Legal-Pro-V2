"""
Script para aplicar sistema de redimensionamento a todos os templates do editor
Mapeia precisamente onde estão todos os 10 tipos de templates e aplica handles funcionais
"""

import re
import os

def mapear_templates_editor():
    """Mapeia todos os templates do editor e suas localizações"""
    
    templates_map = {
        'urgent_box': {
            'name': 'Caixa Urgente',
            'class': 'urgent-box',
            'insert_function': 'insertUrgentBox',
            'duplicate_function': 'duplicateUrgentBox',
            'delete_function': 'deleteUrgentBox',
            'html_pattern': r'<div[^>]*class="[^"]*urgent-box[^"]*"[^>]*>',
        },
        'warning_box': {
            'name': 'Caixa Aviso',
            'class': 'warning-box',
            'insert_function': 'insertWarningBox',
            'duplicate_function': 'duplicateWarningBox',
            'delete_function': 'deleteWarningBox',
            'html_pattern': r'<div[^>]*class="[^"]*warning-box[^"]*"[^>]*>',
        },
        'success_box': {
            'name': 'Caixa de Sucesso',
            'class': 'success-box',
            'insert_function': 'insertSuccessBox',
            'duplicate_function': 'duplicateSuccessBox',
            'delete_function': 'deleteSuccessBox',
            'html_pattern': r'<div[^>]*class="[^"]*success-box[^"]*"[^>]*>',
        },
        'info_box': {
            'name': 'Caixa de Informação',
            'class': 'info-box',
            'insert_function': 'insertInfoBox',
            'duplicate_function': 'duplicateInfoBox',
            'delete_function': 'deleteInfoBox',
            'html_pattern': r'<div[^>]*class="[^"]*info-box[^"]*"[^>]*>',
        },
        'legal_timeline': {
            'name': 'Timeline Jurídico',
            'class': 'legal-timeline',
            'insert_function': 'insertTimeline',
            'duplicate_function': 'duplicateTimeline',
            'delete_function': 'deleteTimeline',
            'html_pattern': r'<div[^>]*class="[^"]*legal-timeline[^"]*"[^>]*>',
        },
        'legal_table': {
            'name': 'Tabela Jurídica',
            'class': 'legal-table',
            'insert_function': 'insertTable',
            'duplicate_function': 'duplicateTable',
            'delete_function': 'deleteTable',
            'html_pattern': r'<div[^>]*class="[^"]*legal-table[^"]*"[^>]*>',
        },
        'progress_bar': {
            'name': 'Barra de Progresso',
            'class': 'progress-container',
            'insert_function': 'insertProgress',
            'duplicate_function': 'duplicateProgress',
            'delete_function': 'deleteProgress',
            'html_pattern': r'<div[^>]*class="[^"]*progress-container[^"]*"[^>]*>',
        },
        'legal_quote': {
            'name': 'Citação Legal',
            'class': 'legal-quote',
            'insert_function': 'insertQuote',
            'duplicate_function': 'duplicateQuote',
            'delete_function': 'deleteQuote',
            'html_pattern': r'<div[^>]*class="[^"]*legal-quote[^"]*"[^>]*>',
        },
        'status_badge': {
            'name': 'Badge de Status',
            'class': 'status-badge',
            'insert_function': 'insertBadge',
            'duplicate_function': 'duplicateBadge',
            'delete_function': 'deleteBadge',
            'html_pattern': r'<span[^>]*class="[^"]*status-badge[^"]*"[^>]*>',
        },
        'visual_elements': {
            'name': 'Elementos Visuais',
            'class': 'visual-element',
            'insert_function': 'insertVisualElement',
            'duplicate_function': 'duplicateVisualElement',
            'delete_function': 'deleteVisualElement',
            'html_pattern': r'<div[^>]*class="[^"]*visual-element[^"]*"[^>]*>',
        }
    }
    
    return templates_map

def gerar_codigo_aplicacao_handles():
    """Gera código JavaScript para aplicar handles a todos os templates"""
    
    templates = mapear_templates_editor()
    
    js_code = """
// =============================================================================
// SISTEMA COMPLETO DE REDIMENSIONAMENTO PARA TODOS OS TEMPLATES DO EDITOR
// Aplicação automática de handles de redimensionamento para os 10 tipos de templates
// =============================================================================

function applyResizeHandlesToAllTemplates() {
    console.log('🔧 Iniciando aplicação de handles de redimensionamento para todos os templates...');
    
    // Mapeamento de todos os templates do editor
    const templateSelectors = [
"""
    
    # Adiciona seletores para cada template
    for template_key, template_info in templates.items():
        js_code += f"        '.{template_info['class']}',  // {template_info['name']}\n"
    
    js_code += """    ];
    
    let totalApplied = 0;
    
    // Aplicar handles para cada tipo de template
    templateSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        console.log(`🎯 Encontrados ${elements.length} elementos para ${selector}`);
        
        elements.forEach(element => {
            if (!element.hasAttribute('data-resize-applied')) {
                applyElementFeatures(element);
                element.setAttribute('data-resize-applied', 'true');
                totalApplied++;
                console.log(`✅ Handles aplicados ao elemento ${selector}`);
            }
        });
    });
    
    console.log(`🎉 Sistema de redimensionamento aplicado a ${totalApplied} elementos!`);
    return totalApplied;
}

// Função para corrigir eventos que causam erro preventDefault
function fixPreventDefaultErrors() {
    console.log('🔧 Corrigindo erros de preventDefault...');
    
    // Corrigir eventos de arrastar que causam erro
    document.addEventListener('dragstart', function(e) {
        if (e && typeof e.preventDefault === 'function') {
            e.preventDefault();
        }
    }, true);
    
    document.addEventListener('drop', function(e) {
        if (e && typeof e.preventDefault === 'function') {
            e.preventDefault();
        }
    }, true);
    
    document.addEventListener('dragover', function(e) {
        if (e && typeof e.preventDefault === 'function') {
            e.preventDefault();
        }
    }, true);
}

// Função para aplicar handles em elementos específicos por classe
function applyHandlesToSpecificClass(className) {
    console.log(`🎯 Aplicando handles específicos para classe: ${className}`);
    
    const elements = document.querySelectorAll(`.${className}`);
    let applied = 0;
    
    elements.forEach(element => {
        if (!element.hasAttribute('data-resize-applied')) {
            applyElementFeatures(element);
            element.setAttribute('data-resize-applied', 'true');
            applied++;
        }
    });
    
    console.log(`✅ Handles aplicados a ${applied} elementos da classe ${className}`);
    return applied;
}

// Observer para aplicar handles automaticamente em novos elementos
function setupAutomaticHandleApplication() {
    console.log('👁️ Configurando observador automático para novos elementos...');
    
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // Verificar se o elemento é um dos templates
                    const templateClasses = ["""
    
    # Adiciona classes dos templates
    for i, (template_key, template_info) in enumerate(templates.items()):
        comma = "," if i < len(templates) - 1 else ""
        js_code += f"'{template_info['class']}'{comma}"
    
    js_code += """];
                    
                    const hasTemplateClass = templateClasses.some(cls => 
                        node.classList && node.classList.contains(cls)
                    );
                    
                    if (hasTemplateClass && !node.hasAttribute('data-resize-applied')) {
                        setTimeout(() => {
                            applyElementFeatures(node);
                            node.setAttribute('data-resize-applied', 'true');
                            console.log('🆕 Handles aplicados automaticamente a novo elemento');
                        }, 100);
                    }
                    
                    // Verificar elementos filhos também
                    templateClasses.forEach(cls => {
                        const childElements = node.querySelectorAll && node.querySelectorAll(`.${cls}`);
                        if (childElements) {
                            childElements.forEach(child => {
                                if (!child.hasAttribute('data-resize-applied')) {
                                    setTimeout(() => {
                                        applyElementFeatures(child);
                                        child.setAttribute('data-resize-applied', 'true');
                                        console.log('🆕 Handles aplicados automaticamente a elemento filho');
                                    }, 100);
                                }
                            });
                        }
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('✅ Observador automático configurado!');
}

// Função para inicializar sistema completo
function initializeCompleteResizeSystem() {
    console.log('🚀 Inicializando sistema completo de redimensionamento...');
    
    // Corrigir erros primeiro
    fixPreventDefaultErrors();
    
    // Aplicar handles a elementos existentes
    const appliedCount = applyResizeHandlesToAllTemplates();
    
    // Configurar observador para novos elementos
    setupAutomaticHandleApplication();
    
    // Aplicar novamente após um delay para garantir
    setTimeout(() => {
        const additionalCount = applyResizeHandlesToAllTemplates();
        console.log(`🔄 Aplicação adicional: ${additionalCount} elementos processados`);
    }, 1000);
    
    console.log(`🎉 Sistema completo inicializado! ${appliedCount} elementos processados inicialmente`);
}

// Auto-executar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCompleteResizeSystem);
} else {
    initializeCompleteResizeSystem();
}

// Exportar funções para uso manual
window.applyResizeHandlesToAllTemplates = applyResizeHandlesToAllTemplates;
window.applyHandlesToSpecificClass = applyHandlesToSpecificClass;
window.initializeCompleteResizeSystem = initializeCompleteResizeSystem;
"""
    
    return js_code

def aplicar_sistema_ao_editor():
    """Aplica o sistema de redimensionamento ao arquivo do editor"""
    
    editor_path = "templates/legal_design_pro_v2/editor.html"
    
    if not os.path.exists(editor_path):
        print(f"❌ Arquivo não encontrado: {editor_path}")
        return False
    
    # Ler arquivo atual
    with open(editor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Gerar código JavaScript
    js_code = gerar_codigo_aplicacao_handles()
    
    # Localizar onde inserir o código (antes do fechamento do script)
    script_end_pattern = r'(</script>\s*</body>)'
    
    if re.search(script_end_pattern, content):
        # Inserir código antes do fechamento do script
        new_content = re.sub(
            script_end_pattern,
            f'\n{js_code}\n\\1',
            content
        )
        
        # Salvar arquivo atualizado
        with open(editor_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Sistema de redimensionamento aplicado ao editor!")
        return True
    else:
        print("❌ Não foi possível localizar onde inserir o código no editor")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando aplicação do sistema de redimensionamento...")
    
    # Mapear templates
    templates = mapear_templates_editor()
    print(f"📋 Mapeados {len(templates)} tipos de templates:")
    for key, info in templates.items():
        print(f"  - {info['name']} (.{info['class']})")
    
    # Aplicar sistema ao editor
    if aplicar_sistema_ao_editor():
        print("\n🎉 Sistema completo aplicado com sucesso!")
        print("\nFuncionalidades implementadas:")
        print("✅ Redimensionamento com 8 handles para todos os templates")
        print("✅ Aplicação automática em elementos existentes")
        print("✅ Observador para novos elementos inseridos")
        print("✅ Correção de erros preventDefault")
        print("✅ Sistema de debug e logs detalhados")
    else:
        print("\n❌ Falha na aplicação do sistema")

if __name__ == "__main__":
    main()