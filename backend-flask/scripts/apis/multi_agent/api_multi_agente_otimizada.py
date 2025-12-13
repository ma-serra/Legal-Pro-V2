#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Multi-Agente Otimizada para Legal Design Pro V2
Sistema com 3 provedores de IA com timeouts otimizados
"""

import os
import time
import logging
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def session_scope():
    """Context manager para sessões do banco de dados"""
    engine = create_engine(os.environ.get('DATABASE_URL'))
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

def detectar_area_juridica(texto_documento):
    """Detecta a área jurídica do documento baseado em palavras-chave"""
    
    # Palavras-chave expandidas por área jurídica
    areas_palavras_chave = {
        'DIREITO AGRÁRIO': [
            'arrendamento rural', 'propriedade rural', 'reforma agrária', 'assentamento',
            'incra', 'itr', 'car', 'cadastro ambiental rural', 'módulo fiscal',
            'usucapião rural', 'terra nua', 'exploração agropecuária', 'parceria rural',
            'comodato rural', 'agricultura familiar', 'agronegócio', 'latifúndio',
            'cultivo', 'pecuária', 'irrigação', 'soja', 'milho', 'arroz', 'feijão',
            'café', 'cana-de-açúcar', 'algodão', 'mandioca', 'sorgo', 'trigo',
            'aveia', 'centeio', 'cevada', 'girassol', 'amendoim', 'mamona',
            'dendê', 'seringueira', 'eucalipto', 'pinus', 'mogno', 'cedro',
            'ipê', 'peroba', 'jatobá', 'aroeira', 'braúna', 'cabreúva',
            'imbuia', 'pau-brasil', 'jacarandá', 'sucupira', 'cumaru',
            'freijó', 'angelim', 'garapeira', 'guaritá', 'itaúba',
            'hectares', 'alqueires', 'tarefas', 'quadras', 'braças'
        ],
        'DIREITO EMPRESARIAL': [
            'sociedade limitada', 'sociedade anônima', 'mei', 'eireli', 'cnpj',
            'contrato social', 'alteração contratual', 'dissolução', 'liquidação',
            'transformação', 'incorporação', 'fusão', 'cisão', 'holding',
            'empresário individual', 'sócio', 'quotas', 'ações', 'assembleia',
            'conselho administrativo', 'diretoria', 'fiscal', 'balanço'
        ],
        'DIREITO TRABALHISTA': [
            'empregado', 'empregador', 'carteira de trabalho', 'ctps', 'contrato de trabalho',
            'rescisão', 'aviso prévio', 'fgts', 'inss', 'férias', 'décimo terceiro',
            'horas extras', 'adicional noturno', 'insalubridade', 'periculosidade',
            'estabilidade', 'licença maternidade', 'auxílio doença', 'acidente de trabalho'
        ],
        'DIREITO CIVIL': [
            'contrato', 'compra e venda', 'locação', 'comodato', 'doação', 'permuta',
            'pessoa física', 'pessoa jurídica', 'capacidade civil', 'personalidade',
            'domicílio', 'residência', 'bens', 'direitos reais', 'posse', 'propriedade',
            'usucapião', 'servidão', 'usufruto', 'penhor', 'hipoteca', 'anticrese'
        ]
    }
    
    texto_lower = texto_documento.lower()
    pontuacao_areas = {}
    
    for area, palavras in areas_palavras_chave.items():
        pontuacao = 0
        for palavra in palavras:
            if palavra.lower() in texto_lower:
                pontuacao += 1
        pontuacao_areas[area] = pontuacao
    
    # Retorna a área com maior pontuação
    if pontuacao_areas:
        area_detectada = max(pontuacao_areas, key=pontuacao_areas.get)
        confianca = pontuacao_areas[area_detectada] / len(areas_palavras_chave[area_detectada]) * 100
        if confianca > 10:  # Mínimo de 10% de confiança
            return area_detectada
    
    return 'DIREITO GERAL'

def processar_multi_agente_otimizado(texto_documento):
    """Processa documento com 3 agentes de forma otimizada"""
    
    logger.info(f"📄 Iniciando análise multi-agente otimizada: {len(texto_documento)} chars")
    
    # Detectar área jurídica
    area_detectada = detectar_area_juridica(texto_documento)
    logger.info(f"🎯 Área detectada: {area_detectada}")
    
    # Selecionar agentes especializados
    with session_scope() as session:
        try:
            query = text(f"""
                SELECT id, nome, descricao, categoria_id
                FROM agente_juridico 
                WHERE categoria_id IN (
                    SELECT id FROM categoria_juridica 
                    WHERE LOWER(nome) LIKE '%{area_detectada.lower().replace('direito ', '')}%'
                )
                AND ativo = true
                ORDER BY nivel_especializacao DESC
                LIMIT 3
            """)
            
            results = session.execute(query).fetchall()
            agentes_selecionados = []
            
            if results:
                for result in results:
                    agente_info = {
                        'id': result[0],
                        'nome': result[1],
                        'descricao': result[2],
                        'categoria_id': result[3]
                    }
                    agentes_selecionados.append(agente_info)
            else:
                # Fallback para agentes gerais
                fallback_query = text("SELECT id, nome, descricao, categoria_id FROM agente_juridico WHERE ativo = true ORDER BY nivel_especializacao DESC LIMIT 3")
                fallback_results = session.execute(fallback_query).fetchall()
                for result in fallback_results:
                    agente_info = {
                        'id': result[0],
                        'nome': result[1],
                        'descricao': result[2],
                        'categoria_id': result[3]
                    }
                    agentes_selecionados.append(agente_info)
            
            logger.info(f"🤖 {len(agentes_selecionados)} agentes selecionados")
            
        except Exception as e:
            logger.error(f"❌ Erro na seleção de agentes: {e}")
            agentes_selecionados = [{
                'id': 1,
                'nome': 'Especialista Jurídico Geral',
                'descricao': 'Análise jurídica geral',
                'categoria_id': 1
            }]
    
    # Processar com 3 APIs
    resultados_analise = []
    total_tokens = 0
    
    # 1. OpenAI GPT-4o
    try:
        import openai
        client_openai = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        agente_1 = agentes_selecionados[0]
        nome_especialista_1 = agente_1['nome']
        
        prompt_1 = f"""Como {nome_especialista_1}, analise este documento jurídico:

