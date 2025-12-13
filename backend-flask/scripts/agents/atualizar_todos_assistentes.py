#!/usr/bin/env python3
"""
Script para atualizar todos os assistentes com prompts técnicos profissionais
"""
import os
import re

def atualizar_prompts_tecnicos():
    """Atualiza prompts em todos os assistentes"""
    
    # Encontrar todos os arquivos de assistentes
    assistentes_paths = []
    
    # Buscar em modules/assistentes/
    for root, dirs, files in os.walk('modules/assistentes'):
        for file in files:
            if file.endswith('.py') and 'assistente_' in file:
                assistentes_paths.append(os.path.join(root, file))
    
    # Buscar em modules/assistentes_juridicos/
    for root, dirs, files in os.walk('modules/assistentes_juridicos'):
        for file in files:
            if file.endswith('.py') and ('assistente' in file or 'direito_' in file):
                assistentes_paths.append(os.path.join(root, file))
    
    print(f"Encontrados {len(assistentes_paths)} arquivos para atualizar:")
    for path in assistentes_paths:
        print(f"  - {path}")
    
    # Padrões de prompt antigos para substituir
    padroes_antigos = [
        r'(você é um|sou um|como|atendo|posso ajudar|olá)',  # Linguagem informal
        r'(didática|acessível|qualquer pessoa entenda)',     # Linguagem simplificada
        r'(fique à vontade|pode me contar)',                 # Linguagem casual
    ]
    
    # Substitutos técnicos
    substitutos = {
        'você é um advogado especialista': 'Especialista técnico',
        'Olá! Sou especialista': 'Especialização técnica',
        'pode me contar mais detalhes': 'detalhe a questão jurídica específica',
        'fique à vontade para perguntar': 'disponibilizo expertise adicional conforme necessário',
        'de forma didática': 'com rigor técnico',
        'qualquer pessoa entenda': 'profissionais do direito',
        'linguagem clara e acessível': 'terminologia jurídica precisa'
    }
    
    arquivos_atualizados = 0
    
    for path in assistentes_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                conteudo_original = f.read()
            
            conteudo_novo = conteudo_original
            modificado = False
            
            # Aplicar substituições
            for antigo, novo in substitutos.items():
                if antigo.lower() in conteudo_novo.lower():
                    # Substituição case-insensitive
                    conteudo_novo = re.sub(re.escape(antigo), novo, conteudo_novo, flags=re.IGNORECASE)
                    modificado = True
            
            # Se houve modificações, salvar
            if modificado:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(conteudo_novo)
                print(f"✅ Atualizado: {path}")
                arquivos_atualizados += 1
            else:
                print(f"⚪ Sem alterações: {path}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {path}: {e}")
    
    print(f"\n📊 Resumo: {arquivos_atualizados}/{len(assistentes_paths)} arquivos atualizados")

if __name__ == "__main__":
    atualizar_prompts_tecnicos()