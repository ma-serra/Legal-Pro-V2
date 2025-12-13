#!/usr/bin/env python3
"""
Ferramenta de Verificação de Contraste UX
Analisa arquivos HTML, CSS e templates para identificar problemas de contraste
que causam experiência de usuário negativa.
"""

import os
import re
import json
from pathlib import Path

class ContrastChecker:
    def __init__(self):
        self.problemas = []
        self.arquivos_analisados = 0
        
    def analisar_sistema(self):
        """Analisa todo o sistema em busca de problemas de contraste."""
        print("🔍 Iniciando verificação de contraste UX...")
        
        # Analisar templates HTML
        self.analisar_templates()
        
        # Analisar arquivos estáticos
        self.analisar_estaticos()
        
        # Gerar relatório
        self.gerar_relatorio()
        
    def analisar_templates(self):
        """Analisa templates HTML em busca de problemas."""
        templates_dir = Path("templates")
        if templates_dir.exists():
            for arquivo in templates_dir.rglob("*.html"):
                self.analisar_arquivo_html(arquivo)
                
    def analisar_estaticos(self):
        """Analisa arquivos estáticos (HTML, CSS)."""
        static_dir = Path("static")
        if static_dir.exists():
            for arquivo in static_dir.rglob("*.html"):
                self.analisar_arquivo_html(arquivo)
            for arquivo in static_dir.rglob("*.css"):
                self.analisar_arquivo_css(arquivo)
                
    def analisar_arquivo_html(self, caminho_arquivo):
        """Analisa um arquivo HTML específico."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                self.arquivos_analisados += 1
                
                # Verificar classes com possíveis problemas de contraste
                problemas_encontrados = []
                
                # Buscar por text-dark em fundos escuros
                if re.search(r'text-dark.*bg-dark|bg-dark.*text-dark', conteudo):
                    problemas_encontrados.append("text-dark + bg-dark detectado")
                
                # Buscar por cor preta explícita
                if re.search(r'color:\s*#000|color:\s*black', conteudo):
                    problemas_encontrados.append("Cor preta explícita detectada")
                    
                # Buscar por inputs sem cor definida
                if re.search(r'<input[^>]*class="[^"]*form-control[^"]*"', conteudo):
                    if not re.search(r'form-control-dark|color:', conteudo):
                        problemas_encontrados.append("Input sem cor definida")
                        
                # Buscar por selects sem cor definida
                if re.search(r'<select[^>]*class="[^"]*form-select[^"]*"', conteudo):
                    if not re.search(r'form-select-dark|color:', conteudo):
                        problemas_encontrados.append("Select sem cor definida")
                        
                # Buscar por labels sem cor definida
                if re.search(r'<label[^>]*class="[^"]*form-label[^"]*"', conteudo):
                    if not re.search(r'text-light|text-white|color:', conteudo):
                        problemas_encontrados.append("Label sem cor clara definida")
                
                if problemas_encontrados:
                    self.problemas.append({
                        'arquivo': str(caminho_arquivo),
                        'tipo': 'HTML',
                        'problemas': problemas_encontrados
                    })
                    
        except Exception as e:
            print(f"Erro ao analisar {caminho_arquivo}: {e}")
            
    def analisar_arquivo_css(self, caminho_arquivo):
        """Analisa um arquivo CSS específico."""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                self.arquivos_analisados += 1
                
                problemas_encontrados = []
                
                # Buscar por cor preta em elementos que podem ter fundo escuro
                if re.search(r'color:\s*#000|color:\s*black', conteudo):
                    problemas_encontrados.append("Cor preta detectada no CSS")
                    
                # Buscar por baixo contraste
                if re.search(r'color:\s*#333.*background.*#000|background.*#000.*color:\s*#333', conteudo):
                    problemas_encontrados.append("Baixo contraste detectado")
                
                if problemas_encontrados:
                    self.problemas.append({
                        'arquivo': str(caminho_arquivo),
                        'tipo': 'CSS',
                        'problemas': problemas_encontrados
                    })
                    
        except Exception as e:
            print(f"Erro ao analisar {caminho_arquivo}: {e}")
            
    def gerar_relatorio(self):
        """Gera relatório detalhado dos problemas encontrados."""
        print(f"\n📊 RELATÓRIO DE CONTRASTE UX")
        print(f"{'='*50}")
        print(f"Arquivos analisados: {self.arquivos_analisados}")
        print(f"Problemas encontrados: {len(self.problemas)}")
        print(f"{'='*50}")
        
        if not self.problemas:
            print("✅ Nenhum problema de contraste detectado!")
            return
            
        for problema in self.problemas:
            print(f"\n❌ Arquivo: {problema['arquivo']}")
            print(f"   Tipo: {problema['tipo']}")
            for p in problema['problemas']:
                print(f"   • {p}")
                
        # Salvar relatório em arquivo
        with open('relatorio_contraste_ux.json', 'w', encoding='utf-8') as f:
            json.dump(self.problemas, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Relatório salvo em: relatorio_contraste_ux.json")
        
        # Gerar sugestões de correção
        self.gerar_sugestoes_correcao()
        
    def gerar_sugestoes_correcao(self):
        """Gera sugestões específicas de correção."""
        print(f"\n🔧 SUGESTÕES DE CORREÇÃO:")
        print(f"{'='*50}")
        
        sugestoes = [
            "1. Substituir 'text-dark' por 'text-light' ou 'text-white' em fundos escuros",
            "2. Adicionar classes específicas para modo escuro: 'form-control-dark', 'form-select-dark'",
            "3. Definir cores explícitas em CSS: color: #ffffff !important;",
            "4. Usar variáveis CSS para contraste: var(--text-color), var(--input-text)",
            "5. Testar contraste mínimo de 4.5:1 para texto normal",
            "6. Aplicar cor branca (#ffffff) para labels em fundos escuros"
        ]
        
        for sugestao in sugestoes:
            print(f"   {sugestao}")

def main():
    """Função principal."""
    checker = ContrastChecker()
    checker.analisar_sistema()

if __name__ == "__main__":
    main()