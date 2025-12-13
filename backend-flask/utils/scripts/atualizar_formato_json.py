#!/usr/bin/env python3
"""
Script para atualizar o formato dos detalhes técnicos nos agentes jurídicos.
Este script garante que todos os valores em detalhes_tecnicos sejam strings JSON.
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import Json, DictCursor

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Obtém a string de conexão do ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

def converter_para_json(detalhes):
    """
    Converte um valor para uma string JSON, tratando diferentes formatos.
    
    Args:
        detalhes: Valor a ser convertido (dict, str, None, etc.)
        
    Returns:
        str: String JSON ou None se o valor for None
    """
    if detalhes is None:
        return None
    
    # Se já for uma string, verifica se é um JSON válido
    if isinstance(detalhes, str):
        try:
            # Tenta converter para dict e depois de volta para string para garantir formato correto
            return json.dumps(json.loads(detalhes))
        except json.JSONDecodeError:
            # Se não for um JSON válido, retorna um JSON vazio
            logger.warning(f"Detalhes técnicos não é um JSON válido: {detalhes[:50]}...")
            return json.dumps({})
    
    # Para outros tipos, tenta converter diretamente
    try:
        return json.dumps(detalhes)
    except:
        logger.warning(f"Não foi possível converter detalhes do tipo {type(detalhes)}")
        return json.dumps({})

def atualizar_agentes():
    """
    Atualiza todos os agentes jurídicos, garantindo que detalhes_tecnicos seja uma string JSON.
    """
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # Primeiro, obtém todos os agentes que precisam ser atualizados
        cursor.execute("SELECT id, detalhes_tecnicos FROM agente_juridico")
        agentes = cursor.fetchall()
        logger.info(f"Encontrados {len(agentes)} agentes para processamento")
        
        contador = 0
        for agente in agentes:
            agente_id = agente['id']
            detalhes = agente['detalhes_tecnicos']
            
            # Converte para JSON se necessário
            json_string = converter_para_json(detalhes)
            
            # Atualiza o registro no banco de dados
            cursor.execute(
                "UPDATE agente_juridico SET detalhes_tecnicos = %s WHERE id = %s",
                (json_string, agente_id)
            )
            contador += 1
            
        # Confirma as alterações
        conn.commit()
        logger.info(f"Atualização concluída. {contador} agentes atualizados.")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar agentes: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Iniciando atualização dos detalhes técnicos dos agentes...")
    atualizar_agentes()
    logger.info("Processo finalizado.")