{texto_documento[:3000]}

Forneça análise estruturada com:
1. ESTRUTURA DO DOCUMENTO
2. ALTERAÇÕES PROPOSTAS 
3. RISCOS JURÍDICOS
4. CONFORMIDADE REGULATÓRIA
5. RECOMENDAÇÕES PRÁTICAS
6. RESUMO EXECUTIVO
7. LIMITAÇÕES DA ANÁLISE

Inicie com: "ANÁLISE ESPECIALIZADA - {nome_especialista_1}"
"""
        
        response_1 = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_1}],
            max_tokens=4000,
            temperature=0.7,
            timeout=30
        )
        
        analise_1 = response_1.choices[0].message.content
        tokens_1 = response_1.usage.total_tokens if response_1.usage else 3000
        total_tokens += tokens_1
        
        resultados_analise.append({
            'api': 'openai',
            'agente_nome': nome_especialista_1,
            'agente_id': agente_1['id'],
            'modelo': 'gpt-4o',
            'analise': analise_1,
            'tokens_usados': tokens_1,
            'status': 'sucesso'
        })
        
        logger.info(f"✅ OpenAI: {tokens_1} tokens - {nome_especialista_1}")
        
    except Exception as e:
        logger.warning(f"⚠️ OpenAI falhou: {e}")
        resultados_analise.append({
            'api': 'openai',
            'agente_nome': agentes_selecionados[0]['nome'],
            'agente_id': agentes_selecionados[0]['id'],
            'modelo': 'gpt-4o',
            'analise': f"ANÁLISE ESPECIALIZADA - {agentes_selecionados[0]['nome']}\n\nErro OpenAI: {e}",
            'tokens_usados': 0,
            'status': 'erro'
        })
    
    # 2. Anthropic Claude
    try:
        import anthropic
        client_anthropic = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        agente_2 = agentes_selecionados[1] if len(agentes_selecionados) > 1 else agentes_selecionados[0]
        nome_especialista_2 = agente_2['nome']
        if agente_2['id'] == agentes_selecionados[0]['id']:
            nome_especialista_2 = f"{nome_especialista_2} - Análise Complementar"
        
        prompt_2 = f"""Como {nome_especialista_2}, analise este documento jurídico:

{texto_documento[:3000]}

Forneça análise estruturada com:
1. ESTRUTURA DO DOCUMENTO
2. ALTERAÇÕES PROPOSTAS 
3. RISCOS JURÍDICOS
4. CONFORMIDADE REGULATÓRIA
5. RECOMENDAÇÕES PRÁTICAS
6. RESUMO EXECUTIVO
7. LIMITAÇÕES DA ANÁLISE

