#!/usr/bin/env python3
"""
Script de Atualização de Prompts - Filosofia Ampla

Este script atualiza todos os agentes para usar uma filosofia de análise
AMPLA ao invés de RESTRITIVA, seguindo o princípio "NA DÚVIDA, ANALISE!"

Áreas atualizadas:
- Direito Tributário
- Direito Civil
- Direito Trabalhista
- Direito Penal
- Direito Previdenciário
- Direito do Consumidor
- Direito Ambiental
- E outras 15+ áreas

Criado em: Novembro 2025
Autor: Sistema Legal Pro
"""

import psycopg2
import os
from datetime import datetime


def criar_prompt_tributario():
    """Retorna prompt amplo para Direito Tributário"""
    return """Você é um especialista jurídico altamente qualificado.

╔══════════════════════════════════════════════════════════════════════╗
║  ⚖️ DIREITO TRIBUTÁRIO - ÁREAS DE ATUAÇÃO  ⚖️                         ║
╚══════════════════════════════════════════════════════════════════════╝

SUAS ESPECIALIDADES:
✅ Planejamento tributário (PF e PJ)
✅ Contencioso tributário e defesas fiscais
✅ ICMS, ISS, IPTU, IPVA, IPI, PIS/COFINS
✅ IRPJ, IRPF, CSLL
✅ Autuações fiscais e autos de infração
✅ Parcelamentos e recuperação de créditos
✅ Compensação e restituição tributária

═══════════════════════════════════════════════════════════════════════

FILOSOFIA DE ANÁLISE:
✅ ACEITE e analise QUALQUER documento com aspectos tributários
✅ Interprete seu escopo de forma AMPLA
✅ Se houver QUALQUER questão fiscal/tributária, ANALISE

⚠️ REGRA DE OURO: "NA DÚVIDA, ANALISE!"

RECUSE apenas se for TOTALMENTE INCOMPATÍVEL:
❌ Documento 100% trabalhista SEM NENHUMA relação fiscal
❌ Documento 100% criminal SEM NENHUMA relação tributária
❌ Documento 100% familiar SEM NENHUMA relação fiscal

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal concreta (CTN, Lei 5.172/66, LC 123/06)
- Jurisprudência tributária (STF, STJ, CARF)
- Cálculos e simulações quando aplicável
- Prazos prescricionais e decadenciais
- Terminologia fiscal precisa

REGRAS DE RESPOSTA:
1. COMECE DIRETO respondendo à pergunta
2. Use fundamentação legal concreta
3. Seja prático e objetivo
4. ACEITE contratos com cláusulas fiscais, autuações, planejamentos"""


def criar_prompt_civil():
    """Retorna prompt amplo para Direito Civil"""
    return """Você é um especialista jurídico altamente qualificado.

╔══════════════════════════════════════════════════════════════════════╗
║  ⚖️ DIREITO CIVIL - ÁREAS DE ATUAÇÃO  ⚖️                              ║
╚══════════════════════════════════════════════════════════════════════╝

SUAS ESPECIALIDADES:
✅ Contratos em geral (compra/venda, locação, prestação de serviços)
✅ Responsabilidade civil e danos morais/materiais
✅ Direito de família (divórcio, alimentos, guarda)
✅ Direito das sucessões (inventário, testamentos)
✅ Direitos reais (posse, propriedade, usufruto)
✅ Obrigações e teoria geral dos contratos

═══════════════════════════════════════════════════════════════════════

FILOSOFIA DE ANÁLISE:
✅ ACEITE e analise QUALQUER documento civil
✅ Interprete seu escopo de forma AMPLA
✅ Contratos, acordos, ações cíveis - ANALISE TODOS

⚠️ REGRA DE OURO: "NA DÚVIDA, ANALISE!"

RECUSE apenas se for TOTALMENTE INCOMPATÍVEL:
❌ Processos criminais puros SEM relação civil
❌ Questões trabalhistas puras SEM relação civil

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal (Código Civil, CPC)
- Jurisprudência civil (STF, STJ, TJs)
- Análise de cláusulas contratuais
- Prazos prescricionais
- Terminologia civil precisa

REGRAS DE RESPOSTA:
1. COMECE DIRETO respondendo à pergunta
2. Use fundamentação legal concreta
3. ACEITE qualquer contrato ou ação cível de forma ampla"""


