#!/usr/bin/env python3
"""
Script de Correção Automática de Contraste UX
Corrige automaticamente os problemas de contraste identificados no sistema.
"""

import os
import re
from pathlib import Path

class AutoContrastFixer:
    def __init__(self):
        self.arquivos_corrigidos = 0
        self.total_correcoes = 0
        
    def corrigir_sistema(self):
        """Corrige automaticamente todos os problemas de contraste."""
        print("🔧 Iniciando correção automática de contraste...")
        
        # Criar CSS global para correções
        self.criar_css_contraste_global()
        
        # Corrigir templates HTML principais
        self.corrigir_templates_criticos()
        
        print(f"\n✅ Correção concluída!")
        print(f"📁 Arquivos corrigidos: {self.arquivos_corrigidos}")
        print(f"🔧 Total de correções: {self.total_correcoes}")
        
    def criar_css_contraste_global(self):
        """Cria arquivo CSS global para garantir contraste adequado."""
        css_content = """/* CSS Global para Correção de Contraste UX */

/* Variáveis de cores para modo escuro */
:root {
    --dark-bg: #1a1a1a;
    --dark-card: #2d2d30;
    --dark-input: #404040;
    --text-white: #ffffff;
    --text-light: #e1e1e1;
    --text-muted-light: #cccccc;
    --border-dark: #555;
}

/* Correção global para inputs em modo escuro */
.form-control, 
input[type="text"], 
input[type="email"], 
input[type="password"], 
input[type="search"], 
textarea {
    background-color: var(--dark-input) !important;
    color: var(--text-white) !important;
    border: 1px solid var(--border-dark) !important;
}

.form-control::placeholder,
input::placeholder,
textarea::placeholder {
    color: var(--text-muted-light) !important;
}

/* Correção global para selects */
.form-select,
select {
    background-color: var(--dark-input) !important;
    color: var(--text-white) !important;
    border: 1px solid var(--border-dark) !important;
}

.form-select option,
select option {
    background-color: var(--dark-input) !important;
    color: var(--text-white) !important;
}

/* Correção global para labels */
.form-label,
label {
    color: var(--text-white) !important;
    font-weight: 500;
}

/* Correção para texto secundário */
.text-muted,
.small {
    color: var(--text-muted-light) !important;
}

/* Correção para cards em modo escuro */
.card {
    background-color: var(--dark-card) !important;
    border: 1px solid var(--border-dark) !important;
}

.card-body {
    color: var(--text-light) !important;
}

/* Correção para tabelas */
.table-dark,
.table {
    color: var(--text-white) !important;
}

.table-dark th,
.table-dark td,
.table th,
.table td {
    color: var(--text-white) !important;
    border-color: var(--border-dark) !important;
}

/* Correção para modals */
.modal-content {
    background-color: var(--dark-card) !important;
    color: var(--text-white) !important;
}

.modal-header,
.modal-body,
.modal-footer {
    color: var(--text-white) !important;
}

/* Correção para botões */
.btn-outline-secondary {
    color: var(--text-white) !important;
    border-color: var(--border-dark) !important;
}

.btn-outline-secondary:hover {
    background-color: var(--dark-input) !important;
    color: var(--text-white) !important;
}

/* Força contraste para elementos problemáticos */
* {
    color: inherit !important;
}

body {
    background-color: var(--dark-bg) !important;
    color: var(--text-white) !important;
}

/* Correção específica para elementos com cor preta */
.text-dark {
    color: var(--text-white) !important;
}

/* Garantir legibilidade em todos os elementos de formulário */
.form-check-label {
    color: var(--text-white) !important;
}

.form-text {
    color: var(--text-muted-light) !important;
}
"""
        
        css_path = Path("static/css/contraste-global.css")
        css_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
            
        print(f"✅ CSS global criado: {css_path}")
        self.arquivos_corrigidos += 1
        self.total_correcoes += 20
        
    def corrigir_templates_criticos(self):
        """Corrige os templates mais críticos identificados."""
        templates_criticos = [
            "templates/layout.html",
            "templates/auth/login.html", 
            "templates/admin/usuarios.html",
            "templates/historico.html"
        ]
        
        for template in templates_criticos:
            if Path(template).exists():
                self.corrigir_template_html(template)
                
    def corrigir_template_html(self, caminho_template):
        """Corrige um template HTML específico."""
        try:
            with open(caminho_template, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            # Adicionar link para CSS de contraste se não existir
            if 'contraste-global.css' not in conteudo and '<head>' in conteudo:
                css_link = '\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/contraste-global.css\') }}">'
                conteudo = conteudo.replace('</head>', css_link + '\n</head>')
                self.total_correcoes += 1
                
            # Substituir classes problemáticas
            correcoes = [
                (r'class="([^"]*?)form-control([^"]*?)"', r'class="\1form-control form-control-dark\2"'),
                (r'class="([^"]*?)form-select([^"]*?)"', r'class="\1form-select form-select-dark\2"'),
                (r'class="([^"]*?)text-dark([^"]*?)"', r'class="\1text-light\2"'),
            ]
            
            for padrao, substituicao in correcoes:
                if re.search(padrao, conteudo):
                    conteudo = re.sub(padrao, substituicao, conteudo)
                    self.total_correcoes += 1
                    
            # Salvar arquivo corrigido
            with open(caminho_template, 'w', encoding='utf-8') as f:
                f.write(conteudo)
                
            print(f"✅ Template corrigido: {caminho_template}")
            self.arquivos_corrigidos += 1
            
        except Exception as e:
            print(f"❌ Erro ao corrigir {caminho_template}: {e}")

def main():
    """Função principal."""
    fixer = AutoContrastFixer()
    fixer.corrigir_sistema()

if __name__ == "__main__":
    main()