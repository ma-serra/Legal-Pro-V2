"""
Atualizar modelos LLM dos assistentes para versões mais recentes (Dezembro 2025)
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

db_url = 'postgresql://postgres:XKtolNYAChqKElojyEfgzUdfpExZmBtM@gondola.proxy.rlwy.net:11843/railway'

# Mapeamento de modelos antigos para novos (Dezembro 2025)
MODEL_UPDATES = {
    # Anthropic - Atualizar para Claude 4.5 series
    'claude-3-opus': 'claude-opus-4.5',
    'claude-3-opus-20240229': 'claude-opus-4.5',
    'claude-3-5-sonnet-20241022': 'claude-sonnet-4.5',
    'claude-3-sonnet': 'claude-sonnet-4.5',
    'claude-3-haiku': 'claude-haiku-4.5',
    
    # OpenAI - Atualizar para GPT-5 series
    'gpt-4o': 'gpt-5.2-thinking',
    'gpt-4o-2024-08-06': 'gpt-5.2-thinking',
    'gpt-4o-mini': 'gpt-5.2-instant',
    'gpt-4': 'gpt-5.2-thinking',
    'gpt-4-turbo': 'gpt-5.2-thinking',
    
    # Google - Atualizar para Gemini 2.5/3
    'gemini-pro': 'gemini-2.5-pro',
    'gemini-1.5-pro': 'gemini-2.5-pro',
    'gemini-1.5-pro-002': 'gemini-2.5-pro',
    'gemini-1.5-flash': 'gemini-2.5-flash',
    'gemini-2.0-flash-exp': 'gemini-2.5-flash',
}

def update_models():
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("=== Atualizando Modelos LLM para Dezembro 2025 ===\n")
    
    # Buscar todos os assistentes
    cur.execute("""
        SELECT id, nome, configuracoes_llm, modelo_ai 
        FROM agente_juridico;
    """)
    
    assistentes = cur.fetchall()
    count_updated = 0
    updates_by_model = {}
    
    for assistente_id, nome, config_llm, modelo_ai in assistentes:
        config = config_llm if config_llm else {}
        old_model = config.get('llm_model', modelo_ai)
        
        if not old_model:
            continue
        
        # Verificar se precisa atualizar
        new_model = MODEL_UPDATES.get(old_model, old_model)
        
        if new_model != old_model:
            # Atualizar configuracoes_llm
            config['llm_model'] = new_model
            
            # Atualizar no banco
            cur.execute("""
                UPDATE agente_juridico 
                SET configuracoes_llm = %s::jsonb,
                    modelo_ai = %s
                WHERE id = %s;
            """, (json.dumps(config), new_model, assistente_id))
            
            count_updated += 1
            
            # Tracking
            if old_model not in updates_by_model:
                updates_by_model[old_model] = {'count': 0, 'new': new_model}
            updates_by_model[old_model]['count'] += 1
            
            if count_updated <= 10:  # Mostrar primeiros 10
                print(f"✅ {nome}: {old_model} -> {new_model}")
    
    print(f"\n=== Resumo das Atualizações ===")
    print(f"Total atualizado: {count_updated} assistentes\n")
    
    print("Por modelo:")
    for old, info in sorted(updates_by_model.items(), key=lambda x: -x[1]['count']):
        print(f"  {old} -> {info['new']}: {info['count']} assistentes")
    
    # Verificar distribuição final
    cur.execute("""
        SELECT 
            configuracoes_llm->>'llm_provider' as provider,
            configuracoes_llm->>'llm_model' as model,
            COUNT(*) as total
        FROM agente_juridico
        WHERE configuracoes_llm IS NOT NULL
        GROUP BY provider, model
        ORDER BY provider, total DESC;
    """)
    
    print(f"\n=== Distribuição Final por Modelo ===")
    for provider, model, total in cur.fetchall():
        print(f"  {provider}/{model}: {total} assistentes")
    
    cur.close()
    conn.close()
    
    print(f"\n✅ Atualização concluída!")

if __name__ == '__main__':
    update_models()