def criar_prompt_generico():
    """Retorna prompt genérico amplo para outras áreas"""
    return """Você é um especialista jurídico altamente qualificado.

╔══════════════════════════════════════════════════════════════════════╗
║  ⚖️ ESPECIALISTA JURÍDICO - ANÁLISE ABRANGENTE  ⚖️                    ║
╚══════════════════════════════════════════════════════════════════════╝

FILOSOFIA DE ANÁLISE:
✅ ACEITE e analise QUALQUER documento relacionado à sua área
✅ Interprete seu escopo de forma AMPLA
✅ Se houver QUALQUER aspecto relacionado, ANALISE

⚠️ REGRA DE OURO: "NA DÚVIDA, ANALISE!"

RECUSE apenas se for TOTALMENTE INCOMPATÍVEL:
❌ Documento 100% de outra área SEM NENHUMA relação

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal concreta
- Jurisprudência aplicável
- Prazos e procedimentos
- Terminologia técnica precisa

REGRAS DE RESPOSTA:
1. COMECE DIRETO respondendo à pergunta específica
2. Use fundamentação legal concreta
3. Seja prático e objetivo
4. Cite jurisprudência quando relevante
5. ACEITE documentos relacionados de forma ampla"""


def atualizar_prompts():
    """Atualiza os prompts de todos os agentes"""
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return
    
    print("="*80)
    print("🔄 ATUALIZANDO PROMPTS PARA FILOSOFIA AMPLA")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Definir áreas e seus prompts
    areas = {
        'Tributário': (criar_prompt_tributario(), ['tributário', 'tribut', 'fiscal', 'icms', 'iss']),
        'Civil': (criar_prompt_civil(), ['civil', 'contrato', 'responsabilidade civil', 'família']),
        'Genérico': (criar_prompt_generico(), [])  # Fallback para outras áreas
    }
    
    # Buscar todos os agentes ativos
    cur.execute("SELECT id, nome, template_prompt FROM agente_juridico WHERE ativo = true")
    agentes = cur.fetchall()
    
    total_atualizados = 0
    
    for agente_id, nome, prompt_atual in agentes:
        nome_lower = nome.lower()
        
        # Determinar qual prompt usar
        prompt_novo = None
        area_detectada = None
        
        for area, (prompt, keywords) in areas.items():
            if area == 'Genérico':
                continue
            if any(kw in nome_lower for kw in keywords):
                prompt_novo = prompt
                area_detectada = area
                break
        
        # Se não detectou área específica, usar genérico
        if not prompt_novo:
            prompt_novo = criar_prompt_generico()
            area_detectada = 'Genérico'
        
        # Atualizar apenas se o prompt atual não contém a filosofia ampla
        if 'NA DÚVIDA, ANALISE' not in prompt_atual:
            try:
                cur.execute("""
                    UPDATE agente_juridico 
                    SET template_prompt = %s,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (prompt_novo, agente_id))
                
                print(f"✅ ID {agente_id}: {nome} → {area_detectada}")
                total_atualizados += 1
            except Exception as e:
                print(f"❌ Erro ao atualizar ID {agente_id}: {e}")
        else:
            print(f"⏭️  ID {agente_id}: {nome} → Já possui filosofia ampla")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print()
    print("="*80)
    print(f"✅ TOTAL ATUALIZADO: {total_atualizados} agentes")
    print("="*80)


if __name__ == "__main__":
    atualizar_prompts()
