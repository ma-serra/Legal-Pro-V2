#!/usr/bin/env python3
"""
Script para remover todos os avisos "" 
dos templates HTML do sistema.
"""

import os
import re

def remover_avisos_innerHTML():
    """Remove avisos de innerHTML de todos os templates"""
    
    # Padrão para encontrar os avisos
    padrao_aviso = r''
    
    arquivos_modificados = []
    total_remocoes = 0
    
    # Buscar todos os arquivos HTML
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                caminho_arquivo = os.path.join(root, file)
                
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo_original = f.read()
                    
                    # Contar quantos avisos existem
                    avisos_encontrados = len(re.findall(padrao_aviso, conteudo_original))
                    
                    if avisos_encontrados > 0:
                        # Remover os avisos
                        conteudo_novo = re.sub(padrao_aviso, '', conteudo_original)
                        
                        # Salvar o arquivo modificado
                        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                            f.write(conteudo_novo)
                        
                        arquivos_modificados.append(caminho_arquivo)
                        total_remocoes += avisos_encontrados
                        
                        print(f"✅ {caminho_arquivo}: {avisos_encontrados} avisos removidos")
                
                except Exception as e:
                    print(f"❌ Erro ao processar {caminho_arquivo}: {str(e)}")
    
    print(f"\n📊 RESUMO:")
    print(f"Arquivos modificados: {len(arquivos_modificados)}")
    print(f"Total de avisos removidos: {total_remocoes}")
    
    if arquivos_modificados:
        print(f"\n📁 ARQUIVOS MODIFICADOS:")
        for arquivo in arquivos_modificados:
            print(f"  ✓ {arquivo}")
    
    return len(arquivos_modificados), total_remocoes

if __name__ == "__main__":
    print("🧹 REMOVENDO AVISOS DE innerHTML")
    print("=" * 50)
    
    arquivos, avisos = remover_avisos_innerHTML()
    
    print(f"\n✅ PROCESSO CONCLUÍDO!")
    print(f"   {arquivos} arquivos limpos")
    print(f"   {avisos} avisos removidos")