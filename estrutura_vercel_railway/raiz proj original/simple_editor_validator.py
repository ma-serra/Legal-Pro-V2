"""
Validador simplificado do Editor Legal Design Pro
Testa funcionalidades sem dependências circulares
"""

import os
import json
import requests
from datetime import datetime

def validate_editor_system():
    """Executa validação completa do sistema"""
    base_url = "http://localhost:5000"
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'summary': {},
        'errors': [],
        'fixes_applied': []
    }
    
    print("🔍 Validando Editor Legal Design Pro...")
    
    # Teste 1: Verificar se a página carrega
    try:
        response = requests.get(f"{base_url}/legal-design-pro/editor", timeout=10)
        page_loaded = response.status_code == 200
        has_editor = 'richEditor' in response.text if page_loaded else False
        has_icons_tab = 'icons-tab' in response.text if page_loaded else False
        
        results['tests']['page_load'] = {
            'status': 'PASS' if page_loaded and has_editor else 'FAIL',
            'page_loaded': page_loaded,
            'editor_present': has_editor,
            'icons_tab_present': has_icons_tab
        }
    except Exception as e:
        results['tests']['page_load'] = {'status': 'ERROR', 'error': str(e)}
    
    # Teste 2: Verificar API de ícones
    try:
        response = requests.get(f"{base_url}/api/icons/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results['tests']['icon_api'] = {
                'status': 'PASS',
                'total_icons': data.get('total_icons', 0),
                'total_packs': data.get('total_packs', 0)
            }
        else:
            results['tests']['icon_api'] = {'status': 'FAIL', 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        results['tests']['icon_api'] = {'status': 'ERROR', 'error': str(e)}
    
    # Teste 3: Verificar API de templates
    try:
        response = requests.get(f"{base_url}/legal-design-pro/api/templates-list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results['tests']['template_api'] = {
                'status': 'PASS' if data.get('success') else 'FAIL',
                'total_templates': data.get('total', 0)
            }
        else:
            results['tests']['template_api'] = {'status': 'FAIL', 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        results['tests']['template_api'] = {'status': 'ERROR', 'error': str(e)}
    
    # Teste 4: Verificar arquivos JavaScript
    js_files = [
        'static/js/icon-library.js',
        'static/js/legal-research.js'
    ]
    
    js_status = {}
    for js_file in js_files:
        js_status[js_file] = os.path.exists(js_file)
    
    results['tests']['javascript_files'] = {
        'status': 'PASS' if all(js_status.values()) else 'FAIL',
        'files': js_status
    }
    
    # Teste 5: Verificar ícones extraídos
    icon_dirs = ['static/icons/legal/pack1', 'static/icons/legal/pack2', 
                'static/icons/legal/pack3', 'static/icons/legal/pack4', 'static/icons/legal/pack5']
    
    icon_counts = {}
    total_icons = 0
    for icon_dir in icon_dirs:
        if os.path.exists(icon_dir):
            count = len([f for f in os.listdir(icon_dir) if f.endswith('.png')])
            icon_counts[icon_dir] = count
            total_icons += count
        else:
            icon_counts[icon_dir] = 0
    
    results['tests']['icon_extraction'] = {
        'status': 'PASS' if total_icons > 100 else 'FAIL',
        'total_icons': total_icons,
        'by_pack': icon_counts
    }
    
    # Gerar resumo
    passed = sum(1 for test in results['tests'].values() if test.get('status') == 'PASS')
    total = len(results['tests'])
    
    results['summary'] = {
        'total_tests': total,
        'passed': passed,
        'success_rate': (passed / total * 100) if total > 0 else 0,
        'overall_status': 'HEALTHY' if passed == total else 'NEEDS_FIXES'
    }
    
    return results

def fix_editor_issues():
    """Aplica correções automáticas nos problemas identificados"""
    fixes_applied = []
    
    # Correção 1: Garantir que Quill.js está carregado
    editor_html = 'templates/legal_design_pro/editor_profissional_completo.html'
    if os.path.exists(editor_html):
        with open(editor_html, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'cdn.quilljs.com' not in content:
            # Adicionar Quill.js se não estiver presente
            quill_cdn = '''
    <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.6/quill.min.js"></script>'''
            
            if '<head>' in content:
                content = content.replace('<head>', f'<head>{quill_cdn}')
                with open(editor_html, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes_applied.append("Adicionado Quill.js CDN ao editor")
    
    # Correção 2: Verificar se todas as abas do editor funcionam
    # (Esta correção seria aplicada via JavaScript, já implementada)
    
    return fixes_applied

def main():
    """Função principal"""
    print("🔧 Aplicando correções automáticas...")
    fixes = fix_editor_issues()
    
    print("🧪 Executando validação...")
    results = validate_editor_system()
    
    # Imprimir resultados
    print("\n" + "="*50)
    print("📋 RELATÓRIO DE VALIDAÇÃO DO EDITOR")
    print("="*50)
    
    print(f"\n📊 Status: {results['summary']['overall_status']}")
    print(f"✅ Taxa de Sucesso: {results['summary']['success_rate']:.1f}%")
    print(f"📈 Testes: {results['summary']['passed']}/{results['summary']['total_tests']}")
    
    print("\n🔍 Detalhes dos Testes:")
    for test_name, test_data in results['tests'].items():
        status = test_data.get('status', 'UNKNOWN')
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"  {icon} {test_name}: {status}")
        
        if test_data.get('error'):
            print(f"     Erro: {test_data['error']}")
    
    if fixes:
        print("\n🔧 Correções Aplicadas:")
        for fix in fixes:
            print(f"  ✓ {fix}")
    
    # Verificar problemas específicos e sugerir soluções
    print("\n💡 Diagnóstico:")
    
    template_api = results['tests'].get('template_api', {})
    if template_api.get('status') != 'PASS':
        print("  ❌ Templates não carregando - verificar API de templates")
    
    icon_api = results['tests'].get('icon_api', {})
    if icon_api.get('status') == 'PASS':
        print(f"  ✅ Biblioteca de ícones funcionando ({icon_api.get('total_icons', 0)} ícones)")
    
    js_files = results['tests'].get('javascript_files', {})
    if js_files.get('status') != 'PASS':
        print("  ❌ Arquivos JavaScript ausentes")
    
    # Salvar relatório
    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: validation_report.json")
    print("="*50)
    
    return results

if __name__ == "__main__":
    main()