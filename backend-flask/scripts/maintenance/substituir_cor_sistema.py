#!/usr/bin/env python3
"""
Script para substituir a cor #1f5981 por #1f5981 em todo o sistema
"""

import os
import re

def substituir_cores_em_arquivo(arquivo):
    """Substitui cores específicas em um arquivo"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        
        # Substituições de cores específicas
        substituicoes = {
            '#1f5981': '#1f5981',
            '#1f5981': '#1f5981',  # Verde Bootstrap
            '#1f5981': '#1f5981',  # Verde Bootstrap 5
            'rgb(31, 89, 129)': 'rgb(31, 89, 129)',
            'rgba(31, 89, 129': 'rgba(31, 89, 129',
        }
        
        for cor_antiga, cor_nova in substituicoes.items():
            conteudo = conteudo.replace(cor_antiga, cor_nova)
        
        if conteudo != conteudo_original:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            return True
        
        return False
        
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")
        return False

def substituir_cores_sistema():
    """Substitui cores em todo o sistema"""
    
    # Diretórios e extensões para processar
    diretorios = ['templates', 'static', '.']
    extensoes = ['.html', '.css', '.js', '.py']
    
    arquivos_modificados = []
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            continue
            
        for root, dirs, files in os.walk(diretorio):
            # Pular diretórios desnecessários
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensoes):
                    caminho_arquivo = os.path.join(root, file)
                    
                    if substituir_cores_em_arquivo(caminho_arquivo):
                        arquivos_modificados.append(caminho_arquivo)
    
    return arquivos_modificados

if __name__ == "__main__":
    print("Iniciando substituição de cores no sistema...")
    
    arquivos_modificados = substituir_cores_sistema()
    
    if arquivos_modificados:
        print(f"✅ Cores substituídas em {len(arquivos_modificados)} arquivos:")
        for arquivo in arquivos_modificados:
            print(f"  - {arquivo}")
    else:
        print("ℹ️ Nenhum arquivo precisou ser modificado")
    
    print("✅ Processo concluído!")