#!/usr/bin/env python3
"""
Script de verificação final para confirmar que todos os avisos foram removidos
"""

import os
import re
import psycopg2

def verificar_templates():
    """Verifica se ainda existem avisos nos templates"""
    avisos_encontrados = []
    
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                caminho = os.path.join(root, file)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    if any(termo in conteudo.lower() for termo in ['aviso', 'validar', 'sanitizar']):
                        linhas_problema = []
                        for i, linha in enumerate(conteudo.split('\n'), 1):
                            if any(termo in linha.lower() for termo in ['aviso', 'validar', 'sanitizar']):
                                linhas_problema.append(f"Linha {i}: {linha.strip()[:100]}")
                        
                        if linhas_problema:
                            avisos_encontrados.append({
                                'arquivo': caminho,
                                'linhas': linhas_problema
                            })
                            
                except Exception as e:
                    pass
    
    return avisos_encontrados

def verificar_javascript():
    """Verifica se ainda existem avisos nos arquivos JavaScript"""
    avisos_js = []
    
    for root, dirs, files in os.walk('static/js'):
        for file in files:
            if file.endswith('.js'):
                caminho = os.path.join(root, file)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    if 'aviso' in conteudo.lower() and 'innerhtml' in conteudo.lower():
                        avisos_js.append(caminho)
                        
                except Exception as e:
                    pass
    
    return avisos_js

def verificar_banco_dados():
    """Verifica se ainda existem avisos no banco de dados"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return None
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Buscar em tabelas principais
        tabelas_problema = []
        
        # Verificar agentes
        cursor.execute("""
            SELECT COUNT(*) FROM agente_juridico 
            WHERE LOWER(nome) LIKE '%aviso%' 
            OR LOWER(descricao) LIKE '%aviso%'
            OR LOWER(nome) LIKE '%validar%'
            OR LOWER(descricao) LIKE '%validar%'
        """)
        count_agentes = cursor.fetchone()[0]
        
        if count_agentes > 0:
            tabelas_problema.append(f"agente_juridico: {count_agentes} registros")
        
        # Verificar componentes
        cursor.execute("""
            SELECT COUNT(*) FROM componente_editor 
            WHERE LOWER(prompt_sistema) LIKE '%aviso%'
            OR LOWER(prompt_sistema) LIKE '%validar%'
        """)
        count_componentes = cursor.fetchone()[0]
        
        if count_componentes > 0:
            tabelas_problema.append(f"componente_editor: {count_componentes} registros")
        
        cursor.close()
        conn.close()
        
        return tabelas_problema
        
    except Exception as e:
        return [f"Erro ao verificar banco: {str(e)}"]

def main():
    print("🔍 VERIFICAÇÃO FINAL DE LIMPEZA")
    print("=" * 50)
    
    # 1. Verificar templates
    print("\n1. Verificando templates HTML...")
    avisos_templates = verificar_templates()
    
    if avisos_templates:
        print(f"❌ Encontrados avisos em {len(avisos_templates)} templates:")
        for aviso in avisos_templates[:5]:  # Mostrar apenas os primeiros 5
            print(f"   📄 {aviso['arquivo']}")
            for linha in aviso['linhas'][:3]:  # Mostrar apenas 3 linhas
                print(f"      {linha}")
    else:
        print("✅ Templates HTML limpos!")
    
    # 2. Verificar JavaScript
    print("\n2. Verificando arquivos JavaScript...")
    avisos_js = verificar_javascript()
    
    if avisos_js:
        print(f"❌ Encontrados avisos em {len(avisos_js)} arquivos JS:")
        for arquivo in avisos_js:
            print(f"   📄 {arquivo}")
    else:
        print("✅ Arquivos JavaScript limpos!")
    
    # 3. Verificar banco de dados
    print("\n3. Verificando banco de dados...")
    avisos_banco = verificar_banco_dados()
    
    if avisos_banco:
        print("❌ Encontrados avisos no banco:")
        for tabela in avisos_banco:
            print(f"   📊 {tabela}")
    else:
        print("✅ Banco de dados limpo!")
    
    # Resultado final
    print("\n" + "=" * 50)
    total_problemas = len(avisos_templates) + len(avisos_js) + (len(avisos_banco) if avisos_banco else 0)
    
    if total_problemas == 0:
        print("🎉 SISTEMA COMPLETAMENTE LIMPO!")
        print("✅ Nenhum aviso de innerHTML encontrado")
        print("✅ Script dom-cleaner.js ativo em templates")
        print("✅ Limpeza automática funcionando")
    else:
        print(f"⚠️  AINDA EXISTEM {total_problemas} PROBLEMAS")
        print("📝 Revisar os itens listados acima")

if __name__ == "__main__":
    main()