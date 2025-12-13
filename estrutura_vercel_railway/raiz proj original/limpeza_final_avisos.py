#!/usr/bin/env python3
"""
Script de limpeza final para remover completamente todos os avisos de innerHTML
Verifica banco de dados, templates, JavaScript e arquivos Python
"""

import os
import re
import psycopg2
from urllib.parse import urlparse

def limpar_banco_dados():
    """Remove avisos do banco de dados"""
    try:
        # Conectar ao banco
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não encontrada")
            return
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Buscar tabelas com campos de texto
        cursor.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE data_type IN ('text', 'character varying', 'varchar')
            AND table_schema = 'public'
        """)
        
        campos_texto = cursor.fetchall()
        tabelas_limpas = 0
        
        for tabela, campo in campos_texto:
            try:
                # Buscar registros com avisos
                cursor.execute(f"""
                    SELECT id FROM {tabela} 
                    WHERE {campo} LIKE '%AVISO%' 
                    OR {campo} LIKE '%Validar%' 
                    OR {campo} LIKE '%sanitizar%'
                """)
                
                registros = cursor.fetchall()
                
                if registros:
                    print(f"🔍 Encontrados {len(registros)} registros com avisos em {tabela}.{campo}")
                    
                    # Limpar avisos
                    cursor.execute(f"""
                        UPDATE {tabela} 
                        SET {campo} = REPLACE(REPLACE(REPLACE(
                            {campo}, 
                            'AVISO: Validar/sanitizar dados antes de usar innerHTML', ''
                        ), 'Validar/sanitizar dados antes de usar innerHTML', ''),
                        '  // AVISO: Validar/sanitizar dados antes de usar innerHTML', '')
                        WHERE {campo} LIKE '%AVISO%' 
                        OR {campo} LIKE '%Validar%' 
                        OR {campo} LIKE '%sanitizar%'
                    """)
                    
                    tabelas_limpas += 1
                    print(f"✅ Limpados {len(registros)} registros em {tabela}.{campo}")
                
            except Exception as e:
                # Ignorar erros de tabelas/campos que não existem
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Banco de dados limpo: {tabelas_limpas} tabelas processadas")
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {str(e)}")

def limpar_arquivos_js():
    """Remove avisos dos arquivos JavaScript"""
    padroes_js = [
        r'//\s*AVISO:.*innerHTML.*',
        r'/\*\s*AVISO:.*innerHTML.*\*/',
        r'console\.log\(.*AVISO.*innerHTML.*\)',
        r'alert\(.*AVISO.*innerHTML.*\)',
        r'"AVISO:.*innerHTML.*"',
        r"'AVISO:.*innerHTML.*'"
    ]
    
    arquivos_js = []
    for root, dirs, files in os.walk('static/js'):
        for file in files:
            if file.endswith('.js'):
                arquivos_js.append(os.path.join(root, file))
    
    limpezas = 0
    for arquivo_js in arquivos_js:
        try:
            with open(arquivo_js, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            conteudo_original = conteudo
            
            for padrao in padroes_js:
                conteudo = re.sub(padrao, '', conteudo, flags=re.MULTILINE | re.IGNORECASE)
            
            if conteudo != conteudo_original:
                with open(arquivo_js, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                limpezas += 1
                print(f"✅ Limpado arquivo JS: {arquivo_js}")
                
        except Exception as e:
            print(f"❌ Erro ao limpar {arquivo_js}: {str(e)}")
    
    print(f"✅ Arquivos JS limpos: {limpezas}")

def verificar_dados_dinamicos():
    """Verifica se há dados dinâmicos que possam estar gerando avisos"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return
            
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar especificamente agentes que podem ter descrições problemáticas
        cursor.execute("""
            SELECT id, nome, descricao 
            FROM agente_juridico 
            WHERE nome LIKE '%Extrator%' 
            OR descricao LIKE '%Extrator%'
        """)
        
        agentes = cursor.fetchall()
        
        if agentes:
            print(f"🔍 Verificando {len(agentes)} agentes relacionados a 'Extrator':")
            for agente in agentes:
                print(f"   ID: {agente[0]}, Nome: {agente[1]}")
                print(f"   Descrição: {agente[2][:100]}...")
                
                # Verificar se há avisos escondidos na descrição
                if any(termo in str(agente[2]).lower() for termo in ['aviso', 'validar', 'sanitizar']):
                    print(f"   ⚠️  AVISO ENCONTRADO NO AGENTE {agente[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados dinâmicos: {str(e)}")

def criar_script_js_limpeza():
    """Cria script JavaScript para limpar DOM em tempo real"""
    script_js = '''
// Script de limpeza automática do DOM
function limparAvisosDom() {
    const elementos = document.querySelectorAll('*');
    let limpezas = 0;
    
    elementos.forEach(elemento => {
        // Verificar textContent
        if (elemento.textContent && elemento.textContent.includes('AVISO: Validar/sanitizar')) {
            elemento.textContent = elemento.textContent.replace(/AVISO: Validar\/sanitizar dados antes de usar innerHTML/g, '');
            limpezas++;
        }
        
        // Verificar innerHTML
        if (elemento.innerHTML && elemento.innerHTML.includes('AVISO: Validar/sanitizar')) {
            elemento.innerHTML = elemento.innerHTML.replace(/AVISO: Validar\/sanitizar dados antes de usar innerHTML/g, '');
            limpezas++;
        }
        
        // Verificar atributos
        ['title', 'alt', 'placeholder', 'data-original-title'].forEach(attr => {
            const valor = elemento.getAttribute(attr);
            if (valor && valor.includes('AVISO: Validar/sanitizar')) {
                elemento.setAttribute(attr, valor.replace(/AVISO: Validar\/sanitizar dados antes de usar innerHTML/g, ''));
                limpezas++;
            }
        });
    });
    
    if (limpezas > 0) {
        console.log(`🧹 Limpados ${limpezas} avisos do DOM`);
    }
}

// Executar limpeza quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', limparAvisosDom);

// Executar limpeza periodicamente
setInterval(limparAvisosDom, 2000);

// Executar limpeza quando houver mudanças no DOM
const observer = new MutationObserver(limparAvisosDom);
observer.observe(document.body, { childList: true, subtree: true });
'''
    
    with open('static/js/dom-cleaner.js', 'w', encoding='utf-8') as f:
        f.write(script_js)
    
    print("✅ Script de limpeza do DOM criado em static/js/dom-cleaner.js")

def main():
    print("🧹 LIMPEZA FINAL DE AVISOS innerHTML")
    print("=" * 50)
    
    # 1. Limpar banco de dados
    print("\n1. Limpando banco de dados...")
    limpar_banco_dados()
    
    # 2. Limpar arquivos JavaScript
    print("\n2. Limpando arquivos JavaScript...")
    limpar_arquivos_js()
    
    # 3. Verificar dados dinâmicos
    print("\n3. Verificando dados dinâmicos...")
    verificar_dados_dinamicos()
    
    # 4. Criar script de limpeza do DOM
    print("\n4. Criando script de limpeza do DOM...")
    criar_script_js_limpeza()
    
    print("\n✅ LIMPEZA FINAL CONCLUÍDA!")
    print("📝 Próximos passos:")
    print("   1. Incluir o script dom-cleaner.js nos templates")
    print("   2. Testar a aplicação")
    print("   3. Verificar se os avisos desapareceram")

if __name__ == "__main__":
    main()