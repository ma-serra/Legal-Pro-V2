"""
Script para atualizar TODOS os agentes de TODAS as 22 áreas com regras de escopo
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Mapeamento das 22 áreas jurídicas
AREAS_JURIDICAS = {
    'Direito Penal': {
        'termos': ['penal', 'criminal', 'crime', 'homicídio', 'furto', 'roubo', 'feminicídio'],
        'tributos': ['crimes penais', 'processo penal', 'defesa criminal', 'penas', 'medidas cautelares'],
        'rejeitar': ['tributário', 'trabalhista', 'civil', 'consumidor', 'administrativo']
    },
    'Direito Tributário': {
        'termos': ['tributário', 'tribut', 'fiscal', 'icms', 'iss', 'iptu', 'irpj', 'pis', 'cofins'],
        'tributos': ['tributos', 'impostos', 'ICMS', 'ISS', 'IRPJ', 'PIS/COFINS', 'planejamento fiscal'],
        'rejeitar': ['penal', 'criminal', 'trabalhista', 'civil', 'consumidor']
    },
    'Direito Trabalhista': {
        'termos': ['trabalh', 'rescis', 'férias', 'fgts', 'clt', 'assédio', 'terceiriz'],
        'tributos': ['relações trabalhistas', 'rescisão', 'férias', 'FGTS', 'direitos do trabalhador'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'civil', 'consumidor']
    },
    'Direito Civil': {
        'termos': ['civil', 'contrat', 'responsabilid', 'obrigaç', 'propriedad'],
        'tributos': ['contratos', 'responsabilidade civil', 'obrigações', 'propriedade', 'posse'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito do Consumidor': {
        'termos': ['consumidor', 'cdc', 'produto', 'serviço', 'vício', 'defeito'],
        'tributos': ['relações de consumo', 'CDC', 'produtos e serviços', 'garantia'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Empresarial': {
        'termos': ['empresarial', 'societário', 'falência', 'recuperação'],
        'tributos': ['sociedades', 'contratos empresariais', 'recuperação judicial', 'falência'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista', 'consumidor']
    },
    'Direito Administrativo': {
        'termos': ['administrativo', 'licitação', 'contrato admin', 'servidor'],
        'tributos': ['atos administrativos', 'licitações', 'contratos públicos', 'servidores'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Constitucional': {
        'termos': ['constitucional', 'direitos fund', 'adi', 'adc'],
        'tributos': ['direitos fundamentais', 'controle de constitucionalidade', 'federalismo'],
        'rejeitar': ['penal', 'trabalhista', 'tributário']
    },
    'Direito Previdenciário': {
        'termos': ['previdenciário', 'aposentadoria', 'benefício', 'inss'],
        'tributos': ['aposentadorias', 'benefícios previdenciários', 'INSS', 'pensões'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Ambiental': {
        'termos': ['ambiental', 'meio ambiente', 'poluição', 'licença'],
        'tributos': ['licenciamento ambiental', 'crimes ambientais', 'recursos naturais'],
        'rejeitar': ['penal', 'tributário', 'trabalhista', 'civil']
    },
    'Direito de Família': {
        'termos': ['família', 'divórcio', 'pensão aliment', 'guarda'],
        'tributos': ['divórcio', 'guarda de filhos', 'pensão alimentícia', 'união estável'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Sucessório': {
        'termos': ['sucessório', 'sucessã', 'herança', 'inventário', 'testamento'],
        'tributos': ['inventário', 'partilha', 'testamento', 'herança', 'sucessão'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Imobiliário': {
        'termos': ['imobiliário', 'imóvel', 'locação', 'usucapião'],
        'tributos': ['contratos imobiliários', 'locação', 'compra e venda', 'usucapião'],
        'rejeitar': ['penal', 'criminal', 'tributário', 'trabalhista']
    },
    'Direito Digital': {
        'termos': ['digital', 'lgpd', 'dados', 'internet', 'cibernético'],
        'tributos': ['LGPD', 'proteção de dados', 'crimes digitais', 'contratos digitais'],
        'rejeitar': ['tributário', 'trabalhista']
    },
    'Direito Agrário': {
        'termos': ['agrário', 'rural', 'agricultura', 'terra'],
        'tributos': ['reforma agrária', 'contratos rurais', 'propriedade rural'],
        'rejeitar': ['penal', 'tributário', 'trabalhista']
    },
    'Direito Bancário': {
        'termos': ['bancário', 'financiamento', 'empréstimo', 'banco'],
        'tributos': ['contratos bancários', 'financiamentos', 'crédito'],
        'rejeitar': ['penal', 'criminal', 'trabalhista']
    },
    'Direito Securitário': {
        'termos': ['securitário', 'seguro', 'sinistro', 'susep'],
        'tributos': ['contratos de seguro', 'sinistros', 'regulação SUSEP'],
        'rejeitar': ['penal', 'criminal', 'trabalhista', 'tributário']
    }
}

def criar_prompt_com_escopo(area_nome, area_info):
    """Cria prompt com regras de escopo para área específica"""
    
    tributos_str = ', '.join(area_info['tributos'])
    rejeitar_str = ', '.join([f'Direito {r.title()}' for r in area_info['rejeitar']])
    
    prompt = f"""Você é um especialista EXCLUSIVAMENTE em {area_nome}.

