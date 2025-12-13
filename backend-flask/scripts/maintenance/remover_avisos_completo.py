#!/usr/bin/env python3
"""
Script completo para remover TODOS os avisos "" 
de qualquer arquivo no sistema (HTML, JS, Python, etc.)
"""

import os
import re

def remover_avisos_sistema_completo():
    """Remove avisos de innerHTML de todo o sistema"""
    
    # Padrões diferentes para encontrar os avisos
    padroes_aviso = [
        r'',
        r'',
        r'',
        r'',
        r'<!--  -->',
        r'/\*  \*/',
        r'# ',
        r'""',
        r"''"
    ]
    
    # Tipos de arquivo para processar
    extensoes_arquivo = ['.html', '.js', '.py', '.css', '.json', '.md']
    
    arquivos_modificados = []
    total_remocoes = 0
    
    # Buscar todos os arquivos relevantes
    for root, dirs, files in os.walk('.'):
        # Pular diretórios desnecessários
        if any(skip in root for skip in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensoes_arquivo):
                caminho_arquivo = os.path.join(root, file)
                
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo_original = f.read()
                    
                    conteudo_novo = conteudo_original
                    avisos_encontrados = 0
                    
                    # Aplicar todos os padrões
                    for padrao in padroes_aviso:
                        matches = len(re.findall(padrao, conteudo_novo))
                        if matches > 0:
                            conteudo_novo = re.sub(padrao, '', conteudo_novo)
                            avisos_encontrados += matches
                    
                    # Se houve modificações, salvar
                    if avisos_encontrados > 0:
                        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                            f.write(conteudo_novo)
                        
                        arquivos_modificados.append(caminho_arquivo)
                        total_remocoes += avisos_encontrados
                        
                        print(f"✅ {caminho_arquivo}: {avisos_encontrados} avisos removidos")
                
                except Exception as e:
                    print(f"❌ Erro ao processar {caminho_arquivo}: {str(e)}")
    
    print(f"\n📊 RESUMO COMPLETO:")
    print(f"Arquivos modificados: {len(arquivos_modificados)}")
    print(f"Total de avisos removidos: {total_remocoes}")
    
    return len(arquivos_modificados), total_remocoes

def buscar_avisos_restantes():
    """Busca por avisos restantes no sistema"""
    
    print("🔍 BUSCANDO AVISOS RESTANTES...")
    
    padroes_busca = [
        r'AVISO.*Validar',
        r'sanitizar.*dados',
        r'innerHTML.*sanitizar',
        r'Validar.*innerHTML'
    ]
    
    arquivos_com_avisos = []
    
    for root, dirs, files in os.walk('.'):
        if any(skip in root for skip in ['__pycache__', '.git', 'node_modules']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in ['.html', '.js', '.py', '.css']):
                caminho_arquivo = os.path.join(root, file)
                
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    for padrao in padroes_busca:
                        if re.search(padrao, conteudo, re.IGNORECASE):
                            arquivos_com_avisos.append(caminho_arquivo)
                            break
                
                except Exception:
                    pass
    
    if arquivos_com_avisos:
        print(f"\n⚠️  AVISOS AINDA ENCONTRADOS EM {len(arquivos_com_avisos)} ARQUIVOS:")
        for arquivo in arquivos_com_avisos:
            print(f"  ⚠️  {arquivo}")
    else:
        print("\n✅ NENHUM AVISO RESTANTE ENCONTRADO!")
    
    return arquivos_com_avisos

if __name__ == "__main__":
    print("🧹 LIMPEZA COMPLETA DO SISTEMA")
    print("=" * 50)
    
    # Remover avisos
    arquivos, avisos = remover_avisos_sistema_completo()
    
    print(f"\n✅ REMOÇÃO CONCLUÍDA!")
    print(f"   {arquivos} arquivos limpos")
    print(f"   {avisos} avisos removidos")
    
    # Buscar avisos restantes
    print("\n" + "=" * 50)
    restantes = buscar_avisos_restantes()
    
    if not restantes:
        print("\n🎉 SISTEMA COMPLETAMENTE LIMPO!")
    else:
        print(f"\n⚠️  AINDA EXISTEM {len(restantes)} ARQUIVOS COM AVISOS")