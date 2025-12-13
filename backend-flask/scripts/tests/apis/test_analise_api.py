#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de validação da API Multi-Agente
Testa o processamento do contrato em anexo e corrige erros
"""

import os
import time
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_documento_contrato():
    """Testa o processamento do documento de contrato"""
    
    # Texto do contrato fornecido
    documento_teste = """
INSTRUMENTO PARTICULAR DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: empresa com sede à Rua Porto Alegre/RS, inscrita no CNPJ/MF
CONTRATADA: MAYMIDIA, com sede à Rua Furriel Luiz Antônio de Vargas, 250, Conj 403, Bairro Bela Vista, CEP 90.470-130, Porto Alegre/RS, inscrita no CNPJ/MF sob nº 47.856.359/0001-29

DO OBJETO
É objeto do presente contrato a PRESTAÇÃO DE SERVIÇOS DE MARKETING DIGITAL por parte da CONTRATADA para promover os serviços da CONTRATANTE.

DAS OBRIGAÇÕES DA CONTRATADA
- Realizar reuniões presenciais ou virtuais previamente agendadas
- Executar os serviços contratados com observância das normas legais aplicáveis
- Adquirir e configurar o provedor de hospedagem contratado (contrato de 12 meses)
- Criação do Site e página de blog entregue ajustados para SEO

DAS OBRIGAÇÕES DA CONTRATANTE
- Realizar reuniões presenciais ou virtuais previamente agendadas
- Fornecer o material necessário para o adequado desenvolvimento dos serviços
- Efetuar os pagamentos devidos à CONTRATADA nos prazos estabelecidos

DO PREÇO
Pela prestação de serviços, a CONTRATANTE deverá pagar à CONTRATADA o valor de R$ 12.678,00 (doze mil seiscentos e setenta e oito reais), sendo entrada de R$ 4.226,00 e mais duas parcelas de R$ 4.226,00 em 30 dias.

DO PRAZO E RESCISÃO
Este contrato tem vigência de 1 (mês) ou até a total entrega dos serviços contratados.

DO FORO
Fica eleito o FORO da Porto Alegre, estado do Rio Grande do Sul.
"""
    
    logger.info("🚀 Iniciando teste da API Multi-Agente com documento real")
    logger.info(f"📄 Documento: {len(documento_teste)} caracteres")
    
    try:
        # Testar configuração das APIs diretamente
        import openai
        import anthropic
        from google import genai
        from google.genai import types
        
        logger.info("✅ Imports das APIs realizados com sucesso")
        
        # Configurar clientes com importação isolada
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY não encontrada")
            
        # Criar cliente OpenAI completamente isolado
        from openai import OpenAI
        client_openai = OpenAI(api_key=openai_key)
        logger.info("✅ Cliente OpenAI configurado")
        
        client_anthropic = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY')
        )
        logger.info("✅ Cliente Anthropic configurado")
        
        client_gemini = genai.Client(
            api_key=os.environ.get('GEMINI_API_KEY')
        )
        logger.info("✅ Cliente Gemini configurado")
        
        # Prompt de teste para análise jurídica
        prompt_teste = f"""ANÁLISE JURÍDICA ESPECIALIZADA

DOCUMENTO PARA ANÁLISE:
{documento_teste[:2000]}

Realize uma análise jurídica COMPLETA e ESTRUTURADA seguindo este formato:

1. IDENTIFICAÇÃO E CONTEXTUALIZAÇÃO
- Tipo de documento: [Especificar natureza jurídica]
- Partes envolvidas: [Identificar as partes]
- Área jurídica predominante: [Determinar ramo do direito]

2. ANÁLISE ESTRUTURAL
- Organização do documento: [Como está estruturado]
- Cláusulas principais: [Disposições mais importantes]

3. IDENTIFICAÇÃO DE RISCOS JURÍDICOS
CRÍTICOS: [Riscos que podem invalidar o documento]
ALTOS: [Problemas graves que requerem correção imediata]
MÉDIOS: [Questões importantes que devem ser revisadas]

4. RECOMENDAÇÕES PRÁTICAS
- Ações imediatas: [O que fazer primeiro]
- Procedimentos recomendados: [Como implementar]

Forneça conteúdo ESPECÍFICO e DETALHADO baseado no documento real apresentado."""
        
        # Teste 1: OpenAI
        logger.info("🤖 Testando OpenAI...")
        response_openai = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista jurídico altamente qualificado. Forneça análises detalhadas, específicas e estruturadas."},
                {"role": "user", "content": prompt_teste}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        analise_openai = response_openai.choices[0].message.content
        tokens_openai = response_openai.usage.total_tokens
        logger.info(f"✅ OpenAI sucesso: {tokens_openai} tokens, {len(analise_openai)} chars")
        
        # Teste 2: Gemini
        logger.info("🤖 Testando Gemini...")
        response_gemini = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_teste,
            config=types.GenerateContentConfig(
                max_output_tokens=2000,
                temperature=0.7
            )
        )
        
        analise_gemini = response_gemini.text if response_gemini.text else "Resposta vazia do Gemini"
        tokens_gemini = len(analise_gemini.split()) * 1.3 if analise_gemini else 0
        logger.info(f"✅ Gemini sucesso: {int(tokens_gemini)} tokens, {len(analise_gemini)} chars")
        
        # Teste 3: Anthropic
        logger.info("🤖 Testando Anthropic...")
        response_anthropic = client_anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt_teste}
            ]
        )
        
        analise_anthropic = response_anthropic.content[0].text
        tokens_anthropic = response_anthropic.usage.input_tokens + response_anthropic.usage.output_tokens
        logger.info(f"✅ Anthropic sucesso: {tokens_anthropic} tokens, {len(analise_anthropic)} chars")
        
        # Consolidar resultados
        resultado_teste = {
            'status': 'sucesso',
            'results': {
                'analise_openai': analise_openai,
                'analise_gemini': analise_gemini,
                'analise_anthropic': analise_anthropic,
                'comparacao': {
                    'consenso': 'Análise realizada com sucesso pelas 3 APIs',
                    'total_tokens': tokens_openai + int(tokens_gemini) + tokens_anthropic,
                    'apis_funcionais': 3,
                    'total_apis': 3
                }
            }
        }
        
        logger.info("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info(f"📊 Total tokens: {resultado_teste['results']['comparacao']['total_tokens']}")
        logger.info("📋 Análises geradas pelas 3 APIs")
        
        return resultado_teste
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'status': 'erro', 'mensagem': str(e)}

if __name__ == "__main__":
    resultado = testar_documento_contrato()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))