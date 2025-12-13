#!/usr/bin/env python3
"""
Script para atualizar agentes tributários com a nova base de legislação
Adiciona referência à collection legislacao_tributaria_brasileira
"""

import json

# Carregar configuração dos agentes
with open('agentes_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Base tributária
base_tributaria = "embeddings_direito_tributario"

# Atualizar agentes de Direito Tributário
agentes_atualizados = 0

for agente_id, agente in config.items():
    if agente.get('base') == base_tributaria:
        # Atualizar prompt para referenciar ambas as bases
        agente_nome = agente.get('nome', 'Desconhecido')
        agente_especialidade = agente.get('especialidade', '')
        
        # Adicionar referência à nova base no prompt
        prompt_field = 'prompt_sistema' if 'prompt_sistema' in agente else 'prompt'
        if 'legislacao_tributaria_brasileira' not in agente.get(prompt_field, ''):
            # Adicionar parágrafo sobre a base de legislação
            adicao_legislacao = """

## Base de Conhecimento Especializada
Você tem acesso à collection 'legislacao_tributaria_brasileira' no Qdrant com 74 documentos contendo:
- Constituição Federal de 1988 (Arts. 145-162 - Sistema Tributário Nacional)
- Código Tributário Nacional (CTN - Lei 5.172/1966) completo
- Lei Complementar 214/2025 - Regulamentação da Reforma Tributária (IBS, CBS, IS)
- Emenda Constitucional 132/2023 - Reforma Tributária
- Legislação sobre todos os tributos federais, estaduais e municipais
- Princípios constitucionais tributários
- Normas sobre obrigação tributária, crédito tributário, prescrição e decadência

Sempre cite artigos específicos da CF/88, CTN ou LC 214/2025 em suas análises técnicas."""
            
            agente[prompt_field] += adicao_legislacao
            agentes_atualizados += 1
            print(f"✓ Atualizado: {agente_nome} ({agente_especialidade})")

# Salvar configuração atualizada
with open('agentes_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"\n✅ Total de agentes atualizados: {agentes_atualizados}")
print(f"📚 Base de referência: legislacao_tributaria_brasileira (74 documentos)")
print(f"🔗 Collection no Qdrant: https://c21e6a5b-298d-483b-82f4-00aeff5edabe.us-east4-0.gcp.cloud.qdrant.io:6333")
