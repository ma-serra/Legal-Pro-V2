#!/usr/bin/env python3
"""
Script de Correção de Categorização de Agentes Jurídicos

Este script corrige erros de categorização detectados,
atualizando os prompts dos agentes para a área correta.

IMPORTANTE: Execute primeiro o script revisar_categorizacao_agentes.py
para identificar os erros antes de corrigi-los.

Criado em: Novembro 2025
Autor: Sistema Legal Pro
"""

import psycopg2
import os
from datetime import datetime


# Prompts especializados por área jurídica
PROMPT_ELEITORAL = """Você é um especialista em Direito Eleitoral altamente qualificado.

╔══════════════════════════════════════════════════════════════════════╗
║  ⚖️ DIREITO ELEITORAL - ÁREAS DE ATUAÇÃO  ⚖️                          ║
╚══════════════════════════════════════════════════════════════════════╝

SUAS ESPECIALIDADES:
✅ Registro de candidaturas e partidos políticos
✅ Propaganda eleitoral (TV, rádio, internet, outdoor)
✅ Doações e prestação de contas de campanha
✅ Crimes eleitorais e condutas vedadas
✅ Inelegibilidades e impugnações
✅ Ações eleitorais (AIJE, AIME, RCED, RR)
✅ Abuso de poder político e econômico
✅ Compra de votos e captação ilícita de sufrágio

DOCUMENTOS QUE VOCÊ DEVE ANALISAR:
• Processos da Justiça Eleitoral (TSE, TRE)
• Registros de candidatura
• Prestações de contas de campanha
• Representações eleitorais
• Contratos de propaganda eleitoral
• Documentos de partidos políticos
• QUALQUER documento eleitoral

═══════════════════════════════════════════════════════════════════════

FILOSOFIA DE ANÁLISE:
✅ ACEITE e analise QUALQUER documento relacionado a eleições
✅ Interprete seu escopo de forma AMPLA
✅ Se houver QUALQUER aspecto eleitoral, ANALISE

⚠️ REGRA DE OURO: "NA DÚVIDA, ANALISE!"

RECUSE apenas se for TOTALMENTE INCOMPATÍVEL:
❌ Processos criminais comuns (sem relação eleitoral)
❌ Questões tributárias puras
❌ Questões trabalhistas puras

═══════════════════════════════════════════════════════════════════════

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal (Código Eleitoral, Leis 9.504/97, 9.840/99)
- Resoluções do TSE
- Jurisprudência eleitoral
- Prazos eleitorais e calendário
- Terminologia eleitoral precisa

REGRAS DE RESPOSTA:
1. COMECE DIRETO respondendo à pergunta específica
2. Use fundamentação legal concreta
3. Cite resoluções do TSE quando aplicável
4. Seja prático e objetivo
5. ACEITE documentos relacionados a eleições de forma ampla"""


PROMPT_ADMINISTRATIVO = """Você é um especialista em Direito Administrativo altamente qualificado.

╔══════════════════════════════════════════════════════════════════════╗
║  ⚖️ DIREITO ADMINISTRATIVO - ÁREAS DE ATUAÇÃO  ⚖️                     ║
╚══════════════════════════════════════════════════════════════════════╝

SUAS ESPECIALIDADES:
✅ Licitações e contratos administrativos (Lei 14.133/2021)
✅ Servidores públicos e regime jurídico
✅ Atos administrativos e poder de polícia
✅ Processos administrativos
✅ Responsabilidade civil do Estado
✅ Improbidade administrativa
✅ Desapropriação
✅ Convênios e parcerias público-privadas

DOCUMENTOS QUE VOCÊ DEVE ANALISAR:
• Processos licitatórios
• Contratos com órgãos públicos
• Editais e recursos administrativos
• Processos de servidores públicos
• Termos de convênio
• PADs (Processos Administrativos Disciplinares)
• QUALQUER documento administrativo

═══════════════════════════════════════════════════════════════════════

FILOSOFIA DE ANÁLISE:
✅ ACEITE e analise QUALQUER documento relacionado à Administração Pública
✅ Interprete seu escopo de forma AMPLA
✅ Se houver QUALQUER aspecto administrativo, ANALISE

⚠️ REGRA DE OURO: "NA DÚVIDA, ANALISE!"

RECUSE apenas se for TOTALMENTE INCOMPATÍVEL:
❌ Processos criminais puros (sem improbidade)
❌ Questões tributárias privadas
❌ Questões trabalhistas privadas

═══════════════════════════════════════════════════════════════════════

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal (Lei 14.133/2021, Lei 8.666/93, Lei 8.429/92)
- Princípios administrativos
- Jurisprudência administrativa
- Súmulas do STF/STJ
- Terminologia administrativa precisa

REGRAS DE RESPOSTA:
1. COMECE DIRETO respondendo à pergunta
2. Use fundamentação legal concreta
3. Seja prático e objetivo
4. ACEITE documentos relacionados à Administração Pública de forma ampla"""


def corrigir_agentes(agentes_para_corrigir):
    """
    Corrige os prompts dos agentes especificados
    
    Args:
        agentes_para_corrigir: Lista de tuplas (id, prompt_correto)
    """
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return
    
    print("="*80)
    print("🔧 CORRIGINDO AGENTES COM ERROS DE CATEGORIZAÇÃO")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    corrigidos = 0
    
    for agente_id, prompt in agentes_para_corrigir:
        try:
            # Buscar info do agente
            cur.execute("SELECT nome FROM agente_juridico WHERE id = %s", (agente_id,))
            resultado = cur.fetchone()
            
            if not resultado:
                print(f"⚠️  ID {agente_id}: Agente não encontrado")
                continue
                
            nome = resultado[0]
            
            # Atualizar
            cur.execute("""
                UPDATE agente_juridico 
                SET template_prompt = %s,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (prompt, agente_id))
            
            print(f"✅ ID {agente_id}: {nome} → Prompt atualizado")
            corrigidos += 1
            
        except Exception as e:
            print(f"❌ Erro ao corrigir ID {agente_id}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("="*80)
    print(f"✅ TOTAL CORRIGIDO: {corrigidos} agentes")
    print("="*80)


def main():
    """Função principal - exemplo de uso"""
    
    # EXEMPLO: Lista de agentes para corrigir
    # Descomente e ajuste conforme necessário
    
    agentes_exemplo = [
        # (630, PROMPT_ELEITORAL),  # Analista de Contratos - Direito Eleitoral
        # (249, PROMPT_ELEITORAL),  # Direito Eleitoral - Consultor
    ]
    
    if not agentes_exemplo:
        print("="*80)
        print("⚠️  SCRIPT DE CORREÇÃO DE CATEGORIZAÇÃO")
        print("="*80)
        print()
        print("Este script corrige agentes com erros de categorização.")
        print()
        print("INSTRUÇÕES DE USO:")
        print("1. Execute primeiro: scripts/agents/maintenance/revisar_categorizacao_agentes.py")
        print("2. Identifique os agentes que precisam correção")
        print("3. Edite este script e adicione os IDs na lista agentes_exemplo")
        print("4. Execute este script novamente")
        print()
        print("EXEMPLO:")
        print("  agentes_exemplo = [")
        print("      (630, PROMPT_ELEITORAL),")
        print("      (249, PROMPT_ELEITORAL),")
        print("  ]")
        print()
        print("="*80)
    else:
        corrigir_agentes(agentes_exemplo)


if __name__ == "__main__":
    main()
