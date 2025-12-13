#!/usr/bin/env python3
"""
Script para extrair e listar todos os 329 especialistas jurídicos
do sistema Legal Design Pro V2 organizados por área
"""

import psycopg2
import os
import json
from collections import defaultdict

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def extrair_especialistas():
    """Extrai todos os especialistas do banco de dados"""
    conn = conectar_banco()
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    query = """
    SELECT 
        id,
        nome,
        COALESCE(area_juridica, 'Não Classificado') as area,
        classe,
        descricao,
        nivel_especializacao,
        capacidades::text as capacidades_json,
        ativo
    FROM agente_juridico 
    WHERE ativo = true 
    ORDER BY area_juridica, nome;
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    especialistas = []
    for row in resultados:
        id_agente, nome, area, classe, descricao, nivel, capacidades_str, ativo = row
        
        # Parse das capacidades JSON
        try:
            capacidades = json.loads(capacidades_str) if capacidades_str else []
        except:
            capacidades = []
        
        especialistas.append({
            'id': id_agente,
            'nome': nome,
            'area': area,
            'classe': classe,
            'descricao': descricao,
            'nivel_especializacao': nivel,
            'capacidades': capacidades,
            'ativo': ativo
        })
    
    cursor.close()
    conn.close()
    
    return especialistas

def gerar_lista_formatada(especialistas):
    """Gera lista formatada organizada por área"""
    
    # Agrupar por área
    por_area = defaultdict(list)
    for esp in especialistas:
        por_area[esp['area']].append(esp)
    
    # Gerar relatório formatado
    relatorio = []
    relatorio.append("# LISTA COMPLETA DOS 329 ESPECIALISTAS JURÍDICOS")
    relatorio.append("## Sistema Legal Design Pro V2 - Multi-Agente IA")
    relatorio.append("")
    relatorio.append(f"**Total de Especialistas Ativos:** {len(especialistas)}")
    relatorio.append(f"**Áreas Jurídicas Cobertas:** {len(por_area)}")
    relatorio.append("")
    relatorio.append("---")
    relatorio.append("")
    
    # Estatísticas por área
    relatorio.append("## 📊 DISTRIBUIÇÃO POR ÁREA JURÍDICA")
    relatorio.append("")
    for area in sorted(por_area.keys()):
        relatorio.append(f"- **{area}**: {len(por_area[area])} especialistas")
    relatorio.append("")
    relatorio.append("---")
    relatorio.append("")
    
    # Lista detalhada por área
    for area in sorted(por_area.keys()):
        relatorio.append(f"## 🎯 {area.upper()}")
        relatorio.append(f"**{len(por_area[area])} Especialistas**")
        relatorio.append("")
        
        for i, esp in enumerate(por_area[area], 1):
            relatorio.append(f"### {i}. {esp['nome']}")
            relatorio.append(f"**ID:** {esp['id']}")
            relatorio.append(f"**Classe:** {esp['classe']}")
            relatorio.append(f"**Nível de Especialização:** {esp['nivel_especializacao']}/5")
            relatorio.append(f"**Descrição:** {esp['descricao']}")
            
            if esp['capacidades']:
                relatorio.append("**Capacidades Principais:**")
                for cap in esp['capacidades']:
                    relatorio.append(f"- {cap}")
            
            relatorio.append("")
            relatorio.append("---")
            relatorio.append("")
    
    # Resumo técnico
    relatorio.append("## 🔧 RESUMO TÉCNICO")
    relatorio.append("")
    relatorio.append("### Distribuição por Classe")
    classes = defaultdict(int)
    for esp in especialistas:
        classes[esp['classe']] += 1
    
    for classe, count in sorted(classes.items()):
        relatorio.append(f"- **{classe}**: {count} agentes")
    
    relatorio.append("")
    relatorio.append("### Distribuição por Nível de Especialização")
    niveis = defaultdict(int)
    for esp in especialistas:
        if esp['nivel_especializacao']:
            niveis[esp['nivel_especializacao']] += 1
    
    for nivel in sorted(niveis.keys()):
        relatorio.append(f"- **Nível {nivel}**: {niveis[nivel]} especialistas")
    
    relatorio.append("")
    relatorio.append("### Capacidades Mais Comuns")
    todas_capacidades = []
    for esp in especialistas:
        todas_capacidades.extend(esp['capacidades'])
    
    from collections import Counter
    cap_counter = Counter(todas_capacidades)
    
    relatorio.append("")
    for cap, count in cap_counter.most_common(15):
        relatorio.append(f"- **{cap}**: {count} especialistas")
    
    relatorio.append("")
    relatorio.append("---")
    relatorio.append("")
    relatorio.append("**Relatório gerado automaticamente pelo Sistema Legal Design Pro V2**")
    relatorio.append(f"**Data:** {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return "\n".join(relatorio)

def main():
    """Função principal"""
    print("🔍 EXTRAINDO ESPECIALISTAS JURÍDICOS...")
    print("=" * 50)
    
    especialistas = extrair_especialistas()
    
    if not especialistas:
        print("❌ Erro ao extrair especialistas")
        return
    
    print(f"✅ {len(especialistas)} especialistas extraídos")
    print("📝 Gerando relatório formatado...")
    
    relatorio = gerar_lista_formatada(especialistas)
    
    # Salvar arquivo
    nome_arquivo = "LISTA_COMPLETA_329_ESPECIALISTAS_JURIDICOS.md"
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(f"✅ Relatório salvo em: {nome_arquivo}")
    print("📊 Relatório contém:")
    print("   • Lista completa dos 329 especialistas")
    print("   • Organização por área jurídica")
    print("   • Capacidades e especializações detalhadas")
    print("   • Estatísticas e análises técnicas")
    print("")
    print("🎯 ESPECIALISTAS POR ÁREA:")
    
    # Preview rápido
    por_area = defaultdict(list)
    for esp in especialistas:
        por_area[esp['area']].append(esp)
    
    for area in sorted(por_area.keys()):
        print(f"   • {area}: {len(por_area[area])} especialistas")
    
    return nome_arquivo

if __name__ == "__main__":
    arquivo_gerado = main()
    print(f"\n🎉 RELATÓRIO COMPLETO DISPONÍVEL EM: {arquivo_gerado}")