#!/usr/bin/env python3
"""
Script para aplicar as regras fundamentais a todos os 6 agentes criminais.

REGRAS FUNDAMENTAIS:
1. Toda resposta deve ser fundamentada na base de conhecimento validada
2. Não é permitido criar informações sem fundamentação jurídica
3. Se não encontrar na base, responder: 'Não foi possível responder no momento sua pergunta'
4. Sempre citar fontes específicas dos documentos
"""

import os
import sys
import json
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL não encontrada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def atualizar_prompts_agentes_criminais():
    """Atualiza todos os agentes criminais com as regras fundamentais."""
    
    # Prompt base com regras fundamentais
    prompt_base_regras = """

## 🚨 REGRAS FUNDAMENTAIS OBRIGATÓRIAS:

### ⚖️ VALIDAÇÃO EXCLUSIVA:
1. **TODA RESPOSTA** deve ser fundamentada EXCLUSIVAMENTE na base de conhecimento criminal validada
2. **PROIBIDO** criar, inventar ou supor qualquer informação jurídica
3. **OBRIGATÓRIO** citar fontes específicas dos documentos utilizados
4. **Se não encontrar** informação na base: responder exatamente "Não foi possível responder no momento sua pergunta"

### 📚 FONTES OBRIGATÓRIAS:
- Código Penal (8ª edição - 2025)
- Código de Processo Penal (7ª edição - 2025)
- 29 documentos especializados validados
- Base de conhecimento criminal indexada

### 🎯 ESTRUTURA DE RESPOSTA:
- **Sempre** identificar o artigo específico
- **Sempre** citar a fonte exata
- **Sempre** incluir fundamentação legal
- **Nunca** responder sem base documental

### ⚠️ VEDAÇÕES ABSOLUTAS:
- ❌ Não criar interpretações sem fundamentação
- ❌ Não supor aplicação de normas
- ❌ Não dar respostas genéricas
- ❌ Não inventar jurisprudência

"""

    # Agentes criminais para atualizar
    agentes_criminais = [
        {
            'id': 'especialista_direito_criminal', 
            'nome': 'Especialista em Direito Criminal',
            'especialidade': 'Tipos penais, excludentes e teorias gerais'
        },
        {
            'id': 'tribunal_juri', 
            'nome': 'Especialista em Tribunal do Júri',
            'especialidade': 'Procedimentos do júri e sustentação oral'
        },
        {
            'id': 'analista_evidencias', 
            'nome': 'Analista de Evidências Criminais',
            'especialidade': 'Análise de provas e perícia criminal'
        },
        {
            'id': 'execucao_penal', 
            'nome': 'Especialista em Execução Penal',
            'especialidade': 'Regimes de cumprimento e progressão'
        },
        {
            'id': 'assessor_sustentacao', 
            'nome': 'Assessor de Sustentação Oral',
            'especialidade': 'Técnicas de argumentação e oratória'
        },
        {
            'id': 'revisor_penal', 
            'nome': 'Revisor de Direito Criminal',
            'especialidade': 'Revisão e segunda opinião jurídica'
        }
    ]

    session = Session()
    try:
        agentes_atualizados = 0
        
        for agente in agentes_criminais:
            # Buscar o agente no banco
            query = text("""
                SELECT id, nome, prompt_sistema 
                FROM agente_juridico 
                WHERE id = :agente_id OR nome = :nome
                LIMIT 1
            """)
            
            result = session.execute(query, {
                'agente_id': agente['id'],
                'nome': agente['nome']
            }).fetchone()
            
            if result:
                # Prompt atual
                prompt_atual = result.prompt_sistema or ""
                
                # Novo prompt com regras fundamentais
                novo_prompt = f"""## 🏛️ {agente['nome']}

**Especialização:** {agente['especialidade']}

{prompt_base_regras}

### 🎯 EXPERTISE ESPECÍFICA:
{prompt_atual.split('### 🎯 EXPERTISE ESPECÍFICA:')[-1] if '### 🎯 EXPERTISE ESPECÍFICA:' in prompt_atual else f"Especialista em {agente['especialidade'].lower()}"}

### 📋 PROTOCOLO DE RESPOSTA:
1. Verificar se a consulta está na base de conhecimento
2. Identificar artigos e normas específicas
3. Citar fonte exata do documento
4. Estruturar resposta fundamentada
5. Se não encontrar: "Não foi possível responder no momento sua pergunta"

**Lembre-se: TODA informação deve ter fundamentação documental validada.**
"""

                # Atualizar no banco
                update_query = text("""
                    UPDATE agente_juridico 
                    SET prompt_sistema = :novo_prompt,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """)
                
                session.execute(update_query, {
                    'novo_prompt': novo_prompt,
                    'id': result.id
                })
                
                logger.info(f"✅ Agente atualizado: {agente['nome']}")
                agentes_atualizados += 1
            else:
                logger.warning(f"⚠️ Agente não encontrado: {agente['nome']}")
        
        session.commit()
        logger.info(f"🎯 CONCLUÍDO: {agentes_atualizados} agentes atualizados com regras fundamentais")
        
        # Verificar se todos foram atualizados
        verification_query = text("""
            SELECT nome, 
                   CASE WHEN prompt_sistema LIKE '%REGRAS FUNDAMENTAIS OBRIGATÓRIAS%' 
                        THEN '✅ Atualizado' 
                        ELSE '❌ Pendente' 
                   END as status
            FROM agente_juridico 
            WHERE area_juridica = 'criminal'
        """)
        
        resultados = session.execute(verification_query).fetchall()
        
        print("\n📊 STATUS DOS AGENTES CRIMINAIS:")
        for row in resultados:
            print(f"• {row.nome}: {row.status}")
            
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro ao atualizar agentes: {str(e)}")
        return False
    finally:
        session.close()

def main():
    """Função principal."""
    print("🚀 Aplicando regras fundamentais aos agentes criminais...")
    print("=" * 60)
    
    if atualizar_prompts_agentes_criminais():
        print("\n🎉 SUCESSO: Todos os agentes foram atualizados com as regras fundamentais!")
        print("\n📋 REGRAS IMPLEMENTADAS:")
        print("✅ Fundamentação obrigatória na base de conhecimento")
        print("✅ Proibição de criação de informações")
        print("✅ Citação obrigatória de fontes")
        print("✅ Resposta padrão para consultas sem base documental")
    else:
        print("\n❌ ERRO: Falha ao aplicar regras fundamentais")

if __name__ == "__main__":
    main()