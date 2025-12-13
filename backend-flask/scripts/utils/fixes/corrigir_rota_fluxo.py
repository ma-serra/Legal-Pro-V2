#!/usr/bin/env python3
"""
Script para corrigir rotas de /fluxo/ para /fluxo conforme solicitado
Remove templates antigos e corrige referências incorretas
"""
import os
import re

def corrigir_rotas_fluxo():
    """Corrige todas as rotas /fluxo/ para /fluxo no sistema"""
    
    print("🔧 Iniciando correção de rotas /fluxo/ para /fluxo")
    
    # Arquivos a serem verificados
    arquivos_para_verificar = [
        'app.py',
        'templates/fluxos/listar.html',
        'templates/fluxos/editor.html', 
        'templates/fluxos/criar.html',
        'templates/fluxos/testar.html',
        'static/js/editor-simples.js',
        'static/js/fluxo-editor.js'
    ]
    
    correcoes_feitas = []
    
    for arquivo in arquivos_para_verificar:
        if os.path.exists(arquivo):
            print(f"📁 Verificando {arquivo}...")
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Procurar por /fluxo/ e substituir por /fluxo
            conteudo_original = conteudo
            
            # Padrões a serem corrigidos
            patterns = [
                (r'"/fluxo/"', '"/fluxo"'),
                (r"'/fluxo/'", "'/fluxo'"),
                (r'href="/fluxo/"', 'href="/fluxo"'),
                (r"href='/fluxo/'", "href='/fluxo'"),
                (r'@app\.route\(\s*["\']\/fluxo\/["\']', '@app.route("/fluxo"'),
                (r'url_for\(["\']fluxo\/["\']', 'url_for("fluxo"')
            ]
            
            for pattern, replacement in patterns:
                if re.search(pattern, conteudo):
                    conteudo = re.sub(pattern, replacement, conteudo)
                    correcoes_feitas.append(f"{arquivo}: {pattern} → {replacement}")
            
            # Salvar apenas se houve mudanças
            if conteudo != conteudo_original:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"✅ {arquivo} corrigido")
            else:
                print(f"✓ {arquivo} já estava correto")
    
    # Remover template antigo se existir
    template_antigo = 'templates/fluxo'
    if os.path.exists(template_antigo):
        try:
            if os.path.isdir(template_antigo):
                import shutil
                shutil.rmtree(template_antigo)
                print(f"🗑️  Diretório de template antigo removido: {template_antigo}")
                correcoes_feitas.append(f"Removido diretório: {template_antigo}")
            else:
                os.remove(template_antigo)
                print(f"🗑️  Arquivo de template antigo removido: {template_antigo}")
                correcoes_feitas.append(f"Removido arquivo: {template_antigo}")
        except Exception as e:
            print(f"❌ Erro ao remover {template_antigo}: {e}")
    
    # Verificar se existe alguma rota incorreta no app.py
    if os.path.exists('app.py'):
        with open('app.py', 'r', encoding='utf-8') as f:
            conteudo_app = f.read()
        
        # Procurar por rotas com /fluxo/ (singular com barra)
        rotas_incorretas = re.findall(r'@app\.route\(["\'][^"\']*fluxo\/[^"\']*["\']', conteudo_app)
        
        if rotas_incorretas:
            print("⚠️  Rotas incorretas encontradas em app.py:")
            for rota in rotas_incorretas:
                print(f"   {rota}")
        else:
            print("✅ Nenhuma rota incorreta encontrada em app.py")
    
    # Relatório final
    print("\n📊 RELATÓRIO DE CORREÇÕES:")
    print("=" * 50)
    
    if correcoes_feitas:
        print(f"✅ {len(correcoes_feitas)} correções realizadas:")
        for correcao in correcoes_feitas:
            print(f"   • {correcao}")
    else:
        print("✅ Nenhuma correção necessária - sistema já estava correto")
    
    print("\n🎯 VERIFICAÇÃO FINAL:")
    print("✓ Rota correta: /fluxo (sem barra final)")
    print("✓ Rota correta: /fluxos (plural para listagem)")
    print("✗ Rota incorreta: /fluxo/ (com barra final)")
    
    return len(correcoes_feitas) > 0

if __name__ == "__main__":
    corrigir_rotas_fluxo()