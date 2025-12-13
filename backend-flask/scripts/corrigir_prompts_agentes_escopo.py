"""
Script para corrigir prompts dos agentes adicionando regras de escopo
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def conectar_db():
    """Conecta ao banco de dados"""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def adicionar_regra_escopo_prompt(prompt_original, area_nome, especialidades):
    """Adiciona regra de escopo ao prompt"""
    
    # Texto da regra de escopo
    regra_escopo = f"""
REGRA FUNDAMENTAL DE ESCOPO:
============================================
VOCÊ TRABALHA EXCLUSIVAMENTE COM: {area_nome}

- Se a questão NÃO for sobre {area_nome}, você DEVE responder:
  "Desculpe, minha especialização é exclusivamente em {area_nome}. Para questões de [área mencionada], 
  recomendo consultar um especialista na área específica."

- NUNCA tente responder questões de Direito Penal, Direito Civil, Direito Trabalhista ou qualquer 
  outra área que não seja {area_nome}.

- Se houver dúvida sobre se a questão está no seu escopo, pergunte ao usuário para esclarecer.

SUAS ESPECIALIDADES ESPECÍFICAS EM {area_nome}:
{especialidades}
============================================

"""
    
    # Inserir a regra logo após a linha de ESPECIALIDADE
    if 'ESPECIALIDADE:' in prompt_original:
        partes = prompt_original.split('PERFIL:', 1)
        if len(partes) == 2:
            return partes[0] + regra_escopo + '\nPERFIL:' + partes[1]
    
    # Se não encontrar o padrão esperado, adicionar no início
    return regra_escopo + '\n' + prompt_original

def identificar_area_juridica(nome, classe, especialidades):
    """Identifica a área jurídica baseada no nome e especialidades"""
    
    mapeamento_areas = {
        'Tributário': ['tribut', 'fiscal', 'icms', 'iss', 'ipi', 'pis', 'cofins', 'irpj', 'csll'],
        'Trabalhista': ['trabalh', 'rescis', 'assédio', 'terceiriz', 'férias', 'fgts', 'insalub', 'periculo'],
        'Civil': ['civil', 'contrat', 'responsabilid', 'família', 'sucessão', 'propriedad'],
        'Penal': ['penal', 'criminal', 'homicídio', 'furto', 'roubo', 'feminicídio'],
        'Empresarial': ['empresarial', 'societário', 'recuperação judicial', 'falência'],
        'Consumidor': ['consumidor', 'cdc', 'produto', 'serviço'],
        'Ambiental': ['ambiental', 'meio ambiente', 'poluição'],
        'Bancário': ['bancário', 'financiamento', 'corporate banking', 'investment'],
        'Securitário': ['securitário', 'seguro', 'sinistro', 'susep'],
        'Previdenciário': ['previdenciário', 'aposentadoria', 'benefício', 'inss']
    }
    
    texto_busca = (nome + ' ' + classe + ' ' + str(especialidades)).lower()
    
    for area, palavras_chave in mapeamento_areas.items():
        if any(palavra in texto_busca for palavra in palavras_chave):
            return f'Direito {area}'
    
    return 'Direito Geral'

def atualizar_prompts_agentes():
    """Atualiza todos os prompts dos agentes com regras de escopo"""
    
    conn = conectar_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Buscar todos os agentes
        cursor.execute("""
            SELECT id, nome, classe, template_prompt, capacidades
            FROM agente_juridico
            WHERE template_prompt IS NOT NULL
        """)
        
        agentes = cursor.fetchall()
        print(f"\n✅ Encontrados {len(agentes)} agentes para atualizar\n")
        
        atualizados = 0
        erros = 0
        
        for agente in agentes:
            try:
                # Extrair especialidades
                if agente['capacidades'] and isinstance(agente['capacidades'], dict):
                    especialidades_list = agente['capacidades'].get('especializacoes', [])
                else:
                    # Tentar extrair do prompt existente
                    if 'ESPECIALIDADE:' in agente['template_prompt']:
                        import re
                        match = re.search(r"ESPECIALIDADE:\s*(\[.*?\])", agente['template_prompt'])
                        if match:
                            especialidades_list = eval(match.group(1))
                        else:
                            especialidades_list = []
                    else:
                        especialidades_list = []
                
                # Identificar área jurídica
                area = identificar_area_juridica(
                    agente['nome'], 
                    agente['classe'],
                    str(especialidades_list)
                )
                
                # Formatar especialidades
                esp_texto = '\n  - '.join(especialidades_list) if especialidades_list else 'Análise jurídica geral'
                
                # Verificar se já tem regra de escopo
                if 'REGRA FUNDAMENTAL DE ESCOPO' in agente['template_prompt']:
                    print(f"⏭️  Agente {agente['id']}: {agente['nome'][:50]} - JÁ TEM REGRA DE ESCOPO")
                    continue
                
                # Adicionar regra de escopo
                novo_prompt = adicionar_regra_escopo_prompt(
                    agente['template_prompt'],
                    area,
                    '  - ' + esp_texto
                )
                
                # Atualizar no banco
                cursor.execute("""
                    UPDATE agente_juridico
                    SET template_prompt = %s,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (novo_prompt, agente['id']))
                
                atualizados += 1
                print(f"✅ Agente {agente['id']}: {agente['nome'][:50]} - {area}")
                
            except Exception as e:
                erros += 1
                print(f"❌ Erro no agente {agente['id']}: {str(e)}")
        
        # Commit das alterações
        conn.commit()
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMO DA ATUALIZAÇÃO:")
        print(f"{'='*70}")
        print(f"Total de agentes: {len(agentes)}")
        print(f"Atualizados: {atualizados}")
        print(f"Erros: {erros}")
        print(f"Já tinham regra: {len(agentes) - atualizados - erros}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro geral: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔧 CORREÇÃO DE PROMPTS DOS AGENTES - REGRAS DE ESCOPO")
    print("="*70 + "\n")
    
    atualizar_prompts_agentes()
    
    print("✅ Processo concluído!")
