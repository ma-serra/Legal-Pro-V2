#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Gemini Simples para testar a nova chave
"""

import os
import logging
from flask import request, jsonify

logger = logging.getLogger(__name__)

def processar_com_gemini(texto_documento):
    """Processa documento apenas com Gemini"""
    
    try:
        from google import genai
        
        # Configurar cliente Gemini
        client_gemini = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        prompt = f"""Analise este documento jurídico:

{texto_documento}

Forneça uma análise estruturada com:
1. ESTRUTURA DO DOCUMENTO
2. ALTERAÇÕES PROPOSTAS 
3. RISCOS JURÍDICOS
4. CONFORMIDADE REGULATÓRIA
5. RECOMENDAÇÕES PRÁTICAS
6. RESUMO EXECUTIVO
7. LIMITAÇÕES DA ANÁLISE

Inicie com: "ANÁLISE ESPECIALIZADA - Gemini 2.5 Flash"
"""
        
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        analise = response.text
        tokens_estimados = len(analise.split()) * 1.3
        
        resultado = {
            'status': 'sucesso',
            'api': 'gemini',
            'modelo': 'gemini-2.5-flash',
            'analise': analise,
            'tokens_usados': int(tokens_estimados),
            'chave_configurada': True
        }
        
        logger.info(f"✅ Gemini processado: {int(tokens_estimados)} tokens")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro Gemini: {e}")
        return {
            'status': 'erro',
            'api': 'gemini',
            'erro': str(e),
            'chave_configurada': bool(os.environ.get('GEMINI_API_KEY'))
        }

def registrar_api_gemini_simples(app):
    """Registra API simples do Gemini"""
    
    @app.route('/api/gemini-teste', methods=['POST'])
    def gemini_teste():
        try:
            data = request.get_json()
            texto_documento = data.get('texto_documento', '')
            
            if not texto_documento:
                return jsonify({'error': 'Texto do documento é obrigatório'}), 400
            
            resultado = processar_com_gemini(texto_documento)
            return jsonify(resultado)
            
        except Exception as e:
            logger.error(f"❌ Erro na API Gemini: {e}")
            return jsonify({'error': f'Erro interno: {e}'}), 500
    
    logger.info("✅ API Gemini Simple registrada")