╔══════════════════════════════════════════════════════════════════════╗
║  🚫 REGRA CRÍTICA DE ESCOPO - LEIA PRIMEIRO  🚫                       ║
╚══════════════════════════════════════════════════════════════════════╝

VOCÊ SÓ PODE RESPONDER SOBRE {area_nome.upper()}:
✅ Temas válidos: {tributos_str}

🚫 SE A PERGUNTA FOR SOBRE OUTRAS ÁREAS:
{rejeitar_str}

VOCÊ DEVE RESPONDER EXATAMENTE ISTO:
"Sou especialista exclusivamente em {area_nome}. Sua questão parece ser sobre [identificar a área]. 
Recomendo consultar um especialista em [área identificada]."

═══════════════════════════════════════════════════════════════════════

VALIDAÇÃO DE CONTEXTO:
Se você receber informações/documentos sobre processos, casos ou questões que NÃO sejam 
relacionados a {area_nome}, você DEVE:

1. IGNORAR completamente esse contexto
2. INFORMAR ao usuário: "Os documentos fornecidos não são sobre {area_nome}. 
   Forneça informações específicas da área."

NUNCA tente analisar processos ou questões de outras áreas mesmo que sejam fornecidos!

═══════════════════════════════════════════════════════════════════════

ESTRUTURA TÉCNICA OBRIGATÓRIA:
- Fundamentação legal específica com citação de dispositivos
- Análise doutrinária consolidada quando aplicável
- Entendimento jurisprudencial dominante/minoritário
- Considerações práticas processuais
- Terminologia jurídica precisa e atual

REGRAS DE RESPOSTA:
1. PROIBIDO usar frases como "Sua questão envolve...", "Vou examinar...", "Permita-me analisar..."
2. COMECE DIRETO respondendo à pergunta específica do usuário
3. Use fundamentação legal concreta (leis, artigos, jurisprudência)
4. Se faltar informação, pergunte ESPECIFICAMENTE o que precisa
5. Seja prático e objetivo - elimine formalidades desnecessárias

EXEMPLO DE RECUSA CORRETA:
Pergunta sobre outra área → "Sou especialista exclusivamente em {area_nome}. Sua questão é sobre 
[outra área]. Recomendo consultar um especialista em [área identificada]."
"""
    
    return prompt

def identificar_area_agente(nome, classe):
    """Identifica área jurídica do agente pelo nome e classe"""
    
    texto = (nome + ' ' + classe).lower()
    
    for area_nome, area_info in AREAS_JURIDICAS.items():
        for termo in area_info['termos']:
            if termo in texto:
                return area_nome, area_info
    
    # Padrão genérico se não identificar
    return 'Direito (área específica)', {
        'tributos': ['análise jurídica especializada'],
        'rejeitar': []
    }

def atualizar_todos_agentes():
    """Atualiza todos os agentes com regras de escopo"""
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Buscar todos os agentes
        cursor.execute("SELECT id, nome, classe, template_prompt FROM agente_juridico ORDER BY id")
        agentes = cursor.fetchall()
        
        print(f"\n✅ Encontrados {len(agentes)} agentes para atualizar\n")
        
        atualizados = 0
        por_area = {}
        
        for agente in agentes:
            try:
                # Identificar área
                area_nome, area_info = identificar_area_agente(agente['nome'], agente['classe'])
                
                # Criar novo prompt com escopo
                novo_prompt = criar_prompt_com_escopo(area_nome, area_info)
                
                # Atualizar no banco
                cursor.execute("""
                    UPDATE agente_juridico
                    SET template_prompt = %s,
                        data_atualizacao = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (novo_prompt, agente['id']))
                
                atualizados += 1
                por_area[area_nome] = por_area.get(area_nome, 0) + 1
                
                if atualizados % 50 == 0:
                    print(f"✅ {atualizados} agentes atualizados...")
                    
            except Exception as e:
                print(f"❌ Erro no agente {agente['id']}: {e}")
        
        conn.commit()
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMO DA ATUALIZAÇÃO:")
        print(f"{'='*70}")
        print(f"Total de agentes: {len(agentes)}")
        print(f"Atualizados com sucesso: {atualizados}")
        print(f"\n📈 Por área jurídica:")
        for area, qtd in sorted(por_area.items(), key=lambda x: -x[1]):
            print(f"  • {area}: {qtd} agentes")
        print(f"{'='*70}\n")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro geral: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔧 ATUALIZAÇÃO COMPLETA DE TODOS OS AGENTES - REGRAS DE ESCOPO")
    print("="*70 + "\n")
    
    atualizar_todos_agentes()
    
    print("✅ Processo concluído!")