Inicie com: "ANÁLISE ESPECIALIZADA - {nome_especialista_2}"
"""
        
        response_2 = client_anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt_2}],
            max_tokens=4000,
            temperature=0.7,
            timeout=30
        )
        
        analise_2 = response_2.content[0].text
        tokens_2 = response_2.usage.input_tokens + response_2.usage.output_tokens if response_2.usage else 3000
        total_tokens += tokens_2
        
        resultados_analise.append({
            'api': 'anthropic',
            'agente_nome': nome_especialista_2,
            'agente_id': agente_2['id'],
            'modelo': 'claude-3-5-sonnet-20241022',
            'analise': analise_2,
            'tokens_usados': tokens_2,
            'status': 'sucesso'
        })
        
        logger.info(f"✅ Anthropic: {tokens_2} tokens - {nome_especialista_2}")
        
    except Exception as e:
        logger.warning(f"⚠️ Anthropic falhou: {e}")
        resultados_analise.append({
            'api': 'anthropic',
            'agente_nome': f"{agentes_selecionados[0]['nome']} - Complementar",
            'agente_id': agentes_selecionados[0]['id'],
            'modelo': 'claude-3-5-sonnet-20241022',
            'analise': f"ANÁLISE ESPECIALIZADA - {agentes_selecionados[0]['nome']} - Complementar\n\nErro Anthropic: {e}",
            'tokens_usados': 0,
            'status': 'erro'
        })
    
    # 3. Google Gemini
    try:
        from google import genai
        client_gemini = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        agente_3 = agentes_selecionados[2] if len(agentes_selecionados) > 2 else agentes_selecionados[0]
        nome_especialista_3 = agente_3['nome']
        if agente_3['id'] == agentes_selecionados[0]['id']:
            nome_especialista_3 = f"{nome_especialista_3} - Análise Adicional"
        
        prompt_3 = f"""Como {nome_especialista_3}, analise este documento jurídico:

{texto_documento[:3000]}

Forneça análise estruturada com:
1. ESTRUTURA DO DOCUMENTO
2. ALTERAÇÕES PROPOSTAS 
3. RISCOS JURÍDICOS
4. CONFORMIDADE REGULATÓRIA
5. RECOMENDAÇÕES PRÁTICAS
6. RESUMO EXECUTIVO
7. LIMITAÇÕES DA ANÁLISE

Inicie com: "ANÁLISE ESPECIALIZADA - {nome_especialista_3}"
"""
        
        response_3 = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_3
        )
        
        analise_3 = response_3.text
        tokens_3 = len(analise_3.split()) * 1.3  # Estimativa
        total_tokens += tokens_3
        
        resultados_analise.append({
            'api': 'gemini',
            'agente_nome': nome_especialista_3,
            'agente_id': agente_3['id'],
            'modelo': 'gemini-2.5-flash',
            'analise': analise_3,
            'tokens_usados': int(tokens_3),
            'status': 'sucesso'
        })
        
        logger.info(f"✅ Gemini: {int(tokens_3)} tokens - {nome_especialista_3}")
        
    except Exception as e:
        logger.warning(f"⚠️ Gemini falhou: {e}")
        resultados_analise.append({
            'api': 'gemini',
            'agente_nome': f"{agentes_selecionados[0]['nome']} - Adicional",
            'agente_id': agentes_selecionados[0]['id'],
            'modelo': 'gemini-2.5-flash',
            'analise': f"ANÁLISE ESPECIALIZADA - {agentes_selecionados[0]['nome']} - Adicional\n\nErro Gemini: {e}",
            'tokens_usados': 0,
            'status': 'erro'
        })
    
    # Resultado final
    resultado_final = {
        'status': 'sucesso',
        'resultados': resultados_analise,
        'total_agentes': len(resultados_analise),
        'total_tokens': int(total_tokens),
        'area_detectada': area_detectada,
        'tempo_total': 60.0,
        'sistema_id': str(int(time.time())),
        'configuracao_aplicada': {
            'apis_utilizadas': [r['api'] for r in resultados_analise],
            'agentes_utilizados': [r['agente_nome'] for r in resultados_analise],
            'max_tokens': 4000,
            'temperature': 0.7
        }
    }
    
    logger.info(f"✅ Análise multi-agente concluída: {len(resultados_analise)} agentes, {int(total_tokens)} tokens")
    return resultado_final

# Função para integração com Flask
def registrar_api_otimizada(app):
    """Registra a API otimizada no Flask"""
    
    @app.route('/api/multi-agente-otimizada', methods=['POST'])
    def multi_agente_otimizada():
        try:
            data = request.get_json()
            texto_documento = data.get('texto_documento', '')
            
            if not texto_documento:
                return jsonify({'error': 'Texto do documento é obrigatório'}), 400
            
            resultado = processar_multi_agente_otimizado(texto_documento)
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro na API otimizada: {e}")
            return jsonify({'error': f'Erro interno: {e}'}), 500
    
    logger.info("✅ API Multi-Agente Otimizada registrada")