#!/usr/bin/env python3
"""
Script para substituir todos os usos de confirm() por modais modernos no sistema
"""

import os
import re
import glob

def replace_confirm_calls(file_path):
    """Substitui chamadas confirm() por modernConfirm() em um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrões para substituir
        patterns = [
            # confirm('mensagem') simples
            (r"confirm\('([^']+)'\)", r"await modernConfirm('\1', 'Confirmar Ação')"),
            # confirm("mensagem") com aspas duplas
            (r'confirm\("([^"]+)"\)', r'await modernConfirm("\1", "Confirmar Ação")'),
            # if (confirm(...))
            (r"if\s*\(\s*confirm\('([^']+)'\)\s*\)", r"if (await modernConfirm('\1', 'Confirmar Ação'))"),
            (r'if\s*\(\s*confirm\("([^"]+)"\)\s*\)', r'if (await modernConfirm("\1", "Confirmar Ação"))'),
            # return confirm(...)
            (r"return\s+confirm\('([^']+)'\)", r"return await modernConfirm('\1', 'Confirmar Ação')"),
            (r'return\s+confirm\("([^"]+)"\)', r'return await modernConfirm("\1", "Confirmar Ação")'),
        ]
        
        changes_made = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                changes_made = True
        
        # Salvar se houve mudanças
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Atualizado: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def add_modal_functions_to_html(file_path):
    """Adiciona as funções do modal moderno a arquivos HTML que não têm"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se já tem as funções
        if 'modernConfirm(' in content:
            return False
        
        # Verifica se tem confirm() mas não tem modernConfirm
        if 'confirm(' not in content:
            return False
        
        modal_html = '''
    <!-- Modal moderno para confirmação -->
    <div id="modernConfirmModal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000; backdrop-filter: blur(4px);">
        <div class="modal-content" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 480px; width: 90%; animation: modalFadeIn 0.3s ease;">
            <div class="modal-header" style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; border-radius: 12px 12px 0 0; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 8px;">
                        <i class="bi bi-exclamation-triangle" style="font-size: 24px;"></i>
                    </div>
                    <h5 id="confirmModalTitle" style="margin: 0; font-weight: 600;">Confirmar Ação</h5>
                </div>
                <button type="button" class="btn-close" onclick="closeModernConfirm()" style="background: none; border: none; color: white; opacity: 0.8; font-size: 24px; cursor: pointer;">×</button>
            </div>
            <div class="modal-body" style="padding: 24px; text-align: center;">
                <div style="margin-bottom: 20px;">
                    <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #fff5f5, #fed7d7); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
                        <i class="bi bi-trash3" style="font-size: 28px; color: #dc3545;"></i>
                    </div>
                    <p id="confirmModalMessage" style="color: #374151; font-size: 16px; line-height: 1.5; margin: 0;">
                        Confirmar esta ação?
                    </p>
                </div>
            </div>
            <div class="modal-footer" style="padding: 16px 24px; background: #f8f9fa; border-radius: 0 0 12px 12px; display: flex; gap: 12px;">
                <button type="button" class="btn btn-light" onclick="closeModernConfirm()" style="flex: 1; padding: 12px; border: 1px solid #dee2e6; border-radius: 8px; font-weight: 500; background: white; cursor: pointer;">
                    Cancelar
                </button>
                <button type="button" class="btn btn-danger" onclick="confirmModernConfirm()" style="flex: 1; padding: 12px; border-radius: 8px; font-weight: 500; background: linear-gradient(135deg, #dc3545, #c82333); border: none; color: white; cursor: pointer;">
                    Confirmar
                </button>
            </div>
        </div>
    </div>

    <style>
        @keyframes modalFadeIn {
            from {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }
        }
    </style>

    <script>
        let modernConfirmResolve = null;

        function modernConfirm(message, title = 'Confirmar Ação') {
            return new Promise((resolve) => {
                modernConfirmResolve = resolve;
                
                document.getElementById('confirmModalTitle').textContent = title;
                document.getElementById('confirmModalMessage').textContent = message;
                document.getElementById('modernConfirmModal').style.display = 'block';
            });
        }

        function closeModernConfirm() {
            document.getElementById('modernConfirmModal').style.display = 'none';
            if (modernConfirmResolve) {
                modernConfirmResolve(false);
                modernConfirmResolve = null;
            }
        }

        function confirmModernConfirm() {
            document.getElementById('modernConfirmModal').style.display = 'none';
            if (modernConfirmResolve) {
                modernConfirmResolve(true);
                modernConfirmResolve = null;
            }
        }
    </script>
'''
        
        # Insere antes do </body>
        if '</body>' in content:
            content = content.replace('</body>', modal_html + '</body>')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Modal adicionado a: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao adicionar modal a {file_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔄 Substituindo confirm() por modais modernos...")
    
    # Buscar arquivos HTML e JS
    file_patterns = [
        'templates/**/*.html',
        'static/**/*.js',
        '*.html',
        '*.js'
    ]
    
    files_updated = 0
    modals_added = 0
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Ignorar arquivos de cache e node_modules
            if any(ignore in file_path for ignore in ['.cache', 'node_modules', '.git']):
                continue
            
            # Adicionar modal a arquivos HTML
            if file_path.endswith('.html'):
                if add_modal_functions_to_html(file_path):
                    modals_added += 1
            
            # Substituir confirm() por modernConfirm()
            if replace_confirm_calls(file_path):
                files_updated += 1
    
    print(f"\n📊 Resumo:")
    print(f"   • {files_updated} arquivos atualizados")
    print(f"   • {modals_added} modais adicionados")
    print(f"✅ Substituição concluída!")

if __name__ == "__main__":
    main()