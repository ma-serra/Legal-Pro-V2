#!/usr/bin/env python3
"""
Script de Revisão de Categorização de Agentes Jurídicos

Este script analisa todos os agentes ativos e detecta inconsistências entre:
- O nome/descrição do agente (área esperada)
- O prompt do sistema (área declarada no prompt)

Criado em: Novembro 2025
Autor: Sistema Legal Pro
"""

import psycopg2
import os
from datetime import datetime


def detectar_area_nome(nome, descricao):
    """Detecta a área jurídica pelo nome e descrição do agente"""
    texto = f"{nome} {descricao}".lower() if descricao else nome.lower()
    
    areas = {
        'Tributário': ['tributário', 'tribut', 'icms', 'iss', 'iptu', 'ipva', 'irpj', 'irpf', 'fiscal'],
        'Eleitoral': ['eleitoral', 'eleição', 'eleitor', 'campanha', 'tse', 'tre'],
        'Penal': ['penal', 'criminal', 'crime', 'homicídio'],
        'Trabalhista': ['trabalh', 'clt', 'emprego', 'rescisão'],
        'Civil': ['civil', 'contrato', 'obrigação'],
        'Previdenciário': ['previdenc', 'inss', 'aposentadoria'],
        'Consumidor': ['consumidor', 'cdc', 'procon'],
        'Ambiental': ['ambiental', 'meio ambiente'],
        'Administrativo': ['administrativo', 'admin'],
        'Constitucional': ['constitucional'],
        'Empresarial': ['empresarial', 'societário', 'sociedade'],
        'Agrário': ['agrário', 'rural', 'agrícola'],
        'Família': ['família', 'divórcio', 'alimentos'],
        'Processual': ['processual', 'processo'],
        'Internacional': ['internacional'],
        'Saúde': ['saúde', 'médico', 'hospitalar'],
        'Tecnologia': ['tecnologia', 'digital', 'lgpd'],
        'Imobiliário': ['imobiliário', 'imóvel'],
        'Bancário': ['bancário', 'banco', 'financeiro'],
        'Securitário': ['securitário', 'seguro', 'apólice']
    }
    
    for area, keywords in areas.items():
        if any(kw in texto for kw in keywords):
            return area
    
    return None


def detectar_area_prompt(prompt):
    """Detecta a área jurídica declarada no prompt do sistema"""
    if not prompt:
        return None
    
    # Analisa apenas os primeiros 500 caracteres do prompt
    prompt_lower = prompt.lower()[:500]
    
    # Procurar por menções explícitas de área
    if 'direito tributário' in prompt_lower or 'tribut' in prompt_lower:
        return 'Tributário'
    elif 'direito eleitoral' in prompt_lower or 'eleitoral' in prompt_lower:
        return 'Eleitoral'
    elif 'direito penal' in prompt_lower or 'criminal' in prompt_lower:
        return 'Penal'
    elif 'direito do trabalho' in prompt_lower or 'trabalh' in prompt_lower:
        return 'Trabalhista'
    elif 'direito civil' in prompt_lower:
        return 'Civil'
    elif 'direito previdenciário' in prompt_lower or 'previdenc' in prompt_lower:
        return 'Previdenciário'
    elif 'direito do consumidor' in prompt_lower or 'consumidor' in prompt_lower:
        return 'Consumidor'
    elif 'direito ambiental' in prompt_lower or 'ambiental' in prompt_lower:
        return 'Ambiental'
    elif 'direito empresarial' in prompt_lower or 'societário' in prompt_lower:
        return 'Empresarial'
    elif 'direito administrativo' in prompt_lower or 'licitações' in prompt_lower:
        return 'Administrativo'
    
    return None


def main():
    """Função principal do script"""
    print("="*80)
    print("🔍 SCRIPT DE REVISÃO - CATEGORIZAÇÃO DE AGENTES JURÍDICOS")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Conectar ao banco
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return
    
    # Buscar todos os agentes ativos
    cur.execute("""
        SELECT id, nome, descricao, template_prompt 
        FROM agente_juridico 
        WHERE ativo = true
        ORDER BY id
    """)
    
    agentes = cur.fetchall()
    
    print(f"📊 Analisando {len(agentes)} agentes ativos...\n")
    
    erros_encontrados = []
    
    # Analisar cada agente
    for agente_id, nome, descricao, prompt in agentes:
        area_nome = detectar_area_nome(nome, descricao)
        area_prompt = detectar_area_prompt(prompt)
        
        # Verificar inconsistência
        if area_nome and area_prompt and area_nome != area_prompt:
            erros_encontrados.append({
                'id': agente_id,
                'nome': nome,
                'area_esperada': area_nome,
                'area_prompt': area_prompt,
                'tipo': 'INCONSISTÊNCIA'
            })
    
    # Exibir resultados
    print("="*80)
    print("❌ ERROS ENCONTRADOS:")
    print("="*80)
    
    if erros_encontrados:
        for erro in erros_encontrados:
            print(f"\n🚨 ID {erro['id']}: {erro['nome']}")
            print(f"   📌 Área pelo Nome: {erro['area_esperada']}")
            print(f"   ⚠️  Área no Prompt: {erro['area_prompt']}")
            print(f"   🔧 Ação: Verificar se categorização está correta")
    else:
        print("\n✅ Nenhuma inconsistência encontrada!")
    
    print("\n" + "="*80)
    print(f"📊 TOTAL DE ERROS: {len(erros_encontrados)}")
    print("="*80)
    
    # Salvar relatório
    relatorio_path = '/tmp/relatorio_agentes_categorizacao.txt'
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE REVISÃO - CATEGORIZAÇÃO DE AGENTES JURÍDICOS\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        if erros_encontrados:
            f.write("ERROS ENCONTRADOS:\n\n")
            for erro in erros_encontrados:
                f.write(f"ID {erro['id']}: {erro['nome']}\n")
                f.write(f"  Área pelo Nome: {erro['area_esperada']}\n")
                f.write(f"  Área no Prompt: {erro['area_prompt']}\n")
                f.write(f"  Status: {erro['tipo']}\n\n")
        else:
            f.write("✅ Nenhum erro encontrado!\n")
    
    print(f"\n💾 Relatório salvo em: {relatorio_path}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
